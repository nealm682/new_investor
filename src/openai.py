from dotenv import load_dotenv
import os
import openai


load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment_google_results(articles):
    """
    Performs sentiment analysis on Google Search results using OpenAI.

    Parameters:
        articles (list): A list of dictionaries containing article metadata.

    Returns:
        list: A list of articles with sentiment scores appended.
    """
    results = []

    for article in articles:
        try:
            content = article["title"] + ". " + article["snippet"]
                    # Create the chat completion using the client

            response = openai.chat.completions.create(
                model="gpt-4",  # Use "gpt-3.5-turbo" if "gpt-4" is unavailable
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI tasked with performing sentiment analysis. "
                                   "Classify the sentiment of the provided text as positive, neutral, or negative."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze the sentiment of this text: {content}"
                    }
                ],
                max_tokens=150,
                temperature=0.5
            )


            sentiment = response.choices[0].message.content
            article["sentiment"] = sentiment
            results.append(article)
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            continue

    return results



# Example function to call OpenAI API
def get_ai_analysis(summary_data):
    try:
        # Construct the prompt
        messages = [
            {
                "role": "system",
                "content": """You are a financial analyst specializing in options and market sentiment analysis. 
                Interpret the data provided using the following context and guidelines:

                - **Put/Call Ratio**:
                - The put-call ratio measures market sentiment by dividing the number of traded put options by the number of traded call options. A put-call ratio of 1 indicates that the number of buyers of calls is the same as the number of buyers for puts. However, a ratio of 1 is not an accurate starting point to measure sentiment in the market because there are normally more investors buying calls than buying puts. So, an average put-call ratio of 0.7 for equities is considered a good basis for evaluating sentiment. Low ratio numbers, like 0.2-0.3, suggest market sentiment is extremely bullish, while a reading over 1.2 suggests the market is becoming too bearish and may be due for a bounce. The put/call ratio is a very helpful tool in gauging whether the market outlook is bullish or bearish for a particular security or an index itself. 
                - 
                - **Equal to .07**: Nuetral sentiment; investors are balanced between put and call options.
                - **Greater than 0.7, or exceeding 1**: means that equity traders are buying more puts than calls. It suggests that bearish sentiment is building in the market. Investors are either speculating that the market will move lower or are hedging their portfolios in case there is a sell-off.
                - **Below .07**: A falling put-call ratio, or below 0.7 and approaching 0.5, is considered a bullish indicator. It means more calls are being bought versus puts.

                - **VIX Value**:
                - **Below 12**: Low market volatility, complacency.
                - **12 to 20**: Normal market conditions, moderate volatility.
                - **Above 20**: Elevated volatility, uncertainty.
                - **Above 30**: Extreme fear and market stress.

                - **Options Greeks**:
                - **Delta**: Indicates sensitivity to price changes; close to 1.0 suggests high correlation with stock movements, while near 0.5 represents at-the-money options. Highlight significant deviations.
                - **Gamma**: Measures Delta sensitivity; high Gamma signals sharp changes in Delta with stock movement. Mention if unusually high.
                - **Theta**: Reflects time decay; negative Theta is standard but significant rates can imply steep value loss over time. Highlight unusual cases.
                - **Vega**: Reflects sensitivity to volatility changes; high Vega can signal volatility-driven value shifts. Mention only if it significantly impacts decision-making.

                - **Historical Stock Performance**:
                - Assess the consistency and volatility of stock returns over the observed period.
                - Highlight stocks with more positive trading days and stable gains as stronger candidates, and flag high-volatility stocks for caution.

                Use these ranges and guidelines to ground your interpretation and provide a well-reasoned summary. 
                Highlight potential insights or risks based on the data trends and explain how the numbers align with broader market conditions or stock-specific sentiment.

                Your task is to assess whether the presented options contract represents a favorable investment opportunity. 
                Provide an expert opinion with actionable insights to guide decision-making. Focus on whether the data supports a favorable risk/reward profile."""
            },
            {
                "role": "user",
                "content": f"Based on the following data, evaluate the option and provide your expert opinion:\n\n{summary_data}\n\n"
                        "Interpret the Greeks only if they stand out or are unusual. For example:\n"
                        "- Delta: Highlight only if it significantly affects price sensitivity or risk.\n"
                        "- Gamma: Mention if it indicates sharp changes in Delta.\n"
                        "- Theta: Discuss only if the rate of time decay is extreme or negligible.\n"
                        "- Vega: Address only if the option's value is highly sensitive to volatility changes.\n\n"
                        "For Put/Call ratio and VIX, provide market sentiment insights. For historical price performance, "
                        "comment on consistency and volatility of returns. Finally, make a recommendation on whether this option seems "
                        "like a good investment based on the overall data."
            }
        ]



        # Create the chat completion using the client
        response = client.chat.completions.create(
            model="gpt-4",  # Use "gpt-3.5-turbo" or other supported models if "gpt-4" is unavailable
            messages=messages,
            max_tokens=600,
            temperature=0.7
        )
        #print(response)
        # Extract and return the assistant's reply
        ai_response = response.choices[0].message.content


        print("\nAI Analysis:")
        print(ai_response)
        return ai_response

    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return None