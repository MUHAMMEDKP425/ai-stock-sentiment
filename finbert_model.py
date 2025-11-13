from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax
import torch
import streamlit as st

@st.cache_resource
def load_finbert():
    model_name = "ProsusAI/finbert"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    return tokenizer, model, device

class FinBERT:
    def __init__(self):
        self.tokenizer, self.model, self.device = load_finbert()

    def analyze_text(self, text, max_length=256):
        # tokenize text
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True
        )

        # move to CPU/GPU
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # model prediction
        with torch.no_grad():
            outputs = self.model(**inputs)

        # convert logits -> probabilities
        scores = softmax(outputs.logits.cpu().numpy()[0])

        labels = ["negative", "neutral", "positive"]

        return {
            "sentiment": labels[scores.argmax()],
            "scores": {
                "negative": float(scores[0]),
                "neutral": float(scores[1]),
