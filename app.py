# =====================================================
# EXECUTIVE PERSONALITY ENGINE — PREMIUM VERSION
# =====================================================

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors

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
# UI PREMIUM
# -----------------------------------------------------
st.markdown("""
<style>
.block-container { max-width:760px; padding:1rem; }
h1,h2,h3 { text-align:center; color:#1F4E79; }
button { width:100%; font-size:17px; border-radius:10px; }

.card { background:white; border-radius:14px; padding:18px; margin:10px 0;
box-shadow:0 4px 14px rgba(0,0,0,0.06); }

.kpi { text-align:center; padding:10px; border-radius:10px;
background:#F7FAFC; border:1px solid #E5E9F0; }
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
    if s["O"]>=70 and s["E"]>=60:
        return "Explorer","Curioso, inovador e orientado à exploração."
    if s["C"]>=70 and s["N"]<=40:
        return "Executor","Focado, disciplinado e consistente."
    if s["C"]>=60 and s["A"]>=60:
        return "Diplomat","Cooperativo, confiável e harmonizador."
    return "Analyst","Reflexivo, estratégico e lógico."

def percentile(v):
    if v>=85: return "Top 10%"
    if v>=70: return "Acima da média"
    if v>=40: return "Média"
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

pillars = list(QUESTIONS.keys())

if "step" not in st.session_state:
    st.session_state.step = 0

st.progress(st.session_state.step/5)

# -----------------------------------------------------
# ETAPAS
# -----------------------------------------------------
if st.session_state.step < 5:

    p = pillars[st.session_state.step]
    st.subheader(f"Pilar {st.session_state.step+1}/5")

    for qid,text,_ in QUESTIONS[p]:
        st.slider(text,1,5,3,key=qid)

    col1,col2 = st.columns(2)

    if col1.button("Voltar") and st.session_state.step>0:
        st.session_state.step -= 1
        st.rerun()

    if col2.button("Próximo"):
        st.session_state.step += 1
        st.rerun()

# -----------------------------------------------------
# SCORE
# -----------------------------------------------------
else:

scores = {}
for p in QUESTIONS:
    vals = []
    for qid, _, rev in QUESTIONS[p]:

        v = st.session_state.get(qid, 3)   # ← CORREÇÃO AQUI

        if rev:
            v = 6 - v

        vals.append(v)

    scores[p] = round((sum(vals) - 7) / 28 * 100, 1)

st.session_state.scores = scores


# -----------------------------------------------------
# RESULTADOS
# -----------------------------------------------------
if "scores" in st.session_state:

    s = st.session_state.scores

    st.markdown("### Executive Snapshot")

    cols = st.columns(5)
    for col,(k,v) in zip(cols,s.items()):
        with col:
            st.markdown(f"<div class='kpi'><b>{k}</b><br>{v}</div>", unsafe_allow_html=True)

    name = st.text_input("Nome para relatório","Participante")

    # Radar
    labels=["Abertura","Conscienciosidade","Extroversão","Amabilidade","Neuroticismo"]
    values=list(s.values())+[list(s.values())[0]]
    angles=np.linspace(0,2*np.pi,5,endpoint=False).tolist()
    angles+=angles[:1]

    fig=plt.figure(figsize=(5,5))
    ax=plt.subplot(polar=True)
    ax.plot(angles,values,color="#1F4E79",linewidth=2)
    ax.fill(angles,values,alpha=0.25,color="#2E86C1")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels,fontsize=9)
    ax.set_yticks([20,40,60,80,100])
    ax.set_title("Behavioral DNA",fontsize=12)
    st.pyplot(fig)

    # MATRIZ
    x=(s["E"]-s["N"]+100)/2
    y=(s["C"]+s["O"])/2

    fig2,ax2=plt.subplots(figsize=(5,5))
    ax2.axhline(50,ls="--",color="#C0C7D1")
    ax2.axvline(50,ls="--",color="#C0C7D1")
    ax2.scatter(x,y,s=150,color="#1F4E79")
    ax2.set_xlim(0,100)
    ax2.set_ylim(0,100)
    ax2.set_title("Executive Positioning Matrix")
    st.pyplot(fig2)

    # TIPOS
    ptype,pdesc = personality_type(s)
    st.markdown(f"### {ptype}")
    st.info(pdesc)

    # BENCHMARK
    st.markdown("### Population Benchmark")
    for k,v in s.items():
        st.progress(v/100,text=f"{k} — {percentile(v)} ({v})")

    # -------------------------------------------------
    # GPT ANALYSIS
    # -------------------------------------------------
    if GPT_AVAILABLE and "OPENAI_API_KEY" in st.secrets:

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

        if st.button("Gerar análise com IA"):

            prompt=f"Analise psicologicamente Big Five: {s}"

            with st.spinner("Gerando análise..."):
                try:
                    r = client.responses.create(
                        model="gpt-4o-mini",
                        input=prompt
                    )
                    st.session_state.analysis = r.output_text
                except Exception as e:
                    st.error("Erro IA")

    if "analysis" in st.session_state:
        st.markdown("### IA Analysis")
        st.write(st.session_state.analysis)

        # PDF
        def gerar_pdf(name,s,analysis):
            buffer=io.BytesIO()
            c=canvas.Canvas(buffer,pagesize=A4)
            w,h=A4

            c.setFont("Helvetica-Bold",18)
            c.drawString(2*cm,h-3*cm,"Executive Personality Report")
            c.drawString(2*cm,h-4*cm,name)

            y=h-6*cm
            for k,v in s.items():
                c.drawString(2*cm,y,f"{k}:{v}")
                y-=0.7*cm

            c.showPage()
            text=c.beginText(2*cm,h-3*cm)
            for line in analysis.split("\n"):
                text.textLine(line)
            c.drawText(text)
            c.save()
            buffer.seek(0)
            return buffer

        pdf = gerar_pdf(name,s,st.session_state.analysis)
        st.download_button("Baixar PDF",pdf,file_name="executive_profile.pdf")
