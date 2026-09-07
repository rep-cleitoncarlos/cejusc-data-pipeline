{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa um dia do calendário utilizado pelas sessões.

SELECT DISTINCT
    CAST(
        STRFTIME(data_sessao, '%Y%m%d')
        AS INTEGER
    ) AS data_sk,

    data_sessao AS data,

    EXTRACT(YEAR FROM data_sessao) AS ano,

    EXTRACT(MONTH FROM data_sessao) AS mes,

    CASE EXTRACT(MONTH FROM data_sessao)
        WHEN 1 THEN 'Janeiro'
        WHEN 2 THEN 'Fevereiro'
        WHEN 3 THEN 'Março'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Maio'
        WHEN 6 THEN 'Junho'
        WHEN 7 THEN 'Julho'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Setembro'
        WHEN 10 THEN 'Outubro'
        WHEN 11 THEN 'Novembro'
        WHEN 12 THEN 'Dezembro'
    END AS nome_mes

FROM {{ ref('stg_sessoes') }}
WHERE data_sessao IS NOT NULL