

def analisar_e_disparar(game, stats, p, m, sh, sa, odd_h, odd_a, sent_vistos, cfg=None):
    # IDENTIFICAÇÃO DO FAVORITO PRÉ-LIVE (OBRIGATÓRIO)
    try:
        oh = float(odd_h) if odd_h else 3.0
        oa = float(odd_a) if odd_a else 3.0
        fav_side = "h" if oh < oa else "a"
    except:
        fav_side = "h"

    # DADOS DO FAVORITO
    fav_gols = sh if fav_side == "h" else sa
    adv_gols = sa if fav_side == "h" else sh
    red_fav = stats.get(f"red_cards_{fav_side}", 0)
    
    # Carrega config pra obter os ranges
    merc = (cfg or {}).get("mercados", {})
    M_HT   = merc.get("over_05_ht", {})
    M_OG   = merc.get("over_gol_partida", {})
    M_BTTS = merc.get("ambas_marcam", {})
    M_OFT  = merc.get("over_15_ft", {})
    M_CHT  = merc.get("escanteio_ht", {})
    M_CFT  = merc.get("escanteio_ft", {})
    
    # MERCADOS
    
    # 1. OVER GOL INTERVALO (HT)
    hti, htf = M_HT.get("minuto_inicio", 15), M_HT.get("minuto_fim", 27)
    if M_HT.get("ativo", True) and p == M_HT.get("periodo", 1) and hti <= m <= htf:
        if sh == 0 and sa == 0 and red_fav == 0:
            return "HT", "Over 0.5 Gols HT"

    # 2. OVER GOL PARTIDA (FT)
    ogi, ogf = M_OG.get("minuto_inicio", 55), M_OG.get("minuto_fim", 75)
    if M_OG.get("ativo", True) and p == M_OG.get("periodo", 2) and ogi <= m <= ogf:
        if (fav_gols <= adv_gols) and (adv_gols - fav_gols <= 1) and red_fav == 0:
            total_gols = sh + sa
            return "OVERGOAL", f"Mais de {total_gols + 0.5} Gols"

    # 3. AMBAS MARCAM (BTTS)
    bi, bf = M_BTTS.get("minuto_inicio", 55), M_BTTS.get("minuto_fim", 75)
    if M_BTTS.get("ativo", True) and p == M_BTTS.get("periodo", 2) and bi <= m <= bf:
        if (sh + sa == 1) and (fav_gols == 0 and adv_gols == 1) and red_fav == 0:
            return "BTTS", "Ambas Marcam"

    # 4. OVER 1.5 GOLS PARTIDA
    oi, of_ = M_OFT.get("minuto_inicio", 55), M_OFT.get("minuto_fim", 75)
    if M_OFT.get("ativo", True) and p == M_OFT.get("periodo", 2) and oi <= m <= of_:
        if (sh + sa == 1) and (fav_gols == 0 and adv_gols == 1) and red_fav == 0:
            return "OFT", "Mais de 1.5 Gols Partida"

    # 5. ESCANTEIO LIMITE HT
    chi, chf = M_CHT.get("minuto_inicio", 32), M_CHT.get("minuto_fim", 38)
    if M_CHT.get("ativo", True) and p == M_CHT.get("periodo", 1) and chi <= m <= chf:
        if (fav_gols <= adv_gols) and (adv_gols - fav_gols <= 1) and red_fav == 0:
            return "CORNER_HT", "Escanteio Limite HT"

    # 6. ESCANTEIO LIMITE FT
    cfi, cff = M_CFT.get("minuto_inicio", 82), M_CFT.get("minuto_fim", 88)
    if M_CFT.get("ativo", True) and p == M_CFT.get("periodo", 2) and cfi <= m <= cff:
        if (fav_gols <= adv_gols) and (adv_gols - fav_gols <= 1) and red_fav == 0:
            return "CORNER_FT", "Escanteio Limite FT"

    return (None, None, None), None

def gerar_layout_relatorio(greens, reds, data_str):
    sep = "━━━━━━━━━━━━━━━━━━━━"
    total = greens + reds
    taxa = (greens / total * 100) if total > 0 else 0.0
    return (
        f"{sep}\n"
        f"<b>📊 RELATÓRIO DIÁRIO — {data_str}</b>\n"
        f"{sep}\n"
        f"✅ GREEN: <b>{greens}</b>\n"
        f"🔴 RED: <b>{reds}</b>\n"
        f"📈 TOTAL DE ENTRADAS: <b>{total}</b>\n"
        f"🎯 ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n"
        f"{sep}\n"
        f"⚠️👆Resultados do dia👆⚠️"
    )

def gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos):
    sep = "\u2501" * 20
    total = greens + reds
    taxa = (greens / total * 100) if total > 0 else 0.0
    msg = f"{sep}\n"
    msg += f"<b>\U0001f4ca RELAT\u00d3RIO MENSAL \u2014 {mes_nome}</b>\n"
    msg += f"{sep}\n"
    msg += f"\u2705 GREEN: <b>{greens}</b>\n"
    msg += f"\U0001f534 RED: <b>{reds}</b>\n"
    msg += f"\U0001f4c8 TOTAL DE ENTRADAS: <b>{total}</b>\n"
    msg += f"\U0001f3af ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n"
    msg += f"{sep}\n"
    msg += f"\U0001f4c5 Dias com entradas: <b>{dias_ativos}</b>\n"
    msg += "\u26a0\ufe0f\U0001f446Resultados do m\u00eas\U0001f446\u26a0\ufe0f"
    return msg

def gerar_layout_radar(jogos_ao_vivo, jogos_na_janela):
    sep = "━━━━━━━━━━━━━━━━━━━━"
    texto_jan = ""
    for j in jogos_na_janela:
        h = j.get("home","") or getattr(j,"home","")
        a = j.get("away","") or getattr(j,"away","")
        m = j.get("minuto","") or getattr(j,"minuto","")
        sh = j.get("sh",0) or getattr(j,"sh",0)
        sa = j.get("sa",0) or getattr(j,"sa",0)
        liga = j.get("liga","") or getattr(j,"liga","")
        texto_jan += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
    if not texto_jan:
        texto_jan = "Nenhum jogo na janela no momento."
    corpo = (
        f"{sep}\n"
        f"📡 RADAR — JOGOS AO VIVO\n"
        f"{sep}\n"
        f"🔴 Jogos na Janela:\n"
        f"{texto_jan}"
        f"{sep}\n"
        f"🟢 Ao Vivo: <b>{len(jogos_ao_vivo)}</b>"
    )
    return corpo
import requests

def obter_nome_liga(game, fonte):
    # apifootball: game['league']['name']
    # SokkerPro: game['league_name']
    liga = "Liga Não Identificada"
    
    if fonte == "apifootball":
        liga = game.get('league', {}).get('name', "Liga Não Identificada")
    elif fonte == "sokkerpro":
        # SokkerPro retorna camelCase: leagueName
        liga = game.get('leagueName') or game.get('league_name', "Liga Não Identificada")
    
    # Se ainda estiver vazio, busca em campos genéricos que as APIs costumam usar
    if liga == "Liga Não Identificada":
        liga = game.get('leagueName') or game.get('league_name') or game.get('competition_name') or game.get('league') or "Liga Não Identificada"
        
    return liga
# ═══════════════════════════════════════════════════════════════════════════════
# BOT MÁQUINA DE GREENS VIP - ZAPIA - VERSÃO ELITE 100% AUTOMÁTICA
# ═══════════════════════════════════════════════════════════════════════════════
import os, json, requests, time
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
from datetime import datetime, timezone, timedelta
import hashlib, re, unicodedata

# ─── Normalização de nomes de times (acentos, abreviações, prefixos) ────────────
def norm_nome_time(nome):
    """Remove acentos, expande abreviações e limpa prefixos/sufixos de nome de time."""
    n = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower().strip()
    # Remove prefixos comuns: msk, hnk, nk, fk, sk, fc, etc
    n = re.sub(r'\b(msk|hnk|nk|fk|sk|fc|ac|ec|se|cf)\b', '', n)
    # Expande abreviações comuns da apifootball
    n = n.replace('u.', 'universitatea').replace('dyn.', 'dynamo').replace('s.n.', '').replace('c.s.', '')
    # Remove siglas de estados e outros prefixos genéricos
    n = re.sub(r'\b(rj|sp|mg|rs|pr|sc|ba|pe|ce|go|mt|ms|df|es|rn|pb|al|se|pi|ma|pa|am|ro|rr|ap|to|fr|ac|ec|se|cf)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()

# ─── Caminhos e Fuso ───────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
SENT_FILE       = os.path.join(BASE_DIR, "sent_live_signals.json")
SINAIS_FILE     = os.path.join(BASE_DIR, "sinais_pendentes.json")
RESULTADO_FILE  = os.path.join(BASE_DIR, "resultados.json")
PERFORMANCE_FILE= os.path.join(BASE_DIR, "performance.json")
LAST_UPDATE_FILE= os.path.join(BASE_DIR, "last_update.json")
BRT             = timezone(timedelta(hours=-3))

# ─── Credenciais ───────────────────────────────────────────────────────────────
TELEGRAM_TOKEN  = os.getenv("TG_TOKEN", "")
TG_TOKEN = TELEGRAM_TOKEN
CHAT_IDS = [os.environ.get("TG_GROUP_ID", "")]
CHAT_ID = CHAT_IDS[0] if CHAT_IDS else ""  # BOOT IA INTELIGENTE (Zapia)

# apifootball — API PRINCIPAL para dados de jogos
API_FOOTBALL_KEYS = [
    os.getenv("APIFOOTBALL_KEY"),   # Chave Mestre protegida
]
API_FOOTBALL_URL = "https://apiv3.apifootball.com"



# RapidAPI (fallback de lista)
RAPIDAPI_URL     = "https://free-api-live-football-data.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  os.getenv("APIFOOTBALL_KEY", ""),
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}



# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"



# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"



# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"

# ═══════════════+++
# TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg_data, reply_to=None, marca=None, home="", away="", odd_b365_val=None, odd_bano_val=None):
    """Envia mensagem formatada com botões inline."""
    if isinstance(msg_data, tuple):
        text, keyboard = msg_data
    else:
        text = msg_data
        keyboard = None

    url_send = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if keyboard:
            payload["reply_markup"] = json.dumps(keyboard)
            
        try:
            r = requests.post(url_send, json=payload, timeout=10)
            res = r.json()
            if res.get("ok"):
                last_mid = res.get("result", {}).get("message_id")
        except:
            pass
    return last_mid

# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVOS LOCAIS
# ═══════════════════════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GH_PAT", "")
GITHUB_REPO  = os.environ.get("GITHUB_REPOSITORY", "cleubianodasilva-png/maquina-de-greens-vip")
SENT_API_PATH        = "sent_live_signals.json"
RESULTADO_API_PATH   = "resultados.json"
PERFORMANCE_API_PATH = "performance.json"

def _crit(mercado, geral, key, default):
    """Pega valor de critério: mercado > geral > default."""
    c = mercado.get("criterios", {})
    if key in c:
        return c[key]
    if key in geral:
        return geral[key]
    return default

def _github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG DINÂMICA — carrega parâmetros do config.json (GitHub + local)
# ═══════════════════════════════════════════════════════════════════════════════
def _load_config():
    """
    Carrega config.json do GitHub (fonte de verdade) + local como fallback.
    Retorna dict com defaults se nada disponível.
    """
    default = {
        "geral": {"appm_min_por_time": 0.7, "appm_min_total": 1.4, "media_gols_minima": 2.2},
        "mercados": {}
    }
    try:
        if GITHUB_TOKEN and GITHUB_REPO:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CONFIG_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                import base64 as _b64
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                # Salva localmente
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"[CONFIG] Carregado do GitHub: {len(data.get('mercados', {}))} mercados")
                return data
    except Exception as e:
        print(f"[CONFIG] Erro GitHub load: {e}")
    # Fallback local
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                print(f"[CONFIG] Carregado local: {len(data.get('mercados', {}))} mercados")
                return data
        except: pass
    print("[CONFIG] Usando defaults")
    return default

def load_sent():
    """Carrega sent do GitHub (fonte de verdade) + arquivo local como fallback."""
    # Tenta GitHub API primeiro
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SENT_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                import base64 as _b64
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                sent = set(data)
                # Limpa chaves antigas (> 2 dias) para não crescer infinito
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                ontem = (datetime.now(BRT) - timedelta(days=1)).strftime('%Y%m%d')
                sent = {k for k in sent if hoje in k or ontem in k}
                # Salva localmente também
                with open(SENT_FILE, 'w') as f: json.dump(list(sent), f)
                print(f"[SENT] Carregado do GitHub: {len(sent)} chaves")
                return sent
        except Exception as e:
            print(f"[SENT] Erro GitHub load: {e}")
    # Fallback: arquivo local
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r') as f: return set(json.load(f))
        except: pass
    return set()

