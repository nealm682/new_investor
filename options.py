import robin_stocks.robinhood as r
import pandas as pd
from dotenv import load_dotenv
import os
import yfinance as yf
import openai
import re



selected_options = []
symbol = ""
profit_or_loss = 0
ask_price = 0
# Initialize variables with default values
put_call_ratio = "N/A"  # Default if not fetched
vix_value = "N/A"       # Default if not fetched
profit_loss_result = None  # Default if no profit/loss is calculated

# Load environment variables from .env file
load_dotenv()

USERNAME = os.getenv("ROBINHOOD_USERNAME")
PASSWORD = os.getenv("ROBINHOOD_PASSWORD")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        #selected_options = (itm_options[-2:] if itm_options else []) + (otm_options[:2] if otm_options else [])
        # Select the first in-the-money option
        first_itm_option = itm_options[-1] if itm_options else None

        # Select the first out-of-the-money option
        first_otm_option = otm_options[0] if otm_options else None

        # Combine selected options
        selected_options = []
        if first_itm_option:
            selected_options.append(first_itm_option)
        if first_otm_option:
            selected_options.append(first_otm_option)

        print(f"\nFiltering the first {option_type.capitalize()} Options 'in the money' for {symbol} (Expiration: {expiration_date}):")
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
        ask_price = float(option_contract.get('ask_price'))  # Price to purchase the option per share
        delta = float(option_contract.get('delta', 0))       # Delta of the option
        current_price = float(option_contract.get('current_price'))  # Current stock price

        if delta == 0:
            print("Delta is missing or zero; results may not be accurate.")
        
        # Simulate stock price change
        stock_price_change = current_price * (percent_change / 100)
        
        # Calculate expected option price change per share using delta
        option_price_change_per_share = delta * stock_price_change
        
        # Calculate option price change per contract (100 shares)
        option_price_change_per_contract = option_price_change_per_share * 100
        
        # Calculate profit or loss
        profit_or_loss = option_price_change_per_contract
        #print(f"Debug: profit_or_loss = {profit_or_loss}")

        return {
            "ask_price": ask_price * 100,  # Total cost of the contract
            "percent_change": percent_change,
            "stock_price_change": round(stock_price_change, 2),
            "option_price_change_per_share": round(option_price_change_per_share, 2),
            "option_price_change_per_contract": round(option_price_change_per_contract, 2),
            "profit_or_loss": round(profit_or_loss, 2)
        }
        
    except Exception as e:
        print(f"Error calculating option profit or loss: {e}")
        return None


def display_option_profit_or_loss(selected_options, percent_change, symbol):
    if not selected_options or len(selected_options) == 0:
        print("No options available to calculate profit or loss.")
        return None

    current_price = fetch_current_price(symbol)
    if current_price is None:
        print(f"Failed to fetch the current stock price for {symbol}.")
        return None

    itm_option = selected_options[0]
    itm_option['current_price'] = current_price
    result = calculate_option_profit_or_loss(itm_option, percent_change)

    if result:
        ask_price = result['ask_price']
        profit_or_loss = result['profit_or_loss']

        print("\nOption Profit or Loss Analysis:")
        print(f"  Ask Price (Contract Cost): ${ask_price}")
        print(f"  Percentage Change: {result['percent_change']}%")
        print(f"  Stock Price Change: ${result['stock_price_change']}")
        print(f"  Option Price Change per Share: ${result['option_price_change_per_share']}")
        print(f"  Option Price Change per Contract: ${result['option_price_change_per_contract']}")
        print(f"  Profit or Loss for the contract: ${profit_or_loss}")

        # Calculate Total Return Percentage
        if ask_price == 0:
            print("Cannot calculate total return percentage because ask price is zero.")
        else:
            total_return_percentage = (profit_or_loss / ask_price) * 100
            print(f"  Total Return Percentage: {round(total_return_percentage, 2)}%\n")

        # Return the result for use in summary_data
        return result
    else:
        return None




def get_put_call_ratio_yfinance(symbol, expiration_date):
    """
    Calculates the put/call ratio for a given ticker and expiration date using yfinance.

    Parameters:
        symbol (str): The stock ticker symbol (e.g., "AAPL").
        expiration_date (str): The expiration date in "YYYY-MM-DD" format.

    Returns:
        float: The put/call ratio.
    """
    try:
        # Fetch the options chain for the specified expiration date
        ticker = yf.Ticker(symbol)
        options_chain = ticker.option_chain(expiration_date)

        # Extract calls and puts DataFrames
        calls = options_chain.calls
        puts = options_chain.puts

        # Sum the volume for calls and puts
        total_call_volume = calls['volume'].fillna(0).sum()
        total_put_volume = puts['volume'].fillna(0).sum()

        # Debugging statements
        print(f"Total Call Volume: {total_call_volume}")
        print(f"Total Put Volume: {total_put_volume}")

        # Calculate the Put/Call Ratio
        if total_call_volume == 0:
            print("Call volume is zero. Cannot calculate Put/Call Ratio.")
            return None

        put_call_ratio = total_put_volume / total_call_volume
        print(f"Put/Call Ratio for {symbol} on {expiration_date}: {put_call_ratio:.2f}")
        return put_call_ratio

    except Exception as e:
        print(f"Error calculating put/call ratio for {symbol} using yfinance: {e}")
        return None




