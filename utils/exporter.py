import pandas as pd
from pathlib import Path

def exportar_por_transportadora(df, transportadora):
    nome = transportadora.replace(" ", "_").replace("/", "_")

    # Seleciona apenas as colunas necessárias
    colunas_desejadas = ["DATA EMISSÃO NF", "TRANSP. ATUAL", "NF EMITIDA"]
    df_limpo = df[colunas_desejadas].copy()

    # Adiciona a coluna extra para preenchimento
    df_limpo["SITUAÇÃO NF"] = ""

    file_path = Path("outputs") / f"{nome}_pendentes.xlsx"
    df_limpo.to_excel(file_path, index=False)
    return file_path
