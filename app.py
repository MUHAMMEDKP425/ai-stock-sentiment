import streamlit as st
from finbert_model import FinBERT
from news_scraper import fetch_text_from_url
from llm_gemini import summarize_and_sentiment

st.title("📈 AI Stock Market Sentiment Analyzer")

text = st.text_area("Paste Stock News or Headline:")

if st.button("Analyze"):
    if text.strip() == "":
        st.warning("Please enter some text")
    else:
        # FinBERT analysis
        finbert = FinBERT()
        result = finbert.analyze(text)

        st.subheader("FinBERT Sentiment")
        st.write(result)

        # Gemini analysis
        try:
            llm = summarize_and_sentiment(text)
            st.subheader("Gemini Summary + Sentiment")
            st.write(llm["raw"])
        except Exception as e:
            st.error
