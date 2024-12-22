
def calculate_option_profit_or_loss(option_contract, percent_change):
    """
    Calculates the profit or loss for an options contract based on a given percentage change in the underlying stock price.
    
    Parameters:
        option_contract (dict): The options contract data (must include 'strike_price', 'ask_price', 'delta').
        percent_change (float): The percentage change in the underlying stock price.

    Returns:
        dict: A dictionary with the calculated profit or loss and relevant information.
    """
    try:
        # Extract necessary data from the option contract
        ask_price = float(option_contract.get('ask_price', 0))  # Price to purchase the option per share
        delta = float(option_contract.get('delta', 0))          # Delta of the option
        current_price = float(option_contract.get('current_price', 0))  # Current stock price

        if not current_price or not ask_price:
            raise ValueError("Current price or ask price is missing or zero.")

        # Simulate stock price change
        stock_price_change = current_price * (percent_change / 100)
        
        # Calculate expected option price change per share using delta
        option_price_change_per_share = delta * stock_price_change
        
        # Calculate option price change per contract (100 shares)
        option_price_change_per_contract = option_price_change_per_share * 100
        
        # Calculate profit or loss
        profit_or_loss = option_price_change_per_contract

        return {
            "ask_price": ask_price * 100,  # Total cost of the contract
            "percent_change": percent_change,
            "stock_price_change": round(stock_price_change, 2),
            "option_price_change_per_share": round(option_price_change_per_share, 2),
            "profit_or_loss": round(profit_or_loss, 2)
        }
    except Exception as e:
        print(f"Error calculating option profit or loss: {e}")
        return None