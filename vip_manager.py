#!/usr/bin/env python3
"""
VIP MANAGER — Máquina de Greens VIP
Sistema de Assinatura R$ 50/mês | Integração Asaas + Telegram

SEGURO: NADA de dados sensíveis salvos no repositório.
O Asaas é o banco de dados — consultamos pagamentos RECEIVED direto da API.

Fluxo:
  1. /assinar → Gera Pix R$ 50 para o cliente
  2. Cliente paga → Asaas confirma → Bot envia link do grupo
  3. A cada execução: verifica pagamentos novos + remove expirados
  4. Expiração calculada: 30 dias a partir da data do pagamento

Uso no GitHub Actions:
  python vip_manager.py check    # Verifica novos pagamentos e ativa
  python vip_manager.py purge    # Remove expirados
  python vip_manager.py pix      # Gera Pix (interativo ou args)
  python vip_manager.py status   # Status do sistema
  python vip_manager.py divulgar # Texto de divulgação
"""

import os
import json
import sys
import time
from datetime import datetime, timedelta, timezone
import urllib.request
import urllib.error

# ========== CONFIG ==========
PRECO = 50.00
DIAS_ASSINATURA = 30
ASAAS_BASE = "https://api.asaas.com/v3"
TELEGRAM_API = "https://api.telegram.org/bot"


def get_asaas_token():
    """Retorna o token do Asaas. O token começa com $ — é literal, não é variável do bash."""
    token = os.environ.get("ASAAS_TOKEN") or os.environ.get("ASAAS_KEY") or ""
    if token:
        return token
    # Fallback: tenta ler de config.json (criado pelo setup)
    try:
        with open("config.json") as f:
            cfg = json.load(f)
            return cfg.get("asaas_token", "")
    except:
        pass
    return ""

def get_tg_token():
    return os.environ.get("TG_TOKEN") or ""

def get_tg_group_id():
    return os.environ.get("TG_GROUP_ID") or ""


# ========== API ASAAS ==========
def asaas(method, path, data=None):
    """Requisição genérica ao Asaas"""
    token = get_asaas_token()
    if not token:
        print("[ERRO] ASAAS_TOKEN não configurado")
        return None
    
    url = f"{ASAAS_BASE}{path}"
    headers = {
        "access_token": token,
        "accept": "application/json",
        "content-type": "application/json"
    }
    body = json.dumps(data).encode() if data else None
    
    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[HTTP {e.code}] {method} {path}")
        return None
    except Exception as e:
        print(f"[ERRO] {e}")
        return None


