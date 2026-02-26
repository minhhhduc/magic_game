# Magic Fighting Game - Pixel Edition

Một trò chơi chiến đấu ma thuật sử dụng nhận diện cử chỉ tay (MediaPipe) và đồ họa Pixel Art.

## Yêu cầu hệ thống
- Python 3.9 trở lên
- Webcam (để nhận diện cử chỉ)

## Hướng dẫn cài đặt

1. **Clone repository:**
   ```bash
   git clone https://github.com/minhhhduc/magic_game.git
   cd magic_game
   ```

2. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy game:**
   ```bash
   python main.py
   ```

## Cách chơi
- **Cử chỉ tay:**
  - Vẽ hình trên màn hình bằng ngón trỏ.
  - **Chụm ngón trỏ và ngón giữa** để kích hoạt phép thuật.
- **Các loại phép thuật:**
  - `O`: Phép Đóng băng (Freeze)
  - `/`: Bắn súng (Gun)
  - `\`: Nổ (Explosion)
  - `|`: Khiên bảo vệ (Shield)
- **Điều khiển phím:**
  - `S`: Bắt đầu / Chơi lại
  - `ENTER`: Chọn nhân vật
  - `Mũi tên Trái/Phải`: Duyệt nhân vật
  - `1, 2, 3, 4`: Tung chiêu nhanh (nếu không có webcam)

## Tính năng nổi bật
- Nhận diện cử chỉ tay thời gian thực.
- Bot đối thủ thông minh, có phản xạ và chiến thuật né chiêu.
- Hiệu ứng âm thanh và nhạc nền đã được cân bằng chuyên nghiệp.
肢
