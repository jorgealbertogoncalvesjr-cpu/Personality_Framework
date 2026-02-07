# =====================================================
# EXECUTIVE PERSONALITY ENGINE — PROFESSIONAL STABLE
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
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


# -----------------------------------------------------
# SESSION INIT (ANTI RESET SLIDERS)
# -----------------------------------------------------
if "initialized" not in st.session_state:
    for p in ["O","C","E","A","N"]:
        for i in range(1,8):
            st.session_state[f"{p.lower()}{i}"] = 3
    st.session_state.initialized = True


# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="Executive Personality Profile", layout="centered")
PASSWORD = "1618"

# -----------------------------------------------------
# GOOGLE SHEETS CONNECTION — SAFE MODE
# -----------------------------------------------------

# -----------------------------------------------------
# CACHE — LOAD POPULATION (ANTI GOOGLE QUOTA)
# -----------------------------------------------------
@st.cache_data(ttl=60)
def load_population():
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()


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

    SHEET_URL = st.secrets["gsheets"]["spreadsheet"]
    sheet = client.open_by_url(SHEET_URL).sheet1

    google_ok = True
    st.sidebar.success("Google Sheets conectado")

except Exception as e:
    st.sidebar.error("Erro Google Sheets")
    st.sidebar.code(str(e))
    google_ok = False


# -----------------------------------------------------
# SAVE RESULT — SAFE WRITE
# -----------------------------------------------------
def save_result(name, scores):

    if not google_ok or sheet is None:
        st.warning("Google Sheets não conectado — dados não salvos")
        return

    try:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            scores["O"],
            scores["C"],
            scores["E"],
            scores["A"],
            scores["N"],
        ]

        sheet.append_row(row)
        st.success("Resultado salvo no Google Sheets")

    except Exception as e:
        st.error("Falha ao salvar no Google Sheets")
        st.code(str(e))


# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🧠 Executive Personality Assessment")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# -----------------------------------------------------
# FUNÇÕES PSICOMÉTRICAS
# -----------------------------------------------------
def personality_type(s):
    if max(s.values()) - min(s.values()) < 12:
        return "Balanced", "Perfil equilibrado"

    if s["O"] > 65 and s["E"] > 60:
        return "Explorer", "Inovador e orientado à exploração"

    if s["C"] > 65 and s["N"] < 45:
        return "Executor", "Disciplinado e orientado a resultados"

    if s["A"] > 65 and s["C"] > 60:
        return "Diplomat", "Cooperativo e harmonizador"

    return "Analyst", "Analítico e estratégico"


def percentile(score, mean=50, std=15):
    z = (score - mean) / std
    return round((0.5 * (1 + math.erf(z / math.sqrt(2)))) * 100, 1)

# -----------------------------------------------------
# QUESTIONÁRIO BIG FIVE
# -----------------------------------------------------
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

if "step" not in st.session_state:
    st.session_state.step = 0

st.progress(st.session_state.step / 5)

# -----------------------------------------------------
# UX QUESTIONÁRIO
# -----------------------------------------------------
if st.session_state.step < 5:

    p = pillars[st.session_state.step]
    st.subheader(PILLAR_NAMES[p])

    for qid, text, _ in QUESTIONS[p]:
       
        st.slider(text, 1, 5, key=qid)

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
            v = st.session_state.get(qid, 3)
            if rev:
                v = 6 - v
            vals.append(v)

        raw = sum(vals) / len(vals)
        scores[p] = round((raw - 1) / 4 * 100, 1)

    st.session_state.scores = scores

# -----------------------------------------------------
# RESULTADOS C-LEVEL
# -----------------------------------------------------
if "scores" not in st.session_state:
    st.stop()

s = st.session_state.scores
name = st.text_input("Nome", "Participante")

if "saved" not in st.session_state:
    save_result(name, s)
    st.session_state.saved = True

ptype, pdesc = personality_type(s)

st.markdown(f"# Perfil Executivo: **{ptype}**")
st.write(pdesc)

# EXECUTIVE SNAPSHOT
st.markdown("## Executive Snapshot")
for k in s:
    val = s[k] if k!="N" else 100-s[k]
    st.metric(PILLAR_NAMES[k], f"{val}")

# MATRIZ EXECUTIVA
st.markdown("## Matriz Executiva")
x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

fig, ax = plt.subplots(figsize=(5,5))
ax.axhline(50, linestyle="--")
ax.axvline(50, linestyle="--")
ax.scatter(x, y, s=180)
ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_xlabel("Visão & Influência")
ax.set_ylabel("Execução & Consistência")
st.pyplot(fig)

# RADAR
st.markdown("## Radar Comportamental")
labels = list(PILLAR_NAMES.values())
vals = [s["O"],s["C"],s["E"],s["A"],100-s["N"]]
angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
vals += vals[:1]
angles += angles[:1]

fig = plt.figure(figsize=(5,5))
ax = plt.subplot(polar=True)
ax.plot(angles, vals, linewidth=2)
ax.fill(angles, vals, alpha=0.1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
st.pyplot(fig)

# BENCHMARK REAL
st.markdown("## Benchmark Real")
try:
   df_pop = load_population()
    for k in ["O","C","E","A","N"]:
        user = s[k] if k!="N" else 100-s[k]
        pop = df_pop[k].mean()
        st.write(f"**{PILLAR_NAMES[k]}**")
        st.metric("Você", round(user,1))
        st.metric("Média Pop.", round(pop,1))
        st.progress(user/100)
except:
    st.info("Benchmark aparecerá após acumular dados")

# PDF
st.markdown("## Relatório PDF")

def gerar_pdf(name,s):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.drawString(100,800,f"Executive Personality Report — {name}")
    y=760
    for k,v in s.items():
        c.drawString(100,y,f"{PILLAR_NAMES[k]}: {round(v,1)}")
        y-=20
    c.save()
    buffer.seek(0)
    return buffer

pdf = gerar_pdf(name,s)

st.download_button("Baixar PDF", pdf, "executive_profile.pdf")
