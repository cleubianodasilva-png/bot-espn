
import os, requests, json
from datetime import datetime

TELEGRAM_TOKEN = os.environ.get("TG_TOKEN", "")
CHAT_ID = os.environ.get("TG_GROUP_ID", "")

def send_telegram(text, botoes=True):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    if botoes:
        payload["reply_markup"] = json.dumps({
            "inline_keyboard": [[
                {"text": "🟣 BET365 🟣", "url": "https://www.bet365.com"},
                {"text": "🔵 PARIPESA 🔵", "url": "https://www.paripesa.com"}
            ]]
        })
    requests.post(url, json=payload)

def send_examples():
    sep = "━━━━━━━━━━━━━━━━━━━━"
    
    mercados = [
        ("⛳️🔥<b>ESCANTEIO LIMITE HT</b>🔥⛳️", "Mais de 8.5 Cantos", "8", "5/6"),
        ("⚽️🔥<b>OVER GOL INTERVALO</b>🔥⚽️", "Mais de 0.5 Gols HT", "-", "4/6"),
        ("⚽️🔥<b>OVER GOL PARTIDA</b>🔥⚽️", "Mais de 2.5 Gols FT", "-", "5/6"),
        ("⚽️🔥<b>AMBAS MARCAM</b>🔥⚽️", "Sim (Ambas Marcam)", "-", "6/6"),
        ("⛳️🔥<b>ESCANTEIO LIMITE FT</b>🔥⛳️", "Mais de 12.5 Cantos", "12", "5/6")
    ]
    
    for titulo, entrada, cantos, crit in mercados:
        msg = (
            f"{sep}\n{titulo}\n"
            f"⚽️ Placar: <b>1 - 1</b>\n"
            f"🌏 Liga: <b>Premier League</b>\n"
            f"📡 <b>Liverpool</b> x <b>Chelsea</b>\n"
            f"⏰️ Minuto: <b>37</b>\n{sep}\n"
            f"📊 <b>Análise ao Vivo da Entrada:</b>\n"
            f"🎯 Chutes no Gol: <b>3 - 2</b>\n"
            f"🚀 Chutes Fora: <b>4 - 2</b>\n"
            f"🔥 Ataques Perigosos: <b>45 - 32</b>\n"
            f"📈 Posse de Bola: <b>52% - 48%</b>\n"
            f"⛳ Escanteios: <b>5 - 3</b>\n"
            f"💰 Odd Mínima Recomendada: <b>1.70</b>\n{sep}\n"
        )
        if "ESCANTEIO" in titulo:
            msg += f"⛳️ Escanteios Atuais: <b>{cantos}</b>\n"
        
        msg += f"📌 Entrada: <b>{entrada}</b>\n✅ Critérios: <b>{crit}</b>\n{sep}\n⚠️Jogue com responsabilidade⚠️"
        send_telegram(msg)

if __name__ == "__main__":
    send_examples()
