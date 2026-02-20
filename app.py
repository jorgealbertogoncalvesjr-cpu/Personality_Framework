import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Executive Personality Engine", layout="centered")

# ────────────────────────────────────────────────
#  DEFINIÇÕES FIXAS – colocar no topo!
# ────────────────────────────────────────────────

QUESTIONS = {
    "O": [("o1", "Tenho imaginação rica", False), ("o2", "Gosto de ideias abstratas", False),
          ("o3", "Interesse por arte", False), ("o4", "Prefiro rotina", True),
          ("o5", "Sou curioso", False), ("o6", "Evito filosofia", True), ("o7", "Penso no futuro", False)],

    "C": [("c1", "Sou organizado", False), ("c2", "Planejo antes", False),
          ("c3", "Cumpro prazos", False), ("c4", "Deixo tarefas", True),
          ("c5", "Sou disciplinado", False), ("c6", "Procrastino", True), ("c7", "Sou responsável", False)],

    "E": [("e1", "Gosto de socializar", False), ("e2", "Inicio conversas", False),
          ("e3", "Sou expressivo", False), ("e4", "Prefiro silêncio", True),
          ("e5", "Confortável em grupos", False), ("e6", "Evito atenção", True), ("e7", "Sou entusiasmado", False)],

    "A": [("a1", "Sou empático", False), ("a2", "Confio nas pessoas", False),
          ("a3", "Evito conflitos", False), ("a4", "Sou crítico", True),
          ("a5", "Gosto de ajudar", False), ("a6", "Sou duro", True), ("a7", "Valorizo cooperação", False)],

    "N": [("n1", "Preocupo-me fácil", False), ("n2", "Fico ansioso", False),
          ("n3", "Mudo humor", False), ("n4", "Sou calmo", True),
          ("n5", "Sinto tensão", False), ("n6", "Raramente estressado", True), ("n7", "Reajo forte", False)]
}

pillars = list(QUESTIONS.keys())
TOTAL_STEPS = len(pillars)          # 5

PASSWORD = "1618"

# ────────────────────────────────────────────────
#  SESSION STATE INICIALIZAÇÃO
# ────────────────────────────────────────────────

if "step" not in st.session_state:
    st.session_state.step = 0

if "scores" not in st.session_state:
    st.session_state.scores = None

if "saved" not in st.session_state:
    st.session_state.saved = False

if "auth" not in st.session_state:
    st.session_state.auth = False

# ────────────────────────────────────────────────
#  AUTENTICAÇÃO
# ────────────────────────────────────────────────

if not st.session_state.auth:
    st.title("Executive Personality Assessment")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if senha == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Senha incorreta")
    st.stop()

# ────────────────────────────────────────────────
# GOOGLE SHEETS – conexão única + minimização de leituras
# ────────────────────────────────────────────────

sheet = None
google_ok = False

try:
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(st.secrets["gsheets"]["spreadsheet"]).sheet1
    google_ok = True
    st.sidebar.success("Google Sheets conectado")
except Exception as e:
    st.sidebar.error("Google Sheets OFF")
    st.sidebar.code(str(e))


# Inicializa o DataFrame populacional no session_state (carrega só UMA VEZ por sessão)
if "pop_df" not in st.session_state:
    st.session_state.pop_df = None
    st.session_state.population_load_attempted = False


# Função de carregamento com retry leve – executada APENAS se ainda não tentou
def try_load_population():
    if not google_ok or sheet is None:
        return pd.DataFrame()

    if st.session_state.population_load_attempted:
        return st.session_state.pop_df

    with st.spinner("Carregando dados populacionais (executado apenas uma vez por sessão)..."):
        for attempt in range(3):
            try:
                df = pd.DataFrame(sheet.get_all_records())
                for c in ["O", "C", "E", "A", "N"]:
                    if c in df.columns:
                        df[c] = pd.to_numeric(df[c], errors="coerce")
                st.session_state.pop_df = df
                st.session_state.population_load_attempted = True
                st.success("Dados populacionais carregados com sucesso.")
                return df

            except Exception as e:
                error_str = str(e).lower()
                if "quota" in error_str or "429" in error_str or "rate limit" in error_str:
                    wait = 20 * (attempt + 1)  # 20s → 40s → 60s
                    st.warning(f"Limite de quota atingido. Tentando novamente em {wait} segundos... (tentativa {attempt+1}/3)")
                    time.sleep(wait)
                else:
                    st.error(f"Erro ao carregar população: {e}")
                    break

        # Se falhar todas as tentativas
        st.session_state.population_load_attempted = True
        st.session_state.pop_df = pd.DataFrame()
        st.warning("Não foi possível carregar os dados populacionais (limite de API). Comparações desabilitadas.")
        return pd.DataFrame()


