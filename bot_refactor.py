

def analisar_e_disparar(game, stats, p, m, sh, sa, odd_h, odd_a, sent_vistos):
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
    
    # MERCADOS
    
    # 1. OVER GOL INTERVALO (HT)
    if p == 1 and 15 <= m <= 27:
        if sh == 0 and sa == 0 and red_fav == 0:
            return "HT", "Over 0.5 Gols HT"

    # 2. OVER GOL PARTIDA (FT)
    if p == 2 and 55 <= m <= 75:
        if (fav_gols <= adv_gols) and (adv_gols - fav_gols <= 1) and red_fav == 0:
            total_gols = sh + sa
            return "OVERGOAL", f"Mais de {total_gols + 0.5} Gols"

    # 3. AMBAS MARCAM (BTTS)
    if p == 2 and 55 <= m <= 75:
        if (sh + sa == 1) and (fav_gols == 0 and adv_gols == 1) and red_fav == 0:
            return "BTTS", "Ambas Marcam"

    # 4. OVER 1.5 GOLS PARTIDA
    if p == 2 and 55 <= m <= 75:
        if (sh + sa == 1) and (fav_gols == 0 and adv_gols == 1) and red_fav == 0:
            return "OFT", "Mais de 1.5 Gols Partida"

    # 5. ESCANTEIO LIMITE HT
    if p == 1 and 28 <= m <= 38:
        if (fav_gols <= adv_gols) and (adv_gols - fav_gols <= 1) and red_fav == 0:
            return "CORNER_HT", "Escanteio Limite HT"

    # 6. ESCANTEIO LIMITE FT
    if p == 2 and 78 <= m <= 88:
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
    # Bzzoiro: game['league_name']
    # ESPN: game['league']
    liga = "Liga Não Identificada"
    
    if fonte == "apifootball":
        liga = game.get('league', {}).get('name', "Liga Não Identificada")
    elif fonte == "bzzoiro":
        liga = game.get('league_name', "Liga Não Identificada")
    elif fonte == "espn":
        liga = game.get('league', "Liga Não Identificada")
    
    # Se ainda estiver vazio, busca em campos genéricos que as APIs costumam usar
    if liga == "Liga Não Identificada":
        liga = game.get('league_name') or game.get('competition_name') or game.get('league') or "Liga Não Identificada"
        
    return liga
# ═══════════════════════════════════════════════════════════════════════════════
# BOT MÁQUINA DE GREENS / ZAPIA - VERSÃO ELITE 100% AUTOMÁTICA
# FONTES: ESPN PÚBLICA + BZZOIRO (TOKEN ATIVO) + APIFOOTBALL (V3 ATIVA)
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

# ESPN (principal — pública, sem chave, sem limite)
ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/soccer/{liga}/scoreboard"
ESPN_SUMMARY    = "https://site.api.espn.com/apis/site/v2/sports/soccer/all/summary"

# Mapeamento de fallback para slugs sem nome retornado pela ESPN
LIGA_NOMES = {
    "eng.1": "Premier League", "esp.1": "La Liga", "ger.1": "Bundesliga",
    "ita.1": "Serie A", "fra.1": "Ligue 1", "por.1": "Primeira Liga",
    "ned.1": "Eredivisie", "bel.1": "Pro League", "tur.1": "Süper Lig",
    "sco.1": "Scottish Premiership", "aut.1": "Bundesliga Áustria",
    "sui.1": "Super League Suíça", "den.1": "Superliga Dinamarca",
    "swe.1": "Allsvenskan", "nor.1": "Eliteserien", "gre.1": "Super League Grécia",
    "cze.1": "Czech First League", "pol.1": "Ekstraklasa",
    "uefa.champions": "UEFA Champions League", "uefa.europa": "UEFA Europa League",
    "uefa.europa_conf": "UEFA Conference League",
    "bra.1": "Brasileirão Série A", "bra.2": "Brasileirão Série B",
    "bra.3": "Brasileirão Série C", "bra.4": "Brasileirão Série D",
    "bra.camp.carioca": "Campeonato Carioca", "bra.camp.gaucho": "Campeonato Gaúcho",
    "bra.camp.mineiro": "Campeonato Mineiro",
    "arg.1": "Liga Profesional Argentina", "col.1": "Liga BetPlay Colombia",
    "chi.1": "Primera División Chile", "chi.2": "Segunda División Chile", "chi.copa_chile": "Copa Chile", "uru.1": "Primera División Uruguai",
    "ecu.1": "LigaPro Ecuador", "bol.1": "División Profesional Bolivia",
    "per.1": "Liga 1 Peru", "ven.1": "Primera División Venezuela",
    "par.1": "División Profesional Paraguay", "par.2": "División Intermedia Paraguay",
    "conmebol.libertadores": "Copa Libertadores",
    "conmebol.sudamericana": "Copa Sudamericana",
    "usa.1": "MLS", "usa.2": "USL Championship", "usa.usl.l1": "USL League One",
    "usa.usl.l2": "USL League Two", "usa.mlsnextpro": "MLS Next Pro",
    "mex.1": "Liga MX", "mex.2": "Liga de Expansión MX",
    "concacaf.champions": "CONCACAF Champions Cup",
    "jpn.1": "J1 League", "kor.1": "K League 1",
    "sau.1": "Saudi Pro League", "qat.1": "Qatar Stars League",
    "rsa.1": "Premier Soccer League", "egy.1": "Egyptian Premier League",
    "fifa.world": "FIFA World Cup", "fifa.worldq": "Eliminatórias Copa do Mundo",
    "uefa.euro.u19": "UEFA Euro Sub-19", "uefa.euro.u21": "UEFA Euro Sub-21",
    "fifa.world.u20": "FIFA Mundial Sub-20",
    "chn.1": "Chinese Super League", "ind.1": "Indian Super League",
    "mys.1": "Malaysian Super League", "tha.1": "Thai League 1",
    "idn.1": "Indonesian Super League", "aus.1": "Australian A-League",
    "isr.1": "Israeli Premier League", "rus.1": "Russian Premier League",
    "fin.1": "Finnish Veikkausliga", "fin.2": "Ykkonen Finlândia", "swe.2": "Swedish SuperEttan",
    "nor.2": "Norwegian 1. Division", "den.2": "Danish 1. Division",
    "nga.1": "Nigerian Professional League", "zim.1": "Premier Soccer League Zimbábue",
    "caf.champions": "CAF Champions League", "afc.champions": "AFC Champions League",
}
ESPN_LIGAS = [
    "afc.asian.cup",
    "afc.champions",
    "afc.cup",
    "afc.cup_qual",
    "afc.cupq",
    "afc.saff.championship",
    "afc.w.asian.cup",
    "aff.championship",
    "arg.1",
    "arg.2",
    "arg.3",
    "arg.4",
    "arg.copa",
    "arg.copa_de_la_superliga",
    "arg.supercopa",
    "arg.supercopa.internacional",
    "arg.trofeo_de_la_campeones",
    "aus.1",
    "aus.w.1",
    "aut.1",
    "bangabandhu.cup",
    "bel.1",
    "bel.promotion.relegation",
    "bol.1",
    "bol.copa",
    "bol.ply.rel",
    "bra.1",
    "bra.2",
    "bra.camp.paulista",
    "bra.camp.carioca",
    "bra.camp.gaucho",
    "bra.camp.mineiro",
    "bra.copa_do_brazil",
    "bra.supercopa_do_brazil",
    "caf.champions",
    "caf.championship",
    "caf.championship_qual",
    "caf.confed",
    "caf.cosafa",
    "caf.nations",
    "caf.nations_qual",
    "caf.w.nations",
    "campeones.cup",
    "can.w.nsl",
    "chi.1",
    "chi.2",
    "chi.copa_chile",
    "chi.1.promotion.relegation",
    "chi.copa_chi",
    "chi.super_cup",
    "chn.1",
    "chn.1.promotion.relegation",
    "club.friendly",
    "col.1",
    "col.copa",
    "col.superliga",
    "concacaf.central.american.cup",
    "concacaf.champions",
    "concacaf.champions_cup",
    "concacaf.confederations_playoff",
    "concacaf.gold",
    "concacaf.gold_qual",
    "concacaf.leagues.cup",
    "concacaf.nations.league",
    "concacaf.u23",
    "concacaf.w.champions_cup",
    "concacaf.w.gold",
    "concacaf.womens.championship",
    "conmebol.america",
    "conmebol.america.femenina",
    "conmebol.libertadores",
    "conmebol.recopa",
    "conmebol.sudamericana",
    "crc.1",
    "den.1",
    "ecu.1",
    "eng.1",
    "eng.2",
    "eng.3",
    "eng.4",
    "eng.5",
    "eng.charity",
    "eng.fa",
    "eng.league_cup",
    "eng.trophy",
    "eng.w.1",
    "eng.w.fa",
    "eng.w.league_cup",
    "eng.w.promotion.relegation",
    "esp.1",
    "esp.2",
    "esp.copa_de_la_reina",
    "esp.copa_del_rey",
    "esp.joan_gamper",
    "esp.super_cup",
    "esp.w.1",
    "fifa.concacaf.olympicsq",
    "fifa.conmebol.olympicsq",
    "fifa.cwc",
    "fifa.friendly",
    "fifa.friendly.w",
    "fifa.friendly_u21",
    "fifa.intercontinental.cup",
    "fifa.intercontinental_cup",
    "fifa.olympics",
    "fifa.shebelieves",
    "fifa.w.champions_cup",
    "fifa.w.concacaf.olympicsq",
    "fifa.w.olympics",
    "fifa.wcq.ply",
    "fifa.world",
    "fifa.world.u17",
    "fifa.world.u20",
    "fifa.worldq.afc",
    "fifa.worldq.caf",
    "fifa.worldq.concacaf",
    "fifa.worldq.conmebol",
    "fifa.worldq.ofc",
    "fifa.worldq.uefa",
    "fifa.wwc",
    "fifa.wwcq.ply",
    "fifa.wworld.u17",
    "fifa.wworldq.uefa",
    "fra.1",
    "fra.1.promotion.relegation",
    "fra.2",
    "fra.coupe_de_france",
    "fra.super_cup",
    "fra.w.1",
    "friendly.emirates_cup",
    "ger.1",
    "ger.2",
    "ger.2.promotion.relegation",
    "ger.dfb_pokal",
    "ger.playoff.relegation",
    "ger.super_cup",
    "global.arnold.clark_cup",
    "global.club_challenge",
    "global.finalissima",
    "global.gulf_cup",
    "global.pinatar_cup",
    "global.toulon",
    "global.u20.intercontinental_cup",
    "global.w.finalissima",
    "gre.1",
    "gua.1",
    "hon.1",
    "ind.1",
    "ind.2",
    "ita.1",
    "ita.2",
    "ita.coppa_italia",
    "ita.super_cup",
    "jpn.1",
    "jpn.world_challenge",
    "ksa.1",
    "ksa.kings.cup",
    "mex.1",
    "mex.2",
    "mex.campeon",
    "ned.1",
    "ned.2",
    "ned.3.promotion.relegation",
    "ned.cup",
    "ned.playoff.relegation",
    "ned.supercup",
    "ned.w.1",
    "ned.w.knvb_cup",
    "nonfifa",
    "nor.1",
    "nor.1.promotion.relegation",
    "par.1",
    "par.2",
    "par.1.supercopa",
    "per.1",
    "por.1",
    "por.1.promotion.relegation",
    "por.taca.portugal",
    "rsa.1",
    "rus.1",
    "rus.1.promotion.relegation",
    "sco.1",
    "sco.1.promotion.relegation",
    "sco.2",
    "sco.2.promotion.relegation",
    "sco.challenge",
    "sco.cis",
    "sco.tennents",
    "slv.1",
    "swe.1",
    "swe.1.promotion.relegation",
    "tur.1",
    "uefa.champions",
    "uefa.champions_qual",
    "uefa.euro",
    "uefa.euro.u19",
    "uefa.euro_u21",
    "uefa.euro_u21_qual",
    "uefa.europa",
    "uefa.europa.conf",
    "uefa.europa.conf_qual",
    "uefa.europa_qual",
    "uefa.euroq",
    "uefa.nations",
    "uefa.super_cup",
    "uefa.w.europa",
    "uefa.w.nations",
    "uefa.wchampions",
    "uefa.wchampions_qual",
    "uefa.weuro",
    "uru.1",
    "uru.2",
    "usa.1",
    "usa.ncaa.m.1",
    "usa.ncaa.w.1",
    "usa.nwsl",
    "usa.nwsl.cup",
    "usa.open",
    "usa.usl.1",
    "usa.usl.l1",
    "usa.usl.l1.cup",
    "usa.usl.l2",
    "usa.mlsnextpro",
    "usa.w.usl.1",
    "ven.1",
]

