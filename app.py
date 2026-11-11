
import os
import logging
import requests
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")

if not BOT_TOKEN:
    raise RuntimeError("Configure a variável BOT_TOKEN no Render.")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    response = requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=15
    )
    response.raise_for_status()


@app.get("/")
def home():
    return "Casino AI Mega Wheel está online!"


@app.post("/webhook")
def webhook():
    if not WEBHOOK_SECRET:
        return "Webhook não configurado", 503

    received_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )
    if received_secret != WEBHOOK_SECRET:
        return "Não autorizado", 401

    update = request.get_json(silent=True) or {}
    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "").strip().lower()

    if not chat_id:
        return jsonify(ok=True)

    if text in ["/start", "/start@casino_ai_mega_wheel_bot"]:
        send_message(
            chat_id,
            "🎡 Casino AI Mega Wheel conectado!\n\n"
            "Use /status para verificar o bot e /ajuda "
            "para ver os comandos."
        )
    elif text == "/status":
        send_message(chat_id, "🟢 Bot online e conectado ao Telegram.")
    elif text == "/ajuda":
        send_message(
            chat_id,
            "Comandos disponíveis:\n"
            "/start - iniciar\n"
            "/status - verificar conexão\n"
            "/ajuda - mostrar comandos\n\n"
            "A leitura automática da roleta ainda será configurada."
        )
    else:
        send_message(
            chat_id,
            "Não reconheci esse comando. Envie /ajuda."
        )

    return jsonify(ok=True)


def configure_webhook():
    if not APP_URL or not WEBHOOK_SECRET:
        logging.warning("APP_URL ou WEBHOOK_SECRET ainda não configurado.")
        return

    response = requests.post(
        f"{TELEGRAM_API}/setWebhook",
        json={
            "url": f"{APP_URL.rstrip('/')}/webhook",
            "secret_token": WEBHOOK_SECRET
        },
        timeout=20
    )
    logging.info("Configuração do webhook: %s", response.text)


configure_webhook()
