from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from deltalake import write_deltalake


# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Fontes
RAW_DIR = BASE_DIR / "data" / "raw"

# Bronze
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def ingest_reclamacoes():
    """
    Lê o arquivo CSV de reclamações e persiste os dados
    na camada Bronze como uma tabela Delta.

    Nenhuma regra de negócio ou transformação de dados
    é aplicada nesta etapa.
    """

    source_file = RAW_DIR / "reclamacoes.csv"
    target_table = BRONZE_DIR / "reclamacoes"

    print(f"Lendo fonte: {source_file}")

    df = pd.read_csv(
        source_file,
        sep=";",
        dtype=str
    )

    # Metadados técnicos da ingestão
    df["_source_file"] = source_file.name
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df["_source_row"] = range(1, len(df) + 1)

    print(f"Registros lidos: {len(df)}")

    write_deltalake(
        target_table,
        df,
        mode="overwrite"
    )

    print(f"Bronze gravada em: {target_table}")


def ingest_sessoes():
    """
    Lê o arquivo JSON de sessões de conciliação e persiste
    os dados na camada Bronze como uma tabela Delta.

    Nenhuma regra de negócio ou transformação de dados
    é aplicada nesta etapa.
    """

    source_file = RAW_DIR / "sessoes_conciliacao.json"
    target_table = BRONZE_DIR / "sessoes_conciliacao"

    print(f"Lendo fonte: {source_file}")

    df = pd.read_json(
        source_file,
        dtype=str
    )

    # Metadados técnicos da ingestão
    df["_source_file"] = source_file.name
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()
    df["_source_row"] = range(1, len(df) + 1)

    print(f"Registros lidos: {len(df)}")

    write_deltalake(
        target_table,
        df,
        mode="overwrite"
    )

    print(f"Bronze gravada em: {target_table}")


def run_ingestion():
    """
    Executa a ingestão de todas as fontes.
    """

    BRONZE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ingest_reclamacoes()
    ingest_sessoes()


if __name__ == "__main__":
    run_ingestion()