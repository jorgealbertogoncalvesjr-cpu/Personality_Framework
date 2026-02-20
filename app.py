import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Executive Personality Engine", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    div[data-testid="stForm"] { border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DE ESTADO ---
if "step" not in st.session_state: st.session_state.step = 0
if "scores" not in st.session_state: st.session_state.scores = None
if "saved" not in st.session_state: st.session_state.saved = False
if "df_pop" not in st.session_state: st.session_state.df_pop = pd.DataFrame()

# --- CONEXÃO GOOGLE SHEETS ---
def get_gsheet_client():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds)
    except:
        return None

# --- LEITURA COM ESTRATÉGIA DE QUOTA (CACHE 15 MIN) ---
@st.cache_data(ttl=900)
def fetch_population_data():
    """Lê do Google Sheets apenas 1x a cada 15 minutos."""
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open_by_url(st.secrets["gsheets"]["spreadsheet"]).sheet1
            data = sheet.get_all_records()
            df = pd.DataFrame(data)
            # Limpeza rápida
            for c in ["O","C","E","A","N"]:
                if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce')
            return df.dropna(subset=["O","C","E","A","N"])
    except Exception as e:
        print(f"Erro na leitura: {e}")
    return pd.DataFrame() # Retorna vazio se falhar

# Carregamento Híbrido
df_pop = fetch_population_data()
if df_pop.empty and not st.session_state.df_pop.empty:
    df_pop = st.session_state.df_pop # Usa o cache da sessão se a API falhar
else:
    st.session_state.df_pop = df_pop

# --- FUNÇÃO DE ESCRITA (SEM TRAVAR O APP) ---
def save_result_silent(name, s):
    try:
        client = get_gsheet_client()
        if client:
            sheet = client.open_by_url(st.secrets["gsheets"]["spreadsheet"]).sheet1
            row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, 
                   s["O"], s["C"], s["E"], s["A"], s["N"]]
            sheet.append_row(row)
            return True
    except:
        return False


# --- LOGIC & QUESTIONS ---
QUESTIONS = {
    "O": [("o1","Imaginação rica",False),("o2","Ideias abstratas",False),("o3","Interesse artístico",False),("o4","Prefere rotina",True),("o5","Curiosidade ativa",False),("o6","Evita filosofia",True),("o7","Visão de futuro",False)],
    "C": [("c1","Organização",False),("c2","Planejamento",False),("c3","Cumpre prazos",False),("c4","Desleixo",True),("c5","Autodisciplina",False),("c6","Procrastinação",True),("c7","Responsabilidade",False)],
    "E": [("e1","Sociabilidade",False),("e2","Inicia conversas",False),("e3","Expressividade",False),("e4","Prefere silêncio",True),("e5","Conforto em grupos",False),("e6","Evita atenção",True),("e7","Entusiasmo",False)],
    "A": [("a1","Empatia",False),("a2","Confiança",False),("a3","Evita conflitos",False),("a4","Espírito crítico",True),("a5","Altruísmo",False),("a6","Dureza/Ceticismo",True),("a7","Cooperação",False)],
    "N": [("n1","Preocupação fácil",False),("n2","Ansiedade",False),("n3","Mudança de humor",False),("n4","Estabilidade/Calma",True),("n5","Tensão",False),("n6","Resiliência ao estresse",True),("n7","Reatividade forte",False)]
}

# --- AUTH ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🛡️ Executive Personality Engine")
    with st.container():
        senha = st.text_input("Acesso Executivo", type="password")
        if st.button("Autenticar"):
            if senha == "1618":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Acesso negado.")
    st.stop()

