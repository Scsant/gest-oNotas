import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils.data_loader import load_excel
from utils.charts import (
    plot_emissoes_por_dia,
    plot_por_transportadora,
    plot_obs_status,
    plot_valor_m3_brl
)
from datetime import timedelta

st.header("📊 Panorama Geral das Notas Fiscais")

uploaded_file = st.file_uploader("📁 Envie a planilha de controle (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)

    # Lista real de transportadoras
    transportadoras_disponiveis = sorted(df["TRANSP. ATUAL"].dropna().unique().tolist())

    # Adiciona a opção "TODOS"
    transportadoras_opcoes = ["TODOS"] + transportadoras_disponiveis

    # Interface
    transportadoras_selecionadas = st.multiselect(
        "🚚 Selecione as transportadoras que deseja visualizar",
        options=transportadoras_opcoes,
        default=["TODOS"]
    )

    # Lógica de filtragem
    if "TODOS" not in transportadoras_selecionadas:
        df = df[df["TRANSP. ATUAL"].isin(transportadoras_selecionadas)]



    periodo = st.selectbox("📆 Período:", ["Últimos 7 dias", "Últimos 15 dias", "Últimos 30 dias", "Mês atual", "Todos"])

    hoje = pd.Timestamp.today()
    if periodo == "Últimos 7 dias":
        df = df[df["DATA EMISSÃO NF"] >= hoje - timedelta(days=7)]
    elif periodo == "Últimos 15 dias":
        df = df[df["DATA EMISSÃO NF"] >= hoje - timedelta(days=15)]
    elif periodo == "Últimos 30 dias":
        df = df[df["DATA EMISSÃO NF"] >= hoje - timedelta(days=30)]
    elif periodo == "Mês atual":
        df = df[df["DATA EMISSÃO NF"].dt.month == hoje.month]


    # Exibe informações principais
    st.subheader("📌 Informações Gerais")
    col1, col2, col3 = st.columns(3)

    data_inicial = df["DATA EMISSÃO NF"].min()
    data_final = df["DATA EMISSÃO NF"].max()

    with col1:
        st.metric("Data inicial", data_inicial.strftime("%d/%m/%Y") if pd.notnull(data_inicial) else "-")
    with col2:
        st.metric("Data final", data_final.strftime("%d/%m/%Y") if pd.notnull(data_final) else "-")
    with col3:
        st.metric("Fazenda", df["FAZENDA"].iloc[0])


    st.write("### 🚚 Transportadoras Atuais")
    st.write(df["TRANSP. ATUAL"].value_counts())

    st.write("### 📊 Total de Notas Emitidas")
    st.write(len(df["NF EMITIDA"].dropna()))

    st.write("### 🔍 Amostra dos Dados")
    st.dataframe(df.head(20))
    fig1 = plot_emissoes_por_dia(df)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = plot_por_transportadora(df)
    st.plotly_chart(fig2, use_container_width=True)

    st.write("### 🧾 Distribuição de Status das Notas")
    st.plotly_chart(plot_obs_status(df), use_container_width=True)



    st.write("### 💰 Valores e Volumes por Transportadora")
    st.plotly_chart(plot_valor_m3_brl(df), use_container_width=True)

