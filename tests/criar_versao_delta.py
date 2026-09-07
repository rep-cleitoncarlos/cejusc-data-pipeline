from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from deltalake import DeltaTable, write_deltalake


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def atualizar_reclamacoes():
    caminho = BRONZE_DIR / "reclamacoes"

    tabela = DeltaTable(caminho)
    df = tabela.to_pandas()

    print(f"Versão antes da alteração: {tabela.version()}")

    # Alteração controlada apenas para demonstrar uma nova versão.
    # O dado continua representando a mesma informação da fonte.
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()

    write_deltalake(
        caminho,
        df,
        mode="overwrite"
    )

    tabela_atualizada = DeltaTable(caminho)

    print(f"Versão depois da alteração: {tabela_atualizada.version()}")


def main():
    atualizar_reclamacoes()


if __name__ == "__main__":
    main()