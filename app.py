# =====================================================
# DNA COMPORTAMENTAL — BIG FIVE (IPIP)
# Landing + Login + Front B2C
# =====================================================

import streamlit as st

# -----------------------------------------------------
# CONFIGURAÇÃO
# -----------------------------------------------------
st.set_page_config(
    page_title="DNA Comportamental",
    page_icon="🧠",
    layout="centered"
)

PASSWORD = "1618"

# -----------------------------------------------------
# ESTILO VISUAL (B2C)
# -----------------------------------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

h1, h2, h3 {
    text-align: center;
}

.big-card {
    background-color: #f5f7fa;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 20px;
}

.cta-button button {
    background-color: #1f77b4;
    color: white;
    font-size: 18px;
    padding: 0.6rem 1.2rem;
    border-radius: 10px;
    width: 100%;
}

.small-text {
    font-size: 13px;
    color: #6c757d;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# LOGIN
# -----------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.markdown("## 🧠 Descubra Seu Perfil Psicológico")

    st.markdown("""
<div class="big-card">

### Você realmente se conhece?

Este teste analisa **5 pilares da sua personalidade** usando base científica internacional:

- 🔎 Como você pensa  
- ⚡ Como você reage sob pressão  
- 🤝 Como você se relaciona  
- 🎯 Seus talentos naturais  
- 🧠 Seu padrão emocional  

</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="big-card">

### O que você recebe ao final:

📊 Gráfico comportamental completo  
🧠 Análise personalizada do seu perfil  
🎯 Pontos fortes naturais  
⚠️ Pontos de atenção  
📄 Relatório visual  

Tempo médio: **3 minutos**

</div>
""", unsafe_allow_html=True)

    senha = st.text_input("Digite a senha de acesso", type="password")

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("Iniciar Avaliação"):
            if senha == PASSWORD:
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Senha incorreta")

    st.markdown("""
<div class="small-text">

Base científica:  
International Personality Item Pool (IPIP)  
Modelo Big Five – Goldberg (1992)  

Este teste utiliza estrutura científica aberta.  
A interpretação é processada por algoritmo proprietário.

</div>
""", unsafe_allow_html=True)

    st.stop()

# -----------------------------------------------------
# LANDING PÓS LOGIN
# ----------------------------------------------------
st.markdown("## 🧠 Avaliação de Perfil Comportamental")

st.markdown("""
<div class="big-card">

Você responderá **35 perguntas rápidas**.

Escala de resposta:

1 → Discordo totalmente  
2 → Discordo  
3 → Neutro  
4 → Concordo  
5 → Concordo totalmente  

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="big-card">

Ao final você receberá:

📊 Seu gráfico comportamental  
🧠 Interpretação do seu perfil  
🎯 Pontos fortes  
⚠️ Pontos de atenção  
📄 Relatório visual  

</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    if st.button("Começar Teste"):
        st.session_state.start_test = True

if "start_test" not in st.session_state:
    st.session_state.start_test = False

# =====================================================
# PARTE 2 — QUESTIONÁRIO BIG FIVE (IPIP-STYLE)
# 35 itens | 5 etapas | Likert | Reverse-coded
# =====================================================

if st.session_state.start_test:

    st.divider()
    st.markdown("### 🧠 Questionário de Personalidade")

    # -------------------------------
    # Escala Likert
    # -------------------------------
    likert_labels = {
        1: "Discordo totalmente",
        2: "Discordo",
        3: "Neutro",
        4: "Concordo",
        5: "Concordo totalmente"
    }

    def likert_question(q_id, text):
        val = st.radio(
            text,
            options=[1,2,3,4,5],
            format_func=lambda x: f"{x} — {likert_labels[x]}",
            horizontal=False,
            key=q_id
        )
        return val

    # -------------------------------
    # Banco de Perguntas (IPIP-style)
    # r=True → item invertido
    # -------------------------------
    QUESTIONS = {
        "O": [  # Openness (Abertura)
            ("o1", "Tenho imaginação vívida e rica.", False),
            ("o2", "Gosto de explorar ideias abstratas.", False),
            ("o3", "Tenho interesse por arte e estética.", False),
            ("o4", "Prefiro rotinas previsíveis.", True),
            ("o5", "Sinto curiosidade por diferentes culturas.", False),
            ("o6", "Evito discussões filosóficas.", True),
            ("o7", "Gosto de pensar sobre possibilidades futuras.", False),
        ],
        "C": [  # Conscientiousness (Conscienciosidade)
            ("c1", "Sou organizado e metódico.", False),
            ("c2", "Planejo antes de agir.", False),
            ("c3", "Cumpro prazos rigorosamente.", False),
            ("c4", "Deixo tarefas inacabadas.", True),
            ("c5", "Sou disciplinado mesmo sem supervisão.", False),
            ("c6", "Procrastino com frequência.", True),
            ("c7", "Tenho senso forte de responsabilidade.", False),
        ],
        "E": [  # Extraversion (Extroversão)
            ("e1", "Sinto-me energizado ao interagir socialmente.", False),
            ("e2", "Inicio conversas com facilidade.", False),
            ("e3", "Sou expressivo emocionalmente.", False),
            ("e4", "Prefiro ambientes silenciosos.", True),
            ("e5", "Sinto-me confortável em grupos grandes.", False),
            ("e6", "Evito ser o centro das atenções.", True),
            ("e7", "Transmito entusiasmo naturalmente.", False),
        ],
        "A": [  # Agreeableness (Amabilidade)
            ("a1", "Sou empático com os outros.", False),
            ("a2", "Confio nas pessoas.", False),
            ("a3", "Evito conflitos sempre que possível.", False),
            ("a4", "Sou crítico com facilidade.", True),
            ("a5", "Gosto de ajudar espontaneamente.", False),
            ("a6", "Posso ser duro em julgamentos.", True),
            ("a7", "Valorizo cooperação acima da competição.", False),
        ],
        "N": [  # Neuroticism (Neuroticismo)
            ("n1", "Preocupo-me facilmente.", False),
            ("n2", "Fico ansioso sob pressão.", False),
            ("n3", "Tenho mudanças de humor frequentes.", False),
            ("n4", "Mantenho calma em situações difíceis.", True),
            ("n5", "Sinto tensão emocional com frequência.", False),
            ("n6", "Raramente me sinto estressado.", True),
            ("n7", "Reajo intensamente a problemas.", False),
        ],
    }

    PILLAR_NAMES = {
        "O": "Abertura (Openness)",
        "C": "Conscienciosidade (Conscientiousness)",
        "E": "Extroversão (Extraversion)",
        "A": "Amabilidade (Agreeableness)",
        "N": "Neuroticismo (Neuroticism)"
    }

    # -------------------------------
    # Estado de etapa
    # -------------------------------
    if "step" not in st.session_state:
        st.session_state.step = 0

    pillars = list(QUESTIONS.keys())
    total_steps = len(pillars)

    # Barra de progresso
    progress = st.session_state.step / total_steps
    st.progress(progress, text=f"Progresso: {st.session_state.step}/{total_steps}")

    # -------------------------------
    # Render da etapa atual
    # -------------------------------
    if st.session_state.step < total_steps:

        current_pillar = pillars[st.session_state.step]
        st.markdown(f"#### Pilar {st.session_state.step+1}/5 — {PILLAR_NAMES[current_pillar]}")

        with st.form(f"form_{current_pillar}"):

            for q_id, text, _ in QUESTIONS[current_pillar]:
                likert_question(q_id, text)

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("⬅ Voltar", disabled=st.session_state.step == 0):
                    st.session_state.step -= 1
                    st.rerun()

            with col2:
                if st.form_submit_button("Próximo ➡"):
                    st.session_state.step += 1
                    st.rerun()

    # -------------------------------
    # Cálculo dos Scores
    # -------------------------------
    else:
        st.success("✔ Questionário concluído")

        def reverse_score(x):
            return 6 - x  # Inversão Likert 1↔5

        scores_raw = {}
        scores_norm = {}

        for p in pillars:
            vals = []
            for q_id, _, is_rev in QUESTIONS[p]:
                v = st.session_state.get(q_id, 3)
                if is_rev:
                    v = reverse_score(v)
                vals.append(v)

            raw = sum(vals)               # 7 a 35
            norm = (raw - 7) / 28 * 100   # 0 a 100

            scores_raw[p] = raw
            scores_norm[p] = round(norm, 1)

        # Guardar para Parte 3
        st.session_state.scores = scores_norm

        st.markdown("### 📊 Pontuação Calculada")

        st.json({
            "Abertura": scores_norm["O"],
            "Conscienciosidade": scores_norm["C"],
            "Extroversão": scores_norm["E"],
            "Amabilidade": scores_norm["A"],
            "Neuroticismo": scores_norm["N"],
        })

        st.info("Na próxima etapa você verá seu gráfico comportamental e análise do perfil.")

# =====================================================
# PARTE 3 — RESULTADOS (Radar + Matriz + Interpretação)
# =====================================================

import numpy as np
import matplotlib.pyplot as plt

if "scores" in st.session_state:

    st.divider()
    st.markdown("## 📊 Seu Resultado")

    # -------------------------------------------------
    # Nome do usuário (personalização)
    # -------------------------------------------------
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    st.session_state.user_name = st.text_input(
        "Digite seu nome para personalizar o relatório",
        value=st.session_state.user_name,
        placeholder="Ex: Maria"
    )

    name = st.session_state.user_name.strip() or "Participante"

    scores = st.session_state.scores

    # -------------------------------------------------
    # 1) GRÁFICO RADAR — DNA COMPORTAMENTAL
    # -------------------------------------------------
    st.markdown("### 🧬 DNA Comportamental (Big Five)")

    categories = [
        "Abertura",
        "Conscienciosidade",
        "Extroversão",
        "Amabilidade",
        "Neuroticismo"
    ]
    values = [
        scores["O"],
        scores["C"],
        scores["E"],
        scores["A"],
        scores["N"]
    ]

    # Fechar o radar
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    values_cycle = values + values[:1]
    angles_cycle = angles + angles[:1]

    fig_radar = plt.figure(figsize=(6, 6))
    ax = plt.subplot(polar=True)
    ax.plot(angles_cycle, values_cycle, linewidth=2)
    ax.fill(angles_cycle, values_cycle, alpha=0.2)
    ax.set_xticks(angles)
    ax.set_xticklabels(categories)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(["20", "40", "60", "80", "100"])
    ax.set_title(f"Perfil de {name}", pad=20)
    st.pyplot(fig_radar)

    # -------------------------------------------------
    # 2) MATRIZ DE POSICIONAMENTO (QUADRANTE)
    # Eixos compostos (simples e explicáveis)
    # X = Orientação Externa  = Extroversão - Neuroticismo
    # Y = Organização/Execução = Conscienciosidade + Abertura
    # Normalização 0–100
    # -------------------------------------------------
    st.markdown("### 🧭 Matriz de Posicionamento")

    x_raw = scores["E"] - scores["N"]          # pode ir de -100 a 100
    y_raw = (scores["C"] + scores["O"]) / 2.0  # 0 a 100

    # Normalizar X para 0–100
    x_norm = (x_raw + 100) / 2.0
    y_norm = y_raw

    fig_mat, axm = plt.subplots(figsize=(6, 6))
    axm.axhline(50, linestyle="--", linewidth=1)
    axm.axvline(50, linestyle="--", linewidth=1)
    axm.scatter(x_norm, y_norm, s=120)
    axm.set_xlim(0, 100)
    axm.set_ylim(0, 100)
    axm.set_xlabel("Orientação Externa (Energia Social ↔ Estabilidade Emocional)")
    axm.set_ylabel("Organização & Abertura (Execução ↔ Exploração)")
    axm.set_title(f"Posicionamento de {name}")

    # Rótulos de quadrante
    axm.text(75, 85, "Alta Execução\nAlta Orientação Externa", ha="center")
    axm.text(25, 85, "Alta Execução\nBaixa Orientação Externa", ha="center")
    axm.text(75, 15, "Baixa Execução\nAlta Orientação Externa", ha="center")
    axm.text(25, 15, "Baixa Execução\nBaixa Orientação Externa", ha="center")

    st.pyplot(fig_mat)

    # Classificação simples do quadrante
    if x_norm >= 50 and y_norm >= 50:
        quadrant = "Q1 — Alta Execução / Alta Orientação Externa"
    elif x_norm < 50 and y_norm >= 50:
        quadrant = "Q2 — Alta Execução / Baixa Orientação Externa"
    elif x_norm < 50 and y_norm < 50:
        quadrant = "Q3 — Baixa Execução / Baixa Orientação Externa"
    else:
        quadrant = "Q4 — Baixa Execução / Alta Orientação Externa"

    st.info(f"Classificação na Matriz: **{quadrant}**")

    # -------------------------------------------------
    # 3) INTERPRETAÇÃO AUTOMÁTICA (nível psicológico)
    # -------------------------------------------------
    st.markdown("### 🧠 Interpretação do Perfil")

    def level(v):
        if v >= 70: return "alto"
        if v >= 40: return "moderado"
        return "baixo"

    interp = f"""
{name} apresenta:

- **Abertura:** nível {level(scores['O'])} — tendência a {'explorar ideias novas e complexas' if scores['O']>=70 else 'equilibrar prática e curiosidade' if scores['O']>=40 else 'preferir o concreto e familiar'}.
- **Conscienciosidade:** nível {level(scores['C'])} — {'forte organização e foco em metas' if scores['C']>=70 else 'disciplina situacional' if scores['C']>=40 else 'espontaneidade e flexibilidade'}.
- **Extroversão:** nível {level(scores['E'])} — {'energia social e assertividade' if scores['E']>=70 else 'equilíbrio entre social e introspectivo' if scores['E']>=40 else 'preferência por ambientes calmos'}.
- **Amabilidade:** nível {level(scores['A'])} — {'cooperação e empatia elevadas' if scores['A']>=70 else 'equilíbrio entre cooperação e objetividade' if scores['A']>=40 else 'postura mais direta e crítica'}.
- **Neuroticismo:** nível {level(scores['N'])} — {'maior reatividade emocional ao estresse' if scores['N']>=70 else 'resposta emocional moderada' if scores['N']>=40 else 'estabilidade emocional e resiliência'}.
"""
    st.markdown(interp)

# =====================================================
# PARTE 4 — GPT PERSONALITY ANALYSIS
# =====================================================

from openai import OpenAI

if "scores" in st.session_state:

    st.divider()
    st.markdown("## 🤖 Análise Psicológica Personalizada")

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    scores = st.session_state.scores
    name = st.session_state.get("user_name", "Participante")

    def build_prompt(name, scores):
        return f"""
Você é um psicólogo comportamental especializado no modelo Big Five.

Gere uma análise personalizada, clara e envolvente para o usuário abaixo.

Nome: {name}

Pontuações (0-100):
Abertura: {scores['O']}
Conscienciosidade: {scores['C']}
Extroversão: {scores['E']}
Amabilidade: {scores['A']}
Neuroticismo: {scores['N']}

Estrutura da resposta:

1. Resumo geral do perfil
2. Como essa pessoa pensa e toma decisões
3. Estilo emocional e reação ao estresse
4. Como se comporta socialmente
5. Pontos fortes naturais
6. Pontos de atenção
7. Sugestões práticas de desenvolvimento pessoal

Tom:
- Positivo e construtivo
- Profissional, porém acessível
- Evitar termos clínicos pesados
- Máx 400 palavras
"""

    # Botão para gerar (evita chamadas repetidas)
    if st.button("Gerar análise personalizada com IA"):

        with st.spinner("Gerando análise psicológica personalizada..."):

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Você é um especialista em psicologia comportamental."},
                        {"role": "user", "content": build_prompt(name, scores)}
                    ],
                    temperature=0.7,
                    max_tokens=700
                )

                analysis = response.choices[0].message.content
                st.session_state.gpt_analysis = analysis

            except Exception as e:
                st.error("Erro ao gerar análise com IA.")
                st.exception(e)

    # Mostrar se já gerado
    if "gpt_analysis" in st.session_state:
        st.markdown("### 🧠 Seu Perfil Interpretado pela IA")
        st.write(st.session_state.gpt_analysis)

        # Download TXT (pode virar PDF depois)
        st.download_button(
            "📄 Baixar análise personalizada",
            data=st.session_state.gpt_analysis.encode("utf-8"),
            file_name=f"Analise_Personalizada_{name}.txt",
            mime="text/plain"
        )





    
    # -------------------------------------------------
    # 4) PONTOS FORTES & ATENÇÃO
    # -------------------------------------------------
    st.markdown("### 🎯 Pontos Fortes Naturais")
    strengths = []
    if scores["C"] >= 70: strengths.append("Alta organização e confiabilidade")
    if scores["O"] >= 70: strengths.append("Criatividade e pensamento exploratório")
    if scores["E"] >= 70: strengths.append("Energia social e comunicação")
    if scores["A"] >= 70: strengths.append("Empatia e cooperação")
    if scores["N"] <= 30: strengths.append("Estabilidade emocional sob pressão")

    if strengths:
        for s in strengths:
            st.write(f"• {s}")
    else:
        st.write("• Perfil equilibrado, sem dominância extrema.")

    st.markdown("### ⚠️ Pontos de Atenção")
    risks = []
    if scores["C"] <= 35: risks.append("Possível dificuldade de consistência e execução")
    if scores["E"] <= 35: risks.append("Tendência ao isolamento em ambientes sociais")
    if scores["A"] <= 35: risks.append("Comunicação pode soar excessivamente direta")
    if scores["O"] <= 35: risks.append("Menor abertura a mudanças e novas ideias")
    if scores["N"] >= 70: risks.append("Maior sensibilidade ao estresse")

    if risks:
        for r in risks:
            st.write(f"• {r}")
    else:
        st.write("• Sem riscos comportamentais evidentes.")

    # -------------------------------------------------
    # 5) BASE PARA PDF (função simples)
    # -------------------------------------------------
    st.markdown("### 📄 Relatório")

    def build_text_report(name, scores, quadrant):
        return f"""
RELATÓRIO DE PERFIL — {name}

Pontuações (0–100):
Abertura: {scores['O']}
Conscienciosidade: {scores['C']}
Extroversão: {scores['E']}
Amabilidade: {scores['A']}
Neuroticismo: {scores['N']}

Matriz de Posicionamento:
{quadrant}

Este relatório é baseado no modelo Big Five (IPIP).
"""

    report_text = build_text_report(name, scores, quadrant)

    st.download_button(
        "📥 Baixar Relatório (TXT)",
        data=report_text.encode("utf-8"),
        file_name=f"Perfil_{name}.txt",
        mime="text/plain"
    )

    st.caption("""
Base científica: International Personality Item Pool (IPIP) — Goldberg (1992).
Este relatório é informativo e não substitui avaliação clínica.
""")


