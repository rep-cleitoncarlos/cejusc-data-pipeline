from pathlib import Path

from deltalake import DeltaTable


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def carregar_bronze(nome):
    caminho = BRONZE_DIR / nome
    tabela = DeltaTable(caminho)
    return tabela.to_pandas()


def validar_reclamacoes():
    df = carregar_bronze("reclamacoes")

    print("\n=== VALIDANDO RECLAMAÇÕES ===")

    print("\nTipos de reclamação encontrados:")
    print(df["tipo_reclamacao"].value_counts(dropna=False))

    print("\nValores reclamados:")
    print(df["valor_reclamado"].to_string(index=False))


def validar_sessoes():
    df = carregar_bronze("sessoes_conciliacao")

    print("\n=== VALIDANDO SESSÕES ===")

    print("\nResultados encontrados:")
    print(df["resultado"].value_counts(dropna=False))

    print("\nValores de acordo:")
    print(df["valor_acordo"].to_string(index=False))

    print("\nParcelas:")
    print(df["parcelas"].to_string(index=False))


def main():
    validar_reclamacoes()
    validar_sessoes()


if __name__ == "__main__":
    main()