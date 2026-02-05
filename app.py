# =====================================================
# EXECUTIVE PERSONALITY ENGINE — PREMIUM (STABLE)
# =====================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# GPT opcional
try:
    from openai import OpenAI
    GPT_AVAILABLE = True
except:
    GPT_AVAILABLE = False

# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="Executive Personality Profile", layout="centered")
PASSWORD = "1618"

# -----------------------------------------------------
# UI
# -----------------------------------------------------
st.markdown("""
<style>
.block-container { max-width:760px; }
h1,h2,h3 { text-align:center; color:#1F4E79; }
button { width:100%; }
</style>
""", unsafe_allow_html=True)

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
# FUNÇÕES
# -----------------------------------------------------
def personality_type(s):
    if s["O"] >= 70 and s["E"] >= 60:
        return "Explorer", "Curioso, inovador e orientado à exploração."
    if s["C"] >= 70 and s["N"] <= 40:
        return "Executor", "Focado, disciplinado e consistente."
    if s["C"] >= 60 and s["A"] >= 60:
        return "Diplomat", "Cooperativo, confiável e harmonizador."
    return "Analyst", "Reflexivo, estratégico e lógico."

def percentile(v):
    if v >= 85: return "Top 10%"
    if v >= 70: return "Acima da média"
    if v >= 40: return "Média"
    return "Abaixo da média"

# -----------------------------------------------------
# QUESTIONÁRIO
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

# -----------------------------------------------------
# ETAPAS
# -----------------------------------------------------
if st.session_state.step < 5:
    p = pillars[st.session_state.step]
    st.subheader(PILLAR_NAMES[p])

    for qid, text, _ in QUESTIONS[p]:
        st.slider(text, 1, 5, 3, key=qid)

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
            if rev: v = 6 - v
            vals.append(v)
        scores[p] = round((sum(vals) - 7) / 28 * 100, 1)
    st.session_state.scores = scores

# -----------------------------------------------------
# RESULTADOS
# -----------------------------------------------------
if "scores" in st.session_state:

    s = st.session_state.scores
    name = st.text_input("Nome", "Participante")

    ptype, pdesc = personality_type(s)

    st.markdown(f"## Perfil Comportamental: **{ptype}**")
    st.write(pdesc)

    st.markdown("### Executive Snapshot")
    st.metric("Abertura", s["O"])
    st.metric("Execução", s["C"])
    st.metric("Energia Social", s["E"])
    st.metric("Cooperação", s["A"])
    st.metric("Estabilidade Emocional", 100 - s["N"])

    st.markdown("### Matriz Executiva")
    x = (s["O"] + s["E"]) / 2
    y = (s["C"] + (100 - s["N"])) / 2

    fig, ax = plt.subplots()
    ax.scatter(x, y, s=160)
    ax.axhline(50, ls="--")
    ax.axvline(50, ls="--")
    ax.set_xlim(0,100)
    ax.set_ylim(0,100)
    st.pyplot(fig)

    st.markdown("### Benchmark Populacional")
    for k,v in s.items():
        display = v if k!="N" else 100-v
        st.progress(display/100, f"{PILLAR_NAMES[k]} — {percentile(display)}")

