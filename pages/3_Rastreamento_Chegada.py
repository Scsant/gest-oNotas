# pages/3_Rastreamento_Chegada.py
import streamlit as st
import pandas as pd
import io
from pandas import ExcelWriter
from utils.data_loader import load_excel
from utils.data_matcher import cruzar_emissao_com_chegada
from utils.charts import plot_tempo_transito, plot_chegadas_por_dia, plot_eficiencia_transportadora

st.header("📍 Rastreamento de Chegada na Fábrica")

st.markdown("""
Esta página permite cruzar os dados de **emissão de notas fiscais** com a **chegada dos caminhões na balança da fábrica**, possibilitando:
- Verificar quais NFs foram localizadas
- Calcular o tempo de trânsito (emissão → chegada)
- Identificar pendências e atrasos
""")

col1, col2 = st.columns(2)
with col1:
    uploaded_emissao = st.file_uploader("📁 Envie a planilha de EMISSÃO de NFs", type=["xlsx"])
with col2:
    uploaded_chegada = st.file_uploader("📥 Envie a planilha de CHEGADAS (balança)", type=["xlsx"])

if uploaded_emissao and uploaded_chegada:
    df_emissao = load_excel(uploaded_emissao)
    df_chegada = load_excel(uploaded_chegada)

    # Normaliza colunas e verifica presença da coluna crítica
    df_emissao.columns = df_emissao.columns.str.strip().str.upper()
    st.write("📋 Colunas da planilha de emissão:", df_emissao.columns.tolist())

    if "DATA EMISSÃO NF" not in df_emissao.columns:
        st.error("❌ Coluna 'DATA EMISSÃO NF' não encontrada na planilha de emissão!")
        st.stop()

    df_emissao["DATA EMISSÃO NF"] = pd.to_datetime(df_emissao["DATA EMISSÃO NF"], errors="coerce")

    # Filtro de data
    st.markdown("### 📅 Filtrar por Data de Emissão")
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Inicial", value=df_emissao["DATA EMISSÃO NF"].min().date())
    with col2:
        data_fim = st.date_input("Data Final", value=df_emissao["DATA EMISSÃO NF"].max().date())

    df_emissao = df_emissao[
        (df_emissao["DATA EMISSÃO NF"] >= pd.to_datetime(data_inicio)) &
        (df_emissao["DATA EMISSÃO NF"] <= pd.to_datetime(data_fim))
    ]

    # Filtros adicionais: ORDEM DE BUSCA e OBS
    st.markdown("### 🔍 Filtros de Validação")
    aplicar_filtros = st.checkbox("Aplicar filtros para excluir notas canceladas, complementares ou já localizadas")

    if aplicar_filtros:
        df_emissao = df_emissao[
            (df_emissao["ORDEM DE BUSCA"].isna()) &
            (df_emissao["OBS"].isna())
        ]

    try:
        df_merged = cruzar_emissao_com_chegada(df_emissao, df_chegada)
    except ValueError as e:
        st.error(str(e))
        st.stop()

    st.success("✅ Dados carregados e cruzados com sucesso!")

    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Notas Emitidas", len(df_emissao))
        with col2:
            st.metric("✅ Chegadas Localizadas", df_merged["LOCALIZADA"].sum())
        with col3:
            st.metric("🚫 Pendentes", len(df_merged) - df_merged["LOCALIZADA"].sum())
        with col4:
            st.metric("🔎 NFs válidas na balança", df_chegada.shape[0])

    st.write("### ⏱️ Tempo de Trânsito (dias entre emissão e chegada)")
    st.plotly_chart(plot_tempo_transito(df_merged), use_container_width=True)

    st.write("### 📈 Chegadas por Dia")
    st.plotly_chart(plot_chegadas_por_dia(df_merged), use_container_width=True)

    st.write("### 🥇 Eficiência por Transportadora")
    st.plotly_chart(plot_eficiencia_transportadora(df_merged), use_container_width=True)

    st.markdown("### 📤 Exportar NFs Pendentes (Não Localizadas na Fábrica)")
    df_pendentes = df_merged[~df_merged["LOCALIZADA"]].copy()

    colunas_exportar = ["NF EMITIDA", "DATA EMISSÃO NF", "TRANSP. ATUAL", "FAZENDA"]
    colunas_existentes = [col for col in colunas_exportar if col in df_pendentes.columns]

    df_export = df_pendentes[colunas_existentes]
    df_export["STATUS"] = "Não localizada na balança"

    st.dataframe(df_export)

    # Geração do Excel na mão aqui, removendo a importação anterior
    output = io.BytesIO()
    with ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name="Pendentes")
    output.seek(0)

    st.download_button(
        label="⬇️ Baixar Pendentes (.xlsx)",
        data=output,
        file_name="notas_pendentes_corrientes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
