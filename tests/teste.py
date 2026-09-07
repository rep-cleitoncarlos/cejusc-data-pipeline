import duckdb

conn = duckdb.connect("data/cejusc.duckdb")

print(
    conn.execute("""
        SELECT
            reclamacao_id,
            resultado,
            valor_reclamado,
            valor_acordo,
            houve_acordo
        FROM main.fato_conciliacao
        WHERE valor_reclamado IS NULL
    """).fetchdf()
)

conn.close()