# ========== TELEGRAM ==========
def tg(method, params=None):
    """Requisição ao Telegram"""
    token = get_tg_token()
    if not token:
        return None
    url = f"{TELEGRAM_API}{token}/{method}"
    headers = {"content-type": "application/json"} if params else {}
    body = json.dumps(params).encode() if params else None
    try:
        req = urllib.request.Request(url, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except:
        return None

def criar_link_grupo():
    """Cria link de convite de 24h"""
    gid = get_tg_group_id()
    if not gid:
        return None
    r = tg("createChatInviteLink", {
        "chat_id": gid,
        "member_limit": 1,
        "expire_date": int(time.time()) + 86400
    })
    if r and r.get("ok"):
        return r["result"]["invite_link"]
    return None

def banir(gid, user_id):
    """Bane e desbane pra liberar reentrada"""
    tg("banChatMember", {"chat_id": gid, "user_id": user_id})
    tg("unbanChatMember", {"chat_id": gid, "user_id": user_id, "only_if_banned": True})

def enviar(chat_id, texto):
    """Envia mensagem"""
    return tg("sendMessage", {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    })

def enviar_grupo(texto):
    return enviar(get_tg_group_id(), texto)


# ========== LÓGICA VIP ==========

def get_membros_grupo():
    """Busca membros atuais do grupo via Telegram"""
    gid = get_tg_group_id()
    if not gid:
        return []
    
    membros = []
    r = tg("getChatAdministrators", {"chat_id": gid})
    if r and r.get("ok"):
        for adm in r["result"]:
            membros.append(str(adm["user"]["id"]))
    
    r = tg("getChatMembersCount", {"chat_id": gid})
    # Não temos como listar todos os membros de forma fácil via Bot API
    # (getChatAdministrators só pega admins)
    # Mas conseguimos remover por user_id quando sabemos quem expirou
    
    return membros

def verificar_pagamentos():
    """
    Coração do sistema:
    - Busca pagamentos PIX RECEIVED no Asaas
    - Verifica quais já foram processados (via externalReference + data)
    - Para cada novo pagamento: cria link do grupo e envia pro cliente
    - Marca como processado salvando num arquivo .processed_ids (única coisa salva)
    """
    print("🔍 Verificando novos pagamentos...")
    
    # IDs já processados (único arquivo local, só números)
    processados = set()
    try:
        with open("vip_processed.json") as f:
            processados = set(json.load(f))
    except:
        pass
    
    group_id = get_tg_group_id()
    if not group_id:
        print("❌ TG_GROUP_ID não configurado")
        return
    
    # Busca pagamentos PIX recebidos
    pagamentos = asaas("GET", "/payments?billingType=PIX&status=RECEIVED&limit=50")
    if not pagamentos or not pagamentos.get("data"):
        # Tenta CONFIRMED
        pagamentos = asaas("GET", "/payments?billingType=PIX&status=CONFIRMED&limit=50")
    
    if not pagamentos or not pagamentos.get("data"):
        print("📭 Nenhum pagamento novo")
        return
    
    novos = 0
    for pag in pagamentos["data"]:
        pid = pag.get("id", "")
        if pid in processados:
            continue
        
        telegram_id = pag.get("externalReference", "")
        nome = pag.get("customerName", "Cliente")
        valor = pag.get("value", 0)
        data_pag = pag.get("paymentDate", pag.get("clientPaymentDate", ""))
        
        if not telegram_id or not telegram_id.strip():
            continue
        
        # Calcula expiração (30 dias a partir do pagamento)
        try:
            dt_pag = datetime.fromisoformat(data_pag.replace("Z", "+00:00"))
        except:
            dt_pag = datetime.now(timezone.utc)
        
        expiracao = dt_pag + timedelta(days=DIAS_ASSINATURA)
        
        # Gera link do grupo
        link = criar_link_grupo()
        if not link:
            print(f"⚠️ Não foi possível gerar link para {nome}")
            continue
        
        # Envia mensagem pro cliente
        msg = (
            f"🎉 <b>Pagamento confirmado!</b>\n\n"
            f"Olá <b>{nome}</b>, sua assinatura <b>Máquina de Greens VIP</b> foi ativada!\n\n"
            f"📅 <b>Validade:</b> até {expiracao.strftime('%d/%m/%Y')}\n"
            f"💰 <b>Valor:</b> R$ {valor:.2f}\n\n"
            f"👇 <b>Entre no grupo VIP:</b>\n"
            f"{link}\n\n"
            f"⚠️ Link expira em 24h. Se vencer, solicite um novo."
        )
        enviar(telegram_id, msg)
        
        # Avisa no grupo
        enviar_grupo(
            f"🎉 <b>NOVO MEMBRO VIP!</b>\n\n"
            f"👤 <b>{nome}</b>\n"
            f"💰 R$ {valor:.2f} confirmado ✅\n"
            f"📅 Válido até {expiracao.strftime('%d/%m/%Y')}\n\n"
            f"Bem-vindo à Máquina de Greens VIP! 🚀"
        )
        
        processados.add(pid)
        novos += 1
        print(f"✅ {nome} ativado — pago em {data_pag[:10]}")
    
    # Salva IDs processados
    with open("vip_processed.json", "w") as f:
        json.dump(list(processados), f, indent=2)
    
    print(f"🎯 {novos} novo(s) assinante(s) ativado(s)")
    return novos


def verificar_expirados():
    """
    Remove quem está no grupo mas não renovou.
    
    Estratégia: 
    - Busca todos os pagamentos RECEIVED do Asaas (últimos 90 dias)
    - Pra cada telegram_id, verifica se tem pagamento < 30 dias
    - Se não tem: expirou
    - Remove do grupo
    """
    print("🔍 Verificando expirados...")
    
    group_id = get_tg_group_id()
    if not group_id:
        return
    
    # Busca TODOS os pagamentos RECEIVED dos últimos 90 dias
    todos = asaas("GET", "/payments?billingType=PIX&status=RECEIVED&limit=100")
    if not todos or not todos.get("data"):
        print("📭 Nenhum pagamento encontrado")
        return
    
    # Agrupa por telegram_id: pega o pagamento mais recente de cada um
    assinantes = {}  # telegram_id -> {nome, data_pagamento, expiracao}
    hoje = datetime.now(timezone.utc)
    
    for pag in todos["data"]:
        tid = pag.get("externalReference", "")
        if not tid or not tid.strip():
            continue
        
        try:
            dp = pag.get("paymentDate", pag.get("clientPaymentDate", ""))
            dt = datetime.fromisoformat(dp.replace("Z", "+00:00"))
        except:
            continue
        
        # Só considera pagamentos dos últimos 90 dias
        if (hoje - dt).days > 90:
            continue
        
        if tid not in assinantes or dt > assinantes[tid]["data_pag"]:
            assinantes[tid] = {
                "nome": pag.get("customerName", "Cliente"),
                "data_pag": dt,
                "expiracao": dt + timedelta(days=DIAS_ASSINATURA)
            }
    
    removidos = 0
    for tid, info in assinantes.items():
        if hoje > info["expiracao"]:
            # Expirado! Remove do grupo
            nome = info["nome"]
            print(f"⏰ Expirado: {nome} (ID: {tid}) — venceu em {info['expiracao'].strftime('%d/%m/%Y')}")
            
            banir(group_id, tid)
            
            enviar(tid,
                f"⏰ <b>Assinatura expirada</b>\n\n"
                f"Olá <b>{nome}</b>, sua assinatura Máquina de Greens VIP venceu.\n\n"
                f"💰 Renove por mais 30 dias: <b>R$ {PRECO:.2f}</b>\n"
                f"📩 Envie <b>/assinar</b> no direct do bot para gerar um novo Pix."
            )
            
            enviar_grupo(
                f"👋 <b>Membro removido</b>\n\n"
                f"<b>{nome}</b> — assinatura expirada.\n"
                f"Volte quando quiser renovar! 🔄"
            )
            
            removidos += 1
    
    print(f"🧹 {removidos} assinante(s) expirado(s) removido(s)")
    return removidos


def gerar_pix(telegram_id, nome, cpf=None, email=None):
    """Gera Pix avulso de R$ 50"""
    print(f"💰 Gerando Pix para {nome}...")
    
    # Busca ou cria cliente
    cliente_id = None
    if cpf:
        c = asaas("GET", f"/customers?cpfCnpj={cpf}")
        if c and c.get("totalCount", 0) > 0:
            cliente_id = c["data"][0]["id"]
    
    if not cliente_id:
        # Tenta criar sem CPF, depois tenta com CPF se falhar
        dados = {
            "name": nome,
            "cpfCnpj": cpf or "00000000000",
            "email": email or "",
            "notificationDisabled": True
        }
        r = asaas("POST", "/customers", dados)
        if r and r.get("id"):
            cliente_id = r["id"]
        elif cpf:
            # Tenta de novo sem CPF
            dados2 = {"name": nome, "cpfCnpj": "00000000000", "email": email or "", "notificationDisabled": True}
            r2 = asaas("POST", "/customers", dados2)
            if r2 and r2.get("id"):
                cliente_id = r2["id"]
    
    if not cliente_id:
        print("❌ Falha ao criar cliente")
        return None
    
    # Cria cobrança PIX
    venc = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")
    cob = {
        "customer": cliente_id,
        "billingType": "PIX",
        "value": PRECO,
        "dueDate": venc,
        "description": f"Máquina de Greens VIP - R$ {PRECO:.2f}/mês",
        "externalReference": telegram_id
    }
    
    r = asaas("POST", "/payments", cob)
    if not r or not r.get("id"):
        print("❌ Falha ao criar cobrança")
        return None
    
    pid = r["id"]
    pix = asaas("GET", f"/payments/{pid}/pixQrCode")
    if not pix:
        print("❌ Falha ao obter QR Code")
        return None
    
    return {
        "payment_id": pid,
        "nome": nome,
        "telegram_id": telegram_id,
        "valor": PRECO,
        "pix_copia_cola": pix.get("payload", ""),
        "pix_qr_code": pix.get("encodedImage", ""),
        "vencimento": venc
    }


def status():
    """Status baseado no Asaas"""
    hoje = datetime.now(timezone.utc)
    
    pagamentos = asaas("GET", "/payments?billingType=PIX&status=RECEIVED&limit=200")
    if not pagamentos:
        print("❌ Não foi possível consultar Asaas")
        return
    
    data = pagamentos.get("data", [])
    
    # Conta assinantes ativos
    ativos = 0
    receita_mensal = 0
    
    for pag in data:
        tid = pag.get("externalReference", "")
        if not tid:
            continue
        try:
            dp = pag.get("paymentDate", pag.get("clientPaymentDate", ""))
            dt = datetime.fromisoformat(dp.replace("Z", "+00:00"))
            if (hoje - dt).days <= DIAS_ASSINATURA:
                ativos += 1
                receita_mensal += pag.get("value", 0)
        except:
            continue
    
    print(f"\n{'='*50}")
    print(f"📊 MÁQUINA DE GREENS VIP")
    print(f"{'='*50}")
    print(f"  💰 Preço: R$ {PRECO:.2f}/mês")
    print(f"  🟢 Assinantes ativos: {ativos}")
    print(f"  💵 Receita mensal: R$ {receita_mensal:.2f}")
    print(f"  💳 Total pagamentos: {len(data)}")
    print(f"  📅 Última verificação: {hoje.strftime('%d/%m/%Y %H:%M')}")
    print(f"  🔒 Dados via API Asaas (zero dados no repositório)")
    print()


def divulgar():
    """Texto de divulgação"""
    print(
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>🚀 MÁQUINA DE GREENS VIP</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 <b>SINAIS AO VIVO COM ALTA ASSERTIVIDADE</b>\n\n"
        f"📊 <b>6 MERCADOS:</b>\n"
        f"⚽️ Over Gol Intervalo\n"
        f"⚽️ Over Gol Partida\n"
        f"⚽️ Over 1.5 Gols Partida\n"
        f"⚽️ Ambas Marcam\n"
        f"🚩 Escanteio Limite HT\n"
        f"🚩 Escanteio Limite FT\n\n"
        f"💰 <b>Investimento: R$ {PRECO:.2f}/mês</b>\n"
        f"💳 Pagamento via <b>PIX</b> (entrada automática)\n\n"
        f"📩 Envie <b>/assinar</b> no direct do bot para garantir sua vaga!"
    )


# ========== MAIN ==========
def main():
    if len(sys.argv) < 2:
        print("Uso: python vip_manager.py [check|purge|pix|status|divulgar]")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        verificar_pagamentos()
    elif cmd == "purge":
        verificar_expirados()
    elif cmd == "pix":
        # Modo interativo ou args
        if len(sys.argv) >= 4:
            args = {}
            for i in range(2, len(sys.argv), 2):
                if i+1 < len(sys.argv):
                    args[sys.argv[i].lstrip("-")] = sys.argv[i+1]
            r = gerar_pix(args.get("telegram", ""), args.get("nome", "Cliente"), args.get("cpf"), args.get("email"))
            if r:
                print(f"✅ Pix gerado!")
                print(f"   Pix Copia e Cola:\n{r['pix_copia_cola']}")
        else:
            print("Uso: python vip_manager.py pix --telegram ID --nome 'Nome' [--cpf CPF]")
    elif cmd == "status":
        status()
    elif cmd == "divulgar":
        divulgar()
    else:
        print(f"Comando desconhecido: {cmd}")


if __name__ == "__main__":
    main()