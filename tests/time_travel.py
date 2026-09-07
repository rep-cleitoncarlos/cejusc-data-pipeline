from pathlib import Path

import duckdb
from deltalake import DeltaTable


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def main():
    caminho = BRONZE_DIR / "reclamacoes"

    tabela_atual = DeltaTable(caminho)
    tabela_anterior = DeltaTable(caminho, version=0)

    df_atual = tabela_atual.to_pandas()
    df_anterior = tabela_anterior.to_pandas()

    print("=" * 60)
    print("DELTA TIME TRAVEL")
    print("=" * 60)

    print(f"\nVersão atual: {tabela_atual.version()}")
    print(f"Versão anterior: {tabela_anterior.version()}")

    print("\nQuantidade de registros:")
    print(f"Versão atual:    {len(df_atual)}")
    print(f"Versão anterior: {len(df_anterior)}")

    # Registra cada versão como uma tabela temporária no DuckDB.
    conn = duckdb.connect()

    conn.register("reclamacoes_atual", df_atual)
    conn.register("reclamacoes_anterior", df_anterior)

    # Esta é a MESMA consulta executada nas duas versões.
    consulta = """
        SELECT
            COUNT(*) AS quantidade_registros,
            COUNT(DISTINCT id_reclamacao) AS reclamacoes_distintas
        FROM {tabela}
    """

    resultado_anterior = conn.execute(
        consulta.format(tabela="reclamacoes_anterior")
    ).fetchdf()

    resultado_atual = conn.execute(
        consulta.format(tabela="reclamacoes_atual")
    ).fetchdf()

    print("\n" + "-" * 60)
    print("MESMA CONSULTA EM DUAS VERSÕES")
    print("-" * 60)

    print("\nVersão anterior:")
    print(resultado_anterior.to_string(index=False))

    print("\nVersão atual:")
    print(resultado_atual.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    main()