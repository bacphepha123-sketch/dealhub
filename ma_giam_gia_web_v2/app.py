from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = "coupons.db"

ADMIN_USER = "admin"
ADMIN_PASSWORD = "123456"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            title TEXT NOT NULL,
            code TEXT NOT NULL,
            discount TEXT NOT NULL,
            min_order TEXT DEFAULT '',
            expires_at TEXT DEFAULT '',
            link TEXT DEFAULT '',
            description TEXT DEFAULT '',
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM coupons").fetchone()[0]
    if count == 0:
        sample = [
            ("Shopee", "Giảm 50K đơn từ 299K", "SALE50", "50K", "299K", "2026-12-31", "https://shopee.vn/", "Mã mẫu để bạn thay bằng mã thật."),
            ("Lazada", "Giảm 100K đơn từ 499K", "LAZADA100", "100K", "499K", "2026-12-31", "https://www.lazada.vn/", "Mã mẫu."),
            ("TikTok Shop", "Giảm 30K đơn từ 199K", "TIKTOK30", "30K", "199K", "2026-12-31", "https://shop.tiktok.com/", "Mã mẫu.")
        ]
        conn.executemany("""
            INSERT INTO coupons
            (platform,title,code,discount,min_order,expires_at,link,description,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, [x + (datetime.now().strftime("%Y-%m-%d %H:%M"),) for x in sample])
        conn.commit()
    conn.close()


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/")
def home():
    platform = request.args.get("platform", "all")
    keyword = request.args.get("q", "").strip()

    conn = get_db()
    sql = "SELECT * FROM coupons WHERE active = 1"
    params = []

    if platform != "all":
        sql += " AND platform = ?"
        params.append(platform)

    if keyword:
        sql += " AND (title LIKE ? OR code LIKE ? OR description LIKE ?)"
        like = f"%{keyword}%"
        params.extend([like, like, like])

    sql += " ORDER BY id DESC"
    coupons = conn.execute(sql, params).fetchall()
    conn.close()

    return render_template("index.html", coupons=coupons, platform=platform, keyword=keyword)


@app.route("/copy/<code>")
def copy_code(code):
    return {"code": code}


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if username == ADMIN_USER and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        flash("Sai tài khoản hoặc mật khẩu.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def admin():
    conn = get_db()
    coupons = conn.execute("SELECT * FROM coupons ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin.html", coupons=coupons)


@app.route("/admin/add", methods=["GET", "POST"])
@admin_required
def add_coupon():
    if request.method == "POST":
        data = [
            request.form.get("platform", ""),
            request.form.get("title", ""),
            request.form.get("code", "").upper(),
            request.form.get("discount", ""),
            request.form.get("min_order", ""),
            request.form.get("expires_at", ""),
            request.form.get("link", ""),
            request.form.get("description", ""),
            1,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ]
        conn = get_db()
        conn.execute("""
            INSERT INTO coupons
            (platform,title,code,discount,min_order,expires_at,link,description,active,created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, data)
        conn.commit()
        conn.close()
        flash("Đã thêm mã giảm giá.", "success")
        return redirect(url_for("admin"))

    return render_template("coupon_form.html", coupon=None, action="Thêm mã")


@app.route("/admin/edit/<int:coupon_id>", methods=["GET", "POST"])
@admin_required
def edit_coupon(coupon_id):
    conn = get_db()
    coupon = conn.execute("SELECT * FROM coupons WHERE id = ?", (coupon_id,)).fetchone()

    if not coupon:
        conn.close()
        return "Không tìm thấy mã.", 404

    if request.method == "POST":
        data = [
            request.form.get("platform", ""),
            request.form.get("title", ""),
            request.form.get("code", "").upper(),
            request.form.get("discount", ""),
            request.form.get("min_order", ""),
            request.form.get("expires_at", ""),
            request.form.get("link", ""),
            request.form.get("description", ""),
            request.form.get("active") == "1",
            coupon_id
        ]
        conn.execute("""
            UPDATE coupons SET
            platform=?, title=?, code=?, discount=?, min_order=?,
            expires_at=?, link=?, description=?, active=?
            WHERE id=?
        """, data)
        conn.commit()
        conn.close()
        flash("Đã cập nhật mã.", "success")
        return redirect(url_for("admin"))

    conn.close()
    return render_template("coupon_form.html", coupon=coupon, action="Sửa mã")


@app.route("/admin/delete/<int:coupon_id>", methods=["POST"])
@admin_required
def delete_coupon(coupon_id):
    conn = get_db()
    conn.execute("DELETE FROM coupons WHERE id = ?", (coupon_id,))
    conn.commit()
    conn.close()
    flash("Đã xóa mã.", "success")
    return redirect(url_for("admin"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
