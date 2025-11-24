from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import sqlite3
import json

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "sessions.db"


# ------------------
# DB INIT
# ------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            history TEXT
        )
    """)
    conn.commit()
    conn.close()


def load_history(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT history FROM sessions WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return []


def save_history(user_id, history):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO sessions (user_id, history)
        VALUES (?, ?)
    """, (user_id, json.dumps(history)))
    conn.commit()
    conn.close()


SYSTEM_PROMPT = """
Ты — AI-помощник компании «Дом Солнца». 
Ты запоминаешь, о каком объекте говорил клиент, регион, платежи, имя.
Ты не повторяешь вопросы, если данные уже есть.
Твой стиль: тёплый, уверенный, экспертный.
"""


# ------------------
# CHAT ENDPOINT
# ------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    # ---- ВАЖНО: защита от отсутствующих полей ----
    user_id = str(data.get("user_id", "anonymous"))
    user_message = data.get("message", "")

    # Загружаем историю
    history = load_history(user_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    reply = response.choices[0].message.content

    # Сохраняем новую историю
    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})
    save_history(user_id, history)

    return jsonify({"reply": reply})


@app.route("/")
def status():
    return "OK"


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
