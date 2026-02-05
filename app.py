import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

# GPT (opcional)
try:
    from openai import OpenAI
    GPT_AVAILABLE = True
except:
    GPT_AVAILABLE = False

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors

st.set_page_config(
    page_title="Executive Personality Profile",
    page_icon="🧠",
    layout="centered"
)

PASSWORD = "1618"

#ETAPA 2 — ESTILO (MOBILE + C-LEVEL)

st.markdown("""
<style>
.block-container { max-width:720px; padding:1rem; }
h1,h2,h3 { text-align:center; }
.big-card { background:#f5f7fa; padding:22px; border-radius:14px; margin-bottom:18px; }
button { width:100%; font-size:18px; }
.small { font-size:12px; color:#6c757d; text-align:center; }
</style>
""", unsafe_allow_html=True)

#Tipologia

def personality_type(scores):
    if scores["O"] >= 70 and scores["E"] >= 60:
        return "Explorer", "Perfil estratégico, orientado à inovação."
    if scores["C"] >= 70 and scores["N"] <= 40:
        return "Executor", "Perfil focado em entrega e consistência."
    if scores["C"] >= 60 and scores["A"] >= 60:
        return "Diplomat", "Perfil cooperativo e confiável."
    return "Analyst", "Perfil analítico e orientado à decisão racional."

#Percentil

def percentile(score):
    if score >= 85: return "Top 10%"
    if score >= 70: return "Acima da média"
    if score >= 40: return "Média populacional"
    return "Abaixo da média"


#PDF

def gerar_pdf(name, scores, quadrant, analysis):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(w/2, h-3*cm, "Relatório Executivo de Perfil")

    c.setFont("Helvetica", 12)
    c.drawCentredString(w/2, h-4.5*cm, f"Participante: {name}")

    y = h-6*cm
    for k, v in scores.items():
        c.drawString(2*cm, y, f"{k}: {v}")
        y -= 0.7*cm

    c.drawString(2*cm, y-0.5*cm, f"Posicionamento: {quadrant}")

    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, h-3*cm, "Análise Estratégica")

    text = c.beginText(2*cm, h-4.5*cm)
    text.setFont("Helvetica", 11)
    for line in analysis.split("\n"):
        text.textLine(line)
    c.drawText(text)

    c.save()
    buffer.seek(0)
    return buffer


#ETAPA 4 — LOGIN

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.title("🧠 Executive Personality Assessment")

    st.markdown("""
<div class="big-card">
Descubra seu perfil psicológico baseado no modelo **Big Five (IPIP)**.
</div>
""", unsafe_allow_html=True)

    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")

    st.stop()


#ETAPA 5 — INÍCIO DO TESTE

st.title("Executive Personality Profile")

if "start_test" not in st.session_state:
    st.session_state.start_test = False

if st.button("Iniciar Avaliação"):
    st.session_state.start_test = True

#ETAPA 6 — QUESTIONÁRIO (35 PERGUNTAS)

QUESTIONS = {
    "O":[("o1","Tenho imaginação rica",False),("o2","Gosto de ideias abstratas",False),
         ("o3","Tenho interesse por arte",False),("o4","Prefiro rotina",True),
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

if st.session_state.start_test:

    for p in QUESTIONS:
        st.subheader(f"Pilar {p}")
        for qid, text, _ in QUESTIONS[p]:
            st.slider(text,1,5,3,key=qid)

    if st.button("Calcular Resultado"):

        scores={}
        for p in QUESTIONS:
            vals=[]
            for qid,_,rev in QUESTIONS[p]:
                v=st.session_state[qid]
                if rev: v=6-v
                vals.append(v)
            scores[p]=round((sum(vals)-7)/28*100,1)

        st.session_state.scores=scores



#ETAPA 7 — RESULTADOS EXECUTIVOS
if "scores" in st.session_state:

    scores=st.session_state.scores

    name=st.text_input("Seu nome","Participante")

    st.markdown("## Executive Behavioral Radar")

    labels=["Abertura","Conscienciosidade","Extroversão","Amabilidade","Neuroticismo"]
    values=list(scores.values())
    values+=values[:1]

    angles=np.linspace(0,2*np.pi,5,endpoint=False).tolist()
    angles+=angles[:1]

    fig=plt.figure(figsize=(5,5))
    ax=plt.subplot(polar=True)
    ax.plot(angles,values)
    ax.fill(angles,values,alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    st.pyplot(fig)


#ETAPA 8 — TIPO + BENCHMARK


if "scores" in st.session_state:
    scores = st.session_state.scores
    ptype, pdesc = personality_type(scores)

    st.markdown("## 🧬 Seu Tipo de Personalidade")
    st.success(f"**{ptype}** — {pdesc}")


st.subheader("Benchmark Populacional")
for k,v in scores.items():
    st.write(k, v, percentile(v))

#ETAPA 9 — GPT

if GPT_AVAILABLE and "OPENAI_API_KEY" in st.secrets and "scores" in st.session_state:

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    scores = st.session_state.scores

    if st.button("Gerar análise personalizada com IA"):

        prompt = f"""
Você é um psicólogo comportamental especialista no modelo Big Five.

Gere uma análise clara, profissional e construtiva.

Pontuações:
Abertura: {scores['O']}
Conscienciosidade: {scores['C']}
Extroversão: {scores['E']}
Amabilidade: {scores['A']}
Neuroticismo: {scores['N']}

Estruture em:
1. Visão geral
2. Estilo cognitivo
3. Perfil emocional
4. Comportamento social
5. Pontos fortes
6. Pontos de atenção
"""

        with st.spinner("Gerando análise psicológica personalizada..."):
            try:
                response = client.responses.create(
                    model="gpt-4o-mini",
                    input=prompt
                )
                st.session_state.analysis = response.output_text
            except Exception as e:
                st.error("Erro ao gerar análise com IA.")
                st.exception(e)

if "analysis" in st.session_state:
    st.markdown("## 🧠 Análise Psicológica (IA)")
    st.write(st.session_state.analysis)


