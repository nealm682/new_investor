# Options Assessment - Robinhood

Options Assessment is a Python-based project that allows users to analyze stock options, including evaluating their Greeks, analyzing historical price changes, and calculating potential profits or losses based on percentage changes in stock price. It uses the Robinhood API for fetching stock and options data.

## Features

- **Login to Robinhood**: Authenticate securely using environment variables.
- **Fetch Options Data**: Analyze options data filtered by expiration dates and strike prices.
- **Calculate Greeks**: Retrieve Delta, Gamma, Theta, Vega, and other metrics for options.
- **Historical Data Analysis**: Analyze daily percentage changes in stock prices over the last 90 days.
- **Profit/Loss Simulation**: Simulate profit or loss for an options contract based on percentage changes in the stock price.

## Setup Instructions

### Prerequisites

1. Python 3.9+ installed on your system.
2. A Robinhood account to fetch stock and options data.
3. `pip` installed for package management.

### Installation

1. Clone this repository:
    ```bash
    git clone <repository-url>
    cd options-assessment
    ```

2. Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate   # On macOS/Linux
    venv\Scripts\activate      # On Windows
    ```

3. Install dependencies from the `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your Robinhood credentials:
    ```
    ROBINHOOD_USERNAME=your_username
    ROBINHOOD_PASSWORD=your_password
    ```

### Run the Program

Execute the following command to start the application:
```bash
python <your_script_name>.py
