import os, json, requests, time
from datetime import datetime, timezone, timedelta

# ─── Caminhos e Fuso ───────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
SENT_FILE       = os.path.join(BASE_DIR, "sent_live_signals.json")
SINAIS_FILE     = os.path.join(BASE_DIR, "sinais_pendentes.json")
RESULTADO_FILE  = os.path.join(BASE_DIR, "resultados.json")
LAST_UPDATE_FILE= os.path.join(BASE_DIR, "last_update.json")
BRT             = timezone(timedelta(hours=-3))

# ─── Credenciais ───────────────────────────────────────────────────────────────
TELEGRAM_TOKEN  = "8925195607:AAEmgjrY0S6bVx95BGSzgHaNxbDlOarcEx8"
CHAT_IDS        = ["-1003530439409"]  # BOOT IA INTELIGENTE (Zapia)
ODDS_API_KEY    = "74e3ecb93cc2333874cb7038b9f682c0"
RAPIDAPI_KEY    = "f72be1a7cdmsha226030291845afp131cd7jsn00f5979540aa"

# API-Football (fallback quando ESPN não tiver o jogo)
API_FOOTBALL_KEYS = [
    "77c645149c00ea5bbcca2c348e8a46c8",   # Chave do irmão (principal)
    "7fa6994f1e4103991a95ad53d2e7cc6b",   # Chave própria (fallback)
]
API_FOOTBALL_URL = "https://v3.football.api-sports.io"

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
    "arg.1": "Liga Profesional Argentina", "col.1": "Liga BetPlay Colombia",
    "chi.1": "Primera División Chile", "uru.1": "Primera División Uruguai",
    "ecu.1": "LigaPro Ecuador", "bol.1": "División Profesional Bolivia",
    "per.1": "Liga 1 Peru", "ven.1": "Primera División Venezuela",
    "par.1": "División Profesional Paraguay",
    "conmebol.libertadores": "Copa Libertadores",
    "conmebol.sudamericana": "Copa Sudamericana",
    "usa.1": "MLS", "usa.2": "USL Championship", "usa.usl.l1": "USL League One",
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
    "fin.1": "Finnish Veikkausliga", "swe.2": "Swedish SuperEttan",
    "nor.2": "Norwegian 1. Division", "den.2": "Danish 1. Division",
    "nga.1": "Nigerian Professional League",
    "caf.champions": "CAF Champions League", "afc.champions": "AFC Champions League",
}
ESPN_LIGAS = [
    "eng.1", "esp.1", "ger.1", "ita.1", "fra.1",
    "por.1", "ned.1", "bel.1", "tur.1", "sco.1", "aut.1", "sui.1", "den.1", "swe.1", "nor.1", "gre.1", "cze.1", "pol.1",
    "fin.1", "swe.2", "nor.2", "den.2", "isr.1", "rus.1",
    "uefa.champions", "uefa.europa", "uefa.europa_conf",
    "bra.1", "bra.2", "bra.3", "bra.4",
    "arg.1", "col.1", "chi.1", "uru.1", "ecu.1", "bol.1", "per.1", "ven.1", "par.1",
    "conmebol.libertadores", "conmebol.sudamericana",
    "usa.1", "usa.2", "usa.usl.l1", "mex.1", "mex.2", "concacaf.champions",
    "jpn.1", "kor.1", "sau.1", "qat.1",
    "chn.1", "ind.1", "mys.1", "tha.1", "idn.1", "aus.1",
    "rsa.1", "egy.1", "nga.1",
    "caf.champions", "afc.champions",
    # 2ª Divisões Europa
    "eng.2", "esp.2", "ger.2", "ita.2", "fra.2", "ned.2", "tur.2", "aut.2", "sui.2", "sco.2", "fin.2",
    # Europa extra
    "cyp.1", "mlt.1", "rou.1", "irl.1",
    # África extra
    "gha.1", "uga.1", "ken.1", "zim.1", "zam.1", "rsa.2",
    # Ásia extra
    "sgp.1", "ind.2",
    # América do Sul 2ª divisão
    "arg.2", "col.2", "chi.2", "per.2", "uru.2", "ecu.2",
    # América Central / Caribe
    "slv.1", "jam.1", "hon.1",
    # América do Sul extra
    "par.2", "ven.2",
    # Competições
    "uefa.nations",
    # Copa do Mundo e Eliminatórias
    "fifa.world", "fifa.worldq",
    "club.friendly",
]

