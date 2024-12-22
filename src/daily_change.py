import pandas as pd
from datetime import datetime

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