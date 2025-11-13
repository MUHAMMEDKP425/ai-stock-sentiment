import requests
from bs4 import BeautifulSoup
import time

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_latest_news(ticker, max_articles=5):
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    articles = []

    for a in soup.select("a.js-content-viewer")[:max_articles]:
        title = a.get_text(strip=True)
        link = a.get("href")
        if link.startswith("/"):
            link = "https://finance.yahoo.com" + link

        text = extract_text(link)
        articles.append({"title": title, "link": link, "text": text})
        time.sleep(0.2)

    return articles


def extract_text(url):
    try:
        r = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        text = "\n".join([p.get_text().strip() for p in soup.find_all("p")])
        return text[:3000]
    except:
        return ""
