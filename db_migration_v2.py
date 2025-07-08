import sqlite3
import os
from datetime import datetime

def migrate():
    db_path = "tickets.db"
    if not os.path.exists(db_path):
        print("❌ 找不到 tickets.db，請先建立原始資料庫！")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 新增 movies 資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            poster TEXT,
            duration INTEGER,
            allowed_screens TEXT
        )
    ''')
    print("✅ movies 資料表已建立/存在")

    # 2. 新增 showtimes 資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')
    print("✅ showtimes 資料表已建立/存在")

    # 3. 新增 blacklist 資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            reason TEXT,
            created_at TEXT
        )
    ''')
    print("✅ blacklist 資料表已建立/存在")

    # 4. tickets 表新增 showtime_id 欄位（如尚未存在）
    cursor.execute("PRAGMA table_info(tickets)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'showtime_id' not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN showtime_id INTEGER")
        print("✅ tickets 表已新增 showtime_id 欄位")
    else:
        print("✅ tickets 表已包含 showtime_id 欄位")

    # 檢查 tickets 表是否已有 seat_no 欄位
    if 'seat_no' not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN seat_no TEXT")
        print('✅ 已新增 seat_no 欄位到 tickets 表')
    else:
        print('ℹ️ tickets 表已包含 seat_no 欄位')

    # 檢查 tickets 表是否已有 owner_email 欄位
    if 'owner_email' not in columns:
        cursor.execute("ALTER TABLE tickets ADD COLUMN owner_email TEXT")
        print('✅ 已新增 owner_email 欄位到 tickets 表')
    else:
        print('ℹ️ tickets 表已包含 owner_email 欄位')

    # 檢查 movies 表是否已有 duration 欄位
    cursor.execute("PRAGMA table_info(movies)")
    movie_columns = [col[1] for col in cursor.fetchall()]
    if 'duration' not in movie_columns:
        cursor.execute("ALTER TABLE movies ADD COLUMN duration INTEGER")
        print('✅ 已新增 duration 欄位到 movies 表')
    else:
        print('ℹ️ movies 表已包含 duration 欄位')

    if 'allowed_screens' not in movie_columns:
        cursor.execute("ALTER TABLE movies ADD COLUMN allowed_screens TEXT")
        print('✅ 已新增 allowed_screens 欄位到 movies 表')
    else:
        print('ℹ️ movies 表已包含 allowed_screens 欄位')

    print('座位編號規則：5排10位（A1~A10, B1~B10, ... E1~E10）')

    conn.commit()
    conn.close()
    print("🎉 資料庫結構升級完成！")

if __name__ == "__main__":
    print("🔧 開始資料庫結構升級...")
    migrate()
    print("✨ 升級結束！") 