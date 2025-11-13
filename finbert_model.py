
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

class FinBERT:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    def analyze(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model(**inputs)
        scores = softmax(outputs.logits.detach().numpy()[0])

        labels = ["negative", "neutral", "positive"]
        sentiment = labels[scores.argmax()]

        return {
            "sentiment": sentiment,
            "scores": {
                "negative": float(scores[0]),
                "neutral": float(scores[1]),
                "positive": float(scores[2])
            }
        }
