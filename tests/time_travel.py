from pathlib import Path

import duckdb
from deltalake import DeltaTable


BASE_DIR = Path(__file__).resolve().parent.parent
DELTA_PATH = BASE_DIR / "data" / "bronze" / "reclamacoes"
SQL_PATH = BASE_DIR / "sql" / "demonstracao_time_travel.sql"


def executar():
    tabela = DeltaTable(DELTA_PATH)

    versao_atual = tabela.version()
    versao_anterior = versao_atual - 1

    print("=" * 60)
    print("DELTA TIME TRAVEL")
    print("=" * 60)
    print()

    print(f"Versão atual:     {versao_atual}")
    print(f"Versão anterior:  {versao_anterior}")
    print()

    con = duckdb.connect()

    # =========================================================
    # Carrega o SQL da demonstração
    # =========================================================

    sql = SQL_PATH.read_text(encoding="utf-8")

    sql = sql.replace(
        "{{VERSAO_ANTERIOR}}",
        str(versao_anterior)
    )

    print("Quantidade de registros:")
    print("-" * 60)

    # Consulta versão atual
    atual = con.execute(
        f"""
        SELECT COUNT(*) AS total_registros
        FROM delta_scan('{DELTA_PATH.as_posix()}')
        """
    ).fetchone()[0]

    # Consulta versão anterior
    anterior = con.execute(
        f"""
        SELECT COUNT(*) AS total_registros
        FROM delta_scan(
            '{DELTA_PATH.as_posix()}',
            version => {versao_anterior}
        )
        """
    ).fetchone()[0]

    print(f"ATUAL       {atual}")
    print(f"ANTERIOR    {anterior}")
    print()

    # =========================================================
    # Verifica REC-TIME-TRAVEL
    # =========================================================

    print("-" * 60)
    print("REGISTRO DE TESTE")
    print("-" * 60)

    registro_anterior = con.execute(
        f"""
        SELECT
            id_reclamacao,
            id_processo,
            tipo_reclamacao,
            valor_reclamado
        FROM delta_scan(
            '{DELTA_PATH.as_posix()}',
            version => {versao_anterior}
        )
        WHERE id_reclamacao = 'REC-TIME-TRAVEL'
        """
    ).fetchone()

    registro_atual = con.execute(
        f"""
        SELECT
            id_reclamacao,
            id_processo,
            tipo_reclamacao,
            valor_reclamado
        FROM delta_scan('{DELTA_PATH.as_posix()}')
        WHERE id_reclamacao = 'REC-TIME-TRAVEL'
        """
    ).fetchone()

    print()
    print(f"Versão {versao_anterior}:")

    if registro_anterior:
        print(f"  id_reclamacao      {registro_anterior[0]}")
        print(f"  id_processo        {registro_anterior[1]}")
        print(f"  tipo_reclamacao    {registro_anterior[2]}")
        print(f"  valor_reclamado    {registro_anterior[3]}")
    else:
        print("  REC-TIME-TRAVEL não encontrado.")

    print()
    print(f"Versão {versao_atual}:")

    if registro_atual:
        print(f"  id_reclamacao      {registro_atual[0]}")
        print(f"  id_processo        {registro_atual[1]}")
        print(f"  tipo_reclamacao    {registro_atual[2]}")
        print(f"  valor_reclamado    {registro_atual[3]}")
    else:
        print("  REC-TIME-TRAVEL não encontrado.")

    print()
    print("-" * 60)
    print("RESULTADO DO TIME TRAVEL")
    print("-" * 60)

    if registro_anterior and not registro_atual:
        print(
            f"✓ A versão {versao_anterior} contém "
            "REC-TIME-TRAVEL."
        )
        print(
            f"✓ A versão {versao_atual} não contém "
            "REC-TIME-TRAVEL."
        )
        print(
            "✓ O estado da versão anterior foi recuperado "
            "com sucesso."
        )
        print()
        print("TIME TRAVEL VALIDADO COM SUCESSO")
    else:
        print(
            "✗ A diferença esperada entre as versões "
            "não foi identificada."
        )

    con.close()


if __name__ == "__main__":
    executar()