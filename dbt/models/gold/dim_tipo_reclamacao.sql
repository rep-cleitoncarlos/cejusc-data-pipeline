{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa um tipo de reclamação padronizado.

WITH tipos AS (

    SELECT DISTINCT
        tipo_reclamacao

    FROM {{ ref('stg_reclamacoes') }}

    WHERE tipo_reclamacao IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY tipo_reclamacao
    ) AS tipo_reclamacao_sk,

    tipo_reclamacao

FROM tipos