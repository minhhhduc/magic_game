# Magic Fighting Game - Pixel Edition

Một trò chơi đối kháng ma thuật sống động kết hợp giữa phong cách đồ họa Pixel Art cổ điển và công nghệ nhận diện cử chỉ tay hiện đại (AI Vision).

## 🌟 Tính Năng Nổi Bật

- **AI Vision Control**: Sử dụng Webcam để vẽ và tung phép thuật bằng chính đôi tay của bạn.
- **Đồ Họa Pixel Art Đỉnh Cao**: Hiệu ứng hạt (particles), starfield parallax, và các đòn đánh ma thuật rực rỡ.
- **Hệ Thống Phối Hợp Tối Ưu**: Game đã được tối ưu hóa cực mạnh (Pre-rendered rendering) giúp duy trì FPS ổn định.
- **Nhiều Anh Hùng**: 5 nhân vật khác nhau với các kỹ năng và thuộc tính riêng biệt.
- **Bot Thông Minh**: Đối trọng với AI bot có khả năng né đòn và phản công linh hoạt.
- **Báo Cáo Trận Đấu**: Màn hình kết thúc trận chuyên nghiệp với tính năng chơi lại (Rematch) tức thì.

## 🛠️ Yêu Cầu Hệ Thống

- **Python**: 3.10 trở lên.
- **Phụ kiện**: Webcam (để chơi bằng cử chỉ tay).
- **Thư viện chính**: `pygame`, `opencv-python`, `mediapipe`, `numpy`, `scikit-learn`.

## 📥 Cài Đặt

1. **Tải mã nguồn**:
   ```bash
   git clone https://github.com/minhhhduc/magic_game.git
   cd magic_game
   ```

2. **Cài đặt môi trường & thư viện**:
   ```bash
   pip install .
   ```

3. **Chạy game**:
   ```bash
   magic-game
   ```

## 🎮 Cách Chơi

### 1. Điều khiển bằng Cử Chỉ (Ưu tiên)
- **Vẽ Phép**: Dùng ngón trỏ di chuyển trên màn hình camera để vẽ hình.
- **Tung Chiêu**: Chụm ngón trỏ và ngón giữa (Pinch) để xác nhận và kích hoạt phép.
- **Các loại phép**:
  - `/`: **Gun** (Sát thương nhanh)
  - `\`: **Bomb** (Sát thương diện rộng)
  - `O`: **Freeze** (Đóng băng kẻ địch)
  - `|`: **Shield** (Bảo vệ bản thân)

### 2. Điều khiển bằng Bàn Phím
- **Tung chiêu nhanh**: Nhấn các phím `1`, `2`, `3`, `4` (Dùng khi không có webcam).
- **Di chuyển**: Phím mũi tên Trái/Phải.
- **Menu/Chọn nhân vật**:
  - `S`: Bắt đầu / Quay lại Menu chính.
  - `Arrows`: Duyệt qua các anh hùng.
  - `ENTER`: Xác nhận chọn nhân vật.
- **Kết thúc trận**:
  - `R`: **Rematch** (Chơi lại ngay lập tức với nhân vật cũ).
  - `S`: Quay lại Menu chính.

## ⚙️ Cấu Hình Nâng Cao
Bạn có thể tùy chỉnh trong file `src/config/settings.py`:
- `TURN_PREDICT_CONSOLE`: Bật/Tắt log nhận diện của AI trong console.
- `FPS`, `WIDTH`, `HEIGHT`: Các thông số kỹ thuật của cửa sổ game.