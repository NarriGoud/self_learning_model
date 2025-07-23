from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import pandas as pd
from torch.nn.functional import softmax
import os

def finviz_stock_sentiment():
    # Load FinBERT model
    tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    # Input and output file paths
    INPUT_FILE = r"data/processed/finviz_stock_news.csv"
    OUTPUT_FILE = r"data/sentiment_encoded/finviz_sentiment_stock_news.csv"

    # Load encoded headlines
    df = pd.read_csv(INPUT_FILE)

    # Validate required columns
    if 'headline' not in df.columns or 'tickers' not in df.columns:
        raise ValueError("❌ Required columns ('headline', 'tickers') not found in the CSV.")

    # Sentiment label mapping
    label_map = {
        0: "Bearish",   # negative
        1: "Bullish",   # positive
        2: "Neutral"    # neutral
    }

    # Predict sentiment
    sentiments = []
    for text in df["headline"].fillna(""):
        inputs = tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = softmax(logits, dim=1)
            label = torch.argmax(probs).item()
            sentiment = label_map[label]
            sentiments.append(sentiment)

    # Add sentiment column and save
    df["sentiment"] = sentiments
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ Sentiment-encoded file saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    finviz_stock_sentiment()