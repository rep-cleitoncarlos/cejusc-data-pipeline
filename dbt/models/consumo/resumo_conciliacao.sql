{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa o resultado agregado de um mês
-- e um tipo de reclamação.
--
-- Objetivo:
-- Disponibilizar os indicadores necessários para responder
-- à pergunta de negócio sobre taxa de acordos e redução média.
--
-- Regras de negócio:
-- 1. Sessão realizada = ACORDO ou NAO_ACORDO.
-- 2. Acordo = resultado ACORDO.
-- 3. Taxa de acordo = acordos / sessões realizadas.
-- 4. Redução percentual =
--    (valor reclamado - valor do acordo) / valor reclamado.
-- 5. A redução média considera somente acordos com
--    valor reclamado positivo e valor de acordo informado.

SELECT
    t.ano,
    t.mes,
    t.nome_mes,
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

GROUP BY
    t.ano,
    t.mes,
    t.nome_mes,
    r.tipo_reclamacao