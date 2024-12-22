import robin_stocks.robinhood as r

def get_expiration_date_for_month(symbol, month):
    """ 
    Fetches expiration dates for the given ticker and filters them for the specified month.
    Returns a list of matching expiration dates (e.g., ["2025-01-03", "2025-01-10", ...]).
    
    :param symbol: Stock ticker symbol (str), e.g. "AAPL"
    :param month: Year-month in 'YYYY-MM' format (str), e.g. "2025-01"
    :return: list of expiration date strings that start with the provided month, 
             or an empty list if none are found or on error.
    """
    try:
        # Fetch all expiration dates for the symbol
        chains = r.options.get_chains(symbol)
        expiration_dates = chains.get('expiration_dates', [])
        
        # Filter dates for the specified month (e.g., "2025-01")
        month_dates = [date for date in expiration_dates if date.startswith(month)]
        if not month_dates:
            # Return an empty list if none match
            return []

        # Return the filtered list (no prints, no inputs)
        return month_dates
    except Exception:
        # If there's an error, just return an empty list
        return []


'''
import robin_stocks.robinhood as r

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

'''