from fastapi import FastAPI, HTTPException
import sqlite3
import random

app = FastAPI()

# Создание базы данных
conn = sqlite3.connect("acronix.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT UNIQUE,
    email TEXT UNIQUE,
    code TEXT
)
""")
conn.commit()


def generate_code():
    """Генерация 6-значного кода"""
    return str(random.randint(100000, 999999))


@app.post("/send_code/")
def send_code(phone: str = None, email: str = None):
    """Отправка кода на телефон или email"""
    if not phone and not email:
        raise HTTPException(status_code=400, detail="Нужно указать номер или email")

    code = generate_code()

    if phone:
        cursor.execute("INSERT OR REPLACE INTO users (phone, code) VALUES (?, ?)", (phone, code))
    elif email:
        cursor.execute("INSERT OR REPLACE INTO users (email, code) VALUES (?, ?)", (email, code))

    conn.commit()
    return {"message": "Код отправлен", "code": code}  # Тут нужно прикрутить отправку


@app.post("/verify_code/")
def verify_code(phone: str = None, email: str = None, code: str = None):
    """Проверка введенного кода"""
    if not code:
        raise HTTPException(status_code=400, detail="Введите код")

    if phone:
        cursor.execute("SELECT code FROM users WHERE phone = ?", (phone,))
    elif email:
        cursor.execute("SELECT code FROM users WHERE email = ?", (email,))
    else:
        raise HTTPException(status_code=400, detail="Введите номер или email")

    result = cursor.fetchone()
    if result and result[0] == code:
        return {"message": "Код верный", "status": "success"}
    else:
        raise HTTPException(status_code=400, detail="Код неверный")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
