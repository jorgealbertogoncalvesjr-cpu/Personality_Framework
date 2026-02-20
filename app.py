# =====================================================
# EXECUTIVE PERSONALITY ENGINE — CONSULTORIA PRO
# =====================================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

st.set_page_config(page_title="Executive Personality Engine", layout="centered")

# ---------------- SESSION INIT ----------------
if "step" not in st.session_state:
    st.session_state.step = 0

if "scores" not in st.session_state:
    st.session_state.scores = None

if "saved" not in st.session_state:
    st.session_state.saved = False

if "init_sliders" not in st.session_state:
    for p in ["o","c","e","a","n"]:
        for i in range(1,8):
            st.session_state[f"{p}{i}"] = 3
    st.session_state.init_sliders = True



#BLOCO 2 — GOOGLE LOW READ ARCHITECTURE

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
    st.sidebar.error("Google OFF")
    st.sidebar.code(str(e))


@st.cache_data(ttl=900)
def load_population():

    if not google_ok or sheet is None:
        return pd.DataFrame()

    try:
        df = pd.DataFrame(sheet.get_all_records())
        for c in ["O","C","E","A","N"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df
    except:
        return pd.DataFrame()


def get_population_if_needed():
    if st.session_state.step < 5:
        return pd.DataFrame()

    if "df_pop" not in st.session_state:
        st.session_state.df_pop = load_population()

    return st.session_state.df_pop


def save_result(name, s):

    if not google_ok or sheet is None:
        return

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name,
        float(s["O"]), float(s["C"]), float(s["E"]),
        float(s["A"]), float(s["N"])
    ]

    for _ in range(3):
        try:
            sheet.append_row(row)
            return
        except:
            time.sleep(2)


#BLOCO 3 — LOGIN

PASSWORD = "1618"

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

#BLOCO 4 — QUESTIONÁRIO OCEAN

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

pillars = list(QUESTIONS.keys())
TOTAL_STEPS = 5

st.progress(st.session_state.step / TOTAL_STEPS)

if st.session_state.step < TOTAL_STEPS:

    p = pillars[st.session_state.step]
    st.subheader(f"Pilar {p}")

    for qid, text, _ in QUESTIONS[p]:
        st.slider(text, 1, 5, key=qid)

    c1, c2 = st.columns(2)

    if c1.button("⬅ Voltar") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if c2.button("Próximo ➡"):
        st.session_state.step += 1
        st.rerun()

#BLOCO 5 — CÁLCULO
else:

    scores = {}

    for p in QUESTIONS:
        vals = []
        for qid, _, rev in QUESTIONS[p]:
            v = int(st.session_state[qid])
            if rev:
                v = 6 - v
            vals.append(v)

        raw = sum(vals) / len(vals)
        scores[p] = round((raw - 1) / 4 * 100, 1)

    st.session_state.scores = scores


#BLOCO 6 — RESULTADOS + MATRIZ + RADAR

if st.session_state.scores is None:
    st.stop()

s = st.session_state.scores
name = st.text_input("Nome", "Participante")

if not st.session_state.saved and sum(s.values()) != 250:
    save_result(name, s)
    st.session_state.saved = True


st.header("Executive Snapshot")

cols = st.columns(5)
for i, k in enumerate(["O","C","E","A","N"]):
    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(k, round(val,1))


# MATRIZ ESTRATÉGICA
x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

fig, ax = plt.subplots(figsize=(6,6))
ax.axhline(50, linestyle="--")
ax.axvline(50, linestyle="--")
ax.scatter(x, y, s=200)
ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_xlabel("Visão & Influência")
ax.set_ylabel("Execução & Consistência")
st.pyplot(fig)


# RADAR
labels = ["O","C","E","A","N"]
vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]

angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
vals += vals[:1]
angles += angles[:1]

fig2 = plt.figure(figsize=(5,5))
ax2 = plt.subplot(polar=True)
ax2.plot(angles, vals)
ax2.fill(angles, vals, alpha=0.15)
ax2.set_ylim(0,100)
st.pyplot(fig2)


# BLOCO 7 — PDF EXECUTIVO
def gerar_pdf(name, s, fig_matrix, fig_radar):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2*cm, "Executive Personality Report")

    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-3*cm, f"Nome: {name}")
    c.drawString(2*cm, height-3.7*cm, f"Data: {datetime.now().strftime('%Y-%m-%d')}")

    y_pos = height - 5*cm
    for k in ["O","C","E","A","N"]:
        val = s[k] if k != "N" else 100 - s[k]
        c.drawString(2*cm, y_pos, f"{k}: {round(val,1)}")
        y_pos -= 0.7*cm

    # MATRIX IMAGE
    img1 = io.BytesIO()
    fig_matrix.savefig(img1, format="PNG", bbox_inches="tight")
    img1.seek(0)
    c.drawImage(ImageReader(img1), 2*cm, height-16*cm, width=12*cm, height=10*cm)

    c.showPage()

    # RADAR IMAGE
    img2 = io.BytesIO()
    fig_radar.savefig(img2, format="PNG", bbox_inches="tight")
    img2.seek(0)
    c.drawImage(ImageReader(img2), 2*cm, height-16*cm, width=12*cm, height=10*cm)

    c.save()
    buffer.seek(0)
    return buffer


pdf = gerar_pdf(name, s, fig, fig2)

st.download_button(
    "📄 Download Executive Report",
    pdf,
    "Executive_Report.pdf"
)
