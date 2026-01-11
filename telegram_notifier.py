import asyncio
from telegram import Bot
async def send_telegram_message(token, chat_id, message):
    try:
        bot = Bot(token=token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Lỗi khi gửi Telegram: {e}")
        return False
async def send_telegram_photo(token, chat_id, photo_path, caption=None):
    try:
        bot = Bot(token=token)
        async with bot:
            with open(photo_path, 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo, caption=caption)
        return True
    except Exception as e:
        print(f"Lỗi khi gửi ảnh Telegram: {e}")
        return False
if __name__ == "__main__":
    import os
    import json
    TOKEN = "xx"
    CHAT_ID = "xx"
    CONFIG_FILE = "config.json"
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                token = config.get("telegram_token", TOKEN)
                chat_id = str(config.get("telegram_chat_id", CHAT_ID))
                if token in ["", "xx", "your_token_here"] or chat_id in ["", "yy", "your_chat_id_here"]:
                    TOKEN = ""
                    CHAT_ID = ""
                else:
                    TOKEN = token
                    CHAT_ID = chat_id
        except Exception:
            pass
    MESSAGE = "Test notification từ Auto Script!"
    if TOKEN and CHAT_ID:
        asyncio.run(send_telegram_message(TOKEN, CHAT_ID, MESSAGE))
    else:
        print("Vui lòng thiết lập TOKEN và CHAT_ID hợp lệ trong file config.json.")
