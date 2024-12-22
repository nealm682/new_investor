import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

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
    



