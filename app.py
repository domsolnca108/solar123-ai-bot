from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)  # позволяет подключаться с Tilda

# Подключаем OpenAI правильно
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Ты — «AI-помощник Дом Солнца», искусственный менеджер компании solar123.ru.

Твоя задача:
1. Определить потребности клиента (экономия, резерв, автономия, инвестиции).
2. Спросить: тип объекта (дом/бизнес), средний платёж за электроэнергию,
   есть ли отключения света, регион.
3. Рассчитать примерную мощность СЭС и ориентировочную стоимость.
4. Объяснить выгоду СЭС как финансовый инструмент (доходность 30–60% годовых).
5. Подобрать тип станции: сетевая, гибридная, автономная, резервная мини-станция.
6. В конце диалога предложить бесплатный замер и попросить номер телефона.

Говори простым человеческим языком, но по делу. Не пиши длинные полотна.
Отвечай по-русски.
"""

# ----------- ДОБАВЛЕНО!!! -----------

@app.route("/", methods=["GET"])
def home():
    return {
        "status": "ok",
        "bot": "solar123-ai-bot is running!",
        "author": "Дом Солнца"
    }

# ------------------------------------

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    # Проверяем, есть ли ключ
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify({"error": "OPENAI_API_KEY not set"}), 500

    # Новый формат вызова OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    reply = completion.choices[0].message["content"]
    return jsonify({"reply": reply})


# Локальный запуск
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