# RapidAPI (fallback de lista)
RAPIDAPI_URL     = "https://free-api-live-football-data.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  os.getenv("APIFOOTBALL_KEY", ""),
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}



# URLs Oficiais das APIs (Conforme Documentação)
BZZOIRO_URL = "https://sports.bzzoiro.com"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
BZZOIRO_TOKEN = os.getenv("BZZOIRO_TOKEN")
BZZOIRO_URL = "https://sports.bzzoiro.com"



# URLs Oficiais das APIs (Conforme Documentação)
BZZOIRO_URL = "https://sports.bzzoiro.com"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
BZZOIRO_TOKEN = os.getenv("BZZOIRO_TOKEN")
BZZOIRO_URL = "https://sports.bzzoiro.com"



# URLs Oficiais das APIs (Conforme Documentação)
BZZOIRO_URL = "https://sports.bzzoiro.com"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"

# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
BZZOIRO_TOKEN = os.getenv("BZZOIRO_TOKEN")
BZZOIRO_URL = "https://sports.bzzoiro.com"

# ═══════════════+++
# TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg, botoes=True, reply_to=None, marca=None, home="", away="", odd_b365_val=None, odd_bano_val=None):
    url_send = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if botoes:
            import urllib.parse
            query = urllib.parse.quote(f"{home} vs {away}") if home and away else ""
            bet365_url   = "https://www.bet365.bet.br/#/AX/"
            paripesa_url = "https://paripesa.com/en/live/football/"
            # Constrói texto dos botões exatamente como na imagem
            txt_b365 = "🟣BET365🟣"
            txt_paripesa = "🔵PARIPESA🔵"
            payload["reply_markup"] = json.dumps({"inline_keyboard": [[
                {"text": txt_b365, "url": bet365_url},
                {"text": txt_paripesa, "url": paripesa_url}
            ]]})
        try:
            r = requests.post(url_send, json=payload, timeout=10)
            mid = r.json().get("result", {}).get("message_id")
            if mid: last_mid = mid
        except:
            pass
    return last_mid

# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVOS LOCAIS
# ═══════════════════════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GH_PAT", "")
GITHUB_REPO  = os.environ.get("GITHUB_REPOSITORY", "cleubianodasilva-png/boot-ia-inteligente-bot")
SENT_API_PATH        = "sent_live_signals.json"
RESULTADO_API_PATH   = "resultados.json"
PERFORMANCE_API_PATH = "performance.json"

def _github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

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

def salvar_resultado(resultado):
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    registros = _load_resultados_github()
    registros.append({"data": hoje, "resultado": resultado, "timestamp": datetime.now(BRT).isoformat()})
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
    if send_telegram(msg, botoes=False):
        sent_ctrl.add(hoje_key)
        save_sent(sent_ctrl)
        print(f"[Relatório] Enviado ({hoje_key})")

# ─── Performance por Mercado ────────────────────────────────────────────────────
MAPA_MERCADO = {
    "HT": "🔥 Over 0.5 Gols HT",
    "LIMITEHT": "🔥 Over Gol Limite HT",
    "BTTS": "⚽ BTTS",
    "OFT": "⚽ Over 1.5 FT",
    "OVERGOAL": "⚽ Over Gol FT",
    "CORNER_HT": "⛳️ Escanteio Limite HT",
    "CORNER_FT": "⛳️ Escanteio Limite FT"
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
    linhas = []
    for cod, info in dados.items():
        nome = info["nome"]
        g = info["green"]
        r = info["red"]
        t = info["total"]
        pct = info["pct"]
        valido = info["valido"]
        barra = ""
        if t > 0:
            g_pct = int(g / t * 10)
            barra = "🟢" * g_pct + "🔴" * (10 - g_pct)
        status = "✅" if valido else "⏳"
        linhas.append(
            f"{nome}\n"
            f"   {status} Total: {t} | 🟢 {g} | 🔴 {r}\n"
            f"   🎯 Acerto: <b>{pct:.1f}%</b>\n"
            f"   {barra}"
        )
    total_g = sum(d["green"] for d in dados.values())
    total_r = sum(d["red"] for d in dados.values())
    total_t = total_g + total_r
    total_pct = (total_g / total_t * 100) if total_t > 0 else 0

    msg = (
        f"{sep}\n"
        f"📊<b>RELATÓRIO DE PERFORMANCE</b>📊\n"
        f"{sep}\n"
        f"{chr(10).join(linhas)}\n"
        f"{sep}\n"
        f"📌 <b>GERAL: {total_t} sinais | 🟢 {total_g} | 🔴 {total_r} | {total_pct:.1f}%</b>\n"
        f"{sep}\n"
        f"<b>Regras de Validação:</b>\n"
        f"✅ Mínimo 1000 entradas + ≥70% acerto = Mercado <b>VÁLIDO</b>\n"
        f"⏳ Ainda não atingiu os critérios\n"
        f"{sep}"
    )
    return msg

def enviar_relatorio_performance():
    """Envia relatório de performance para o Telegram."""
    msg = gerar_layout_performance()
    if send_telegram(msg, botoes=False):
        print("[PERFORMANCE] Relatório enviado")

# ═══════════════════════════════════════════════════════════════════════════════
# API 1 — ESPN: lista de jogos ao vivo em TODAS as ligas
# ═══════════════════════════════════════════════════════════════════════════════
def _fetch_liga(liga_slug):
    """Busca jogos ao vivo de uma liga ESPN. Retorna lista de jogos."""
    resultado = []
    try:
        url  = ESPN_SCOREBOARD.format(liga=liga_slug)
        r    = requests.get(url, timeout=8)
        if r.status_code != 200:
            return resultado
        data       = r.json()
        ligas_data = data.get("leagues", [])
        liga_nome  = ligas_data[0].get("name", "") if ligas_data else ""
        if not liga_nome or liga_nome.lower() in ("all", liga_slug):
            liga_nome = LIGA_NOMES.get(liga_slug, liga_slug)
        events = data.get("events", [])
        for e in events:
            try:
                eid  = e.get("id", "")
                comp   = e.get("competitions", [{}])[0]
                status = comp.get("status", {}).get("type", {})
                state  = status.get("state", "")
                minuto_raw = comp.get("status", {}).get("displayClock", "0")
                try:
                    minuto = int(minuto_raw.replace("'","").split("+")[0].split(":")[0])
                except:
                    clock = comp.get("status", {}).get("clock", 0)
                    minuto = int(float(clock) // 60) if clock else 0

                if state == "post":
                    # Ignora jogos adiados, cancelados ou suspensos
                    short_detail = comp.get("status", {}).get("type", {}).get("shortDetail", "").lower()
                    type_name    = comp.get("status", {}).get("type", {}).get("name", "").lower()
                    if any(x in short_detail or x in type_name for x in
                           ["postponed", "canceled", "cancelled", "suspended", "abandoned", "postp"]):
                        continue
                    date_str = e.get("date", "")
                    if date_str:
                        try:
                            from datetime import timezone as _tz
                            dt_jogo = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            agora   = datetime.now(_tz.utc)
                            diff    = (agora - dt_jogo).total_seconds()
                            # diff deve ser positivo (jogo no passado) e dentro do tempo
                            if 0 <= diff <= (90 + 15) * 60:
                                minuto = 85
                                state  = "in"
                            else:
                                continue
                        except:
                            continue
                    else:
                        continue
                if state not in ("in",):
                    continue
                period = comp.get("status", {}).get("period", 1)
                if not period or period == 0:
                    period = 2 if minuto > 45 else 1
                teams  = comp.get("competitors", [])
                if len(teams) < 2:
                    continue
                home_t = teams[0]
                away_t = teams[1]
                sh     = int(home_t.get("score", 0) or 0)
                sa     = int(away_t.get("score", 0) or 0)
                home   = home_t.get("team", {}).get("displayName", "")
                away   = away_t.get("team", {}).get("displayName", "")
                liga   = liga_nome if liga_nome and liga_nome.lower() not in ("all", liga_slug.lower()) else LIGA_NOMES.get(liga_slug, liga_slug)
                resultado.append({
                    "fid": eid, "home": home, "away": away,
                    "sh": sh, "sa": sa, "minuto": minuto,
                    "period": period, "liga": liga, "liga_slug": liga_slug, "source": "espn"
                })
            except:
                continue
    except:
        pass
    return resultado


def get_jogos_espn(fids_existentes=None):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    if fids_existentes is None: fids_existentes = set()
    jogos  = []
    vistos = set(fids_existentes)
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_fetch_liga, slug): slug for slug in ESPN_LIGAS}
        for future in as_completed(futures):
            for j in future.result():
                if j["fid"] not in vistos:
                    vistos.add(j["fid"])
                    jogos.append(j)
    print(f"[ESPN] {len(jogos)} jogos novos (excluindo {len(fids_existentes)} já cobertos)")
    return jogos


