import robin_stocks.robinhood as r
import streamlit as st

from src.fetch_price import fetch_current_price

def fetch_and_evaluate_greeks(symbol, expiration_date, option_type="call"):
    """
    Fetches options data by symbol and expiration date, evaluates Greeks,
    and calculates intrinsic and extrinsic values along with theta decay.
    
    Instead of printing, this function uses st.write() to display output
    in the Streamlit UI.
    """
    try:
        st.write(f"**Fetching {option_type} options for {symbol} expiring on {expiration_date}...**")
        options = r.options.find_options_by_expiration(
            inputSymbols=symbol,
            expirationDate=expiration_date,
            optionType=option_type
        )

        if not options:
            st.write("No options data found for the given parameters.")
            return

        current_price = fetch_current_price(symbol)
        if current_price is None:
            st.write("Unable to fetch the current price. Exiting.")
            return

        st.write(f"Current Price of {symbol}: **{current_price}**")

        # Sort options by strike price
        options = sorted(options, key=lambda x: float(x['strike_price']))

        # Separate in-the-money and out-of-the-money options
        itm_options = [opt for opt in options if float(opt['strike_price']) <= current_price]
        otm_options = [opt for opt in options if float(opt['strike_price']) > current_price]

        # Select closest options
        first_itm_option = itm_options[-1] if itm_options else None
        first_otm_option = otm_options[0] if otm_options else None
        
        selected_options = []
        if first_itm_option:
            selected_options.append(first_itm_option)
        if first_otm_option:
            selected_options.append(first_otm_option)

        st.write(f"**Selected {option_type.capitalize()} Options for {symbol}** (Expiration: {expiration_date}):")
        st.write("=" * 60)

        # Analyze Greeks and calculate intrinsic/extrinsic values
        for option in selected_options:
            strike_price = float(option.get('strike_price', 'N/A'))
            market_data = r.options.get_option_market_data(
                inputSymbols=symbol,
                expirationDate=expiration_date,
                strikePrice=strike_price,
                optionType=option_type
            )

            if isinstance(market_data, list) and market_data:
                # Some versions of get_option_market_data return [[{}]], so check
                first_entry = market_data[0][0] if isinstance(market_data[0], list) and market_data[0] else {}
                delta = first_entry.get('delta', 'N/A')
                gamma = first_entry.get('gamma', 'N/A')
                theta = float(first_entry.get('theta', 0))
                vega = first_entry.get('vega', 'N/A')
                premium = float(first_entry.get('adjusted_mark_price', 0))
            else:
                delta = gamma = theta = vega = premium = 'N/A'

            if premium == 'N/A':
                intrinsic_value = 'N/A'
                extrinsic_value = 'N/A'
                theta_decay_percentage = 'N/A'
                intrinsic_value_dollar = 'N/A'
                extrinsic_value_dollar = 'N/A'
            else:
                # Calculate intrinsic/extrinsic
                if option_type == "call":
                    intrinsic_value = max(0, (current_price - strike_price))
                else:  # put
                    intrinsic_value = max(0, (strike_price - current_price))
                
                extrinsic_value = premium - intrinsic_value
                theta_decay_percentage = (abs(theta) / premium) * 100 if premium > 0 else 0
                # Dollar amounts (per contract = 100 shares)
                intrinsic_value_dollar = intrinsic_value * 100
                extrinsic_value_dollar = (premium * 100) - intrinsic_value_dollar

            st.write(f"**Strike Price**: {strike_price}")
            st.write(f"  - Delta: {delta}")
            st.write(f"  - Gamma: {gamma}")
            st.write(f"  - Theta: {theta}")
            st.write(f"  - Vega: {vega}")
            st.write(f"  - Premium: {premium}")
            st.write(f"  - Intrinsic Value: {round(intrinsic_value, 2) if intrinsic_value != 'N/A' else 'N/A'}")
            st.write(f"  - Intrinsic Value (Dollar): ${round(intrinsic_value_dollar, 2) if intrinsic_value_dollar != 'N/A' else 'N/A'}")
            st.write(f"  - Extrinsic Value: {round(extrinsic_value, 2) if extrinsic_value != 'N/A' else 'N/A'}")
            st.write(f"  - Extrinsic Value (Dollar): ${round(extrinsic_value_dollar, 2) if extrinsic_value_dollar != 'N/A' else 'N/A'}")
            st.write(f"  - Theta Decay (%): {round(theta_decay_percentage, 2) if theta_decay_percentage != 'N/A' else 'N/A'}%")
            st.write("")

        return selected_options

    except Exception as e:
        st.write(f"**Error fetching options data**: {e}")
        return None

