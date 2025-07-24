import scrapers.finviz_stock_news_scraper as finviz_stock_scraper
import scrapers.finviz_market_news_scraper as finviz_market_scraper
import scrapers.tradingview_news_scraper as tradingview_scraper
import mergers.finviz_tradingview_csv_merger as finviz_tradingview_csv_merger
import sentiments.finviz_stocknews_sentiment as finviz_stock_sentiment
import sentiments.finviz_tradingview_sentiment as finviz_tradingview_sentiment
import mergers.all_news_merged as all_news_merger
import sentiments.csv_jsonl_converter as csv_jsonl_converter
import sentiments.jsonl_cleaner as jsonl_cleaner
import time

def run_full_pipeline():
    print("main.py file has started")
    # Run the Finviz stock news scraper
    finviz_stock_scraper.finviz_stock_news_scraper()
    print("Finviz stock news scraper completed.")
    time.sleep(2)

    # Run the Finviz market news scraper
    finviz_market_scraper.finviz_market_news_scraper()
    print("Finviz market news scraper completed.")
    time.sleep(2)

    # Run the TradingView news scraper
    tradingview_scraper.scrape_all_tradingview()
    print("TradingView news scraper completed.")
    time.sleep(2)

    # Run the merger for Finviz and TradingView CSV files
    finviz_tradingview_csv_merger.parse_and_merge_news()
    print("Finviz and TradingView CSV merger completed.")
    time.sleep(2)

    # Run the sentiment analysis for Finviz stock news
    finviz_stock_sentiment.finviz_stock_sentiment()
    print("Finviz stock news sentiment analysis completed.")
    time.sleep(2)

    # Run the sentiment analysis for Finviz TradingView news
    finviz_tradingview_sentiment.finviz_tradingview_sentiment()
    print("Finviz TradingView news sentiment analysis completed.")
    time.sleep(2)

    # Run the merger for all news
    all_news_merger.merge_csv_files()
    print("All news merger completed.")
    time.sleep(2)

    # Convert CSV to JSONL
    csv_jsonl_converter.csv_to_json()
    print("CSV to JSONL conversion completed.")
    time.sleep(2)

    # Clean the JSONL file
    jsonl_cleaner.jsonl_cleaner()
    print("jsonl cleaning completed.")

if __name__ == "__main__":
    run_full_pipeline()
    print("Full pipeline execution completed.")