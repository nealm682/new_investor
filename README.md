# Options Assessment - Advanced Stock Options Analysis

Options Assessment is a Python-based project designed to help users analyze stock options, evaluate their Greeks, and assess key market metrics such as the Put/Call Ratio and VIX. The tool integrates multiple APIs, including Robinhood, Yahoo Finance, and OpenAI, to provide comprehensive insights for informed decision-making.

## SPECIAL NOTE: Your credentials are not saved. 

## Note from the developer of `robin-stocks`
These functions make real-time calls to your Robinhood account. Unlike the app, there are no warnings when you are about to buy, sell, or cancel an order. It is up to **YOU** to use these commands responsibly.

## Framework

The project utilizes the following technologies and APIs:
- **Robinhood API via `robin-stocks`**: For fetching stock and options data.
- **Yahoo Finance (`yfinance`)**: For additional market metrics such as the VIX and Put/Call Ratio.
- **OpenAI API**: For providing advanced financial analysis and sentiment insights.
  
You can reference the `robin-stocks` package at: [robin-stocks GitHub](https://github.com/jmfernandes/robin_stocks).

## Features

- **Login and Authentication**:
  - Secure login to Robinhood using environment variables.
  - Credentials are not stored locally.
- **Fetch Options Data**:
  - Analyze options data filtered by expiration dates and strike prices.
- **Calculate Greeks**:
  - Retrieve and interpret Delta, Gamma, Theta, Vega, and other relevant metrics.
  - Assess the impact of Greeks on potential profits or risks.
- **Historical Data Analysis**:
  - Analyze daily percentage changes in stock prices over the last 90 days.
  - Evaluate trends, consistency, and volatility.
- **Profit/Loss Simulation**:
  - Simulate potential profit or loss for an options contract based on percentage changes in the stock price.
- **Market Sentiment Metrics**:
  - Calculate the Put/Call Ratio to gauge market sentiment.
  - Fetch and interpret the VIX (Volatility Index) to assess market conditions.
- **AI-Powered Insights**:
  - Utilize OpenAI for advanced financial analysis and sentiment evaluation.
  - Generate actionable insights and expert opinions on options contracts.

## Setup Instructions

### Prerequisites

1. Python 3.9+ installed on your system.
2. A Robinhood account for accessing stock and options data.
3. API access to OpenAI and an internet connection for using Yahoo Finance.
4. `pip` installed for package management.

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

4. Create a `.env` file in the root directory and add your credentials and API keys:
    ```plaintext
    ROBINHOOD_USERNAME=your_username
    ROBINHOOD_PASSWORD=your_password
    OPENAI_API_KEY=your_openai_api_key
    ```

### Run the Program

To start the application, execute the following command:
```bash
python options.py
