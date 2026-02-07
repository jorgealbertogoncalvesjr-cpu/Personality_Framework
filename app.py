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


st.set_page_config(page_title="Executive Personality Engine", layout="centered")

st.markdown("""
<style>
    .stSlider > div {
        padding-bottom: 12px;
    }
    .stButton button {
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)



# -----------------------------------------------------
# SESSION STATE — ANTI RESET DEFINITIVO
# -----------------------------------------------------
if "answers" not in st.session_state:
    st.session_state.answers = {}

def get_answer(key):
    return st.session_state.answers.get(key, 3)

def set_answer(key, val):
    st.session_state.answers[key] = val




# -----------------------------------------------------
# LEGAL / AUTORES / BASE CIENTÍFICA
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

<b>Base científica:</b> Modelo dos Cinco Grandes Fatores de Personalidade (Big Five / OCEAN)<br>

<b>Autores fundamentais:</b><br>
• Lewis Goldberg (1990) — Estrutura lexical da personalidade<br>
• Paul Costa & Robert McCrae (1992) — NEO-PI-R<br>

<b>Nota:</b> Esta aplicação é uma ferramenta de desenvolvimento e autoconhecimento, 
não constitui diagnóstico psicológico ou avaliação clínica.

</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# SESSION INIT — ANTI RESET
# -----------------------------------------------------
if "init" not in st.session_state:
    for p in ["o","c","e","a","n"]:
        for i in range(1,8):
            st.session_state[f"{p}{i}"] = 3
    st.session_state.step = 0
    st.session_state.init = True

PASSWORD = "1618"

# -----------------------------------------------------
# GOOGLE SHEETS SAFE CONNECT
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


    if sheet is None:
        return pd.DataFrame()
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()


# -----------------------------------------------------
# CACHE POPULATION — ANTI QUOTA
# -----------------------------------------------------
@st.cache_data(ttl=60)
def load_population():
    if not google_ok:
        return pd.DataFrame()
    try:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except:
        return pd.DataFrame()

# -----------------------------------------------------
# SAVE RESULT
# -----------------------------------------------------
def save_result(name, scores):
    if not google_ok:
        return
    try:
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            scores["O"],
            scores["C"],
            scores["E"],
            scores["A"],
            scores["N"]
        ]
        sheet.append_row(row)
    except:
        pass

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
# UX QUESTIONÁRIO — MOBILE / CONSULTORIA
# -----------------------------------------------------

TOTAL_STEPS = 5

progress_pct = int((st.session_state.step / TOTAL_STEPS) * 100)

st.markdown(f"""
### 🧠 Avaliação de Perfil Executivo  
**Etapa {st.session_state.step + 1} de {TOTAL_STEPS} — {progress_pct}% concluído**
""")

st.progress(st.session_state.step / TOTAL_STEPS)

# ---------- PILAR HEADER ----------
if st.session_state.step < 5:

    p = pillars[st.session_state.step]

    st.markdown(f"""
    <div style="
        padding:14px;
        border-radius:10px;
        background:#EEF4FF;
        border-left:6px solid #4A7BFF;
        margin-bottom:10px;
    ">
        <b style="font-size:18px">{PILLAR_NAMES[p]}</b><br>
        <span style="font-size:13px;color:#555">
        Avalie o quanto cada afirmação representa você.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # ---------- LEGENDA ----------
    st.caption("1 = Discordo totalmente | 3 = Neutro | 5 = Concordo totalmente")

    # ---------- QUESTIONS ----------
    for qid, text, _ in QUESTIONS[p]:

        if qid not in st.session_state:
            st.session_state[qid] = 3

        st.slider(
            label=text,
            min_value=1,
            max_value=5,
            key=qid
        )

    # ---------- NAV BUTTONS ----------
    c1, c2 = st.columns(2)

    if c1.button("⬅ Voltar", use_container_width=True) and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if c2.button("Próximo ➡", use_container_width=True):
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
# RESULTS
# -----------------------------------------------------
if "scores" not in st.session_state:
    st.stop()

s=st.session_state.scores
name=st.text_input("Nome","Participante")

if "saved" not in st.session_state:
    save_result(name,s)
    st.session_state.saved=True

# -----------------------------------------------------
# EXECUTIVE SNAPSHOT
# -----------------------------------------------------
st.header("Executive Snapshot")
for k,v in s.items():
    val=v if k!="N" else 100-v
    st.metric(k, val)

# -----------------------------------------------------
# MATRIX CONSULTING
# -----------------------------------------------------
st.subheader("Matriz Executiva de Posicionamento")

x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

fig, ax = plt.subplots(figsize=(6,6))

# Quadrantes
ax.fill_between([0,50], 50,100, alpha=0.12)
ax.fill_between([50,100],50,100, alpha=0.05)
ax.fill_between([0,50],0,50, alpha=0.04)
ax.fill_between([50,100],0,50, alpha=0.09)

ax.axhline(50, linestyle="--")
ax.axvline(50, linestyle="--")

ax.scatter(x, y, s=250)

ax.text(20,80,"Executor Técnico", fontsize=9)
ax.text(65,80,"Líder Estratégico", fontsize=9)
ax.text(15,20,"Zona de Desenvolvimento", fontsize=9)
ax.text(65,20,"Perfil Adaptativo", fontsize=9)

ax.set_xlim(0,100)
ax.set_ylim(0,100)
ax.set_xlabel("Visão & Influência")
ax.set_ylabel("Execução & Consistência")

st.pyplot(fig)


#CONSULTORIA REAL

st.subheader("Leitura Executiva")

if x > 60 and y > 60:
    st.success("Perfil de Liderança Estratégica — visão sistêmica e alta execução.")
elif x < 50 and y > 60:
    st.info("Executor Técnico — forte capacidade de entrega e disciplina.")
elif x > 60 and y < 50:
    st.warning("Perfil Influenciador — visão elevada, execução variável.")
else:
    st.error("Zona de Desenvolvimento — foco em estrutura e consistência.")


# -----------------------------------------------------
# RADAR
# -----------------------------------------------------
st.subheader("Radar Comportamental")

labels = ["Abertura","Execução","Energia Social","Cooperação","Estabilidade"]
vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]

angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
vals += vals[:1]
angles += angles[:1]

fig = plt.figure(figsize=(5,5))
ax = plt.subplot(polar=True)

ax.plot(angles, vals, linewidth=2)
ax.fill(angles, vals, alpha=0.15)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)
ax.set_yticks([20,40,60,80])
ax.set_ylim(0,100)

st.pyplot(fig)

#Indice de Liderança Executiva

st.subheader("Índice de Liderança Executiva")

leadership = (s["C"]*0.35 + s["O"]*0.20 + s["E"]*0.20 + s["A"]*0.15 + (100-s["N"])*0.10)

st.metric("Leadership Score", round(leadership,1))

if leadership > 70:
    st.success("Alta capacidade de liderança executiva")
elif leadership > 55:
    st.info("Perfil de liderança em desenvolvimento")
else:
    st.warning("Potencial de liderança a desenvolver")



# -----------------------------------------------------
# BENCHMARK
# -----------------------------------------------------
st.subheader("Benchmark Populacional")

df_pop = load_population()

if not df_pop.empty:
    for k in ["O","C","E","A","N"]:
        user = s[k] if k!="N" else 100-s[k]
        pop = df_pop[k].mean()

        st.write(f"**{k}**")
        st.metric("Você", round(user,1))
        st.metric("Média", round(pop,1))
        st.progress(user/100)
else:
    st.info("Benchmark será exibido após acumular dados.")


#Cluster Executivo
st.subheader("Cluster Executivo")

if leadership > 70 and x > 60:
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
st.subheader("Consistency Index")
std=np.std(list(s.values()))
st.metric("Índice",round(100-std*3,1))

File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/exec_code.py", line 75, in exec_func_with_error_handling
    result = func()
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_runner.py", line 574, in code_to_exec
    exec(code, module.__dict__)
    ~~~~^^^^^^^^^^^^^^^^^^^^^^^
File "/mount/src/personality_framework/app.py", line 45, in <module>
    st.set_page_config(page_title="Executive Personality Engine", layout="centered")
    ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/metrics_util.py", line 408, in wrapped_func
    result = non_optional_func(*args, **kwargs)
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/commands/page_config.py", line 260, in set_page_config
    ctx.enqueue(msg)
    ~~~~~~~~~~~^^^^^
File "/home/adminuser/venv/lib/python3.13/site-packages/streamlit/runtime/scriptrunner/script_run_context.py", line 140, in enqueue
    raise StreamlitAPIException(
    ...<4 lines>...
    )
