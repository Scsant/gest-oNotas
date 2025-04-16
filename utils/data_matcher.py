# utils/data_matcher.py
import pandas as pd

def cruzar_emissao_com_chegada(df_emissao, df_chegada):
    # Normaliza os nomes de colunas
    df_chegada.columns = df_chegada.columns.str.strip()
    df_emissao.columns = df_emissao.columns.str.strip()

    # Busca coluna de Nota Fiscal ignorando case e espaços
    colunas_normalizadas = {col.strip().lower(): col for col in df_chegada.columns}
    nota_col_chegada = colunas_normalizadas.get("nota fiscal")

    if not nota_col_chegada:
        cols_disponiveis = list(df_chegada.columns)
        raise ValueError(f"❌ Coluna 'Nota Fiscal' não encontrada na planilha de chegada! Colunas disponíveis: {cols_disponiveis}")

    # Padroniza as colunas de nota para string limpa, sem ponto decimal
    df_emissao["NF EMITIDA"] = df_emissao["NF EMITIDA"].astype(str).str.strip().str.split('.').str[0]
    df_chegada[nota_col_chegada] = (
        df_chegada[nota_col_chegada]
        .dropna()
        .astype(str)
        .str.strip()
        .str.split('.')
        .str[0]
    )

    # Remove viagens sem NF (SP)
    df_chegada = df_chegada[df_chegada[nota_col_chegada].notna()]
    df_chegada = df_chegada[df_chegada[nota_col_chegada].astype(str).str.strip().str.isnumeric()]

    # Merge
    df_merged = df_emissao.merge(
        df_chegada[[nota_col_chegada, "DATA CHEGADA BALANÇA"]],
        left_on="NF EMITIDA", right_on=nota_col_chegada,
        how="left"
    )

    df_merged["LOCALIZADA"] = df_merged["DATA CHEGADA BALANÇA"].notna()

    # Tempo de trânsito
    df_merged["DATA EMISSÃO NF"] = pd.to_datetime(df_merged["DATA EMISSÃO NF"], errors="coerce")
    df_merged["DATA CHEGADA BALANÇA"] = pd.to_datetime(df_merged["DATA CHEGADA BALANÇA"], errors="coerce")
    df_merged["TEMPO TRANSITO"] = (df_merged["DATA CHEGADA BALANÇA"] - df_merged["DATA EMISSÃO NF"]).dt.days

    return df_merged
