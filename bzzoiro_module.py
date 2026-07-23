"""
bzzoiro_module.py — Módulo de integração com a API Bzzoiro v2
Fonte PRINCIPAL de dados para o Bot Máquina de Greens

API: https://sports.bzzoiro.com/api/v2/
Token: {{credential:BZZOIRO_TOKEN}} ou env var BZZOIRO_TOKEN

Dados fornecidos:
  - Eventos ao vivo (1st_half, 2nd_half)
  - Stats detalhados: dangerous_attack, corner_kicks, attack, ball_possession, cards
  - Incidentes: gols, cartões
  - Odds via endpoint /odds/
"""

import os, json, requests, time, hashlib, re, unicodedata
from datetime import datetime, timezone, timedelta

BZZOIRO_BASE = "https://sports.bzzoiro.com/api/v2"
BZZOIRO_TOKEN = os.getenv("BZZOIRO_TOKEN", "a6b76b2ca04a56cbf4f1339acbc3597724d2e590")
BZZOIRO_HEADERS = {
    "Authorization": f"Token {BZZOIRO_TOKEN}",
    "User-Agent": "Mozilla/5.0"
}

BRT = timezone(timedelta(hours=-3))


def _req(path, params=None, timeout=8):
    """Faz requisição à API Bzzoiro v2."""
    url = f"{BZZOIRO_BASE}/{path}"
    try:
        r = requests.get(url, headers=BZZOIRO_HEADERS, params=params, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        print(f"[BZZOIRO] HTTP {r.status_code} para {url}")
        return None
    except Exception as e:
        print(f"[BZZOIRO] Erro req {url}: {e}")
        return None


def get_jogos_bzzoiro(fids_existentes=None):
    """
    Busca TODOS os jogos ao vivo via Bzzoiro v2.
    Retorna lista de jogos no formato padronizado do bot.
    """
    jogos = []
    
    # Busca jogos do 1º e 2º tempo
    for status in ("1st_half", "2nd_half"):
        data = _req("events/", params={"status": status, "limit": 100})
        if not data:
            continue
        
        for ev in data.get("results", []):
            eid = ev.get("id")
            home = ev.get("home_team", "")
            away = ev.get("away_team", "")
            if not home or not away:
                continue
            
            minuto = ev.get("current_minute") or 0
            period = ev.get("period", "")
            sh = int(ev.get("home_score") or 0)
            sa = int(ev.get("away_score") or 0)
            league_id = ev.get("league_id", 0)
            
            # Determinar período (1 ou 2)
            p = 2 if "2" in str(period) else 1
            
            # Nome da liga via league_id
            liga = _get_league_name(league_id)
            
            jogos.append({
                "fid": f"bzz_{eid}",
                "fid_raw": str(eid),
                "home": home,
                "away": away,
                "sh": sh,
                "sa": sa,
                "minuto": minuto,
                "period": p,
                "liga": liga,
                "source": "bzzoiro",
                "league_id": league_id,
                "odd_h": None,
                "odd_a": None,
                "odds_b365": {},
                "odds_bano": {}
            })
    
    print(f"[BZZOIRO] {len(jogos)} jogos ao vivo encontrados")
    return jogos


_LEAGUE_CACHE = {}
def _get_league_name(league_id):
    """Busca nome da liga pelo ID (com cache)."""
    if not league_id:
        return "Liga Não Identificada"
    if league_id in _LEAGUE_CACHE:
        return _LEAGUE_CACHE[league_id]
    
    try:
        data = _req(f"leagues/{league_id}/")
        if data:
            name = data.get("name", "Liga Não Identificada")
            country = data.get("country", "")
            full = f"{name}" if not country else f"{name} ({country})"
            _LEAGUE_CACHE[league_id] = full
            return full
    except:
        pass
    
    _LEAGUE_CACHE[league_id] = "Liga Não Identificada"
    return "Liga Não Identificada"


def get_stats_bzzoiro(fid_raw):
    """
    Busca estatísticas detalhadas de uma partida via Bzzoiro v2.
    
    Retorna dict no formato:
    {
        "chutes_tot_h": int, "chutes_tot_a": int,
        "chutes_gol_h": int, "chutes_gol_a": int,
        "escanteios_h": int, "escanteios_a": int,
        "ataques_perigosos_h": int, "ataques_perigosos_a": int,
        "posse_h": int, "posse_a": int,
        "yellow_cards_h": int, "yellow_cards_a": int,
        "red_cards_h": int, "red_cards_a": int,
        "faltas_h": int, "faltas_a": int,
        "ataques_tot_h": int, "ataques_tot_a": int,
        "appm_h": float, "appm_a": float,
        "minuto": int
    }
    """
    stats = {}
    try:
        data = _req(f"events/{fid_raw}/stats/")
        if not data:
            return stats
        
        s = data.get("stats", {})
        home = s.get("home", {})
        away = s.get("away", {})
        
        # Só considera se tiver dados reais
        if not home or not away:
            return stats
        
        # ✅ Bzzoiro v2 AGORA TEM dados de chutes nativos (total_shots, shots_on_target).
        #    Extrai direto sem depender de fallback ESPN/Promiedos.
        stats["chutes_tot_h"] = int(home.get("total_shots", 0) or 0)
        stats["chutes_tot_a"] = int(away.get("total_shots", 0) or 0)
        stats["chutes_gol_h"] = int(home.get("shots_on_target", 0) or 0)
        stats["chutes_gol_a"] = int(away.get("shots_on_target", 0) or 0)
        
        # Campos diretos da Bzzoiro
        stats["escanteios_h"] = int(home.get("corner_kicks", 0) or 0)
        stats["escanteios_a"] = int(away.get("corner_kicks", 0) or 0)
        
        # ⭐ DANGEROUS ATTACK REAL — sem cálculo sintético
        stats["ataques_perigosos_h"] = int(home.get("dangerous_attack", 0) or 0)
        stats["ataques_perigosos_a"] = int(away.get("dangerous_attack", 0) or 0)
        
        stats["ataques_tot_h"] = int(home.get("attack", 0) or 0)
        stats["ataques_tot_a"] = int(away.get("attack", 0) or 0)
        
        stats["posse_h"] = int(home.get("ball_possession", 0) or 0)
        stats["posse_a"] = int(away.get("ball_possession", 0) or 0)
        
        stats["yellow_cards_h"] = int(home.get("yellow_cards", 0) or 0)
        stats["yellow_cards_a"] = int(away.get("yellow_cards", 0) or 0)
        
        stats["red_cards_h"] = int(home.get("red_cards", 0) or 0)
        stats["red_cards_a"] = int(away.get("red_cards", 0) or 0)
        
        stats["faltas_h"] = int(home.get("free_kicks", 0) or 0)
        stats["faltas_a"] = int(away.get("free_kicks", 0) or 0)
        
        # APPM (Ataques Perigosos Por Minuto)
        stats["appm_h"] = home.get("dangerous_attack_pct", 0) or 0
        stats["appm_a"] = away.get("dangerous_attack_pct", 0) or 0
        stats["minuto"] = 0  # será preenchido pelo caller
        
        print(f"[BZZOIRO-STATS] OK: esc {stats['escanteios_h']}x{stats['escanteios_a']} | atq_perig {stats['ataques_perigosos_h']}x{stats['ataques_perigosos_a']} | posse {stats['posse_h']}%/{stats['posse_a']}%")
        return stats
        
    except Exception as e:
        print(f"[BZZOIRO-STATS ERRO] {e}")
        return stats


def get_odds_bzzoiro(fid_raw):
    """
    Busca odds de um jogo via Bzzoiro v2.
    Mercado: 1x2 (HOME/DRAW/AWAY) — é o que a API retorna.
    Retorna (odd_h, odd_a) ou (None, None).
    """
    try:
        data = _req("odds/", params={"event_id": fid_raw, "limit": 20})
        if not data:
            return None, None
        
        odds_h = []
        odds_a = []
        for o in data.get("results", []):
            market = o.get("market", "")
            outcome = o.get("outcome", "")
            decimal = o.get("decimal_odds")
            
            if market == "1x2":
                if outcome == "HOME":
                    odds_h.append(decimal)
                elif outcome == "AWAY":
                    odds_a.append(decimal)
        
        # Pega a menor odd (melhor valor) para cada lado
        odd_h = min(odds_h) if odds_h else None
        odd_a = min(odds_a) if odds_a else None
        
        return odd_h, odd_a
    except Exception as e:
        print(f"[BZZOIRO-ODDS ERRO] {e}")
        return None, None


def checar_resultado_bzzoiro(sinal):
    """
    Verifica resultado de um sinal usando Bzzoiro v2.
    Similar à checar_resultado() do bot_refactor mas usando Bzzoiro.
    Retorna "green", "red" ou None (ainda pendente).
    """
    try:
        fid_raw = str(sinal.get("fixture_id", "")).replace("bzz_", "")
        mercado = sinal.get("mercado")
        
        # Dados do evento
        data = _req(f"events/{fid_raw}/")
        if not data:
            return None
        
        status = data.get("status", "")
        period = data.get("period", "")
        current_min = data.get("current_minute") or 0
        
        # Verificar se terminou ou está no 2º tempo
        is_final = (status == "finished")
        is_2h = ("2" in str(period))
        
        if not (is_final or (mercado in ["HT", "LIMITEHT", "CORNER_HT"] and is_2h)):
            return None
        
        # Placar
        gh = int(data.get("home_score") or 0)
        ga = int(data.get("away_score") or 0)
        total_final = gh + ga
        
        # Placar HT
        gh_ht = int(data.get("home_score_ht") or 0)
        ga_ht = int(data.get("away_score_ht") or 0)
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
            stats = get_stats_bzzoiro(fid_raw)
            if stats:
                c_final = max(0, stats.get("escanteios_h", 0)) + max(0, stats.get("escanteios_a", 0))
                c_entrada = sinal.get("extra_val", 0)
                if c_final > c_entrada:
                    return "green"
                if is_final:
                    return "red"
            return None
        
        return None
    except Exception as e:
        print(f"[BZZOIRO-CHECK ERRO] {e}")
        return None