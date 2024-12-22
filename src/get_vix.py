import requests
import yfinance as yf

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


