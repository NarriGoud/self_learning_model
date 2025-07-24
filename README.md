# JSONL/CSV Cleaner Utility 🧹

This is a simple Python script to clean `.jsonl` or `.csv` files by:
- Removing duplicate entries based on `input`
- Skipping rows with empty or short outputs
- Filtering out known unwanted content (like "Sign in to read exclusive news")
- Normalizing whitespace and formatting

## 🔧 Configuration
Edit the following variables inside the script:
- `INPUT_FILE`: Path to your input file (`.jsonl` or `.csv`)
- `OUTPUT_FILE`: Path where the cleaned output will be saved
- `TARGET_TEXT`: Any specific unwanted line of text to be filtered out

## 🚀 Usage
```bash
python clean_data.py
