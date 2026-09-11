-- ============================================================
-- DEMONSTRAÇÃO DELTA LAKE - TIME TRAVEL
-- ============================================================
--
-- Objetivo:
-- Demonstrar que o Delta Lake mantém versões da tabela
-- e permite consultar o estado atual e um estado anterior.
--
-- A tabela utilizada é:
-- data/bronze/reclamacoes
--
-- O marcador {{VERSAO_ANTERIOR}} é substituído automaticamente
-- pelo script tests/time_travel.py.
--
-- A demonstração utiliza as versões consecutivas:
--
-- versão anterior → contém REC-TIME-TRAVEL
-- versão atual    → não contém REC-TIME-TRAVEL
--
-- O registro REC-TIME-TRAVEL é um registro técnico criado
-- exclusivamente para demonstrar o versionamento.
-- ============================================================


-- ============================================================
-- 1. VERSÃO ATUAL
-- ============================================================

SELECT
    'ATUAL' AS versao,
    COUNT(*) AS total_registros
FROM delta_scan('data/bronze/reclamacoes');


-- ============================================================
-- 2. VERSÃO ANTERIOR
-- ============================================================

SELECT
    'ANTERIOR' AS versao,
    COUNT(*) AS total_registros
FROM delta_scan(
    'data/bronze/reclamacoes',
    version => {{VERSAO_ANTERIOR}}
);


-- ============================================================
-- 3. REGISTRO NA VERSÃO ATUAL
-- ============================================================

SELECT
    id_reclamacao,
    id_processo,
    tipo_reclamacao,
    valor_reclamado
FROM delta_scan('data/bronze/reclamacoes')
WHERE id_reclamacao = 'REC-TIME-TRAVEL';


-- ============================================================
-- 4. MESMO REGISTRO NA VERSÃO ANTERIOR
-- ============================================================

SELECT
    id_reclamacao,
    id_processo,
    tipo_reclamacao,
    valor_reclamado
FROM delta_scan(
    'data/bronze/reclamacoes',
    version => {{VERSAO_ANTERIOR}}
)
WHERE id_reclamacao = 'REC-TIME-TRAVEL';