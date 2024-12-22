from src.fetch_price import fetch_current_price
from src.calculate_profit import calculate_option_profit_or_loss


def display_option_profit_or_loss(selected_options, percent_changes, symbol):
    """
    Displays the profit or loss for an options contract based on multiple percentage changes in the stock price.

    Parameters:
        selected_options (list): List of options contracts.
        percent_changes (list): List of percentage changes to simulate (e.g., [1, 10, 20]).
        symbol (str): The stock ticker symbol.

    Returns:
        None
    """
    if not selected_options or len(selected_options) == 0:
        print("No options available to calculate profit or loss.")
        return

    current_price = fetch_current_price(symbol)
    if current_price is None:
        print(f"Failed to fetch the current stock price for {symbol}.")
        return

    # Use the first in-the-money option for calculations
    itm_option = selected_options[0]
    itm_option['current_price'] = current_price

    # Display Ground Truth
    print("\nOption Profit or Loss Analysis:")
    print(f"  Current Price of Underlying Stock: ${current_price:.2f}")
    print(f"  Current Value of the Contract: ${float(itm_option['ask_price']) * 100:.2f}\n")

    # Iterate through percentage changes
    for percent_change in percent_changes:
        result = calculate_option_profit_or_loss(itm_option, percent_change)
        if result:
            print(f"Percentage Change: {result['percent_change']}%")
            print(f"  Stock Price Change: ${result['stock_price_change']}")
            print(f"  Profit or Loss for the Contract: ${result['profit_or_loss']}")
            total_return_percentage = (result['profit_or_loss'] / result['ask_price']) * 100
            print(f"  Total Return Percentage: {round(total_return_percentage, 2)}%\n")
