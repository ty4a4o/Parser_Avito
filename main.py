from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sqlite3
from passlib.context import CryptContext
from datetime import datetime, timedelta

app = FastAPI()
DB_NAME = "backend.db"
# Контекст для работы с паролями
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- МОДЕЛИ ---
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# Модели для заказов и выполнения оставляем прежними из прошлого шага
class OrderCreate(BaseModel):
    user_id: int
    title: str
    target_url: str
    views_count: int

class TaskComplete(BaseModel):
    user_id: int
    order_id: int

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # ТАБЛИЦА ПОЛЬЗОВАТЕЛЕЙ (ОБНОВЛЕНА)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT UNIQUE, 
                  email TEXT UNIQUE, 
                  password_hash TEXT,
                  balance INTEGER DEFAULT 1000)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, title TEXT, 
                  target_url TEXT, views_limit INTEGER, views_done INTEGER DEFAULT 0)''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS task_logs 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, order_id INTEGER, completed_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- ЭНДПОИНТЫ АВТОРИЗАЦИИ ---

@app.post("/register")
def register(user: UserRegister):
    conn = get_db_connection()
    hashed_password = pwd_context.hash(user.password)
    try:
        conn.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                     (user.username, user.email, hashed_password))
        conn.commit()
        return {"status": "success", "message": "Регистрация завершена"}
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "Логин или Email уже заняты"}
    finally:
        conn.close()

@app.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    db_user = conn.execute("SELECT * FROM users WHERE username = ?", (user.username,)).fetchone()
    conn.close()
    
    if not db_user or not pwd_context.verify(user.password, db_user["password_hash"]):
        return {"status": "error", "message": "Неверный логин или пароль"}
    
    res = dict(db_user)
    # Удаляем хеш пароля перед отправкой клиенту
    del res["password_hash"]
    res["points"] = res["balance"]
    return {"status": "success", "user": res}

@app.post("/orders/create")
def create_order(order: OrderCreate):
    conn = get_db_connection()
    try:
        price = order.views_count * 5
        user = conn.execute("SELECT balance FROM users WHERE id = ?", (order.user_id,)).fetchone()
        
        if not user or user["balance"] < price:
            return {"status": "error", "message": f"Недостаточно баллов (нужно {price})"}

        conn.execute("BEGIN")
        conn.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (price, order.user_id))
        conn.execute("""INSERT INTO orders (owner_id, title, target_url, views_limit) 
                     VALUES (?, ?, ?, ?)""", (order.user_id, order.title, order.target_url, order.views_count))
        conn.commit()
        return {"status": "success", "message": f"Заказ создан! Списано {price} баллов."}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@app.get("/tasks/available/{user_id}")
def get_available_tasks(user_id: int):
    conn = get_db_connection()
    cutoff = datetime.now() - timedelta(hours=24)
    query = """
        SELECT id, title FROM orders 
        WHERE owner_id != ? 
        AND views_done < views_limit
        AND id NOT IN (SELECT order_id FROM task_logs WHERE user_id = ? AND completed_at > ?)
    """
    tasks = conn.execute(query, (user_id, user_id, cutoff)).fetchall()
    conn.close()
    return [dict(t) for t in tasks]

@app.post("/tasks/complete")
def complete_task(data: TaskComplete):
    conn = get_db_connection()
    try:
        cutoff = datetime.now() - timedelta(hours=24)
        # Проверка таймера
        check = conn.execute("SELECT 1 FROM task_logs WHERE user_id=? AND order_id=? AND completed_at > ?", 
                             (data.user_id, data.order_id, cutoff)).fetchone()
        if check: return {"status": "error", "message": "Задание уже выполнено (кулдаун 24ч)"}

        conn.execute("BEGIN")
        conn.execute("UPDATE users SET balance = balance + 5 WHERE id = ?", (data.user_id,))
        conn.execute("UPDATE orders SET views_done = views_done + 1 WHERE id = ?", (data.order_id,))
        conn.execute("INSERT INTO task_logs (user_id, order_id, completed_at) VALUES (?, ?, ?)", 
                     (data.user_id, data.order_id, datetime.now()))
        conn.commit()
        return {"status": "success", "message": "+5 баллов начислено!"}
    except Exception as e:
        conn.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@app.get("/orders/all")
def get_all_orders():
    conn = get_db_connection()
    orders = conn.execute("SELECT id, title, target_url, views_done, views_limit FROM orders").fetchall()
    conn.close()
    return [dict(o) for o in orders]
