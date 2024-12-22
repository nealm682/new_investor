# streamlit run options1.py [ARGUMENTS]
import os
import re
import streamlit as st
import robin_stocks.robinhood as r
import yfinance as yf

# -- Your custom modules
from src.robinhood_login import login_to_robinhood
from src.fetch_price import fetch_current_price
from src.fetch_greeks import fetch_and_evaluate_greeks
from src.check_expiration import get_expiration_date_for_month  # We'll wrap its return in a list
from src.historical_prices import fetch_historical_closing_prices
from src.daily_change import analyze_daily_percentage_changes_90_days
from src.calculate_profit import calculate_option_profit_or_loss
from src.display_profit import display_option_profit_or_loss
from src.get_vix import get_vix_value
from src.pcr import get_put_call_ratio_60_days
from src.get_google import fetch_google_news
from src.openai import get_ai_analysis, analyze_sentiment_google_results
from src.sentiment_analysis import sentiment_analysis

# Globals (optional)
put_call_ratio = "N/A"
vix_value = "N/A"
profit_loss_result = None


def main():
    # -----------------------
    # SIDEBAR FOR CREDENTIALS
    # -----------------------
    with st.sidebar:
        st.subheader("Enter Your Credentials")

        # 1) Robinhood
        st.markdown("**Robinhood** – [https://robinhood.com/](https://robinhood.com/)")
        rh_username = st.text_input("Robinhood Username", "", key="rh_user")
        rh_password = st.text_input("Robinhood Password", "", type="password", key="rh_pass")

        # 2) OpenAI
        st.markdown("**OpenAI** – [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)")
        openai_api_key = st.text_input("OpenAI API Key", "", type="password", key="openai_api")

        # 3) Google Search (Custom Search Engine)
        st.markdown("**Google API** – [https://developers.google.com/custom-search/v1/introduction](https://developers.google.com/custom-search/v1/introduction)")
        google_api_key = st.text_input("Google API Key", "", key="google_api")

        st.markdown("**Google CX** – [https://programmablesearchengine.google.com/controlpanel/all](https://programmablesearchengine.google.com/controlpanel/all)")
        google_cx = st.text_input("Google CX", "", key="google_cx")

        if st.button("Save Credentials"):
            os.environ["ROBINHOOD_USERNAME"] = rh_username
            os.environ["ROBINHOOD_PASSWORD"] = rh_password
            os.environ["OPENAI_API_KEY"] = openai_api_key
            os.environ["GOOGLE_API_KEY"] = google_api_key
            os.environ["GOOGLE_CX"] = google_cx

            st.success("Credentials saved to environment variables.")

    # -----------------------
    # MAIN TITLE
    # -----------------------
    st.title("Robinhood Options Analysis")

    # 1. Automatic login to Robinhood upon app launch
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.write("Attempting to log in to Robinhood...")
        login_success = login_to_robinhood()
        if login_success:
            st.session_state["logged_in"] = True
            st.success("Successfully logged in to Robinhood.")
        else:
            st.error("Failed to log in to Robinhood. Please check your credentials.")
            st.stop()

    # 2. User inputs for symbol, option type, and year-month
    st.subheader("Enter your option parameters:")
    symbol_input = st.text_input("Stock Ticker Symbol (e.g. AAPL, TSLA):", "")
    option_type_input = st.selectbox("Option Type:", ["call", "put"])
    year_month_input = st.text_input("Expiration Month (YYYY-MM, e.g., 2025-01):", "")

    # 3. Button to fetch expiration dates
    if st.button("Fetch Expiration Dates"):
        # Validate symbol
        if not symbol_input or not symbol_input.isalpha():
            st.error("Please enter a valid stock ticker symbol (alphabetic only).")
            st.stop()  # Stop for this run (error), user must fix input

        # Validate option type
        if option_type_input not in ['call', 'put']:
            st.error("Invalid option type. Must be 'call' or 'put'.")
            st.stop()

        # Validate year-month format
        if not re.match(r"\d{4}-\d{2}", year_month_input):
            st.error("Invalid format. Please use 'YYYY-MM' (e.g., 2025-01).")
            st.stop()

        # Retrieve expiration(s)
        expiration_data = get_expiration_date_for_month(symbol_input.upper(), year_month_input)

        # Ensure we have a *list* of dates
        # (If get_expiration_date_for_month returns a single string, wrap it)
        if isinstance(expiration_data, str):
            expiration_list = [expiration_data]
        else:
            # We assume it's already a list/None
            expiration_list = expiration_data

        if not expiration_list:
            st.error("No expiration dates returned for that month. Check symbol or month/year.")
            st.stop()
        else:
            # Save them to session state
            st.session_state["symbol"] = symbol_input.upper()
            st.session_state["option_type"] = option_type_input.lower()
            st.session_state["year_month"] = year_month_input
            st.session_state["expiration_dates"] = expiration_list

            st.success(f"Expiration dates fetched! Found {len(expiration_list)} date(s).")

    # 4. If we have fetched expiration dates, display them for selection
    if "expiration_dates" in st.session_state and st.session_state["expiration_dates"]:
        st.subheader("Select an expiration date below:")
        chosen_expiration = st.radio(
            "Expiration Dates",
            st.session_state["expiration_dates"]
        )

        # 5. Button to run the rest of the analysis
        if st.button("Run Analysis with Selected Expiration"):
            symbol = st.session_state["symbol"]
            option_type = st.session_state["option_type"]
            expiration_date = chosen_expiration

            st.write(f"### Running Analysis for {symbol} ({option_type}) expiring {expiration_date}")

            # =========== REPLACE PRINTS WITH st.write() ===========

            # 5a) Fetch & Evaluate Greeks
            selected_options = fetch_and_evaluate_greeks(symbol, expiration_date, option_type)
            st.write("Fetched Greeks for the selected option(s).")

            # 5b) Fetch last 90 days of historical data
            historical_data = fetch_historical_closing_prices(symbol, span="3month")
            if historical_data:
                st.write(f"Fetched 3-month historical data for {symbol}.")

            # 5c) Analyze daily % changes
            analysis = analyze_daily_percentage_changes_90_days(historical_data)
            if "error" in analysis:
                st.write(f"Error: {analysis['error']}")
            else:
                st.write("#### Daily Percentage Change Analysis (Last 90 Days):")
                st.write(f"- Trading Days Analyzed: {analysis['trading_days_analyzed']}")
                st.write(f"- Positive Days: {analysis['positive_days']}")
                st.write(f"- Average Positive Change: {analysis['average_positive_change']}%")
                st.write(f"- Negative Days: {analysis['negative_days']}")
                st.write(f"- Average Negative Change: {analysis['average_negative_change']}%")

            # 5d) Fetch News & Analyze
            api_key = os.getenv("GOOGLE_API_KEY")
            cx = os.getenv("GOOGLE_CX")
            st.write(f"\nFetching recent news for {symbol}...")
            articles = fetch_google_news(symbol, api_key, cx)

            if articles:
                st.write("Analyzing news sentiment...")
                analyzed_articles = analyze_sentiment_google_results(articles)
                st.write("#### News Sentiment Analysis:")
                for article in analyzed_articles:
                    st.write(f"**Title**: {article['title']}")
                    st.write(f"**Sentiment**: {article['sentiment']}")
                    st.write(f"**URL**: {article['link']}\n")
            else:
                st.write("No news articles found.")

            # 5e) Display Option Profit or Loss
            st.write("#### Estimated Profit or Loss for Various % Changes:")
            percent_change = [1, 10, 20]
            display_option_profit_or_loss(selected_options, percent_change, symbol)

            # 5f) Put/Call Ratio
            global put_call_ratio
            put_call_ratio = get_put_call_ratio_60_days(symbol)
            if put_call_ratio is None:
                st.write("Failed to fetch Put/Call Ratio.")
            else:
                st.write(f"Put/Call Ratio: {put_call_ratio}")

            # 5g) VIX Value
            global vix_value
            vix_value = get_vix_value()
            if vix_value is None:
                st.write("Failed to fetch VIX Value.")
            else:
                st.write(f"VIX Value: {vix_value}")

            # 5h) Prepare summary data for AI
            summary_data = f"""
Stock Symbol: {symbol}
Option Type: {option_type}
Expiration Date: {expiration_date}

Selected Options and Greeks:
"""
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

            if analysis and "error" not in analysis:
                summary_data += f"""
Historical Price Analysis (Last 90 Days):
  Trading Days Analyzed: {analysis['trading_days_analyzed']}
  Positive Days: {analysis['positive_days']}
  Average Positive Change: {analysis['average_positive_change']}%
  Negative Days: {analysis['negative_days']}
  Average Negative Change: {analysis['average_negative_change']}%
"""

            summary_data += f"""
Sentiment Indicators:
  Put/Call Ratio: {put_call_ratio if put_call_ratio else 'N/A'}
  VIX Value: {vix_value if vix_value else 'N/A'}
"""

            if articles:
                # Summarize the news
                analyzed_articles = analyze_sentiment_google_results(articles)
                news_summary = "\nNews Sentiment Analysis:\n"
                for article in analyzed_articles:
                    news_summary += f"Title: {article['title']}\n"
                    news_summary += f"Sentiment: {article['sentiment']}\n"
                    news_summary += f"URL: {article['link']}\n\n"
                summary_data += news_summary
            else:
                summary_data += "\nNews Sentiment Analysis:\nNo recent news articles found.\n"

            global profit_loss_result
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

            # 5i) Call AI analysis function
            st.subheader("AI Analysis:")
            ai_answer = get_ai_analysis(summary_data)
            if ai_answer:
                st.write(ai_answer)
            else:
                st.write("No AI response returned.")


if __name__ == "__main__":
    # Initialize session_state variables
    if "expiration_dates" not in st.session_state:
        st.session_state["expiration_dates"] = []

    main()

