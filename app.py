import os
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from dotenv import load_dotenv

from finbert_model import FinBERT
from news_fetcher import fetch_latest_news
from llm_gemini import summarize_and_sentiment_gemini
from stock_list import stock_symbols

# Load API keys from .env
load_dotenv()

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Stock Sentiment Analyzer",
    page_icon="📈",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM DESIGN
# --------------------------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background: linear-gradient(135deg, #07111f, #101d35);
    color: #ffffff;
}

/* Main content width */
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Main heading */
.hero-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 5px;
}

.hero-title span {
    color: #38bdf8;
}

.hero-subtitle {
    text-align: center;
    color: #38bdf8;
    font-size: 23px;
    font-weight: 600;
    margin-bottom: 12px;
}

.hero-description {
    text-align: center;
    color: #aabbd2;
    font-size: 15px;
    margin-bottom: 35px;
}

/* Section headings */
h2, h3 {
    color: #ffffff !important;
}

/* Normal text */
p, label, .stMarkdown {
    color: #dce7f5;
}

/* Input field */
[data-testid="stTextInput"] input {
    background-color: #172840 !important;
    color: #ffffff !important;
    border: 1px solid #34516f !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #2563eb, #0891b2);
    color: white !important;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    padding: 10px 20px;
    transition: 0.3s;
}

.stButton button:hover {
    background: linear-gradient(90deg, #1d4ed8, #0e7490);
    border: none;
}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #14243a;
    border: 1px solid #263f5c;
    border-radius: 15px;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: #172b45;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #2d4968;
}

/* Progress bar */
.stProgress > div > div > div {
    background-color: #38bdf8;
}

/* Divider */
hr {
    border-color: #29415e;
}

