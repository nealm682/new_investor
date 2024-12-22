import robin_stocks.robinhood as r

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