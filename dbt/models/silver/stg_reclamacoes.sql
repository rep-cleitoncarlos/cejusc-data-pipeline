{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa uma reclamação recebida da fonte original.
--
-- Regras de transformação:
-- 1. Data é convertida para DATE.
-- 2. Valor reclamado é convertido para DECIMAL.
-- 3. Separador decimal "," é convertido para ".".
-- 4. Tipo de reclamação é padronizado para uma representação canônica.
-- 5. Valores ausentes não são preenchidos artificialmente.

SELECT
    TRIM(id_reclamacao) AS id_reclamacao,

    TRIM(id_processo) AS id_processo,

    COALESCE(
        TRY_CAST(data_reclamacao AS DATE),
        TRY_STRPTIME(data_reclamacao, '%d/%m/%Y')::DATE
    ) AS data_reclamacao,

    CASE
        WHEN LOWER(TRIM(tipo_reclamacao)) IN (
            'cobrança indevida',
            'cobranca indevida'
        )
        THEN 'cobranca_indevida'

        WHEN LOWER(TRIM(tipo_reclamacao)) IN (
            'falha no servico',
            'falha na prestação de serviço'
        )
        THEN 'falha_servico'

        ELSE LOWER(TRIM(tipo_reclamacao))
    END AS tipo_reclamacao,

    TRY_CAST(
        REPLACE(
            NULLIF(TRIM(valor_reclamado), ''),
            ',',
            '.'
        ) AS DECIMAL(12,2)
    ) AS valor_reclamado,

    TRIM(canal) AS canal,

    TRIM(conciliador_id) AS conciliador_id,

    TRIM(modalidade_preferida) AS modalidade_preferida,

    _source_file,
    _ingested_at,
    _source_row

FROM {{ source('bronze', 'reclamacoes') }}