{{ config(materialized='table') }}

-- Grain:
-- Uma linha representa uma sessão de conciliação
-- associada a uma reclamação.

-- Regras de negócio:
-- 1. Sessão realizada = ACORDO ou NAO_ACORDO.
-- 2. Sessão não realizada = AUSENTE_RECLAMANTE ou AUSENTE_RECLAMADO.
-- 3. Houve acordo = resultado ACORDO.
-- 4. A redução percentual será calculada na camada de consumo,
--    e não armazenada como regra pré-calculada na fonte.

SELECT
    s.id_sessao AS sessao_id,

    r.id_reclamacao AS reclamacao_id,

    t.data_sk AS data_sessao_sk,

    tr.tipo_reclamacao_sk,

    r.conciliador_id,

    s.resultado,

    r.valor_reclamado,

    s.valor_acordo,

    s.parcelas,

    s.tempo_sessao_minutos,

    CASE
        WHEN s.resultado IN ('ACORDO', 'NAO_ACORDO')
            THEN 1
        ELSE 0
    END AS sessao_realizada,

    CASE
        WHEN s.resultado = 'ACORDO'
            THEN 1
        ELSE 0
    END AS houve_acordo

FROM {{ ref('stg_sessoes') }} s

INNER JOIN {{ ref('stg_reclamacoes') }} r
    ON s.id_reclamacao = r.id_reclamacao

LEFT JOIN {{ ref('dim_tempo') }} t
    ON s.data_sessao = t.data

LEFT JOIN {{ ref('dim_tipo_reclamacao') }} tr
    ON r.tipo_reclamacao = tr.tipo_reclamacao