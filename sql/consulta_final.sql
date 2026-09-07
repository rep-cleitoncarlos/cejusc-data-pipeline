-- Pergunta de negócio:
-- Qual é a taxa de acordos realizados nas sessões de conciliação
-- e qual é o percentual médio de redução do valor reclamado
-- nos acordos, por tipo de reclamação e por período?

SELECT
    ano,
    mes,
    nome_mes,
    tipo_reclamacao,
    sessoes_realizadas,
    acordos,
    taxa_acordo,
    reducao_media_percentual
FROM main.resumo_conciliacao
ORDER BY
    ano,
    mes,
    tipo_reclamacao;