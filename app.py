# =====================================================
# APP — PERSONALITY PROFILE (BIG FIVE / IPIP)
# Landing + Login + Base
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

# -----------------------------------------------------
# LOGIN SIMPLES
# -----------------------------------------------------
PASSWORD = "1618"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    st.title("🧠 Descubra Seu DNA Comportamental")

    st.markdown("""
### Você se conhece de verdade?

Com base no modelo científico **Big Five (OCEAN)**, este teste revela:

- Como você pensa  
- Como você age sob pressão  
- Como você se relaciona  
- Seus pontos fortes naturais  
- Seu estilo emocional  

⚡ Resultado visual + análise personalizada  
📊 Base científica internacional  
📄 Relatório exclusivo  

""")

    senha = st.text_input("Digite a senha de acesso", type="password")

    if st.button("Iniciar Avaliação"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")

    st.caption("""
Base científica: International Personality Item Pool (IPIP)  
Modelo Big Five – Goldberg (1992)  
Este app gera interpretação algorítmica proprietária.
""")

    st.stop()

# -----------------------------------------------------
# LANDING APÓS LOGIN
# -----------------------------------------------------
st.title("🧠 Avaliação de Perfil Comportamental")

st.markdown("""
Você responderá **35 perguntas rápidas** (menos de 3 minutos).

Escala:
1 → Discordo totalmente  
2 → Discordo  
3 → Neutro  
4 → Concordo  
5 → Concordo totalmente  

Ao final você receberá:

- 📊 Seu gráfico comportamental
- 🧠 Interpretação do seu perfil
- 🎯 Pontos fortes naturais
- ⚠️ Pontos de atenção
- 📄 Relatório visual

Clique abaixo para iniciar.
""")

if st.button("Começar Teste"):
    st.session_state.start_test = True

# Guardar estado
if "start_test" not in st.session_state:
    st.session_state.start_test = False
