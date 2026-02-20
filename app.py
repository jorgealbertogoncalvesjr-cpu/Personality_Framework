# =====================================================
# EXECUTIVE ENGINE — LOW READ ARCHITECTURE (ANTI 429)
# =====================================================

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    st.sidebar.error("Google OFF")
    st.sidebar.code(str(e))


# ---------------- LOW READ POPULATION ----------------

@st.cache_data(ttl=900, show_spinner=False)   # 15 min
def load_population_lowread():

    if not google_ok or sheet is None:
        return pd.DataFrame()

    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        for c in ["O","C","E","A","N"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce")

        return df

    except Exception as e:

        # QUOTA EXCEEDED → usa cache local
        if "429" in str(e) or "Quota exceeded" in str(e):
            if "df_pop" in st.session_state:
                return st.session_state.df_pop
            return pd.DataFrame()

        return pd.DataFrame()


# NÃO carregar durante questionário
df_pop = pd.DataFrame()

def get_population_if_needed():

    if st.session_state.step < 5:
        return pd.DataFrame()

    if "df_pop" not in st.session_state:
        st.session_state.df_pop = load_population_lowread()

    return st.session_state.df_pop


# ---------------- SAVE (WRITE SAFE) ----------------

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


# ---------------- SAVE (WRITE SAFE) ----------------

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


# ---------------- SAVE (WRITE SAFE) ----------------

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



# =====================================================
# CÁLCULO FINAL (EXECUTA APENAS NA ÚLTIMA ETAPA)
# =====================================================
else:

    scores = {}

    for p in QUESTIONS:

        vals = []

        for qid, _, rev in QUESTIONS[p]:

            # segurança: garante que resposta existe
            if qid not in st.session_state:
                st.error(f"Resposta ausente: {qid}")
                st.stop()

            v = int(st.session_state[qid])

            if rev:
                v = 6 - v

            vals.append(v)

        raw = sum(vals) / len(vals)
        scores[p] = round((raw - 1) / 4 * 100, 1)

    st.session_state.scores = scores


# =====================================================
# RESULTS
# =====================================================
if st.session_state.scores is None:
    st.stop()

s = st.session_state.scores
name = st.text_input("Nome", "Participante")


# -----------------------------------------------------
# SAVE — EVITA SALVAR SCORE DEFAULT (50)
# -----------------------------------------------------
if (
    not st.session_state.saved
    and s is not None
    and sum(s.values()) != 250     # evita salvar tudo 50
):
    save_result(name, s)
    st.session_state.saved = True


# =====================================================
# EXECUTIVE PROFILE
# =====================================================
st.header("Executive Profile")

cols = st.columns(5)

for i, k in enumerate(["O","C","E","A","N"]):

    val = s[k] if k != "N" else 100 - s[k]
    cols[i].metric(k, round(val, 1))


# =====================================================
# LOAD POPULATION — APENAS AGORA (LOW READ)
# =====================================================
df_pop = get_population_if_needed()


# =====================================================
# EXECUTIVE PERCENTILE (SEGURO)
# =====================================================
st.subheader("Executive Percentile")

for k in ["O","C","E","A","N"]:

    val = s[k] if k != "N" else 100 - s[k]

    # se base vazia → neutro
    if df_pop.empty or k not in df_pop.columns:
        pct = 50
    else:
        pct = percentile(val, k)

    st.metric(f"{k} Percentile", f"{pct}%")


# =====================================================
# BENCHMARK (SÓ SE HOUVER BASE)
# =====================================================
st.subheader("Benchmark")

if not df_pop.empty and len(df_pop) > 3:

    for k in ["O","C","E","A","N"]:

        user_val = s[k] if k != "N" else 100 - s[k]
        pop_mean = df_pop[k].mean()

        st.write(f"**{k}**")

        c1, c2 = st.columns(2)
        c1.metric("Você", round(user_val, 1))
        c2.metric("Média", round(pop_mean, 1))

        st.progress(min(max(user_val / 100, 0), 1))

else:
    st.info("Benchmark aparecerá após acumular dados suficientes.")