# --- QUESTIONÁRIO ---
pillars = list(QUESTIONS.keys())
if st.session_state.step < 5:
    p = pillars[st.session_state.step]
    labels = {"O":"Abertura","C":"Conscienciosidade","E":"Extroversão","A":"Amabilidade","N":"Estabilidade Emocional"}
    
    st.title(f"Avaliação: {labels[p]}")
    st.progress((st.session_state.step + 1) / 5)
    
    with st.form(f"form_{p}"):
        for qid, text, _ in QUESTIONS[p]:
            st.select_slider(text, options=[1,2,3,4,5], value=3, key=f"val_{qid}", 
                             help="1: Discordo Totalmente | 5: Concordo Totalmente")
        
        c1, c2 = st.columns([1,1])
        if st.session_state.step > 0:
            if c1.form_submit_button("⬅ Voltar"):
                st.session_state.step -= 1
                st.rerun()
        if c2.form_submit_button("Próximo ➡" if st.session_state.step < 4 else "Finalizar"):
            st.session_state.step += 1
            st.rerun()
    st.stop()


# --- CÁLCULO DE RESULTADOS ---
if st.session_state.scores is None:
    results = {}
    for p in QUESTIONS:
        vals = []
        for qid, _, rev in QUESTIONS[p]:
            v = st.session_state[f"val_{qid}"]
            vals.append(6 - v if rev else v)
        # Escala 0 a 100
        raw_avg = sum(vals) / len(vals)
        results[p] = round((raw_avg - 1) / 4 * 100, 1)
    st.session_state.scores = results

s = st.session_state.scores
user_name = st.sidebar.text_input("Nome do Líder", "Executivo Anon")

# Gravação automática (uma única vez)
if not st.session_state.saved:
    if save_result_silent(user_name, s):
        st.session_state.saved = True
        st.sidebar.success("Dados Sincronizados")

# --- LAYOUT DE RESULTADOS ---
st.title("📊 Executive Dashboard")
st.markdown(f"**Candidato:** {user_name} | **Data:** {datetime.now().strftime('%d/%m/%Y')}")

# Métricas Principais
m1, m2, m3, m4, m5 = st.columns(5)
metrics = [("Abertura", "O"), ("Gestão", "C"), ("Influência", "E"), ("Acordo", "A"), ("Estabilidade", "N")]
for i, (label, key) in enumerate(metrics):
    val = s[key] if key != "N" else (100 - s[key]) # Invertemos N para "Estabilidade"
    [m1, m2, m3, m4, m5][i].metric(label, f"{val}%")

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("Radar de Competências")
    # Gráfico Radar usando Plotly
    categories = ['Abertura', 'Conscienciosidade', 'Extroversão', 'Amabilidade', 'Estabilidade']
    values = [s['O'], s['C'], s['E'], s['A'], 100-s['N']]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Perfil'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("Matriz de Posicionamento")
    # Lógica de Quadrante
    foco_pessoas = (s["E"] + s["A"]) / 2
    foco_resultado = (s["C"] + (100 - s["N"])) / 2
    
    # 
    
    if foco_resultado > 60 and foco_pessoas > 60:
        st.success("### 🏆 Perfil: Líder Estratégico\nFoco equilibrado entre pessoas e execução de alto nível.")
    elif foco_resultado > 60:
        st.info("### ⚙️ Perfil: Executor Técnico\nAlta capacidade de entrega, foco em processos e prazos.")
    elif foco_pessoas > 60:
        st.warning("### 📣 Perfil: Influenciador\nFoco em engajamento, comunicação e motivação de times.")
    else:
        st.error("### 🚀 Perfil: Em Desenvolvimento\nNecessita suporte em estruturação de processos e liderança.")

# --- BENCHMARK POPULACIONAL (USANDO O CACHE) ---
st.divider()
st.subheader("🌎 Comparativo com População Executiva")

if not df_pop.empty:
    bench_cols = st.columns(5)
    for i, k in enumerate(["O","C","E","A","N"]):
        avg_pop = df_pop[k].mean()
        user_val = s[k]
        diff = user_val - avg_pop
        bench_cols[i].metric(f"Média {k}", f"{round(avg_pop,1)}%", f"{round(diff,1)}%")
else:
    st.info("Aguardando volume de dados para benchmark.")

if st.button("Nova Avaliação"):
    for key in list(st.session_state.keys()):
        if key not in ["df_pop"]: del st.session_state[key]
    st.rerun()

