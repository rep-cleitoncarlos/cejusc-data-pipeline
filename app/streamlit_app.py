from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# CONFIGURAÇÃO
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE = BASE_DIR / "data" / "cejusc.duckdb"

st.set_page_config(
    page_title="Indicadores de Conciliação — CEJUSC",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f8fafc;
    }

    .main .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #17365d;
    }

    .dashboard-header {
        margin-bottom: 1.5rem;
    }

    .dashboard-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #17365d;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0;
    }

    .filter-box {
        background: linear-gradient(
            135deg,
            #eef6ff 0%,
            #f8fbff 100%
        );

        border: 1px solid #dbeafe;
        border-radius: 14px;

        padding: 1rem 1.2rem 0.7rem 1.2rem;

        margin-bottom: 1.5rem;
    }

    .filter-title {
        color: #17365d;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .kpi-card {
        position: relative;

        min-height: 125px;

        border-radius: 14px;

        padding: 1.15rem 1.3rem;

        border: 1px solid rgba(148, 163, 184, 0.22);

        box-shadow:
            0 3px 10px rgba(15, 23, 42, 0.05);

        overflow: hidden;
    }

    .kpi-card-blue {
        background: linear-gradient(
            135deg,
            #eff8ff 0%,
            #e8f4ff 100%
        );

        border-left: 4px solid #2196f3;
    }

    .kpi-card-green {
        background: linear-gradient(
            135deg,
            #effcf5 0%,
            #e9f9f0 100%
        );

        border-left: 4px solid #35b779;
    }

    .kpi-card-purple {
        background: linear-gradient(
            135deg,
            #f7f1ff 0%,
            #f2ebff 100%
        );

        border-left: 4px solid #7c3aed;
    }

    .kpi-card-orange {
        background: linear-gradient(
            135deg,
            #fff7ed 0%,
            #fff1e5 100%
        );

        border-left: 4px solid #f97316;
    }

    .kpi-icon {
        position: absolute;

        top: 17px;
        right: 18px;

        width: 42px;
        height: 42px;

        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 1.25rem;

        background: rgba(255, 255, 255, 0.75);
    }

    .kpi-label {
        color: #475569;

        font-size: 0.88rem;

        font-weight: 600;

        margin-bottom: 0.4rem;
    }

    .kpi-value {
        color: #17365d;

        font-size: 2rem;

        font-weight: 700;

        line-height: 1.2;
    }

    .kpi-description {
        color: #64748b;

        font-size: 0.72rem;

        margin-top: 0.4rem;
    }

    .chart-title {
        color: #17365d;

        font-size: 1.25rem;

        font-weight: 700;

        margin-bottom: 0.15rem;
    }

    .chart-subtitle {
        color: #64748b;

        font-size: 0.8rem;

        margin-bottom: 0.5rem;
    }

    .section-title {
        color: #17365d;

        font-size: 1.25rem;

        font-weight: 700;

        margin-top: 1rem;
    }

    .info-box {
        background: #eff8ff;

        border: 1px solid #bfdbfe;

        border-radius: 12px;

        padding: 1rem 1.2rem;

        color: #334155;

        font-size: 0.82rem;
    }

    .info-title {
        color: #17365d;

        font-weight: 700;

        margin-bottom: 0.3rem;
    }

    .footer {
        text-align: center;

        color: #94a3b8;

        font-size: 0.75rem;

        margin-top: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ACESSO AO BANCO
# ============================================================

@st.cache_data(ttl=60)
def carregar_dados():

    if not DATABASE.exists():
        raise FileNotFoundError(
            f"Banco DuckDB não encontrado em:\n{DATABASE}"
        )

    conn = duckdb.connect(
        str(DATABASE),
        read_only=True,
    )

    # --------------------------------------------------------
    # Consumo por período e tipo
    # --------------------------------------------------------

    df_resumo = conn.execute(
        """
        SELECT
            ano,
            mes,
            nome_mes,
            tipo_reclamacao,
            sessoes_realizadas,
            acordos,
            taxa_acordo,
            reducao_media_percentual
        FROM main.resumo_conciliacao
        ORDER BY
            ano,
            mes,
            tipo_reclamacao
        """
    ).fetchdf()

    # --------------------------------------------------------
    # Indicadores gerais
    # --------------------------------------------------------

    df_geral = conn.execute(
        """
        SELECT
            sessoes_realizadas,
            acordos,
            taxa_acordo,
            reducao_media_percentual
        FROM main.indicadores_gerais
        """
    ).fetchdf()

    # --------------------------------------------------------
    # Indicadores para os filtros do dashboard
    # --------------------------------------------------------

    df_dashboard = conn.execute(
        """
        SELECT
            ano,
            mes,
            tipo_reclamacao,
            sessoes_realizadas,
            acordos,
            taxa_acordo,
            reducao_media_percentual
        FROM main.indicadores_dashboard
        """
    ).fetchdf()

    conn.close()

    return df_resumo, df_geral, df_dashboard


# ============================================================
# CARREGAMENTO
# ============================================================

try:

    df, df_geral, df_dashboard = carregar_dados()

except Exception as erro:

    st.error(
        "Não foi possível carregar os dados do pipeline."
    )

    st.code(str(erro))

    st.stop()


if df.empty:

    st.warning(
        "A camada de Consumo não possui dados."
    )

    st.stop()


if df_geral.empty:

    st.warning(
        "Os indicadores gerais não estão disponíveis."
    )

    st.stop()


if df_dashboard.empty:

    st.warning(
        "Os indicadores para o dashboard não estão disponíveis."
    )

    st.stop()


# ============================================================
# CABEÇALHO
# ============================================================

st.title("⚖️ Indicadores de Conciliação — CEJUSC")

st.markdown(
    "Análise da taxa de acordos e da redução média "
    "dos valores reclamados nas sessões de conciliação."
)


# ============================================================
# FILTROS
# ============================================================

st.subheader("🔎 Filtros de análise")


col1, col2, col3 = st.columns(3)


# ------------------------------------------------------------
# Ano
# ------------------------------------------------------------

with col1:

    anos = sorted(
        df["ano"]
        .dropna()
        .unique()
        .tolist()
    )

    ano_opcoes = ["Todos"] + [
        int(ano)
        for ano in anos
    ]

    ano_selecionado = st.selectbox(
        "Ano",
        ano_opcoes,
    )


# ------------------------------------------------------------
# Mês
# ------------------------------------------------------------

with col2:

    meses = (
        df[
            [
                "mes",
                "nome_mes",
            ]
        ]
        .drop_duplicates()
        .sort_values("mes")
    )

    mes_opcoes = ["Todos"] + (
        meses["nome_mes"].tolist()
    )

    mes_selecionado = st.selectbox(
        "Mês",
        mes_opcoes,
    )


# ------------------------------------------------------------
# Tipo
# ------------------------------------------------------------

with col3:

    tipos = sorted(
        df["tipo_reclamacao"]
        .dropna()
        .unique()
        .tolist()
    )

    tipo_opcoes = ["Todos"] + tipos

    tipo_selecionado = st.selectbox(
        "Tipo de reclamação",
        tipo_opcoes,
    )


# ============================================================
# FILTRAGEM DE APRESENTAÇÃO
# ============================================================

df_filtrado = df.copy()


if ano_selecionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["ano"] == ano_selecionado
    ]


