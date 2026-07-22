#!/usr/bin/env python3
"""
Módulo Promiedos — API de futebol ao vivo com odds pré-live e ao vivo.
Endpoint: https://api.promiedos.com.ar
Header: X-VER: 1.11.7.5
"""

import os, json, requests, time, hashlib, unicodedata
from datetime import datetime, timezone, timedelta

PROMIEDOS_BASE = "https://api.promiedos.com.ar"
PROMIEDOS_HEADERS = {"X-VER": "1.11.7.5", "User-Agent": "Mozilla/5.0"}

BRT = timezone(timedelta(hours=-3))

# ─── Cache simples ───
_CACHE = {}
_CACHE_TTL = 30  # segundos

def _cache_get(key):
    if key in _CACHE:
        val, ts = _CACHE[key]
        if time.time() - ts < _CACHE_TTL:
            return val
    return None

def _cache_set(key, val):
    _CACHE[key] = (val, time.time())

# ─── Normalização de nomes (compatível com bot_refactor) ───
def norm_nome_time(nome):
    n = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower().strip()
    for prefixo in ["msk ", "hnk ", "nk ", "fk ", "sk ", "fc ", "ac ", "ss ", "as ",
                     "real ", "cd ", "ad ", "cf ", "ud ", "sd ", "cda ", "ca ",
                     "ec ", "sc ", "se ", "aa ", "ae ", "ap ", "ag ", "aa ",
                     "sociedade ", "esporte ", "clube ", "grêmio ", "sport "]:
        if n.startswith(prefixo):
            n = n[len(prefixo):]
    for sufixo in [" fc", " ac", " cf", " ud", " cd", " sc", " se", " ec",
                   " futebol", " clube", " esporte"]:
        if n.endswith(sufixo):
            n = n[:-len(sufixo)]
    n = n.replace("-", " ").replace("_", " ").replace(".", " ").strip()
    n = " ".join(n.split())
    return n


def get_jogos_promiedos(fids_existentes=None):
    """
    Retorna lista de jogos ao vivo/programados com odds pre-live.
    Formato compatível com o antigo Bzzoiro.
    """
    cache_key = "jogos_promiedos"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    try:
        r = requests.get(f"{PROMIEDOS_BASE}/games/today", headers=PROMIEDOS_HEADERS, timeout=15)
        if r.status_code != 200:
            print(f"[PROMIEDOS] Erro HTTP {r.status_code}")
            return []
        data = r.json()
        leagues = data.get("leagues", [])
        jogos = []
        seen = set()

        for liga in leagues:
            league_name = liga.get("name", "Liga Desconhecida")
            for g in liga.get("games", []):
                gid = g.get("id", "")
                if not gid:
                    continue

                teams = g.get("teams", [])
                if len(teams) < 2:
                    continue

                home = teams[0].get("name", "Time A")
                away = teams[1].get("name", "Time B")

                # Deduplicação por nome normalizado
                dedup_key = f"{norm_nome_time(home)}-{norm_nome_time(away)}"
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                # Status
                status = g.get("status", {})
                if isinstance(status, dict):
                    sym = status.get("symbol_name", "Prog.")
                else:
                    sym = "Prog."

                # Placar
                scores = g.get("scores", [0, 0])
                if isinstance(scores, list) and len(scores) >= 2:
                    sh, sa = int(scores[0] or 0), int(scores[1] or 0)
                else:
                    sh, sa = 0, 0

                # Minuto
                game_time = g.get("game_time", 0) or 0
                minuto = int(game_time) if game_time > 0 else 0

                # Período
                if sym in ("1°", "1H"):
                    period = 1
                elif sym in ("2°", "2H"):
                    period = 2
                elif sym == "HT":
                    period = 1
                elif sym == "FT":
                    continue  # Jogo já terminou, não interessa
                else:
                    period = 0  # Pré-jogo

                # Odds pré-live (main_odds)
                odds_h, odds_a = None, None
                main_odds = g.get("main_odds", {})
                options = main_odds.get("options", []) if isinstance(main_odds, dict) else []
                odds_b365 = {}
                odds_bano = {}
                for opt in options:
                    name = opt.get("name", "")
                    val = opt.get("value")
                    if name == "1":
                        odds_h = float(val) if val else None
                        odds_b365["1"] = odds_h
                        odds_bano["1"] = odds_h
                    elif name == "2":
                        odds_a = float(val) if val else None
                        odds_b365["2"] = odds_a
                        odds_bano["2"] = odds_a

                jogos.append({
                    "fid": f"prom_{gid}",
                    "fid_raw": gid,
                    "home": home,
                    "away": away,
                    "sh": sh,
                    "sa": sa,
                    "minuto": minuto,
                    "liga": league_name,
                    "period": period,
                    "source": "promiedos",
                    "odd_h": odds_h,
                    "odd_a": odds_a,
                    "odds_b365": odds_b365,
                    "odds_bano": odds_bano
                })

        print(f"[PROMIEDOS] {len(jogos)} jogos encontrados")
        _cache_set(cache_key, jogos)
        return jogos

    except Exception as e:
        print(f"[PROMIEDOS ERRO] get_jogos_promiedos: {e}")
        return []


