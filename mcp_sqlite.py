# mcp_sqlite.py

"""
mcp.py
SQLite 기반 MCP 서버 모듈 (CRUD + 충돌 체크)
"""

import sqlite3

# ---------------------------
# DB 초기화
# ---------------------------
DB_PATH = "scheduler.db"
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# 테이블 생성 (없으면 새로 만듦)
cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    date TEXT,
    time TEXT,
    participants TEXT
)
""")
conn.commit()


# ---------------------------
# CRUD 구현
# ---------------------------

def call_mcp_create_event(event: dict):
    cursor.execute(
        "INSERT INTO events (title, date, time, participants) VALUES (?, ?, ?, ?)",
        (
            event.get("title"),
            event.get("date"),
            event.get("time"),
            ",".join(event.get("participants", [])) if event.get("participants") else ""
        )
    )
    conn.commit()
    return {"status": "success"}


def call_mcp_read_events(query: dict):
    date = query.get("date")
    if not date:
        return {"events": []}

    cursor.execute("SELECT title, date, time, participants FROM events WHERE date=?", (date,))
    rows = cursor.fetchall()
    return {
        "events": [
            {
                "title": r[0],
                "date": r[1],
                "time": r[2],
                "participants": r[3].split(",") if r[3] else []
            }
            for r in rows
        ]
    }


def call_mcp_update_event(event: dict):
    # title + date + time을 기준으로 업데이트 예시
    cursor.execute(
        "UPDATE events SET participants=? WHERE title=? AND date=? AND time=?",
        (
            ",".join(event.get("participants", [])),
            event.get("title"),
            event.get("date"),
            event.get("time"),
        )
    )
    conn.commit()
    return {"status": "updated"}


def call_mcp_delete_event(event: dict):
    cursor.execute(
        "DELETE FROM events WHERE title=? AND date=? AND time=?",
        (
            event.get("title"),
            event.get("date"),
            event.get("time"),
        )
    )
    conn.commit()
    return {"status": "deleted"}


def call_mcp_check_conflict(event: dict):
    """
    같은 date + time에 이미 일정이 있는지 확인
    """
    cursor.execute(
        "SELECT title, date, time, participants FROM events WHERE date=? AND time=?",
        (event.get("date"), event.get("time"))
    )
    row = cursor.fetchone()

    if row:
        return {
            "conflict": True,
            "existing_event": {
                "title": row[0],
                "date": row[1],
                "time": row[2],
                "participants": row[3].split(",") if row[3] else []
            }
        }
    return {"conflict": False}
