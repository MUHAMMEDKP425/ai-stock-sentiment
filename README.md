# 📈 AI Stock Market Sentiment Analyzer

An AI-powered stock market sentiment analysis dashboard built using **Python, FinBERT, NLP, and Generative AI**. The application analyzes financial news, classifies market sentiment, and visualizes historical stock price trends through an interactive Streamlit dashboard.

## 🚀 Project Overview

The AI Stock Market Sentiment Analyzer aims to help users understand the sentiment surrounding publicly traded companies by analyzing financial news articles.

It combines a pretrained financial NLP model with external financial data APIs to provide sentiment insights and historical stock price visualizations.

## ✨ Key Features

- **Financial News Retrieval:** Fetch stock-related financial news using the Marketaux API.
- **AI Sentiment Analysis:** Use FinBERT to classify financial news into Positive, Negative, and Neutral categories.
- **Sentiment Probability Scores:** Display sentiment probabilities for analyzed news.
- **Generative AI Integration:** Includes Google Gemini integration for financial news summarization and sentiment explanations.
- **Historical Stock Data:** Retrieve historical stock price information using Yahoo Finance.
- **Interactive Visualizations:** Display sentiment distribution and historical stock price charts using Plotly.
- **Interactive Dashboard:** Explore stock analysis through a Streamlit web application.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web dashboard |
| FinBERT | Financial sentiment analysis |
| PyTorch | Deep learning framework |
| Hugging Face Transformers | Pretrained NLP model |
| Google Gemini API | AI-powered news summarization |
| Marketaux API | Financial news retrieval |
| Yahoo Finance (yfinance) | Historical stock price data |
| Plotly | Interactive data visualization |
| SciPy | Sentiment score processing |
| Pandas & NumPy | Data processing |

## 🧠 How It Works

The application follows this workflow:

1. The user enters a stock ticker symbol, such as TSLA, AAPL, or MSFT.
2. The application retrieves related financial news using the Marketaux API.
3. The retrieved news text is analyzed using the pretrained FinBERT model.
4. FinBERT classifies the news sentiment as Positive, Negative, or Neutral.
5. The application calculates and displays sentiment scores.
6. The Gemini integration is designed to summarize financial news and provide explanations.
7. Historical stock price data is retrieved using yfinance.
8. Plotly visualizes sentiment distribution and historical stock price trends.
9. Streamlit displays the results in an interactive dashboard.

## 🏗️ Project Architecture

```text
AI Stock Market Sentiment Analyzer
│
├── app.py
│   └── Main Streamlit dashboard
│
├── finbert_model.py
│   └── FinBERT sentiment analysis
│
├── llm_gemini.py
│   └── Gemini news summarization
│
├── news_fetcher.py
│   └── Marketaux API integration
│
├── news_scraper.py
│   └── Webpage text extraction utility
│
├── stock_list.py
│   └── Stock ticker suggestions
│
├── requirements.txt
│   └── Python dependencies
│
├── README.md
│   └── Project documentation
│
└── .gitignore
    └── Excluded files and secrets
```

## 📊 Data Sources

### 1. Marketaux API
Used to retrieve financial news articles related to selected stock symbols.

### 2. Yahoo Finance
Integrated through the `yfinance` Python library to retrieve historical stock price information.

### 3. FinBERT
A pretrained financial language model from ProsusAI used to analyze financial text sentiment.

### 4. Google Gemini
Integrated for AI-powered financial news summarization and explanations. This component is currently being updated and tested.

## 💻 Installation and Setup

### Prerequisites

- Python 3.10 or later
- Git
- VS Code or another Python IDE
- Marketaux API key
- Google Gemini API key

### Step 1: Clone the repository

```bash
git clone https://github.com/MUHAMMEDKP425/ai-stock-sentiment.git
```

### Step 2: Navigate to the project directory

```bash
cd ai-stock-sentiment
```

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### Step 4: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Configure API keys

Create a `.env` file in the project root directory.

Add your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
MARKETAUX_API_KEY=your_marketaux_api_key
```

Never upload your `.env` file or expose your API keys publicly.

### Step 6: Run the application

```bash
streamlit run app.py
```

The application will open in your browser using the local Streamlit address.

## 📁 Project Structure

| File | Description |
|---|---|
| `app.py` | Main dashboard and application logic |
| `finbert_model.py` | FinBERT model loading and sentiment classification |
| `llm_gemini.py` | Gemini API integration |
| `news_fetcher.py` | Financial news retrieval |
| `news_scraper.py` | Webpage text extraction utility |
| `stock_list.py` | Predefined stock ticker list |
| `requirements.txt` | Project dependencies |
| `.gitignore` | Git exclusion rules |

## 🔮 Future Improvements

- Improve financial news freshness and retrieval.
- Update and fully test the Gemini integration.
- Integrate additional financial news sources.
- Expand the supported stock ticker database.
- Add historical sentiment tracking.
- Introduce sentiment trend comparisons.
- Explore stock price prediction using machine learning.
- Improve dashboard performance and user experience.

## ⚠