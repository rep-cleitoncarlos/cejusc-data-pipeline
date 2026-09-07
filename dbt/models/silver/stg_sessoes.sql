{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa uma sessão de conciliação recebida da fonte original.
--
-- Regras de transformação:
-- 1. Data da sessão é convertida para DATE.
-- 2. Resultado da sessão é padronizado.
-- 3. Valor do acordo é convertido para DECIMAL.
-- 4. Separador decimal "," é convertido para ".".
-- 5. Quantidade de parcelas é convertida para INTEGER.
-- 6. Tempo da sessão é convertido para INTEGER.
-- 7. Valores ausentes não são preenchidos artificialmente.

SELECT
    TRIM(id_sessao) AS id_sessao,

    TRIM(id_reclamacao) AS id_reclamacao,

    COALESCE(
        TRY_CAST(data_sessao AS DATE),
        TRY_STRPTIME(data_sessao, '%d/%m/%Y')::DATE
    ) AS data_sessao,

    CASE
        WHEN LOWER(TRIM(resultado)) IN ('nao acordo', 'não acordo')
            THEN 'NAO_ACORDO'
        WHEN UPPER(TRIM(resultado)) = 'ACORDO'
            THEN 'ACORDO'
        WHEN UPPER(TRIM(resultado)) = 'AUSENTE_RECLAMANTE'
            THEN 'AUSENTE_RECLAMANTE'
        WHEN UPPER(TRIM(resultado)) = 'AUSENTE_RECLAMADO'
            THEN 'AUSENTE_RECLAMADO'
        ELSE UPPER(TRIM(resultado))
    END AS resultado,

    TRY_CAST(
        REPLACE(
            NULLIF(TRIM(valor_acordo), ''),
            ',',
            '.'
        ) AS DECIMAL(12,2)
    ) AS valor_acordo,

    TRY_CAST(
        NULLIF(TRIM(parcelas), '')
        AS INTEGER
    ) AS parcelas,

    TRY_CAST(
        NULLIF(TRIM(tempo_sessao_minutos), '')
        AS INTEGER
    ) AS tempo_sessao_minutos,

    TRIM(observacao) AS observacao,

    _source_file,
    _ingested_at,
    _source_row

FROM {{ source('bronze', 'sessoes_conciliacao') }}