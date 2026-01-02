import asyncio
from telegram import Bot

async def send_telegram_message(token, chat_id, message):
    """
    Gửi tin nhắn đến Telegram.
    """
    try:
        bot = Bot(token=token)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"Lỗi khi gửi Telegram: {e}")
        return False

async def send_telegram_photo(token, chat_id, photo_path, caption=None):
    """
    Gửi ảnh đến Telegram kèm chú thích.
    """
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
    # Đây là mẫu, người dùng cần điền thông tin thật vào
    TOKEN = "xx"
    CHAT_ID = "xx"
    MESSAGE = "Test notification từ Auto Script!"
    
    # Chạy thử
    if TOKEN == "xx": # Đã cập nhật token thật
        asyncio.run(send_telegram_message(TOKEN, CHAT_ID, MESSAGE))
    else:
        print("Vui lòng thiết lập TOKEN và CHAT_ID trong file này hoặc file cấu hình.")
