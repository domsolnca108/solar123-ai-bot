from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
Ты — «AI-помощник Дом Солнца», искусственный менеджер компании solar123.ru.

Твоя задача:
1. Определить потребности клиента (экономия, резерв, автономия, инвестиции).
2. Спросить: тип объекта (дом/бизнес), средний платёж за электроэнергию,
   есть ли отключения света, регион.
3. Рассчитать примерную мощность СЭС и ориентировочную стоимость.
4. Объяснить выгоду.
5. Подобрать тип станции.
6. В конце — предложить бесплатный замер и попросить телефон.

Говори простым языком. Отвечай по-русски.
"""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
    )

    reply = response.choices[0].message.content
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
