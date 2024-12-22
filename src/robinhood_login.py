import robin_stocks.robinhood as r
from dotenv import load_dotenv
import os

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