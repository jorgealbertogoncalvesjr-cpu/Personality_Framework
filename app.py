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
# ETAPA 1 — BASE UX + SCORE CORRIGIDO
# -----------------------------------------------------
st.markdown("""
<style>
.block-container { max-width:780px; padding:1.2rem; }

h1 { font-size:28px; }
h2 { font-size:22px; }
h3 { font-size:19px; }

.stSlider label { font-size:16px !important; }

button { width:100%; font-size:18px; padding:0.6rem; }

.likert {
    font-size:14px;
    color:#5A6A7A;
    margin-bottom:8px;
}

@media (max-width:768px){
    h1{font-size:24px}
    h2{font-size:20px}
    h3{font-size:17px}
}
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

st.markdown("""
<div class="likert">
<b>Escala:</b><br>
1 — Discordo totalmente<br>
2 — Discordo<br>
3 — Neutro<br>
4 — Concordo<br>
5 — Concordo totalmente
</div>
""", unsafe_allow_html=True)




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
# ETAPAS DO QUESTIONÁRIO (UX EM 5 PASSOS)
# -----------------------------------------------------

if st.session_state.step < 5:

    p = pillars[st.session_state.step]
    st.subheader(PILLAR_NAMES[p])

    # Perguntas do pilar atual
  # Perguntas do pilar atual
for qid, text, _ in QUESTIONS[p]:

    # garante persistência
    if qid not in st.session_state:
        st.session_state[qid] = 3

    st.slider(
        text,
        min_value=1,
        max_value=5,
        key=qid
    )



    col1, col2 = st.columns(2)

    with col1:
        if st.button("⬅ Voltar") and st.session_state.step > 0:
            st.session_state.step -= 1
            st.rerun()

    with col2:
        if st.button("Próximo ➡"):
            st.session_state.step += 1
            st.rerun()

else:

    # -------------------------------------------------
    # CÁLCULO DOS SCORES (0–100) — BLOCO CORRETO
    # -------------------------------------------------


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

            scores[p] = round((raw - 1) / 4 * 100, 1)

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

    # =========================
    # EXECUTIVE SNAPSHOT
    # =========================
    st.markdown("## Executive Snapshot")

    st.metric("🧠 Abertura Cognitiva", f"{s['O']}")
    st.metric("🎯 Execução & Disciplina", f"{s['C']}")
    st.metric("⚡ Energia Social", f"{s['E']}")
    st.metric("🤝 Cooperação", f"{s['A']}")
    st.metric("🧘 Estabilidade Emocional", f"{100 - s['N']}")

    # =========================
    # MATRIZ EXECUTIVA
    # =========================
    st.markdown("## Matriz Executiva de Posicionamento")

    x = (s["O"] + s["E"]) / 2
    y = (s["C"] + (100 - s["N"])) / 2

    fig, ax = plt.subplots(figsize=(6,6))

    ax.axhspan(50,100, xmin=0.5, xmax=1, alpha=0.08, color="green")
    ax.axhspan(50,100, xmin=0, xmax=0.5, alpha=0.08, color="blue")
    ax.axhspan(0,50, xmin=0, xmax=0.5, alpha=0.08, color="orange")
    ax.axhspan(0,50, xmin=0.5, xmax=1, alpha=0.08, color="purple")

    ax.axhline(50, linestyle="--")
    ax.axvline(50, linestyle="--")

    ax.scatter(x, y, s=180, color="#1F4E79")

    ax.set_xlim(0,100)
    ax.set_ylim(0,100)

    ax.set_xlabel("Visão & Influência")
    ax.set_ylabel("Execução & Consistência")

    ax.text(75,85,"Líder Estratégico", ha="center", fontsize=9)
    ax.text(25,85,"Executor Técnico", ha="center", fontsize=9)
    ax.text(25,15,"Zona de Desenvolvimento", ha="center", fontsize=9)
    ax.text(75,15,"Perfil Adaptativo", ha="center", fontsize=9)

    st.pyplot(fig)

    st.info("""
    **Como interpretar**

    🔵 Executor Técnico → forte execução, menor influência  
    🟢 Líder Estratégico → visão + execução elevadas  
    🟠 Zona de Desenvolvimento → foco em evolução  
    🟣 Perfil Adaptativo → flexível e explorador  
    """)

    # =========================
    # BENCHMARK
    # =========================
    st.markdown("## Benchmark Populacional")

    for k, v in s.items():
        user = v if k != "N" else 100 - v
        pop = 50

        diff = user - pop

        st.write(f"**{PILLAR_NAMES[k]}**")

        col1, col2 = st.columns(2)
        col1.metric("Você", f"{user}")
        col2.metric("População", f"{pop}", delta=f"{diff:+}")

        st.progress(user/100)
