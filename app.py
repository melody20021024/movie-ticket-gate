from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from datetime import datetime
import qrcode
import random
import os
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # ✅ 不要把中文變 Unicode 編碼
app.secret_key = 'your-secret-key-here'  # 用於session加密

# 管理員密碼設定
ADMIN_PASSWORD = "admin123"  # 你可以修改這個密碼

def get_ticket_from_db(ticket_id):
    """從SQLite資料庫中獲取票券資訊"""
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, movie, seat, verified FROM tickets WHERE id = ?", (ticket_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "name": result[0],
            "movie": result[1],
            "seat": result[2],
            "verified": bool(result[3]) if result[3] is not None else False
        }
    return None

def send_ticket_email(email, name, ticket_id, movie, seat, qr_path):
    """寄送票券Email"""
    try:
        # Email配置（可以根據需要修改）
        SMTP_SERVER = "smtp.gmail.com"  # Gmail SMTP伺服器
        SMTP_PORT = 587  # TLS端口
        SENDER_EMAIL = "your-email@gmail.com"  # 發送者Email
        SENDER_PASSWORD = "your-app-password"  # Gmail應用程式密碼
        
        # 建立Email內容
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email
        msg['Subject'] = f'🎫 您的電影票券 - {movie}'
        
        # 更豐富的Email正文
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .ticket-info {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .ticket-info ul {{ list-style: none; padding: 0; }}
                .ticket-info li {{ padding: 8px 0; border-bottom: 1px solid #eee; }}
                .ticket-info li:last-child {{ border-bottom: none; }}
                .qr-section {{ text-align: center; margin: 20px 0; }}
                .footer {{ background: #f8f9fa; padding: 15px; text-align: center; color: #666; font-size: 14px; }}
                .highlight {{ color: #667eea; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 虛擬影城</h1>
                <h2>電影票券確認</h2>
            </div>
            
            <div class="content">
                <p>親愛的 <span class="highlight">{name}</span>，</p>
                <p>感謝您選擇虛擬影城！您的電影票券已成功購買並確認。</p>
                
                <div class="ticket-info">
                    <h3>🎫 票券詳細資訊</h3>
                    <ul>
                        <li><strong>票券編號：</strong> <span class="highlight">{ticket_id}</span></li>
                        <li><strong>電影名稱：</strong> {movie}</li>
                        <li><strong>座位號碼：</strong> {seat}</li>
                        <li><strong>持票人：</strong> {name}</li>
                        <li><strong>購買時間：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                    </ul>
                </div>
                
                <div class="qr-section">
                    <h3>📱 入場QR碼</h3>
                    <p>請在電影院入口處出示此QR碼進行驗票</p>
                    <img src="cid:qr_code" alt="QR Code" style="width: 200px; height: 200px;">
                </div>
                
                <h3>📋 重要提醒</h3>
                <ul>
                    <li>請提前15分鐘到達電影院</li>
                    <li>請攜帶有效身份證件</li>
                    <li>QR碼僅限使用一次</li>
                    <li>請勿將QR碼分享給他人</li>
                </ul>
                
                <p>祝您觀影愉快！🎭</p>
            </div>
            
            <div class="footer">
                <p>虛擬影城團隊</p>
                <p>如有問題，請聯繫客服：support@virtualcinema.com</p>
                <p>此為系統自動發送，請勿回覆此郵件</p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # 添加QR碼圖片
        with open(os.path.join("static", qr_path), 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<qr_code>')
            img.add_header('Content-Disposition', 'inline', filename=f'ticket_{ticket_id}.png')
            msg.attach(img)
        
        # 發送Email（模擬模式）
        print(f"📧 Email已發送給 {email}")
        print(f"   票券編號：{ticket_id}")
        print(f"   電影：{movie}")
        print(f"   📨 收件人：{email}")
        print(f"   🕒 發送時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 實際發送Email（取消註解並設定正確的SMTP資訊）
        """
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✅ Email成功發送到 {email}")
        except Exception as smtp_error:
            print(f"❌ SMTP發送失敗: {smtp_error}")
        """
        
    except Exception as e:
        print(f"❌ 發送Email時發生錯誤: {e}")
        print(f"   錯誤詳情: {str(e)}")

def mark_ticket_verified(ticket_id):
    """標記票券為已驗證"""
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    
    # 檢查是否有verified欄位
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'verified' in columns:
        cursor.execute("UPDATE tickets SET verified = 1 WHERE id = ?", (ticket_id,))
        print(f"✅ 票券 {ticket_id} 已標記為驗證")
    else:
        print(f"⚠️ 資料庫中沒有verified欄位，無法標記驗證狀態")
    
    conn.commit()
    conn.close()

def get_showtimes_by_movie(movie_id):
    return db_get_showtimes_by_movie(movie_id)

def get_showtime_by_id(showtime_id):
    return db_get_showtime_by_id(showtime_id)

def get_showtime_remain(showtime_id):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE showtime_id=?", (showtime_id,))
    sold = cursor.fetchone()[0]
    conn.close()
    showtime = get_showtime_by_id(showtime_id)
    total = showtime["seats"] if showtime else 0
    return total - sold

def get_all_movies():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    movies = {row["id"]: dict(row) for row in cursor.fetchall()}
    conn.close()
    return movies

@app.route("/")
def home():
    return redirect("/cinema")

@app.route("/cinema")
def cinema_home():
    movies = get_all_movies()
    return render_template("index.html", movies=movies, get_showtimes_by_movie=get_showtimes_by_movie, get_showtime_remain=get_showtime_remain)

@app.route("/buy/<movie_id>", methods=["GET", "POST"])
def buy_ticket(movie_id):
    movies = get_all_movies()
    movie = movies.get(movie_id)
    if not movie:
        flash("找不到該電影！")
        return redirect(url_for("index"))
    all_showtimes = get_showtimes_by_movie(movie_id)
    selected_showtime = request.args.get("showtime_id")
    # 產生座位編號
    rows = ['A', 'B', 'C', 'D', 'E']
    seats_per_row = 10
    seat_map = [f"{row}{num}" for row in rows for num in range(1, seats_per_row+1)]
    sold_seats = []
    if selected_showtime:
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()
        cursor.execute("SELECT seat_no FROM tickets WHERE showtime_id=?", (selected_showtime,))
        sold_seats = [r[0] for r in cursor.fetchall() if r[0]]
        conn.close()
    if request.method == "GET":
        return render_template("buy_form.html", movie=movie, showtimes=all_showtimes, selected_showtime=selected_showtime, seat_map=seat_map, sold_seats=sold_seats)
    # POST 表單送出：建立多張票券
    name = request.form.get("name")
    email = request.form.get("email")
    form_showtime_id = request.form.get("showtime_id") or selected_showtime
    seat_nos = request.form.getlist("seat_no")
    num_people = int(request.form.get("num_people", 1))
    if len(seat_nos) != num_people:
        flash(f"購買人數與選位數量不符，請選擇 {num_people} 個座位！")
        return redirect(url_for("buy_ticket", movie_id=movie_id, showtime_id=form_showtime_id))
    if not seat_nos or len(seat_nos) == 0:
        flash("請選擇至少一個座位！")
        return redirect(url_for("buy_ticket", movie_id=movie_id, showtime_id=form_showtime_id))
    if len(seat_nos) > 10:
        flash("一次最多只能購買10張票！")
        return redirect(url_for("buy_ticket", movie_id=movie_id, showtime_id=form_showtime_id))
    # 防呆：檢查是否有座位已被購買
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    for seat_no in seat_nos:
        cursor.execute("SELECT 1 FROM tickets WHERE showtime_id=? AND seat_no=?", (form_showtime_id, seat_no))
        if cursor.fetchone():
            conn.close()
            flash(f"座位 {seat_no} 已被購買，請重新選擇！")
            return redirect(url_for("buy_ticket", movie_id=movie_id, showtime_id=form_showtime_id))
    showtime = get_showtime_by_id(form_showtime_id)
    showtime_info = f"{showtime['start_time']}｜影廳{showtime['screen']}" if showtime else ""
    ticket_ids = []
    for seat_no in seat_nos:
        ticket_id = str(random.randint(100000, 999999))
        cursor.execute("INSERT INTO tickets (id, name, movie, seat, email, showtime_id, seat_no, owner_email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (ticket_id, name, movie["title"], seat_no, email, form_showtime_id, seat_no, email))
        ticket_ids.append(ticket_id)
        # 產生QR碼
        qr_path = f"{ticket_id}.png"
        qr_img = qrcode.make(ticket_id)
        full_path = os.path.join("static", qr_path)
        with open(full_path, 'wb') as f:
            qr_img.save(f)
        # 寄送Email票券資訊（如果有email）
        if email:
            send_ticket_email(email, name, ticket_id, movie["title"], seat_no, qr_path)
    conn.commit()
    conn.close()
    # 預覽頁顯示所有票券
    return render_template("preview_ticket.html", ticket_ids=ticket_ids, movie=movie["title"], seats=seat_nos, name=name, showtime=showtime_info)

@app.route("/preview_ticket/<ticket_id>")
def preview_ticket(ticket_id):
    """預覽票券QR碼"""
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, movie, seat 
        FROM tickets 
        WHERE id = ?
    """, (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    
    if ticket:
        name, movie, seat = ticket
        qr_path = f"{ticket_id}.png"
        return render_template("preview_ticket.html",
                               ticket_id=ticket_id,
                               movie=movie,
                               seat=seat,
                               name=name,
                               qr_path=qr_path)
    else:
        return "❌ 票券不存在", 404

@app.route("/verify_ticket/<ticket_id>")
def verify_page(ticket_id):
    # ✅ 修復：從SQLite資料庫讀取票券資訊
    ticket_info = get_ticket_from_db(ticket_id)
    if ticket_info:
        # 標記票券為已驗證
        mark_ticket_verified(ticket_id)
        ticket_info["verified"] = True
        return render_template("result_success.html", info=ticket_info)
    else:
        return render_template("result_fail.html")

@app.route("/verify", methods=["POST"])
def verify_ticket():
    # ✅ 修復：處理request.json可能為None的問題
    data = request.get_json()
    if not data:
        return jsonify({
            "status": "fail",
            "message": "❌ 無效請求格式"
        }), 400
    
    ticket_id = data.get("ticket_id")
    if not ticket_id:
        return jsonify({
            "status": "fail",
            "message": "❌ 缺少票券編號"
        }), 400

    # ✅ 修復：從SQLite資料庫讀取票券資訊
    ticket_info = get_ticket_from_db(ticket_id)
    if ticket_info:
        # 標記票券為已驗證
        mark_ticket_verified(ticket_id)
        ticket_info["verified"] = True
        
        return jsonify({
            "status": "success",
            "info": ticket_info
        })
    else:
        return jsonify({
            "status": "fail",
            "message": "❌ 無效票券，請洽櫃台"
        }), 404

@app.route("/scan/<ticket_id>")
def scan_ticket(ticket_id):
    # ✅ 修復：從SQLite資料庫讀取票券資訊
    ticket_info = get_ticket_from_db(ticket_id)
    if ticket_info:
        return render_template("result_success.html", info=ticket_info)
    else:
        return render_template("result_fail.html")

@app.route("/my_tickets/")
def my_tickets():
    name = request.args.get("name")
    email = request.args.get("email")
    if not name and not email:
        return render_template("my_tickets.html", tickets=None, name=None, email=None)
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if email:
        cursor.execute("SELECT * FROM tickets WHERE owner_email=? ORDER BY id DESC", (email,))
    else:
        cursor.execute("SELECT * FROM tickets WHERE name=? ORDER BY id DESC", (name,))
    tickets = cursor.fetchall()
    conn.close()
    return render_template("my_tickets.html", tickets=tickets, name=name, email=email)

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """管理員登入頁面"""
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="❌ 密碼錯誤")
    
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    """管理員登出"""
    session.pop('admin_logged_in', None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_dashboard():
    """管理員後台 - 顯示所有票券記錄"""
    # 檢查是否已登入
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    
    # 檢查資料表結構
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # 根據實際欄位動態構建查詢
    if 'email' in columns and 'verified' in columns:
        cursor.execute("""
            SELECT id, name, movie, seat, email, created_at, verified 
            FROM tickets 
            ORDER BY created_at DESC
        """)
        tickets = cursor.fetchall()
        
        # 格式化票券資料
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                "id": ticket[0],
                "name": ticket[1],
                "movie": ticket[2],
                "seat": ticket[3],
                "email": ticket[4] if ticket[4] else "未提供",
                "created_at": ticket[5],
                "verified": bool(ticket[6]) if ticket[6] is not None else False
            })
    elif 'email' in columns:
        cursor.execute("""
            SELECT id, name, movie, seat, email, created_at
            FROM tickets 
            ORDER BY created_at DESC
        """)
        tickets = cursor.fetchall()
        
        # 格式化票券資料
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                "id": ticket[0],
                "name": ticket[1],
                "movie": ticket[2],
                "seat": ticket[3],
                "email": ticket[4] if ticket[4] else "未提供",
                "created_at": ticket[5],
                "verified": False
            })
    else:
        cursor.execute("""
            SELECT id, name, movie, seat, created_at
            FROM tickets 
            ORDER BY created_at DESC
        """)
        tickets = cursor.fetchall()
        
        # 格式化票券資料
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                "id": ticket[0],
                "name": ticket[1],
                "movie": ticket[2],
                "seat": ticket[3],
                "email": "未提供",
                "created_at": ticket[4],
                "verified": False
            })
    
    conn.close()
    
    # 統計資訊
    total_tickets = len(ticket_list)
    verified_tickets = sum(1 for t in ticket_list if t["verified"])
    unverified_tickets = total_tickets - verified_tickets
    
    return render_template("admin_dashboard.html", 
                         tickets=ticket_list,
                         total_tickets=total_tickets,
                         verified_tickets=verified_tickets,
                         unverified_tickets=unverified_tickets)

@app.route("/admin/verify/<ticket_id>")
def admin_verify_ticket(ticket_id):
    """管理員手動驗票"""
    # 檢查是否已登入
    if not session.get('admin_logged_in'):
        return redirect(url_for("admin_login"))
    
    mark_ticket_verified(ticket_id)
    return redirect(url_for("admin_dashboard"))

@app.route("/movie/<movie_id>")
def movie_detail(movie_id):
    movies = get_all_movies()
    movie = movies.get(movie_id)
    if not movie:
        flash("找不到該電影！")
        return redirect(url_for("index"))
    return render_template("movie_detail.html", movie=movie, movie_id=movie_id, get_showtimes_by_movie=get_showtimes_by_movie, get_showtime_remain=get_showtime_remain)

@app.route("/admin/showtimes")
def admin_showtimes():
    movies = get_all_movies()
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    showtimes_list = []
    for s in db_get_all_showtimes():
        movie = movies.get(s["movie_id"])
        showtimes_list.append({
            "id": s["id"],
            "movie_title": movie["title"] if movie else "(已刪除)",
            "start_time": s["start_time"],
            "screen": s["screen"],
            "seats": s["seats"]
        })
    return render_template("admin_showtimes.html", showtimes=showtimes_list, get_showtime_remain=get_showtime_remain)

@app.route("/admin/showtimes/new", methods=["GET", "POST"])
def admin_add_showtime():
    movies = get_all_movies()
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    if request.method == "GET":
        return render_template("admin_add_showtime.html", movies=movies)
    movie_id = request.form.get("movie_id")
    start_time = request.form.get("start_time")
    screen_val = request.form.get("screen")
    seats_val = request.form.get("seats")
    screen = int(screen_val) if screen_val is not None and screen_val != '' else 1
    seats = int(seats_val) if seats_val is not None and seats_val != '' else 50
    new_id = f"s{random.randint(1000,9999)}"
    db_add_showtime({
        "id": new_id,
        "movie_id": movie_id,
        "start_time": start_time,
        "screen": screen,
        "seats": seats
    })
    flash("新增場次成功！")
    return redirect(url_for("admin_showtimes"))

@app.route("/admin/showtimes/delete/<showtime_id>")
def admin_delete_showtime(showtime_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    db_delete_showtime(showtime_id)
    flash("場次已刪除！")
    return redirect(url_for("admin_showtimes"))

@app.route("/admin/showtimes/edit/<showtime_id>", methods=["GET", "POST"])
def admin_edit_showtime(showtime_id):
    movies = get_all_movies()
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    showtime = db_get_showtime_by_id(showtime_id)
    if not showtime:
        flash("找不到該場次！")
        return redirect(url_for("admin_showtimes"))
    if request.method == "GET":
        return render_template("admin_edit_showtime.html", showtime=showtime, movies=movies)
    movie_id = request.form.get("movie_id")
    start_time = request.form.get("start_time")
    screen_val = request.form.get("screen")
    seats_val = request.form.get("seats")
    screen = int(screen_val) if screen_val is not None and screen_val != '' else showtime["screen"]
    seats = int(seats_val) if seats_val is not None and seats_val != '' else showtime["seats"]
    db_update_showtime(showtime_id, {
        "movie_id": movie_id,
        "start_time": start_time,
        "screen": screen,
        "seats": seats
    })
    flash("場次已更新！")
    return redirect(url_for("admin_showtimes"))

@app.route("/transfer_ticket/<ticket_id>", methods=["POST"])
def transfer_ticket(ticket_id):
    new_email = request.form.get("new_email")
    new_name = request.form.get("new_name")
    owner_email = request.args.get("email") or request.form.get("owner_email")
    owner_name = request.args.get("name") or request.form.get("owner_name")
    if not new_email or not new_name:
        return "請輸入受讓人姓名與Email！", 400
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("SELECT owner_email, name FROM tickets WHERE id=?", (ticket_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "找不到該票券！", 404
    # 允許用 email 或 name 驗證 owner
    if (owner_email and row[0] != owner_email) and (owner_name and row[1] != owner_name):
        conn.close()
        return "您無權分票此票券！", 403
    cursor.execute("UPDATE tickets SET owner_email=?, name=? WHERE id=?", (new_email, new_name, ticket_id))
    conn.commit()
    conn.close()
    return "分票成功"  # AJAX用，純文字

# --- 資料庫場次操作 ---
def db_get_all_showtimes():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM showtimes ORDER BY start_time ASC")
    result = cursor.fetchall()
    conn.close()
    return [dict(r) for r in result]

def db_get_showtime_by_id(showtime_id):
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM showtimes WHERE id = ?", (showtime_id,))
    r = cursor.fetchone()
    conn.close()
    return dict(r) if r else None

def db_get_showtimes_by_movie(movie_id):
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM showtimes WHERE movie_id = ? ORDER BY start_time ASC", (movie_id,))
    result = cursor.fetchall()
    conn.close()
    return [dict(r) for r in result]

def db_add_showtime(s):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO showtimes (id, movie_id, start_time, screen, seats) VALUES (?, ?, ?, ?, ?)",
                   (s["id"], s["movie_id"], s["start_time"], s["screen"], s["seats"]))
    conn.commit()
    conn.close()

def db_update_showtime(showtime_id, s):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE showtimes SET movie_id=?, start_time=?, screen=?, seats=? WHERE id=?",
                   (s["movie_id"], s["start_time"], s["screen"], s["seats"], showtime_id))
    conn.commit()
    conn.close()

def db_delete_showtime(showtime_id):
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM showtimes WHERE id=?", (showtime_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    app.run(debug=True, port=5001)


