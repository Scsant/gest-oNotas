import streamlit as st
import pandas as pd
from utils.data_loader import load_excel
from utils.filters import filtrar_notas_pendentes
from utils.exporter import exportar_por_transportadora
from datetime import date

st.header("📤 Notas Pendentes por Transportadora")

uploaded_file = st.file_uploader("📁 Envie a planilha (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)

    st.success("✅ Planilha carregada!")

    col1, col2 = st.columns(2)
    with col1:
        data_inicial = st.date_input("📅 Data inicial", value=date.today().replace(day=1))
    with col2:
        data_limite = st.date_input("📅 Data limite", value=date.today())



    df_filtrado = filtrar_notas_pendentes(df, data_limite)

    transportadoras = df_filtrado["TRANSP. ATUAL"].dropna().unique()
    transportadora_selecionada = st.selectbox("🚛 Selecione a transportadora", sorted(transportadoras))

    df_final = df_filtrado[df_filtrado["TRANSP. ATUAL"] == transportadora_selecionada]

    st.write(f"### 🔍 Resultado: {len(df_final)} notas pendentes")
    st.dataframe(df_final)

    if not df_final.empty:
        file_path = exportar_por_transportadora(df_final, transportadora_selecionada)
        with open(file_path, "rb") as f:
            st.download_button(
                label="📥 Baixar Excel da Transportadora",
                data=f,
                file_name=file_path.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
