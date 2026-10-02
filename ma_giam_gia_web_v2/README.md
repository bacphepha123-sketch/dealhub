# Website tổng hợp mã giảm giá

Website Flask + SQLite gồm:

- Trang chủ hiển thị mã giảm giá.
- Lọc theo Shopee, Lazada, TikTok Shop.
- Tìm kiếm mã.
- Nút sao chép mã.
- Nút đi tới sàn.
- Trang admin đăng nhập.
- Admin thêm / sửa / xóa / bật tắt mã.
- Database SQLite tự tạo.

## 1. Cài Python

Khuyến nghị Python 3.11+.

## 2. Mở terminal trong thư mục dự án

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

## 3. Cài thư viện

```bash
pip install -r requirements.txt
```

## 4. Chạy web

```bash
python app.py
```

Sau đó mở:

http://127.0.0.1:5000

## Tài khoản admin demo

Username:

```text
admin
```

Password:

```text
123456
```

Bạn nên đổi tài khoản/mật khẩu và `app.secret_key` trước khi đưa website lên internet.

## Cấu trúc

```text
ma_giam_gia_web/
│
├── app.py
├── requirements.txt
├── README.md
├── coupons.db        # tự sinh sau lần chạy đầu
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── admin.html
│   └── coupon_form.html
│
└── static/
    └── style.css
```