def save_sent(sent):
    """Salva sent localmente E no GitHub (fonte de verdade)."""
    with open(SENT_FILE, 'w') as f: json.dump(list(sent), f)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SENT_API_PATH}"
            # Pega SHA atual
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(list(sent)).encode()).decode()
            payload = {"message": "state: atualiza sent [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[SENT] Salvo no GitHub: {len(sent)} chaves")
            else:
                print(f"[SENT] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[SENT] Erro GitHub save: {e}")

def _load_sinais_github():
    """Carrega sinais_pendentes.json do GitHub."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/sinais_pendentes.json"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                return json.loads(_b64.b64decode(r.json()["content"]).decode())
        except Exception as e:
            print(f"[SINAIS] Erro load GitHub: {e}")
    if os.path.exists(SINAIS_FILE):
        try:
            with open(SINAIS_FILE, 'r') as f: return json.load(f)
        except: pass
    return []

def _save_sinais_github(sinais):
    """Salva sinais_pendentes.json no GitHub E localmente."""
    import base64 as _b64
    with open(SINAIS_FILE, 'w') as f: json.dump(sinais, f)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/sinais_pendentes.json"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(sinais).encode()).decode()
            payload = {"message": "state: atualiza sinais_pendentes [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[SINAIS] Salvo no GitHub: {len(sinais)} pendentes")
            else:
                print(f"[SINAIS] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[SINAIS] Erro save GitHub: {e}")

def registrar_sinal(fid, mercado, home, away, message_id, extra_val=None):
    sinais = _load_sinais_github()
    sinais.append({
        "fixture_id": fid, "mercado": mercado,
        "home": home, "away": away,
        "message_id": message_id, "extra_val": extra_val,
        "timestamp": datetime.now(BRT).isoformat()
    })
    _save_sinais_github(sinais)

def _load_resultados_github():
    """Carrega resultados.json do GitHub. Retorna lista de registros."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTADO_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"[RESULTADO] Erro load GitHub: {e}")
    # Fallback local
    if os.path.exists(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return []

def _save_resultados_github(registros):
    """Salva resultados.json no GitHub E localmente."""
    import base64 as _b64
    with open(RESULTADO_FILE, 'w') as f: json.dump(registros, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTADO_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(registros, indent=2).encode()).decode()
            payload = {"message": "state: atualiza resultados [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[RESULTADO] Salvo no GitHub: {len(registros)} registros")
            else:
                print(f"[RESULTADO] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[RESULTADO] Erro save GitHub: {e}")

def salvar_resultado(resultado, mercado=None):
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    registros = _load_resultados_github()
    registros.append({
        "data": hoje, "resultado": resultado,
        "mercado": mercado,
        "timestamp": datetime.now(BRT).isoformat()
    })
    _save_resultados_github(registros)


def get_relatorio_mensal():
    hoje = datetime.now(BRT)
    mes_str = hoje.strftime("%Y-%m")
    greens, reds = 0, 0
    registros = _load_resultados_github()
    dias_ativos = set()
    for r in registros:
        data_reg = r.get("data", "")
        if data_reg.startswith(mes_str):
            dias_ativos.add(data_reg)
            if r.get("resultado") == "green": greens += 1
            else: reds += 1
    return greens, reds, len(dias_ativos)

def get_relatorio_hoje():
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    greens, reds = 0, 0
    registros = _load_resultados_github()
    for r in registros:
        if r.get("data") == hoje:
            if r.get("resultado") == "green": greens += 1
            else: reds += 1
    return greens, reds


def enviar_relatorio_mensal():
    hoje = datetime.now(BRT)
    meses_pt = ["Janeiro","Fevereiro","Mar\u00e7o","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes_nome = f"{meses_pt[hoje.month-1]}/{hoje.year}"
    greens, reds, dias_ativos = get_relatorio_mensal()
    msg = gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos)
    return msg

def enviar_relatorio_diario():
    hoje_key = f"relatorio_{datetime.now(BRT).strftime('%Y-%m-%d')}"
    hoje = datetime.now(BRT).strftime("%d/%m/%Y")
    greens, reds = get_relatorio_hoje()
    msg = gerar_layout_relatorio(greens, reds, hoje)
    if send_telegram(msg):
        sent_ctrl.add(hoje_key)
        save_sent(sent_ctrl)
        print(f"[Relatório] Enviado ({hoje_key})")

# ─── Performance por Mercado ────────────────────────────────────────────────────
MAPA_MERCADO = {
    "HT": "⚽️🔥OVER GOL INTERVALO🔥⚽️",
    "BTTS": "⚽🔥AMBAS MARCAM🔥⚽️",
    "OFT": "⚽🔥OVER 1.5 GOLS FT🔥⚽️",
    "OVERGOAL": "⚽🔥OVER GOL PARTIDA🔥⚽️",
    "CORNER_HT": "🚩🔥ESCANTEIO ÁSIAT/LMT HT🔥🚩",
    "CORNER_FT": "🚩🔥ESCANTEIO ÁSIAT/LMT FT🔥🚩"
}

def _load_performance_github():
    """Carrega performance.json do GitHub. Retorna dict {mercado: {green, red, total}}."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PERFORMANCE_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[PERFORMANCE] Erro load GitHub: {e}")
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {}

def _save_performance_github(perf):
    """Salva performance.json no GitHub E localmente."""
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump(perf, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PERFORMANCE_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(perf, indent=2).encode()).decode()
            payload = {"message": "state: atualiza performance [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[PERFORMANCE] Salvo no GitHub: {sum(v.get('total',0) for v in perf.values())} registros")
            else:
                print(f"[PERFORMANCE] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[PERFORMANCE] Erro save GitHub: {e}")

def registrar_performance(mercado, resultado):
    """Registra resultado de um mercado específico no performance.json."""
    perf = _load_performance_github()
    if mercado not in perf:
        perf[mercado] = {"green": 0, "red": 0, "total": 0}
    perf[mercado]["total"] += 1
    if resultado == "green":
        perf[mercado]["green"] += 1
    else:
        perf[mercado]["red"] += 1
    _save_performance_github(perf)
    total = perf[mercado]["total"]
    greens = perf[mercado]["green"]
    pct = greens / total * 100 if total > 0 else 0
    print(f"[PERFORMANCE] {MAPA_MERCADO.get(mercado, mercado)}: {resultado} ({greens}/{total} = {pct:.1f}%)")

def get_performance():
    """Retorna dict com performance e % por mercado, e validação 70%/1000."""
    perf = _load_performance_github()
    resultado = {}
    for cod, nome in MAPA_MERCADO.items():
        p = perf.get(cod, {"green": 0, "red": 0, "total": 0})
        total = p["total"]
        greens = p["green"]
        reds = p["red"]
        pct = (greens / total * 100) if total > 0 else 0
        valido = total >= 1000 and pct >= 70
        resultado[cod] = {
            "nome": nome, "green": greens, "red": reds,
            "total": total, "pct": pct, "valido": valido
        }
    return resultado

def gerar_layout_performance():
    """Gera layout do relatório de performance por mercado."""
    dados = get_performance()
    sep = "━" * 20
    blocos = []
    for cod, info in dados.items():
        nome = info["nome"]
        g = info["green"]
        r = info["red"]
        t = info["total"]
        pct = info["pct"]
        blocos.append(
            f"<b>{nome}</b>\n"
            f"   ⏳ Total: {t} | 🟢 {g} | 🔴 {r}\n"
            f"   🎯 Acerto: {pct:.1f}%"
        )
    total_g = sum(d["green"] for d in dados.values())
    total_r = sum(d["red"] for d in dados.values())
    total_t = total_g + total_r
    total_pct = (total_g / total_t * 100) if total_t > 0 else 0

    msg = (
        f"{sep}\n"
        f"📊<b>RELATÓRIO DE PERFORMANCE</b>📊\n"
        f"{sep}\n"
        f"{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}"
        f"{sep}\n"
        f"📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n"
        f"      | 🟢 {total_g} | 🔴 {total_r} | {total_pct:.1f}%|\n"
        f"{sep}\n"
        f"Regras de Validação:\n"
        f"✅ Mínimo 1000 entradas + ≥70%\n"
        f"{sep}"
    )
    return msg

def enviar_relatorio_performance():
    """Gera o relatório de performance. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_performance()

def get_performance_24h():
    """Retorna performance por mercado nas últimas 24h a partir dos resultados salvos."""
    registros = _load_resultados_github()
    agora = datetime.now(BRT)
    corte = agora - timedelta(hours=24)
    
    perf = {}
    for cod, nome in MAPA_MERCADO.items():
        perf[cod] = {"nome": nome, "green": 0, "red": 0, "total": 0}
    
    for r in registros:
        ts_str = r.get("timestamp", "")
        mercado = r.get("mercado", "")
        resultado = r.get("resultado", "")
        if not ts_str or not mercado or not resultado:
            continue
        if mercado not in perf:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone(timedelta(hours=-3)))
            if ts < corte:
                continue
        except:
            continue
        perf[mercado]["total"] += 1
        if resultado == "green":
            perf[mercado]["green"] += 1
        else:
            perf[mercado]["red"] += 1
    
    for cod, info in perf.items():
        t = info["total"]
        g = info["green"]
        info["pct"] = (g / t * 100) if t > 0 else 0
    
    return perf

def gerar_layout_mercados24h():
    """Gera layout do relatório de performance por mercado nas últimas 24h."""
    dados = get_performance_24h()
    sep = "━" * 20
    blocos = []
    for cod, info in dados.items():
        nome = info["nome"]
        g = info["green"]
        r = info["red"]
        t = info["total"]
        pct = info["pct"]
        blocos.append(
            f"<b>{nome}</b>\n"
            f"   Total: {t} | 🟢 {g} | 🔴 {r}\n"
            f"   🎯 Acerto: {pct:.1f}%"
        )
    total_g = sum(d["green"] for d in dados.values())
    total_r = sum(d["red"] for d in dados.values())
    total_t = total_g + total_r
    total_pct = (total_g / total_t * 100) if total_t > 0 else 0

    msg = (
        f"{sep}\n"
        f"📊<b>MERCADOS — ÚLTIMAS 24H</b>📊\n"
        f"{sep}\n"
        f"{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}"
        f"{sep}\n"
        f"📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n"
        f"      | 🟢 {total_g} | 🔴 {total_r} | {total_pct:.1f}%|\n"
        f"{sep}"
    )
    return msg

