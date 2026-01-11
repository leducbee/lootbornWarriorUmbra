#!/bin/bash
echo "--- Đang khởi tạo quá trình build cho Windows ---"
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller không tìm thấy. Đang cài đặt..."
    pip install pyinstaller
fi
pyinstaller --onefile --console --name "AutoScript" --distpath dist/win main.py
echo "--- Đang copy các file cần thiết vào thư mục dist/win ---"
cp config.json dist/win/
mkdir -p dist/win/src/assets/working
mkdir -p dist/win/src/assets/scanning
echo "--- Build hoàn tất! ---"
echo "--- Đang nén thư mục thành file zip ---"
cd dist && zip -r AutoScript_win.zip win && cd ..
echo "File thực thi và các cấu hình nằm trong thư mục: dist/win"
echo "File nén: dist/AutoScript_win.zip"
echo "Lưu ý: Bạn cần tự bỏ các file ảnh asset vào thư mục src/assets/working và src/assets/scanning trong dist/win (hoặc giải nén zip rồi bỏ vào)."
