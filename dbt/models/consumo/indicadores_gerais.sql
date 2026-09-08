{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa o resultado consolidado de todo o conjunto
-- de sessões de conciliação disponíveis na camada de Gold.
--
-- Objetivo:
-- Disponibilizar os indicadores gerais para apresentação,
-- sem que a camada de consumo da aplicação precise recalculá-los.
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
    SUM(sessao_realizada) AS sessoes_realizadas,

    SUM(houve_acordo) AS acordos,

    ROUND(
        100.0 * SUM(houve_acordo)
        / NULLIF(SUM(sessao_realizada), 0),
        2
    ) AS taxa_acordo,

    ROUND(
        100.0 * AVG(
            CASE
                WHEN houve_acordo = 1
                 AND valor_reclamado > 0
                 AND valor_acordo IS NOT NULL
                THEN
                    (
                        valor_reclamado - valor_acordo
                    ) / valor_reclamado
            END
        ),
        2
    ) AS reducao_media_percentual

FROM {{ ref('fato_conciliacao') }}