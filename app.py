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
# -----------------------------------------------------
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

