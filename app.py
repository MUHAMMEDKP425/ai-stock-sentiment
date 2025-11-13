import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

from finbert_model import FinBERT
from news_fetcher import fetch_latest_news
from llm_gemini import summarize_and_sentiment_gemini
from stock_list import stock_symbols


# -----------------------------
# Page Settings
# -----------------------------
st.set_page_config(page_title="AI Stock Sentiment Analyzer", layout="wide")


# -----------------------------
# CSS for Clean White UI
# -----------------------------
st.markdown("""
<style>

body {
    background-color: #ffffff !important;
}

/* Title styling */
.main-title {
    font-size: 45px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 0px;
}

.sub-title {
    font-size: 20px;
    text-align: center;
    color: #777777;
    margin-top: -10px;
    margin-bottom: 30px;
}

/* Card container */
.card {
    background: #ffffff;
    padding: 25px;
    border-radius: 18px;
    border: 1px solid #dddddd;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 25px;
}

/* Search box */
input[type="text"] {
    border-radius: 10px !important;
    padding: 10px !important;
    border: 1.5px solid #cccccc !important;
    background-color: #f9f9f9 !important;
}

/* Progress bar */
.stProgress > div > div > div {
    background-color: #4b7bec !important;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------
# TITLES
# -----------------------------
st.markdown("<h1 class='main-title'>AI Stock Market</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='sub-title' style='color:#4b7bec;'>Sentiment Analyzer</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Powered by AI to analyze sentiment, news & trends for any stock.</p>", unsafe_allow_html=True)


# -----------------------------
# SEARCH BAR
# -----------------------------
col_search, col_btn = st.columns([3, 1])

with col_search:
    query = st.text_input("Search stock (AAPL, TSLA, TCS...)")

selected_ticker = None

# Suggestion dropdown
suggestions = []
if query:
    q = query.upper()
    for sym, name in stock_symbols.items():
        if q in sym or query.lower() in name.lower():
            suggestions.append(f"{sym} – {name}")

if suggestions:
    for s in suggestions:
        if st.button(s):
            selected_ticker = s.split(" – ")[0]

# If no suggestion selected, fallback:
if not selected_ticker:
    selected_ticker = query.upper() if query else "AAPL"

analyze = col_btn.button("Analyze", use_container_width=True)


# -----------------------------
# RUN ANALYSIS
# -----------------------------
if analyze:

    # Fetch news
    with st.spinner("Fetching latest news..."):
        articles = fetch_latest_news(selected_ticker, max_articles=3)

    st.markdown(f"<h2>{selected_ticker} – AI Sentiment Analysis</h2>", unsafe_allow_html=True)

    # Create card container
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    finbert = FinBERT()

    final_sentiment_score = 0
    final_sentiment_label = "Neutral"

    summaries = []

    for article in articles:
        text = article["text"] or article["title"]
        
        # FinBERT score
        result = finbert.analyze_text(text)
        score = result["scores"]["positive"]
        final_sentiment_score = score * 100

        if score > 0.55:
            final_sentiment_label = "Positive"
        elif score < 0.45:
            final_sentiment_label = "Negative"
        else:
            final_sentiment_label = "Neutral"

        # Gemini Summary
        try:
            ai_summary = summarize_and_sentiment_gemini(text)
        except:
            ai_summary = "Gemini API key missing."

        summaries.append(ai_summary)

    # -----------------------------
    # SENTIMENT BAR
    # -----------------------------
    st.write("### Sentiment Score")
    st.progress(final_sentiment_score / 100)
    st.write(f"**{final_sentiment_label} ({final_sentiment_score:.0f}%)**")

    # -----------------------------
    # SUMMARY SECTION
    # -----------------------------
    st.write("### Analysis Summary")
    for s in summaries:
        st.write(s)
        st.write("---")

    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------
    # PRICE CHART
    # -----------------------------
    try:
        st.write("### Price Chart")
        data = yf.Ticker(selected_ticker).history(period="3mo")

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines"))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    except:
        st.warning("⚠ Unable to load price data.")

