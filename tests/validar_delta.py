from pathlib import Path

from deltalake import DeltaTable


BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"


def mostrar_historico(nome_tabela):
    caminho = BRONZE_DIR / nome_tabela

    tabela = DeltaTable(caminho)

    print("\n" + "=" * 60)
    print(f"TABELA: {nome_tabela}")
    print("=" * 60)

    print(f"Versão atual: {tabela.version()}")

    print("\nHistórico:")
    print(tabela.history())


def main():
    mostrar_historico("reclamacoes")
    mostrar_historico("sessoes_conciliacao")


if __name__ == "__main__":
    main()