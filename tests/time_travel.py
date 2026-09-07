from pathlib import Path

import duckdb
from deltalake import DeltaTable


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def main():
    caminho = BRONZE_DIR / "reclamacoes"

    tabela_atual = DeltaTable(caminho)

    versao_atual = tabela_atual.version()

    if versao_atual == 0:
        print("A tabela Delta possui apenas uma versão.")
        print("É necessário ter pelo menos duas versões para demonstrar Time Travel.")
        return

    versao_anterior = versao_atual - 1

    tabela_anterior = DeltaTable(
        caminho,
        version=versao_anterior
    )

    df_atual = tabela_atual.to_pandas()
    df_anterior = tabela_anterior.to_pandas()

    print("=" * 60)
    print("DELTA TIME TRAVEL")
    print("=" * 60)

    print(f"\nVersão atual:     {versao_atual}")
    print(f"Versão anterior:  {versao_anterior}")

    print("\nQuantidade de registros:")
    print(f"Versão atual:     {len(df_atual)}")
    print(f"Versão anterior:  {len(df_anterior)}")

    conn = duckdb.connect()

    conn.register("reclamacoes_atual", df_atual)
    conn.register("reclamacoes_anterior", df_anterior)

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

    print(f"\nVersão {versao_anterior}:")
    print(resultado_anterior.to_string(index=False))

    print(f"\nVersão {versao_atual}:")
    print(resultado_atual.to_string(index=False))

    conn.close()


if __name__ == "__main__":
    main()