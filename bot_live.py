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
TELEGRAM_TOKEN  = os.environ.get("TG_TOKEN", "")
CHAT_IDS        = [os.environ.get("TG_GROUP_ID", "")]  # BOOT IA INTELIGENTE (Zapia)
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
    "x-rapidapi-key":  RAPIDAPI_KEY,
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg, botoes=True, reply_to=None, marca=None, home="", away=""):
    url_send = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {"chat_id": chat_id, "text": msg, "parse_mode": "HTML"}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if botoes:
            import urllib.parse
            query = urllib.parse.quote(f"{home} vs {away}") if home and away else ""
            bet365_url   = "https://www.bet365.com/"
            paripesa_url = "https://paripesa.com/"
            payload["reply_markup"] = json.dumps({"inline_keyboard": [[
                {"text": "🟣 BET365",   "url": bet365_url},
                {"text": "🔵 PARIPESA", "url": paripesa_url}
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
SENT_API_PATH      = "sent_live_signals.json"
RESULTADO_API_PATH = "resultados.json"

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

def get_relatorio_hoje():
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    greens, reds = 0, 0
    registros = _load_resultados_github()
    for r in registros:
        if r.get("data") == hoje:
            if r.get("resultado") == "green": greens += 1
            else: reds += 1
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
# API 1B — API-Football: jogos ao vivo (preenche o que a ESPN não cobre)
# ═══════════════════════════════════════════════════════════════════════════════
def get_jogos_apifootball(fids_espn):
    """Busca todos os jogos ao vivo na API-Football e retorna os que ESPN não tem."""
    for key in API_FOOTBALL_KEYS:
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
                print(f"[API-Football] Chave {key[:8]}... sem acesso: {erros}")
                continue
            fixtures = rjson.get("response", [])
            if not fixtures:
                print(f"[API-Football] Chave {key[:8]}... retornou 0 jogos")
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
            print(f"[API-Football] {len(jogos)} jogos novos (chave {key[:8]}...)")
            return jogos
        except Exception as e:
            print(f"[API-Football] Erro chave {key[:8]}...: {e}")
            continue
    print("[API-Football] Todas as chaves falharam")
    return []


# ═══════════════════════════════════════════════════════════════════════════════
# API-Football: estatísticas de um jogo específico
# ═══════════════════════════════════════════════════════════════════════════════
def get_stats_apifootball_live(fid):
    """Busca stats ao vivo de um fixture da API-Football."""
    for key in API_FOOTBALL_KEYS:
        try:
            r = requests.get(
                f"{API_FOOTBALL_URL}/fixtures",
                params={"id": fid},
                headers={"x-apisports-key": key},
                timeout=10
            )
            rjson = r.json()
            data = rjson.get("response", [])
            if not data:
                continue
            f = data[0]
            stats = {}
            # Estatísticas detalhadas
            r2 = requests.get(
                f"{API_FOOTBALL_URL}/fixtures/statistics",
                params={"fixture": fid},
                headers={"x-apisports-key": key},
                timeout=10
            )
            r2json = r2.json()
            stat_data = r2json.get("response", [])
            if stat_data:
                home_id = stat_data[0]["team"]["id"]
                for team in stat_data:
                    side = "h" if team["team"]["id"] == home_id else "a"
                    for s in team["statistics"]:
                        k   = s["type"].lower().replace(" ", "_")
                        val = s["value"] or 0
                        if k == "corner_kicks":  stats[f"escanteios_{side}"] = val
                        if k == "total_shots":   stats[f"chutes_tot_{side}"]  = val
                        if k == "shots_on_goal": stats[f"chutes_gol_{side}"]  = val
                # Cartões vermelhos via events
                r3 = requests.get(
                    f"{API_FOOTBALL_URL}/fixtures/events",
                    params={"fixture": fid},
                    headers={"x-apisports-key": key},
                    timeout=10
                )
                events = r3.json().get("response", [])
                red_h, red_a = 0, 0
                for ev in events:
                    if ev.get("type") == "Card" and "Red" in (ev.get("detail") or ""):
                        if ev.get("team", {}).get("id") == home_id: red_h += 1
                        else: red_a += 1
                stats["red_cards_h"], stats["red_cards_a"] = red_h, red_a
            # Garante defaults
            for side in ["h", "a"]:
                for k in ["chutes_tot", "chutes_gol", "red_cards"]:
                    stats.setdefault(f"{k}_{side}", 0)
                stats.setdefault(f"escanteios_{side}", -1)
                stats.setdefault(f"posse_{side}", 0.0)
                stats.setdefault(f"passes_precisos_{side}", 0)
            stats["fav_side"] = "h" if stats.get("chutes_tot_h", 0) >= stats.get("chutes_tot_a", 0) else "a"
            print(f"[API-Football Stats] fixture {fid} OK")
            return stats
        except Exception as e:
            print(f"[API-Football Stats] Erro: {e}")
            continue
    return {}


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
    """Retorna 'h' ou 'a' baseado na menor odd. Prioridade: 1.ESPN, 2.APIFootball, 3.Bzzoiro."""
    # 1. Tenta ESPN (grátis)
    if fid and league:
        try:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league}/scoreboard"
            r = requests.get(url, timeout=6)
            for ev in r.json().get("events", []):
                comp = ev.get("competitions", [{}])[0]
                if str(comp.get("id", "")) != str(fid): continue
                for odd in comp.get("odds", []):
                    ml = odd.get("moneyline", {})
                    if ml:
                        def _get_ml(side):
                            for key in ("close", "open", "current"):
                                v = ml.get(side, {}).get(key, {}).get("odds")
                                if v: return v
                            return 99
                        odd_h, odd_a = _moneyline_to_decimal(_get_ml("home")), _moneyline_to_decimal(_get_ml("away"))
                        if odd_h < 90 and odd_a < 90:
                            fav = "h" if odd_h <= odd_a else "a"
                            print(f"[ODDS-ESPN] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                            return fav
        except: pass

    # 2. Fallback APIfootball.com (v3)
    if fid and str(fid).startswith("apfc_"):
        try:
            match_id = str(fid).replace("apfc_","")
            r = requests.get("https://apiv3.apifootball.com/", params={"action": "get_odds", "match_id": match_id, "APIkey": APIFOOTBALL_COM_KEY}, timeout=8)
            odds_data = r.json()
            if isinstance(odds_data, list) and odds_data:
                odd = odds_data[0]
                odd_h, odd_a = float(odd.get("odd_1", 0) or 0), float(odd.get("odd_2", 0) or 0)
                if odd_h > 1 and odd_a > 1:
                    fav = "h" if odd_h <= odd_a else "a"
                    print(f"[ODDS-APFC] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                    return fav
        except: pass

    # 3. Fallback Bzzoiro Odds
    if fid and str(fid).startswith("bzz_"):
        try:
            fid_raw = str(fid).replace("bzz_", "")
            headers = {"Authorization": "Token " + BZZOIRO_TOKEN}
            r = requests.get(f"{BZZOIRO_URL}/api/v2/events/{fid_raw}/odds/pre-live/", headers=headers, timeout=8)
            if r.status_code == 200:
                data = r.json()
                for mkt in data.get("odds", []):
                    if mkt.get("name") in ("1x2", "Full Time Result"):
                        choices = {c.get("name"): float(c.get("value", 99)) for c in mkt.get("choices", [])}
                        odd_h, odd_a = choices.get("1", 99), choices.get("2", 99)
                        if odd_h < 90 and odd_a < 90:
                            fav = "h" if odd_h <= odd_a else "a"
                            print(f"[ODDS-BZZ] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                            return fav
        except: pass

    return None

# ═══════════════════════════════════════════════════════════════════════════════
# FILTRO DE JANELAS
# ═══════════════════════════════════════════════════════════════════════════════
def get_odd_favorito_num(home, away, fid=None, league=None):
    """Retorna a odd decimal do favorito (numero). Prioridade: 1.ESPN, 2.APIFootball, 3.Bzzoiro."""
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
    sep = "━━━━━━━━━━━━━━━━━━━━"
    if not stats: stats = {}
    cg_h, cg_a = stats.get("chutes_gol_h", 0), stats.get("chutes_gol_a", 0)
    ct_h, ct_a = stats.get("chutes_tot_h", 0), stats.get("chutes_tot_a", 0)
    cf_h, cf_a = max(0, ct_h - cg_h), max(0, ct_a - cg_a)
    ap_h, ap_a = stats.get("atq_perigosos_h", stats.get("dangerous_attacks_h", 0)), stats.get("atq_perigosos_a", stats.get("dangerous_attacks_a", 0))
    pos_h, pos_a = stats.get("posse_h", 50), stats.get("posse_a", 50)
    esc_h, esc_a = stats.get("escanteios_h", 0), stats.get("escanteios_a", 0)
    if "CORNER" in mercado:
        linha = cantos_atual + 0.5
        entrada = f"Mais de {linha} Cantos"
    titles = {
        "HT": "⚽️🔥<b>OVER GOL INTERVALO</b>🔥⚽️",
        "BTTS": "⚽️🔥<b>AMBAS MARCAM</b>🔥⚽️",
        "OFT": "⚽️🔥<b>OVER 1.5 GOLS PARTIDA</b>🔥⚽️",
        "OVERGOAL": "⚽️🔥<b>OVER GOL PARTIDA</b>🔥⚽️",
        "LIMITEHT": "⚽️🔥<b>OVER GOL LIMITE HT</b>🔥⚽️",
        "CORNER_HT": "⛳️🔥<b>ESCANTEIO LIMITE HT</b>🔥⛳️",
        "CORNER_FT": "⛳️🔥<b>ESCANTEIO LIMITE FT</b>🔥⛳️"
    }
    title = titles.get(mercado, f"⚽️🔥<b>{mercado}</b>🔥⚽️")
    eb = (f"🎯 Chutes no Gol: <b>{cg_h} - {cg_a}</b>\n"
          f"🚀 Chutes Fora: <b>{cf_h} - {cf_a}</b>\n"
          f"🔥 Ataques Perigosos: <b>{ap_h} - {ap_a}</b>\n"
          f"📈 Posse de Bola: <b>{pos_h}% - {pos_a}%</b>\n"
          f"⛳ Escanteios: <b>{esc_h} - {esc_a}</b>")
    msg = (f"{sep}\n{title}\n"
           f"⚽️ Placar: <b>{placar}</b>\n"
           f"🌏 Liga: <b>{liga}</b>\n"
           f"📡 <b>{home}</b> x <b>{away}</b>\n"
           f"⏰️ Minuto: <b>{minuto}</b>\n{sep}\n"
           f"📊 <b>Análise ao Vivo da Entrada:</b>\n{eb}\n"
           f"💰 Odd Mínima Recomendada: <b>1.70</b>\n{sep}\n")
    if "CORNER" in mercado: msg += f"⛳️ Escanteios Atuais: <b>{cantos_atual}</b>\n"
    msg += f"📌 Entrada: <b>{entrada}</b>\n✅ Critérios: <b>{n}/6</b>\n{sep}\n⚠️Jogue com responsabilidade⚠️"
    return msg
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
        elif mercado == "LIMITEHT":
            linescore = competitors[0].get("linescores", [])
            ht_total  = sum(int(l.get("displayValue", 0) or 0) for l in linescore[:1])
            return "green" if ht_total >= 1 else "red"
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
            chat_id = str(msg.get("chat", {}).get("id", ""))
            msg_ts  = msg.get("date", 0)
            # Ignora comandos com mais de 30 minutos (evita processar acúmulo muito antigo)
            if agora_ts - msg_ts > 1800:
                continue
            if chat_id not in [str(c) for c in CHAT_IDS]:
                continue
            if text == "/relatorio" and not relatorio_respondido:
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
                    linhas_janela = "Nenhum jogo na janela no momento.\n"
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
                        linhas_fora += f"... e mais {len(fora_janela)-10} jogos\n"
                else:
                    linhas_fora = "—\n"
                msg_radar = (
                    f"{sep}\n📡 <b>RADAR AO VIVO</b> 📡\n{sep}\n"
                    f"🔴 <b>{total_jogos_live} jogos ao vivo</b>\n"
                    f"🎯 <b>{len(jogos_na_janela)} na janela alvo</b>\n"
                    f"{sep}\n"
                    f"<b>🎯 NA JANELA:</b>\n{linhas_janela}"
                    f"{sep}\n"
                    f"<b>⏳ FORA DA JANELA:</b>\n{linhas_fora}"
                    f"{sep}"
                )
                send_telegram(msg_radar, botoes=False)
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
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def run():
    print("[Iniciando monitoramento — ESPN + API-Football + Odds API]")
    sent      = load_sent()
    total_env = 0
    # janela_id por hora — evita duplicata mesmo se Actions rodar 2x no mesmo minuto
    janela_id = datetime.now(BRT).strftime('%Y%m%d%H')

    # PASSO 1A: ESPN busca todos os jogos ao vivo
    jogos_espn = get_jogos_espn()
    fids_espn  = {j["fid"] for j in jogos_espn}

    # PASSO 1B: API-Football preenche o que ESPN não cobre
    jogos_apif = get_jogos_apifootball(fids_espn)

    # Junta tudo — ESPN tem prioridade (stats mais ricas via summary)
    jogos_live = jogos_espn + jogos_apif
    print(f"[Total] {len(jogos_live)} jogos ao vivo (ESPN={len(jogos_espn)} + API-Football=0)")

    # PASSO 2: Filtra janelas alvo
    jogos_na_janela = filtrar_janelas(jogos_live)
    print(f"[Janela] {len(jogos_na_janela)} jogos nas janelas alvo")

    check_status_command(total_jogos_live=len(jogos_live), jogos_live=jogos_live, jogos_na_janela=jogos_na_janela)

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

        # Busca stats UMA vez — reutiliza para tudo (fonte depende da origem do jogo)
        source = j.get("source", "espn")
        if source == "apifootball":
            stats = get_stats_apifootball_live(fid)
        else:
            stats = get_stats_espn(fid, h, a)
            if stats: j.update(stats)

        # Verifica se tem dados reais — sem stats E sem odds, pula o jogo
        tem_stats = stats and (
            stats.get("chutes_tot_h", 0) > 0 or
            stats.get("chutes_tot_a", 0) > 0 or
            stats.get("escanteios_h", -1) >= 0 or
            stats.get("escanteios_a", -1) >= 0
        )

        # Determinar favorito pelas odds (ESPN primeiro, depois Odds API)
        fav_final = get_favorito_odds(h, a, fid=fid, league=j.get("liga_slug", j.get("liga", "")))
        fav_por_odds = fav_final in ("h", "a")

        # Sem odds = favorito indefinido (regra restrita por odds pré-live)
        if not fav_por_odds:
            fav_final = None
            print(f"[FAV-SKIP] {h} x {a} — sem odds disponíveis")

        red_fav = stats.get(f"red_cards_{fav_final}", 0) if stats else 0

        # Placar do favorito e adversário
        fav_gols = sh if fav_final == "h" else sa
        adv_gols = sa if fav_final == "h" else sh

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

        # MERCADO 1: OVER 0.5 HT (15-27 min, 0x0, favorito empatando, sem vermelho do fav)
        if p == 1 and 15 <= m <= 27 and fav_por_odds and fav_empatando and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_ht_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 3, "HT", "Over 0.5 HT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "HT", h, a, mid)

        # MERCADO 1B: OVER GOL LIMITE HT (15-25 min, 0x0, odd fav ≤ 1.50, prob 1.5 FT ≥ 75%, prob 0.5 HT ≥ 65%, APPM fav ≥ 1)
        if p == 1 and 15 <= m <= 25 and red_fav == 0:
            odd_fav_num = get_odd_favorito_num(h, a, fid=fid, league=j.get("liga_slug", j.get("liga", "")))
            chutes_tot_total = (stats.get("chutes_tot_h", 0) + stats.get("chutes_tot_a", 0)) if stats else 0
            chutes_gol_total = (stats.get("chutes_gol_h", 0) + stats.get("chutes_gol_a", 0)) if stats else 0
            chutes_gol_fav   = stats.get(f"chutes_gol_{fav_final}", 0) if stats else 0
            prob_15_ft, prob_05_ht = calcular_prob_gols_ht(chutes_tot_total, chutes_gol_total, m)
            appm_fav = chutes_gol_fav
            print(f"[LIMITE-HT] {h} x {a} | odd_fav={odd_fav_num} | prob_15ft={prob_15_ft}% | prob_05ht={prob_05_ht}% | appm={appm_fav}")
            if (odd_fav_num <= 1.50 and prob_15_ft >= 75 and prob_05_ht >= 65 and appm_fav >= 1):
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                key = f"{fid}_limiteht_{hoje}"
                if key not in sent:
                    mid = send_telegram(msg_universal(h, a, m, liga, 4, "LIMITEHT", "Over 0.5 HT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                    if mid:
                        sent.add(key); total_env += 1
                        registrar_sinal(fid, "LIMITEHT", h, a, mid)

        # MERCADO 2: AMBAS MARCAM BTTS (60-75 min, fav perdendo por 1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and fav_por_odds and fav_perdendo_1 and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_btts_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "BTTS", "Ambas Marcam", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "BTTS", h, a, mid)

        # MERCADO 3: OVER 1.5 FT (60-75 min, fav empatando ou perdendo por 1, placares: 0x0/1x0/0x1/1x1, sem vermelho do fav)
        if p == 2 and 60 <= m <= 75 and fav_por_odds and oft_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_oft_{hoje}"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OFT", "Over 1.5 FT", placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OFT", h, a, mid)

        # MERCADO 4: OVER GOL PARTIDA (60-75 min, placares 0x0/1x1/0x1/1x0, favorito empatando ou perdendo por 1)
        overgoal_placar = (sh == 0 and sa == 0) or (sh == 1 and sa == 1) or (sh == 0 and sa == 1) or (sh == 1 and sa == 0)
        # 0x0 e 1x1 = sempre validos; 1x0 e 0x1 exigem favorito empatando ou perdendo por 1
        overgoal_valido = overgoal_placar and ((sh == 0 and sa == 0) or (sh == 1 and sa == 1) or fav_empatando or fav_perdendo_1)
        if p == 2 and 60 <= m <= 75 and fav_por_odds and overgoal_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_overgoal_{hoje}"
            # Linha dinâmica: sempre acima do total de gols atual
            total_gols = sh + sa
            if total_gols == 0:
                linha_over = "Over 0.5 FT"
            elif total_gols == 1:
                linha_over = "Over 1.5 FT"
            elif total_gols == 2:
                linha_over = "Over 2.5 FT"
            elif total_gols == 3:
                linha_over = "Over 3.5 FT"
            else:
                linha_over = f"Over {total_gols + 0.5:.1f} FT"
            if key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 4, "OVERGOAL", linha_over, placar, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "OVERGOAL", h, a, mid)

        # MERCADO 5: ESCANTEIO LIMITE HT (30-38 min, fav confirmado, empatando ou perdendo por 1, sem vermelho)
        if p == 1 and 30 <= m <= 38 and fav_por_odds and corner_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_cht_{hoje}"
            cantos_h = stats.get("escanteios_h", -1) if stats else -1
            cantos_a = stats.get("escanteios_a", -1) if stats else -1
            cantos = (max(0, cantos_h) + max(0, cantos_a)) if (cantos_h >= 0 and cantos_a >= 0) else -1
            if cantos < 0:
                print(f"[SKIP-CORNER-HT] {h} x {a} — escanteios sem dado real, pulando")
            elif key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_HT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
                if mid:
                    sent.add(key); total_env += 1
                    registrar_sinal(fid, "CORNER_HT", h, a, mid, extra_val=cantos)

        # MERCADO 6: ESCANTEIO LIMITE FT (80-88 min, fav confirmado, empatando ou perdendo por 1, sem vermelho)
        if p == 2 and 80 <= m <= 88 and fav_por_odds and corner_valido and red_fav == 0:
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{fid}_cft_{hoje}"
            cantos_h = stats.get("escanteios_h", -1) if stats else -1
            cantos_a = stats.get("escanteios_a", -1) if stats else -1
            cantos = (max(0, cantos_h) + max(0, cantos_a)) if (cantos_h >= 0 and cantos_a >= 0) else -1
            if cantos < 0:
                print(f"[SKIP-CORNER-FT] {h} x {a} — escanteios sem dado real, pulando")
            elif key not in sent:
                mid = send_telegram(msg_universal(h, a, m, liga, 5, "CORNER_FT", "", placar, cantos_atual=cantos, stats=stats, sh=sh, sa=sa, fav_final=fav_final), marca=key, home=h, away=a)
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
                emoji = "🟢 GREEN CONFIRMADO 🟢" if res == "green" else "🔴 RED CONFIRMADO 🔴"
                send_telegram(emoji, botoes=False, reply_to=s.get("message_id"))
                salvar_resultado(res)
            else:
                rest.append(s)
        _save_sinais_github(rest)
        print(f"[SINAIS] {len(sinais_p) - len(rest)} resultados confirmados, {len(rest)} ainda pendentes")
    except Exception as e:
        print(f"[SINAIS] Erro validação: {e}")

    print(f"Finalizado. Enviados: {total_env}")

if __name__ == "__main__":
    run()

