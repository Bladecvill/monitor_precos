import sqlite3, logging
from contextlib import contextmanager
from config import DB_NAME

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback(); raise
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS precos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL, preco REAL, url TEXT,
        site TEXT, categoria TEXT, data_coleta TEXT)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS alertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE, limite REAL,
        ativo INTEGER DEFAULT 1)''')

def insert_preco(dado):
    sql = 'INSERT INTO precos (nome,preco,url,site,categoria,data_coleta)'
    ' VALUES (:nome,:preco,:url,:site,:categoria,:data_coleta)'
    with get_connection() as conn:
        return conn.execute(sql, dado).lastrowid

def insert_precos_batch(dados):
    return [insert_preco(d) for d in dados]

def get_historico(nome=None, dias=30):
    sql = 'SELECT * FROM precos WHERE data_coleta >= datetime("now",?)'
    params = [f'-{dias} days']
    if nome: sql += ' AND nome LIKE ?'; params.append(f'%{nome}%')
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql+' ORDER BY data_coleta ASC', params)]

def get_ultimo_preco(nome):
    sql = 'SELECT * FROM precos WHERE nome LIKE ? ORDER BY data_coleta DESC LIMIT 1'
    with get_connection() as conn:
        r = conn.execute(sql, (f'%{nome}%',)).fetchone()
        return dict(r) if r else None

def get_preco_anterior(nome):
    sql = 'SELECT * FROM precos WHERE nome LIKE ? ORDER BY data_coleta DESC LIMIT 1 OFFSET 1'
    with get_connection() as conn:
        r = conn.execute(sql, (f'%{nome}%',)).fetchone()
        return dict(r) if r else None

def get_produtos_monitorados():
    sql = '''SELECT nome, MAX(preco) as ultimo_preco, site,
    categoria, url, MAX(data_coleta) as ultima_coleta
    FROM precos GROUP BY nome'''
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql)]

def insert_alerta(nome, limite, ativo=True):
    sql = '''INSERT INTO alertas (nome,limite,ativo) VALUES (?,?,?)
    ON CONFLICT(nome) DO UPDATE SET limite=excluded.limite,ativo=excluded.ativo'''
    with get_connection() as conn:
        return conn.execute(sql, (nome, limite, int(ativo))).lastrowid

def get_alertas(ativos_apenas=False):
    sql = 'SELECT * FROM alertas'
    if ativos_apenas: sql += ' WHERE ativo=1'
    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql)]

def delete_alerta(id):
    with get_connection() as conn:
        return conn.execute('DELETE FROM alertas WHERE id=?', (id,)).rowcount > 0

def toggle_alerta(id):
    sql = 'UPDATE alertas SET ativo = CASE WHEN ativo=1 THEN 0 ELSE 1 END WHERE id=?'
    with get_connection() as conn:
        return conn.execute(sql, (id,)).rowcount > 0