import robin_stocks.robinhood as r
import pandas as pd
from dotenv import load_dotenv
import os

selected_options = []

# Load environment variables from .env file
load_dotenv()

USERNAME = os.getenv("ROBINHOOD_USERNAME")
PASSWORD = os.getenv("ROBINHOOD_PASSWORD")

def login_to_robinhood():
    """
    Logs into the Robinhood account using username and password.
    """
    try:
        login = r.login(username=USERNAME, password=PASSWORD)
        print("Login successful.")
        return login
    except Exception as e:
        print(f"Failed to log in: {e}")
        return None

def login_to_robinhood():
    """
    Logs into the Robinhood account using username and password.
    """
    try:
        login = r.login(username=USERNAME, password=PASSWORD)
        print("Login successful.")
        return login
    except Exception as e:
        print(f"Failed to log in: {e}")
        return None

def fetch_current_price(symbol):
    """
    Fetches the current stock price for the given symbol.
    """
    try:
        quote = r.stocks.get_stock_quote_by_symbol(symbol)
        #print(f"DEBUG: Stock quote for {symbol}: {quote}")
        return float(quote['last_trade_price'])
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def fetch_and_evaluate_greeks(symbol, expiration_date, option_type="call"):
    """
    Fetches options data by symbol and expiration date, and evaluates Greeks.
    Filters to show 2 in-the-money and 2 out-of-the-money options closest to the current price.
    """
    try:
        print(f"\nFetching {option_type} options for {symbol} expiring on {expiration_date}...")
        options = r.options.find_options_by_expiration(
            inputSymbols=symbol, 
            expirationDate=expiration_date, 
            optionType=option_type
        )

        #print(f"DEBUG: Raw options data: {options}")

        if not options:
            print("No options data found for the given parameters.")
            return

        # Get current stock price
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

        # Select 2 closest in-the-money and 2 closest out-of-the-money options
        selected_options = (itm_options[-2:] if itm_options else []) + (otm_options[:2] if otm_options else [])

        print(f"\nFiltered {option_type.capitalize()} Options for {symbol} (Expiration: {expiration_date}):")
        print("=" * 60)

        # Fetch and display options and Greeks
        for option in selected_options:
            strike_price = option.get('strike_price', 'N/A')

            # Fetch detailed market data for Greeks
            market_data = r.options.get_option_market_data(
                inputSymbols=symbol,
                expirationDate=expiration_date,
                strikePrice=strike_price,
                optionType=option_type
            )

            #print(f"DEBUG: Market data for strike price {strike_price}: {market_data}")

            # Check if market_data is a nested list and extract Greeks
            if isinstance(market_data, list) and market_data:
                first_entry = market_data[0][0] if isinstance(market_data[0], list) and market_data[0] else {}
                delta = first_entry.get('delta', 'N/A')
                gamma = first_entry.get('gamma', 'N/A')
                theta = first_entry.get('theta', 'N/A')
                vega = first_entry.get('vega', 'N/A')
            else:
                delta = gamma = theta = vega = 'N/A'

            #print(f"DEBUG: Greeks for strike price {strike_price}: Delta: {delta}, Gamma: {gamma}, Theta: {theta}, Vega: {vega}")

            print(f"Strike Price: {strike_price}")
            print(f"  Delta: {delta}")
            print(f"  Gamma: {gamma}")
            print(f"  Theta: {theta}")
            print(f"  Vega: {vega}\n")

            return selected_options


    except Exception as e:
        print(f"Error fetching options data: {e}")

def get_expiration_date_for_month(symbol, month):
    """
    Fetches expiration dates for the given ticker and filters them for the specified month.
    Presents the user with letter-based options to select an expiration date.
    """
    try:
        # Fetch all expiration dates for the symbol
        chains = r.options.get_chains(symbol)
        expiration_dates = chains.get('expiration_dates', [])
        #print(f"DEBUG: All expiration dates for {symbol}: {expiration_dates}")

        # Filter dates for the specified month (e.g., "2025-01")
        month_dates = [date for date in expiration_dates if date.startswith(month)]
        if not month_dates:
            print(f"No expiration dates found for {symbol} in {month}.")
            return None

        # Display options with letters
        print(f"Available expiration dates for {symbol} in {month}:")
        for i, date in enumerate(month_dates):
            print(f"  {chr(97 + i)}) {date}")

        # Let the user choose a date
        choice = input("Select an expiration date by letter: ").strip().lower()
        index = ord(choice) - 97  # Convert letter to index
        if 0 <= index < len(month_dates):
            return month_dates[index]
        else:
            print("Invalid selection.")
            return None
    except Exception as e:
        print(f"Error fetching expiration dates for {symbol}: {e}")
        return None
    

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
    

