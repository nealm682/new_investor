# run using this command:  streamlit run ui.py [ARGUMENTS]

import streamlit as st
import robin_stocks.robinhood as r
import pandas as pd
import altair as alt
from dotenv import load_dotenv
import os
import yfinance as yf
import openai
import re
from datetime import datetime, timedelta
import requests
from options import fetch_and_evaluate_greeks, get_put_call_ratio_60_days, get_vix_value, fetch_historical_closing_prices, analyze_daily_percentage_changes_90_days, fetch_google_news, analyze_sentiment_google_results, fetch_and_evaluate_greeks

# Load environment variables from .env file
load_dotenv()

USERNAME = os.getenv("ROBINHOOD_USERNAME")
PASSWORD = os.getenv("ROBINHOOD_PASSWORD")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
api_key = os.getenv("GOOGLE_API_KEY")

# Streamlit UI setup
st.title("Options Analysis Dashboard")
st.sidebar.header("User Inputs")

# User inputs from the sidebar
symbol = st.sidebar.text_input("Enter the stock ticker symbol:", value="AAPL")
option_type = st.sidebar.selectbox("Option Type", options=["call", "put"])
expiration_month = st.sidebar.text_input("Enter expiration month (YYYY-MM):", value="2025-01")

# Robinhood login
def login_to_robinhood():
    try:
        login = r.login(username=USERNAME, password=PASSWORD)
        st.sidebar.success("Login successful.")
        return login
    except Exception as e:
        st.sidebar.error(f"Failed to log in: {e}")
        return None

# Function to fetch expiration dates and present them to the user
def get_expiration_date_for_month(symbol, month):
    try:
        chains = r.options.get_chains(symbol)
        expiration_dates = chains.get('expiration_dates', [])
        month_dates = [date for date in expiration_dates if date.startswith(month)]
        if not month_dates:
            st.warning(f"No expiration dates found for {symbol} in {month}.")
            return None
        selected_date = st.sidebar.selectbox("Select an expiration date:", month_dates)
        return selected_date
    except Exception as e:
        st.error(f"Error fetching expiration dates for {symbol}: {e}")
        return None

# Display options data
def display_options_data(options_data):
    if options_data:
        for option in options_data:
            st.write(f"Strike Price: {option['strike_price']}")
            st.write(f"Delta: {option.get('delta', 'N/A')}")
            st.write(f"Gamma: {option.get('gamma', 'N/A')}")
            st.write(f"Theta: {option.get('theta', 'N/A')}")
            st.write(f"Vega: {option.get('vega', 'N/A')}")
            st.write("---")
    else:
        st.warning("No options data to display.")

# Login to Robinhood
if login_to_robinhood():
    expiration_date = get_expiration_date_for_month(symbol, expiration_month)
    if expiration_date:
        st.sidebar.text(f"Using expiration date: {expiration_date}")

        # Fetching Greeks and other data
        options_data = fetch_and_evaluate_greeks(symbol, expiration_date, option_type)
        st.header("Options Data")
        display_options_data(options_data)

        # Fetch historical data
        historical_data = fetch_historical_closing_prices(symbol, span="3month")
        if historical_data:
            df_historical = pd.DataFrame(historical_data)
            df_historical['date'] = pd.to_datetime(df_historical['date'])

            st.header("Historical Closing Prices")
            # Create an Altair chart to control the size
            chart = alt.Chart(df_historical).mark_line().encode(
                x='date:T',
                y='close_price:Q'
            ).properties(
                width=600,  # Set desired width
                height=300  # Set desired height
            )
            st.altair_chart(chart)

        # Perform analysis on historical data
        if historical_data:
            analysis = analyze_daily_percentage_changes_90_days(historical_data)
            if "error" not in analysis:
                st.header("Daily Percentage Change Analysis (Last 90 Days)")
                st.write(f"Trading Days Analyzed: {analysis['trading_days_analyzed']}")
                st.write(f"Positive Days: {analysis['positive_days']}")
                st.write(f"Average Positive Change: {analysis['average_positive_change']}%")
                st.write(f"Negative Days: {analysis['negative_days']}")
                st.write(f"Average Negative Change: {analysis['average_negative_change']}%")

        # Fetch Put/Call Ratio and VIX value
        put_call_ratio = get_put_call_ratio_60_days(symbol)
        vix_value = get_vix_value()

        if put_call_ratio:
            st.header("Sentiment Indicators")
            st.write(f"Put/Call Ratio: {put_call_ratio:.2f}")
        if vix_value:
            st.write(f"VIX Value: {vix_value:.2f}")

        # News sentiment analysis
        cx = os.getenv("GOOGLE_CX")
        articles = fetch_google_news(symbol, api_key, cx)
        if articles:
            st.header("News Sentiment Analysis")
            analyzed_articles = analyze_sentiment_google_results(articles)
            for article in analyzed_articles:
                st.write(f"Title: {article['title']}")
                st.write(f"Sentiment: {article['sentiment']}")
                st.write(f"URL: {article['link']}")
                st.write("---")

else:
    st.sidebar.error("Unable to log in to Robinhood. Please check your credentials.")
