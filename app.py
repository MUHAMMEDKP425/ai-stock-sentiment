import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

from finbert_model import FinBERT
from news_fetcher import fetch_latest_news
from llm_gemini import summarize_and_sentiment_gemini
from stock_list import stock_symbols


# ------------------------------------------------
# FORCE LIGHT MODE FOR ALL USERS
# ------------------------------------------------
st.markdown("""
<style>
:root, html, body, [data-testid="stAppViewContainer"] {
    color-scheme: light !important;
    background-color: #ffffff !important;
}
[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important;
}
[data-testid="stHeader"] {
    background-color: #ffffff !important;
}
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------
# PAGE SETTINGS
# ------------------------------------------------
st.set_page_config(page_title="AI Stock Sentiment Analyzer", layout="wide")


# ------------------------------------------------
# MAIN TITLE UI
# ------------------------------------------------
st.markdown("""
    <style>
        .main-title {
            font-size: 45px;
            font-weight: 800;
            text-align: center;
            margin-bottom: -10px;
        }
        .sub-title {
            font-size: 22px;
            text-align: center;
            color: #4b7bec;
            margin-bottom: 10px;
        }
        .desc-text {
            font-size: 17px;
            text-align: center;
            color: #777777;
            margin-bottom: 35px;
        }
        .card {
            background: #ffffff;
            padding: 25px;
            border-radius: 15px;
            border: 1px solid #dddddd;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 25px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>AI Stock Market</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='sub-title'>Sentiment Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='desc-text'>Powered by AI to analyze sentiment, news & trends for any stock.</p>", unsafe_allow_html=True)


# ------------------------------------------------
# 🔥 TRENDING STOCKS
# ------------------------------------------------
st.markdown("### 🔥 Trending Stocks Today")

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
selected_ticker = None

for idx, (symbol, name) in enumerate(trending_stocks):
    with cols[idx % 4]:
        if st.button(f"{symbol} – {name}", use_container_width=True):
            selected_ticker = symbol
            st.success(f"Selected: {symbol}")


# ------------------------------------------------
# SEARCH BAR
# ------------------------------------------------
st.markdown("### 🔎 Search Stock")

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input("Search stock (AAPL, TSLA, TCS...)")

with col2:
    analyze_btn = st.button("Analyze", use_container_width=True)

# Autocomplete suggestions
if not selected_ticker:
    suggestions = []
    if query:
        for sym, name in stock_symbols.items():
            if query.upper() in sym or query.lower() in name.lower():
                suggestions.append(f"{sym} – {name}")

    for s in suggestions:
        if st.button(s):
            selected_ticker = s.split(" – ")[0]


if not selected_ticker:
    selected_ticker = query.upper() if query else None


# ------------------------------------------------
# ANALYZE CLICKED
# ------------------------------------------------
if analyze_btn:

    if not selected_ticker:
        st.error("Please enter or select a stock.")
        st.stop()

    # Fetch news
    with st.spinner("Fetching latest news..."):
        articles = fetch_latest_news(selected_ticker, max_articles=3)

    if not articles:
        st.error("No news found for this stock.")
        st.stop()

    st.markdown(f"## {selected_ticker} – AI Sentiment Analysis")

    # Start Card
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    finbert = FinBERT()
    summaries = []

    # Process articles
    final_score = 0
    final_label = "Neutral"

    for article in articles:
        text = article["text"] or article["title"]

        # FinBERT result
        result = finbert.analyze_text(text)
        pos_score = result["scores"]["positive"]
        final_score = pos_score * 100

        if pos_score > 0.55:
            final_label = "Positive"
        elif pos_score < 0.45:
            final_label = "Negative"
        else:
            final_label = "Neutral"

        # Gemini summary
        try:
            summary = summarize_and_sentiment_gemini(text)
        except:
            summary = "Gemini API key missing."

        summaries.append(summary)

    # Sentiment Score
    st.write("### Sentiment Score")
    st.progress(final_score / 100)
    st.write(f"**{final_label} ({final_score:.0f}%)**")

    # Summary
    st.write("### Analysis Summary")
    for s in summaries:
        st.write(s)
        st.write("---")

    st.markdown("</div>", unsafe_allow_html=True)


    # ------------------------------------------------
    # PRICE CHART
    # ------------------------------------------------
    st.write("### 📈 Price Chart")

    try:
        data = yf.Ticker(selected_ticker).history(period="3mo")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close"))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Unable to load price data.")
