import streamlit as st
from src.finbert_model import FinBERT
from src.news_fetcher import fetch_latest_news
from src.llm_gemini import summarize_and_sentiment_gemini
import os

st.set_page_config(page_title="AI Stock Market Analyzer", layout="wide")

st.title("📊 AI Stock Market Sentiment Analyzer")

# Input for stock ticker
ticker = st.text_input("Enter Stock Name or Ticker (Example: TSLA, AAPL, MSFT):", value="TSLA")

if st.button("Analyze Sentiment"):
    
    # Fetch news
    with st.spinner("Fetching latest news..."):
        articles = fetch_latest_news(ticker.upper(), max_articles=5)

    if not articles:
        st.error("No news found for this ticker. Try another one.")
    else:
        st.success(f"Fetched {len(articles)} articles successfully!")

        finbert = FinBERT()

        # Loop through each article
        for article in articles:

            st.markdown("### 📰 " + article['title'])
            st.markdown(f"[Read full article]({article['link']})")

            text = article['text'] or article['title']

            # FinBERT Sentiment
            st.markdown("### 🔍 FinBERT Sentiment Analysis")
            finbert_result = finbert.analyze_text(text)
            st.json(finbert_result)

            # Gemini Summary + Sentiment
            st.markdown("### 🤖 Gemini AI Summary & Sentiment")

            try:
                summary = summarize_and_sentiment_gemini(text)
                st.write(summary)
            except Exception as e:
                st.warning("⚠ Gemini API key missing or invalid.")
                st.write(e)
