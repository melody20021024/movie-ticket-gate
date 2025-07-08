import sqlite3
from datetime import datetime, timedelta
import random

def get_movies():
    conn = sqlite3.connect('tickets.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies')
    movies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return movies

def insert_showtime(movie_id, start_time, screen, seats=50):
    showtime_id = f's{random.randint(1000,9999)}{random.randint(1000,9999)}'
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO showtimes (id, movie_id, start_time, screen, seats) VALUES (?, ?, ?, ?, ?)',
                   (showtime_id, movie_id, start_time, screen, seats))
    conn.commit()
    conn.close()

def auto_schedule():
    movies = get_movies()
    # 取得明天日期
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    # 先清除明天的 showtimes（避免重複）
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM showtimes WHERE date(start_time)=?", (tomorrow.isoformat(),))
    conn.commit()
    conn.close()
    # 每個影廳獨立排片
    screens = [1, 2, 3]
    for screen in screens:
        # 找出允許排在此廳的電影
        allowed_movies = [m for m in movies if m.get('allowed_screens') and str(screen) in str(m['allowed_screens']).split(',')]
        if not allowed_movies:
            continue
        t = datetime.combine(tomorrow, datetime.strptime('09:00', '%H:%M').time())
        while True:
            # 輪流排 allowed_movies
            for m in allowed_movies:
                duration = m.get('duration') or 120
                start_time = t.strftime('%Y-%m-%d %H:%M')
                insert_showtime(m['id'], start_time, screen, seats=50)
                # 下一場次 = 本片時長 + 10(清場) + 5(下場入場)
                t = t + timedelta(minutes=duration + 10 + 5)
                # 若超過晚上23:00就不再排
                if t.hour >= 23:
                    break
            if t.hour >= 23:
                break
    print('✅ 明天自動排片完成！')

if __name__ == '__main__':
    auto_schedule() 