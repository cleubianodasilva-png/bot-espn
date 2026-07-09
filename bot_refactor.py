import os
import json
import requests
import time
from datetime import datetime, timezone, timedelta

# Configurações de API (Secrets)
TELEGRAM_TOKEN = os.getenv("TG_TOKEN", "")
CHAT_ID = os.getenv("TG_GROUP_ID", "")
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
BZZOIRO_TOKEN = os.getenv("BZZOIRO_TOKEN", "")

print("🚀 [DEBUG] Iniciando execução do Robô Elite...")
try:
    print(f"⏰ [DEBUG] Hora atual: {datetime.now(timezone.utc)}")
except Exception as e:
    print(f"❌ Erro ao imprimir hora: {e}")

def send_telegram(message, chat_id=CHAT_ID):
    if not TELEGRAM_TOKEN or not chat_id: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def check_status_command():
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        res = requests.get(url, timeout=10).json()
        if not res.get("ok"): return
        agora = time.time()
        for up in res.get("result", []):
            msg = up.get("message", {})
            text = msg.get("text", "")
            cid = str(msg.get("chat", {}).get("id", ""))
            msg_ts = msg.get("date", 0)
            if text in ["/radar", "/relatorio"] and (agora - msg_ts < 600):
                if text == "/radar":
                    send_telegram("🛰️ *Radar Ativo:* Robô monitorando jogos.", cid)
                elif text == "/relatorio":
                    send_telegram("📊 *Relatório:* Gerando dados...", cid)
    except Exception as e:
        print(f"Erro comandos: {e}")

def run():
    print("🛠️ Executando varredura principal...")
    check_status_command()
    print("✅ Varredura concluída.")

if __name__ == '__main__':
    run()
