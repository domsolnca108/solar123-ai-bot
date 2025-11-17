from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Берём ключ из переменной окружения на Render
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    # локальный запуск, Render сам подставит свой порт
    app.run(host="0.0.0.0", port=10000)
