# =====================================================
# EXECUTIVE PERSONALITY ENGINE — PREMIUM (STABLE)
# =====================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Executive Personality Profile", layout="centered")
PASSWORD = "1618"


#Google Sheets

conn = st.connection("gsheets", type=GSheetsConnection)
SHEET_URL = st.secrets["gsheets"]["spreadsheet"]

def save_result(name, scores):
    try:
        df_existing = conn.read(spreadsheet=SHEET_URL)

        new_row = pd.DataFrame([{
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nome": name,
            "O": scores["O"],
            "C": scores["C"],
            "E": scores["E"],
            "A": scores["A"],
            "N": scores["N"],
        }])

        df_updated = pd.concat([df_existing, new_row], ignore_index=True)
        conn.update(spreadsheet=SHEET_URL, data=df_updated)

    except:
        st.warning("Não foi possível salvar no Google Sheets.")



#LOGIN


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

#ETAPA 4 — FUNÇÕES PSICOMÉTRICAS

def personality_type(s):
    if max(s.values()) - min(s.values()) < 12:
        return "Balanced", "Perfil equilibrado, sem dominância forte."

    if s["O"] > 65 and s["E"] > 60:
        return "Explorer", "Curioso, inovador e orientado à exploração."

    if s["C"] > 65 and s["N"] < 45:
        return "Executor", "Focado, disciplinado e consistente."

    if s["A"] > 65 and s["C"] > 60:
        return "Diplomat", "Cooperativo, confiável e harmonizador."

    return "Analyst", "Reflexivo, estratégico e lógico."


def percentile(score, mean=50, std=15):
    z = (score - mean) / std
    p = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    return round(p * 100, 1)

#QUESTIONARIO
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
    "O":"Abertura à Experiência",
    "C":"Conscienciosidade",
    "E":"Extroversão",
    "A":"Amabilidade",
    "N":"Estabilidade Emocional"
}

pillars = list(QUESTIONS.keys())

if "step" not in st.session_state:
    st.session_state.step = 0

st.progress(st.session_state.step / 5)

if st.session_state.step < 5:

    p = pillars[st.session_state.step]
    st.subheader(PILLAR_NAMES[p])

    for qid, text, _ in QUESTIONS[p]:
        if qid not in st.session_state:
            st.session_state[qid] = 3

        st.slider(text, 1, 5, key=qid)

    col1, col2 = st.columns(2)

    if col1.button("⬅ Voltar") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if col2.button("Próximo ➡"):
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

#RESULTADOS + SAVE + BENCHMARK

if "scores" in st.session_state:

    s = st.session_state.scores
    name = st.text_input("Nome", "Participante")

    if "saved" not in st.session_state:
        save_result(name, s)
        st.session_state.saved = True

    ptype, pdesc = personality_type(s)

    st.markdown(f"## Perfil: **{ptype}**")
    st.write(pdesc)

    st.markdown("## Executive Snapshot")
    st.metric("Abertura", s["O"])
    st.metric("Execução", s["C"])
    st.metric("Energia Social", s["E"])
    st.metric("Cooperação", s["A"])
    st.metric("Estabilidade Emocional", 100 - s["N"])

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

    st.markdown("## Benchmark vs População")

    try:
        df_pop = conn.read(spreadsheet=SHEET_URL)

        for k in ["O","C","E","A","N"]:
            user = s[k] if k != "N" else 100 - s[k]
            pop_mean = df_pop[k].mean()

            st.write(f"**{PILLAR_NAMES[k]}**")
            st.metric("Você", round(user,1))
            st.metric("Média Pop.", round(pop_mean,1))
            st.progress(user/100)

    except:
        st.info("Benchmark aparecerá após acumular dados.")