# ═══════════════════════════════════════════════════════════════════════════════
# API 1B — apifootball: jogos ao vivo (preenche o que a ESPN não cobre)
# ═══════════════════════════════════════════════════════════════════════════════
def get_jogos_apifootball(fids_espn):
    """Busca todos os jogos ao vivo na apifootball e retorna os que ESPN não tem."""
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
                    # Pula se ESPN já tem
                    if fid in fids_espn:
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
                stats["posse_h"], stats["posse_a"] = int(h_val), int(a_val)
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
                stats["posse_h"], stats["posse_a"] = int(h_val), int(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}

def get_stats_bzzoiro(fid_raw, home, away):
    try:
        headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
        r = requests.get(f"{BZZOIRO_URL}/api/v2/events/{fid_raw}/stats/", headers=headers, timeout=10)
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


def get_jogos_bzzoiro(fids_existentes):
    try:
        headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
        r = requests.get(BZZOIRO_URL + "/api/v2/events/live/", headers=headers, timeout=15)
        data = r.json()
        results = data.get("events", [])
        jogos = []
        for ev in results:
            fid = "bzz_" + str(ev.get("id", ""))
            if fid in fids_existentes: continue
            sh, sa = int(ev.get("home_score") or 0), int(ev.get("away_score") or 0)
            minuto = ev.get("current_minute") or 0
            if not isinstance(minuto, int):
                try: minuto = int(str(minuto).split("'")[0])
                except: minuto = 0
            # Bzzoiro retorna league_name diretamente (league field pode ser None)
            liga_nome = ev.get("league_name", "") or ""
            if not liga_nome:
                liga = ev.get("league", {}) or {}
                liga_nome = liga.get("name", "Desconhecida") if isinstance(liga, dict) else str(liga)
            p_raw = str(ev.get("period", "") or "")
            period = 1 if "1" in p_raw or minuto <= 45 else 2
            jogos.append({
                "fid": fid, "fid_raw": str(ev.get("id", "")),
                "home": ev.get("home_team", ""), "away": ev.get("away_team", ""),
                "sh": sh, "sa": sa, "minuto": minuto,
                "period": period, "liga": liga_nome, "source": "bzzoiro"
            })
        print(f"[Bzzoiro] {len(jogos)} novos jogos")
        return jogos
    except Exception as e:
        print(f"[Bzzoiro ERRO] {e}")
        return []

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
                stats["posse_h"], stats["posse_a"] = int(h_val), int(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}

def get_stats_bzzoiro(fid_raw, home, away):
    try:
        headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
        r = requests.get(f"{BZZOIRO_URL}/api/v2/events/{fid_raw}/stats/", headers=headers, timeout=10)
        data = r.json()
        raw_stats = data.get("stats", {})
        stats = {}
        any_nonzero = False
        for side, key in [("home", "h"), ("away", "a")]:
            side_data = raw_stats.get(side, {})
            val = int(side_data.get("total_shots", 0) or 0)
            stats[f"chutes_tot_{key}"] = val
            if val > 0: any_nonzero = True
            val = int(side_data.get("shots_on_target", 0) or 0)
            stats[f"chutes_gol_{key}"] = val
            if val > 0: any_nonzero = True
            val = int(side_data.get("corner_kicks", 0) or 0)
            stats[f"escanteios_{key}"] = val
            if val > 0: any_nonzero = True
            val = int(side_data.get("dangerous_attack", 0) or 0)
            stats[f"ataques_perigosos_{key}"] = val
            if val > 0: any_nonzero = True
            val = int(side_data.get("ball_possession", 0) or 0)
            stats[f"posse_{key}"] = val
            if val > 0: any_nonzero = True
            cards = side_data.get("cards", {})
            if isinstance(cards, dict):
                stats[f"red_cards_{key}"] = int(cards.get("red", 0) or 0)
        # Se TUDO é zero, o ID não existe no Bzzoiro → retorna vazio pra ativar fallback
        if not any_nonzero:
            return {}
        return stats
    except: return {}

def get_stats_bzzoiro_by_name(home, away):
    """Fallback: busca stats no Bzzoiro pelo nome dos times."""
    import unicodedata
    def norm(s):
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()
    try:
        headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
        r = requests.get(BZZOIRO_URL + "/api/v2/events/live/", headers=headers, timeout=15)
        data = r.json()
        events = data.get("events", [])
        h_busca = norm(home)
        a_busca = norm(away)
        for ev in events:
            h_nome = norm(ev.get("home_team", ""))
            a_nome = norm(ev.get("away_team", ""))
            if (h_busca in h_nome or h_nome in h_busca) and (a_busca in a_nome or a_nome in a_busca):
                eid = ev.get("id")
                rs = requests.get(BZZOIRO_URL + f"/api/v2/events/{eid}/stats/", headers=headers, timeout=10)
                sd = rs.json()
                raw_stats = sd.get("stats", {})
                stats = {}
                for side_label, side_key in [("home", "h"), ("away", "a")]:
                    side_data = raw_stats.get(side_label, {})
                    stats[f"chutes_tot_{side_key}"] = int(side_data.get("total_shots", 0) or 0)
                    stats[f"chutes_gol_{side_key}"] = int(side_data.get("shots_on_target", 0) or 0)
                    stats[f"escanteios_{side_key}"] = int(side_data.get("corner_kicks", 0) or 0)
                    stats[f"ataques_perigosos_{side_key}"] = int(side_data.get("dangerous_attack", 0) or 0)
                    stats[f"posse_{side_key}"] = int(side_data.get("ball_possession", 0) or 0)
                    cards = side_data.get("cards", {})
                    if isinstance(cards, dict):
                        stats[f"red_cards_{side_key}"] = int(cards.get("red", 0) or 0)
                if stats.get("chutes_tot_h", 0) > 0 or stats.get("escanteios_h", -1) >= 0:
                    print(f"[BZZ-NAME] Stats por nome OK: {ev.get('home_team')}x{ev.get('away_team')} | esc {stats.get('escanteios_h')}x{stats.get('escanteios_a')}")
                    return stats
        return {}
    except Exception as e:
        print(f"[BZZ-NAME] Erro: {e}")
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