def get_stats_promiedos(game_id):
    """
    Busca estatísticas detalhadas de uma partida via gamecenter.
    Retorna dict compatível com o formato do antigo Bzzoiro.
    """
    cache_key = f"stats_prom_{game_id}"
    cached = _cache_get(cache_key)
    if cached:
        return cached

    try:
        r = requests.get(f"{PROMIEDOS_BASE}/gamecenter/{game_id}", headers=PROMIEDOS_HEADERS, timeout=10)
        if r.status_code != 200:
            return {}
        data = r.json()
        game = data.get("game", {})
        stats_raw = game.get("statistics", [])
        if not stats_raw:
            return {}

        stats = {}

        # Mapeamento de nomes em espanhol → chaves do bot
        mapping = {
            "total remates": "chutes_tot",
            "remates al arco": "chutes_gol",
            "saques de esquina": "escanteios",
            "ataques": "ataques_totais",
            "posesión": "posse",
            "tarjetas amarillas": "yellow_cards",
            "tarjetas rojas": "red_cards",
        }

        for s in stats_raw:
            name = s.get("name", "").lower().strip()
            values = s.get("values", [])
            if len(values) < 2:
                continue
            try:
                h_val = values[0].replace("%", "").strip()
                a_val = values[1].replace("%", "").strip()
                if not h_val or not a_val:
                    continue
                key = mapping.get(name)
                if key:
                    if key == "posse":
                        h_int = int(float(h_val.replace(",", ".")))
                        a_int = int(float(a_val.replace(",", ".")))
                    else:
                        h_int = int(h_val)
                        a_int = int(a_val)
                    stats[f"{key}_h"] = h_int
                    stats[f"{key}_a"] = a_int
            except (ValueError, IndexError):
                continue

        # Se tem "Total Remates" mas não tem "Remates al arco", usa total como fallback
        if "chutes_tot_h" in stats and "chutes_gol_h" not in stats:
            stats["chutes_gol_h"] = stats["chutes_tot_h"]
            stats["chutes_gol_a"] = stats["chutes_tot_a"]

        # Se tem chutes_gol mas não tem chutes_tot, usa chutes_gol como total
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]

        # Ataques Perigosos — Promiedos NÃO tem esse campo separado.
        # O campo "Ataques" da Promiedos são ataques TOTAIS (não perigosos).
        # Usamos ataques_totais como proxy de pressão pro APPM (é o melhor que a Promiedos oferece).
        # NOTA: "ataques_totais" = total de ataques (Promiedos) — é o melhor proxy disponível
        if "ataques_totais_h" in stats:
            stats["ataques_perigosos_h"] = stats["ataques_totais_h"]
            stats["ataques_perigosos_a"] = stats["ataques_totais_a"]
        elif "chutes_tot_h" in stats and "chutes_gol_h" in stats:
            # Fallback: chutes + chutes no alvo
            stats["ataques_perigosos_h"] = stats["chutes_tot_h"] + stats["chutes_gol_h"]
            stats["ataques_perigosos_a"] = stats["chutes_tot_a"] + stats["chutes_gol_a"]
        else:
            stats["ataques_perigosos_h"] = 0
            stats["ataques_perigosos_a"] = 0

        # Odds do gamecenter (live_odds)
        live_odds = game.get("live_odds", {})
        if isinstance(live_odds, dict):
            odds_data = live_odds.get("odds", {})
            if isinstance(odds_data, dict):
                original = odds_data.get("original", [])
                for opt in original:
                    if opt.get("name") == "1":
                        stats["odd_h"] = float(opt["value"])
                    elif opt.get("name") == "2":
                        stats["odd_a"] = float(opt["value"])

        _cache_set(cache_key, stats)
        return stats

    except Exception as e:
        print(f"[PROMIEDOS ERRO] get_stats_promiedos({game_id}): {e}")
        return {}


