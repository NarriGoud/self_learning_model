import json
import os
import random

# 🔧 Configuration
INPUT_FILE = "data/converted_jsonl/converted.jsonl"
OUTPUT_FILE = "data/cleaned_jsonl/final_cleaned.jsonl"
SHUFFLED_OUTPUT_FILE = "data/final_shuffled/final_cleaned_shuffled.jsonl"
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

    # 👉 Automatically shuffle after cleaning
    shuffler(output_path, SHUFFLED_OUTPUT_FILE)

def shuffler(input_path="data/cleaned_jsonl/final_cleaned.jsonl", output_path="data/cleaned_jsonl/final_cleaned_shuffled.jsonl"):
    # 🔄 Read lines
    with open(input_path, 'r', encoding='utf-8') as infile:
        data = [json.loads(line) for line in infile]

    # 🔀 Shuffle
    random.shuffle(data)

    # 💾 Write shuffled lines
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for item in data:
            outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"🔀 Shuffled JSONL saved to: {output_path}")

def jsonl_cleaner():
    ext = os.path.splitext(INPUT_FILE)[1].lower()
    if ext == ".jsonl":
        clean_jsonl(INPUT_FILE, OUTPUT_FILE, TARGET_TEXT)
    else:
        print("❌ Unsupported file type. Please use a .jsonl file.")

if __name__ == "__main__":
    jsonl_cleaner()
