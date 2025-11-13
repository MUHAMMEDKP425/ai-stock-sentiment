import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import os

from finbert_model import FinBERT
from news_fetcher import fetch_latest_news
from llm_gemini import summarize_and_sentiment_gemini
from stock_list import stock_symbols


# -------------------------------
# Simple CSS for search bar
# -------------------------------
st.markdown("""
<style>
input[type="text"] {
    border: 2px solid #4b7bec !important;
    border-radius: 10px !important;
    padding: 10px !important;
    font-size: 16px !important;
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="AI Stock Market Analyzer", layout="wide")

# -------------------------------
# Title
# -------------------------------
st.title("📊 AI Stock Market Sentiment Analyzer")


# -------------------------------
# 🔥 TRENDING STOCKS SECTION
# -------------------------------
st.markdown("## 🔥 Trending Stocks Today")

trending_stocks = [
    ("TSLA", "Tesla"),
    ("AAPL", "Apple"),
    ("NVDA", "NVIDIA"),
    ("META", "Meta"),
    ("AMZN", "Amazon"),
    ("GOOG", "Alphabet"),
    ("TCS", "Tata Consultancy Services"),
    ("RELIANCE", "Reliance Industries"),
]

cols = st.columns(4)

ticker = None  # will be set when user clicks

for i, (symbol, name) in enumerate(trending_stocks):
    with cols[i % 4]:
        if st.button(f"{symbol} – {name}"):
            ticker = symbol
            st.success(f"Selected Trending Stock: {symbol}")


# -------------------------------
# SEARCH BAR WITH SUGGESTIONS
# -------------------------------
st.subheader("🔎 Search Stock")

query = st.text_input("Type ticker or company name...")

if not ticker:   # only use search bar if user didn't click trending
    suggestions = []
    selected = None

    if query:
        q_upper = query.upper()
        for symbol, name in stock_symbols.items():
            if q_upper in symbol or query.lower() in name.lower():
                suggestions.append(f"{symbol} – {name}")

    if suggestions:
        st.write("### Suggestions:")
        for s in suggestions:
            if st.button(s):
                ticker = s.split(" – ")[0]
                st.success(f"Selected: {ticker}")
                selected = True

    if not ticker:
        ticker = st.text_input("Or enter ticker manually:", value="TSLA")


# -------------------------------
# Analyze Button
# -------------------------------
if st.button("Analyze Sentiment"):

    # Fetch News
    with st.spinner("Fetching latest news..."):
        articles = fetch_latest_news(ticker.upper(), max_articles=5)

    if not articles:
        st.error("No news found for this ticker. Try another one.")
        st.stop()

    st.success(f"Fetched {len(articles)} articles successfully!")

    finbert = FinBERT()
    results = []

    # Process each article
    for article in articles:

        st.markdown("### 📰 " + article['title'])
        st.markdown(f"[Read full article]({article['link']})")

        text = article['text'] or article['title']

        # -------------------------------
        # FinBERT Sentiment
        # -------------------------------
        st.markdown("### 🔍 FinBERT Sentiment Analysis")
        finbert_result = finbert.analyze_text(text)
        st.json(finbert_result)

        # -------------------------------
        # Gemini Summary
        # -------------------------------
        st.markdown("### 🤖 Gemini AI Summary & Sentiment")

        try:
            summary = summarize_and_sentiment_gemini(text)
            st.write(summary)
        except Exception as e:
            st.warning("⚠ Gemini API key missing or invalid.")
            st.write(e)

        results.append({
            "title": article['title'],
            "link": article['link'],
            "finbert": finbert_result
        })

    # -------------------------------
    # PRICE CHART
    # -------------------------------
    st.markdown("## 📈 Stock Price History")

    try:
        data = yf.Ticker(ticker).history(period="3mo")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price"))
        fig.update_layout(title=f"{ticker} Price (Last 3 Months)", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Unable to fetch price data.")

    st.success("Analysis Completed!")
