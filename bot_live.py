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
CHAT_IDS        = ["-1003530439409"]
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
    # Europa - 1ª divisão
    "eng.1","eng.2","eng.3","eng.4","eng.5",
    "esp.1","esp.2","ger.1","ger.2","ita.1","ita.2","ita.3","ita.4","ita.5","fra.1","fra.2",
    "por.1","ned.1","ned.2","ned.3","bel.1","tur.1","tur.2","sco.1","sco.2","sco.3","sco.4",
    "aut.1","aut.2","sui.1","sui.2","den.1","den.2","den.3","den.4","den.5","swe.1","swe.2",
    "nor.1","nor.2","nor.3","gre.1","cze.1","pol.1","fin.1","fin.2",
    "isr.1","rus.1","irl.1","nir.1","mlt.1","cyp.1",
    # UEFA
    "uefa.champions","uefa.europa","uefa.europa.conf",
    "uefa.nations","uefa.wchampions",
    # América do Sul
    "bra.1","bra.2","bra.3","bra.4",
    "arg.1","arg.2","arg.3","arg.4","arg.5","col.1","col.2","chi.1","chi.2",
    "uru.1","uru.2","ecu.1","ecu.2","bol.1",
    "per.1","per.2","ven.1","ven.2","par.1","par.2",
    "conmebol.libertadores","conmebol.sudamericana","conmebol.recopa",
    # América do Norte/Central/Caribe
    "usa.1","usa.2","usa.usl.l1","usa.nwsl","usa.open",
    "mex.1","mex.2","jam.1","slv.1",
    "concacaf.champions","concacaf.gold","concacaf.nations.league",
    # Ásia
    "jpn.1","kor.1","chn.1","ind.1","ind.2",
    "tha.1","mys.1","idn.1","sgp.1",
    "afc.champions","afc.cup",
    # África
    "rsa.1","rsa.2","egy.1","gha.1","ken.1","uga.1","zim.1","zam.1",
    "caf.confederation","caf.champions",
    # Oceania
    "aus.1",
    # Mundial / Eliminatórias
    "fifa.world","fifa.cwc","fifa.olympics","fifa.confederations",
    "fifa.worldq.uefa","fifa.worldq.conmebol","fifa.worldq.concacaf",
    "fifa.worldq.afc","fifa.worldq.caf","fifa.worldq.ofc",
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
def send_telegram(msg, botoes=True, reply_to=None, marca=None):
    url_send = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
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
            r = requests.post(url_send, json=payload, timeout=10)
            mid = r.json().get("result", {}).get("message_id")
            if mid: last_mid = mid
        except:
            pass
    return last_mid

# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVOS LOCAIS
# ═══════════════════════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "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")
GITHUB_REPO  = os.environ.get("GITHUB_REPOSITORY", "cleubianodasilva-png/boot-ia-inteligente-bot")
SENT_API_PATH = "sent_live_signals.json"

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
    # Proteção contra duplicata: só envia 1x por dia
    hoje_key = f"relatorio_{datetime.now(BRT).strftime('%Y-%m-%d')}"
    sent_ctrl = load_sent()
    if hoje_key in sent_ctrl:
        print(f"[Relatório] Já enviado hoje ({hoje_key}), ignorando.")
        return
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
        f"⚠️👆<i>Resultados do dia</i>👆⚠️"
    )
    if send_telegram(msg, botoes=False):
        sent_ctrl.add(hoje_key)
        save_sent(sent_ctrl)
        print(f"[Relatório] Enviado e registrado ({hoje_key})")

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
                    date_str = e.get("date", "")
                    if date_str:
                        try:
                            from datetime import timezone as _tz
                            dt_jogo = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                            agora   = datetime.now(_tz.utc)
                            diff    = (agora - dt_jogo).total_seconds()
                            if diff <= (90 + 15) * 60:
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
                    "period": period, "liga": liga, "source": "espn"
                })
            except:
                continue
    except:
        pass
    return resultado


