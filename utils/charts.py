import plotly.express as px
import pandas as pd

def plot_emissoes_por_dia(df):
    df_grouped = df.groupby("DATA EMISSÃO NF").size().reset_index(name="Quantidade")

    fig = px.line(df_grouped,
                  x="DATA EMISSÃO NF",
                  y="Quantidade",
                  title="📅 Emissões por Dia",
                  markers=True)

    fig.update_layout(xaxis_title="Data", yaxis_title="Quantidade de Notas", hovermode="x unified")
    return fig


def plot_por_transportadora(df):
    df_grouped = df["TRANSP. ATUAL"].value_counts().nlargest(10).reset_index()
    df_grouped.columns = ["Transportadora", "Quantidade"]

    apelidos = {
        "CARGO POLO COMERCIO, LOGISTICA E TRANSPORTE": "Cargo Polo",
        "EXPRESSO NEPOMUCENO SA": "Nepomuceno",
        "JSL SA": "JSL",
        "EUCLIDES R GARBUIO TRANSPORTES LTDA": "Garbuio",
        "VDA LOGISTICA LTDA": "VDA",
        "EXPRESSO OLSEN TRANSP ROD CARGAS LT": "Olsen",
        "PLACIDOS TRANSP RODOVIARIO LTDA": "Placidos",
        "EXPRESSO NEPOMUCENO S/A": "Nepomuceno",
        "BRACELL SP CELULOSE LTDA": "Bracell",
        "              BRACELL SP CELULOSE LTDA": "Bracell",
        "EXPRESSO OLSEN TRANSPORTES RODOVIÁRIOS DE CARGAS LTDA": "Olsen",
        "                                                                BRACELL SP CELULOSE LTDA                                                                   ": "Bracell",

        "SERRANALOG TRANSPORTES LTDA": "Serrana"
    }

    # Aplica apelidos onde possível
    df_grouped["Transportadora"] = df_grouped["Transportadora"].apply(
        lambda x: apelidos.get(x, x)
    )

    fig = px.bar(df_grouped,
                 x="Transportadora",
                 y="Quantidade",
                 title="🚛 Transportadoras por Emissão",
                 text="Quantidade")

    fig.update_layout(yaxis_title="Quantidade de Notas")
    
    return fig



# ... (as outras funções já existentes continuam)

def plot_obs_status(df):
    df_obs = df.copy()
    df_obs["OBS_CAT"] = df_obs["OBS"].fillna("VÁLIDA").str.upper()

    def categorizar(obs):
        if "CANCELADA" in obs:
            return "Cancelada"
        elif "CANCELAR" in obs:
            return "Enviada p/ Cancelar"
        elif "VINCULADA" in obs:
            return "Vinculada"
        elif obs == "VÁLIDA":
            return "Emitida"
        else:
            return "Outros"

    df_obs["Status"] = df_obs["OBS_CAT"].apply(categorizar)

    resumo = df_obs["Status"].value_counts().reset_index()
    resumo.columns = ["Status", "Quantidade"]

    cores = {
        "Emitida": "#1f77b4",           # Azul
        "Cancelada": "#d62728",         # Vermelho
        "Enviada p/ Cancelar": "#ff7f0e", # Laranja
        "Vinculada": "#2ca02c",         # Verde
        "Outros": "#7f7f7f"             # Cinza
    }

    pull_map = {
        "Cancelada": 0.1,
        "Emitida": 0,
        "Enviada p/ Cancelar": 0,
        "Vinculada": 0,
        "Outros": 0
    }

    fig = px.pie(resumo,
                 names="Status",
                 values="Quantidade",
                 
                 color="Status",
                 color_discrete_map=cores,
                 hole=0.4)

    fig.update_traces(
        textinfo="percent+label",
        pull=[pull_map.get(s, 0) for s in resumo["Status"]]
    )

    return fig



def plot_valor_m3_brl(df):
    df_agg = df.groupby("TRANSP. ATUAL")[["M3", "BRL"]].sum().reset_index().sort_values("BRL", ascending=False).head(10)

    # Dicionário de apelidos
    apelidos = {
        "CARGO POLO COMERCIO, LOGISTICA E TRANSPORTE": "Cargo Polo",
        "EXPRESSO NEPOMUCENO SA": "Nepomuceno",
        "JSL SA": "JSL",
        "EUCLIDES R GARBUIO TRANSPORTES LTDA": "Garbuio",
        "VDA LOGISTICA LTDA": "VDA",
        "EXPRESSO OLSEN TRANSP ROD CARGAS LT": "Olsen",
        "PLACIDOS TRANSP RODOVIARIO LTDA": "Placidos",
        "EXPRESSO NEPOMUCENO S/A": "Nepomuceno",
        "BRACELL SP CELULOSE LTDA": "Bracell",
        "              BRACELL SP CELULOSE LTDA": "Bracell",
        "EXPRESSO OLSEN TRANSPORTES RODOVIÁRIOS DE CARGAS LTDA": "Olsen",
        "                                                                BRACELL SP CELULOSE LTDA                                                                   ": "Bracell",

        "SERRANALOG TRANSPORTES LTDA": "Serrana"
    }

    # Aplica os apelidos
    df_agg["TRANSP. ATUAL"] = df_agg["TRANSP. ATUAL"].apply(lambda x: apelidos.get(x, x))

    fig = px.bar(df_agg,
                 x="TRANSP. ATUAL",
                 y=["BRL", "M3"],
                 barmode="group",
                 title="💰 Valor (BRL) e Volume (M3) por Transportadora")

    fig.update_layout(
        xaxis_title="Transportadora",
        yaxis_title="Total",
        yaxis_tickformat=",.0f"
    )

    return fig




def plot_tempo_transito(df):
    df_plot = df[df["LOCALIZADA"] & df["TEMPO TRANSITO"].notna()]
    fig = px.histogram(df_plot, x="TEMPO TRANSITO", nbins=15,
                       title="⏱️ Distribuição do Tempo de Trânsito (dias)")
    return fig

def plot_chegadas_por_dia(df):
    df_plot = df[df["LOCALIZADA"]].copy()
    df_plot["DATA CHEGADA BALANÇA"] = pd.to_datetime(df_plot["DATA CHEGADA BALANÇA"])
    df_count = df_plot.groupby("DATA CHEGADA BALANÇA").size().reset_index(name="Quantidade")
    fig = px.line(df_count, x="DATA CHEGADA BALANÇA", y="Quantidade",
                  title="📈 Chegadas por Dia", markers=True)
    return fig

def plot_eficiencia_transportadora(df):
    df_plot = df[df["LOCALIZADA"] & df["TEMPO TRANSITO"].notna()].copy()
    df_grouped = df_plot.groupby("TRANSP. ATUAL")["TEMPO TRANSITO"].mean().reset_index()
    df_grouped = df_grouped.sort_values("TEMPO TRANSITO")
    fig = px.bar(df_grouped, x="TRANSP. ATUAL", y="TEMPO TRANSITO",
                 title="🥇 Média de Tempo de Trânsito por Transportadora")
    return fig