def get_vix_value():
    """
    Fetches the current VIX index value using yfinance.

    Returns:
        float: The current VIX value.
    """
    try:
        vix = yf.Ticker("^VIX")
        vix_data = vix.history(period="1d")
        current_vix = vix_data['Close'].iloc[-1]
        print(f"\nCurrent VIX Value: {current_vix:.2f}")
        return current_vix
    except Exception as e:
        print(f"Error fetching VIX value: {e}")
        return None


def sentiment_analysis(put_call_ratio, vix_value):
    """
    Analyzes sentiment indicators to provide trading insights.

    Parameters:
        put_call_ratio (float): The put/call ratio for the ticker.
        vix_value (float): The current VIX index value.

    Returns:
        None
    """
    insights = []

    # Analyze put/call ratio
    # Analyze put/call ratio
    if put_call_ratio is not None:
        if put_call_ratio < 1.0:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests bullish sentiment, indicating that more call options are traded than puts, reflecting optimism among investors."
            )
        elif 1.0 <= put_call_ratio <= 1.5:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests neutral to mildly bearish sentiment, with a relatively balanced demand for puts and calls."
            )
        elif 1.5 < put_call_ratio <= 2.0:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests bearish sentiment, indicating more put options traded than calls, reflecting caution or a hedging behavior among investors."
            )
        else:  # Above 2.0
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates strong bearish sentiment, suggesting heightened fear or hedging activity, with a significant preference for puts over calls."
            )

    # Analyze VIX value
    if vix_value is not None:
        if vix_value < 12:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates low market volatility, reflecting complacency or confidence among market participants."
            )
        elif 12 <= vix_value <= 20:
            insights.append(
                f"The VIX value of {vix_value:.2f} is within the normal range, suggesting moderate volatility and typical market conditions."
            )
        elif 20 < vix_value <= 30:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates elevated market volatility, reflecting uncertainty or potential market stress."
            )
        else:  # Above 30
            insights.append(
                f"The VIX value of {vix_value:.2f} signals extreme market volatility, indicating significant fear and potential market turmoil."
            )


    # Combine insights
    print("\nSentiment Analysis:")
    for insight in insights:
        print(f"  - {insight}")


# Example function to call OpenAI API
def get_ai_analysis(summary_data):
    try:
        # Construct the prompt
        messages = [
            {
                "role": "system",
                "content": """You are a financial analyst specializing in options and market sentiment analysis. 
                Interpret the data provided using the following context and guidelines:

                - **Put/Call Ratio**:
                - **Below 1.0**: Bullish sentiment; more call options traded, indicating optimism.
                - **1.0 to 1.5**: Neutral to mildly bearish sentiment.
                - **Above 1.5**: Bearish sentiment; more put options traded, indicating caution or fear.

                - **VIX Value**:
                - **Below 12**: Low market volatility, complacency.
                - **12 to 20**: Normal market conditions, moderate volatility.
                - **Above 20**: Elevated volatility, uncertainty.
                - **Above 30**: Extreme fear and market stress.

                - **Options Greeks**:
                - **Delta**: Indicates sensitivity to price changes; close to 1.0 suggests high correlation with stock movements, while near 0.5 represents at-the-money options. Highlight significant deviations.
                - **Gamma**: Measures Delta sensitivity; high Gamma signals sharp changes in Delta with stock movement. Mention if unusually high.
                - **Theta**: Reflects time decay; negative Theta is standard but significant rates can imply steep value loss over time. Highlight unusual cases.
                - **Vega**: Reflects sensitivity to volatility changes; high Vega can signal volatility-driven value shifts. Mention only if it significantly impacts decision-making.

                - **Historical Stock Performance**:
                - Assess the consistency and volatility of stock returns over the observed period.
                - Highlight stocks with more positive trading days and stable gains as stronger candidates, and flag high-volatility stocks for caution.

                Use these ranges and guidelines to ground your interpretation and provide a well-reasoned summary. 
                Highlight potential insights or risks based on the data trends and explain how the numbers align with broader market conditions or stock-specific sentiment.

                Your task is to assess whether the presented options contract represents a favorable investment opportunity. 
                Provide an expert opinion with actionable insights to guide decision-making. Focus on whether the data supports a favorable risk/reward profile."""
            },
            {
                "role": "user",
                "content": f"Based on the following data, evaluate the option and provide your expert opinion:\n\n{summary_data}\n\n"
                        "Interpret the Greeks only if they stand out or are unusual. For example:\n"
                        "- Delta: Highlight only if it significantly affects price sensitivity or risk.\n"
                        "- Gamma: Mention if it indicates sharp changes in Delta.\n"
                        "- Theta: Discuss only if the rate of time decay is extreme or negligible.\n"
                        "- Vega: Address only if the option's value is highly sensitive to volatility changes.\n\n"
                        "For Put/Call ratio and VIX, provide market sentiment insights. For historical price performance, "
                        "comment on consistency and volatility of returns. Finally, make a recommendation on whether this option seems "
                        "like a good investment based on the overall data."
            }
        ]



        # Create the chat completion using the client
        response = client.chat.completions.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" or other supported models if "gpt-4" is unavailable
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        #print(response)
        # Extract and return the assistant's reply
        ai_response = response.choices[0].message.content


        print("\nAI Analysis:")
        print(ai_response)
        return ai_response

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None




