# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import json
import io
import os
from datetime import datetime
from stock_list import stock_symbols


# Local modules (files in repo root)
from finbert_model import FinBERT
from news_fetcher import fetch_latest_news
from llm_gemini import summarize_and_sentiment_gemini

st.set_page_config(page_title="AI Stock Sentiment Dashboard", layout="wide", initial_sidebar_state="expanded")

# -------------------------
# Sidebar - Controls
# -------------------------
st.sidebar.header("Dashboard Controls")
ticker = st.sidebar.text_input("Ticker (e.g. TSLA, AAPL)", value="TSLA")
max_articles = st.sidebar.slider("Max articles to fetch", 1, 8, 5)
price_period = st.sidebar.selectbox("Price period", ["1mo", "3mo", "6mo", "1y"], index=1)
use_gemini = st.sidebar.checkbox("Use Gemini for summaries (optional)", value=False)
analyze_btn = st.sidebar.button("Run Analysis")

st.title("📊 AI Stock Market Sentiment Dashboard")

# Helpful info / last run
if "last_run" not in st.session_state:
    st.session_state.last_run = None

# -------------------------
# Helper functions
# -------------------------
@st.cache_data(ttl=3600)
def get_price_history(sym, period="3mo"):
    try:
        tk = yf.Ticker(sym)
        hist = tk.history(period=period, interval="1d")
        hist = hist.reset_index()
        return hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    except Exception:
        return pd.DataFrame()

def aggregate_sentiments(results):
    rows = []
    for r in results:
        f = r.get("finbert", {})
        rows.append({
            "title": r.get("title"),
            "link": r.get("link"),
            "finbert_label": f.get("sentiment") or f.get("label"),
            "finbert_neg": f.get("scores", {}).get("negative"),
            "finbert_neu": f.get("scores", {}).get("neutral"),
            "finbert_pos": f.get("scores", {}).get("positive"),
            "llm_raw": r.get("llm_raw", "")
        })
    df = pd.DataFrame(rows)
    agg = {}
    if not df.empty:
        agg['avg_pos'] = df['finbert_pos'].mean()
        agg['avg_neu'] = df['finbert_neu'].mean()
        agg['avg_neg'] = df['finbert_neg'].mean()
        label_scores = {'positive': agg['avg_pos'], 'neutral': agg['avg_neu'], 'negative': agg['avg_neg']}
        agg['overall_label'] = max(label_scores, key=label_scores.get)
    else:
        agg = {'avg_pos': None, 'avg_neu': None, 'avg_neg': None, 'overall_label': None}
    agg['generated_at'] = datetime.utcnow()
    return agg, df

def to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

def to_json_bytes(data):
    return json.dumps(data, indent=2).encode('utf-8')

# -------------------------
# Run analysis
# -------------------------
if analyze_btn:
    st.session_state.last_run = datetime.utcnow().isoformat()
    with st.spinner("Fetching news..."):
        articles = fetch_latest_news(ticker.upper(), max_articles=max_articles)

    if not articles:
        st.error("No articles found for this ticker. Try another ticker or increase max articles.")
    else:
        st.success(f"Fetched {len(articles)} articles successfully!")
        finbert = FinBERT()
        results = []

        # Process articles
        progress = st.progress(0)
        for i, a in enumerate(articles):
            text = a.get("text") or a.get("title") or ""
            fin_res = finbert.analyze_text(text)
            item = {"title": a.get("title"), "link": a.get("link"), "text": text, "finbert": fin_res}

            # Optional LLM summary
            if use_gemini:
                try:
                    item['llm_raw'] = summarize_and_sentiment_gemini(text)
                except Exception as e:
                    item['llm_raw'] = f"LLM error: {e}"
            else:
                item['llm_raw'] = ""

            results.append(item)
            progress.progress(int((i+1)/len(articles)*100))
        progress.empty()

        # Aggregate
        agg, df = aggregate_sentiments(results)

        # -------------------------
        # Top summary cards
        # -------------------------
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Sentiment", str(agg['overall_label']).capitalize() if agg['overall_label'] else "N/A",
                    delta=f"Pos:{None if agg['avg_pos'] is None else round(agg['avg_pos']*100,1)}%")
        col2.metric("Positive (avg)", f"{None if agg['avg_pos'] is None else round(agg['avg_pos']*100,1)}%")
        col3.metric("Neutral (avg)", f"{None if agg['avg_neu'] is None else round(agg['avg_neu']*100,1)}%")
        col4.metric("Negative (avg)", f"{None if agg['avg_neg'] is None else round(agg['avg_neg']*100,1)}%")

        # -------------------------
        # Price chart
        # -------------------------
        st.markdown("### 📈 Price History")
        hist = get_price_history(ticker.upper(), period=price_period)
        if hist.empty:
            st.info("Price data not found.")
        else:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist['Date'], y=hist['Close'], mode='lines', name='Close'))
            fig.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=350)
            st.plotly_chart(fig, use_container_width=True)

        # -------------------------
        # Sentiment distribution chart
        # -------------------------
        st.markdown("### 📊 Sentiment Distribution (per article)")
        if not df.empty:
            df_plot = df.reset_index().melt(id_vars=['index','title','link','llm_raw','finbert_label'],
                                            value_vars=['finbert_neg','finbert_neu','finbert_pos'],
                                            var_name='score_type', value_name='score')
            # map names
            df_plot['score_type'] = df_plot['score_type'].map({
                'finbert_neg':'Negative',
                'finbert_neu':'Neutral',
                'finbert_pos':'Positive'
            })
            fig2 = px.bar(df_plot, x='title', y='score', color='score_type', barmode='group',
                          labels={'title':'Article','score':'Score','score_type':'Sentiment'})
            fig2.update_layout(xaxis={'categoryorder':'total descending'}, height=380)
            st.plotly_chart(fig2, use_container_width=True)

            # Articles table with expanders
            st.markdown("### 📰 Articles & Details")
            for idx, row in df.iterrows():
                st.subheader(f"{idx+1}. {row['title']}" if row['title'] else f"{idx+1}. Untitled")
                if row.get('link'):
                    st.markdown(f"[Read full article]({row['link']})")
                st.write(f"**FinBERT:** {row['finbert_label']}  —  pos:{round(row['finbert_pos'],3)} | neu:{round(row['finbert_neu'],3)} | neg:{round(row['finbert_neg'],3)}")
                if row.get('llm_raw'):
                    with st.expander("LLM Summary / Rationale"):
                        st.write(row['llm_raw'])
                # show small snippet
                orig_text = next((r['text'] for r in results if r['title']==row['title']), "")
                snippet = (orig_text[:600] + '...') if orig_text and len(orig_text) > 600 else orig_text
                st.write(snippet)

            # Download buttons
            csv_bytes = to_csv_bytes(df)
            json_bytes = to_json_bytes(results)
            st.download_button("Download CSV", data=csv_bytes, file_name=f"{ticker}_sentiment.csv", mime="text/csv")
            st.download_button("Download JSON", data=json_bytes, file_name=f"{ticker}_sentiment.json", mime="application/json")
        else:
            st.info("No article data to display.")

        # Show raw aggregated metadata
        st.markdown("### ℹ️ Analysis metadata")
        st.json(agg)

else:
    st.info("Enter a ticker and click 'Run Analysis' in the sidebar to begin.")
