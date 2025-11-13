
import google.generativeai as genai
import os

def summarize_and_sentiment(text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("No GEMINI_API_KEY found")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"Summarize this news and predict its sentiment: {text}"
    response = model.generate_content(prompt)
    return {"raw": response.text}