# RapidAPI (fallback de lista)
RAPIDAPI_URL     = "https://free-api-live-football-data.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg, botoes=True, reply_to=None):
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if botoes:
            payload["reply_markup"] = json.dumps({"inline_keyboard": [[
                {"text": "🟣 BET365",   "url": "https://www.bet365.com/"},
                {"text": "🔵 PARIPESA", "url": "https://media.bet/pt/live/football"}
            ]]})
        try:
            r = requests.post(url, json=payload, timeout=10)
            mid = r.json().get("result", {}).get("message_id")
            if mid: last_mid = mid
        except:
            pass
    return last_mid

# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVOS LOCAIS
# ═══════════════════════════════════════════════════════════════════════════════
def load_sent():
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r') as f: return set(json.load(f))
        except: pass
    return set()

def save_sent(sent):
    with open(SENT_FILE, 'w') as f: json.dump(list(sent), f)

def registrar_sinal(fid, mercado, home, away, message_id, extra_val=None):
    sinais = []
    if os.path.exists(SINAIS_FILE):
        try:
            with open(SINAIS_FILE, 'r') as f: sinais = json.load(f)
        except: pass
    sinais.append({
        "fixture_id": fid, "mercado": mercado,
        "home": home, "away": away,
        "message_id": message_id, "extra_val": extra_val,
        "timestamp": datetime.now(BRT).isoformat()
    })
    with open(SINAIS_FILE, 'w') as f: json.dump(sinais, f)

def salvar_resultado(resultado):
    # Suporta tanto formato lista [{data, resultado}] quanto dict {greens, reds}
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    registros = []
    if os.path.exists(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, 'r') as f:
                dados = json.load(f)
            if isinstance(dados, list):
                registros = dados
            elif isinstance(dados, dict):
                # Converte formato antigo para lista
                for _ in range(dados.get("greens", 0)):
                    registros.append({"data": hoje, "resultado": "green"})
                for _ in range(dados.get("reds", 0)):
                    registros.append({"data": hoje, "resultado": "red"})
        except: pass
    registros.append({"data": hoje, "resultado": resultado, "timestamp": datetime.now(BRT).isoformat()})
    with open(RESULTADO_FILE, 'w') as f: json.dump(registros, f, indent=2)

def get_relatorio_hoje():
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    greens, reds = 0, 0
    if os.path.exists(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, 'r') as f: dados = json.load(f)
            if isinstance(dados, list):
                for r in dados:
                    if r.get("data") == hoje:
                        if r.get("resultado") == "green": greens += 1
                        else: reds += 1
            elif isinstance(dados, dict):
                greens = dados.get("greens", 0)
                reds   = dados.get("reds", 0)
        except: pass
    return greens, reds

def enviar_relatorio_diario():
    sep = "━━━━━━━━━━━━━━━━━━━━"
    hoje = datetime.now(BRT).strftime("%d/%m/%Y")
    greens, reds = get_relatorio_hoje()
    total = greens + reds
    taxa  = (greens / total * 100) if total > 0 else 0
    msg = (
        f"{sep}\n📊 <b>RELATÓRIO DIÁRIO — {hoje}</b>\n{sep}\n"
        f"✅ <b>GREEN:</b> {greens}\n"
        f"🔴 <b>RED:</b> {reds}\n"
        f"📈 <b>TOTAL DE ENTRADAS:</b> {total}\n"
        f"🎯 <b>ASSERTIVIDADE:</b> {taxa:.1f}%\n{sep}\n"
        f"💰 <i>Máquina de Greens — Resultados do dia!</i>"
    )
    send_telegram(msg, botoes=False)

