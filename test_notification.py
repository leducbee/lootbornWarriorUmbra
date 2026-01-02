import asyncio
from telegram_notifier import send_telegram_message, send_telegram_photo
from telegram import Bot
import pyautogui
import os

# Telegram Config
TELEGRAM_TOKEN = "xx"
TELEGRAM_CHAT_ID = "xx"

async def main_loop():
    title = "Auto Script Notification"
    message = "Found treasure"
    
    # Khởi tạo offset để bỏ qua các tin nhắn cũ
    last_update_id = -1
    try:
        bot = Bot(token=TELEGRAM_TOKEN)
        async with bot:
            updates = await bot.get_updates(offset=-1, timeout=1)
            if updates:
                last_update_id = updates[-1].update_id
                print(f"Đã bỏ qua các tin nhắn cũ (ID cuối: {last_update_id})")
            
            print(f"Bắt đầu vòng lặp gửi thông báo mỗi 20 giây...")
            print(f"Gửi 'stop' qua Telegram để dừng lại.")

            seconds_counter = 0
            while True:
                # 1. Kiểm tra lệnh 'stop' từ Telegram mỗi giây
                try:
                    updates = await bot.get_updates(offset=last_update_id + 1, timeout=1)
                    for update in updates:
                        last_update_id = update.update_id
                        if update.message and str(update.message.chat_id) == TELEGRAM_CHAT_ID:
                            text = update.message.text.lower().strip()
                            print(f"Nhận tin nhắn: '{text}' (ID: {update.update_id})")
                            if text == "stop":
                                print(f"Đã nhận lệnh 'stop' (ID: {update.update_id}). Đang dừng vòng lặp...")
                                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="Vòng lặp thông báo đã dừng theo yêu cầu của bạn.")
                                return
                except Exception as e:
                    print(f"Lỗi khi kiểm tra lệnh: {e}")

                # 2. Gửi thông báo mỗi 20 giây
                if seconds_counter % 20 == 0:
                    print(f"[{seconds_counter}s] Đang capture màn hình và gửi thông báo: {message}...")
                    screenshot_path = "test_screenshot.png"
                    try:
                        img = pyautogui.screenshot()
                        img.save(screenshot_path)
                        
                        if os.path.exists(screenshot_path):
                            success = await send_telegram_photo(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, screenshot_path, caption=f"🔔 {title}\n{message}")
                        else:
                            print(f"Lỗi: Không thể tạo file screenshot {screenshot_path}")
                            success = await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"🔔 {title}\n{message} (Không kèm ảnh do lỗi capture)")
                        
                        if success:
                            print("Đã gửi thành công kèm ảnh.")
                        else:
                            print("Gửi thất bại.")
                    except Exception as e:
                        print(f"Lỗi khi capture/gửi ảnh: {e}")
                        await send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, f"🔔 {title}\n{message} (Lỗi: {e})")
                    
                    # Xóa file sau khi gửi
                    if os.path.exists(screenshot_path):
                        os.remove(screenshot_path)

                seconds_counter += 1
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Lỗi khởi tạo hoặc thực thi bot: {e}")

if __name__ == "__main__":
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            asyncio.run(main_loop())
        except KeyboardInterrupt:
            print("\nĐã dừng bởi người dùng (Ctrl+C).")
    else:
        print("Vui lòng thiết lập TELEGRAM_TOKEN và TELEGRAM_CHAT_ID.")
