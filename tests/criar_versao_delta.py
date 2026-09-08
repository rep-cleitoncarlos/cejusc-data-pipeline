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

    versao_antes = tabela.version()

    print(f"Versão antes da alteração: {versao_antes}")
    print(f"Registros antes da alteração: {len(df)}")

    # ---------------------------------------------------------
    # ALTERAÇÃO CONTROLADA PARA DEMONSTRAÇÃO DO TIME TRAVEL
    # ---------------------------------------------------------
    #
    # Este registro é adicionado exclusivamente para demonstrar
    # que uma nova versão da tabela Delta pode representar um
    # estado diferente da versão anterior.
    #
    # Não representa uma nova informação real do projeto.
    # ---------------------------------------------------------

    nova_reclamacao = {
        "id_reclamacao": "REC-TIME-TRAVEL",
        "id_processo": "PROC-TIME-TRAVEL",
        "data_reclamacao": "2026-08-31",
        "tipo_reclamacao": "cobranca indevida",
        "valor_reclamado": "500.00",
        "canal": "TESTE",
        "conciliador_id": "TESTE",
        "modalidade_preferida": "TESTE",
        "_source_file": "TIME_TRAVEL_TESTE",
        "_ingested_at": datetime.now(timezone.utc).isoformat(),
        "_source_row": -1,
    }

    # Evita adicionar o registro novamente caso o script
    # seja executado mais de uma vez.
    if "REC-TIME-TRAVEL" not in df["id_reclamacao"].astype(str).values:
        df = pd.concat(
            [
                df,
                pd.DataFrame([nova_reclamacao])
            ],
            ignore_index=True
        )

    # Atualiza o timestamp de ingestão para representar
    # uma nova versão da Bronze.
    df["_ingested_at"] = datetime.now(timezone.utc).isoformat()

    write_deltalake(
        caminho,
        df,
        mode="overwrite"
    )

    tabela_atualizada = DeltaTable(caminho)

    print(f"Versão depois da alteração: {tabela_atualizada.version()}")
    print(f"Registros depois da alteração: {len(df)}")


def main():
    atualizar_reclamacoes()


if __name__ == "__main__":
    main()