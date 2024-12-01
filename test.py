import yfinance as yf

symbol = "EME"
expiration_date = "2025-01-17"

# Get options chain
ticker = yf.Ticker(symbol)
options_chain = ticker.option_chain(expiration_date)

# Check puts and calls
puts = options_chain.puts
calls = options_chain.calls

print("Calls Data:")
print(calls)
print("Puts Data:")
print(puts)