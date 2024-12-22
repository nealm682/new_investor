import robin_stocks.robinhood as r
import streamlit as st

def fetch_historical_closing_prices(symbol, span="3month"):
    """
    Fetches historical daily closing prices for the given stock ticker.

    Parameters:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        span (str): The time span for historical data. Options:
                    'day', 'week', 'month', '3month', 'year', '5year', 'all'.

    Returns:
        list: A list of dictionaries with 'date' and 'close_price'.
    """
    try:
        # Fetch historical data
        historicals = r.stocks.get_stock_historicals(
            symbol,
            span=span,            # Control the span (e.g., '3month')
            bounds='regular'      # Fetch regular trading session data
        )

        if not historicals:
            st.write(f"No historical data found for {symbol}.")
            return []

        # Extract and format data
        data = [
            {"date": item["begins_at"], "close_price": item["close_price"]}
            for item in historicals
        ]

        # Optionally, you could log the raw data in the UI:
        # st.write(f"DEBUG: Historical closing prices for {symbol}: {data}")

        return data

    except Exception as e:
        st.write(f"Error fetching historical closing prices for {symbol}: {e}")
        return []

'''
import robin_stocks.robinhood as r

def fetch_historical_closing_prices(symbol, span="3month"):
    """
    Fetches historical daily closing prices for the given stock ticker.

    Parameters:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        span (str): The time span for historical data. Options: 'day', 'week', 'month', '3month', 'year', '5year', 'all'.

    Returns:
        list: A list of dictionaries with 'date' and 'close_price'.
    """
    try:
        # Fetch historical data
        historicals = r.stocks.get_stock_historicals(
            symbol,
            span=span,            # Control the span (e.g., '3month')
            bounds='regular'      # Fetch regular trading session data
        )

        if not historicals:
            print(f"No historical data found for {symbol}.")
            return []

        # Extract and format data
        data = [
            {"date": item["begins_at"], "close_price": item["close_price"]}
            for item in historicals
        ]

        #print(f"DEBUG: Historical closing prices for {symbol}: {data}")
        return data
    except Exception as e:
        print(f"Error fetching historical closing prices for {symbol}: {e}")
        return []
'''