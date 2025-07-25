import requests
import time
import os
import telegram
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = "https://your-render-api-url.onrender.com"

bot = telegram.Bot(token=BOT_TOKEN)

async def main():
    print("[🤖] Telegram bot is live on Render!")
    last_update_id = None

    while True:
        updates = await bot.get_updates(offset=last_update_id, timeout=10)

        for update in updates:
            last_update_id = update.update_id + 1

            text = update.message.text.lower()
            if text == "/status":
                res = requests.get(f"{API_URL}/status").json()
                await bot.send_message(chat_id=CHAT_ID, text=f"Status: {res['status']}")
            elif text == "/run":
                await bot.send_message(chat_id=CHAT_ID, text="🚀 Running pipeline...")
                res = requests.get(f"{API_URL}/run").json()
                await bot.send_message(chat_id=CHAT_ID, text="✅ Done\n" + res.get("stdout", "No output"))

        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
