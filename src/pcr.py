import streamlit as st
from datetime import datetime, timedelta
import yfinance as yf

def get_put_call_ratio_60_days(symbol):
    """
    Calculates the aggregated put/call ratio for a given ticker over the next 60 days using yfinance.

    Parameters:
        symbol (str): The stock ticker symbol (e.g., "AAPL").

    Returns:
        float: The aggregated put/call ratio over the next 60 days, or None if it cannot be calculated.
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
            st.write("No expiration dates within the next 60 days.")
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
                st.write(f"Error fetching options chain for {expiration_date}: {e}")
                continue

        # Debug / status messages
        st.write(f"Total Call Volume (60 days): {total_call_volume}")
        st.write(f"Total Put Volume (60 days): {total_put_volume}")

        # Calculate the Put/Call Ratio
        if total_call_volume == 0:
            st.write("Call volume is zero. Cannot calculate Put/Call Ratio.")
            return None

        put_call_ratio = total_put_volume / total_call_volume
        st.write(f"Aggregated Put/Call Ratio for {symbol} over the next 60 days: {put_call_ratio:.2f}")
        return put_call_ratio

    except Exception as e:
        st.write(f"Error calculating aggregated put/call ratio for {symbol}: {e}")
        return None

'''
from datetime import datetime, timedelta
import yfinance as yf

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


'''