def get_stats_espn(eid, home, away):
    """Busca estatísticas de um jogo via ESPN summary. Sem custo."""
    try:
        r    = requests.get(ESPN_SUMMARY, params={"event": eid}, timeout=10)
        data = r.json()
        stats = {}
        teams_data = data.get("boxscore", {}).get("teams", [])
        if not teams_data:
            return {}
        # Identifica home/away pelo campo homeAway dos competitors no header
        competitors = data.get("header", {}).get("competitions", [{}])[0].get("competitors", [])
        home_id = None
        away_id = None
        for c in competitors:
            if c.get("homeAway") == "home": home_id = str(c.get("team", {}).get("id", ""))
            if c.get("homeAway") == "away": away_id = str(c.get("team", {}).get("id", ""))
        for team_box in teams_data:
            tid  = str(team_box.get("team", {}).get("id", ""))
            if home_id and away_id:
                side = "h" if tid == home_id else "a"
            else:
                # fallback pelo nome se não tiver id
                tname = team_box.get("team", {}).get("displayName", "")
                side  = "h" if tname.lower() == home.lower() else "a"
            for s in team_box.get("statistics", []):
                label = s.get("label", "").lower()
                name  = s.get("name", "")
                val   = s.get("displayValue", "0")
                try: val_int = int(val)
                except: val_int = 0
                if "corner"  in label:
                    stats[f"escanteios_{side}"] = val_int
                    stats[f"corner_data_{side}"] = True
                if label == "shots":                     stats[f"chutes_tot_{side}"]      = val_int
                if "on goal" in label:                   stats[f"chutes_gol_{side}"]      = val_int
                if "red"     in label:                   stats[f"red_cards_{side}"]       = val_int
                if "possession" in label:
                    try: stats[f"posse_{side}"] = float(val)
                    except: stats[f"posse_{side}"] = 0.0
                if name == "accuratePasses":             stats[f"passes_precisos_{side}"] = val_int

        # Garante defaults
        for side in ["h", "a"]:
            for k in ["chutes_tot", "chutes_gol", "red_cards", "passes_precisos"]:
                stats.setdefault(f"{k}_{side}", 0)
            stats.setdefault(f"posse_{side}", 0.0)
        # Escanteios: -1 = sem dados (liga não suportada)
        stats.setdefault("escanteios_h", -1)
        stats.setdefault("escanteios_a", -1)

        stats["fav_side"] = "h" if stats.get("chutes_tot_h", 0) >= stats.get("chutes_tot_a", 0) else "a"
        print(f"[ESPN Stats] {home} x {away} | chutes: {stats.get('chutes_tot_h',0)}/{stats.get('chutes_tot_a',0)} | cantos: {stats.get('escanteios_h',0)}/{stats.get('escanteios_a',0)}")
        return stats
    except Exception as e:
        print(f"[ESPN Stats] Erro: {e}")
        return {}

# ═══════════════════════════════════════════════════════════════════════════════
# FALLBACK — apifootball: estatísticas (usado se ESPN falhar)
# ═══════════════════════════════════════════════════════════════════════════════
    for key in [APIFOOTBALL_COM_KEY]:
        try:
            r     = requests.get(f"{API_FOOTBALL_URL}/fixtures/statistics",
                                 params={"fixture": fid},
                                 headers={"x-apisports-key": key}, timeout=10)
            rjson = r.json()
            if (r.headers.get("x-ratelimit-requests-remaining") == "0"
                    or (isinstance(rjson.get("errors"), dict) and rjson.get("errors", {}).get("requests"))
                    or (isinstance(rjson.get("errors"), dict) and rjson.get("errors", {}).get("access"))):
                print(f"[apifootball] Chave {key[:8]}... indisponível")
                continue
            data = rjson.get("response", [])
            if not data: continue
            stats   = {}
            home_id = data[0]["team"]["id"]
            for team in data:
                side = "h" if team["team"]["id"] == home_id else "a"
                for s in team["statistics"]:
                    k   = s["type"].lower().replace(" ", "_")
                    val = s["value"] or 0
                    if k == "corner_kicks":  stats[f"escanteios_{side}"] = val
                    if k == "total_shots":   stats[f"chutes_tot_{side}"]  = val
                    if k == "shots_on_goal": stats[f"chutes_gol_{side}"]  = val
            r2     = requests.get(f"{API_FOOTBALL_URL}/fixtures/events",
                                  params={"fixture": fid},
                                  headers={"x-apisports-key": key}, timeout=10)
            events = r2.json().get("response", [])
            red_h, red_a = 0, 0
            for ev in events:
                if ev.get("type") == "Card" and "Red" in (ev.get("detail") or ""):
                    if ev.get("team", {}).get("id") == home_id: red_h += 1
                    else: red_a += 1
            stats["red_cards_h"], stats["red_cards_a"] = red_h, red_a
            stats["fav_side"] = "h" if stats.get("chutes_tot_h", 0) >= stats.get("chutes_tot_a", 0) else "a"
            print(f"[apifootball] Stats OK chave {key[:8]}...")
            return stats
        except:
            continue
    return {}

