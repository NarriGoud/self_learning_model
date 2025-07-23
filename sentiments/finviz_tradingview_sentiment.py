import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForTokenClassification, pipeline

def finviz_tradingview_sentiment():
    # Load FinBERT model for sentiment
    sentiment_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    sentiment_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")

    # Load NER model for ticker extraction
    ner_tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    ner_model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
    ner_pipeline = pipeline("ner", model=ner_model, tokenizer=ner_tokenizer, grouped_entities=True)

    # Load input CSV
    input_path = r"data/processed/finviz_tradingview_merged.csv"
    df = pd.read_csv(input_path)

    # Sentiment mapping (FinBERT returns: 0 = negative, 1 = positive, 2 = neutral)
    label_map = {
        0: "Bearish",
        1: "Bullish",
        2: "Neutral"
    }

    # Run sentiment analysis
    def get_sentiment(text):
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = sentiment_model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            predicted_class = torch.argmax(scores, dim=1).item()
        return label_map[predicted_class]

    # Run NER to extract tickers (ORG-like entities)
    def extract_tickers(text):
        entities = ner_pipeline(text)
        tickers = []
        for ent in entities:
            word = ent['word'].replace('##', '').strip()
            if word.isupper() and 1 <= len(word) <= 5:
                tickers.append(word)
        return ', '.join(sorted(set(tickers)))

    # Apply both sentiment and ticker extraction
    df["sentiment"] = df["Headline"].fillna("").apply(get_sentiment)
    df["tickers"] = df["Headline"].fillna("").apply(extract_tickers)

    # Save output
    output_path = r"data/sentiment_encoded/finviz_sentiment_tradingview.csv"
    df.to_csv(output_path, index=False)

    print(f"✅ Sentiment analysis completed and saved to {output_path}")

if __name__ == "__main__":
    finviz_tradingview_sentiment()