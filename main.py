import os
import requests
import time
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

PUMP_API = "https://pump.fun/api/tokens"
BONK_API = "https://bonk.fun/api/tokens"
RUGCHECK_API = "https://api.rugcheck.xyz/tokens/"

seen_tokens = set()

def check_token_safety(ca):
    try:
        response = requests.get(f"{RUGCHECK_API}{ca}")
        data = response.json()
        return data.get("safety", {}).get("verdict", "UNKNOWN")
    except Exception:
        return "UNKNOWN"

def fetch_tokens(api_url):
    try:
        response = requests.get(api_url)
        return response.json().get("tokens", [])
    except Exception:
        return []

def notify_token(platform, token):
    ca = token.get("address")
    name = token.get("name")
    symbol = token.get("symbol")
    price = round(float(token.get("priceUsd", 0)), 5)
    mc = round(float(token.get("marketCapUsd", 0)))
    liq = round(float(token.get("liquidityUsd", 0)))

    safety = check_token_safety(ca)
    if safety != "GOOD":
        return

    if mc > 7000 and liq > 500:
        msg = (
            f"🚀 [{platform.upper()}] عملة جديدة!\n\n"
            f"👤 الاسم: {name} (${symbol})\n"
            f"📈 السعر: ${price}\n"
            f"🏦 القيمة السوقية: ${mc}\n"
            f"💧 السيولة: ${liq}\n"
            f"🛡️ الأمان: {safety}\n"
            f"🔗 الرابط: https://{platform}.fun/token/{ca}\n\n"
            f"#{symbol} #Crypto #Solana #Memecoin"
        )
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def monitor():
    while True:
        for platform, url in [("pump", PUMP_API), ("bonk", BONK_API)]:
            tokens = fetch_tokens(url)
            for token in tokens:
                ca = token.get("address")
                if ca and ca not in seen_tokens:
                    seen_tokens.add(ca)
                    notify_token(platform, token)
        time.sleep(20)

if __name__ == "__main__":
    print("Monitoring pump.fun and bonk.fun...")
    monitor()
