from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import tempfile
import re
import os
import shutil

def scrape_all_tradingview(output_file: str = 'data/raw/tradingview_news.txt'):
    # List of URLs to scrape
    urls = [
        "https://in.tradingview.com/news/top-stories/all/",
        "https://in.tradingview.com/news/top-providers/reuters/",
        "https://in.tradingview.com/news/top-providers/trading-economics/",
        "https://in.tradingview.com/news/top-providers/moneycontrol/",
        "https://in.tradingview.com/news/top-providers/tradingview/",
        "https://in.tradingview.com/news/top-providers/marketbeat/",
        "https://in.tradingview.com/news/top-providers/barchart/",
        "https://in.tradingview.com/news/top-providers/cointelegraph/",
        "https://in.tradingview.com/news/top-providers/beincrypto/",
        "https://in.tradingview.com/news/top-providers/zacks/",
        "https://in.tradingview.com/news/top-providers/stockstory/",
        "https://in.tradingview.com/news/top-providers/marketindex/",
        "https://in.tradingview.com/news/markets/crypto/",
        "https://in.tradingview.com/news/markets/corporate-bonds/",
        "https://in.tradingview.com/news/world/middle-east/",
        "https://in.tradingview.com/news/world/south-america/",
        "https://in.tradingview.com/news/world/uk/",
        "https://in.tradingview.com/news/world/asia/",
        "https://in.tradingview.com/news/world/oceania/"
    ]

    options = Options()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--allow-insecure-localhost")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")  # ✅ Recommended headless mode

    # ✅ Create a unique temp user data dir
    user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={user_data_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # 🧹 Save the path to cleanup later
    driver.user_data_dir = user_data_dir

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'a', encoding='utf-8') as f:
        for url in urls:
            print(f"[→] Scraping: {url}")
            driver.get(url)
            time.sleep(5)

            # Extract timestamps
            timestamp_elements = driver.find_elements(By.XPATH, '//relative-time')
            timestamps = [elem.get_attribute('title') for elem in timestamp_elements]

            # Extract headlines
            headline_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "title-BpSwpmE")]')
            headlines = [elem.text.strip() for elem in headline_elements]

            # Extract providers
            provider_elements = driver.find_elements(By.XPATH, '//span[contains(@class, "provider")]')
            providers = [elem.text.strip() for elem in provider_elements]

            # Align lengths
            min_len = min(len(timestamps), len(headlines), len(providers))

            for i in range(min_len):
                f.write(f"[{timestamps[i]}] ({providers[i]}) {headlines[i]}")

            print(f"[✓] Done: {min_len} items scraped")

    driver.quit()
    cleanup_driver(driver)
    print("[✔] All done! Saved to", output_file)


def cleanup_driver(driver):
    if hasattr(driver, "user_data_dir"):
        shutil.rmtree(driver.user_data_dir, ignore_errors=True)

def parse_news_line(line):
    # Extract timestamp
    timestamp_match = re.search(r"[(.*?)]", line)
    timestamp = timestamp_match.group(1).strip() if timestamp_match else ""

    # Extract provider
    provider_match = re.search(r"((.*?))", line)
    provider = provider_match.group(1).strip() if provider_match else ""

    # Get remaining content after provider
    rest = re.split(r")s*", line, maxsplit=1)[-1]

    # Extract symbol and headline
    symbol_match = re.match(r"([A-Z-/.]+):s+", rest)
    if symbol_match:
        symbol = symbol_match.group(1).strip()
        headline = rest[symbol_match.end():].strip()
    else:
        symbol = ""
        headline = rest.strip()

    return [timestamp, symbol, provider, headline]

if __name__ == "__main__":
    scrape_all_tradingview()


