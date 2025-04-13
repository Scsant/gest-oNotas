import streamlit as st
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="NF Dashboard",
    page_icon="🌲",
    layout="wide"
)

# Criar pastas padrão se não existirem
for folder in ["data", "outputs"]:
    Path(folder).mkdir(exist_ok=True)

# Título principal
st.markdown("""
# 🌲 DATASCIENCE LOGÍSTICA FLORESTAL
### Sistema Inteligente de Gestão de Notas Fiscais e Performance de Transportadoras
""")

# Separador visual
st.markdown("---")

# Destaques rápidos
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Status do Sistema", value="Online ✅")
with col2:
    st.metric(label="Data de Hoje", value=date.today().strftime("%d/%m/%Y"))
with col3:
    st.metric(label="Versão", value="v1.0.0")

st.markdown("""
Este sistema foi criado para oferecer uma **visão estratégica e preditiva** sobre a movimentação de cargas no setor florestal, com foco em:

- 📦 Emissão e rastreio de Notas Fiscais
- 🚛 Performance por transportadora
- 📉 Monitoramento de atrasos e cancelamentos
- 📊 Análises dinâmicas e geração de relatórios

> Acesse as abas laterais para começar!
""")