# ═══════════════════════════════════════════════════════════════════════════════
# API 1 — ESPN: lista de jogos ao vivo em TODAS as ligas
# ═══════════════════════════════════════════════════════════════════════════════
def get_jogos_espn():
    jogos  = []
    vistos = set()
    for liga_slug in ESPN_LIGAS:
        try:
            url  = ESPN_SCOREBOARD.format(liga=liga_slug)
            r    = requests.get(url, timeout=8)
            if r.status_code != 200:
                continue
            data   = r.json()
            # Pega o nome real da liga
            ligas_data = data.get("leagues", [])
            liga_nome  = ligas_data[0].get("name", "") if ligas_data else ""
            # ESPN às vezes retorna "all" como nome — ignorar e usar mapeamento
            if not liga_nome or liga_nome.lower() in ("all", liga_slug):
                liga_nome = LIGA_NOMES.get(liga_slug, liga_slug)
            events = data.get("events", [])
            for e in events:
                try:
                    eid  = e.get("id", "")
                    if eid in vistos:
                        continue
                    comp   = e.get("competitions", [{}])[0]
                    status = comp.get("status", {}).get("type", {})
                    state  = status.get("state", "")
                    minuto_raw = comp.get("status", {}).get("displayClock", "0")
                    try:
                        minuto = int(minuto_raw.replace("'","").split("+")[0].split(":")[0])
                    except:
                        clock = comp.get("status", {}).get("clock", 0)
                        minuto = int(float(clock) // 60) if clock else 0

                    # Aceita "post" recente (encerrado há menos de 15 min) para janela 80-88
                    if state == "post":
                        date_str = e.get("date", "")
                        if date_str:
                            try:
                                from datetime import timezone as _tz
                                dt_jogo = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                                agora   = datetime.now(_tz.utc)
                                diff    = (agora - dt_jogo).total_seconds()
                                # Jogo de 90min + até 15min de tolerância
                                if diff <= (90 + 15) * 60:
                                    minuto = 85  # coloca na janela 80-88
                                    state  = "in"
                                else:
                                    continue
                            except:
                                continue
                        else:
                            continue
                    if state not in ("in",):
                        continue
                    # Calcula period corretamente
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
                    vistos.add(eid)
                    jogos.append({
                        "fid"   : eid,
                        "home"  : home,
                        "away"  : away,
                        "sh"    : sh,
                        "sa"    : sa,
                        "minuto": minuto,
                        "period": period,
                        "liga"  : liga,
                        "source": "espn"
                    })
                except:
                    continue
            time.sleep(0.3)
        except:
            continue
    print(f"[ESPN] {len(jogos)} jogos ao vivo ({len(ESPN_LIGAS)} ligas monitoradas)")
    return jogos


# ═══════════════════════════════════════════════════════════════════════════════
# API 2 — ESPN: estatísticas do jogo (chutes, cantos, cartões)
# ═══════════════════════════════════════════════════════════════════════════════
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
# FALLBACK — API-Football: estatísticas (usado se ESPN falhar)
# ═══════════════════════════════════════════════════════════════════════════════
def get_stats_apifootball(fid):
    for key in API_FOOTBALL_KEYS:
        try:
            r     = requests.get(f"{API_FOOTBALL_URL}/fixtures/statistics",
                                 params={"fixture": fid},
                                 headers={"x-apisports-key": key}, timeout=10)
            rjson = r.json()
            if (r.headers.get("x-ratelimit-requests-remaining") == "0"
                    or (isinstance(rjson.get("errors"), dict) and rjson.get("errors", {}).get("requests"))
                    or (isinstance(rjson.get("errors"), dict) and rjson.get("errors", {}).get("access"))):
                print(f"[API-Football] Chave {key[:8]}... indisponível")
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
            print(f"[API-Football] Stats OK chave {key[:8]}...")
            return stats
        except:
            continue
    return {}

# ═══════════════════════════════════════════════════════════════════════════════
# API 3 — THE ODDS API: valida favorito pelas odds
# ═══════════════════════════════════════════════════════════════════════════════
def get_favorito_odds(home, away):
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/soccer/odds/",
                         params={"apiKey": ODDS_API_KEY, "regions": "eu",
                                 "markets": "h2h", "oddsFormat": "decimal"}, timeout=10)
        for evento in r.json():
            nomes = [evento.get("home_team","").lower(), evento.get("away_team","").lower()]
            if home.lower() in nomes and away.lower() in nomes:
                for book in evento.get("bookmakers", []):
                    for mkt in book.get("markets", []):
                        if mkt["key"] == "h2h":
                            outcomes = {o["name"].lower(): o["price"] for o in mkt["outcomes"]}
                            odd_h = outcomes.get(home.lower(), 99)
                            odd_a = outcomes.get(away.lower(), 99)
                            return "h" if odd_h <= odd_a else "a"
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# FILTRO DE JANELAS
# ═══════════════════════════════════════════════════════════════════════════════
def filtrar_janelas(jogos):
    resultado = []
    for j in jogos:
        m, p = j["minuto"], j["period"]
        em_janela = (
            (p == 1 and 15 <= m <= 27) or
            (p == 1 and 30 <= m <= 38) or
            (p == 2 and 60 <= m <= 75) or
            (p == 2 and 80 <= m <= 88)
        )
        if em_janela:
            resultado.append(j)
    return resultado

