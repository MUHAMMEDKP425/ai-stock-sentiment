import requests
import os

def fetch_latest_news(ticker, max_articles=5):
    api_key = os.getenv("MARKETAUX_API_KEY")
    
    if not api_key:
        raise Exception("MARKETAUX_API_KEY missing in Streamlit Secrets")

    url = "https://api.marketaux.com/v1/news/all"

    params = {
        "api_token": api_key,
        "symbols": ticker,
        "filter_entities": True,
        "limit": max_articles,
        "language": "en"
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    for item in data.get("data", []):
        articles.append({
            "title": item.get("title"),
            "text": item.get("snippet"),
            "link": item.get("url")
        })

    return articles
