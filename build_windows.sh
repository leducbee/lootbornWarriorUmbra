#!/bin/bash

echo "--- Đang khởi tạo quá trình build cho Windows ---"

# Kiểm tra pyinstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller không tìm thấy. Đang cài đặt..."
    pip install pyinstaller
fi

# Chạy lệnh build cho Windows
pyinstaller --onefile --console --name "AutoScript" --distpath dist/win main.py

echo "--- Đang copy các file cần thiết vào thư mục dist/win ---"
cp config.json dist/win/
cp initial_coordinates.txt dist/win/
# Tạo lại cấu trúc src/assets rỗng
mkdir -p dist/win/src/assets/working
mkdir -p dist/win/src/assets/scanning

echo "--- Build hoàn tất! ---"
echo "File thực thi và các cấu hình nằm trong thư mục: dist/win"
echo "Lưu ý: Bạn cần tự bỏ các file ảnh asset vào thư mục src/assets/working và src/assets/scanning trong dist/win."
