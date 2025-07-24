from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import tempfile
import os
import csv
import shutil

# --- Config ---
TARGET_URL = "https://finviz.com/news.ashx?v=2"
OUTPUT_FILE = "data/raw/finviz_market_news.txt"
YEAR = "2025"

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

def scrape_news(driver, year):
    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    time.sleep(5)  # Allow page to load
    print("Page loaded, starting to scrape...")

    rows = driver.find_elements(By.CSS_SELECTOR, "tr.news_table-row")
    current_provider = None
    scraped_data = []

    for row in rows:
        try:
            # Check if row is a provider heading
            provider_cell = row.find_elements(By.CLASS_NAME, "news_heading-cell")
            if provider_cell:
                current_provider = provider_cell[0].text.strip()
                continue

            if current_provider:
                time_elem = row.find_element(By.CLASS_NAME, "news_date-cell").text.strip()
                headline_elem = row.find_element(By.CLASS_NAME, "nn-tab-link").text.strip()
                full_datetime = f"{time_elem}-{year}"
                scraped_data.append((full_datetime, current_provider, headline_elem))
        except:
            continue

    return scraped_data

def save_to_txt(data, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "provider", "headline"])  # ✅ header added
        writer.writerows(data)
    print(f"Scraped {len(data)} news items and saved to {output_file}")

def finviz_market_news_scraper():
    driver = setup_driver()
    try:
        data = scrape_news(driver, YEAR)
    finally:
        driver.quit()
        cleanup_driver(driver)
    save_to_txt(data, OUTPUT_FILE)

if __name__ == "__main__":
    finviz_market_news_scraper()


