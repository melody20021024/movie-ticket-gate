import sqlite3

# 預設電影資料
movies = [
    {
        "id": "m001",
        "title": "沙丘2",
        "description": "保羅亞崔迪聯手弗瑞曼人，展開復仇之路，改變宇宙命運。",
        "poster": "static/Dune.jpg",
        "duration": 155,
        "allowed_screens": "1,2,3"
    },
    {
        "id": "m002",
        "title": "哥吉拉大戰金剛",
        "description": "兩大巨獸史詩對決，地球命運岌岌可危。",
        "poster": "static/Godzilla.jpg",
        "duration": 113,
        "allowed_screens": "1,2,3"
    },
    {
        "id": "m003",
        "title": "Barbie",
        "description": "芭比娃娃勇闖現實世界，展開奇幻冒險。",
        "poster": "static/Barbie.jpg",
        "duration": 114,
        "allowed_screens": "1,2,3"
    }
]

def init_movies():
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    for m in movies:
        # 檢查是否已存在
        cursor.execute("SELECT 1 FROM movies WHERE id = ?", (m["id"],))
        if cursor.fetchone():
            print(f"電影 {m['title']} 已存在，略過。")
            continue
        cursor.execute(
            "INSERT INTO movies (id, title, description, poster, duration, allowed_screens) VALUES (?, ?, ?, ?, ?, ?)",
            (m["id"], m["title"], m["description"], m["poster"], m["duration"], m["allowed_screens"])
        )
        print(f"已新增電影：{m['title']}")
    conn.commit()
    conn.close()
    print("✅ 電影資料初始化完成！")

if __name__ == "__main__":
    init_movies() 