def analyze_daily_percentage_changes_90_days(historical_data):
    """
    Analyzes daily percentage changes in stock closing prices for the last 90 calendar days.
    Determines positive and negative percentage changes and calculates metrics.

    Parameters:
        historical_data (list of dict): Historical data with 'date' and 'close_price'.
            Example: [{"date": "2024-11-21T19:00:00Z", "close_price": 105}, ...]

    Returns:
        dict: A dictionary containing metrics for positive and negative changes.
    """
    try:
        if not historical_data or len(historical_data) < 2:
            return {"error": "Insufficient data for analysis."}

        # Convert to DataFrame for easier processing
        df = pd.DataFrame(historical_data)
        df["date"] = pd.to_datetime(df["date"])  # Ensure date is datetime format
        df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")  # Convert to numeric

        # Keep only the last 90 calendar days
        today = pd.Timestamp.now(tz='UTC')  # Ensure timezone awareness
        start_date = today - pd.Timedelta(days=90)
        df = df[df["date"] >= start_date]

        # Group by date to get the last closing price of each trading day
        df = df.groupby(df["date"].dt.date)["close_price"].last().reset_index()
        df.rename(columns={"date": "trading_date"}, inplace=True)

        # Calculate daily percentage changes
        df["pct_change"] = df["close_price"].pct_change() * 100

        # Separate positive and negative changes
        positive_changes = df[df["pct_change"] > 0]["pct_change"].tolist()
        negative_changes = df[df["pct_change"] < 0]["pct_change"].tolist()

        # Calculate metrics
        positive_count = len(positive_changes)
        negative_count = len(negative_changes)
        avg_positive_change = sum(positive_changes) / positive_count if positive_count > 0 else 0
        avg_negative_change = sum(negative_changes) / negative_count if negative_count > 0 else 0

        # Return summary metrics
        return {
            "trading_days_analyzed": len(df),
            "positive_days": positive_count,
            "average_positive_change": round(avg_positive_change, 2),
            "negative_days": negative_count,
            "average_negative_change": round(avg_negative_change, 2)
        }

    except Exception as e:
        return {"error": str(e)}

def calculate_option_profit_or_loss(option_contract, percent_change):
    """
    Calculates the profit or loss for an options contract based on a given percentage change in the underlying stock price.
    
    Parameters:
        option_contract (dict): The options contract data (must include 'strike_price', 'ask_price', 'delta').
        percent_change (float): The percentage change in the underlying stock price.

    Returns:
        dict: A dictionary with the calculated profit or loss and relevant information.
    """
    try:
        # Extract necessary data from the option contract
        ask_price = float(option_contract.get('ask_price'))  # Price to purchase the option
        delta = float(option_contract.get('delta', 0))       # Delta of the option
        current_price = float(option_contract.get('current_price'))  # Current stock price
        
        if delta == 0:
            print("Delta is missing or zero; results may not be accurate.")
        
        # Simulate stock price change
        stock_price_change = current_price * (percent_change / 100)
        
        # Calculate expected option price change using delta
        option_price_change = delta * stock_price_change * 100  # Scaled for contract (100 shares)
        
        # Calculate profit or loss
        profit_or_loss = option_price_change  # Profit is directly proportional to the delta impact

        return {
            "ask_price": ask_price * 100,  # Total cost of the contract
            "percent_change": percent_change,
            "stock_price_change": round(stock_price_change, 2),
            "option_price_change": round(option_price_change, 2),
            "profit_or_loss": round(profit_or_loss, 2)
        }

    except Exception as e:
        print(f"Error calculating option profit or loss: {e}")
        return None


def display_option_profit_or_loss(selected_options, percent_change):
    """
    Displays the profit or loss for the first in-the-money option contract based on the percentage change.

    Parameters:
        selected_options (list): List of options contracts (filtered ITM and OTM).
        percent_change (float): The percentage change in the underlying stock price.

    Returns:
        None
    """
    if not selected_options or len(selected_options) == 0:
        print("No options available to calculate profit or loss.")
        return

    # Take the first in-the-money option
    itm_option = selected_options[0]
    itm_option['current_price'] = 349.16  # Example: Replace this with the actual stock price from your API
    result = calculate_option_profit_or_loss(itm_option, percent_change)
    
    if result:
        print("\nOption Profit or Loss Analysis:")
        print(f"  Ask Price (Contract Cost): ${result['ask_price']}")
        print(f"  Percentage Change: {result['percent_change']}%")
        print(f"  Stock Price Change: ${result['stock_price_change']}")
        print(f"  Option Price Change: ${result['option_price_change']}")
        print(f"  Profit or Loss: ${result['profit_or_loss']}\n")





def main():
    """
    Main function to log in and evaluate options Greeks.
    """
    if login_to_robinhood():
        symbol = input("Enter the stock ticker symbol: ").strip().upper()
        option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()

        # Ask for month instead of full expiration date
        year_month = input("Enter the expiration month (YYYY-MM, e.g., 2025-01): ").strip()

        # Fetch expiration dates for the selected month
        expiration_date = get_expiration_date_for_month(symbol, year_month)
        if not expiration_date:
            print("No valid expiration date selected. Exiting.")
            return

        print(f"Using expiration date: {expiration_date}")
        selected_options = fetch_and_evaluate_greeks(symbol, expiration_date, option_type)

        # Fetch last 90 days of historical data (3 months)
        historical_data = fetch_historical_closing_prices(symbol, span="3month")
        if historical_data:
            print(f"Working on the following ticker: {symbol}:")
            #for record in historical_data:
                #print(f"Date: {record['date']}, Close Price: {record['close_price']}")
            

        analysis = analyze_daily_percentage_changes_90_days(historical_data)
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
        else:
            print(f"\nDaily Percentage Change Analysis (Last 90 Days):")
            print(f"  Trading Days Analyzed: {analysis['trading_days_analyzed']}")
            print(f"  Positive Days: {analysis['positive_days']}")
            print(f"  Average Positive Change: {analysis['average_positive_change']}%")
            print(f"  Negative Days: {analysis['negative_days']}")
            print(f"  Average Negative Change: {analysis['average_negative_change']}%")

        percent_change = 1.0
        display_option_profit_or_loss(selected_options, percent_change)

    else:
        print(f"No historical data available for {symbol}.")
        


if __name__ == "__main__":
    main()