# Função auxiliar para obter os dados (nunca faz nova leitura se já carregou ou tentou)
@st.cache_data(ttl=3600, show_spinner=False)  # cache extra de segurança, mas principal controle é session_state
def get_population_data():
    if st.session_state.pop_df is None and not st.session_state.population_load_attempted:
        return try_load_population()
    return st.session_state.pop_df


# ────────────────────────────────────────────────
# SALVAMENTO – com retry maior e controle de duplicatas
# ────────────────────────────────────────────────

def save_result(name, s):
    if not google_ok or sheet is None:
        st.info("Salvamento desabilitado: conexão com Google Sheets não disponível.")
        return

    if st.session_state.get("result_saved", False):
        return  # evita salvar múltiplas vezes no mesmo rerun

    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name.strip() if name else "Anônimo",
        float(s.get("O", 0)),
        float(s.get("C", 0)),
        float(s.get("E", 0)),
        float(s.get("A", 0)),
        float(s.get("N", 0))
    ]

    for attempt in range(4):
        try:
            sheet.append_row(row)
            st.session_state.result_saved = True
            st.success("Resultado salvo com sucesso no Google Sheets!")
            return
        except Exception as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                wait = 15 * (attempt + 1)   # 15s, 30s, 45s, 60s
                st.warning(f"Quota excedida ao salvar. Tentando novamente em {wait}s... ({attempt+1}/4)")
                time.sleep(wait)
            else:
                st.error(f"Erro ao salvar resultado: {e}")
                break
    else:
        st.error("Não foi possível salvar o resultado após várias tentativas (limite de API).")

# ────────────────────────────────────────────────
#  QUESTIONÁRIO
# ────────────────────────────────────────────────

st.progress(st.session_state.step / TOTAL_STEPS)

if st.session_state.step < TOTAL_STEPS:

    p = pillars[st.session_state.step]
    st.subheader(f"Pilar {p}")

    for qid, text, _ in QUESTIONS[p]:
        # value= st.session_state.get(qid, 3)  → mantém valor anterior ou default
        st.slider(
            label=text,
            min_value=1,
            max_value=5,
            value=st.session_state.get(qid, 3),
            key=qid
        )

    c1, c2 = st.columns(2)

    if c1.button("⬅ Voltar") and st.session_state.step > 0:
        st.session_state.step -= 1
        st.rerun()

    if c2.button("Próximo ➡"):
        st.session_state.step += 1
        st.rerun()

# ────────────────────────────────────────────────
#  CÁLCULO DE SCORES (só quando terminou todas as perguntas)
# ────────────────────────────────────────────────

if st.session_state.step == TOTAL_STEPS and st.session_state.scores is None:

    scores = {}
    for p in pillars:
        values = []
        inverted = []
        for qid, _, invert in QUESTIONS[p]:
            val = st.session_state.get(qid, 3)
            if invert:
                inverted.append(val)
            else:
                values.append(val)
        
        # Média normal + média invertida (convertida)
        normal_mean = np.mean(values) if values else 3
        invert_mean = np.mean([6 - v for v in inverted]) if inverted else 3
        scores[p] = (normal_mean + invert_mean) / 2 * 20   # escala para ~0–100

    st.session_state.scores = scores

# ────────────────────────────────────────────────
#  TELA FINAL – RESULTADOS
# ────────────────────────────────────────────────

if st.session_state.step == TOTAL_STEPS:

    if st.session_state.scores is None:
        st.error("Erro interno: scores não calculados.")
        st.stop()

    s = st.session_state.scores
    name = st.text_input("Nome", "Participante")

    # Salva apenas uma vez
    if not st.session_state.saved and sum(s.values()) > 10:  # evita salvar zeros/nulos
        save_result(name, s)
        st.session_state.saved = True
        st.success("Resultado salvo!")

    st.header("Executive Profile")

    cols = st.columns(5)
    for i, k in enumerate(["O", "C", "E", "A", "N"]):
        val = s[k] if k != "N" else 100 - s[k]
        cols[i].metric(k, round(val, 1))

    # Matriz estratégica
    x = (s["O"] + s["E"]) / 2
    y = (s["C"] + (100 - s["N"])) / 2

    st.subheader("Matriz Estratégica")
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axhline(50, linestyle="--", color="gray")
    ax.axvline(50, linestyle="--", color="gray")
    ax.scatter(x, y, s=200, color="teal")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Visão & Influência")
    ax.set_ylabel("Execução & Consistência")
    st.pyplot(fig)

    # Radar
    st.subheader("Radar Comportamental")
    labels = ["O", "C", "E", "A", "N (inv)"]
    vals = [s["O"], s["C"], s["E"], s["A"], 100 - s["N"]]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    vals += vals[:1]
    angles += angles[:1]

    fig2, ax2 = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax2.plot(angles, vals, linewidth=2)
    ax2.fill(angles, vals, alpha=0.15)
    ax2.set_ylim(0, 100)
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(labels)
    st.pyplot(fig2)