if mes_selecionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["nome_mes"] == mes_selecionado
    ]


if tipo_selecionado != "Todos":

    df_filtrado = df_filtrado[
        df_filtrado["tipo_reclamacao"]
        == tipo_selecionado
    ]


# ============================================================
# INDICADORES
# ============================================================

st.subheader("Indicadores")

st.caption(
    f"Indicadores para: "
    f"{ano_selecionado} · "
    f"{mes_selecionado} · "
    f"{tipo_selecionado}"
)


# ============================================================
# CSS DOS CARDS
# ============================================================

st.markdown(
    """
    <style>

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 125px;
        box-shadow: 0 3px 10px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 0.88rem;
        font-weight: 600;
        color: #475569;
    }

    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #17365d;
    }

    div[data-testid="stHorizontalBlock"]
        > div:nth-child(1)
        div[data-testid="stMetric"] {
        border-left: 4px solid #2196f3;
        background: linear-gradient(
            135deg,
            #eff8ff 0%,
            #e8f4ff 100%
        );
    }

    div[data-testid="stHorizontalBlock"]
        > div:nth-child(2)
        div[data-testid="stMetric"] {
        border-left: 4px solid #35b779;
        background: linear-gradient(
            135deg,
            #effcf5 0%,
            #e9f9f0 100%
        );
    }

    div[data-testid="stHorizontalBlock"]
        > div:nth-child(3)
        div[data-testid="stMetric"] {
        border-left: 4px solid #7c3aed;
        background: linear-gradient(
            135deg,
            #f7f1ff 0%,
            #f2ebff 100%
        );
    }

    div[data-testid="stHorizontalBlock"]
        > div:nth-child(4)
        div[data-testid="stMetric"] {
        border-left: 4px solid #f97316;
        background: linear-gradient(
            135deg,
            #fff7ed 0%,
            #fff1e5 100%
        );
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SELEÇÃO DOS INDICADORES CONFORME OS FILTROS
# ============================================================

# O Streamlit não recalcula nenhuma regra de negócio.
# Apenas seleciona o registro previamente calculado pelo dbt.
#
# No modelo indicadores_dashboard:
# NULL representa "Todos".

filtro_ano = (
    ano_selecionado
    if ano_selecionado != "Todos"
    else None
)

filtro_mes = (
    int(
        meses.loc[
            meses["nome_mes"] == mes_selecionado,
            "mes",
        ].iloc[0]
    )
    if mes_selecionado != "Todos"
    else None
)

filtro_tipo = (
    tipo_selecionado
    if tipo_selecionado != "Todos"
    else None
)


df_indicador = df_dashboard.copy()


# ------------------------------------------------------------
# Filtro de ano
# ------------------------------------------------------------

if filtro_ano is None:

    df_indicador = df_indicador[
        df_indicador["ano"].isna()
    ]

else:

    df_indicador = df_indicador[
        df_indicador["ano"] == filtro_ano
    ]


# ------------------------------------------------------------
# Filtro de mês
# ------------------------------------------------------------

if filtro_mes is None:

    df_indicador = df_indicador[
        df_indicador["mes"].isna()
    ]

else:

    df_indicador = df_indicador[
        df_indicador["mes"] == filtro_mes
    ]


# ------------------------------------------------------------
# Filtro de tipo
# ------------------------------------------------------------

if filtro_tipo is None:

    df_indicador = df_indicador[
        df_indicador["tipo_reclamacao"].isna()
    ]

else:

    df_indicador = df_indicador[
        df_indicador["tipo_reclamacao"]
        == filtro_tipo
    ]


# ============================================================
# VALORES DOS INDICADORES
# ============================================================

if df_indicador.empty:

    sessoes = 0
    acordos = 0
    taxa = None
    reducao = None

else:

    indicador = df_indicador.iloc[0]

    sessoes = indicador["sessoes_realizadas"]
    acordos = indicador["acordos"]
    taxa = indicador["taxa_acordo"]
    reducao = indicador["reducao_media_percentual"]


# ============================================================
# CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


# ------------------------------------------------------------
# Sessões realizadas
# ------------------------------------------------------------

with kpi1:

    st.metric(
        label="👥  Sessões realizadas",
        value=f"{int(sessoes)}",
        help="Sessões efetivamente realizadas.",
    )


# ------------------------------------------------------------
# Acordos realizados
# ------------------------------------------------------------

with kpi2:

    st.metric(
        label="🤝  Acordos realizados",
        value=f"{int(acordos)}",
        help="Sessões encerradas com acordo.",
    )


# ------------------------------------------------------------
# Taxa de acordo
# ------------------------------------------------------------

with kpi3:

    if pd.notna(taxa):

        valor_taxa = f"{float(taxa):.2f}%"

    else:

        valor_taxa = "N/A"


    st.metric(
        label="🎯  Taxa de acordo",
        value=valor_taxa,
        help="Percentual de acordos sobre as sessões realizadas.",
    )


# ------------------------------------------------------------
# Redução média
# ------------------------------------------------------------

with kpi4:

    if pd.notna(reducao):

        valor_reducao = f"{float(reducao):.2f}%"

    else:

        valor_reducao = "N/A"


    st.metric(
        label="%  Redução média",
        value=valor_reducao,
        help="Redução média dos valores reclamados nos acordos.",
    )


# ============================================================
# GRÁFICOS
# ============================================================

col1, col2 = st.columns(2)


# ============================================================
# FUNÇÃO AUXILIAR PARA GRÁFICOS
# ============================================================

def configurar_grafico(fig):

    fig.update_layout(
        height=390,

        margin=dict(
            l=10,
            r=10,
            t=20,
            b=10,
        ),

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial, sans-serif",
            color="#475569",
            size=12,
        ),

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
        ),

        xaxis=dict(
            title=None,
            showgrid=False,
            tickfont=dict(
                size=11
            ),
        ),

        yaxis=dict(
            title=None,
            range=[0, 100],
            gridcolor="#e2e8f0",
            zeroline=False,
        ),

        hovermode="x unified",
    )

    return fig


# ============================================================
# TAXA DE ACORDO
# ============================================================

with col1:

    st.subheader("Taxa de acordo")

    st.caption(
        "Comparação da taxa de acordo por período e tipo de reclamação."
    )

    dados = df_filtrado[
        [
            "ano",
            "mes",
            "nome_mes",
            "tipo_reclamacao",
            "taxa_acordo",
        ]
    ].dropna(
        subset=["taxa_acordo"]
    ).copy()

    if not dados.empty:

        dados = dados.sort_values(
            ["ano", "mes"]
        )

        dados["periodo"] = (
            dados["nome_mes"]
            + "/"
            + dados["ano"].astype(str)
        )

        fig = go.Figure()

        cores = [
            "#1976D2",
            "#64B5F6",
            "#EF4444",
            "#FCA5A5",
        ]

        for i, tipo in enumerate(
            dados["tipo_reclamacao"].unique()
        ):

            serie = dados[
                dados["tipo_reclamacao"] == tipo
            ]

            fig.add_trace(
                go.Bar(
                    x=serie["periodo"],
                    y=serie["taxa_acordo"],
                    name=tipo,
                    marker_color=cores[
                        i % len(cores)
                    ],
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Taxa: %{y:.2f}%"
                        "<extra>"
                        + tipo
                        + "</extra>"
                    ),
                )
            )

        fig = configurar_grafico(fig)

        fig.update_layout(
            barmode="group",
            bargap=0.25,
            bargroupgap=0.08,
            yaxis=dict(
                title="Taxa de acordo (%)",
                range=[0, 100],
                dtick=20,
                gridcolor="#e2e8f0",
                zeroline=False,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    else:

        st.info(
            "Não existem dados de taxa de acordo "
            "para os filtros selecionados."
        )


# ============================================================
# REDUÇÃO MÉDIA
# ============================================================

with col2:

    st.subheader("Redução média")

    st.caption(
        "Redução média dos valores reclamados nos acordos."
    )

    dados = df_filtrado[
        [
            "ano",
            "mes",
            "nome_mes",
            "tipo_reclamacao",
            "reducao_media_percentual",
        ]
    ].dropna(
        subset=["reducao_media_percentual"]
    ).copy()

    if not dados.empty:

        dados = dados.sort_values(
            ["ano", "mes"]
        )

        dados["periodo"] = (
            dados["nome_mes"]
            + "/"
            + dados["ano"].astype(str)
        )

        fig = go.Figure()

        cores = [
            "#1976D2",
            "#64B5F6",
            "#EF4444",
            "#FCA5A5",
        ]

        for i, tipo in enumerate(
            dados["tipo_reclamacao"].unique()
        ):

            serie = dados[
                dados["tipo_reclamacao"] == tipo
            ]

            fig.add_trace(
                go.Bar(
                    x=serie["periodo"],
                    y=serie[
                        "reducao_media_percentual"
                    ],
                    name=tipo,
                    marker_color=cores[
                        i % len(cores)
                    ],
                    hovertemplate=(
                        "<b>%{x}</b><br>"
                        "Redução: %{y:.2f}%"
                        "<extra>"
                        + tipo
                        + "</extra>"
                    ),
                )
            )

        fig = configurar_grafico(fig)

        fig.update_layout(
            barmode="group",
            bargap=0.25,
            bargroupgap=0.08,
            yaxis=dict(
                title="Redução média (%)",
                range=[0, 100],
                dtick=20,
                gridcolor="#e2e8f0",
                zeroline=False,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )

    else:

        st.info(
            "Não existem dados de redução média "
            "para os filtros selecionados."
        )


# ============================================================
# DETALHAMENTO
# ============================================================

st.markdown(
    '<div class="section-title">📊 Detalhamento</div>',
    unsafe_allow_html=True,
)


df_exibicao = df_filtrado.copy()


df_exibicao = df_exibicao.rename(
    columns={
        "ano": "Ano",
        "mes": "Mês",
        "nome_mes": "Nome do mês",
        "tipo_reclamacao": "Tipo de reclamação",
        "sessoes_realizadas": "Sessões realizadas",
        "acordos": "Acordos",
        "taxa_acordo": "Taxa de acordo (%)",
        "reducao_media_percentual": "Redução média (%)",
    }
)


st.dataframe(
    df_exibicao,
    use_container_width=True,
    hide_index=True,
    height=360,
    column_config={
        "Ano": st.column_config.NumberColumn(
            format="%d"
        ),

        "Mês": st.column_config.NumberColumn(
            format="%d"
        ),

        "Sessões realizadas": st.column_config.NumberColumn(
            format="%d"
        ),

        "Acordos": st.column_config.NumberColumn(
            format="%d"
        ),

        "Taxa de acordo (%)": st.column_config.NumberColumn(
            format="%.2f%%"
        ),

        "Redução média (%)": st.column_config.NumberColumn(
            format="%.2f%%"
        ),
    },
)


# ============================================================
# SOBRE OS DADOS
# ============================================================

with st.expander("ℹ️ Sobre os dados apresentados"):

    st.markdown(
        """
        Os indicadores apresentados neste dashboard são
        provenientes da **camada de Consumo** do pipeline de dados.

        **Fluxo:**

        Fontes → Python → Bronze/Delta Lake → Silver/dbt
        → Gold/dbt → Consumo/dbt → Streamlit

        O Streamlit atua somente como camada de apresentação.
        As regras de negócio e os cálculos dos indicadores
        são realizados e materializados pelo dbt.
        """
    )


# ============================================================
# PERGUNTA DE NEGÓCIO
# ============================================================

with st.expander(
    "📌 Pergunta de negócio"
):

    st.markdown(
        """
        **Qual é a taxa de acordos realizados nas sessões de
        conciliação e qual é o percentual médio de redução do
        valor reclamado nos acordos, por tipo de reclamação
        e por período?**
        """
    )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown(
    """
    <div class="footer">
        CEJUSC — Pipeline de Dados · Dados 100% sintéticos
    </div>
    """,
    unsafe_allow_html=True,
)