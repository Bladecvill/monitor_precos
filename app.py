import streamlit as st
import pandas as pd
import plotly.express as px
from database import (init_db, get_produtos_monitorados, get_historico,
                      get_alertas, insert_alerta, delete_alerta, toggle_alerta)
from alerts import enviar_preco_manual
from config import DEFAULT_ALERT_LIMITS, WHATSAPP_ENABLED

st.set_page_config(page_title='Coletor de Preços', page_icon='📊', layout='wide')

if 'db_init' not in st.session_state:
    init_db()
    st.session_state['db_init'] = True

def fmt(v): 
    return f'R$ {v:,.2f}' if v else '—'

pagina = st.sidebar.radio('', ['📊 Dashboard', '📈 Histórico', '🔔 Alertas'])

# --- DASHBOARD ---
if pagina == '📊 Dashboard':
    st.title('Produtos Monitorados')
    produtos = get_produtos_monitorados()
    
    if not produtos: 
        st.info('Sem dados. Rode seed_data.py ou aguarde a coleta.')
    else:
        df = pd.DataFrame(produtos)
        c1, c2, c3 = st.columns(3)
        c1.metric('Produtos', len(df))
        c2.metric('Sites', df['site'].nunique())
        c3.metric('Categorias', df['categoria'].nunique())
        
        st.dataframe(df[['nome','ultimo_preco','site','categoria','ultima_coleta']],
                     use_container_width=True, hide_index=True)
                     
        # Botões WhatsApp por produto
        for i, row in df.iterrows():
            col1, col2 = st.columns([5,1])
            col1.write(f"{row['nome']} — {fmt(row['ultimo_preco'])}")
            if col2.button('📱 WhatsApp', key=f'wa_{i}'):
                res = enviar_preco_manual(row['nome'], row['ultimo_preco'],
                                          row['url'], row['site'])
                st.toast('Enviado!' if res['enviado'] else 'Desabilitado')
                
        fig = px.bar(df, x='nome', y='ultimo_preco', color='site')
        st.plotly_chart(fig, use_container_width=True)

# --- HISTÓRICO ---
elif pagina == '📈 Histórico':
    st.title('Histórico de Preços')
    nome = st.text_input('Filtrar produto')
    dias = st.slider('Período (dias)', 1, 365, 30)
    regs = get_historico(nome or None, dias)
    
    if regs:
        df = pd.DataFrame(regs)
        df['data_coleta'] = pd.to_datetime(df['data_coleta'])
        st.plotly_chart(px.line(df, x='data_coleta', y='preco', color='nome'),
                        use_container_width=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button('📥 CSV', df.to_csv(index=False), 'historico.csv', 'text/csv')

# --- ALERTAS ---
elif pagina == '🔔 Alertas':
    st.title('Alertas de Preço')
    with st.form('form'):
        nome = st.text_input('Produto')
        limite = st.number_input('Preço limite (R$)', min_value=0.01, step=10.0)
        if st.form_submit_button('Salvar') and nome:
            insert_alerta(nome, limite)
            st.rerun()
            
    if st.button('Carregar padrões'):
        [insert_alerta(n, l) for n, l in DEFAULT_ALERT_LIMITS.items()]
        st.rerun()
        
    for a in get_alertas():
        c1, c2, c3, c4 = st.columns([4,2,1,1])
        c1.write(f"{'🟢' if a['ativo'] else '🔴'} {a['nome']}")
        c2.write(fmt(a['limite']))
        if c3.button('🔄', key=f"t_{a['id']}"): 
            toggle_alerta(a['id'])
            st.rerun()
        if c4.button('🗑', key=f"d_{a['id']}"): 
            delete_alerta(a['id'])
            st.rerun()