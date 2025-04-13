import pandas as pd

def filtrar_notas_pendentes(df, data_limite):
    df = df.copy()
    
    df["DATA EMISSÃO NF"] = pd.to_datetime(df["DATA EMISSÃO NF"], errors="coerce")
    df = df[df["DATA EMISSÃO NF"].dt.year == 2025]
    

    df = df[df["DATA EMISSÃO NF"] <= pd.Timestamp(data_limite)]
    

    # Aqui está o ajuste definitivo: pegar onde ORDEM DE BUSCA está vazia
    df = df[df["ORDEM DE BUSCA"].isna()]
    

    df = df[df["OBS"].isna() | (df["OBS"].astype(str).str.strip() == "")]
    

    return df
