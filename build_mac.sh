#!/bin/bash

echo "--- Đang khởi tạo quá trình build cho macOS ---"

# Kiểm tra pyinstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller không tìm thấy. Đang cài đặt..."
    pip install pyinstaller
fi

# Chạy lệnh build
pyinstaller --onefile --name "AutoScript" --distpath dist/mac main.py

echo "--- Đang copy các file cần thiết vào thư mục dist/mac ---"
cp config.json dist/mac/
cp initial_coordinates.txt dist/mac/
# Tạo lại cấu trúc src/assets rỗng
mkdir -p dist/mac/src/assets/working
mkdir -p dist/mac/src/assets/scanning

echo "--- Build hoàn tất! ---"
echo "File thực thi và các cấu hình nằm trong thư mục: dist/mac"
echo "Lưu ý: Bạn cần tự bỏ các file ảnh asset vào thư mục src/assets/working và src/assets/scanning trong dist/mac."
