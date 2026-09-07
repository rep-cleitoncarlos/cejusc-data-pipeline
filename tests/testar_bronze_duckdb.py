from pathlib import Path

import duckdb


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cejusc.duckdb"

conn = duckdb.connect(DB_PATH)

conn.execute("INSTALL delta")
conn.execute("LOAD delta")

reclamacoes = conn.execute("""
    SELECT COUNT(*)
    FROM delta_scan('data/bronze/reclamacoes')
""").fetchone()[0]

sessoes = conn.execute("""
    SELECT COUNT(*)
    FROM delta_scan('data/bronze/sessoes_conciliacao')
""").fetchone()[0]

print(f"Reclamações: {reclamacoes}")
print(f"Sessões: {sessoes}")

conn.close()