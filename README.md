# KaraokeBookingApp

Ứng dụng đặt phòng karaoke trực tuyến - một giải pháp quản lý và đặt phòng karaoke hiệu quả.

## 📋 Mô tả

KaraokeBookingApp là một ứng dụng web được xây dựng với **Python** (Backend), **HTML/CSS** (Frontend) cho phép người dùng:
- Duyệt danh sách phòng karaoke
- Đặt phòng trực tuyến
- Quản lý các đơn đặt hàng
- Cập nhật thông tin phòng và giá cước

## 🛠️ Công nghệ sử dụng

- **Backend**: Python (Flask/Django)
- **Frontend**: HTML, CSS
- **Database**: MySQL
- **Hệ thống**: Web Application

## 📦 Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.x
- MySQL Server
- pip (Python package manager)

### 2. Cấu hình môi trường

```bash
# Clone repository
git clone https://github.com/num153/KaraokeBookingApp.git
cd KaraokeBookingApp

# Cài đặt dependencies
pip install -r requirements.txt

# Cấu hình biến môi trường
# Tạo file .env hoặc cấu hình trong ứng dụng
```

### 3. Cấu hình Database

1. **Tạo schema MySQL:**
   ```sql
   CREATE SCHEMA karadb;
   ```

2. **Cấu hình kết nối Python với MySQL:**
   - Tên user: `root`
   - Mật khẩu: [mật khẩu MySQL của bạn]
   - Database: `karadb`

3. **Tạo các bảng từ models:**
   ```bash
   python models.py
   ```

4. **Import dữ liệu ban đầu:**
   ```bash
   python create_db.py
   ```

## 🚀 Chạy ứng dụng

```bash
# Khởi chạy server
python app.py
```

Ứng dụng sẽ chạy trên `http://localhost:5000` (hoặc port khác tùy cấu hình)

## 📁 Cấu trúc dự án

```
KaraokeBookingApp/
├── app.py                 # File chính
├── create_db.py          # Script tạo database
├── models.py             # Định nghĩa models
├── requirements.txt      # Dependencies
├── templates/            # File HTML
├── static/              # File CSS, JS, images
└── README.md
```

## 👥 Tính năng chính

- ✅ Xem danh sách phòng karaoke
- ✅ Đặt phòng trực tuyến
- ✅ Quản lý đơn đặt hàng
- ✅ Giao diện người dùng thân thiện
- ✅ Hệ thống quản lý database