def enviar_relatorio_mercados24h():
    """Gera o relatório de mercados 24h. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_mercados24h()

# ESPN removido — usa apenas SokkerPro


# ═══════════════════════════════════════════════════════════════════════════════
# API 1B — apifootball: jogos ao vivo
# ═══════════════════════════════════════════════════════════════════════════════
def get_jogos_apifootball(fids_apifootball):
    """Busca todos os jogos ao vivo na apifootball."""
    for key in [APIFOOTBALL_COM_KEY]:
        try:
            r = requests.get(
                f"{API_FOOTBALL_URL}/fixtures",
                params={"live": "all"},
                headers={"x-apisports-key": key},
                timeout=15
            )
            rjson = r.json()
            erros = rjson.get("errors", {})
            if erros and (erros.get("requests") or erros.get("access") or erros.get("token")):
                print(f"[apifootball] Chave {key[:8]}... sem acesso: {erros}")
                continue
            fixtures = rjson.get("response", [])
            if not fixtures:
                print(f"[apifootball] Chave {key[:8]}... retornou 0 jogos")
                continue
            jogos = []
            for f in fixtures:
                try:
                    fid    = str(f["fixture"]["id"])
                    # Pula se apifootball já tem
                    if fid in fids_apifootball:
                        continue
                    status = f["fixture"]["status"]
                    state  = status.get("short", "")
                    # Só jogos ao vivo (1H, HT, 2H, ET, P, BT)
                    if state not in ("1H", "HT", "2H", "ET", "P", "BT"):
                        continue
                    minuto = status.get("elapsed", 0) or 0
                    period = 1 if state in ("1H", "HT") or minuto <= 45 else 2
                    home   = f["teams"]["home"]["name"]
                    away   = f["teams"]["away"]["name"]
                    sh     = f["goals"]["home"] or 0
                    sa     = f["goals"]["away"] or 0
                    liga   = f["league"]["name"]
                    jogos.append({
                        "fid": fid, "home": home, "away": away,
                        "sh": sh, "sa": sa, "minuto": minuto,
                        "period": period, "liga": liga, "source": "apifootball"
                    })
                except:
                    continue
            print(f"[apifootball] {len(jogos)} jogos novos (chave {key[:8]}...)")
            return jogos
        except Exception as e:
            print(f"[apifootball] Erro chave {key[:8]}...: {e}")
            continue
    print("[apifootball] Todas as chaves falharam")
    return []


# ═══════════════════════════════════════════════════════════════════════════════
# apifootball: estatísticas de um jogo específico
# ═══════════════════════════════════════════════════════════════════════════════
def get_stats_apifootball_live(fid):
    """Busca stats ao vivo via action=get_statistics da apifootball."""
    try:
        params = {"action": "get_statistics", "match_id": fid, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(fid) not in data:
            return {}
        raw = data[str(fid)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        # Garantir chutes_tot se tivermos chutes_gol mas nao chutes_tot
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        for side in ["h", "a"]:
            for k in ["chutes_tot", "chutes_gol", "red_cards", "ataques", "ataques_perigosos", "posse"]:
                stats.setdefault(f"{k}_{side}", 0)
            stats.setdefault(f"escanteios_{side}", -1)
        print(f"[apifootball Stats] action=get_statistics fid {fid} OK")
        return stats
    except Exception as e:
        print(f"[apifootball Stats] Erro: {e}")
        return {}




def get_stats_apifootball_v3(match_id):
    try:
        params = {"action": "get_statistics", "match_id": match_id, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(match_id) not in data: return {}
        raw = data[str(match_id)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}

def get_stats_sokkerpro(fid_raw, home, away):
    try:
        headers = {}  # SokkerPro
        data = r.json()
        raw_stats = data.get("stats", {})
        stats = {}
        for side, key in [("home", "h"), ("away", "a")]:
            side_data = raw_stats.get(side, {})
            stats[f"chutes_tot_{key}"] = int(side_data.get("total_shots", 0) or 0)
            stats[f"chutes_gol_{key}"] = int(side_data.get("shots_on_target", 0) or 0)
            stats[f"escanteios_{key}"] = int(side_data.get("corner_kicks", 0) or 0)
            cards = side_data.get("cards", {})
            if isinstance(cards, dict):
                stats[f"red_cards_{key}"] = int(cards.get("red", 0) or 0)
        return stats
    except: return {}




def get_jogos_apifootball_v3(fids_existentes):
    try:
        hoje = datetime.now().strftime("%Y-%m-%d")
        params = {"action": "get_events", "match_live": "1", "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=15)
        data = r.json()
        if not isinstance(data, list): return []

        # Busca odds de UMA vez (from=hoje&to=hoje) e indexa por match_id + bookmaker
        odds_idx = {}
        try:
            params_odd = {"action": "get_odds", "from": hoje, "to": hoje, "APIkey": APIFOOTBALL_COM_KEY}
            ro = requests.get(APIFOOTBALL_URL, params=params_odd, timeout=15)
            odds_raw = ro.json()
            if isinstance(odds_raw, list):
                for odd in odds_raw:
                    mid = odd.get("match_id")
                    bk = odd.get("odd_bookmakers", "").lower()
                    if mid and bk and odd.get("odd_1") and odd.get("odd_2"):
                        if mid not in odds_idx:
                            odds_idx[mid] = {}
                        odds_idx[mid][bk] = odd
        except:
            pass
        print(f"[APIF-ODDS] {len(odds_idx)} jogos com odds carregadas")

        jogos = []
        for ev in data:
            status_raw = str(ev.get("match_status", "0") or "0").replace("'","").strip()
            if status_raw.lower() == "finished":
                continue
            fid = "apif_" + str(ev.get("match_id", ""))
            if fid in fids_existentes: continue
            status_digits = __import__('re').findall(r'\d+', status_raw)
            minuto = int(status_digits[0]) if status_digits else 0
            liga_nome = (ev.get("league_name", "") or "").strip()
            country = (ev.get("country_name", "") or "").strip()
            if country and liga_nome and " " + country not in (" " + liga_nome):
                liga_nome = f"{liga_nome} {country}"
            if not liga_nome:
                liga_nome = ev.get("league", "") or ev.get("competition_name", "") or "Liga"

            fid_raw = str(ev.get("match_id", ""))
            odd_h = odd_a = None
            odds_b365 = {}
            odds_bano = {}
            if fid_raw in odds_idx:
                bks = odds_idx[fid_raw]
                # Moneyline odd_h/odd_a: prioridade Bet365 > Betano > qualquer outra
                odd_h = odd_a = None
                for bk_alvo in ("bet365", "betano"):
                    if bk_alvo in bks:
                        oh = bks[bk_alvo].get("odd_1")
                        oa = bks[bk_alvo].get("odd_2")
                        if oh and oa:
                            odd_h = float(oh)
                            odd_a = float(oa)
                            break
                if not (odd_h and odd_a):
                    for bk, od in bks.items():
                        oh = od.get("odd_1")
                        oa = od.get("odd_2")
                        if oh and oa:
                            odd_h = float(oh)
                            odd_a = float(oa)
                            break
                for bk_alvo, dest in [("bet365", odds_b365), ("betano", odds_bano)]:
                    if bk_alvo in bks:
                        entry = bks[bk_alvo]
                        for campo in ("o+0.5","o+1","o+1.5","o+2","o+2.5","bts_yes","bts_no","odd_1","odd_2"):
                            v = entry.get(campo)
                            if v: dest[campo] = float(v)

            jogos.append({
                "fid": fid, "fid_raw": fid_raw,
                "home": ev.get("match_hometeam_name", ""),
                "away": ev.get("match_awayteam_name", ""),
                "sh": int(ev.get("match_hometeam_score", 0) or 0),
                "sa": int(ev.get("match_awayteam_score", 0) or 0),
                "minuto": minuto,
                "liga": liga_nome,
                "period": 2 if minuto >= 45 else 1,
                "source": "apifootball",
                "home_id": str(ev.get("match_hometeam_id", "")),
                "away_id": str(ev.get("match_awayteam_id", "")),
                "odd_h": odd_h,
                "odd_a": odd_a,
                "odds_b365": odds_b365,
                "odds_bano": odds_bano
            })
        print(f"[APIF-v3] {len(jogos)} novos jogos (de {len(data)} totais)")
        return jogos
    except Exception as e:
        print(f"[APIF-v3 ERRO] {e}")
        return []


_CACHED_DATA = None

def _get_data():
    """Busca dados do SokkerPro com cache — UMA chamada HTTP por execução."""
    global _CACHED_DATA
    if _CACHED_DATA is not None:
        return _CACHED_DATA
    try:
        r = requests.get(SOKKERPRO_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        _CACHED_DATA = r.json()
        return _CACHED_DATA
    except Exception as e:
        print(f"[SKP] Erro ao buscar dados: {e}")
        return None

def _get_float(val, default=0.0):
    if not val or str(val).strip() in ('', 'None'): return default
    try: return float(str(val).split('#')[0].strip())
    except: return default

def _get_int(val, default=0):
    if not val or str(val).strip() in ('', 'None'): return default
    try: return int(float(str(val)))
    except: return default

def get_jogos_sokkerpro(fids_existentes):
    data = _get_data()
    if not data: return []
    jogos = []
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                fid = str(fix.get('fixtureId', ''))
                if not fid or fid in fids_existentes: continue
                status = fix.get('status', '')
                minuto = _get_int(fix.get('minute', 0))
                # Mapear status para period numerico
                if status in ('FT', 'PEN'): continue  # ignorar finalizados
                if status == '2nd': period = 2
                elif status == '1st': period = 1
                elif status == 'HT': period = 1
                elif status == 'NS': period = 0
                else: period = 0
                # Só incluir se tiver dados basicos
                if status == 'NS' and not minuto: continue
                jogos.append({
                    "fid": fid,
                    "home": fix.get('localTeamName', 'Home'),
                    "away": fix.get('visitorTeamName', 'Away'),
                    "minuto": minuto or _get_int(fix.get('minutePrimeiroTempo', 0)) or _get_int(fix.get('minuteSegundoTempo', 0)),
                    "period": period,
                    "sh": _get_int(fix.get('scoresLocalTeam', 0)),
                    "sa": _get_int(fix.get('scoresVisitorTeam', 0)),
                    "liga": fix.get('leagueName', 'Liga'),
                    "pais": fix.get('countryName', ''),
                    "source": "sokkerpro"
                })
    except: pass
    return jogos


def get_stats_sokkerpro(fid_raw, home="", away=""):
    data = _get_data()
    if not data: return {}
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    return {
                        "chutes_tot_h": _get_int(fix.get('localShotsTotal', 0)),
                        "chutes_tot_a": _get_int(fix.get('visitorShotsTotal', 0)),
                        "chutes_gol_h": _get_int(fix.get('localShotsOnGoal', 0)),
                        "chutes_gol_a": _get_int(fix.get('visitorShotsOnGoal', 0)),
                        "escanteios_h": _get_int(fix.get('localCorners', 0)),
                        "escanteios_a": _get_int(fix.get('visitorCorners', 0)),
                        "ataques_perigosos_h": _get_int(fix.get('localAttacksDangerousAttacks', 0)),
                        "ataques_perigosos_a": _get_int(fix.get('visitorAttacksDangerousAttacks', 0)),
                        "red_cards_h": _get_int(fix.get('localRedCards', 0)),
                        "red_cards_a": _get_int(fix.get('visitorRedCards', 0)),
                        "medias_home_goal": _get_float(fix.get('medias_home_goal', 0)),
                        "medias_away_goal": _get_float(fix.get('medias_away_goal', 0))
                    }
    except: pass
    return {}


def get_odds_sokkerpro(fid_raw):
    data = _get_data()
    if not data: return (None, None)
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    # XBET_VENCEDOR_HOME/AWAY = odds pré-live (disponível sempre)
                    oh = _get_float(fix.get('XBET_VENCEDOR_HOME'))
                    oa = _get_float(fix.get('XBET_VENCEDOR_AWAY'))
                    if oh > 1 and oa > 1:
                        return (oh, oa)
                    # Fallback: BET365_VENCEDOR_1_LIVE/2_LIVE = odds ao vivo
                    oh = _get_float(fix.get('BET365_VENCEDOR_1_LIVE'))
                    oa = _get_float(fix.get('BET365_VENCEDOR_2_LIVE'))
                    if oh > 1 and oa > 1:
                        return (oh, oa)
                    return (None, None)
    except: pass
    return (None, None)

# --- REPLICANDO FUN\u00c7\u00d5ES DE LAYOUT E L\u00d3GICA ---def get_stats_apifootball_v3(match_id):
    try:
        params = {"action": "get_statistics", "match_id": match_id, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(match_id) not in data: return {}
        raw = data[str(match_id)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}



def get_stats_sokkerpro_by_name(home, away):
    """Fallback: busca stats no SokkerPro pelo nome dos times."""
    try:
        data = _get_data()
        if not data: return {}
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if fix.get('localTeamName', '').lower() == home.lower() and fix.get('visitorTeamName', '').lower() == away.lower():
                    return {
                        "chutes_tot_h": _get_int(fix.get('localShotsTotal', 0)),
                        "chutes_tot_a": _get_int(fix.get('visitorShotsTotal', 0)),
                        "chutes_gol_h": _get_int(fix.get('localShotsOnGoal', 0)),
                        "chutes_gol_a": _get_int(fix.get('visitorShotsOnGoal', 0)),
                        "escanteios_h": _get_int(fix.get('localCorners', 0)),
                        "escanteios_a": _get_int(fix.get('visitorCorners', 0)),
                        "ataques_perigosos_h": _get_int(fix.get('localAttacksDangerousAttacks', 0)),
                        "ataques_perigosos_a": _get_int(fix.get('visitorAttacksDangerousAttacks', 0)),
                        "medias_home_goal": _get_float(fix.get('medias_home_goal', 0)),
                        "medias_away_goal": _get_float(fix.get('medias_away_goal', 0))
                    }
    except: pass
    return {}

def get_stats_apifootball_by_name(home, away):
    """Fallback: busca jogo na apifootball pelo nome dos times e retorna stats."""
    import unicodedata
    def norm(s):
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()
    try:
        r = requests.get(APIFOOTBALL_URL, params={"action": "get_events", "match_live": "1", "APIkey": APIFOOTBALL_COM_KEY}, timeout=15)
        data = r.json()
        if not isinstance(data, list): return {}
        h_busca = norm(home)
        a_busca = norm(away)
        # Procura jogo onde os nomes dos times batem (parcialmente)
        for ev in data:
            h_nome = norm(ev.get("match_hometeam_name", ""))
            a_nome = norm(ev.get("match_awayteam_name", ""))
            if (h_busca in h_nome or h_nome in h_busca) and (a_busca in a_nome or a_nome in a_busca):
                mid = str(ev.get("match_id", ""))
                if mid:
                    print(f"[APIF-NAME] Match por nome: {ev['match_hometeam_name']} x {ev['match_awayteam_name']} → ID {mid}")
                    return get_stats_apifootball_v3(mid)
        # Tenta também ao contrário (home/away invertido)
        for ev in data:
            h_nome = norm(ev.get("match_hometeam_name", ""))
            a_nome = norm(ev.get("match_awayteam_name", ""))
            if (h_busca in a_nome or a_nome in h_busca) and (a_busca in h_nome or h_nome in a_busca):
                mid = str(ev.get("match_id", ""))
                if mid:
                    print(f"[APIF-NAME] Match invertido: {ev['match_hometeam_name']} x {ev['match_awayteam_name']} → ID {mid}")
                    stats = get_stats_apifootball_v3(mid)
                    if stats:
                        # Inverter os lados quando o match for invertido
                        for campo in ["escanteios_h","escanteios_a","chutes_tot_h","chutes_tot_a","chutes_gol_h","chutes_gol_a","red_cards_h","red_cards_a","posse_h","posse_a"]:
                            campo_inv = campo.replace("_h","_x").replace("_a","_h").replace("_x","_a")
                            if campo in stats: stats[campo_inv] = stats.pop(campo)
                    return stats
        return {}
    except: return {}




def _moneyline_to_decimal(ml):
    """Converte moneyline americano para decimal."""
    try:
        ml = float(ml)
        if ml > 0:
            return round(ml / 100 + 1, 3)
        else:
            return round(100 / abs(ml) + 1, 3)
    except:
        return 99.0

def get_favorito_odds(home, away, fid=None, league=None):
    """Retorna ('h'|'a', odd_h, odd_a) baseado na menor odd. Usa apifootball e SokkerPro."""
    # Fallback 1: SokkerPro odds
    if fid:
        try:
            oh, oa = get_odds_sokkerpro(fid)
            if oh and oa and oh > 1 and oa > 1:
                fav = "h" if oh <= oa else "a"
                print(f"[ODDS-SKP] {home} x {away} | Casa:{oh} Fora:{oa} -> Fav:{fav}")
                return (fav, oh, oa)
        except Exception as e:
            print(f"[ODDS-SKP] Erro: {e}")

    # Fallback 3: APIfootball.com odds (quando fid for do apifootball)
    if fid and str(fid).replace("apif_","").isdigit():
        try:
            match_id = str(fid).replace("apif_","")
            r = requests.get("https://apiv3.apifootball.com/",
                             params={"action": "get_odds", "match_id": match_id,
                                     "APIkey": APIFOOTBALL_COM_KEY}, timeout=8)
            odds_data = r.json()
            if isinstance(odds_data, list) and odds_data:
                # Prioridade: Bet365 > Betano > qualquer outra
                odd_ml = None
                for bk_alvo in ("bet365", "betano"):
                    for od in odds_data:
                        if str(od.get("odd_bookmakers", "")).lower() == bk_alvo:
                            odd_ml = od
                            break
                    if odd_ml:
                        break
                if not odd_ml:
                    odd_ml = odds_data[0]
                try:
                    odd_h = float(odd_ml.get("odd_1", 0) or 0)
                    odd_a = float(odd_ml.get("odd_2", 0) or 0)
                    if odd_h > 1 and odd_a > 1:
                        fav = "h" if odd_h <= odd_a else "a"
                        print(f"[ODDS-APFC] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                        return (fav, odd_h, odd_a)
                except:
                    pass
        except Exception as e:
            print(f"[ODDS-APFC] Erro: {e}")

    # Fallback 3: Odds API (quando tiver cota)
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/soccer/odds/",
                         params={"apiKey": ODDS_API_KEY, "regions": "eu",
                                 "markets": "h2h", "oddsFormat": "decimal"}, timeout=10)
        if r.status_code == 200:
            for evento in r.json():
                nomes = [evento.get("home_team","").lower(), evento.get("away_team","").lower()]
                if home.lower() in nomes and away.lower() in nomes:
                    for book in evento.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            if mkt["key"] == "h2h":
                                outcomes = {o["name"].lower(): o["price"] for o in mkt["outcomes"]}
                                odd_h = outcomes.get(home.lower(), 99)
                                odd_a = outcomes.get(away.lower(), 99)
                                fav = "h" if odd_h <= odd_a else "a"
                                print(f"[ODDS-API] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                                return (fav, odd_h, odd_a)
    except:
        pass
    return (None, None, None)

# ═══════════════════════════════════════════════════════════════════════════════
# FILTRO DE JANELAS
# ═══════════════════════════════════════════════════════════════════════════════
def get_odd_favorito_num(home, away, fid=None, league=None, fid_raw=None):
    """Retorna a odd decimal do favorito (numero). Usa SokkerPro ou apifootball."""
    if fid_raw:
        try:
            headers = {}  # SokkerPro
            if r.status_code == 200:
                odds = r.json().get("odds", {})
                oh = float(odds.get("home_win") or 99)
                oa = float(odds.get("away_win") or 99)
                if oh < 90 and oa < 90:
                    return min(oh, oa)
        except: pass
    
    if fid:
        try:
            # SokkerPro odds
            oh, oa = get_odds_sokkerpro(fid)
            if oh and oa and oh > 1 and oa > 1:
                return min(oh, oa)
        except: pass
    
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/soccer/odds/",
                         params={"apiKey": ODDS_API_KEY, "regions": "eu",
                                 "markets": "h2h", "oddsFormat": "decimal"}, timeout=10)
        if r.status_code == 200:
            for evento in r.json():
                nomes = [evento.get("home_team","").lower(), evento.get("away_team","").lower()]
                if home.lower() in nomes and away.lower() in nomes:
                    for book in evento.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            if mkt["key"] == "h2h":
                                outcomes = {o["name"].lower(): o["price"] for o in mkt["outcomes"]}
                                odd_h = outcomes.get(home.lower(), 99)
                                odd_a = outcomes.get(away.lower(), 99)
                                return min(odd_h, odd_a)
    except:
        pass
    return 99

def calcular_prob_gols_ht(chutes_tot, chutes_gol, minuto):
    """Estima prob de gols usando taxa de chutes como proxy de xG."""
    import math as _math
    taxa_conversao = 0.10
    xg = chutes_gol * taxa_conversao + chutes_tot * 0.04
    min_restantes_ht = max(45 - minuto, 1)
    min_restantes_ft = max(90 - minuto, 1)
    taxa_por_min = xg / max(minuto, 1)
    xg_rest_ht = taxa_por_min * min_restantes_ht
    xg_rest_ft = taxa_por_min * min_restantes_ft
    xg_total_ft = xg + xg_rest_ft
    prob_05_ht = round((1 - _math.exp(-max(xg_rest_ht, 0.05))) * 100, 1)
    prob_15_ft = round((1 - _math.exp(-max(xg_total_ft - 1, 0.1))) * 100, 1)
    return prob_15_ft, prob_05_ht

def filtrar_janelas(jogos):
    resultado = []
    for j in jogos:
        m = j["minuto"]
        p_raw = j["period"]
        if isinstance(p_raw, str):
            p = 2 if '2' in p_raw else 1
        else:
            p = p_raw
            
        em_janela = (
            (p == 1 and 15 <= m <= 27) or
            (p == 1 and 28 <= m <= 38) or
            (p == 2 and 55 <= m <= 77) or
            (p == 2 and 78 <= m <= 88)
        )
        if em_janela:
            resultado.append(j)
    return resultado

# ═══════════════════════════════════════════════════════════════════════════════
# MENSAGEM PADRÃO
# ═══════════════════════════════════════════════════════════════════════════════
def gerar_motivo(mercado, stats, sh, sa, fav_final, minuto, cantos_atual=0):
    chutes_h          = stats.get("chutes_tot_h", 0) if stats else 0
    chutes_a          = stats.get("chutes_tot_a", 0) if stats else 0
    chutes_gol_h      = stats.get("chutes_gol_h", 0) if stats else 0
    chutes_gol_a      = stats.get("chutes_gol_a", 0) if stats else 0
    cantos_h          = max(0, stats.get("escanteios_h", 0)) if stats else 0
    cantos_a          = max(0, stats.get("escanteios_a", 0)) if stats else 0
    red_h             = stats.get("red_cards_h", 0) if stats else 0
    red_a             = stats.get("red_cards_a", 0) if stats else 0
    posse_h_raw       = stats.get("posse_h", 0.0) if stats else 0.0
    posse_a_raw       = stats.get("posse_a", 0.0) if stats else 0.0
    atq_perig_h       = stats.get("ataques_perigosos_h", 0) if stats else 0
    atq_perig_a       = stats.get("ataques_perigosos_a", 0) if stats else 0
    posse_h = int(round(float(posse_h_raw) * 100)) if float(posse_h_raw) <= 1 else int(round(float(posse_h_raw)))
    posse_a = int(round(float(posse_a_raw) * 100)) if float(posse_a_raw) <= 1 else int(round(float(posse_a_raw)))
    total_chutes      = chutes_h + chutes_a
    total_cantos      = cantos_h + cantos_a
    total_atq_perig   = atq_perig_h + atq_perig_a
    tem_dados         = total_chutes > 0 or total_cantos > 0 or total_atq_perig > 0

    if not tem_dados:
        return "Estatísticas não disponíveis para esta liga"

    # Labels
    if fav_final == "h":
        fav_label   = "Favorito"
        zebra_label = "Zebra"
        fav_chutes  = chutes_h; fav_gol = chutes_gol_h
        adv_chutes  = chutes_a; adv_gol = chutes_gol_a
        fav_atq     = atq_perig_h
        adv_atq     = atq_perig_a
    elif fav_final == "a":
        fav_label   = "Favorito"
        zebra_label = "Zebra"
        fav_chutes  = chutes_a; fav_gol = chutes_gol_a
        adv_chutes  = chutes_h; adv_gol = chutes_gol_h
        fav_atq     = atq_perig_a
        adv_atq     = atq_perig_h
    else:
        fav_label   = "Casa"
        zebra_label = "Fora"
        fav_chutes  = chutes_h; fav_gol = chutes_gol_h
        adv_chutes  = chutes_a; adv_gol = chutes_gol_a
        fav_atq     = atq_perig_h
        adv_atq     = atq_perig_a

    jogo_aberto    = sh == 0 and sa == 0
    fav_perdendo   = (fav_final == "h" and sh < sa) or (fav_final == "a" and sa < sh)
    fav_ganhando   = (fav_final == "h" and sh > sa) or (fav_final == "a" and sa > sh)
    zebra_dominando = adv_chutes > fav_chutes
    minuto_seguro  = max(minuto, 1)
    fav_atq_por_min = round(fav_atq / minuto_seguro, 2)
    adv_atq_por_min = round(adv_atq / minuto_seguro, 2)
    fav_amassando   = fav_atq_por_min >= 0.70 and adv_atq_por_min < 0.70
    adv_amassando   = adv_atq_por_min >= 0.70 and fav_atq_por_min < 0.70
    ambos_pressionando = fav_atq_por_min >= 0.70 and adv_atq_por_min >= 0.70

    vermelho = ""
    if red_h > 0 or red_a > 0:
        vermelho = " 🟥 Vermelho: " + ("Casa" if red_h > 0 else "Fora")

    posse_txt = ""
    if posse_h >= 55:
        posse_txt = f", Casa com {posse_h}% de posse"
    elif posse_a >= 55:
        posse_txt = f", Fora com {posse_a}% de posse"

    # ════════════════════════════════════════════════════════════════
    # ALERTAS POR MERCADO — motivo da entrada
    # ════════════════════════════════════════════════════════════════

    if "CORNER" in mercado or "ESCANTEIO" in mercado:
        if "HT" in mercado:
            if total_atq_perig >= 12:
                return f"Pressão ofensiva muito alta no 1º tempo{vermelho}"
            elif total_atq_perig >= 8:
                return f"Pressão ofensiva elevada no 1º tempo{vermelho}"
            return f"Pressão ofensiva em crescimento no 1º tempo{vermelho}"
        else:
            if total_atq_perig >= 25:
                return f"Pressão ofensiva constante durante a partida{vermelho}"
            elif total_atq_perig >= 15:
                return f"Pressão ofensiva sustentada na partida{vermelho}"
            return f"Pressão ofensiva contínua na partida{vermelho}"

    if mercado == "HT":
        if chutes_gol_h >= 1 and chutes_gol_a >= 1:
            return f"Ambas equipes finalizando no alvo{vermelho}"
        if chutes_gol_h >= 1:
            return f"{fav_label if fav_final=='h' else 'Casa'} finalizando no alvo{vermelho}"
        if chutes_gol_a >= 1:
            return f"{fav_label if fav_final=='a' else 'Fora'} finalizando no alvo{vermelho}"
        if total_chutes >= 8:
            return f"Alta intensidade de chutes no 1º tempo{vermelho}"
        if fav_amassando:
            return f"{fav_label} dominando as ações ofensivas no 1º tempo{vermelho}"
        if ambos_pressionando:
            return f"Ambas equipes pressionando no campo de ataque{vermelho}"
        return f"Jogo movimentado com chances nos dois lados{vermelho}"

    if mercado == "BTTS":
        if chutes_gol_h >= 2 and chutes_gol_a >= 1:
            return f"Ambas equipes com finalizações no alvo{vermelho}"
        if fav_chutes >= 6 and adv_chutes >= 4:
            return f"Ambas equipes atacando com frequência{vermelho}"
        if ambos_pressionando:
            return f"Pressão ofensiva dos dois lados{vermelho}"
        if fav_amassando and adv_chutes >= 4:
            return f"{fav_label} dominando mas {zebra_label} também responde no ataque{vermelho}"
        return f"Ambas equipes com volume de ataque{vermelho}"

    if mercado == "OFT":
        if sh + sa == 1:
            return f"Placar em {sh}x{sa} com movimentação — {total_chutes} chutes | Mais um gol esperado para Over 1.5{vermelho}"
        if total_chutes >= 12:
            return f"Jogo com {total_chutes} finalizações — forte tendência de mais gols no 2º tempo{vermelho}"
        if ambos_pressionando:
            return f"Pressão total — {total_atq_perig} ataques perigosos | Over 1.5 FT com boa projeção{vermelho}"
        if total_atq_perig >= 10:
            return f"{total_atq_perig} ataques perigosos — placar deve se mover para Over 1.5{vermelho}"
        return f"Partida com bons números ofensivos — {total_chutes} chutes em {minuto}' | Over 1.5{vermelho}"

    if mercado == "OVERGOAL":
        if jogo_aberto:
            return f"Jogo 0x0 mas aberto — {total_chutes} chutes, {total_atq_perig} ataques perigosos | Gol esperado{vermelho}"
        if fav_amassando or adv_amassando:
            return f"Time amassando e placar ainda baixo — {total_atq_perig} atq. perigosos | Over Gol Partida{vermelho}"
        if total_atq_perig >= 12:
            return f"Pressão ofensiva muito alta — {total_atq_perig} ataques perigosos | Gol no FT{vermelho}"
        return f"Expectativa de gol com base no volume — {total_chutes} chutes, {total_atq_perig} ataques{vermelho}"

    # ── Fallback: análise geral (pra segurança) ──
    if jogo_aberto:
        if chutes_gol_h >= 3 and chutes_gol_a >= 3:
            return f"Jogo aberto com grandes chances de gol dos dois lados — {chutes_gol_h} finalizações de Casa, {chutes_gol_a} de Fora{posse_txt}{vermelho}"
        if fav_chutes >= 8 and fav_gol >= 3:
            return f"Jogo aberto, {fav_label} criando grandes chances — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if zebra_dominando and adv_chutes >= 6 and adv_gol >= 2:
            return f"Jogo aberto, {zebra_label} surpreendendo — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if total_chutes >= 12:
            return f"Jogo aberto e bastante movimentado — {chutes_h} chutes de Casa, {chutes_a} de Fora, sem gols ainda{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes and fav_gol > 0:
            return f"Jogo aberto, {fav_label} dominando com {fav_chutes} chutes ({fav_gol} no alvo){posse_txt}{vermelho}"
        if fav_amassando:
            return f"Jogo aberto, {fav_label} amassando — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if adv_amassando:
            return f"Jogo aberto, {zebra_label} pressionando muito — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Jogo aberto, ambas equipes pressionando forte — {total_atq_perig} ataques perigosos no total{posse_txt}{vermelho}"
        return f"Jogo aberto, ambas buscando o primeiro gol — {chutes_h} chutes x {chutes_a}{posse_txt}{vermelho}"

    if fav_perdendo:
        if fav_chutes >= 8 and fav_gol >= 3:
            return f"Grandes chances do {fav_label} empatar — chegando constantemente com {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes >= 6 and fav_gol >= 2:
            return f"{fav_label} em busca do empate, criando boas chances — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_amassando:
            return f"{fav_label} perdendo mas amassando! — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if zebra_dominando and adv_chutes >= 8:
            return f"{zebra_label} dominando e ameaçando ampliar — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if adv_amassando:
            return f"{zebra_label} com mais volume de ataque — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Ambas pressionando — {total_atq_perig} ataques perigosos, jogo aberto{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes:
            return f"{fav_label} em busca do empate, pressionando com {fav_chutes} chutes x {adv_chutes}{posse_txt}{vermelho}"
        return f"{fav_label} perdendo e tentando reagir — {fav_chutes} chutes x {adv_chutes} da {zebra_label}{posse_txt}{vermelho}"

    if fav_ganhando:
        if adv_chutes >= 8 and adv_gol >= 3:
            return f"{zebra_label} pressionando forte em busca do empate — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if adv_amassando:
            return f"{zebra_label} amassando mesmo perdendo — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if fav_chutes >= 8:
            return f"{fav_label} controlando e ampliando a pressão — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_amassando:
            return f"{fav_label} na frente e amassando — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Ambas pressionando, placar aberto — {total_atq_perig} ataques perigosos{posse_txt}{vermelho}"
        return f"{fav_label} vencendo, jogo controlado — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"

    if chutes_gol_h >= 3 and chutes_gol_a >= 3:
        return f"Jogo bastante movimentado, ambas chutando no alvo — {chutes_gol_h} finalizações de Casa, {chutes_gol_a} de Fora{posse_txt}{vermelho}"
    if chutes_h >= 8 and chutes_a >= 8:
        return f"Jogo intenso dos dois lados — {chutes_h} chutes de Casa, {chutes_a} de Fora{posse_txt}{vermelho}"
    if fav_chutes >= 8 and fav_gol >= 3:
        return f"{fav_label} chegando constantemente na área — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
    if zebra_dominando and adv_chutes >= 6:
        return f"{zebra_label} surpreendendo com mais volume — {adv_chutes} chutes ({adv_gol} no alvo) x {fav_chutes} do {fav_label}{posse_txt}{vermelho}"
    if fav_chutes > adv_chutes and fav_gol > 0:
        return f"{fav_label} criando mais chances — {fav_chutes} chutes ({fav_gol} no alvo) x {adv_chutes}{posse_txt}{vermelho}"
    if fav_amassando:
        return f"{fav_label} amassando em busca da virada — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
    if adv_amassando:
        return f"{zebra_label} pressionando para virar — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
    if ambos_pressionando:
        return f"Jogo eletrizante, ambas pressionando — {total_atq_perig} ataques perigosos{posse_txt}{vermelho}"
    if total_cantos >= 6:
        return f"Jogo bastante movimentado pelas laterais — {total_cantos} escanteios, {total_chutes} chutes{posse_txt}{vermelho}"
    return f"Jogo equilibrado, ambas criando chances — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"

def msg_universal(home, away, minuto, liga, pais, n, mercado, entrada, placar, extra_val=None, cantos_atual=0, stats=None, sh=0, sa=0, fav_final="h", odd_h=None, odd_a=None, odd_b365=None, odd_bano=None):
    # Definir a entrada conforme os layouts das imagens
    if "CORNER" in mercado or "ESCANTEIO" in mercado:
        linha = cantos_atual + 0.5
        entrada = f"Mais de {linha}🚩"
    elif mercado in ("HT", "BTTS", "OFT", "OVERGOAL"):
        if "Over" not in str(entrada) and "Ambas" not in str(entrada):
            if mercado == "OFT": entrada = "Over 1.5"
            elif mercado == "BTTS": entrada = "Ambas Marcam"
            elif mercado == "HT": entrada = "Over 0.5"
        entrada = f"{entrada}⚽️"

    # Extração de estatísticas
    chutes_h = stats.get("chutes_tot_h", 0) if stats else 0
    chutes_a = stats.get("chutes_tot_a", 0) if stats else 0
    alvo_h   = stats.get("chutes_gol_h", 0) if stats else 0
    alvo_a   = stats.get("chutes_gol_a", 0) if stats else 0
    cant_h   = stats.get("escanteios_h", 0) if stats else 0
    cant_a   = stats.get("escanteios_a", 0) if stats else 0
    atq_per_h = stats.get("ataques_perigosos_h", 0) if stats else 0
    atq_per_a = stats.get("ataques_perigosos_a", 0) if stats else 0
    
    # ════════════════════════════════════════════════════════════════
    # SISTEMA DE ALERTAS UNIFICADO
    # ════════════════════════════════════════════════════════════════
    # Cleubiano thresholds (APPM puro) — definem a intensidade da pressão
    # Zapia thresholds (APPM + mercado + stats) — refinam o contexto
    # ════════════════════════════════════════════════════════════════
    
    atq_max = max(atq_per_h, atq_per_a)
    appm_val = round(atq_max / minuto, 2) if minuto > 0 else 0
    
    # — Quem está pressionando —
    if atq_per_h > atq_per_a:
        quem = "do Mandante"
        dominante = home
    elif atq_per_a > atq_per_h:
        quem = "do Visitante"
        dominante = away
    else:
        quem = "de ambas equipes"
        dominante = "Ambos"
    
    periodo = "1º tempo" if minuto <= 45 else "2º tempo"
    
    # — Variáveis auxiliares —
    total_chutes = chutes_h + chutes_a
    total_alvo = alvo_h + alvo_a
    total_atq = atq_per_h + atq_per_a
    total_cant = cant_h + cant_a
    jogo_aberto = placar == "0x0"
    fav_nome = home if fav_final == "h" else (away if fav_final == "a" else "—")
    
    # ════════════════════════════════════════════════════════════════
    # THRESHOLDS CLEUBIANO — APPM PURO (ÚNICO SISTEMA DE ALERTA)
    # ════════════════════════════════════════════════════════════════
    if appm_val >= 2.0:
        alerta = "Partida Com Pressão Constante."
    elif appm_val >= 1.5:
        alerta = "Partida Pegando Fogo."
    elif appm_val >= 1.0:
        alerta = "Partida Com Ritmo Intenso."
    elif appm_val >= 0.8:
        alerta = f"Partida com pressão {quem}."
    elif appm_val >= 0.7:
        alerta = "Partida Com Ritmo Moderado."
    elif appm_val >= 0.5:
        alerta = "Partida Com Ritmo Médio."
    elif appm_val >= 0.3:
        alerta = "Partida Com Ritmo Fraco."
    else:
        alerta = "Partida Com Ritmo Muito Baixo."

    # APPM para exibição no layout
    appm = appm_val

    # Emojis EXATOS do print 1784355796901
    seta = "🚩" # No print é a seta vermelha que o Telegram renderiza como o emoji 🚩 ou similar
    seta_v = "🚩" 

    if "CORNER" in mercado or "ESCANTEIO" in mercado:
        nome_m = mercado.replace('CORNER_', 'ESCANTEIO ÁSIAT/LMT ')
        title = f"🚩🔥{nome_m}🔥🚩"
    else:
        titles_map = {
            "HT": "OVER GOL INTERVALO",
            "BTTS": "AMBAS MARCAM",
            "OFT": "OVER 1.5 GOLS PARTIDA",
            "OVERGOAL": "OVER GOL PARTIDA"
        }
        title = f"⚽️🔥{titles_map.get(mercado, mercado)}🔥⚽️"

    odd_rec = "1.70"
    sep = "━━━━━━━━━━━━━━━━━━━━"

    # Monta texto da liga (com país se disponível)
    liga_texto = f"<b>🌍 Liga: {liga}</b>"
    if pais:
        liga_texto = f"<b>🌍 Liga: {liga} ({pais})</b>"

    # Layout EXATO dos 6 templates - tudo em negrito, sem "OPORTUNIDADE IDENTIFICADA"
    msg = (
        f"{sep}\n"
        f"<b>{title}</b>\n"
        f"{sep}\n"
        f"<b>⚽️ Placar: {placar}</b>\n"
        f"{liga_texto}\n"
        f"<b>📡 {home} x {away}</b>\n"
        f"<b>👀 ODDs: Casa {odd_h or '—'} / Fora {odd_a or '—'}</b>\n"
        f"<b>⏰️ Minuto: {minuto}'</b>\n"
        f"{sep}\n"
        f"<b>📊 Estatísticas ao Vivo da Partida:</b>\n"
        f"<b>🚀 Chutes Totais: {chutes_h} | {chutes_a}</b>\n"
        f"<b>🎯 Chutes No Alvo: {alvo_h} | {alvo_a}</b>\n"
        f"<b>⚔️ Ataques Perigosos: {atq_per_h} | {atq_per_a}</b>\n"
        f"<b>🚩 Escanteios: {cant_h} | {cant_a}</b>\n"
        f"{sep}\n"
        f"<b>💡 Análise Técnica da Partida:</b>\n"
        f"<b>🎯 Favorito: {fav_nome}</b>\n"
        f"<b>🔥 Pressão APPM:⚠️{appm}⚠️</b>\n"
        f"<b>🚨 Alerta: {alerta}</b>\n"
        f"{sep}\n"
        f"<b>📌 Entrada: {entrada}</b>\n"
        f"<b>💰 ODD Recomendada: {odd_rec}+</b>\n"
        f"{sep}\n"
        "<b>🔔Jogue com Responsabilidade🔔</b>"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🟣BET365🟣", "url": "https://www.bet365.bet.br/#/AX/"},
                {"text": "🔵PARIPESA🔵", "url": "https://paripesa.com/mobile?bf=667237b941dd4_5426307053"}
            ]
        ]
    }
    return msg, keyboard
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🟣BET365🟣", "url": "https://www.bet365.bet.br/#/AX/"},
                {"text": "🔵PARIPESA🔵", "url": "https://paripesa.com/mobile?bf=667237b941dd4_5426307053"}
            ]
        ]
    }
    
    return msg, keyboard

def checar_resultado(sinal):
    """Verifica se um sinal já enviado deu green ou red usando SokkerPro."""
    try:
        fid_raw = str(sinal.get("fixture_id", "")).replace("skp_", "")
        mercado = sinal.get("mercado")
        
        # Busca dados do jogo via SokkerPro
        data = _get_data()
        if not data: return None
        
        # Procura a fixture pelo ID
        fixture = None
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    fixture = fix
                    break
            if fixture: break
        
        if not fixture: return None
        
        status = fixture.get('status', '')
        minute = int(fixture.get('minute', 0) or 0)
        is_final = status in ('FT', 'PEN')
        # So confirma HT se estiver no 2o tempo (minuto >= 50) ou status HT/2nd
        # Evita confirmar durante acrescimos do 1T (minuto 45-49 com status 1st)
        is_2h = (status in ('2nd', 'HT')) or (minute >= 50)
        
        if not (is_final or (mercado in ["HT", "CORNER_HT"] and is_2h)):
            return None
        
        # Placar atual
        gh = int(fixture.get('scoresLocalTeam', 0) or 0)
        ga = int(fixture.get('scoresVisitorTeam', 0) or 0)
        total_final = gh + ga
        
        # Placar HT (scoresHT = total de gols no intervalo)
        scores_ht = int(fixture.get('scoresHT', 0) or 0)
        # Estima HT individual: busca o placar mais recente antes do HT
        # SokkerPro não separa home/away no HT, mas scoresHT já é o total
        # Para mercado HT, precisamos apenas saber se houve gol
        total_ht = scores_ht
        
        # Lógica por Mercado
        if mercado in ["HT"]:
            return "green" if total_ht >= 1 else ("red" if (is_2h or is_final) else None)
        
        elif mercado == "BTTS":
            return "green" if (gh >= 1 and ga >= 1) else ("red" if is_final else None)
        
        elif mercado == "OFT":
            return "green" if total_final >= 2 else ("red" if is_final else None)
            
        elif mercado == "OVERGOAL":
            gols_entrada = sinal.get("extra_val", 0)
            return "green" if total_final > gols_entrada else ("red" if is_final else None)
            
        elif mercado in ["CORNER_HT"]:
            c_h = _get_int(fixture.get('localCorners', 0))
            c_a = _get_int(fixture.get('visitorCorners', 0))
            c_final = max(0, c_h) + max(0, c_a)
            c_entrada = sinal.get("extra_val", 0)
            if c_final > c_entrada: return "green"
            # RED se já entrou no 2º tempo (escanteios do 1º tempo já estão finalizados)
            return "red" if is_2h else None

        elif mercado == "CORNER_FT":
            c_h = _get_int(fixture.get('localCorners', 0))
            c_a = _get_int(fixture.get('visitorCorners', 0))
            c_final = max(0, c_h) + max(0, c_a)
            c_entrada = sinal.get("extra_val", 0)
            if c_final > c_entrada: return "green"
            return "red" if is_final else None

        return None
    except: return None




# ═══════════════════════════════════════════════════════════════════════════════
# COMANDOS TELEGRAM (/relatoriodiario e /radar)
# ═══════════════════════════════════════════════════════════════════════════════
def check_status_command(total_jogos_live=0, jogos_live=None, jogos_na_janela=None):
    import base64 as _b64
    last_id = 0
    # Lê last_update do GitHub para persistir entre execuções
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/last_update.json"
            r = requests.get(url, headers=_github_headers(), timeout=6)
            if r.status_code == 200:
                last_id = json.loads(_b64.b64decode(r.json()["content"]).decode()).get("last_id", 0)
        except: pass
    elif os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE, 'r') as f: last_id = json.load(f).get("last_id", 0)
        except: pass
    try:
        sep = "━━━━━━━━━━━━━━━━━━━━"
        r   = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                           params={"offset": last_id + 1, "timeout": 5}, timeout=10).json()
        if not r.get("ok"): return
        new_last_id = last_id
        radar_respondido = False
        relatorio_respondido = False
        agora_ts = datetime.now(timezone.utc).timestamp()
        for update in r.get("result", []):
            new_last_id = update["update_id"]
            msg     = update.get("message", {})
            text    = msg.get("text", "")
            chat_orig = msg.get("chat", {}).get("id", 0)
            msg_ts  = msg.get("date", 0)
            # Ignora comandos com mais de 30 minutos (evita processar acúmulo muito antigo)
            if agora_ts - msg_ts > 600: # Ignora comandos com mais de 10 minutos
                continue
            pass  # responde em qualquer chat
            if text == "/relatoriomensal" and not relatorio_respondido:
                msg = enviar_relatorio_mensal()
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                              json={"chat_id": chat_orig, "text": msg, "parse_mode": "HTML"})
                relatorio_respondido = True
            if text == "/relatoriodiario" and not relatorio_respondido:
                enviar_relatorio_diario()
                relatorio_respondido = True
            elif text == "/mercados" or text == "/mercados24h":
                try:
                    if text == "/mercados24h":
                        msg = enviar_relatorio_mercados24h()
                    else:
                        msg = enviar_relatorio_performance()
                    if msg:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                                      json={"chat_id": chat_orig, "text": msg, "parse_mode": "HTML"})
                    else:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                                      json={"chat_id": chat_orig, "text": "Ainda sem dados de performance registrados.", "parse_mode": "HTML"})
                except Exception as e:
                    print(f"[PERFORMANCE] Erro: {e}")
            elif text == "/radar" and not radar_respondido:
                jogos_live = jogos_live or []
                jogos_na_janela = jogos_na_janela or []
                # Monta lista de jogos na janela
                if jogos_na_janela:
                    linhas_janela = ""
                    for j in jogos_na_janela:
                        h = j.get("home", "")
                        a = j.get("away", "")
                        m = j.get("minuto", 0)
                        sh = j.get("sh", 0)
                        sa = j.get("sa", 0)
                        liga = j.get("liga", "")
                        linhas_janela += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
                else:
                    linhas_janela = "Nenhum jogo na janela no momento."
                # Monta lista de jogos ao vivo fora da janela (até 10)
                fora_janela = [j for j in jogos_live if j not in jogos_na_janela]
                if fora_janela:
                    linhas_fora = ""
                    for j in fora_janela[:10]:
                        h = j.get("home", "")
                        a = j.get("away", "")
                        m = j.get("minuto", 0)
                        sh = j.get("sh", 0)
                        sa = j.get("sa", 0)
                        linhas_fora += f"⏳ {h} x {a} | {m}' | {sh}x{sa}\n"
                    if len(fora_janela) > 10:
                        linhas_fora += f"... e mais {len(fora_janela)-10} jogos"
                else:
                    linhas_fora = "—"
                msg_radar = (
                    f"{sep}\n"
                    f"📡👉<b>RADAR DE JOGOS AO VIVO</b>👈📡\n"
                    f"{sep}\n"
                    f"🔴 <b>{total_jogos_live} jogos ao vivo</b>\n"
                    f"🎯 <b>{len(jogos_na_janela)} na janela alvo</b>\n"
                    f"{sep}\n"
                    f"🚨<b>JOGOS NO ALVO:</b>\n{linhas_janela}"
                    f"{sep}\n"
                    f"<b>⏳ FORA DA JANELA:</b>\n{linhas_fora}"
                    f"{sep}"
                )
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_orig, "text": msg_radar, "parse_mode": "HTML"}, timeout=10)
                radar_respondido = True
        if new_last_id > last_id:
            with open(LAST_UPDATE_FILE, 'w') as f: json.dump({"last_id": new_last_id}, f)
            # Salva no GitHub para persistir entre execuções
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/last_update.json"
            r_get = requests.get(url, headers=_github_headers(), timeout=6)
            sha_lu = r_get.json().get("sha", "") if r_get.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps({"last_id": new_last_id}).encode()).decode()
            payload = {"message": "state: last_update [skip ci]", "content": content_b64}
            if sha_lu: payload["sha"] = sha_lu
            r_put = requests.put(url, headers=_github_headers(), json=payload, timeout=8)
            print(f"[CMD] last_id salvo: {new_last_id} | status: {r_put.status_code} | token_ok: {bool(GITHUB_TOKEN)}")
    except Exception as e:
        print(f"[CMD] Erro ao processar comandos: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# HISTÓRICO — Média de gols (usando H2H da apifootball)
# ═══════════════════════════════════════════════════════════════════════════════
_HIST_CACHE = {}
def get_media_gols_historica(home_id, away_id):
    """Retorna a média de gols por partida (jogo todo) dos últimos 10 jogos de cada time.
    Usa a API H2H da apifootball. Cache em memória pra evitar chamadas repetidas."""
    chave = f"{home_id}_{away_id}"
    if chave in _HIST_CACHE:
        return _HIST_CACHE[chave]

    if not home_id or not away_id or home_id == "" or away_id == "":
        _HIST_CACHE[chave] = -1.0
        return -1.0

    try:
        params = {"action": "get_H2H", "firstTeamId": home_id, "secondTeamId": away_id, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not isinstance(data, dict):
            _HIST_CACHE[chave] = -1.0
            return -1.0

        # Junta todos os resultados dos dois times
        todos_jogos = []
        for chave_lista in ["firstTeam_lastResults", "secondTeam_lastResults"]:
            lista = data.get(chave_lista, [])
            if isinstance(lista, list):
                for j in lista:
                    try:
                        ph = int(j.get("match_hometeam_score", 0) or 0)
                        pa = int(j.get("match_awayteam_score", 0) or 0)
                        todos_jogos.append(ph + pa)
                    except: pass

        if len(todos_jogos) < 4:
            _HIST_CACHE[chave] = -1.0
            return -1.0

        media = round(sum(todos_jogos) / len(todos_jogos), 1)
        _HIST_CACHE[chave] = media
        return media
    except:
        _HIST_CACHE[chave] = 0.0
        return 0.0

def get_media_gols_historica_skp(home, away, stats):
    """Retorna a média de gols usando os campos medias da própria API SokkerPro.
    As médias são fornecidas pela SokkerPro (mínimo 10 jogos).
    Sem dados = retorna -1 (bloqueia: -1 < 2.2 = False).
    Aplicado APENAS nos mercados de gol (escanteios livres)."""
    chave = f"{home}_{away}"
    if chave in _HIST_CACHE:
        return _HIST_CACHE[chave]

    if not stats:
        _HIST_CACHE[chave] = -1.0
        return -1.0

    try:
        media_h = stats.get("medias_home_goal", 0)
        media_a = stats.get("medias_away_goal", 0)

        # Sem dados de média → retorna -1 (bloqueia na prática)
        if media_h <= 0 and media_a <= 0:
            _HIST_CACHE[chave] = -1.0
            return -1.0

        media_total = media_h + media_a
        _HIST_CACHE[chave] = media_total
        return media_total
    except:
        _HIST_CACHE[chave] = -1.0
        return -1.0

# ═══════════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def run():
    # ─── ISOLAMENTO POR REPOSITÓRIO: cada bot usa SÓ sua fonte ───
    _repo_atual = os.environ.get("GITHUB_REPOSITORY", "").lower()
    if "sokkerpro" in _repo_atual:
        BOT_SOURCE = "sokkerpro"
    else:
        BOT_SOURCE = "sokkerpro"

    print(f"[Iniciando monitoramento — Fonte: {BOT_SOURCE.upper()} | Repo: {_repo_atual}]")
    # Carrega config dinâmico
    cfg = _load_config()
    GERAL = cfg.get("geral", {})
    MERCADOS = cfg.get("mercados", {})
    # Atalhos para cada mercado
    M_HT    = MERCADOS.get("over_05_ht", {})
    M_BTTS  = MERCADOS.get("ambas_marcam", {})
    M_OFT   = MERCADOS.get("over_15_ft", {})
    M_OG    = MERCADOS.get("over_gol_partida", {})
    M_CHT   = MERCADOS.get("escanteio_ht", {})
    M_CFT   = MERCADOS.get("escanteio_ft", {})
    sent      = load_sent()
    total_env = 0
    janela_id = datetime.now(BRT).strftime('%Y%m%d%H')

    # ─────────────────────────────────────────────────────────────
    # PASSO 1: Coleta APENAS da fonte designada do bot
    # ─────────────────────────────────────────────────────────────
    jogos_live = []
    if BOT_SOURCE == "apifootball":
        jogos_live = get_jogos_apifootball_v3(set())
        print(f"[apifootball] {len(jogos_live)} jogos ao vivo")

    elif BOT_SOURCE == "sokkerpro":
        jogos_live = get_jogos_sokkerpro(set())
        print(f"[SokkerPro] {len(jogos_live)} jogos ao vivo")

    # PASSO 2: Filtra janelas alvo
    jogos_na_janela = filtrar_janelas(jogos_live)
    print(f"[Janela] {len(jogos_na_janela)} jogos nas janelas alvo")

    check_status_command(total_jogos_live=len(jogos_live), jogos_live=jogos_live, jogos_na_janela=jogos_na_janela)

    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDAÇÃO DE SINAIS PENDENTES — roda SEMPRE, mesmo sem jogos na janela
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        sinais_p = _load_sinais_github()
        rest = []
        for s in sinais_p:
            res = checar_resultado(s)
            if res:
                emoji = "🟢GREEN CONFIRMADO🟢" if res == "green" else "🔴RED CONFIRMADO🔴"
                send_telegram(emoji, reply_to=s.get("message_id"))
                salvar_resultado(res, mercado=s.get("mercado"))
                registrar_performance(s.get("mercado"), res)
            else:
                rest.append(s)
        _save_sinais_github(rest)
        print(f"[SINAIS] {len(sinais_p) - len(rest)} resultados confirmados, {len(rest)} ainda pendentes")
    except Exception as e:
        print(f"[SINAIS] Erro validação: {e}")

    if not jogos_na_janela:
        print("[OK] Nenhum jogo na janela — aguardando próximo ciclo")
        save_sent(sent)
        print("Finalizado. Enviados: 0")
        return

    # PASSO 3: Dedup simples (dentro da própria fonte — remove duplicatas do mesmo jogo)
    jogos_dedup = []
    vistos_chaves = set()
    for j in jogos_na_janela:
        hn_j = norm_nome_time(j["home"])
        an_j = norm_nome_time(j["away"])
        chave = hashlib.md5(f"{hn_j}-{an_j}".encode()).hexdigest()[:16]
        if chave not in vistos_chaves:
            vistos_chaves.add(chave)
            jogos_dedup.append(j)
    print(f"[Dedup] {len(jogos_na_janela)} -> {len(jogos_dedup)} jogos unicos")
    
    for j in jogos_dedup:
        fid    = j["fid"]
        h, a   = j["home"], j["away"]
        # Normaliza nomes pra chave estável entre APIs diferentes
        hn = norm_nome_time(h)
        an = norm_nome_time(a)
        dedup_id = hashlib.md5(f"{hn}-{an}".encode()).hexdigest()[:12]
        m, p   = j["minuto"], j["period"]
        sh, sa = j["sh"], j["sa"]
        liga   = str(j["liga"])
        pais   = j.get("pais", "")
        stot   = sh + sa
        placar = f"{sh}x{sa}"

        print(f"[Analisando] {h} x {a} | {placar} | {m}min")

        # ─── Stats da fonte designada apenas (sem fusão entre APIs) ───
        fid_raw = j.get("fid_raw", fid)
        stats = {}
        if BOT_SOURCE == "apifootball":
            try:
                sa_api = get_stats_apifootball_live(fid_raw)
                if isinstance(sa_api, dict) and sa_api: stats = sa_api
            except: pass
            if not stats or not (stats.get("escanteios_h", -1) >= 0 and stats.get("escanteios_a", -1) >= 0):
                try:
                    sa3 = get_stats_apifootball_v3(fid_raw)
                    if isinstance(sa3, dict) and sa3: stats = sa3
                except: pass
            if not stats or not (stats.get("escanteios_h", -1) >= 0 and stats.get("escanteios_a", -1) >= 0):
                try:
                    sa_name = get_stats_apifootball_by_name(h, a)
                    if isinstance(sa_name, dict) and sa_name.get("escanteios_h", -1) >= 0:
                        stats = sa_name
                        print(f"[APIF-NAME] Stats por nome OK: esc {sa_name.get('escanteios_h')}x{sa_name.get('escanteios_a')}")
                except: pass

        elif BOT_SOURCE == "sokkerpro":
            try:
                sb = get_stats_sokkerpro(fid_raw, h, a)
                if isinstance(sb, dict) and sb: stats = sb
            except: pass
            if not stats or not (stats.get("chutes_tot_h", 0) > 0 or stats.get("chutes_tot_a", 0) > 0 or
                                  stats.get("escanteios_h", -1) >= 0 or stats.get("escanteios_a", -1) >= 0 or
                                  stats.get("ataques_perigosos_h", 0) > 0 or stats.get("ataques_perigosos_a", 0) > 0):
                try:
                    sb_name = get_stats_sokkerpro_by_name(h, a)
                    if isinstance(sb_name, dict):
                        if "Club Friendlies" in liga:
                            stats = sb_name
                            print(f"[SKP-NAME] Friendlies aceito: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')}")
                        elif (sb_name.get("chutes_tot_h", 0) > 0 or sb_name.get("chutes_tot_a", 0) > 0 or
                              sb_name.get("ataques_perigosos_h", 0) > 0 or sb_name.get("ataques_perigosos_a", 0) > 0 or
                              sb_name.get("chutes_gol_h", 0) > 0 or sb_name.get("chutes_gol_a", 0) > 0):
                            stats = sb_name
                            print(f"[SKP-NAME] Stats via nome OK: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')} | chutes {sb_name.get('chutes_tot_h')}x{sb_name.get('chutes_tot_a')}")
                except: pass

        # Preenche defaults para campos que faltam
        for k in ["chutes_tot_h","chutes_tot_a","chutes_gol_h","chutes_gol_a"]:
            stats.setdefault(k, 0)
        for k in ["escanteios_h","escanteios_a"]:
            stats.setdefault(k, -1)
        for k in ["red_cards_h","red_cards_a"]:
            stats.setdefault(k, 0)

        if stats:
            print(f"[STATS-{BOT_SOURCE.upper()}] {h} x {a} | chutes: {stats.get('chutes_tot_h',0)}/{stats.get('chutes_tot_a',0)} | cantos: {stats.get('escanteios_h',-1)}/{stats.get('escanteios_a',-1)} | atq_perig: {stats.get('ataques_perigosos_h',0)}/{stats.get('ataques_perigosos_a',0)}")

        # Verifica se tem dados reais — sem stats E sem odds, pula o jogo
        tem_stats = stats and (
            stats.get("chutes_tot_h", 0) > 0 or
            stats.get("chutes_tot_a", 0) > 0 or
            stats.get("escanteios_h", -1) > 0 or
            stats.get("escanteios_a", -1) > 0 or
            stats.get("ataques_perigosos_h", 0) > 0 or
            stats.get("ataques_perigosos_a", 0) > 0
        )
        if not tem_stats:
            print(f"[SKIP] {h} x {a} — sem stats reais (chutes, cantos ou ataques perigosos) em nenhuma API, pulando jogo")
            continue

        # Favorito: odds da própria fonte (cada bot só usa sua API)
        odd_h = j.get("odd_h")
        odd_a = j.get("odd_a")
        fav_por_odds = False

        if BOT_SOURCE == "apifootball":
            if odd_h and odd_a and odd_h > 1 and odd_a > 1:
                fav_final = "h" if odd_h <= odd_a else "a"
                fav_por_odds = True
                print(f"[ODDS] {h} x {a} — odd Casa:{odd_h:.2f} Fora:{odd_a:.2f} (apifootball)")
            if not fav_por_odds:
                try:
                    r_odd = requests.get("https://apiv3.apifootball.com/",
                                     params={"action": "get_odds", "match_id": fid_raw, "APIkey": APIFOOTBALL_COM_KEY}, timeout=8)
                    odds_data = r_odd.json()
                    if isinstance(odds_data, list) and odds_data:
                        odd_ml = None
                        for bk_alvo in ("bet365", "betano"):
                            for od in odds_data:
                                if str(od.get("odd_bookmakers", "")).lower() == bk_alvo:
                                    odd_ml = od; break
                            if odd_ml: break
                        if not odd_ml: odd_ml = odds_data[0]
                        odd_h, odd_a = float(odd_ml.get("odd_1", 0)), float(odd_ml.get("odd_2", 0))
                        if odd_h > 1 and odd_a > 1:
                            fav_final = "h" if odd_h <= odd_a else "a"
                            fav_por_odds = True
                except: pass



        elif BOT_SOURCE == "sokkerpro":
            try:
                oh, oa = get_odds_sokkerpro(fid_raw)
                if oh and oa and oh > 1 and oa > 1:
                    odd_h, odd_a = oh, oa
                    fav_final = "h" if odd_h <= odd_a else "a"
                    fav_por_odds = True
                    print(f"[ODDS-SKP] {h} x {a} — odd Casa:{odd_h:.2f} Fora:{odd_a:.2f}")
            except: pass

        # Sem odds = usa stats (chutes) como fallback para definir favorito
        if not fav_por_odds:
            if stats and stats.get("fav_side") in ("h", "a"):
                fav_final = stats["fav_side"]
                print(f"[FAV-STATS] {h} x {a} — sem odds, favorito pelo chutes: {fav_final}")
            elif stats and (stats.get("chutes_tot_h", 0) > 0 or stats.get("chutes_tot_a", 0) > 0):
                fav_final = "h" if stats.get("chutes_tot_h", 0) >= stats.get("chutes_tot_a", 0) else "a"
                print(f"[FAV-STATS] {h} x {a} — sem odds, favorito pelo chutes: {fav_final}")
            else:
                fav_final = "h"
                print(f"[FAV-HOME] {h} x {a} — sem odds e sem stats, assumindo mandante como favorito")

        # Se NENHUMA fonte retornou odds válidas, pula o jogo
        if not (odd_h and odd_h > 1 and odd_a and odd_a > 1):
            print(f"[SKIP-SEM-ODDS] {h} x {a} — nenhuma odd válida (Casa:{odd_h} Fora:{odd_a}), pulando sinal")
            continue

        red_fav = stats.get(f"red_cards_{fav_final}", 0) if stats else 0

        # Placar do favorito e adversário
        fav_gols = sh if fav_final == "h" else sa
        adv_gols = sa if fav_final == "h" else sh

        # ─── DIAGNÓSTICO INICIAL DO JOGO ───
        print(f"[DIAG] {h} x {a} | placar={placar} | min={m} | periodo={p} | fav={fav_final} | gols_fav={fav_gols} gols_adv={adv_gols} | odds_casa={odd_h} odds_fora={odd_a} | chutes_totais={stats.get('chutes_tot_h',0)}x{stats.get('chutes_tot_a',0)} | chutes_gol={stats.get('chutes_gol_h',0)}x{stats.get('chutes_gol_a',0)} | atq_perig={stats.get('ataques_perigosos_h',0)}x{stats.get('ataques_perigosos_a',0)} | escanteios={stats.get('escanteios_h','?')}x{stats.get('escanteios_a','?')} | red_fav={red_fav}")

        # Favorito empatando = placar igual
        fav_empatando = (sh == sa)
        # Favorito perdendo por exatamente 1 gol — SOMENTE placares 0x1 ou 1x0 (total = 1 gol) — usado em OFT
        fav_perdendo_1 = (adv_gols - fav_gols) == 1 and (sh + sa) == 1
        # Favorito perdendo por exatamente 1 gol sem restrição de total — usado em escanteios e overgoal
        fav_perdendo_1_livre = (adv_gols - fav_gols) == 1
        # Condição escanteio: fav empatando OU perdendo por 1 (qualquer placar)
        corner_valido = fav_empatando or fav_perdendo_1_livre
        # Over 1.5 FT: placares válidos APENAS 1x0 ou 0x1 (fav perdendo por 1, total = 1 gol)
        fav_gols_oft = sh if fav_final == "h" else sa
        adv_gols_oft = sa if fav_final == "h" else sh
        oft_valido = (
            (adv_gols_oft - fav_gols_oft) == 1 and
            (sh + sa) == 1
        )

        # APPM, chutes, escanteios — valores brutos (cada mercado usa seu threshold)
        _aph_val = stats.get("ataques_perigosos_h", 0) if stats else 0
        _apa_val = stats.get("ataques_perigosos_a", 0) if stats else 0
        _apt_val = _aph_val + _apa_val
        _appm_total = round(_apt_val / m, 2) if m > 0 else 0
        _appm_h = round(_aph_val / m, 2) if m > 0 else 0
        _appm_a = round(_apa_val / m, 2) if m > 0 else 0
        _chutes_alvo_h = stats.get("chutes_gol_h", 0) if stats else 0
        _chutes_alvo_a = stats.get("chutes_gol_a", 0) if stats else 0
        _chutes_tot_h = stats.get("chutes_tot_h", 0) if stats else 0
        _chutes_tot_a = stats.get("chutes_tot_a", 0) if stats else 0
        _escanteios_h = stats.get("escanteios_h", -1) if stats else -1
        _escanteios_a = stats.get("escanteios_a", -1) if stats else -1

        # HISTÓRICO — Média de gols por partida
        home_id = j.get("home_id", "")
        away_id = j.get("away_id", "")
        media_hist = 0.0
        if BOT_SOURCE == "sokkerpro":
            media_hist = get_media_gols_historica_skp(h, a, stats)
        elif home_id and away_id:
            media_hist = get_media_gols_historica(home_id, away_id)

        # MERCADO 1: OVER 0.5 HT
        ht_ini = M_HT.get("minuto_inicio", 15)
        ht_fim = M_HT.get("minuto_fim", 27)
        if M_HT.get("ativo", True) and p == M_HT.get("periodo", 1) and ht_ini <= m <= ht_fim:
            # Critérios dinâmicos do mercado
            ht_appm_time = _crit(M_HT, GERAL, "appm_min_por_time", 0.7)
            ht_appm_total = _crit(M_HT, GERAL, "appm_min_total", 1.4)
            ht_media = _crit(M_HT, GERAL, "media_gols_partida_min", 2.2)
            ht_chutes_alvo = _crit(M_HT, GERAL, "chutes_alvo_min", 3)
            ht_chutes_tot = _crit(M_HT, GERAL, "chutes_totais_min", 6)
            ht_atq_perig = _crit(M_HT, GERAL, "ataques_perigosos_min", 15)
            ht_red_max = _crit(M_HT, GERAL, "max_red_card_fav", 0)
            ht_diff_max = _crit(M_HT, GERAL, "diferenca_gols_fav_max", 0)
            ht_appm_ok = _appm_h >= ht_appm_time or _appm_a >= ht_appm_time or _appm_total >= ht_appm_total
            ht_media_ok = media_hist >= ht_media if media_hist >= 0 else False
            ht_chutes_alvo_ok = (_chutes_alvo_h + _chutes_alvo_a) >= ht_chutes_alvo
            ht_chutes_tot_ok = (_chutes_tot_h + _chutes_tot_a) >= ht_chutes_tot
            if not (sh == 0 and sa == 0):
                print(f"[DIAG-HT-BARRA] {h} x {a} — placar não é 0x0 ({placar}), pulando")
            elif not fav_empatando:
                print(f"[DIAG-HT-BARRA] {h} x {a} — favorito não empatando (fav={fav_final}, gols_fav={fav_gols} adv={adv_gols}), pulando")
            elif red_fav > ht_red_max:
                print(f"[DIAG-HT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {ht_red_max}), pulando")
            elif not ht_appm_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}, min {ht_appm_time}/{ht_appm_total}), pulando")
            elif not ht_media_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — média histórica {media_hist:.1f} < {ht_media}, pulando")
            elif not ht_chutes_alvo_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — chutes no alvo insuficientes ({_chutes_alvo_h+_chutes_alvo_a} < {ht_chutes_alvo}), pulando")
            elif not ht_chutes_tot_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — chutes totais insuficientes ({_chutes_tot_h+_chutes_tot_a} < {ht_chutes_tot}), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_ht_{hoje}"
                if key in sent:
                    print(f"[DIAG-HT-DUP] {h} x {a} — já enviado hoje ({key}), pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 3, "HT", "Over 0.5", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "HT", h, a, mid)

        # MERCADO 2: AMBAS MARCAM BTTS
        btts_ini = M_BTTS.get("minuto_inicio", 55)
        btts_fim = M_BTTS.get("minuto_fim", 75)
        if M_BTTS.get("ativo", True) and p == M_BTTS.get("periodo", 2) and btts_ini <= m <= btts_fim and ((sh == 1 and sa == 0) or (sh == 0 and sa == 1)):
            b_appm_time = _crit(M_BTTS, GERAL, "appm_min_por_time", 0.7)
            b_appm_total = _crit(M_BTTS, GERAL, "appm_min_total", 1.4)
            b_media = _crit(M_BTTS, GERAL, "media_gols_partida_min", 2.2)
            b_chutes_alvo = _crit(M_BTTS, GERAL, "chutes_alvo_min", 3)
            b_chutes_tot = _crit(M_BTTS, GERAL, "chutes_totais_min", 6)
            b_atq = _crit(M_BTTS, GERAL, "ataques_perigosos_min", 15)
            b_red_max = _crit(M_BTTS, GERAL, "max_red_card_fav", 0)
            b_diff_max = _crit(M_BTTS, GERAL, "diferenca_gols_fav_max", 1)
            b_appm_ok = _appm_h >= b_appm_time or _appm_a >= b_appm_time or _appm_total >= b_appm_total
            b_media_ok = media_hist >= b_media if media_hist >= 0 else False
            b_chutes_ok = (_chutes_alvo_h + _chutes_alvo_a) >= b_chutes_alvo
            if not fav_perdendo_1:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — favorito não perdendo por 1 (fav_gols={fav_gols} adv={adv_gols}), pulando")
            elif red_fav > b_red_max:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {b_red_max}), pulando")
            elif not b_appm_ok:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not b_media_ok:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — média histórica {media_hist:.1f} < {b_media}, pulando")
            elif not b_chutes_ok:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — chutes no alvo ({_chutes_alvo_h+_chutes_alvo_a} < {b_chutes_alvo}), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_btts_{hoje}"
                if key in sent:
                    print(f"[DIAG-BTTS-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("bts_yes") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("bts_yes") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 4, "BTTS", "Ambas Marcam", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "BTTS", h, a, mid)

        # MERCADO 3: OVER 1.5 FT
        oft_ini = M_OFT.get("minuto_inicio", 55)
        oft_fim = M_OFT.get("minuto_fim", 75)
        if M_OFT.get("ativo", True) and p == M_OFT.get("periodo", 2) and oft_ini <= m <= oft_fim and ((sh == 1 and sa == 0) or (sh == 0 and sa == 1)):
            o_appm_time = _crit(M_OFT, GERAL, "appm_min_por_time", 0.7)
            o_appm_total = _crit(M_OFT, GERAL, "appm_min_total", 1.4)
            o_media = _crit(M_OFT, GERAL, "media_gols_partida_min", 2.2)
            o_chutes_alvo = _crit(M_OFT, GERAL, "chutes_alvo_min", 3)
            o_red_max = _crit(M_OFT, GERAL, "max_red_card_fav", 0)
            o_appm_ok = _appm_h >= o_appm_time or _appm_a >= o_appm_time or _appm_total >= o_appm_total
            o_media_ok = media_hist >= o_media if media_hist >= 0 else False
            if not fav_perdendo_1:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — favorito não perdendo por 1 (fav_gols={fav_gols} adv={adv_gols}), pulando")
            elif red_fav > o_red_max:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {o_red_max}), pulando")
            elif not o_appm_ok:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not o_media_ok:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — média histórica {media_hist:.1f} < {o_media}, pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_oft_{hoje}"
                mid = None
                if key in sent:
                    print(f"[DIAG-OFT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+1.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+1.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 4, "OFT", "Over 1.5", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OFT", h, a, mid)

        # MERCADO 4: OVER GOL PARTIDA
        og_ini = M_OG.get("minuto_inicio", 55)
        og_fim = M_OG.get("minuto_fim", 75)
        overgoal_valido = (fav_empatando or fav_perdendo_1)
        if M_OG.get("ativo", True) and p == M_OG.get("periodo", 2) and og_ini <= m <= og_fim:
            og_appm_time = _crit(M_OG, GERAL, "appm_min_por_time", 0.7)
            og_appm_total = _crit(M_OG, GERAL, "appm_min_total", 1.4)
            og_media = _crit(M_OG, GERAL, "media_gols_partida_min", 2.2)
            og_chutes_alvo = _crit(M_OG, GERAL, "chutes_alvo_min", 3)
            og_chutes_tot = _crit(M_OG, GERAL, "chutes_totais_min", 6)
            og_atq = _crit(M_OG, GERAL, "ataques_perigosos_min", 15)
            og_red_max = _crit(M_OG, GERAL, "max_red_card_fav", 0)
            og_appm_ok = _appm_h >= og_appm_time or _appm_a >= og_appm_time or _appm_total >= og_appm_total
            og_media_ok = media_hist >= og_media if media_hist >= 0 else False
            if not overgoal_valido:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav > og_red_max:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {og_red_max}), pulando")
            elif not og_appm_ok:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not og_media_ok:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — média histórica {media_hist:.1f} < {og_media}, pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_overgoal_{hoje}"
                # Linha dinâmica: sempre acima do total de gols atual
                total_gols = sh + sa
                if total_gols == 0:
                    linha_over = "Over 0.5"
                elif total_gols == 1:
                    linha_over = "Over 1.5"
                elif total_gols == 2:
                    linha_over = "Over 2.5"
                elif total_gols == 3:
                    linha_over = "Over 3.5"
                else:
                    linha_over = f"Over {total_gols + 0.5:.1f}"
                mid = None
                if key in sent:
                    print(f"[DIAG-OVERGOAL-DUP] {h} x {a} — já enviado hoje ({key}), pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 4, "OVERGOAL", linha_over, placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OVERGOAL", h, a, mid, extra_val=total_gols)

        # MERCADO 5: ESCANTEIO LIMITE HT
        cht_ini = M_CHT.get("minuto_inicio", 32)
        cht_fim = M_CHT.get("minuto_fim", 38)
        if M_CHT.get("ativo", True) and p == M_CHT.get("periodo", 1) and cht_ini <= m <= cht_fim:
            cht_appm_time = _crit(M_CHT, GERAL, "appm_min_por_time", 0.7)
            cht_appm_total = _crit(M_CHT, GERAL, "appm_min_total", 1.4)
            cht_escanteios = _crit(M_CHT, GERAL, "escanteios_minimos", 2)
            cht_red_max = _crit(M_CHT, GERAL, "max_red_card_fav", 0)
            cht_appm_ok = _appm_h >= cht_appm_time or _appm_a >= cht_appm_time or _appm_total >= cht_appm_total
            cht_esc_ok = (_escanteios_h + _escanteios_a) >= cht_escanteios if _escanteios_h >= 0 and _escanteios_a >= 0 else True
            corner_cond = corner_valido
            if not corner_cond:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav > cht_red_max:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {cht_red_max}), pulando")
            elif not cht_appm_ok:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not cht_esc_ok:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — escanteios insuficientes ({_escanteios_h+_escanteios_a} < {cht_escanteios}), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_cht_{hoje}"
                cantos_h = stats.get("escanteios_h", -1) if stats else -1
                cantos_a = stats.get("escanteios_a", -1) if stats else -1
                cantos = (max(0, cantos_h) + max(0, cantos_a)) if (cantos_h >= 0 and cantos_a >= 0) else -1
                mid = None
                if cantos < 0:
                    print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — cantos={cantos} sem dados, pulando")
                elif key in sent:
                    print(f"[DIAG-CORNER-HT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365_e = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano_e = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 5, "CORNER_HT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365_e, odd_bano=obano_e), marca=key, home=h, away=a, odd_b365_val=ob365_e, odd_bano_val=obano_e)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_HT", h, a, mid, extra_val=cantos)

        # MERCADO 6: ESCANTEIO LIMITE FT
        cft_ini = M_CFT.get("minuto_inicio", 82)
        cft_fim = M_CFT.get("minuto_fim", 88)
        if M_CFT.get("ativo", True) and p == M_CFT.get("periodo", 2) and cft_ini <= m <= cft_fim:
            cft_appm_time = _crit(M_CFT, GERAL, "appm_min_por_time", 0.7)
            cft_appm_total = _crit(M_CFT, GERAL, "appm_min_total", 1.4)
            cft_escanteios = _crit(M_CFT, GERAL, "escanteios_minimos", 2)
            cft_red_max = _crit(M_CFT, GERAL, "max_red_card_fav", 0)
            cft_appm_ok = _appm_h >= cft_appm_time or _appm_a >= cft_appm_time or _appm_total >= cft_appm_total
            cft_esc_ok = (_escanteios_h + _escanteios_a) >= cft_escanteios if _escanteios_h >= 0 and _escanteios_a >= 0 else True
            corner_ft_cond = corner_valido
            if not corner_ft_cond:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav > cft_red_max:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {cft_red_max}), pulando")
            elif not cft_appm_ok:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not cft_esc_ok:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — escanteios insuficientes ({_escanteios_h+_escanteios_a} < {cft_escanteios}), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_cft_{hoje}"
                cantos_h = stats.get("escanteios_h", -1) if stats else -1
                cantos_a = stats.get("escanteios_a", -1) if stats else -1
                if cantos_h >= 0 and cantos_a >= 0:
                    cantos = max(0, cantos_h) + max(0, cantos_a)
                else:
                    cantos = -1
                mid = None
                if cantos < 0:
                    print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — cantos={cantos} sem dados, pulando")
                elif key in sent:
                    print(f"[DIAG-CORNER-FT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365_e = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano_e = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, pais, 5, "CORNER_FT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365_e, odd_bano=obano_e), marca=key, home=h, away=a, odd_b365_val=ob365_e, odd_bano_val=obano_e)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_FT", h, a, mid, extra_val=cantos)

    save_sent(sent)

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO-DISPATCH: /relatoriodiario + /mercados24h às 23:55
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        agora_hora = datetime.now(BRT)
        if agora_hora.hour == 23 and agora_hora.minute >= 55:
            print(f"[AUTO] 23:55 — disparando relatório diário + mercados 24h")
            enviar_relatorio_diario()
            msg_mercados = enviar_relatorio_mercados24h()
            if msg_mercados:
                send_telegram(msg_mercados)
    except Exception as e:
        print(f"[AUTO] Erro auto-dispatch: {e}")
    print(f"Finalizado. Enviados: {total_env}")



if __name__ == "__main__":
    run()



