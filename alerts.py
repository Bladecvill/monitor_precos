import logging, time
import pywhatkit
from config import WHATSAPP_PHONE, WHATSAPP_ENABLED
from database import get_alertas, get_ultimo_preco, get_preco_anterior

COOLDOWN = 6 * 3600
_ultimo_envio = {}

def _pode_enviar(nome):
    return time.time() - _ultimo_envio.get(nome, 0) >= COOLDOWN

def enviar_whatsapp(numero, mensagem):
    if not WHATSAPP_ENABLED: return False
    try:
        pywhatkit.sendwhatmsg_instantly(f'+{numero}', mensagem, wait_time=15, tab_close=True)
        return True
    except Exception as e:
        logging.error(e)
        return False

def enviar_preco_manual(nome, preco, url, site):
    msg = f'📊 Preço sob demanda\n{nome}\nR$ {preco:.2f}\n{site}\n{url}'
    return {'nome': nome, 'enviado': enviar_whatsapp(WHATSAPP_PHONE, msg), 'mensagem': msg}

def verificar_alertas():
    disparados = []
    for alerta in get_alertas(ativos_apenas=True):
        nome, limite = alerta['nome'], alerta['limite']
        reg = get_ultimo_preco(nome)
        
        if not reg or not reg['preco']: continue
        
        if reg['preco'] <= limite and _pode_enviar(nome):
            ant = get_preco_anterior(nome)
            msg = (f'🚨 ALERTA DE PREÇO!\n{nome}\n'
                   f'Anterior: R$ {ant["preco"]:.2f}\n' if ant else ''
                   f'Atual: R$ {reg["preco"]:.2f}\n{reg["url"]}')
                   
            if enviar_whatsapp(WHATSAPP_PHONE, msg):
                _ultimo_envio[nome] = time.time()
                disparados.append({'nome': nome, 'preco_atual': reg['preco']})
                
    return disparados