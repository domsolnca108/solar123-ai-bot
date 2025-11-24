from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import sqlite3
import json

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_PATH = "sessions.db"


# ------------------------------------
# База данных
# ------------------------------------
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
    else:
        return None


def save_history(user_id, history):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO sessions (user_id, history)
        VALUES (?, ?)
    """, (user_id, json.dumps(history, ensure_ascii=False)))
    conn.commit()
    conn.close()


# ------------------------------------
# SYSTEM PROMPT
# ------------------------------------
SYSTEM_PROMPT = """
Ты — «AI-помощник Дом Солнца», менеджер компании Solar123.ru.

Твоя миссия:
1. Помнить клиента — объект, регион, платеж, имя, пожелания.
2. Не задавать повторных вопросов, если данные уже есть.
3. Помогать: считать мощность, стоимость, выгоду и окупаемость.
4. Давать рекомендации по типу станции.
5. Завершать предложением бесплатного расчёта инженера.
Отвечай дружелюбно, спокойно, понятным языком.
"""


# ------------------------------------
# Основной чат с памятью
# ------------------------------------
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "user_id обязателен"}), 400

    # Загружаем историю
    history = load_history(user_id)
    if not history:
        history = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Добавляем сообщение клиента
    history.append({"role": "user", "content": user_message})

    # Отправляем запрос к OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        temperature=0.7
    )

    reply = response.choices[0].message.content

    # Сохраняем ответ бота в историю
    history.append({"role": "assistant", "content": reply})

    # Обновляем базу данных
    save_history(user_id, history)

    return jsonify({"reply": reply})


# ------------------------------------
# Статус API
# ------------------------------------
@app.route("/", methods=["GET"])
def status():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