def main():
    """
    Main function to log in and evaluate options Greeks.
    """
    if login_to_robinhood():
        symbol = input("Enter the stock ticker symbol: ").strip().upper()
        while not symbol.isalpha():
            print("Invalid symbol. Please enter a valid stock ticker symbol.")
            symbol = input("Enter the stock ticker symbol: ").strip().upper()

        option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()
        while option_type not in ['call', 'put']:
            print("Invalid option type. Please enter 'call' or 'put'.")
            option_type = input("Enter the option type ('call' or 'put'): ").strip().lower()

        # Ask for month instead of full expiration date
        year_month = input("Enter the expiration month (YYYY-MM, e.g., 2025-01): ").strip()
        while not re.match(r"\d{4}-\d{2}", year_month):
            print("Invalid format. Please use 'YYYY-MM' format.")
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
        display_option_profit_or_loss(selected_options, percent_change, symbol)

        # Fetch Put/Call Ratio
        put_call_ratio = get_put_call_ratio_yfinance(symbol, expiration_date)
        if put_call_ratio is None:
            print("Failed to fetch Put/Call Ratio.")
        else:
            print(f"Put/Call Ratio: {put_call_ratio}")

        # Fetch VIX Value
        vix_value = get_vix_value()
        if vix_value is None:
            print("Failed to fetch VIX Value.")
        else:
            print(f"VIX Value: {vix_value}")

        # Prepare summary data for AI analysis
        summary_data = f"""
Stock Symbol: {symbol}
Option Type: {option_type}
Expiration Date: {expiration_date}

Selected Options and Greeks:
"""

        # Include Greeks for each selected option
        if selected_options:
            for option in selected_options:
                strike_price = option.get('strike_price', 'N/A')
                delta = option.get('delta', 'N/A')
                gamma = option.get('gamma', 'N/A')
                theta = option.get('theta', 'N/A')
                vega = option.get('vega', 'N/A')
                summary_data += f"""
Strike Price: {strike_price}
  Delta: {delta}
  Gamma: {gamma}
  Theta: {theta}
  Vega: {vega}
"""

        # Add historical analysis
        if analysis and "error" not in analysis:
            summary_data += f"""
Historical Price Analysis (Last 90 Days):
  Trading Days Analyzed: {analysis['trading_days_analyzed']}
  Positive Days: {analysis['positive_days']}
  Average Positive Change: {analysis['average_positive_change']}%
  Negative Days: {analysis['negative_days']}
  Average Negative Change: {analysis['average_negative_change']}%
"""

        # Add sentiment analysis
        summary_data += f"""
        Sentiment Indicators:
        Put/Call Ratio: {put_call_ratio if put_call_ratio is not None else 'N/A'}
        VIX Value: {vix_value if vix_value is not None else 'N/A'}
        """

        # Include profit or loss estimation
        if profit_loss_result:
            summary_data += f"""
Option Profit or Loss Analysis:
  Ask Price (Contract Cost): ${profit_loss_result['ask_price']}
  Percentage Change: {profit_loss_result['percent_change']}%
  Stock Price Change: ${profit_loss_result['stock_price_change']}
  Option Price Change per Share: ${profit_loss_result['option_price_change_per_share']}
  Option Price Change per Contract: ${profit_loss_result['option_price_change_per_contract']}
  Profit or Loss for the Contract: ${profit_loss_result['profit_or_loss']}
"""

        # Call the AI analysis function
        get_ai_analysis(summary_data)





    else:
        print(f"No historical data available for {symbol}.")
        


if __name__ == "__main__":
    main()