/* Footer */
.footer {
    text-align: center;
    color: #8196b2;
    font-size: 13px;
    margin-top: 50px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# HERO SECTION
# --------------------------------------------------

st.markdown("""
<div class="hero-title">
    AI STOCK <span>MARKET</span>
</div>

<div class="hero-subtitle">
    SENTIMENT ANALYZER
</div>

<div class="hero-description">
    Intelligent Financial News Analysis Powered by Artificial Intelligence
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# STOCK SEARCH
# --------------------------------------------------

st.markdown("### 🔎 Explore Stock Market")

col1, col2 = st.columns([3, 1])

with col1:
    query = st.text_input(
        "Search by company name or ticker",
        placeholder="Example: AAPL, TSLA, MSFT, NVIDIA..."
    )

with col2:
    st.write("")
    st.write("")
    analyze_btn = st.button(
        "🚀 Analyze Stock",
        use_container_width=True
    )


# --------------------------------------------------
# STOCK SUGGESTIONS
# --------------------------------------------------

selected_ticker = None

if query:
    matches = []

    for symbol, company in stock_symbols.items():
        if (
            query.upper() in symbol.upper()
            or query.lower() in company.lower()
        ):
            matches.append((symbol, company))

    if matches:
        st.write("**Matching stocks:**")

        suggestion_cols = st.columns(min(len(matches), 4))

        for index, (symbol, company) in enumerate(matches[:4]):
            with suggestion_cols[index]:
                if st.button(
                    f"{symbol} | {company}",
                    key=f"suggestion_{symbol}"
                ):
                    st.session_state["selected_ticker"] = symbol

    elif query:
        st.info("No matching stock in the suggestion list. You can still try its ticker symbol.")


if "selected_ticker" in st.session_state:
    selected_ticker = st.session_state["selected_ticker"]
elif query:
    selected_ticker = query.strip().upper()


# --------------------------------------------------
# ANALYZE STOCK
# --------------------------------------------------

if analyze_btn:

    if not selected_ticker:
        st.error("Please enter a stock ticker.")
        st.stop()

    st.session_state["selected_ticker"] = selected_ticker

    st.markdown("---")
    st.markdown(f"## 📊 {selected_ticker} Analysis")

    # Fetch news
    try:
        with st.spinner("Fetching latest financial news..."):
            articles = fetch_latest_news(
                selected_ticker,
                max_articles=3
            )

    except Exception as e:
        st.error(f"Unable to fetch news: {e}")
        st.stop()

    if not articles:
        st.warning("No news articles found for this stock.")
        st.stop()

    # Load FinBERT
    try:
        with st.spinner("Loading FinBERT AI model..."):
            finbert = FinBERT()

    except Exception as e:
        st.error(f"Unable to load FinBERT: {e}")
        st.stop()

    # Analyze articles
    all_scores = []
    summaries = []

    with st.spinner("Analyzing financial news with AI..."):

        for article in articles:

            text = article.get("text") or article.get("title") or ""

            if not text.strip():
                continue

            # FinBERT analysis
            try:
                result = finbert.analyze_text(text)
                all_scores.append(result["scores"])

            except Exception as e:
                st.warning(f"FinBERT analysis failed: {e}")
                continue

            # Gemini summary
            try:
                summary = summarize_and_sentiment_gemini(text)

            except Exception as e:
                summary = f"Gemini summary unavailable: {e}"

            summaries.append({
                "title": article.get("title", "Financial News"),
                "summary": summary,
                "link": article.get("link")
            })

    if not all_scores:
        st.error("Could not analyze the available news articles.")
        st.stop()

    # Calculate average sentiment
    average_positive = sum(
        score["positive"] for score in all_scores
    ) / len(all_scores)

    average_negative = sum(
        score["negative"] for score in all_scores
    ) / len(all_scores)

    average_neutral = sum(
        score["neutral"] for score in all_scores
    ) / len(all_scores)

    sentiment_score = average_positive * 100

    if average_positive > average_negative and average_positive > average_neutral:
        sentiment_label = "Positive"
    elif average_negative > average_positive and average_negative > average_neutral:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"

    # --------------------------------------------------
    # SENTIMENT RESULTS
    # --------------------------------------------------

    st.markdown("### 🧠 AI Sentiment Results")

    metric1, metric2, metric3 = st.columns(3)

    with metric1:
        st.metric(
            "Overall Sentiment",
            sentiment_label
        )

    with metric2:
        st.metric(
            "Positive Probability",
            f"{average_positive * 100:.1f}%"
        )

    with metric3:
        st.metric(
            "Articles Analyzed",
            len(all_scores)
        )

    st.markdown("#### Sentiment Distribution")

    sentiment_df = pd.DataFrame({
        "Sentiment": ["Positive", "Neutral", "Negative"],
        "Probability": [
            average_positive,
            average_neutral,
            average_negative
        ]
    })

    st.bar_chart(
        sentiment_df.set_index("Sentiment"),
        color="#38bdf8"
    )

    # --------------------------------------------------
    # GEMINI NEWS SUMMARIES
    # --------------------------------------------------

    st.markdown("---")
    st.markdown("### 📰 AI Financial News Analysis")

    if summaries:

        for item in summaries:

            with st.container(border=True):

                st.markdown(f"#### {item['title']}")

                st.write(item["summary"])

                if item["link"]:
                    st.markdown(
                        f"[Read Original Article]({item['link']})"
                    )

    else:
        st.info("No news summaries available.")

    # --------------------------------------------------
    # STOCK PRICE CHART
    # --------------------------------------------------

    st.markdown("---")
    st.markdown("### 📈 Historical Stock Price")

    try:
        with st.spinner("Loading stock price history..."):

            stock_data = yf.Ticker(selected_ticker).history(
                period="3mo"
            )

        if stock_data.empty:
            st.warning("No historical price data available.")

        else:

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=stock_data.index,
                    y=stock_data["Close"],
                    mode="lines",
                    name="Closing Price",
                    line=dict(
                        color="#38bdf8",
                        width=3
                    ),
                    fill="tozeroy",
                    fillcolor="rgba(56,189,248,0.08)"
                )
            )

            fig.update_layout(
                height=420,
                template="plotly_dark",
                paper_bgcolor="#14243a",
                plot_bgcolor="#14243a",
                font=dict(color="#dce7f5"),
                xaxis_title="Date",
                yaxis_title="Stock Price",
                margin=dict(l=20, r=20, t=30, b=20),
                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

    except Exception as e:
        st.warning(f"Unable to load stock price data: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown("""
<div class="footer">
    <b>AI Stock Market Sentiment Analyzer</b>
    <br><br>
    Powered by FinBERT · Google Gemini · Python · Streamlit
    <br><br>
    Financial News Analysis and Stock Market Visualization
    <br><br>
    For educational and research purposes only.
    Not financial investment advice.
</div>
""", unsafe_allow_html=True)