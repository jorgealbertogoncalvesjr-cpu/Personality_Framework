# =====================================================
# EXECUTIVE PERSONALITY ENGINE — ENTERPRISE CONSULTING
# =====================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
import io
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# -----------------------------------------------------
# PAGE CONFIG — PRIMEIRA LINHA STREAMLIT
# -----------------------------------------------------
st.set_page_config(page_title="Executive Personality Engine", layout="centered")

# -----------------------------------------------------
# SESSION STATE SAFE INIT
# -----------------------------------------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "step" not in st.session_state:
    st.session_state.step = 0

if "init" not in st.session_state:
    for p in ["o","c","e","a","n"]:
        for i in range(1,8):
            st.session_state[f"{p}{i}"] = 3
    st.session_state.init = True

# -----------------------------------------------------
# UI STYLE (MOBILE)
# -----------------------------------------------------
st.markdown("""
<style>
    .stSlider > div { padding-bottom: 12px; }
    .stButton button {
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# LEGAL
# -----------------------------------------------------
st.markdown("""
<div style="padding:12px;border-radius:8px;background:#F6F8FB;border:1px solid #E1E5EE;font-size:13px">
<b>Base científica:</b> Big Five (OCEAN)<br>
Lewis Goldberg (1990) • Costa & McCrae (1992)<br>
Ferramenta de desenvolvimento — não diagnóstico clínico.
</div>
""", unsafe_allow_html=True)

PASSWORD = "1618"

# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Executive Personality Assessment")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# -----------------------------------------------------
# GOOGLE SHEETS
# -----------------------------------------------------
sheet = None
google_ok = False

try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_url(st.secrets["gsheets"]["spreadsheet"]).sheet1
    google_ok = True
    st.sidebar.success("Google Sheets conectado")

except Exception as e:
    st.sidebar.error("Sheets OFF")
    st.sidebar.code(str(e))

@st.cache_data(ttl=60)
def load_population():
    if sheet is None:
        return pd.DataFrame()
    try:
        return pd.DataFrame(sheet.get_all_records())
    except:
        return pd.DataFrame()

def save_result(name, scores):
    if not google_ok:
        return
    try:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            scores["O"], scores["C"], scores["E"], scores["A"], scores["N"]
        ])
    except:
        pass


QUESTIONS = {
    "O":[("o1","Tenho imaginação rica",False),("o2","Gosto de ideias abstratas",False),
         ("o3","Interesse por arte",False),("o4","Prefiro rotina",True),
         ("o5","Sou curioso",False),("o6","Evito filosofia",True),("o7","Penso no futuro",False)],
    "C":[("c1","Sou organizado",False),("c2","Planejo antes",False),
         ("c3","Cumpro prazos",False),("c4","Deixo tarefas",True),
         ("c5","Sou disciplinado",False),("c6","Procrastino",True),("c7","Sou responsável",False)],
    "E":[("e1","Gosto de socializar",False),("e2","Inicio conversas",False),
         ("e3","Sou expressivo",False),("e4","Prefiro silêncio",True),
         ("e5","Confortável em grupos",False),("e6","Evito atenção",True),("e7","Sou entusiasmado",False)],
    "A":[("a1","Sou empático",False),("a2","Confio nas pessoas",False),
         ("a3","Evito conflitos",False),("a4","Sou crítico",True),
         ("a5","Gosto de ajudar",False),("a6","Sou duro",True),("a7","Valorizo cooperação",False)],
    "N":[("n1","Preocupo-me fácil",False),("n2","Fico ansioso",False),
         ("n3","Mudo humor",False),("n4","Sou calmo",True),
         ("n5","Sinto tensão",False),("n6","Raramente estressado",True),("n7","Reajo forte",False)]
}

PILLAR_NAMES = {
    "O":"Abertura",
    "C":"Execução",
    "E":"Energia Social",
    "A":"Cooperação",
    "N":"Estabilidade Emocional"
}

pillars = list(QUESTIONS.keys())

TOTAL_STEPS = 5
st.progress(st.session_state.step / TOTAL_STEPS)

if st.session_state.step < 5:

    p = pillars[st.session_state.step]

    st.subheader(PILLAR_NAMES[p])
    st.caption("1=Discordo | 3=Neutro | 5=Concordo")

    for qid, text, _ in QUESTIONS[p]:
        if qid not in st.session_state:
            st.session_state[qid] = 3

        st.slider(text, 1, 5,
                  value=st.session_state[qid],
                  key=qid)

    c1, c2 = st.columns(2)

    if c1.button("⬅ Voltar") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if c2.button("Próximo ➡"):
        st.session_state.step += 1
        st.rerun()

else:
    scores = {}

    for p in QUESTIONS:
        vals = []
        for qid, _, rev in QUESTIONS[p]:
            v = st.session_state[qid]
            if rev:
                v = 6 - v
            vals.append(v)

        scores[p] = round((sum(vals)/len(vals)-1)/4*100,1)

    st.session_state.scores = scores

