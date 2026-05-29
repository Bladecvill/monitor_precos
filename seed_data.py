import random
from datetime import datetime, timedelta
from database import init_db, insert_precos_batch, insert_alerta
from config import PRODUCTS, DEFAULT_ALERT_LIMITS

PRECOS_BASE = {
    'SSD Kingston A400 480GB': 249.90,
    'Monitor LG UltraGear 27GN750': 1799.00,
    'RTX 4060 Ti 16GB': 3499.00,
    'Memória RAM Corsair Vengeance 16GB DDR5': 479.90,
}

def seed(dias=30):
    init_db()
    regs = []
    
    for p in PRODUCTS:
        base = PRECOS_BASE.get(p['nome'], 100.0)
        preco = base
        
        for i in range(dias, 0, -1):
            preco = max(base*.8, min(base*1.2, preco*(1+random.uniform(-.03,.03))))
            regs.append({
                'nome': p['nome'], 
                'preco': round(preco, 2),
                'url': p['url'], 
                'site': p['site'],
                'categoria': p.get('categoria', 'Geral'),
                'data_coleta': (datetime.now() - timedelta(days=i)).isoformat()
            })
            
    ids = insert_precos_batch(regs)
    [insert_alerta(n, l) for n, l in DEFAULT_ALERT_LIMITS.items()]
    print(f'{len(ids)} registros e {len(DEFAULT_ALERT_LIMITS)} alertas inseridos.')

if __name__ == '__main__': 
    seed()