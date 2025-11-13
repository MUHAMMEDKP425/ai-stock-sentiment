import streamlit as st
from src.finbert_model import FinBERT
from src.news_fetcher import fetch_latest_news
from src.llm_gemini import summarize_and_sentiment_gemini
import os

st.set_page_config(page_title="AI Stock Market Analyzer", layout="wide")
st.title("📊 AI Stock Market Sentiment Analyzer")

# Input
ticker = st.text_input("Enter Stock Name or Ticker:", value="TSLA")

# Button
if st.button("Analyze"):
    with st.spinner("Fetching latest news..."):
        articles = fetch_latest_news(ticker.upper(), max_articles=5)

    if not articles:
        st.error("No news found. Try another ticker.")
    else:
        st.success(f"Fetched {len(articles)} news articles!")

        finbert = FinBERT()

        for article in articles:
            st.subheader("📰 " + article['title'])
            st.markdown(f"[Read full article]({article['link']})")

            text = article['text'] or article['title']

            # FinBERT Sentiment
            st.markdown("### 🔍 FinBERT Sentiment")
            finbert_result = finbert.analyze_text(text)
            st.json(finbert_result)

            # Gemini Summary
            st.markdown("### 🤖 Gemini Summary")
            try:
                summary = summarize_and_sentiment_gemini(text)