def get_odds_promiedos(game_id):
    """
    Retorna odds pré-live e ao vivo de uma partida.
    Retorno: (odd_h, odd_a, dict_live_odds)
    """
    try:
        r = requests.get(f"{PROMIEDOS_BASE}/gamecenter/{game_id}", headers=PROMIEDOS_HEADERS, timeout=10)
        if r.status_code != 200:
            return None, None, {}
        data = r.json()
        game = data.get("game", {})

        # Tenta odds pré-live do gamecenter (live_odds.odds.original)
        live_odds = game.get("live_odds", {})
        if isinstance(live_odds, dict):
            odds_data = live_odds.get("odds", {})
            if isinstance(odds_data, dict):
                original = odds_data.get("original", [])
                live = odds_data.get("live", [])
                odd_h = odd_a = None
                for opt in original:
                    if opt.get("name") == "1":
                        odd_h = float(opt["value"])
                    elif opt.get("name") == "2":
                        odd_a = float(opt["value"])
                live_dict = {}
                for opt in live:
                    live_dict[opt.get("name", "")] = opt.get("value")
                if odd_h and odd_a:
                    return odd_h, odd_a, live_dict

        # Fallback: main_odds do resumo
        main_odds = game.get("main_odds", {})
        if isinstance(main_odds, dict):
            options = main_odds.get("options", [])
            odd_h = odd_a = None
            for opt in options:
                if opt.get("name") == "1":
                    odd_h = float(opt["value"])
                elif opt.get("name") == "2":
                    odd_a = float(opt["value"])
            if odd_h and odd_a:
                return odd_h, odd_a, {}

        return None, None, {}

    except Exception as e:
        print(f"[PROMIEDOS ERRO] get_odds_promiedos({game_id}): {e}")
        return None, None, {}


def checar_resultado_promiedos(sinal):
    """
    Verifica se um sinal deu green ou red usando Promiedos gamecenter.
    Compatível com a interface do antigo checar_resultado_bzzoiro.
    """
    try:
        fid_raw = str(sinal.get("fixture_id", "")).replace("prom_", "")
        mercado = sinal.get("mercado")

        r = requests.get(f"{PROMIEDOS_BASE}/gamecenter/{fid_raw}", headers=PROMIEDOS_HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        game = data.get("game", {})

        # Status
        status = game.get("status", {})
        if isinstance(status, dict):
            sym = status.get("symbol_name", "")
        else:
            sym = ""

        is_final = sym == "FT"
        is_2h = sym in ("2°", "2H") or int(game.get("game_time", 0) or 0) >= 50

        # Placar
        scores = game.get("scores", [0, 0])
        if isinstance(scores, list) and len(scores) >= 2:
            gh = int(scores[0] or 0)
            ga = int(scores[1] or 0)
        else:
            gh, ga = 0, 0
        total_final = gh + ga

        if not (is_final or (mercado in ["HT", "LIMITEHT", "CORNER_HT"] and is_2h)):
            return None

        if mercado in ["HT", "LIMITEHT"]:
            return "green" if total_final >= 1 else ("red" if (is_2h or is_final) else None)
        elif mercado == "BTTS":
            return "green" if (gh >= 1 and ga >= 1) else ("red" if is_final else None)
        elif mercado == "OFT":
            return "green" if total_final >= 2 else ("red" if is_final else None)
        elif mercado == "OVERGOAL":
            gols_entrada = sinal.get("extra_val", 0)
            return "green" if total_final > gols_entrada else ("red" if is_final else None)
        elif mercado in ["CORNER_HT", "CORNER_FT"]:
            # Busca escanteios nas estatísticas
            stats_raw = game.get("statistics", [])
            c_final = 0
            for s in stats_raw:
                if "esquina" in s.get("name", "").lower():
                    values = s.get("values", [])
                    if len(values) >= 2:
                        try:
                            c_final = int(values[0]) + int(values[1])
                        except:
                            pass
                    break
            c_entrada = sinal.get("extra_val", 0)
            if c_final > c_entrada:
                return "green"
            return "red" if is_final else None
        return None
    except Exception as e:
        print(f"[PROMIEDOS AUDIT ERRO] {e}")
        return None