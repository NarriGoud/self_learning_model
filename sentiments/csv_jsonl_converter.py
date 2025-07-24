import os
import json
import pandas as pd
import time
import requests
import random
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# ========== 🔑 CONFIG ==========
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "meta-llama/llama-3-8b-instruct"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
BATCH_SIZE = 20
INPUT_CSV = "data/merged/finviz_tradingview_merged.csv"
OUTPUT_JSONL = "data/converted_jsonl/converted.jsonl"
UNIVERSAL_INSTRUCTIONS = [
    "Analyze the sentiment of this stock market news headline.",
    "Determine if the following stock market news headline is bullish, bearish, or neutral.",
    "Classify the sentiment expressed in this financial news headline.",
    "Identify the market sentiment in the headline provided.",
    "Assess whether this headline indicates a positive, negative, or neutral sentiment.",
    "Evaluate the investor sentiment reflected in the following news headline.",
    "Detect the sentiment in the given stock-related news headline.",
    "Is this stock news headline bullish, bearish, or neutral? Justify your answer.",
    "Provide sentiment analysis (bullish, bearish, neutral) for the following headline.",
    "What is the likely market reaction to this news headline? Label the sentiment."
]
# ===============================

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://yourdomain.com",
    "X-Title": "HeadlineSentimentTool"
}

def build_prompt(instruction, headline):
    return f"""{instruction}

### Headline:
{headline}

### Output Format:
Sentiment: <Bullish / Bearish / Neutral>
Reason: <Short reason>"""

def format_jsonl(instruction, input_text, output_text):
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output_text
    }

def call_llm(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"⚠️ Exception: {e}")
    return None

def process_batch(batch_df):
    results = []
    for _, row in batch_df.iterrows():
        headline = row['headline']
        instruction = random.choice(UNIVERSAL_INSTRUCTIONS)
        prompt = build_prompt(instruction, headline)
        output = call_llm(prompt)

        if output:
            formatted = format_jsonl(instruction, headline, output.strip())
        else:
            formatted = format_jsonl(instruction, headline, "Sentiment: Unknown\nReason: API call failed.")

        results.append(formatted)
        time.sleep(1)

    return results

def save_jsonl(data_list, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✅ JSONL file saved: {filename}")

def csv_to_json():
    df = pd.read_csv(INPUT_CSV)
    print(f"📊 Loaded {len(df)} headlines.")
    all_results = []

    for i in range(0, len(df), BATCH_SIZE):
        batch_df = df.iloc[i:i+BATCH_SIZE]
        print(f"🔄 Processing batch {i//BATCH_SIZE + 1}/{(len(df) + BATCH_SIZE - 1)//BATCH_SIZE}")
        results = process_batch(batch_df)
        all_results.extend(results)

    save_jsonl(all_results, OUTPUT_JSONL)
    print("🎯 All done!")

if __name__ == "__main__":
    csv_to_json()
