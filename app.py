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
# PAGE CONFIG — SEMPRE PRIMEIRO
# -----------------------------------------------------
st.set_page_config(page_title="Executive Personality Engine", layout="centered")

# -----------------------------------------------------
# SESSION STATE — SAFE INIT (ANTI RESET)
# -----------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 0

if "scores" not in st.session_state:
    st.session_state.scores = None

if "saved" not in st.session_state:
    st.session_state.saved = False

# inicializa sliders apenas UMA vez
if "init" not in st.session_state:
    for p in ["o","c","e","a","n"]:
        for i in range(1,8):
            key = f"{p}{i}"
            if key not in st.session_state:
                st.session_state[key] = 3
    st.session_state.init = True

# -----------------------------------------------------
# UI STYLE
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
    st.sidebar.error("Google Sheets OFF")
    st.sidebar.code(str(e))


@st.cache_data(ttl=900, show_spinner=False)
def load_population():

    if not google_ok or sheet is None:
        return pd.DataFrame()

    try:
        df = pd.DataFrame(sheet.get_all_records())

        for c in ["O","C","E","A","N"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df

    except Exception as e:

        if "Quota exceeded" in str(e):
            st.warning("Google quota temporariamente excedida. Usando cache local.")
            return st.session_state.get("df_pop", pd.DataFrame())

        return pd.DataFrame()


def save_result(name, s):
    if not google_ok or sheet is None:
        return
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name,
        float(s["O"]), float(s["C"]), float(s["E"]),
        float(s["A"]), float(s["N"])
    ]
    sheet.append_row(row, value_input_option="USER_ENTERED")


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



progress_pct = int((st.session_state.step / TOTAL_STEPS) * 100)

st.progress(st.session_state.step / TOTAL_STEPS)

if st.session_state.step < TOTAL_STEPS:

    p = pillars[st.session_state.step]

    st.subheader(PILLAR_NAMES[p])
    st.caption("1 = Discordo totalmente • 3 = Neutro • 5 = Concordo totalmente")

    for qid, text, _ in QUESTIONS[p]:

        if qid not in st.session_state:
            st.session_state[qid] = 3

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
            v = st.session_state[qid]
            if rev:
                v = 6 - v
            vals.append(v)

        raw = sum(vals) / len(vals)
        scores[p] = round((raw - 1) / 4 * 100, 1)

    st.session_state.scores = scores


if st.session_state.scores is None:
    st.stop()

s = st.session_state.scores

if (
    not st.session_state.saved
    and s is not None
    and sum(s.values()) != 250   # evita salvar tudo 50
):
    save_result("Participante", s)
    st.session_state.saved = True


st.markdown("## Executive Profile")

labels = {
    "O":"Abertura",
    "C":"Execução",
    "E":"Energia Social",
    "A":"Cooperação",
    "N":"Estabilidade Emocional"
}

cols = st.columns(5)

for i, k in enumerate(["O","C","E","A","N"]):
    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(labels[k], f"{round(val,1)}")


st.markdown("## Executive Profile")

labels = {
    "O":"Abertura",
    "C":"Execução",
    "E":"Energia Social",
    "A":"Cooperação",
    "N":"Estabilidade Emocional"
}

cols = st.columns(5)

for i, k in enumerate(["O","C","E","A","N"]):
    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(labels[k], f"{round(val,1)}")

x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

st.markdown("### Executive Interpretation")

if x > 65 and y > 65:
    st.success("Strategic Leadership Profile — strong vision and execution capacity.")
elif x < 50 and y > 65:
    st.info("Execution Specialist — disciplined and delivery-oriented.")
elif x > 65 and y < 50:
    st.warning("Influencer Profile — strong vision, execution varies.")
else:
    st.error("Development Zone — focus on structure and consistency.")


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


st.markdown("### Population Benchmark")

if "df_pop" not in st.session_state:
    st.session_state.df_pop = load_population()

df_pop = st.session_state.df_pop

if not df_pop.empty and len(df_pop) > 5:

    for k in ["O","C","E","A","N"]:

        user_val = s[k] if k != "N" else 100 - s[k]
        pop_mean = df_pop[k].mean()

        st.write(f"**{labels[k]}**")
        st.metric("You", round(user_val,1))
        st.metric("Population Mean", round(pop_mean,1))
        st.progress(user_val / 100)

else:
    st.info("Benchmark will appear after more data is collected.")

st.markdown("### Executive Percentile")

for k in ["O","C","E","A","N"]:
    val = s[k] if k != "N" else 100 - s[k]
    pct = percentile(val)
    st.metric(f"{labels[k]} Percentile", f"{pct}%")

st.markdown("### Executive Report PDF")

from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

