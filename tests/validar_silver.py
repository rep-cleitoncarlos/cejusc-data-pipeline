from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cejusc.duckdb"


def main():
    conn = duckdb.connect(DB_PATH)

    print("=" * 60)
    print("VALIDAÇÃO DA SILVER")
    print("=" * 60)

    print("\n=== RECLAMAÇÕES ===")

    print("\nTipos padronizados:")
    print(
        conn.execute("""
            SELECT tipo_reclamacao, COUNT(*) AS quantidade
            FROM main.stg_reclamacoes
            GROUP BY tipo_reclamacao
            ORDER BY tipo_reclamacao
        """).fetchdf()
    )

    print("\nValores reclamados:")
    print(
        conn.execute("""
            SELECT id_reclamacao, valor_reclamado
            FROM main.stg_reclamacoes
            ORDER BY id_reclamacao
        """).fetchdf()
    )

    print("\nTipos das colunas:")
    print(
        conn.execute("""
            DESCRIBE main.stg_reclamacoes
        """).fetchdf()
    )

    print("\n=== SESSÕES ===")

    print("\nResultados:")
    print(
        conn.execute("""
            SELECT resultado, COUNT(*) AS quantidade
            FROM main.stg_sessoes
            GROUP BY resultado
            ORDER BY resultado
        """).fetchdf()
    )

    print("\nValores de acordo:")
    print(
        conn.execute("""
            SELECT id_sessao, valor_acordo, parcelas
            FROM main.stg_sessoes
            ORDER BY id_sessao
        """).fetchdf()
    )

    print("\nTipos das colunas:")
    print(
        conn.execute("""
            DESCRIBE main.stg_sessoes
        """).fetchdf()
    )

    conn.close()


if __name__ == "__main__":
    main()