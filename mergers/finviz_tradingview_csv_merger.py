import re
import csv
from datetime import datetime

def parse_and_merge_news():
    # File paths
    TXT_FILES = [
        "data/raw/tradingview_news.txt",
        "data/raw/finviz_market_news.txt"
    ]
    OUTPUT_FILE = "data/processed/finviz_tradingview_merged.csv"

    # Regex patterns
    pattern1 = re.compile(r"^\[(\w{3} \d{1,2}, \d{4}), [^\]]+\] \((.*?)\) (.+)$")
    pattern2 = re.compile(r"^(\w{3}-\d{2}-\d{4}),\s([^,]+),\s(.+)$")

    parsed_rows = []

    for file_path in TXT_FILES:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                # Try pattern1
                match1 = pattern1.match(line)
                if match1:
                    try:
                        raw_date = match1.group(1)
                        parsed_date = datetime.strptime(raw_date, "%b %d, %Y").strftime("%b-%d-%Y")
                    except ValueError:
                        parsed_date = raw_date

                    provider = match1.group(2)
                    headline = match1.group(3)
                    parsed_rows.append([parsed_date, provider, headline])
                    continue

                # Try pattern2
                match2 = pattern2.match(line)
                if match2:
                    date = match2.group(1)
                    provider = match2.group(2).strip()
                    headline = match2.group(3)
                    parsed_rows.append([date, provider, headline])
                    continue

                print(f"⚠️ Skipping unmatched line: {line}")

    # Save to CSV
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["date", "provider", "headline"])
        writer.writerows(parsed_rows)

    print(f"✅ Parsed {len(parsed_rows)} headlines. Saved to '{OUTPUT_FILE}'")

# Example call
if __name__ == "__main__":
    parse_and_merge_news()


