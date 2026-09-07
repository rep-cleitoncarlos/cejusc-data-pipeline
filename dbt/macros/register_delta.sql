{% macro register_delta_sources() %}

    CREATE SCHEMA IF NOT EXISTS bronze;

    CREATE OR REPLACE VIEW bronze.reclamacoes AS
    SELECT *
    FROM delta_scan('../data/bronze/reclamacoes');

    CREATE OR REPLACE VIEW bronze.sessoes_conciliacao AS
    SELECT *
    FROM delta_scan('../data/bronze/sessoes_conciliacao');

{% endmacro %}