# ═══════════════════════════════════════════════════════════════════════════════
# MENSAGEM PADRÃO
# ═══════════════════════════════════════════════════════════════════════════════
def gerar_motivo(mercado, stats, sh, sa, fav_final, cantos_atual=0):
    chutes_h     = stats.get("chutes_tot_h", 0) if stats else 0
    chutes_a     = stats.get("chutes_tot_a", 0) if stats else 0
    chutes_gol_h = stats.get("chutes_gol_h", 0) if stats else 0
    chutes_gol_a = stats.get("chutes_gol_a", 0) if stats else 0
    cantos_h     = max(0, stats.get("escanteios_h", 0)) if stats else 0
    cantos_a     = max(0, stats.get("escanteios_a", 0)) if stats else 0
    red_h        = stats.get("red_cards_h", 0) if stats else 0
    red_a        = stats.get("red_cards_a", 0) if stats else 0
    fav_chutes   = chutes_h if fav_final == "h" else chutes_a
    fav_chutes_g = chutes_gol_h if fav_final == "h" else chutes_gol_a
    total_chutes = chutes_h + chutes_a
    total_cantos = cantos_h + cantos_a
    tem_dados    = total_chutes > 0 or total_cantos > 0

    if fav_final == "h":
        fav_label = "🏠 Casa"
    elif fav_final == "a":
        fav_label = "✈️ Fora"
    else:
        fav_label = "⚠️ Consultar casa de apostas"

    if not tem_dados:
        return f"⭐️ Favorito: {fav_label}\n✅ Estatísticas não disponíveis para esta liga"

    partes = [f"⭐️ Favorito: {fav_label}"]

    # Volume de jogo
    if total_chutes >= 10:
        partes.append(f"Jogo intenso com {total_chutes} chutes no total ({chutes_h} casa x {chutes_a} fora)")
    elif total_chutes > 0:
        partes.append(f"{total_chutes} chutes no total ({chutes_h} casa x {chutes_a} fora)")

    # Chutes no alvo
    total_gol = chutes_gol_h + chutes_gol_a
    if total_gol > 0:
        partes.append(f"{total_gol} chutes no alvo ({chutes_gol_h} x {chutes_gol_a})")

    # Escanteios
    if total_cantos > 0:
        partes.append(f"{total_cantos} escanteios cobrados ({cantos_h} x {cantos_a})")

    # Cartão vermelho
    if red_h > 0 or red_a > 0:
        partes.append(f"⚠️ Cartão vermelho: {'Casa' if red_h > 0 else 'Fora'}")

    return "✅ " + " | ".join(partes)


