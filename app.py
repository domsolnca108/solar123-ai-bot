from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # включаем CORS, чтобы Tilda могла отправлять запросы

# Берём ключ из переменной окружения на Render
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
Ты — «AI-помощник Дом Солнца», искусственный менеджер компании solar123.ru.

Твоя задача:
1. Определить потребности клиента.
2. Узнать: дом/бизнес, платеж за свет, отключения, регион.
3. Рассчитать мощность СЭС.
4. Объяснить выгоду как инвестицию.
5. Подобрать тип станции.
6. Спросить телефон для замера.

Отвечай коротко, по делу и по-русски.
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
