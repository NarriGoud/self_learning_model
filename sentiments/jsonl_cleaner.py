import json
import csv
import os

# 🔧 Configuration
INPUT_FILE = "data/converted_jsonl/converted.jsonl"   # or "sentiment_output.csv"
OUTPUT_FILE = "data/cleaned_jsonl/final_cleaned.jsonl"    # or "cleaned_output.csv"
TARGET_TEXT = "Sign in to read exclusive news"

def normalize_text(text):
    return ' '.join(text.strip().split())

def clean_jsonl(input_path, output_path, target_text):
    total = 0
    removed = 0
    seen_inputs = set()

    # 🧠 Load existing inputs to avoid duplicates across appends
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as existing:
            for line in existing:
                try:
                    item = json.loads(line.strip())
                    seen_inputs.add(item.get("input", "").strip())
                except:
                    continue

    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'a', encoding='utf-8') as outfile:  # append mode

        for line in infile:
            total += 1
            try:
                item = json.loads(line.strip())
                input_text = item.get("input", "").strip()
                output_text = item.get("output", "").strip() if "output" in item else ""

                # Normalization
                input_text = normalize_text(input_text)
                item["input"] = input_text

                # Cleaning Conditions
                if (
                    not input_text or
                    input_text == target_text or
                    len(output_text) < 5 or
                    input_text in seen_inputs
                ):
                    removed += 1
                    continue

                seen_inputs.add(input_text)
                outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

            except json.JSONDecodeError:
                print(f"⚠️ Skipping malformed line: {line.strip()}")

    print(f"✅ [JSONL] Total rows processed: {total}")
    print(f"🗑️ [JSONL] Rows removed: {removed}")
    print(f"📁 Appended to file: {output_path}")


def clean_csv(input_path, output_path, target_text):
    total = 0
    removed = 0
    seen_inputs = set()

    # 🚫 Appending CSV is more complex. This block assumes rewrite only.
    # If needed, we can implement smart append with deduplication.

    with open(input_path, 'r', encoding='utf-8', newline='') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            total += 1
            input_text = normalize_text(row.get("input", ""))
            output_text = row.get("output", "").strip()

            row["input"] = input_text  # Normalize input

            if (
                not input_text or
                input_text == target_text or
                len(output_text) < 5 or
                input_text in seen_inputs
            ):
                removed += 1
                continue

            seen_inputs.add(input_text)
            writer.writerow(row)

    print(f"✅ [CSV] Total rows processed: {total}")
    print(f"🗑️ [CSV] Rows removed: {removed}")
    print(f"📁 Cleaned file saved as: {output_path}")


def jsonl_cleaner():
    ext = os.path.splitext(INPUT_FILE)[1].lower()
    if ext == ".jsonl":
        clean_jsonl(INPUT_FILE, OUTPUT_FILE, TARGET_TEXT)
    elif ext == ".csv":
        clean_csv(INPUT_FILE, OUTPUT_FILE, TARGET_TEXT)
    else:
        print("❌ Unsupported file type. Please use a .jsonl or .csv file.")

if __name__ == "__main__":
    jsonl_cleaner()
