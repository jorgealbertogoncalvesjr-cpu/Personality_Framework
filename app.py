# =====================================================
# EXECUTIVE PERSONALITY ENGINE — CLEAN STABLE VERSION
# =====================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

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


# ---------------- GOOGLE CONNECT ----------------
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


# ---------------- LOAD POPULATION (CACHE) ----------------
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


if "df_pop" not in st.session_state:
    st.session_state.df_pop = load_population()

df_pop = st.session_state.df_pop


# ---------------- SAVE RESULT ----------------
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


# ---------------- PERCENTILE ----------------
def percentile(value, col):

    if df_pop.empty or col not in df_pop.columns:
        return 50

    series = df_pop[col].dropna()
    if len(series) == 0:
        return 50

    return int((series < value).mean() * 100)

# =====================================================
# ATAPA II LOGIN + QUESTIONARIO
# =====================================================

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
    st.subheader(f"Pilar: {p}")

    for qid, text, _ in QUESTIONS[p]:

        st.slider(
            label=text,
            min_value=1,
            max_value=5,
            key=qid
        )

    c1, c2 = st.columns(2)

    if c1.button("⬅ Voltar") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if c2.button("Próximo ➡"):
        st.session_state.step += 1
        st.rerun()



# =====================================================
# ETAPA III Calculo
# =====================================================

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


# =====================================================
# ETAPA IV RESULTADOS
# =====================================================


if st.session_state.scores is None:
    st.stop()

s = st.session_state.scores
name = st.text_input("Nome", "Participante")

if not st.session_state.saved and sum(s.values()) != 250:
    save_result(name, s)
    st.session_state.saved = True


st.header("Executive Profile")

cols = st.columns(5)
for i, k in enumerate(["O","C","E","A","N"]):
    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(k, round(val,1))


# ---------- MATRIX ----------
x = (s["O"] + s["E"]) / 2
y = (s["C"] + (100 - s["N"])) / 2

st.subheader("Leitura Executiva")

if x > 60 and y > 60:
    st.success("Perfil Estratégico")
elif x < 50 and y > 60:
    st.info("Executor Técnico")
elif x > 60 and y < 50:
    st.warning("Perfil Influenciador")
else:
    st.error("Zona de Desenvolvimento")


# ---------- PERCENTILE ----------
st.subheader("Executive Percentile")

for k in ["O","C","E","A","N"]:
    val = s[k] if k != "N" else 100 - s[k]
    pct = percentile(val, k)
    st.metric(f"{k} Percentile", f"{pct}%")

# =====================================================
# ETAPA V BENCHMARK
# =====================================================

st.subheader("Benchmark Populacional")

if not df_pop.empty:

    for k in ["O","C","E","A","N"]:

        user_val = s[k] if k != "N" else 100 - s[k]
        pop_mean = df_pop[k].mean()

        st.write(f"**{k}**")
        st.metric("Você", round(user_val,1))
        st.metric("Média", round(pop_mean,1))
        st.progress(user_val / 100)

else:
    st.info("Benchmark aparecerá após mais dados.")
