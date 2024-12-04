import robin_stocks.robinhood as r
import pandas as pd
from dotenv import load_dotenv
import os
import yfinance as yf
import openai
import re
from datetime import datetime, timedelta
import requests



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
api_key = os.getenv("GOOGLE_API_KEY")

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
        ask_price = float(option_contract.get('ask_price', 0))  # Price to purchase the option per share
        delta = float(option_contract.get('delta', 0))          # Delta of the option
        current_price = float(option_contract.get('current_price', 0))  # Current stock price

        if not current_price or not ask_price:
            raise ValueError("Current price or ask price is missing or zero.")

        # Simulate stock price change
        stock_price_change = current_price * (percent_change / 100)
        
        # Calculate expected option price change per share using delta
        option_price_change_per_share = delta * stock_price_change
        
        # Calculate option price change per contract (100 shares)
        option_price_change_per_contract = option_price_change_per_share * 100
        
        # Calculate profit or loss
        profit_or_loss = option_price_change_per_contract

        return {
            "ask_price": ask_price * 100,  # Total cost of the contract
            "percent_change": percent_change,
            "stock_price_change": round(stock_price_change, 2),
            "option_price_change_per_share": round(option_price_change_per_share, 2),
            "profit_or_loss": round(profit_or_loss, 2)
        }
    except Exception as e:
        print(f"Error calculating option profit or loss: {e}")
        return None




def display_option_profit_or_loss(selected_options, percent_changes, symbol):
    """
    Displays the profit or loss for an options contract based on multiple percentage changes in the stock price.

    Parameters:
        selected_options (list): List of options contracts.
        percent_changes (list): List of percentage changes to simulate (e.g., [1, 10, 20]).
        symbol (str): The stock ticker symbol.

    Returns:
        None
    """
    if not selected_options or len(selected_options) == 0:
        print("No options available to calculate profit or loss.")
        return

    current_price = fetch_current_price(symbol)
    if current_price is None:
        print(f"Failed to fetch the current stock price for {symbol}.")
        return

    # Use the first in-the-money option for calculations
    itm_option = selected_options[0]
    itm_option['current_price'] = current_price

    # Display Ground Truth
    print("\nOption Profit or Loss Analysis:")
    print(f"  Current Price of Underlying Stock: ${current_price:.2f}")
    print(f"  Current Value of the Contract: ${float(itm_option['ask_price']) * 100:.2f}\n")

    # Iterate through percentage changes
    for percent_change in percent_changes:
        result = calculate_option_profit_or_loss(itm_option, percent_change)
        if result:
            print(f"Percentage Change: {result['percent_change']}%")
            print(f"  Stock Price Change: ${result['stock_price_change']}")
            print(f"  Profit or Loss for the Contract: ${result['profit_or_loss']}")
            total_return_percentage = (result['profit_or_loss'] / result['ask_price']) * 100
            print(f"  Total Return Percentage: {round(total_return_percentage, 2)}%\n")




def get_put_call_ratio_60_days(symbol):
    """
    Calculates the aggregated put/call ratio for a given ticker over the next 60 days using yfinance.

    Parameters:
        symbol (str): The stock ticker symbol (e.g., "AAPL").

    Returns:
        float: The aggregated put/call ratio over the next 60 days.
    """
    try:
        # Fetch the ticker object
        ticker = yf.Ticker(symbol)

        # Get all expiration dates
        expiration_dates = ticker.options

        # Filter expiration dates to include only those within the next 60 days
        today = datetime.now()
        cutoff_date = today + timedelta(days=60)
        filtered_expiration_dates = [
            date for date in expiration_dates if datetime.strptime(date, "%Y-%m-%d") <= cutoff_date
        ]

        if not filtered_expiration_dates:
            print("No expiration dates within the next 60 days.")
            return None

        # Initialize totals
        total_call_volume = 0
        total_put_volume = 0

        # Loop through filtered expiration dates and calculate volumes
        for expiration_date in filtered_expiration_dates:
            try:
                # Fetch the options chain for each expiration date
                options_chain = ticker.option_chain(expiration_date)

                # Sum the volume for calls and puts
                calls = options_chain.calls
                puts = options_chain.puts
                total_call_volume += calls['volume'].fillna(0).sum()
                total_put_volume += puts['volume'].fillna(0).sum()

            except Exception as e:
                print(f"Error fetching options chain for {expiration_date}: {e}")
                continue

        # Debugging statements
        print(f"Total Call Volume (60 days): {total_call_volume}")
        print(f"Total Put Volume (60 days): {total_put_volume}")

        # Calculate the Put/Call Ratio
        if total_call_volume == 0:
            print("Call volume is zero. Cannot calculate Put/Call Ratio.")
            return None

        put_call_ratio = total_put_volume / total_call_volume
        print(f"Aggregated Put/Call Ratio for {symbol} over the next 60 days: {put_call_ratio:.2f}")
        return put_call_ratio

    except Exception as e:
        print(f"Error calculating aggregated put/call ratio for {symbol}: {e}")
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


