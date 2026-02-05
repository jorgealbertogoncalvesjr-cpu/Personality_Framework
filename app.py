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

st.set_page_config(page_title="Executive Personality Profile", layout="centered")
PASSWORD = "1618"



# =========================
# UI PREMIUM — THEME
# =========================
st.markdown("""
<style>
:root {
  --primary:#1F4E79;
  --accent:#2E86C1;
  --bg:#F4F6F8;
  --text:#1C2833;
}

.block-container { max-width:760px; padding:1rem; }
h1,h2,h3 { text-align:center; color:var(--primary); }

.card {
  background:white;
  border-radius:14px;
  padding:18px 20px;
  margin:12px 0;
  box-shadow:0 4px 14px rgba(0,0,0,0.06);
}

.kpi {
  text-align:center;
  padding:12px;
  border-radius:12px;
  background:linear-gradient(180deg,#FFFFFF,#F7FAFC);
  border:1px solid #E5E9F0;
}

button { width:100%; font-size:17px; border-radius:10px; }
.small { font-size:12px; color:#6B7280; text-align:center; }

@media (max-width:768px){
  h1{font-size:1.6rem}
  h2{font-size:1.3rem}
}
</style>
""", unsafe_allow_html=True)



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


st.markdown("### Behavioral Archetype")

st.markdown(f"""
<div class="card">
<h3>{ptype}</h3>
<p>{pdesc}</p>
</div>
""", unsafe_allow_html=True)


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



if "step" not in st.session_state:
    st.session_state.step=0

pillars=list(QUESTIONS.keys())

st.progress(st.session_state.step/5)

if st.session_state.step<5:
    p=pillars[st.session_state.step]
    st.subheader(f"Pilar {st.session_state.step+1}/5")

    for qid,text,_ in QUESTIONS[p]:
        st.slider(text,1,5,3,key=qid)

    col1,col2=st.columns(2)
    if col1.button("Voltar") and st.session_state.step>0:
        st.session_state.step-=1
        st.rerun()

    if col2.button("Próximo"):
        st.session_state.step+=1
        st.rerun()

else:
    scores={}
    for p in QUESTIONS:
        vals=[]
        for qid,_,rev in QUESTIONS[p]:
            v=st.session_state[qid]
            if rev: v=6-v
            vals.append(v)
        scores[p]=round((sum(vals)-7)/28*100,1)

    st.session_state.scores=scores


if "scores" in st.session_state:
    
# =========================
# KPIs EXECUTIVOS
# =========================
st.markdown("### Executive Snapshot")

c1,c2,c3,c4,c5 = st.columns(5)
for col,(k,v) in zip([c1,c2,c3,c4,c5], s.items()):
    with col:
        st.markdown(f"""
        <div class="kpi">
        <b>{k}</b><br>
        <span style="font-size:20px">{v}</span>
        </div>
        """, unsafe_allow_html=True)

    name=st.text_input("Nome","Participante")

    # Radar
    fig = plt.figure(figsize=(5,5))
ax = plt.subplot(polar=True)
ax.plot(angles, values, linewidth=2, color="#1F4E79")
ax.fill(angles, values, alpha=0.25, color="#2E86C1")
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=9)
ax.set_yticks([20,40,60,80,100])
ax.set_title("Behavioral DNA", fontsize=13, pad=18)
st.pyplot(fig)


    # MATRIZ EXECUTIVA (proxy MCA)
    fig2,ax2 = plt.subplots(figsize=(5,5))
ax2.axhline(50,ls="--",lw=1,color="#C0C7D1")
ax2.axvline(50,ls="--",lw=1,color="#C0C7D1")
ax2.scatter(x,y,s=160,color="#1F4E79")

ax2.set_xlim(0,100)
ax2.set_ylim(0,100)
ax2.set_title("Executive Positioning Matrix", fontsize=12)

ax2.text(75,85,"Strategic Driver",ha="center",fontsize=8)
ax2.text(25,85,"Operational Leader",ha="center",fontsize=8)
ax2.text(25,15,"Stability Core",ha="center",fontsize=8)
ax2.text(75,15,"Adaptive Explorer",ha="center",fontsize=8)

st.pyplot(fig2)


    quadrant=("Q1","Q2","Q3","Q4")[(x<50)*2+(y<50)]

def level(v):
    if v>=70: return "high"
    if v>=40: return "balanced"
    return "developing"

st.markdown("### Executive Behavioral Interpretation")

st.markdown(f"""
**{name}** demonstrates a **{level(s['C'])} execution profile**,  
combined with **{level(s['O'])} cognitive openness** and  
**{level(s['E'])} external orientation**.

From an emotional standpoint, the stability index is **{100-s['N']}**,  
indicating a tendency toward **{'resilience' if s['N']<40 else 'moderate reactivity' if s['N']<70 else 'high sensitivity'}**.

Overall, this configuration suggests a **{ptype} behavioral archetype**,  
typically associated with **{pdesc.lower()}**.
""")

st.markdown("### Population Benchmark")

for k,v in s.items():
    bar_color = "#1F4E79" if v>=50 else "#AAB7C4"
    st.progress(v/100, text=f"{k} — {percentile(v)} ({v})")



def gerar_pdf_premium(name,s,analysis):

    buffer=io.BytesIO()
    c=canvas.Canvas(buffer,pagesize=A4)
    w,h=A4

    primary=colors.HexColor("#1F4E79")

    # Capa
    c.setFillColor(primary)
    c.setFont("Helvetica-Bold",20)
    c.drawCentredString(w/2,h-3*cm,"Executive Personality Report")
    c.setFont("Helvetica",12)
    c.drawCentredString(w/2,h-4*cm,name)

    # Scores
    y=h-6*cm
    for k,v in s.items():
        c.drawString(2*cm,y,f"{k}: {v}")
        y-=0.7*cm

    c.showPage()

    # IA
    text=c.beginText(2*cm,h-3*cm)
    for line in analysis.split("\n"):
        text.textLine(line)
    c.drawText(text)

    c.save()
    buffer.seek(0)
    return buffer

if "analysis" in st.session_state:
    pdf=gerar_pdf_premium(name,s,st.session_state.analysis)
    st.download_button("Download Premium Report (PDF)",pdf,file_name="executive_profile.pdf")
Fti

