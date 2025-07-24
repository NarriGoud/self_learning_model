from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import time
import re
import os
import csv
from datetime import datetime
import shutil

# --- Config ---
TARGET_URL = "https://finviz.com/news.ashx?v=3"
OUTPUT_FILE = "data/raw/finviz_stock_news.txt"

def cleanup_driver(driver):
    if hasattr(driver, "user_data_dir"):
        shutil.rmtree(driver.user_data_dir, ignore_errors=True)

def setup_driver():
    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--headless=new")  # Use new headless mode (better support)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # ✅ Use a unique temp directory to avoid conflicts
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    # Launch driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Attach the path for later cleanup
    driver.user_data_dir = user_data_dir
    return driver


def scrape_stock_news(driver):
    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    time.sleep(5)  # Wait for the full page to load

    rows = driver.find_elements(By.CSS_SELECTOR, "tr.news_table-row")
    print(f"✅ Found {len(rows)} rows.")

    data_lines = []

    for row in rows:
        try:
            tds = row.find_elements(By.TAG_NAME, "td")

            time_text = tds[0].text.strip() if len(tds) > 0 else ""

            provider_elem = tds[1].find_elements(
                By.CSS_SELECTOR,
                "span.news_date-cell.color-text.is-muted.text-right"
            )
            provider_text = provider_elem[-1].text.strip() if provider_elem else "Unknown"

            headline_elem = tds[1].find_element(By.CLASS_NAME, "nn-tab-link")
            headline = headline_elem.text.strip()

            tickers_elem = tds[1].find_elements(By.CLASS_NAME, "select-none")
            tickers = [t.text.strip() for t in tickers_elem if t.text.strip()]
            ticker_str = ", ".join(tickers)

            line = f"{time_text}, {provider_text}, {headline}, {ticker_str}"
            data_lines.append(line)

        except Exception as e:
            print(f"⚠️ Error scraping a row: {e}")
            continue

    return data_lines

def save_to_txt(data_lines, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for line in data_lines:
            f.write(line + "")
    print(f"✅ Scraped and saved {len(data_lines)} rows to '{output_file}'")

def clean_finviz_news():
    input_txt = "data/raw/finviz_stock_news.txt"
    output_csv = "data/processed/finviz_stock_news.csv"
    today = datetime.today().strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)

    # Load lines
    with open(input_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    data = []

    for line in lines:
        parts = line.strip().split(", ", 3)
        if len(parts) < 3:
            continue

        time_text = parts[0]
        provider = parts[1]
        headline = parts[2] if len(parts) == 3 else parts[2]

        tickers = list(set(re.findall(r"[A-Z]{1,5}", headline)))

        data.append([today, provider, headline.strip(), tickers])

    # Write to CSV
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "provider", "headline", "tickers"])
        writer.writerows(data)

    print("✅ Cleaned CSV saved as:", output_csv)

def finviz_stock_news_scraper():
    driver = setup_driver()
    try:
        data_lines = scrape_stock_news(driver)
    finally:
        driver.quit()
        cleanup_driver(driver)
    save_to_txt(data_lines, OUTPUT_FILE)
    time.sleep(2)  # Ensure file is written before processing
    clean_finviz_news()

if __name__ == "__main__":
    finviz_stock_news_scraper()


