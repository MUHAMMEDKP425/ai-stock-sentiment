
import requests
from bs4 import BeautifulSoup

def fetch_text_from_url(url):
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    paragraphs = soup.find_all("p")
    return "\n".join([p.get_text().strip() for p in paragraphs])
