import pandas as pd

def load_excel(file):
    df = pd.read_excel(file, engine='openpyxl')

    # Corrige nomes de colunas (garante padronização)
    df.columns = df.columns.str.strip().str.upper()

    # Converte datas
    if "DATA EMISSÃO NF" in df.columns:
        df["DATA EMISSÃO NF"] = pd.to_datetime(df["DATA EMISSÃO NF"], errors='coerce')

    return df
