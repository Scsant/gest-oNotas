# pages/4_Recomendacao_Emissao.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_excel

st.header("📊 Recomendação Diária de Emissão de NFs")

st.markdown("""
Essa análise calcula a **quantidade segura de notas fiscais a serem emitidas por dia**, considerando:
- A média de notas que chegam por dia na fábrica
- O prazo de validade da NF por estado:
  - MS: 6 dias
  - MG: 6 dias
  - PR: 5 dias

💡 Use isso para evitar cancelamentos por expiração de prazo!
""")

uploaded_file = st.file_uploader("📥 Envie a planilha de CHEGADAS (balança)", type=["xlsx"])

if uploaded_file:
    df = load_excel(uploaded_file)

    df.columns = df.columns.str.strip().str.upper()

    # Conversão e limpeza
    if "DATA CHEGADA BALANÇA" not in df.columns or "REGIÃO" not in df.columns:
        st.error("❌ A planilha precisa ter as colunas 'DATA CHEGADA BALANÇA' e 'REGIÃO'")
    else:
        df["DATA CHEGADA BALANÇA"] = pd.to_datetime(df["DATA CHEGADA BALANÇA"], errors="coerce")
        df = df.dropna(subset=["DATA CHEGADA BALANÇA", "REGIÃO"])

        # Mapeia REGIÃO → ESTADO
        def mapear_estado(regiao):
            if "MG" in regiao:
                return "MG"
            elif "PR" in regiao:
                return "PR"
            elif "MS" in regiao:
                return "MS"
            else:
                return "OUTROS"

        df["ESTADO"] = df["REGIÃO"].apply(mapear_estado)

        estados_disponiveis = df["ESTADO"].unique().tolist()
        estado = st.selectbox("📍 Escolha o estado de destino das NFs", options=sorted([e for e in estados_disponiveis if e != "OUTROS"]))

        dias_validade = {"MS": 6, "MG": 6, "PR": 5}
        validade = dias_validade.get(estado, 6)

        df_estado = df[df["ESTADO"] == estado].copy()
        df_estado["DIA"] = df_estado["DATA CHEGADA BALANÇA"].dt.date

        # Calcula a média móvel de 7 dias e usa a menor média como base para emissão segura
        df_daily = df_estado.groupby("DIA").size().reset_index(name="Chegadas")
        df_daily = df_daily.sort_values("DIA")
        df_daily["MediaMovel"] = df_daily["Chegadas"].rolling(window=7, min_periods=1).mean()
        media_base = df_daily["MediaMovel"].min()
        emissao_segura = media_base 

        st.metric("📦 Emissão diária segura para {}".format(estado), f"{emissao_segura:.0f} NFs")

        # Gráfico de chegadas por dia
        df_daily["Limite Seguro"] = emissao_segura

        fig = px.bar(df_daily, x="DIA", y="Chegadas", title=f"📈 Chegadas por Dia - {estado}", labels={"DIA": "Data", "Chegadas": "Qtd. Chegadas"})
        fig.add_scatter(x=df_daily["DIA"], y=df_daily["Limite Seguro"], mode="lines", name="Limite Seguro")
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"⚖️ Recomendamos emitir no máximo **{emissao_segura:.0f} NFs/dia** no estado {estado}, considerando {validade} dias de validade.")
