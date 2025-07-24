import pandas as pd
import os

def merge_csv_files():
    try:
        file1 = 'data/sentiment_encoded/finviz_sentiment_stock_news.csv'
        file2 = 'data/sentiment_encoded/finviz_sentiment_tradingview.csv'

        # Output file path
        output_file = 'data/merged/finviz_tradingview_merged.csv'
        df1 = pd.read_csv(file1)
        df2 = pd.read_csv(file2)

        merged_df = pd.concat([df1, df2], ignore_index=True)

        # Optional: Drop duplicates if needed
        merged_df.drop_duplicates(inplace=True)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        merged_df.to_csv(output_file, index=False)

        print(f"[✅] Merged CSV saved to: {output_file}")
    except Exception as e:
        print(f"[❌] Error during merge: {e}")

if __name__ == "__main__":
    merge_csv_files()