# ═══════════════════════════════════════════════════════════════════════════════
# API 3 — ODDS: favorito pela menor odd (ESPN moneyline ou The Odds API)
# ═══════════════════════════════════════════════════════════════════════════════
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
    """Retorna ('h'|'a', odd_h, odd_a) baseado na menor odd. Usa ESPN primeiro, depois Odds API."""
    # Tenta ESPN (grátis, sem cota)
    if fid and league:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
            r = requests.get(url, timeout=6)
            for ev in r.json().get("events", []):
                comp = ev.get("competitions", [{}])[0]
                ev_fid = str(comp.get("id", ""))
                if ev_fid != str(fid):
                    continue
                odds_list = comp.get("odds", [])
                for odd in odds_list:
                    if not odd:
                        continue
                    ml = odd.get("moneyline", {})
                    if ml:
                        # Prioridade: close (pre-game) > open > current (live)
                        def _get_ml(side):
                            for key in ("close", "open", "current"):
                                v = ml.get(side, {}).get(key, {}).get("odds")
                                if v:
                                    return v
                            return 99
                        odd_h = _moneyline_to_decimal(_get_ml("home"))
                        odd_a = _moneyline_to_decimal(_get_ml("away"))
                        if odd_h < 90 and odd_a < 90:
                            fav = "h" if odd_h <= odd_a else "a"
                            print(f"[ODDS-ESPN] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                            return (fav, odd_h, odd_a)
        except Exception as e:
            print(f"[ODDS-ESPN] Erro: {e}")

    # Fallback 2: Bzzoiro odds (quando fid for da Bzzoiro)
    if fid and str(fid).startswith("bzz_"):
        try:
            fid_raw = str(fid).replace("bzz_", "")
            headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
            r = requests.get(BZZOIRO_URL + f"/api/v2/events/{fid_raw}/odds/", headers=headers, timeout=8)
            if r.status_code == 200:
                bz = r.json().get("odds", {})
                odd_h = float(bz.get("home_win", 0) or 0)
                odd_a = float(bz.get("away_win", 0) or 0)
                if odd_h > 1 and odd_a > 1:
                    fav = "h" if odd_h <= odd_a else "a"
                    print(f"[ODDS-BZZ] {home} x {away} | Casa:{odd_h} Fora:{odd_a} -> Fav:{fav}")
                    return (fav, odd_h, odd_a)
        except Exception as e:
            print(f"[ODDS-BZZ] Erro: {e}")

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
def get_odd_favorito_num(home, away, fid=None, league=None):
    """Retorna a odd decimal do favorito (numero). Usa ESPN primeiro, depois Odds API."""
    if fid and league:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
            r = requests.get(url, timeout=6)
            for ev in r.json().get("events", []):
                comp = ev.get("competitions", [{}])[0]
                if str(comp.get("id", "")) != str(fid):
                    continue
                for odd in comp.get("odds", []):
                    if not odd:
                        continue
                    ml = odd.get("moneyline", {})
                    if ml:
                        def _get_ml(side):
                            for key in ("close", "open", "current"):
                                v = ml.get(side, {}).get(key, {}).get("odds")
                                if v:
                                    return v
                            return 99
                        odd_h = _moneyline_to_decimal(_get_ml("home"))
                        odd_a = _moneyline_to_decimal(_get_ml("away"))
                        if odd_h < 90 and odd_a < 90:
                            return min(odd_h, odd_a)
        except:
            pass
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

    if mercado == "LIMITEHT":
        if jogo_aberto and total_chutes >= 8:
            return f"Jogo aberto com muitas finalizações e sem gols{vermelho}"
        if fav_perdendo and fav_chutes >= 6:
            return f"{fav_label} perdendo e pressionando no campo ofensivo{vermelho}"
        if fav_amassando:
            return f"{fav_label} amassando em busca do empate{vermelho}"
        if total_atq_perig >= 8:
            return f"Alta pressão ofensiva nos minutos finais do 1º tempo{vermelho}"
        return f"Pressão ofensiva para gol antes do intervalo{vermelho}"

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

def msg_universal(home, away, minuto, liga, n, mercado, entrada, placar, extra_val=None, cantos_atual=0, stats=None, sh=0, sa=0, fav_final="h", odd_h=None, odd_a=None, odd_b365=None, odd_bano=None):
    if "CORNER" in mercado or "ESCANTEIO" in mercado:
        linha = cantos_atual + 0.5
        entrada = f"Mais de {linha}🚩"

    # Adiciona ⚽ na entrada para mercados de gol
    if mercado in ("HT", "LIMITEHT", "BTTS", "OFT", "OVERGOAL"):
        entrada = str(entrada).rstrip() + "⚽️"
    
    titles = {
        "HT": "⚽️🔥OVER GOL INTERVALO🔥⚽️",
        "LIMITEHT": "⚽️🔥OVER GOL LIMITE HT🔥⚽️",
        "BTTS": "⚽️🔥AMBAS MARCAM🔥⚽️",
        "OFT": "⚽️🔥OVER 1.5 GOLS PARTIDA🔥⚽️",
        "OVERGOAL": "⚽️🔥OVER GOL PARTIDA🔥⚽️",
        "CORNER_HT": "🚩🔥ESCANTEIO ÁSIAT/LMT HT🔥🚩",
        "CORNER_FT": "🚩🔥ESCANTEIO ÁSIAT/LMT FT🔥🚩",
    }
    title = titles.get(mercado, f"🚩🔥{mercado}🔥🚩")
    
    if stats:
        chutes_h = stats.get("chutes_tot_h", 0)
        chutes_a = stats.get("chutes_tot_a", 0)
        alvo_h = stats.get("chutes_gol_h", 0)
        alvo_a = stats.get("chutes_gol_a", 0)
        cant_h = stats.get("escanteios_h", 0)
        cant_a = stats.get("escanteios_a", 0)
        atq_perig_h = stats.get("ataques_perigosos_h", 0)
        atq_perig_a = stats.get("ataques_perigosos_a", 0)
    else:
        chutes_h = 0
        chutes_a = 0
        alvo_h = 0
        alvo_a = 0
        cant_h = 0
        cant_a = 0
        atq_perig_h = 0
        atq_perig_a = 0

    sep = "━━━━━━━━━━━━━━━━━━━━"
    
    # --- ANALISE DINAMICA (APPM - Ataques Perigosos Por Minuto do TIME DOMINANTE) ---
    # Pressão e alerta baseados exclusivamente no time com MAIS ataques perigosos
    atq_dominante = max(atq_perig_h, atq_perig_a)
    if minuto > 0:
        appm_dominante = round(atq_dominante / minuto, 2)
    else:
        appm_dominante = 0

    # Alerta dinâmico baseado EXCLUSIVAMENTE no APPM do time dominante
    # Decide quem está pressionando mais
    if atq_perig_h > atq_perig_a:
        quem_pressiona = "do Mandante"
    elif atq_perig_a > atq_perig_h:
        quem_pressiona = "do Visitante"
    else:
        quem_pressiona = "de ambas equipes"

    if appm_dominante >= 2.0:
        alerta = "Partida pegando fogo."
    elif appm_dominante >= 1.2:
        alerta = "Partida com ritmo intenso."
    elif appm_dominante >= 0.7:
        alerta = f"Partida com bastante pressão {quem_pressiona}."
    elif appm_dominante >= 0.4:
        alerta = "Partida com ritmo moderado."
    else:
        alerta = "Partida com ritmo baixo."
        alerta = "Partida com ritmo ofensivo muito baixo 👇"

    if fav_final == "h":
        fav_nome = home
    elif fav_final == "a":
        fav_nome = away
    else:
        fav_nome = "—"

    # Mapeia mercado → campo da API

    msg = (
        sep + "\n"
        + "<b>" + title + "</b>\n"
        + sep + "\n"
        + "<b>⚽️ Placar:</b> <b>" + str(placar) + "</b>\n"
        + "<b>🌍 Liga:</b> <b>" + str(liga) + "</b>\n"
        + "📡 <b>" + str(home) + "</b> x <b>" + str(away) + "</b>\n"
        + "<b>👀 ODDs:</b> <b>Casa " + (f"{odd_h:.2f}" if odd_h else "—") + " / Fora " + (f"{odd_a:.2f}" if odd_a else "—") + "</b>\n"
        + "<b>⏰ Minuto:</b> <b>" + str(minuto) + "'</b>\n"
        + sep + "\n"
        + "📊 <b>Estatísticas ao Vivo da Partida:</b>\n"
        + "<b>🚀 Chutes Totais:</b> <b>" + str(chutes_h) + " | " + str(chutes_a) + "</b>\n"
        + "<b>🎯 Chutes No Alvo:</b> <b>" + str(alvo_h) + " | " + str(alvo_a) + "</b>\n"
        + "<b>⚔️ Ataques Perigosos:</b> <b>" + str(atq_perig_h) + " | " + str(atq_perig_a) + "</b>\n"
        + "<b>🚩 Escanteios:</b> <b>" + str(cant_h) + " | " + str(cant_a) + "</b>\n"
        + sep + "\n"
        + "<b>💡 Análise Técnica da Partida:</b>\n"
        + "<b>🎯 Favorito:</b> <b>" + str(fav_nome) + "</b>\n"
        + "<b>🔥 Pressão APPM:</b> <b>⚠️" + str(appm_dominante) + "⚠️</b>\n"
        + "<b>🚨 Alerta:</b> <b>" + alerta + "</b>\n"
        + sep + "\n"
        + "📌 Entrada: <b>" + str(entrada) + "</b>\n"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🟣BET365🟣", "url": "https://www.bet365.bet.br/#/AX/"},
                {"text": "🔵PARIPESA🔵", "url": "https://paripesa.com/en/live/football/"}
            ]
        ]
    }
    
    return msg, keyboard

def send_telegram(msg_data, marca="Zapia", home="H", away="A", odd_b365_val=None, odd_bano_val=None):
    text, keyboard = msg_data
    # ... logic to send text and reply_markup=keyboard ...

    try:
        eid     = str(sinal.get("fixture_id"))
        mercado = sinal.get("mercado")
        
        # 1. Busca via ESPN Summary
        r    = requests.get(ESPN_SUMMARY, params={"event": eid}, timeout=10)
        data = r.json()
        header = data.get("header", {})
        comps  = header.get("competitions", [])
        if not comps: return None
        comp   = comps[0]
        status = comp.get("status", {})
        state  = status.get("type", {}).get("state", "").lower()
        
        # Só audita se o jogo acabou ('post') ou se estamos checando HT e o jogo está no 2H ou post.
        is_final = (state == "post")
        is_2h    = (state == "in" and int(status.get("period", 0)) >= 2)
        
        if not (is_final or (mercado in ["HT", "LIMITEHT", "CORNER_HT"] and is_2h)):
            return None

        # Placar Final (ou atual se is_2h)
        gh, ga = 0, 0
        competitors = comp.get("competitors", [])
        for c in competitors:
            if c.get("homeAway") == "home": gh = int(c.get("score", 0) or 0)
            if c.get("homeAway") == "away": ga = int(c.get("score", 0) or 0)
        total_final = gh + ga

        # Placar HT (Extraído dos linescores)
        gh_ht, ga_ht = 0, 0
        for c in competitors:
            ls = c.get("linescores", [])
            if len(ls) > 0:
                val = int(ls[0].get("displayValue", 0) or 0)
                if c.get("homeAway") == "home": gh_ht = val
                else: ga_ht = val
        total_ht = gh_ht + ga_ht

        # Lógica por Mercado
        if mercado in ["HT", "LIMITEHT"]:
            return "green" if total_ht >= 1 else ("red" if (is_2h or is_final) else None)
        
        elif mercado == "BTTS":
            return "green" if (gh >= 1 and ga >= 1) else ("red" if is_final else None)
        
        elif mercado == "OFT":
            return "green" if total_final >= 2 else ("red" if is_final else None)
            
        elif mercado == "OVERGOAL":
            gols_entrada = sinal.get("extra_val", 0)
            return "green" if total_final > gols_entrada else ("red" if is_final else None)
            
        elif mercado in ["CORNER_HT", "CORNER_FT"]:
            stats = get_stats_espn(eid, sinal.get("home",""), sinal.get("away",""))
            c_final = stats.get("escanteios_h", 0) + stats.get("escanteios_a", 0)
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
            _HIST_CACHE[chave] = 0.0
            return 0.0

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
            _HIST_CACHE[chave] = 0.0
            return 0.0

        media = round(sum(todos_jogos) / len(todos_jogos), 1)
        _HIST_CACHE[chave] = media
        return media
    except:
        _HIST_CACHE[chave] = 0.0
        return 0.0

