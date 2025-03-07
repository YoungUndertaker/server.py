from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()

def get_db_connection():
    """Функция для создания нового соединения с базой данных."""
    conn = sqlite3.connect("database.db", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            code TEXT
        )
    """)
    conn.commit()
    return conn

@app.post("/send_code/")
def send_code(phone: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO users (phone, code) VALUES (?, ?)", (phone, "1234"))
            conn.commit()
        return {"message": "Код отправлен"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_code/")
def get_code(phone: str):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT code FROM users WHERE phone = ?", (phone,))
            row = cursor.fetchone()
        if row:
            return {"code": row[0]}
        else:
            raise HTTPException(status_code=404, detail="Код не найден")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