def msg_universal(home, away, minuto, liga, n, mercado, entrada, placar, extra_val=None, cantos_atual=0, stats=None, sh=0, sa=0, fav_final="h"):
    sep    = "━━━━━━━━━━━━━━━━━━━━"
    motivo = gerar_motivo(mercado, stats, sh, sa, fav_final, cantos_atual)
    if "CORNER" in mercado:
        linha  = cantos_atual + 0.5
        entrada = f"Mais de {linha} Cantos"
    titles = {
        "HT"       : "⚽️🔥<b>OVER GOL INTERVALO</b>🔥⚽️",
        "BTTS"     : "⚽️🔥<b>AMBAS MARCAM</b>🔥⚽️",
        "OFT"      : "⚽️🔥<b>OVER 1.5 GOLS PARTIDA</b>🔥⚽️",
        "OVERGOAL" : "⚽️🔥<b>OVER GOL PARTIDA</b>🔥⚽️",
        "CORNER_HT": "⛳️🔥<b>ESCANTEIO LIMITE HT</b>🔥⛳️",
        "CORNER_FT": "⛳️🔥<b>ESCANTEIO LIMITE FT</b>🔥⛳️",
    }
    title = titles.get(mercado, f"⚽️🔥<b>{mercado}</b>🔥⚽️")

    if "CORNER" in mercado:
        return (
            f"{sep}\n{title}\n⚠️Placar: {placar}\n🌐 Liga: {liga}\n"
            f"⚔️ <b>{home}</b> x <b>{away}</b>\n🕐 Minuto: <b>{minuto}'</b>\n{sep}\n"
            f"📊 <b>Análise ao Vivo da Entrada:</b>\n📝 {motivo}\n"
            f"💰 Odd Mínima Recomendada: 1.70\n{sep}\n"
            f"⛳️ Escanteios Atuais: <b>{cantos_atual}</b>\n"
            f"📌 Entrada: <b>{entrada}</b>\n"
            f"✅ Critérios: <b>{n}/6</b>\n{sep}\n"
            f"⚠️Jogue com responsabilidade⚠️"
        )
    return (
        f"{sep}\n{title}\n⚠️Placar: {placar}\n🌐 Liga: {liga}\n"
        f"⚔️ <b>{home}</b> x <b>{away}</b>\n🕐 Minuto: <b>{minuto}'</b>\n{sep}\n"
        f"📊 <b>Análise ao Vivo da Entrada:</b>\n📝 {motivo}\n"
        f"💰 Odd Mínima Recomendada: 1.70\n{sep}\n"
        f"📌 Entrada: <b>{entrada}</b>\n✅ Critérios: <b>{n}/6</b>\n{sep}\n"
        f"⚠️Jogue com responsabilidade⚠️"
    )

# ═══════════════════════════════════════════════════════════════════════════════
# VALIDAÇÃO DE RESULTADOS (usa ESPN para checar placar final)
# ═══════════════════════════════════════════════════════════════════════════════
def checar_resultado(sinal):
    try:
        eid     = str(sinal.get("fixture_id"))
        mercado = sinal.get("mercado")
        # Busca via ESPN summary
        r    = requests.get(ESPN_SUMMARY, params={"event": eid}, timeout=10)
        data = r.json()
        status_obj = data.get("header", {}).get("competitions", [{}])[0].get("status", {})
        state      = status_obj.get("type", {}).get("state", "")
        if state != "post": return None
        competitors = data.get("header", {}).get("competitions", [{}])[0].get("competitors", [])
        gh, ga = 0, 0
        for c in competitors:
            if c.get("homeAway") == "home": gh = int(c.get("score", 0) or 0)
            if c.get("homeAway") == "away": ga = int(c.get("score", 0) or 0)
        total = gh + ga
        if mercado == "HT":
            # Pega placar do HT nos linescores
            linescore = competitors[0].get("linescores", [])
            ht_total  = sum(int(l.get("displayValue", 0) or 0) for l in linescore[:1])
            return "green" if ht_total >= 1 else "red"
        elif mercado == "BTTS":
            return "green" if gh >= 1 and ga >= 1 else "red"
        elif mercado == "OFT":
            return "green" if total >= 2 else "red"
        elif mercado == "OVERGOAL":
            return "green" if total >= 1 else "red"
        elif mercado in ["CORNER_HT", "CORNER_FT"]:
            stats = get_stats_espn(eid, sinal.get("home",""), sinal.get("away",""))
            c_final = stats.get("escanteios_h", 0) + stats.get("escanteios_a", 0)
            c_entrada = sinal.get("extra_val", 0)  # cantos no momento do sinal
            # Green se cantos finais > cantos no momento do sinal (linha = cantos_entrada + 0.5)
            return "green" if c_final > c_entrada else "red"
        return None
    except:
        return None

