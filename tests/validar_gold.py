from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "cejusc.duckdb"


def main():
    conn = duckdb.connect(DB_PATH)

    print("=" * 60)
    print("VALIDAÇÃO DA GOLD")
    print("=" * 60)

    print("\n=== DIM_TEMPO ===")

    print(
        conn.execute("""
            SELECT *
            FROM main.dim_tempo
            ORDER BY data
        """).fetchdf()
    )

    print("\n=== DIM_TIPO_RECLAMACAO ===")

    print(
        conn.execute("""
            SELECT *
            FROM main.dim_tipo_reclamacao
            ORDER BY tipo_reclamacao_sk
        """).fetchdf()
    )

    print("\n=== FATO_CONCILIACAO ===")

    print(
        conn.execute("""
            SELECT
                resultado,
                sessao_realizada,
                houve_acordo,
                COUNT(*) AS quantidade
            FROM main.fato_conciliacao
            GROUP BY
                resultado,
                sessao_realizada,
                houve_acordo
            ORDER BY resultado
        """).fetchdf()
    )

    print("\nQuantidade de registros da fato:")

    print(
        conn.execute("""
            SELECT COUNT(*) AS quantidade
            FROM main.fato_conciliacao
        """).fetchdf()
    )

    conn.close()


if __name__ == "__main__":
    main()