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
# PAGE CONFIG — DEVE SER O PRIMEIRO st.*
# -----------------------------------------------------
st.set_page_config(page_title="Executive Personality Engine", layout="centered")

# -----------------------------------------------------
# SESSION STATE SAFE INIT (ANTI RESET / ANTI BUG)
# -----------------------------------------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}

if "step" not in st.session_state:
    if st.session_state.step == TOTAL_STEPS and not st.session_state.saved:
    save_result("Participante", s)
    st.session_state.saved = True


if "scores" not in st.session_state:
    st.session_state.scores = None

if "saved" not in st.session_state:
    st.session_state.saved = False

if "init" not in st.session_state:
    for p in ["o","c","e","a","n"]:
        for i in range(1,8):
            key = f"{p}{i}"
            if key not in st.session_state:
                st.session_state[key] = 3
    st.session_state.init = True


# -----------------------------------------------------
# UI STYLE — CONSULTORIA / MOBILE FRIENDLY
# -----------------------------------------------------
st.markdown("""
<style>
    .stSlider > div { padding-bottom: 10px; }
    .stButton button {
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# LEGAL / BASE CIENTÍFICA
# -----------------------------------------------------
st.markdown("""
<div style="
padding:12px;
border-radius:8px;
background:#F6F8FB;
border:1px solid #E1E5EE;
font-size:13px;
line-height:1.4;
">

<b>Base científica:</b> Big Five Personality Model (OCEAN)<br>
<b>Autores:</b> Goldberg (1990) | Costa & McCrae (1992)<br>
Ferramenta de desenvolvimento — não é diagnóstico clínico.

</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
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
# GOOGLE SHEETS — SAFE CONNECT
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
    google_ok = False
    st.sidebar.error("Google Sheets OFF")
    st.sidebar.code(str(e))


# -----------------------------------------------------
# CACHE — LOAD POPULATION (ANTI GOOGLE QUOTA 429)
# -----------------------------------------------------
@st.cache_data(ttl=120)
def load_population():
    if not google_ok or sheet is None:
        return pd.DataFrame()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # garante colunas numéricas
        for c in ["O","C","E","A","N"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df

    except:
        return pd.DataFrame()


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
            float(scores["O"]),
            float(scores["C"]),
            float(scores["E"]),
            float(scores["A"]),
            float(scores["N"])
        ]

        sheet.append_row(row)
        st.success("Resultado salvo no Google Sheets")

    except Exception as e:
        st.error("Falha ao salvar no Google Sheets")
        st.code(str(e))


# -----------------------------------------------------
# BENCHMARK ENGINE — POPULATION VS USER
# -----------------------------------------------------
def benchmark_vs_population(user_scores):

    df_pop = load_population()

    if df_pop.empty or len(df_pop) < 5:
        st.info("Benchmark aparecerá após acumular mais dados.")
        return None

    pop_means = {
        "O": df_pop["O"].mean(),
        "C": df_pop["C"].mean(),
        "E": df_pop["E"].mean(),
        "A": df_pop["A"].mean(),
        "N": df_pop["N"].mean()
    }

    return pop_means

# -----------------------------------------------------
# BIG FIVE STRUCTURE
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


# -----------------------------------------------------
# PREMIUM HEADER — MOBILE FRIENDLY
# -----------------------------------------------------

TOTAL_STEPS = 5
progress_pct = int((st.session_state.step / TOTAL_STEPS) * 100)

st.markdown(f"""
<div style="padding:14px;border-radius:12px;background:#F4F7FF;border:1px solid #E1E6FF">
<b style="font-size:18px">🧠 Executive Personality Assessment</b><br>
Etapa <b>{st.session_state.step + 1}</b> de {TOTAL_STEPS} • {progress_pct}% concluído
</div>
""", unsafe_allow_html=True)

st.progress(st.session_state.step / TOTAL_STEPS)


# -----------------------------------------------------
# QUESTION FLOW — PREMIUM UI
# -----------------------------------------------------

if st.session_state.step < TOTAL_STEPS:

    p = pillars[st.session_state.step]

    # Card Pilar
    st.markdown(f"""
    <div style="
        padding:16px;
        border-radius:12px;
        background:white;
        border:1px solid #E4E8F2;
        box-shadow:0px 2px 6px rgba(0,0,0,0.04);
        margin-top:10px;
        margin-bottom:10px;
    ">
        <b style="font-size:20px;color:#2B3A67">{PILLAR_NAMES[p]}</b><br>
        <span style="font-size:13px;color:#666">
        Avalie o quanto cada afirmação representa você.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.caption("1 = Discordo totalmente • 3 = Neutro • 5 = Concordo totalmente")

    # ---------- SLIDERS ----------
    for qid, text, _ in QUESTIONS[p]:

    if qid not in st.session_state:
        st.session_state[qid] = 3

    st.slider(
        label=text,
        min_value=1,
        max_value=5,
        key=qid
    )

      


    # ---------- NAVIGATION ----------
    col1, col2 = st.columns(2)

    if col1.button("⬅ Voltar", use_container_width=True) and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if col2.button("Próximo ➡", use_container_width=True):
        st.session_state.step += 1
        st.rerun()


# -----------------------------------------------------
# SCORE ENGINE — CORRIGE SCORE=50
# -----------------------------------------------------
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

        # Conversão correta para 0–100
        scores[p] = round((raw - 1) / 4 * 100, 1)

    st.session_state.scores = scores
    
# DEBUG silencioso (remova depois)
if st.sidebar.checkbox("DEBUG MODE", False):
    st.sidebar.write("Session answers:")
    dbg = {k: st.session_state[k] for k in st.session_state if len(k)==2}
    st.sidebar.write(dbg)

def percentile(score, mean=50, std=15):
    z = (score - mean) / std
    return round((0.5 * (1 + math.erf(z / math.sqrt(2)))) * 100, 1)


# -----------------------------------------------------
# RESULTS — SAFE
# -----------------------------------------------------
if st.session_state.scores is None:
    st.stop()


s = st.session_state.scores


# -----------------------------------------------------
# EXECUTIVE HEADER — McKINSEY STYLE
# -----------------------------------------------------
st.markdown("""
<div style="
padding:16px;
border-radius:12px;
background:white;
border:1px solid #E6E9F2;
box-shadow:0px 2px 6px rgba(0,0,0,0.04);
margin-top:10px;
margin-bottom:10px;
">
<b style="font-size:22px;color:#1F2A44">Executive Profile</b><br>
<span style="color:#6B7280;font-size:13px">
Behavioral & Leadership Pattern Analysis
</span>
</div>
""", unsafe_allow_html=True)



# -----------------------------------------------------
# EXECUTIVE SNAPSHOT — CARDS
# -----------------------------------------------------
st.markdown("### Executive Snapshot")

cols = st.columns(5)

labels = {
    "O":"Abertura",
    "C":"Execução",
    "E":"Energia",
    "A":"Cooperação",
    "N":"Estabilidade"
}

for i, k in enumerate(["O","C","E","A","N"]):
    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(labels[k], f"{round(val,1)}")

st.markdown("### Percentil Executivo")

for k in ["O","C","E","A","N"]:
    val = s[k] if k != "N" else 100 - s[k]
    pct = percentile(val)
    st.metric(f"{labels[k]} Percentil", f"{pct}%")


# -----------------------------------------------------
# MATRIX EXECUTIVE — CONSULTING QUADRANT
# -----------------------------------------------------
st.markdown("### Executive Positioning Matrix")

x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

fig, ax = plt.subplots(figsize=(6,6))

ax.axhline(50, linestyle="--", linewidth=1)
ax.axvline(50, linestyle="--", linewidth=1)

ax.scatter(x, y, s=220)

ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_xlabel("Vision & Influence")
ax.set_ylabel("Execution & Consistency")

ax.text(70,85,"Strategic Leader", fontsize=9)
ax.text(15,85,"Execution Specialist", fontsize=9)
ax.text(15,15,"Development Zone", fontsize=9)
ax.text(70,15,"Adaptive Profile", fontsize=9)

st.pyplot(fig)



# -----------------------------------------------------
# EXECUTIVE INTERPRETATION
# -----------------------------------------------------
st.markdown("### Executive Interpretation")

if x > 65 and y > 65:
    st.success("Strategic Leadership Profile — strong vision and execution capacity.")
elif x < 50 and y > 65:
    st.info("Execution Specialist — disciplined and delivery-oriented.")
elif x > 65 and y < 50:
    st.warning("Influencer Profile — strong vision, execution varies.")
else:
    st.error("Development Zone — focus on structure and consistency.")



# -----------------------------------------------------
# RADAR — BEHAVIORAL SHAPE
# -----------------------------------------------------
st.markdown("### Behavioral Radar")

labels_radar = ["Abertura","Execução","Energia Social","Cooperação","Estabilidade"]
vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]

angles = np.linspace(0, 2*np.pi, len(labels_radar), endpoint=False).tolist()
vals += vals[:1]
angles += angles[:1]

fig = plt.figure(figsize=(5,5))
ax = plt.subplot(polar=True)

ax.plot(angles, vals, linewidth=2)
ax.fill(angles, vals, alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels_radar)
ax.set_yticks([20,40,60,80])
ax.set_ylim(0,100)

st.pyplot(fig)



# -----------------------------------------------------
# LEADERSHIP INDEX — CONSULTING MODEL
# -----------------------------------------------------
st.markdown("### Executive Leadership Index")

leadership = (
    s["C"] * 0.35 +
    s["O"] * 0.20 +
    s["E"] * 0.20 +
    s["A"] * 0.15 +
    (100 - s["N"]) * 0.10
)

st.metric("Leadership Score", round(leadership,1))

if leadership > 75:
    st.success("High executive leadership capacity.")
elif leadership > 60:
    st.info("Leadership profile in development.")
else:
    st.warning("Leadership potential to be developed.")



# -----------------------------------------------------
# BENCHMARK — REAL GOOGLE DATA
# -----------------------------------------------------
st.markdown("### Population Benchmark")

df_pop = load_population()

if not df_pop.empty:

    for k in ["O","C","E","A","N"]:

        user_val = s[k] if k != "N" else 100 - s[k]
        pop_mean = df_pop[k].mean()

        st.write(f"**{labels[k]}**")
        st.metric("You", round(user_val,1))
        st.metric("Population Mean", round(pop_mean,1))
        st.progress(user_val / 100)

else:
    st.info("Benchmark will appear after population data grows.")



# -----------------------------------------------------
# EXECUTIVE CLUSTER
# -----------------------------------------------------
st.markdown("### Executive Cluster")

if leadership > 75 and x > 65:
    st.success("Strategic Leader")
elif s["C"] > 65:
    st.info("Execution Driver")
elif s["A"] > 65:
    st.info("Integrator")
else:
    st.warning("Adaptive Profile")



# -----------------------------------------------------
# CONSISTENCY INDEX
# -----------------------------------------------------
st.markdown("### Consistency Index")

std = np.std(list(s.values()))
consistency = round(100 - std * 3, 1)

st.metric("Consistency Score", consistency)

# -----------------------------------------------------
# PDF — ENTERPRISE CONSULTING REPORT (3 PAGES)
# -----------------------------------------------------
st.markdown("### Executive Report PDF")

from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

def gerar_pdf(name, s):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # =====================================================
    # PAGE 1 — EXECUTIVE SUMMARY
    # =====================================================
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2.5*cm, "Executive Personality Report")

    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-3.5*cm, f"Participant: {name}")
    c.drawString(2*cm, height-4.2*cm, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height-5.5*cm, "Executive Snapshot")

    y = height - 6.5*cm
    for k in ["O","C","E","A","N"]:
        val = s[k] if k != "N" else 100 - s[k]
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, y, f"{k}: {round(val,1)}")
        y -= 0.7*cm


    leadership = (
        s["C"]*0.35 +
        s["O"]*0.20 +
        s["E"]*0.20 +
        s["A"]*0.15 +
        (100-s["N"])*0.10
    )

    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, height-11*cm, "Leadership Index")

    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-12*cm, f"Score: {round(leadership,1)}")

    c.setFont("Helvetica", 9)
    c.drawString(2*cm, 3*cm,
        "Base científica: Big Five Personality Model (Goldberg, 1990 | Costa & McCrae, 1992)")
    c.drawString(2*cm, 2.5*cm,
        "Ferramenta de desenvolvimento — não constitui diagnóstico clínico.")

    c.showPage()

    # =====================================================
    # PAGE 2 — RADAR CHART
    # =====================================================
    labels = ["Abertura","Execução","Energia Social","Cooperação","Estabilidade"]
    vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]

    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    vals_plot = vals + vals[:1]
    angles_plot = angles + angles[:1]

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot(polar=True)
    ax.plot(angles_plot, vals_plot, linewidth=2)
    ax.fill(angles_plot, vals_plot, alpha=0.1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels)
    ax.set_ylim(0,100)

    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format="PNG", bbox_inches="tight")
    plt.close(fig)
    img_buffer.seek(0)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height-2.5*cm, "Behavioral Radar")

    c.drawImage(ImageReader(img_buffer), 3*cm, height-16*cm, width=12*cm, height=12*cm)

    c.showPage()

    # =====================================================
    # PAGE 3 — EXECUTIVE MATRIX
    # =====================================================
    x = (s["O"] + s["E"]) / 2
    y = (s["C"] + (100 - s["N"])) / 2

    fig, ax = plt.subplots(figsize=(4,4))
    ax.axhline(50, linestyle="--")
    ax.axvline(50, linestyle="--")
    ax.scatter(x, y, s=200)
    ax.set_xlim(0,100)
    ax.set_ylim(0,100)
    ax.set_xlabel("Vision & Influence")
    ax.set_ylabel("Execution & Consistency")

    img_buffer2 = io.BytesIO()
    plt.savefig(img_buffer2, format="PNG", bbox_inches="tight")
    plt.close(fig)
    img_buffer2.seek(0)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, height-2.5*cm, "Executive Positioning Matrix")

    c.drawImage(ImageReader(img_buffer2), 3*cm, height-16*cm, width=12*cm, height=12*cm)

    c.showPage()

    c.save()
    buffer.seek(0)

    return buffer



# -----------------------------------------------------
# DOWNLOAD BUTTON
# -----------------------------------------------------
name = st.text_input("Nome no relatório", "Participante")

pdf_file = gerar_pdf(name, s)

st.download_button(
    label="📄 Baixar Executive Report (PDF)",
    data=pdf_file,
    file_name="Executive_Personality_Report.pdf",
    mime="application/pdf"
)