# ═══════════════════════════════════════════════════════════════════════════════
# COMANDOS TELEGRAM (/relatorio e /radar)
# ═══════════════════════════════════════════════════════════════════════════════
def check_status_command(total_jogos_live=0):
    last_id = 0
    if os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE, 'r') as f: last_id = json.load(f).get("last_id", 0)
        except: pass
    try:
        sep = "━━━━━━━━━━━━━━━━━━━━"
        r   = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                           params={"offset": last_id + 1, "timeout": 5}, timeout=10).json()
        if not r.get("ok"): return
        new_last_id = last_id
        for update in r.get("result", []):
            new_last_id = update["update_id"]
            msg     = update.get("message", {})
            text    = msg.get("text", "")
            chat_id = str(msg.get("chat", {}).get("id", ""))
            if chat_id != str(CHAT_IDS[0]):
                continue
            if text == "/relatorio":
                enviar_relatorio_diario()
            elif text == "/radar":
                send_telegram(
                    f"{sep}\n📡⚠️<b>JOGOS NO RADAR</b>⚠️📡\n{sep}\n"
                    f"O Robô está monitorando <b>{total_jogos_live}</b> jogos ao vivo.\n{sep}\n"
                    f"🔍 Buscando Oportunidades nos 6 mercados...\n{sep}",
                    botoes=False
                )
        if new_last_id > last_id:
            with open(LAST_UPDATE_FILE, 'w') as f: json.dump({"last_id": new_last_id}, f)
    except: pass