'''
from src.fetch_price import fetch_current_price
import robin_stocks.robinhood as r

def fetch_and_evaluate_greeks(symbol, expiration_date, option_type="call"):
    """
    Fetches options data by symbol and expiration date, evaluates Greeks,
    and calculates intrinsic and extrinsic values along with theta decay.
    """
    try:
        print(f"\nFetching {option_type} options for {symbol} expiring on {expiration_date}...")
        options = r.options.find_options_by_expiration(
            inputSymbols=symbol,
            expirationDate=expiration_date,
            optionType=option_type
        )

        if not options:
            print("No options data found for the given parameters.")
            return

        current_price = fetch_current_price(symbol)
        if current_price is None:
            print("Unable to fetch the current price. Exiting.")
            return

        print(f"Current Price of {symbol}: {current_price}")

        # Sort options by strike price
        options = sorted(options, key=lambda x: float(x['strike_price']))

        # Separate in-the-money and out-of-the-money options
        itm_options = [opt for opt in options if float(opt['strike_price']) <= current_price]
        otm_options = [opt for opt in options if float(opt['strike_price']) > current_price]

        # Select closest options
        first_itm_option = itm_options[-1] if itm_options else None
        first_otm_option = otm_options[0] if otm_options else None
        selected_options = []
        if first_itm_option:
            selected_options.append(first_itm_option)
        if first_otm_option:
            selected_options.append(first_otm_option)

        print(f"\nSelected {option_type.capitalize()} Options for {symbol} (Expiration: {expiration_date}):")
        print("=" * 60)

        # Analyze Greeks and calculate intrinsic/extrinsic values
        for option in selected_options:
            strike_price = float(option.get('strike_price', 'N/A'))
            market_data = r.options.get_option_market_data(
                inputSymbols=symbol,
                expirationDate=expiration_date,
                strikePrice=strike_price,
                optionType=option_type
            )

            if isinstance(market_data, list) and market_data:
                first_entry = market_data[0][0] if isinstance(market_data[0], list) and market_data[0] else {}
                delta = first_entry.get('delta', 'N/A')
                gamma = first_entry.get('gamma', 'N/A')
                theta = float(first_entry.get('theta', 0))
                vega = first_entry.get('vega', 'N/A')
                premium = float(first_entry.get('adjusted_mark_price', 0))
            else:
                delta = gamma = theta = vega = premium = 'N/A'

            intrinsic_value = max(0, current_price - strike_price) if option_type == "call" else max(0, strike_price - current_price)
            extrinsic_value = premium - intrinsic_value if premium != 'N/A' else 'N/A'
            theta_decay_percentage = (abs(theta) / premium) * 100 if premium > 0 else 0
            # Calculate intrinsic and extrinsic values in dollar amounts
            intrinsic_value_dollar = intrinsic_value * 100
            extrinsic_value_dollar = (premium * 100) - intrinsic_value_dollar if premium != 'N/A' else 'N/A'



            print(f"Strike Price: {strike_price}")
            print(f"  Delta: {delta}")
            print(f"  Gamma: {gamma}")
            print(f"  Theta: {theta}")
            print(f"  Vega: {vega}")
            print(f"  Premium: {premium}")
            print(f"  Intrinsic Value: {round(intrinsic_value, 2)}")
            print(f"  Intrinsic Value (Dollar): ${round(intrinsic_value_dollar, 2)}")
            print(f"  Extrinsic Value: {round(extrinsic_value, 2) if extrinsic_value != 'N/A' else 'N/A'}")
            print(f"  Extrinsic Value (Dollar): ${round(extrinsic_value_dollar, 2) if extrinsic_value_dollar != 'N/A' else 'N/A'}")
            print(f"  Theta Decay (%): {round(theta_decay_percentage, 2)}%\n")

        return selected_options

    except Exception as e:
        print(f"Error fetching options data: {e}")

'''