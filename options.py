import robin_stocks.robinhood as r
import os
import yfinance as yf
import re
from src.robinhood_login import login_to_robinhood
from src.fetch_price import fetch_current_price
from src.fetch_greeks import fetch_and_evaluate_greeks
from src.check_expiration import get_expiration_date_for_month
from src.historical_prices import fetch_historical_closing_prices
from src.daily_change import analyze_daily_percentage_changes_90_days
from src.calculate_profit import calculate_option_profit_or_loss
from src.display_profit import display_option_profit_or_loss
from src.get_vix import get_vix_value
from src.pcr import get_put_call_ratio_60_days
from src.get_google import fetch_google_news
from src.openai import get_ai_analysis, analyze_sentiment_google_results
from src.sentiment_analysis import sentiment_analysis
 
selected_options = []
symbol = ""
profit_or_loss = 0
ask_price = 0
# Initialize variables with default values
put_call_ratio = "N/A"  # Default if not fetched
vix_value = "N/A"       # Default if not fetched
profit_loss_result = None  # Default if no profit/loss is calculated





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