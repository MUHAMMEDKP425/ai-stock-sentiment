import google.generativeai as genai
import os

def summarize_and_sentiment_gemini(text):
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise Exception("No GEMINI_API_KEY found in Streamlit Secrets.")

    # Configure Gemini
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
    Summarize this stock news in 2 sentences.
    Then give sentiment: positive, neutral, or negative.
    Then give one short reason explaining why.

    News:
    {text}
    """

    response = model.generate_content(prompt)
    return response.text