def get_jogos_espn():
    from concurrent.futures import ThreadPoolExecutor, as_completed
    jogos  = []
    vistos = set()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(_fetch_liga, slug): slug for slug in ESPN_LIGAS}
        for future in as_completed(futures):
            for j in future.result():
                if j["fid"] not in vistos:
                    vistos.add(j["fid"])
                    jogos.append(j)
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
    posse_h_raw  = stats.get("posse_h", 0.0) if stats else 0.0
    posse_a_raw  = stats.get("posse_a", 0.0) if stats else 0.0
    posse_h = int(round(float(posse_h_raw) * 100)) if float(posse_h_raw) <= 1 else int(round(float(posse_h_raw)))
    posse_a = int(round(float(posse_a_raw) * 100)) if float(posse_a_raw) <= 1 else int(round(float(posse_a_raw)))
    total_chutes = chutes_h + chutes_a
    total_cantos = cantos_h + cantos_a
    tem_dados    = total_chutes > 0 or total_cantos > 0

    if not tem_dados:
        return "Estatísticas não disponíveis para esta liga"

    # Labels com identidade: Favorito(Casa/Fora) ou Zebra(Casa/Fora)
    if fav_final == "h":
        fav_label  = "Favorito (Casa)"
        zebra_label = "Zebra (Fora)"
        fav_chutes = chutes_h; fav_gol = chutes_gol_h
        adv_chutes = chutes_a; adv_gol = chutes_gol_a
    elif fav_final == "a":
        fav_label  = "Favorito (Fora)"
        zebra_label = "Zebra (Casa)"
        fav_chutes = chutes_a; fav_gol = chutes_gol_a
        adv_chutes = chutes_h; adv_gol = chutes_gol_h
    else:
        fav_label  = "Casa"
        zebra_label = "Fora"
        fav_chutes = chutes_h; fav_gol = chutes_gol_h
        adv_chutes = chutes_a; adv_gol = chutes_gol_a

    # Contexto do placar
    jogo_aberto  = sh == 0 and sa == 0
    fav_perdendo = (fav_final == "h" and sh < sa) or (fav_final == "a" and sa < sh)
    fav_ganhando = (fav_final == "h" and sh > sa) or (fav_final == "a" and sa > sh)
    # Zebra dominando nos dados
    zebra_dominando = adv_chutes > fav_chutes

    if red_h > 0 or red_a > 0:
        vermelho = " | 🟥 Vermelho: " + ("Casa" if red_h > 0 else "Fora")
    else:
        vermelho = ""

    posse_txt = ""
    if posse_h >= 55:
        posse_txt = f", Casa com {posse_h}% de posse"
    elif posse_a >= 55:
        posse_txt = f", Fora com {posse_a}% de posse"

    # ── JOGO ABERTO (0x0) ─────────────────────────────────────────
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
        return f"Jogo aberto, ambas buscando o primeiro gol — {chutes_h} chutes x {chutes_a}{posse_txt}{vermelho}"

    # ── FAVORITO PERDENDO ─────────────────────────────────────────
    if fav_perdendo:
        if fav_chutes >= 8 and fav_gol >= 3:
            return f"Grandes chances do {fav_label} empatar — chegando constantemente com {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes >= 6 and fav_gol >= 2:
            return f"{fav_label} em busca do empate, criando boas chances — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if zebra_dominando and adv_chutes >= 8:
            return f"{zebra_label} dominando e ameaçando ampliar — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes:
            return f"{fav_label} em busca do empate, pressionando com {fav_chutes} chutes x {adv_chutes}{posse_txt}{vermelho}"
        return f"{fav_label} perdendo e tentando reagir — {fav_chutes} chutes x {adv_chutes} da {zebra_label}{posse_txt}{vermelho}"

    # ── FAVORITO GANHANDO ─────────────────────────────────────────
    if fav_ganhando:
        if adv_chutes >= 8 and adv_gol >= 3:
            return f"{zebra_label} pressionando forte em busca do empate — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes >= 8:
            return f"{fav_label} controlando e ampliando a pressão — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes:
            return f"{fav_label} na frente e dominando — {fav_chutes} chutes x {adv_chutes} da {zebra_label}{posse_txt}{vermelho}"
        return f"{fav_label} vencendo, jogo controlado — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"

    # ── PLACAR EMPATADO (não 0x0) ─────────────────────────────────
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
    if total_cantos >= 6:
        return f"Jogo bastante movimentado pelas laterais — {total_cantos} escanteios, {total_chutes} chutes{posse_txt}{vermelho}"
    return f"Jogo equilibrado, ambas criando chances — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"

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
        fav_por_odds = fav_final in ("h", "a")

        if not fav_por_odds:
            # Fallback 1: maior volume de chutes
            ch = stats.get("chutes_tot_h", 0) if stats else 0
            ca = stats.get("chutes_tot_a", 0) if stats else 0
            eh = max(0, stats.get("escanteios_h", 0)) if stats else 0
            ea = max(0, stats.get("escanteios_a", 0)) if stats else 0
            if ch > ca:
                fav_final = "h"
                print(f"[FAV-FALLBACK] {h} x {a} — Casa favorita por chutes ({ch}x{ca})")
            elif ca > ch:
                fav_final = "a"
                print(f"[FAV-FALLBACK] {h} x {a} — Fora favorita por chutes ({ca}x{ch})")
            # Fallback 2: maior número de escanteios (empate nos chutes)
            elif eh > ea:
                fav_final = "h"
                print(f"[FAV-FALLBACK] {h} x {a} — Casa favorita por escanteios ({eh}x{ea})")
            elif ea > eh:
                fav_final = "a"
                print(f"[FAV-FALLBACK] {h} x {a} — Fora favorita por escanteios ({ea}x{eh})")
            else:
                fav_final = "?"
                print(f"[SKIP-FAV] {h} x {a} — sem dados suficientes para identificar favorito")

        # fav_confirmado = odds OU fallback por estatísticas (chutes/escanteios)
        fav_confirmado = fav_por_odds or (fav_final in ("h", "a"))
        if fav_final not in ("h", "a"):
            # Sem odds e sem fallback — pula escanteio mas continua outros mercados com "h"
            fav_final = "h"

        red_fav = stats.get(f"red_cards_{fav_final}", 0) if stats else 0

        # Placar do favorito e adversário
        fav_gols = sh if fav_final == "h" else sa
        adv_gols = sa if fav_final == "h" else sh

        # Favorito empatando = placar igual
        fav_empatando = (sh == sa)
        # Favorito perdendo por exatamente 1 gol (qualquer placar)
        fav_perdendo_1 = (adv_gols - fav_gols) == 1
        # Condição escanteio: fav empatando OU perdendo por no máximo 1 gol
        corner_valido = fav_empatando or fav_perdendo_1
        # Over 1.5 FT: placares válidos APENAS 1x0 ou 0x1 (fav perdendo por 1, total = 1 gol)
        fav_gols_oft = sh if fav_final == "h" else sa
        adv_gols_oft = sa if fav_final == "h" else sh
        oft_valido = (
            (adv_gols_oft - fav_gols_oft) == 1 and
            (sh + sa) == 1
        )

        # MERCADO 1: OVER 0.5 HT (15-27 min, 0x0, favorito empatando, sem vermelho do fav)
        if p == 1 and 15 <= m <= 27 and stot == 0 and fav_empatando and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_ht_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 3, "HT", "Over 0.5 HT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "HT", h, a, mid)

        # MERCADO 2: AMBAS MARCAM BTTS (60-75 min, fav perdendo por 1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and fav_perdendo_1 and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_btts_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "BTTS", "Ambas Marcam", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "BTTS", h, a, mid)

        # MERCADO 3: OVER 1.5 FT (60-75 min, fav empatando ou perdendo por 1, placares: 0x0/1x0/0x1/1x1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and oft_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_oft_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OFT", "Over 1.5 FT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OFT", h, a, mid)

        # MERCADO 4: OVER 0.5 FT (60-75 min, 0x0, favorito empatando, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and stot == 0 and fav_empatando and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_overgoal_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OVERGOAL", "Over 0.5 FT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OVERGOAL", h, a, mid)

        # MERCADO 5: ESCANTEIO LIMITE HT (30-38 min, fav confirmado, empatando ou perdendo por 1, sem vermelho)
        if p == 1 and 30 <= m <= 38 and fav_confirmado and corner_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_cht_{hoje}"
            cantos_h = stats.get("escanteios_h", 0) if stats else 0
            cantos_a = stats.get("escanteios_a", 0) if stats else 0
            cantos = max(0, cantos_h) + max(0, cantos_a)  # -1 vira 0
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_HT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_HT", h, a, mid, extra_val=cantos)

        # MERCADO 6: ESCANTEIO LIMITE FT (80-88 min, fav confirmado, empatando ou perdendo por 1, sem vermelho)
        if p == 2 and 80 <= m <= 88 and fav_confirmado and corner_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_cft_{hoje}"
            cantos_h = stats.get("escanteios_h", 0) if stats else 0
            cantos_a = stats.get("escanteios_a", 0) if stats else 0
            cantos = max(0, cantos_h) + max(0, cantos_a)  # -1 vira 0
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_FT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key)
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
