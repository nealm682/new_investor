import streamlit as st

def sentiment_analysis(put_call_ratio, vix_value):
    """
    Analyzes sentiment indicators to provide trading insights.

    Parameters:
        put_call_ratio (float): The put/call ratio for the ticker.
        vix_value (float): The current VIX index value.

    Returns:
        None
    """
    insights = []

    # Analyze put/call ratio
    if put_call_ratio is not None:
        if put_call_ratio < 0.7:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates bullish sentiment, "
                f"suggesting optimism as more call options are traded compared to puts."
            )
        elif put_call_ratio == 0.7:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests neutral sentiment, "
                f"indicating more puts are being traded compared to calls."
            )
        else:  # Above 2.0 or any other value >= 0.7 (depending on your logic)
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates strong bearish sentiment, "
                f"suggesting heightened fear or significant hedging activity."
            )

    # Analyze VIX value
    if vix_value is not None:
        if vix_value < 12:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates low market volatility, "
                f"reflecting complacency or confidence among market participants."
            )
        elif 12 <= vix_value <= 20:
            insights.append(
                f"The VIX value of {vix_value:.2f} is within the normal range, "
                f"suggesting moderate volatility and typical market conditions."
            )
        elif 20 < vix_value <= 30:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates elevated market volatility, "
                f"reflecting uncertainty or potential market stress."
            )
        else:  # Above 30
            insights.append(
                f"The VIX value of {vix_value:.2f} signals extreme market volatility, "
                f"indicating significant fear and potential market turmoil."
            )

    # Display the analysis in the Streamlit UI
    if insights:
        st.write("**Sentiment Analysis:**")
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.write("No sentiment indicators available.")


'''
def sentiment_analysis(put_call_ratio, vix_value):
    """
    Analyzes sentiment indicators to provide trading insights.

    Parameters:
        put_call_ratio (float): The put/call ratio for the ticker.
        vix_value (float): The current VIX index value.

    Returns:
        None
    """
    insights = []

    # Analyze put/call ratio
    # Analyze put/call ratio
    if put_call_ratio is not None:
        if put_call_ratio < 0.7:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates bullish sentiment, suggesting optimism as more call options are traded compared to puts."
            )
        elif put_call_ratio == .07:
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} suggests neutral sentiment, indicating more puts are being traded compared to calls."
            )
        else:  # Above 2.0
            insights.append(
                f"The put/call ratio of {put_call_ratio:.2f} indicates strong bearish sentiment, suggesting heightened fear or significant hedging activity."
            )

    # Analyze VIX value
    if vix_value is not None:
        if vix_value < 12:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates low market volatility, reflecting complacency or confidence among market participants."
            )
        elif 12 <= vix_value <= 20:
            insights.append(
                f"The VIX value of {vix_value:.2f} is within the normal range, suggesting moderate volatility and typical market conditions."
            )
        elif 20 < vix_value <= 30:
            insights.append(
                f"The VIX value of {vix_value:.2f} indicates elevated market volatility, reflecting uncertainty or potential market stress."
            )
        else:  # Above 30
            insights.append(
                f"The VIX value of {vix_value:.2f} signals extreme market volatility, indicating significant fear and potential market turmoil."
            )


    # Combine insights
    print("\nSentiment Analysis:")
    for insight in insights:
        print(f"  - {insight}")
'''