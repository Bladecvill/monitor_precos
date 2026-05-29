import re, logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from config import DEFAULT_HEADERS, REQUEST_TIMEOUT, REQUEST_RETRY

def _limpar_preco(texto):
    if not texto: return None
    texto = re.sub(r'[Rr$€£]', '', texto).replace('à vista','').strip()
    
    if ',' in texto and '.' in texto:
        texto = texto.replace('.','').replace(',','.')
    elif ',' in texto: 
        texto = texto.replace(',','.')
        
    texto = re.sub(r'[^\d.]', '', texto)
    
    try: 
        return round(float(texto), 2)
    except: 
        return None

def fetch_page(url, retries=REQUEST_RETRY):
    for i in range(retries):
        try:
            r = requests.get(url, headers=DEFAULT_HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            return r.text
        except: 
            pass
    return None

def _extrair(soup, seletores, atributo=None):
    for s in seletores:
        if not s: continue
        el = soup.select_one(s)
        if el:
            val = el.get(atributo) if atributo else el.get_text(strip=True)
            if val: return val
    return None

SELETORES = {
    'amazon': {
        'preco': ['span.a-price-whole','span.a-price span.a-offscreen',
                  '#priceblock_ourprice','.a-color-price','meta[itemprop="price"]'],
        'nome':  ['#productTitle','h1.a-size-large','h1','title'],
    },
    'kabum': {
        'preco': ['h3.finalPrice','span.regularPrice','meta[itemprop="price"]'],
        'nome':  ['h1.productName','h1','title'],
    },
    'terabyte': {
        'preco': ['span.price','div.product-price span','meta[itemprop="price"]'],
        'nome':  ['h1.product-title','h1','title'],
    },
}

def scrape_produto(produto):
    site = produto.get('site','').lower()
    sels = SELETORES.get(site)
    if not sels: return None
    
    html = fetch_page(produto['url'])
    if not html: return None
    
    soup = BeautifulSoup(html, 'lxml')
    preco_txt = _extrair(soup, sels['preco'])
    nome_txt  = _extrair(soup, sels['nome']) or produto['nome']
    
    return {
        'nome': nome_txt, 
        'preco': _limpar_preco(preco_txt),
        'url': produto['url'], 
        'site': site,
        'categoria': produto.get('categoria','Geral'),
        'data_coleta': datetime.now().isoformat(),
    }

def scrape_todos(produtos):
    return [r for p in produtos if (r := scrape_produto(p))]