def gerar_pdf(name, s):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # PAGE 1 — SUMMARY
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height-2.5*cm, "Executive Personality Report")

    c.setFont("Helvetica", 11)
    c.drawString(2*cm, height-3.5*cm, f"Participant: {name}")
    c.drawString(2*cm, height-4.2*cm, f"Date: {datetime.now().strftime('%Y-%m-%d')}")

    y = height - 6*cm
    for k in ["O","C","E","A","N"]:
        val = s[k] if k != "N" else 100 - s[k]
        c.drawString(2*cm, y, f"{k}: {round(val,1)}")
        y -= 0.7*cm

    c.showPage()

    # PAGE 2 — RADAR
    labels_radar = ["O","C","E","A","N"]
    vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]

    angles = np.linspace(0, 2*np.pi, len(vals), endpoint=False).tolist()
    vals += vals[:1]
    angles += angles[:1]

    fig = plt.figure(figsize=(4,4))
    ax = plt.subplot(polar=True)
    ax.plot(angles, vals)
    ax.fill(angles, vals, alpha=0.1)

    img = io.BytesIO()
    plt.savefig(img, format="PNG", bbox_inches="tight")
    plt.close(fig)
    img.seek(0)

    c.drawImage(ImageReader(img), 3*cm, height-16*cm, width=12*cm, height=12*cm)
    c.showPage()

    # PAGE 3 — MATRIX
    x = (s["O"] + s["E"]) / 2
    y = (s["C"] + (100 - s["N"])) / 2

    fig, ax = plt.subplots(figsize=(4,4))
    ax.axhline(50, linestyle="--")
    ax.axvline(50, linestyle="--")
    ax.scatter(x, y)
    ax.set_xlim(0,100)
    ax.set_ylim(0,100)

    img2 = io.BytesIO()
    plt.savefig(img2, format="PNG", bbox_inches="tight")
    plt.close(fig)
    img2.seek(0)

    c.drawImage(ImageReader(img2), 3*cm, height-16*cm, width=12*cm, height=12*cm)
    c.save()

    buffer.seek(0)
    return buffer

name_pdf = st.text_input("Nome no relatório", "Participante")
pdf_file = gerar_pdf(name_pdf, s)

st.download_button("📄 Download Executive Report", pdf_file, "Executive_Report.pdf")

st.markdown("### Executive Cluster")

if leadership > 75 and x > 65:
    st.success("Strategic Leader")
elif s["C"] > 65:
    st.info("Execution Driver")
elif s["A"] > 65:
    st.info("Integrator")
else:
    st.warning("Adaptive Profile")

st.markdown("### Consistency Index")

std = np.std(list(s.values()))
consistency = round(100 - std * 3, 1)

st.metric("Consistency Score", consistency)

if consistency > 80:
    st.success("Alta consistência comportamental")
elif consistency > 65:
    st.info("Perfil relativamente consistente")
else:
    st.warning("Alta variabilidade comportamental")

st.markdown("### Benchmark vs Population")

if "df_pop" not in st.session_state:
    st.session_state.df_pop = load_population()

df_pop = st.session_state.df_pop

if not df_pop.empty and len(df_pop) > 5:

    pop_means = [
        df_pop["O"].mean(),
        df_pop["C"].mean(),
        df_pop["E"].mean(),
        df_pop["A"].mean(),
        df_pop["N"].mean()
    ]

    user_vals = [s["O"], s["C"], s["E"], s["A"], s["N"]]

    fig, ax = plt.subplots(figsize=(6,4))
    x_axis = np.arange(5)

    ax.bar(x_axis - 0.2, user_vals, 0.4, label="You")
    ax.bar(x_axis + 0.2, pop_means, 0.4, label="Population")

    ax.set_xticks(x_axis)
    ax.set_xticklabels(["O","C","E","A","N"])
    ax.set_ylim(0,100)
    ax.legend()

    st.pyplot(fig)

else:
    st.info("Benchmark gráfico disponível após maior base de dados.")

st.markdown("### Benchmark vs Population")

if "df_pop" not in st.session_state:
    st.session_state.df_pop = load_population()

df_pop = st.session_state.df_pop

if not df_pop.empty and len(df_pop) > 5:

    pop_means = [
        df_pop["O"].mean(),
        df_pop["C"].mean(),
        df_pop["E"].mean(),
        df_pop["A"].mean(),
        df_pop["N"].mean()
    ]

    user_vals = [s["O"], s["C"], s["E"], s["A"], s["N"]]

    fig, ax = plt.subplots(figsize=(6,4))
    x_axis = np.arange(5)

    ax.bar(x_axis - 0.2, user_vals, 0.4, label="You")
    ax.bar(x_axis + 0.2, pop_means, 0.4, label="Population")

    ax.set_xticks(x_axis)
    ax.set_xticklabels(["O","C","E","A","N"])
    ax.set_ylim(0,100)
    ax.legend()

    st.pyplot(fig)

else:
    st.info("Benchmark gráfico disponível após maior base de dados.")


st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="metric-container"] {
    background: white;
    border: 1px solid #E5E7EB;
    padding: 12px;
    border-radius: 10px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
}

h2, h3 {
    color: #1F2A44;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)
