{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa os indicadores consolidados para
-- uma combinação dos filtros de ano, mês e tipo de reclamação.
--
-- Quando uma dimensão possui valor NULL, significa "Todos"
-- naquela dimensão.
--
-- Exemplos:
-- 2025 + 3 + cobranca_indevida
-- 2025 + 3 + NULL
-- 2025 + NULL + cobranca_indevida
-- NULL + NULL + NULL
--
-- Objetivo:
-- Disponibilizar indicadores previamente calculados para
-- a camada de apresentação, evitando regras de negócio
-- no Streamlit.

SELECT
    t.ano,
    t.mes,
    r.tipo_reclamacao,

    SUM(f.sessao_realizada) AS sessoes_realizadas,

    SUM(f.houve_acordo) AS acordos,

    ROUND(
        100.0 * SUM(f.houve_acordo)
        / NULLIF(SUM(f.sessao_realizada), 0),
        2
    ) AS taxa_acordo,

    ROUND(
        100.0 * AVG(
            CASE
                WHEN f.houve_acordo = 1
                 AND f.valor_reclamado > 0
                 AND f.valor_acordo IS NOT NULL
                THEN
                    (
                        f.valor_reclamado - f.valor_acordo
                    ) / f.valor_reclamado
            END
        ),
        2
    ) AS reducao_media_percentual

FROM {{ ref('fato_conciliacao') }} f

INNER JOIN {{ ref('dim_tempo') }} t
    ON f.data_sessao_sk = t.data_sk

INNER JOIN {{ ref('dim_tipo_reclamacao') }} r
    ON f.tipo_reclamacao_sk = r.tipo_reclamacao_sk

GROUP BY GROUPING SETS (

    (t.ano, t.mes, r.tipo_reclamacao),

    (t.ano, t.mes),

    (t.ano, r.tipo_reclamacao),

    (t.mes, r.tipo_reclamacao),

    (t.ano),

    (t.mes),

    (r.tipo_reclamacao),

    ()
)