# ═══════════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def run():
    print("[Iniciando monitoramento — ESPN + apifootball + Odds API]")
    sent      = load_sent()
    total_env = 0
    # janela_id por hora — evita duplicata mesmo se Actions rodar 2x no mesmo minuto
    janela_id = datetime.now(BRT).strftime('%Y%m%d%H')

    # ─────────────────────────────────────────────────────────────
    # PASSO 1A: apifootball — 1ª fonte de jogos (mais completa)
    # ─────────────────────────────────────────────────────────────
    jogos_apif = get_jogos_apifootball_v3(set())
    fids_apif  = {j["fid"] for j in jogos_apif}

    # ─────────────────────────────────────────────────────────────
    # PASSO 1B: ESPN — 2ª fonte, complementa o que apifootball não cobriu
    # ─────────────────────────────────────────────────────────────
    jogos_espn = get_jogos_espn(fids_apif)

    # ─────────────────────────────────────────────────────────────
    # PASSO 1C: Bzzoiro — 3ª fonte, preenche o que faltar
    # ─────────────────────────────────────────────────────────────
    jogos_bzz = get_jogos_bzzoiro(fids_apif | {j["fid"] for j in jogos_espn})

    # Junta tudo na ordem: apifootball > ESPN > Bzzoiro
    jogos_live = jogos_apif + jogos_espn + jogos_bzz
    print(f"[Total] {len(jogos_live)} jogos ao vivo (apifootball={len(jogos_apif)} + ESPN={len(jogos_espn)} + bzzoiro={len(jogos_bzz)})")

    # PASSO 2: Filtra janelas alvo
    jogos_na_janela = filtrar_janelas(jogos_live)
    print(f"[Janela] {len(jogos_na_janela)} jogos nas janelas alvo")

    check_status_command(total_jogos_live=len(jogos_live), jogos_live=jogos_live, jogos_na_janela=jogos_na_janela)

    if not jogos_na_janela:
        print("[OK] Nenhum jogo na janela — aguardando próximo ciclo")
        save_sent(sent)
        print("Finalizado. Enviados: 0")
        return

    # PASSO 3: Dedup por nome dos times (mesmo jogo de APIs diferentes)
    jogos_dedup = []
    vistos_jogos = {}
    for j in jogos_na_janela:
        # Normaliza pra mesma chave entre APIs
        hn_j = norm_nome_time(j["home"])
        an_j = norm_nome_time(j["away"])
        # Remove sufixos genéricos de nome de time (Riverhounds, United, City, etc.)
        hn_j = re.sub(r'\b(riverhounds|united|city|juniors|athletic|atlético|nacional|wanderers|rover|rovers|dynamo|galaxy|sporting|real|inter|internacional|deportivo|racing|club|instituto)\b', '', hn_j).strip()
        an_j = re.sub(r'\b(riverhounds|united|city|juniors|athletic|atlético|nacional|wanderers|rover|rovers|dynamo|galaxy|sporting|real|inter|internacional|deportivo|racing|club|instituto)\b', '', an_j).strip()
        chave = (hn_j, an_j)
        # Também tenta substring match: se um time contém o nome do outro
        chave_encontrada = None
        for v_chave in vistos_jogos:
            v_h, v_a = v_chave
            h_match = hn_j in v_h or v_h in hn_j
            a_match = an_j in v_a or v_a in an_j
            if h_match and a_match:
                chave_encontrada = v_chave
                break
        if chave_encontrada:
            existente = vistos_jogos[chave_encontrada]
            # Se a duplicata NÃO é apifootball e a existente É apifootball, mantém apifootball (com odds)
            if existente.get("source") == "apifootball":
                print(f"[DEDUP] mantendo apifootball com odds: {existente['home']} x {existente['away']} (ignorando {j.get('source','?')} - {j['home']} x {j['away']})")
            elif j.get("source") == "apifootball":
                vistos_jogos[chave_encontrada] = j
                idx = jogos_dedup.index(existente)
                jogos_dedup[idx] = j
                print(f"[DEDUP] substituido {existente['home']} x {existente['away']} ({existente.get('source','?')}) -> apifootball (com odds)")
            else:
                print(f"[DEDUP] ignorando duplicata de {j['home']} x {j['away']} ({j.get('source','?')})")
        elif chave not in vistos_jogos:
            vistos_jogos[chave] = j
            jogos_dedup.append(j)
        else:
            existente = vistos_jogos[chave]
            if existente.get("source") == "apifootball":
                print(f"[DEDUP] mantendo apifootball com odds: {existente['home']} x {existente['away']} (ignorando {j.get('source','?')})")
            elif j.get("source") == "apifootball":
                vistos_jogos[chave] = j
                idx = jogos_dedup.index(existente)
                jogos_dedup[idx] = j
                print(f"[DEDUP] substituido {existente['home']} x {existente['away']} ({existente.get('source','?')}) -> apifootball (com odds)")
            else:
                print(f"[DEDUP] ignorando duplicata de {j['home']} x {j['away']} ({j.get('source','?')})")
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
        stot   = sh + sa
        placar = f"{sh}x{sa}"

        print(f"[Analisando] {h} x {a} | {placar} | {m}min")

        # Stats FUSION: apifootball (principal) → ESPN → Bzzoiro (reservas)
        fid_raw = j.get("fid_raw", fid)
        stats_apif = {}
        try:
            sa_api = get_stats_apifootball_live(fid_raw)
            if isinstance(sa_api, dict): stats_apif = sa_api
        except: pass
        if not stats_apif:
            try:
                sa3 = get_stats_apifootball_v3(fid_raw)
                if isinstance(sa3, dict): stats_apif = sa3
            except: pass
        # Fallback: busca por nome dos times se o ID falhar (apifootball cobre 700+ ligas)
        if not stats_apif or not (stats_apif.get("escanteios_h", -1) >= 0 and stats_apif.get("escanteios_a", -1) >= 0):
            try:
                sa_name = get_stats_apifootball_by_name(h, a)
                if isinstance(sa_name, dict) and sa_name.get("escanteios_h", -1) >= 0:
                    stats_apif = sa_name
                    print(f"[APIF-NAME] Stats por nome OK: esc {sa_name.get('escanteios_h')}x{sa_name.get('escanteios_a')}")
            except: pass
        stats_espn = {}
        try:
            # ESPN stats: só funciona com ID ESPN limpo (sem prefixo)
            if j.get("source") == "espn" and fid_raw:
                eid_clean = fid_raw  # ESPN raw ID já é o event ID
                se = get_stats_espn(eid_clean, h, a)
                if isinstance(se, dict): stats_espn = se
        except: pass
        stats_bzz = {}
        try:
            sb = get_stats_bzzoiro(fid_raw, h, a)
            if isinstance(sb, dict): stats_bzz = sb
        except: pass
        # Fallback Bzzoiro por nome (quando o ID da apifootball nao funciona no Bzzoiro)
        # Para ligas normais: se Bzzoiro tem só cantos (sem chutes/ataques), precisa de fallback
        if "Club Friendlies" in liga:
            precisa_fallback = not stats_bzz or not (stats_bzz.get("chutes_tot_h", 0) > 0 or stats_bzz.get("escanteios_h", -1) >= 0)
        else:
            precisa_fallback = not stats_bzz or not (stats_bzz.get("chutes_tot_h", 0) > 0 or stats_bzz.get("chutes_tot_a", 0) > 0 or
                                                      stats_bzz.get("ataques_perigosos_h", 0) > 0 or stats_bzz.get("ataques_perigosos_a", 0) > 0 or
                                                      stats_bzz.get("chutes_gol_h", 0) > 0 or stats_bzz.get("chutes_gol_a", 0) > 0)
        if precisa_fallback:
            try:
                sb_name = get_stats_bzzoiro_by_name(h, a)
                if isinstance(sb_name, dict):
                    # Club Friendlies: sempre confiável, aceita dados normalmente
                    if "Club Friendlies" in liga:
                        stats_bzz = sb_name
                        print(f"[BZZ-NAME] Friendlies aceito: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')}")
                    else:
                        # Demais ligas: só aceita fallback se tiver scout real (chutes, ataques ou chutes no gol)
                        if (sb_name.get("chutes_tot_h", 0) > 0 or sb_name.get("chutes_tot_a", 0) > 0 or
                            sb_name.get("ataques_perigosos_h", 0) > 0 or sb_name.get("ataques_perigosos_a", 0) > 0 or
                            sb_name.get("chutes_gol_h", 0) > 0 or sb_name.get("chutes_gol_a", 0) > 0):
                            stats_bzz = sb_name
                            print(f"[BZZ-NAME] Stats via nome OK: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')} | chutes {sb_name.get('chutes_tot_h')}x{sb_name.get('chutes_tot_a')}")
            except: pass

        stats = {}
        for src_nome, src in [("apifootball", stats_apif), ("ESPN", stats_espn), ("Bzzoiro", stats_bzz)]:
            for campo in ["chutes_tot_h","chutes_tot_a","chutes_gol_h","chutes_gol_a","escanteios_h","escanteios_a","red_cards_h","red_cards_a","posse_h","posse_a","ataques_h","ataques_a","ataques_perigosos_h","ataques_perigosos_a"]:
                if campo not in src:
                    continue
                val = src[campo]
                if not isinstance(val, (int,float)) or val < 0:
                    continue
                current = stats.get(campo, -1)
                if current == -1:
                    stats[campo] = val
                    stats["_fonte_"+campo] = src_nome
                elif current == 0 and val > 0:
                    stats[campo] = val
                    stats["_fonte_"+campo] = src_nome
        for k in ["chutes_tot_h","chutes_tot_a","chutes_gol_h","chutes_gol_a"]:
            stats.setdefault(k, 0)
        for k in ["escanteios_h","escanteios_a"]:
            stats.setdefault(k, -1)
        for k in ["red_cards_h","red_cards_a"]:
            stats.setdefault(k, 0)
        print(f"[STATS-FUSION] {h} x {a} | chutes: {stats.get('chutes_tot_h',0)}/{stats.get('chutes_tot_a',0)} | cantos: {stats.get('escanteios_h',-1)}/{stats.get('escanteios_a',-1)}")

        # Verifica se tem dados reais — sem stats E sem odds, pula o jogo
        tem_stats = stats and (
            stats.get("chutes_tot_h", 0) > 0 or
            stats.get("chutes_tot_a", 0) > 0 or
            stats.get("escanteios_h", -1) >= 0 or
            stats.get("escanteios_a", -1) >= 0
        )
        if not tem_stats:
            print(f"[SKIP] {h} x {a} — sem stats em nenhuma API, pulando jogo")
            continue

        # Favorito: primeiro usa odds inline da apifootball (ja veio na coleta), depois ESPN, depois tenta de novo
        odd_h = j.get("odd_h")
        odd_a = j.get("odd_a")
        fav_por_odds = False
        if odd_h and odd_a and odd_h > 1 and odd_a > 1:
            fav_final = "h" if odd_h <= odd_a else "a"
            fav_por_odds = True
            print(f"[ODDS-INLINE] {h} x {a} — odd Casa:{odd_h:.2f} Fora:{odd_a:.2f} (apifootball)")
        # Fallback: ESPN/Odds API
        if not fav_por_odds:
            fav_final, odd_h, odd_a = get_favorito_odds(h, a, fid=fid, league=j.get("liga_slug", j.get("liga", "")))
            fav_por_odds = fav_final in ("h", "a")
        # Fallback: apifootball por match_id (pra jogos que ESPN nao cobriu)
        if not fav_por_odds:
            try:
                r_odd = requests.get("https://apiv3.apifootball.com/",
                                 params={"action": "get_odds", "match_id": fid_raw, "APIkey": APIFOOTBALL_COM_KEY}, timeout=8)
                odds_data = r_odd.json()
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
                    odd_h, odd_a = float(odd_ml.get("odd_1", 0)), float(odd_ml.get("odd_2", 0))
                    if odd_h > 1 and odd_a > 1:
                        fav_final = "h" if odd_h <= odd_a else "a"
                        fav_por_odds = True
            except: pass

        # Fallback odds via Bzzoiro (com auth e campos corretos)
        if not fav_por_odds:
            try:
                headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
                r = requests.get(f"https://sports.bzzoiro.com/api/v2/events/{fid_raw}/odds/", headers=headers, timeout=8)
                bz = r.json().get("odds", {})
                odd_h = float(bz.get("home_win", 0) or 0)
                odd_a = float(bz.get("away_win", 0) or 0)
                if odd_h > 1 and odd_a > 1:
                    fav_final = "h" if odd_h <= odd_a else "a"
                    fav_por_odds = True
            except:
                pass

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

        # APPM — Ataques Perigosos Por Minuto (filtro geral anti-jogo morno)
        _aph_val = stats.get("ataques_perigosos_h", 0) if stats else 0
        _apa_val = stats.get("ataques_perigosos_a", 0) if stats else 0
        _apt_val = _aph_val + _apa_val
        _appm_total = round(_apt_val / m, 2) if m > 0 else 0
        _appm_h = round(_aph_val / m, 2) if m > 0 else 0
        _appm_a = round(_apa_val / m, 2) if m > 0 else 0
        # APPM seletiva por repositório
        # maquina-de-greens-bot (Grupo GITHUB): APPM ativo
        #   - OVER GOLS: casa ≥ 0.8 OU fora ≥ 0.8 OU total ≥ 1.5
        #   - ESCANTEIOS: casa ≥ 0.7 OU fora ≥ 0.7 OU total ≥ 1.4
        # boot-ia-inteligente-bot (Grupo ZAPIA): livre
        _repo_atual = os.environ.get("GITHUB_REPOSITORY", "")
        if "maquina-de-greens" in _repo_atual:
            appm_valido   = _appm_h >= 0.7 or _appm_a >= 0.7 or _appm_total >= 1.4  # escanteios
            appm_gols_ok  = _appm_h >= 0.8 or _appm_a >= 0.8 or _appm_total >= 1.5  # over gols
            if not appm_valido:
                print(f"[APPM-BLOQUEADO] {h} x {a} — APPM casa={_appm_h} fora={_appm_a} total={_appm_total} (mín: 0.7/time ou 1.4 total)")
            if not appm_gols_ok:
                print(f"[APPM-GOLS-BLOQUEADO] {h} x {a} — APPM casa={_appm_h} fora={_appm_a} total={_appm_total} (mín: 0.8/time ou 1.5 total)")
        else:
            appm_valido   = True
            appm_gols_ok  = True

        # HISTÓRICO — Média de gols por partida (jogo todo) ≥ 2.0
        # Req. para: Over Gol HT, Over Gol FT e BTTS
        home_id = j.get("home_id", "")
        away_id = j.get("away_id", "")
        media_hist = 0.0
        if home_id and away_id:
            media_hist = get_media_gols_historica(home_id, away_id)
        hist_ok = media_hist < 0 or media_hist >= 2.0  # -1 = sem dados históricos (não bloqueia)
        if not hist_ok:
            print(f"[HIST-BLOQUEADO] {h} x {a} — média {media_hist:.1f} < 2.0, pulando mercados de gol")

        # MERCADO 1: OVER 0.5 HT (15-27 min, 0x0, favorito empatando, sem vermelho do fav, média hist ≥ 2.0)
        if p == 1 and 15 <= m <= 27:
            if not (sh == 0 and sa == 0):
                print(f"[DIAG-HT-BARRA] {h} x {a} — placar não é 0x0 ({placar}), pulando")
            elif not fav_empatando:
                print(f"[DIAG-HT-BARRA] {h} x {a} — favorito não empatando (fav={fav_final}, gols_fav={fav_gols} adv={adv_gols}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-HT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_gols_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not hist_ok:
                print(f"[DIAG-HT-BARRA] {h} x {a} — média histórica {media_hist:.1f} < 2.0, pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_ht_{hoje}"
                if key in sent:
                    print(f"[DIAG-HT-DUP] {h} x {a} — já enviado hoje ({key}), pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 3, "HT", "Over 0.5", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "HT", h, a, mid)

        # MERCADO 1B: OVER GOL LIMITE HT (15-27 min, 0x0, odd fav ≤ 1.80, prob 1.5 FT ≥ 60%, prob 0.5 HT ≥ 50%, APPM casa/fora ≥ 0.8)
        if p == 1 and 15 <= m <= 27 and sh == 0 and sa == 0 and red_fav == 0:
            odd_fav_num = get_odd_favorito_num(h, a, fid=fid, league=j.get("liga_slug", j.get("liga", "")))
            
            # APPM: ataques perigosos por minuto (casa OU fora ≥ 0.8)
            appm_casa = _appm_h
            appm_fora = _appm_a
            appm_ht_ok = appm_casa >= 0.8 or appm_fora >= 0.8
            
            # Cálculo de probabilidades via chutes (se tiver)
            chutes_tot_total = (stats.get("chutes_tot_h", 0) + stats.get("chutes_tot_a", 0)) if stats else 0
            chutes_gol_total = (stats.get("chutes_gol_h", 0) + stats.get("chutes_gol_a", 0)) if stats else 0
            prob_15_ft, prob_05_ht = calcular_prob_gols_ht(chutes_tot_total, chutes_gol_total, m)
            
            # Fallback: se não tem stats de chutes nem ataques, usa odd do favorito como proxy
            if chutes_tot_total == 0 and odd_fav_num <= 1.80:
                prob_15_ft = max(prob_15_ft, 65)
                prob_05_ht = max(prob_05_ht, 55)
                if not appm_ht_ok and _aph_val == 0 and _apa_val == 0:
                    appm_ht_ok = True
            
            print(f"[LIMITE-HT] {h} x {a} | odd_fav={odd_fav_num} | prob_15ft={prob_15_ft}% | prob_05ht={prob_05_ht}% | appm_casa={appm_casa} appm_fora={appm_fora} | appm_ht_ok={appm_ht_ok}")
            
            # Diagnóstico detalhado
            limite_ht_ok = True
            if odd_fav_num > 1.80:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — odd do favorito {odd_fav_num} > 1.80, pulando")
                limite_ht_ok = False
            elif prob_15_ft < 60:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — prob 1.5 FT {prob_15_ft}% < 60%, pulando")
                limite_ht_ok = False
            elif prob_05_ht < 50:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — prob 0.5 HT {prob_05_ht}% < 50%, pulando")
                limite_ht_ok = False
            elif not appm_ht_ok:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — APPM casa/fora insuficiente (casa={appm_casa} fora={appm_fora}, precisa ≥0.8), pulando")
                limite_ht_ok = False
            elif not appm_gols_ok:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — APPM gols insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
                limite_ht_ok = False
            elif not hist_ok:
                print(f"[DIAG-LIMITEHT-BARRA] {h} x {a} — média histórica {media_hist:.1f} < 2.0, pulando")
                limite_ht_ok = False
            if limite_ht_ok:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_limiteht_{hoje}"
                if key not in sent:
                    ob365 = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 4, "LIMITEHT", "Over 0.5", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "LIMITEHT", h, a, mid)

        # MERCADO 2: AMBAS MARCAM BTTS (55-75 min, fav perdendo por 1, sem vermelho do fav, média hist ≥ 2.0)
        if p == 2 and 55 <= m <= 75 and ((sh == 1 and sa == 0) or (sh == 0 and sa == 1)):
            if not fav_perdendo_1:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — favorito não perdendo por 1 (fav_gols={fav_gols} adv={adv_gols}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_gols_ok:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not hist_ok:
                print(f"[DIAG-BTTS-BARRA] {h} x {a} — média histórica {media_hist:.1f} < 2.0, pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_btts_{hoje}"
                if key in sent:
                    print(f"[DIAG-BTTS-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("bts_yes") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("bts_yes") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 4, "BTTS", "Ambas Marcam", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "BTTS", h, a, mid)

        # MERCADO 3: OVER 1.5 FT (55-75 min, fav perdendo por 1, placar 1x0/0x1, sem vermelho do fav, média hist ≥ 2.0)
        if p == 2 and 55 <= m <= 75 and ((sh == 1 and sa == 0) or (sh == 0 and sa == 1)):
            if not fav_perdendo_1:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — favorito não perdendo por 1 (fav_gols={fav_gols} adv={adv_gols}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_gols_ok:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not hist_ok:
                print(f"[DIAG-OFT-BARRA] {h} x {a} — média histórica {media_hist:.1f} < 2.0, pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_oft_{hoje}"
                if key in sent:
                    print(f"[DIAG-OFT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+1.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+1.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 4, "OFT", "Over 1.5", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OFT", h, a, mid)

        # MERCADO 4: OVER GOL PARTIDA (55-75 min, placares 0x0/1x1/0x1/1x0, favorito empatando ou perdendo por 1, média hist ≥ 2.0)
        overgoal_valido = (fav_empatando or fav_perdendo_1)
        if p == 2 and 55 <= m <= 75:
            if not overgoal_valido:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_gols_ok:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            elif not hist_ok:
                print(f"[DIAG-OVERGOAL-BARRA] {h} x {a} — média histórica {media_hist:.1f} < 2.0, pulando")
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
                if key in sent:
                    print(f"[DIAG-OVERGOAL-DUP] {h} x {a} — já enviado hoje ({key}), pulando")
                else:
                    ob365 = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 4, "OVERGOAL", linha_over, placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OVERGOAL", h, a, mid, extra_val=total_gols)

        # MERCADO 5: ESCANTEIO LIMITE HT (32-38 min, fav confirmado, empatando ou perdendo por 1, sem vermelho, APPM ≥ 1)
        if p == 1 and 32 <= m <= 38:
            corner_cond = (fav_empatando or fav_perdendo_1)
            if not corner_cond:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_valido:
                print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}, precisa ≥0.7/time ou ≥1.4 total), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_cht_{hoje}"
                cantos_h = stats.get("escanteios_h", -1) if stats else -1
                cantos_a = stats.get("escanteios_a", -1) if stats else -1
                cantos = (max(0, cantos_h) + max(0, cantos_a)) if (cantos_h >= 0 and cantos_a >= 0) else -1
                if cantos < 0:
                    print(f"[DIAG-CORNER-HT-BARRA] {h} x {a} — cantos={cantos} sem dados, pulando")
                elif key in sent:
                    print(f"[DIAG-CORNER-HT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365_e = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano_e = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_HT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365_e, odd_bano=obano_e), marca=key, home=h, away=a, odd_b365_val=ob365_e, odd_bano_val=obano_e)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_HT", h, a, mid, extra_val=cantos)

        # MERCADO 6: ESCANTEIO LIMITE FT (82-88 min, fav confirmado, empatando ou perdendo por 1, sem vermelho)
        if p == 2 and 82 <= m <= 88:
            corner_ft_cond = (fav_empatando or fav_perdendo_1)
            if not corner_ft_cond:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — favorito não empata nem perde por 1 (fav_empatando={fav_empatando} fav_perdendo_1={fav_perdendo_1}), pulando")
            elif red_fav != 0:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav}), pulando")
            elif not appm_valido:
                print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — APPM insuficiente (casa={_appm_h} fora={_appm_a} total={_appm_total}), pulando")
            else:
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{dedup_id}_cft_{hoje}"
                cantos_h = stats.get("escanteios_h", -1) if stats else -1
                cantos_a = stats.get("escanteios_a", -1) if stats else -1
                if cantos_h >= 0 and cantos_a >= 0:
                    cantos = max(0, cantos_h) + max(0, cantos_a)
                else:
                    cantos = -1
                if cantos < 0:
                    print(f"[DIAG-CORNER-FT-BARRA] {h} x {a} — cantos={cantos} sem dados, pulando")
                elif key in sent:
                    print(f"[DIAG-CORNER-FT-DUP] {h} x {a} — já enviado hoje, pulando")
                else:
                    ob365_e = j.get("odds_b365", {}).get("o+0.5") if j.get("odds_b365") else None
                    obano_e = j.get("odds_bano", {}).get("o+0.5") if j.get("odds_bano") else None
                    mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_FT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365_e, odd_bano=obano_e), marca=key, home=h, away=a, odd_b365_val=ob365_e, odd_bano_val=obano_e)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_FT", h, a, mid, extra_val=cantos)

    save_sent(sent)

    # Validação de resultados pendentes — lê e salva via GitHub
    try:
        sinais_p = _load_sinais_github()
        rest = []
        for s in sinais_p:
            res = checar_resultado(s)
            if res:
                emoji = "🟢GREEN CONFIRMADO🟢" if res == "green" else "🔴RED CONFIRMADO🔴"
                send_telegram(emoji, botoes=False, reply_to=s.get("message_id"))
                salvar_resultado(res)
                registrar_performance(s.get("mercado"), res)
            else:
                rest.append(s)
        _save_sinais_github(rest)
        print(f"[SINAIS] {len(sinais_p) - len(rest)} resultados confirmados, {len(rest)} ainda pendentes")
    except Exception as e:
        print(f"[SINAIS] Erro validação: {e}")

    # Processa comandos pendentes com dados reais
    try:
        processar_comandos_pendentes(TG_TOKEN, CHAT_ID, jogos_live, jogos_na_janela)
    except Exception as e:
        print(f"[CMD] Erro chamando comandos: {e}")
    # Processa comandos pendentes com dados reais
    try:
        processar_comandos_pendentes(TG_TOKEN, CHAT_ID, jogos_live, jogos_na_janela)
    except Exception as e:
        print(f"[CMD] Erro chamando comandos: {e}")
    print(f"Finalizado. Enviados: {total_env}")



def processar_comandos_pendentes(token, chat_id, jogos_live=None, jogos_na_janela=None):
    """Processa comandos /relatoriodiario e /radar com checkpoint de update_id."""
    if jogos_live is None: jogos_live = []
    if jogos_na_janela is None: jogos_na_janela = []
    max_id = 0
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates", timeout=10).json()
        if r.get("ok"):
            for update in r.get("result", []):
                uid = update.get("update_id", 0)
                if uid > max_id: max_id = uid
                msg = update.get("message", {})
                text = (msg.get("text", "") or "").strip()
                chat_orig = msg.get("chat", {}).get("id", 0)
                sep = "━" * 20
                if "/radar" in text:
                    linhas_jan = ""
                    for j in jogos_na_janela:
                        h = j.get("home",""); a = j.get("away","")
                        m = j.get("minuto",""); sh = j.get("sh",0); sa = j.get("sa",0)
                        liga = j.get("liga","")
                        linhas_jan += f"\U0001f3af <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
                    if not linhas_jan:
                        linhas_jan = "Nenhum jogo na janela no momento."
                    fora = [j for j in jogos_live if j not in jogos_na_janela][:10]
                    linhas_fora = ""
                    for j in fora:
                        h = j.get("home",""); a = j.get("away","")
                        m = j.get("minuto",""); sh = j.get("sh",0); sa = j.get("sa",0)
                        linhas_fora += f"\u23f3 {h} x {a} | {m}' | {sh}x{sa}\n"
                    if not linhas_fora: linhas_fora = "\u2014"
                    msg_radar = (
                        f"{sep}\n"
                        f"📡👉<b>RADAR DE JOGOS AO VIVO</b>👈📡\n"
                        f"{sep}\n"
                        f"🔴 <b>{len(jogos_live)} jogos ao vivo</b>\n"
                        f"🎯 <b>{len(jogos_na_janela)} na janela alvo</b>\n"
                        f"{sep}\n"
                        f"🚨<b>JOGOS NO ALVO:</b>\n{linhas_jan}"
                        f"{sep}\n"
                        f"<b>⏳ FORA DA JANELA:</b>\n{linhas_fora}"
                        f"{sep}"
                    )
                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                  json={"chat_id": chat_orig, "text": msg_radar, "parse_mode": "HTML"})
                    print(f"[CMD] Radar respondido com {len(jogos_live)} jogos live, {len(jogos_na_janela)} na janela")
                elif "/relatoriomensal" in text:
                    try:
                        msg = enviar_relatorio_mensal()
                        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                      json={"chat_id": chat_orig, "text": msg, "parse_mode": "HTML"})
                    except Exception as e:
                        print(f"[REL-MENSAL] Erro: {e}")
                elif "/relatoriodiario" in text:
                    try: enviar_relatorio_diario()
                    except: pass
                elif "/mercados" in text:
                    try:
                        msg = enviar_relatorio_performance()
                        if not msg:
                            requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                                          json={"chat_id": chat_orig, "text": "Ainda sem dados de performance registrados.", "parse_mode": "HTML"})
                    except Exception as e:
                        print(f"[PERFORMANCE] Erro: {e}")
        if max_id > 0:
            try:
                off = max_id
                requests.get(f"https://api.telegram.org/bot{token}/getUpdates?offset={off+1}", timeout=5)
            except: pass
    except Exception as e:
        print(f"[CMD] Erro processar comandos: {e}")
if __name__ == "__main__":
    run()