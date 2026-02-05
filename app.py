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