def fetch_google_news(ticker, api_key, cx):
    """
    Fetches recent stock news articles using the Google Custom Search JSON API.

    Parameters:
        ticker (str): Stock ticker symbol (e.g., "AAPL").
        api_key (str): Your Google API key.
        cx (str): Your Programmable Search Engine ID.

    Returns:
        list: A list of dictionaries containing article titles, links, and snippets.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    query = f"{ticker} stock news"  # Search query

    params = {
        "q": query,
        "key": api_key,
        "cx": cx,  # Include the Search Engine ID
        "num": 5  # Fetch top 5 articles
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        
        # Parse and return relevant information
        return [
            {"title": item["title"], "link": item["link"], "snippet": item["snippet"]}
            for item in results
        ]
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []



def analyze_sentiment_google_results(articles):
    """
    Performs sentiment analysis on Google Search results using OpenAI.

    Parameters:
        articles (list): A list of dictionaries containing article metadata.

    Returns:
        list: A list of articles with sentiment scores appended.
    """
    results = []

    for article in articles:
        try:
            content = article["title"] + ". " + article["snippet"]
                    # Create the chat completion using the client

            response = openai.chat.completions.create(
                model="gpt-4",  # Use "gpt-3.5-turbo" if "gpt-4" is unavailable
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI tasked with performing sentiment analysis. "
                                   "Classify the sentiment of the provided text as positive, neutral, or negative."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of this text: {content}"
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )


            sentiment = response.choices[0].message.content
            article["sentiment"] = sentiment
            results.append(article)
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            continue

    return results



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
        if put_call_ratio < 0.7:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates bullish sentiment, suggesting optimism as more call options are traded compared to puts."
            )
        elif put_call_ratio == .07:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests neutral sentiment, indicating more puts are being traded compared to calls."
            )
        else:  # Above 2.0
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates strong bearish sentiment, suggesting heightened fear or significant hedging activity."
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
                - The put-call ratio measures market sentiment by dividing the number of traded put options by the number of traded call options. A put-call ratio of 1 indicates that the number of buyers of calls is the same as the number of buyers for puts. However, a ratio of 1 is not an accurate starting point to measure sentiment in the market because there are normally more investors buying calls than buying puts. So, an average put-call ratio of 0.7 for equities is considered a good basis for evaluating sentiment. Low ratio numbers, like 0.2-0.3, suggest market sentiment is extremely bullish, while a reading over 1.2 suggests the market is becoming too bearish and may be due for a bounce. The put/call ratio is a very helpful tool in gauging whether the market outlook is bullish or bearish for a particular security or an index itself. 
                - 
                - **Equal to .07**: Nuetral sentiment; investors are balanced between put and call options.
                - **Greater than 0.7, or exceeding 1**: means that equity traders are buying more puts than calls. It suggests that bearish sentiment is building in the market. Investors are either speculating that the market will move lower or are hedging their portfolios in case there is a sell-off.
                - **Below .07**: A falling put-call ratio, or below 0.7 and approaching 0.5, is considered a bullish indicator. It means more calls are being bought versus puts.

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



        # Fetch News Articles and Analyze Sentiment
        api_key = os.getenv("GOOGLE_API_KEY")
        cx = os.getenv("GOOGLE_CX")
        print(f"\nFetching recent news for {symbol}...")
        articles = fetch_google_news(symbol, api_key, cx)

        if articles:
            print("\nAnalyzing news sentiment...")
            analyzed_articles = analyze_sentiment_google_results(articles)
            print("\nNews Sentiment Analysis:")
            for article in analyzed_articles:
                print(f"Title: {article['title']}")
                print(f"Sentiment: {article['sentiment']}")
                print(f"URL: {article['link']}\n")
        else:
            print("No news articles found.")


        percent_change = [1, 10, 20]
        display_option_profit_or_loss(selected_options, percent_change, symbol)

        # Fetch Put/Call Ratio
        put_call_ratio = get_put_call_ratio_60_days(symbol)
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


        # Include news sentiment analysis
        if articles:
            analyzed_articles = analyze_sentiment_google_results(articles)
            news_summary = "\nNews Sentiment Analysis:\n"
            for article in analyzed_articles:
                news_summary += f"Title: {article['title']}\n"
                news_summary += f"Sentiment: {article['sentiment']}\n"
                news_summary += f"URL: {article['link']}\n\n"
            summary_data += news_summary
        else:
            summary_data += "\nNews Sentiment Analysis:\nNo recent news articles found.\n"



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