# ═══════════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def run():
    print("[Iniciando monitoramento — ESPN + Odds API]")
    sent      = load_sent()
    total_env = 0
    # janela_id por hora — evita duplicata mesmo se Actions rodar 2x no mesmo minuto
    janela_id = datetime.now(BRT).strftime('%Y%m%d%H')

    # PASSO 1: ESPN busca todos os jogos ao vivo
    jogos_live = get_jogos_espn()
    check_status_command(total_jogos_live=len(jogos_live))

    # PASSO 2: Filtra janelas alvo
    jogos_na_janela = filtrar_janelas(jogos_live)
    print(f"[Janela] {len(jogos_na_janela)} jogos nas janelas alvo")

    if not jogos_na_janela:
        print("[OK] Nenhum jogo na janela — aguardando próximo ciclo")
        save_sent(sent)
        print("Finalizado. Enviados: 0")
        return

    # PASSO 3: Analisa cada jogo na janela
    for j in jogos_na_janela:
        fid    = j["fid"]
        h, a   = j["home"], j["away"]
        m, p   = j["minuto"], j["period"]
        sh, sa = j["sh"], j["sa"]
        liga   = str(j["liga"])
        stot   = sh + sa
        placar = f"{sh}x{sa}"

        print(f"[Analisando] {h} x {a} | {placar} | {m}min")

        # Busca stats UMA vez — reutiliza para tudo
        stats = get_stats_espn(fid, h, a)

        # Determinar favorito pelas odds
        fav_final = get_favorito_odds(h, a)
        if not fav_final:
            fav_final = "?"  # Sem odds disponível — favorito não identificado
            print(f"[FAV-FALLBACK] {h} x {a} — sem odds disponível")

        # Cartão vermelho do favorito
        red_fav = stats.get(f"red_cards_{fav_final}", 0) if stats else 0

        # Placar do favorito e adversário
        fav_gols = sh if fav_final == "h" else sa
        adv_gols = sa if fav_final == "h" else sh

        # Favorito empatando = placar igual
        fav_empatando = (sh == sa)
        # Favorito perdendo por exatamente 1 gol — placar obrigatório: 0x1 ou 1x0
        fav_perdendo_1 = (
            (sh == 0 and sa == 1 and fav_final == "h") or
            (sh == 1 and sa == 0 and fav_final == "a")
        )

        # MERCADO 1: OVER 0.5 HT (15-27 min, 0x0, favorito empatando, sem vermelho do fav)
        if p == 1 and 15 <= m <= 27 and stot == 0 and fav_empatando and red_fav == 0:
            key = f"{fid}_ht"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 3, "HT", "Over 0.5 HT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "HT", h, a, mid)

        # MERCADO 2: AMBAS MARCAM BTTS (60-75 min, fav perdendo por 1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and fav_perdendo_1 and red_fav == 0:
            key = f"{fid}_btts"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "BTTS", "Ambas Marcam", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "BTTS", h, a, mid)

        # MERCADO 3: OVER 1.5 FT (60-75 min, fav perdendo por 1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and fav_perdendo_1 and red_fav == 0:
            key = f"{fid}_oft"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OFT", "Over 1.5 FT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OFT", h, a, mid)

        # MERCADO 4: OVER 0.5 FT (60-75 min, 0x0, favorito empatando, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and stot == 0 and fav_empatando and red_fav == 0:
            key = f"{fid}_overgoal"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OVERGOAL", "Over 0.5 FT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OVERGOAL", h, a, mid)

        # MERCADO 5: ESCANTEIO LIMITE HT (30-38 min, fav empatando ou perdendo por 1, sem vermelho do fav)
        if p == 1 and 30 <= m <= 38 and (fav_empatando or fav_perdendo_1) and red_fav == 0:
            key = f"{fid}_cht"
            cantos_h = stats.get("escanteios_h", 0) if stats else 0
            cantos_a = stats.get("escanteios_a", 0) if stats else 0
            cantos = max(0, cantos_h) + max(0, cantos_a)  # -1 vira 0
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_HT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_HT", h, a, mid, extra_val=cantos)

        # MERCADO 6: ESCANTEIO LIMITE FT (80-88 min, fav empatando ou perdendo por 1, sem vermelho do fav)
        if p == 2 and 80 <= m <= 88 and (fav_empatando or fav_perdendo_1) and red_fav == 0:
            key = f"{fid}_cft"
            cantos_h = stats.get("escanteios_h", 0) if stats else 0
            cantos_a = stats.get("escanteios_a", 0) if stats else 0
            cantos = max(0, cantos_h) + max(0, cantos_a)  # -1 vira 0
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_FT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final))
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_FT", h, a, mid, extra_val=cantos)

    save_sent(sent)

    # Validação de resultados pendentes
    if os.path.exists(SINAIS_FILE):
        try:
            with open(SINAIS_FILE, 'r') as f: sinais_p = json.load(f)
            rest = []
            for s in sinais_p:
                res = checar_resultado(s)
                if res:
                    emoji = "🟢 GREEN CONFIRMADO 🟢" if res == "green" else "🔴 RED CONFIRMADO 🔴"
                    send_telegram(emoji, botoes=False, reply_to=s.get("message_id"))
                    salvar_resultado(res)
                else:
                    rest.append(s)
            with open(SINAIS_FILE, 'w') as f: json.dump(rest, f)
        except: pass

    print(f"Finalizado. Enviados: {total_env}")

if __name__ == "__main__":
    run()
