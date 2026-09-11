from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
BRONZE_DIR = ROOT / "data" / "bronze"
SILVER_DIR = ROOT / "data" / "silver"
GOLD_DIR = ROOT / "data" / "gold"
QUARANTINE_DIR = ROOT / "data" / "quarantine"

DUCKDB_FILE = ROOT / "data" / "cejusc.duckdb"

DBT_TARGET_DIR = ROOT / "dbt" / "target"
DBT_LOGS_DIR = ROOT / "dbt" / "logs"


def limpar_diretorio(diretorio: Path):
    """Remove o conteúdo de um diretório, mas mantém o diretório."""
    if not diretorio.exists():
        diretorio.mkdir(parents=True)
        return

    for item in diretorio.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def main():
    print("=" * 60)
    print("PREPARAÇÃO DO AMBIENTE PARA A APRESENTAÇÃO")
    print("=" * 60)

    print("\n[1/5] Verificando fontes...")
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"A pasta de fontes não foi encontrada: {RAW_DIR}"
        )

    arquivos_raw = list(RAW_DIR.iterdir())

    if not arquivos_raw:
        raise RuntimeError(
            "A pasta data/raw está vazia. "
            "As fontes originais precisam permanecer disponíveis."
        )

    print(f"      OK - {len(arquivos_raw)} arquivo(s) encontrado(s) em data/raw")

    print("\n[2/5] Limpando camadas geradas...")
    for diretorio in [
        BRONZE_DIR,
        SILVER_DIR,
        GOLD_DIR,
        QUARANTINE_DIR,
    ]:
        limpar_diretorio(diretorio)
        print(f"      OK - {diretorio.relative_to(ROOT)}")

    print("\n[3/5] Removendo banco DuckDB...")
    if DUCKDB_FILE.exists():
        DUCKDB_FILE.unlink()
        print("      OK - data/cejusc.duckdb removido")
    else:
        print("      OK - banco já não existia")

    print("\n[4/5] Limpando artefatos do dbt...")
    for diretorio in [
        DBT_TARGET_DIR,
        DBT_LOGS_DIR,
    ]:
        limpar_diretorio(diretorio)
        print(f"      OK - {diretorio.relative_to(ROOT)}")

    print("\n[5/5] Conferindo ambiente...")

    print(f"      Fontes preservadas: {RAW_DIR.exists()}")
    print(f"      Bronze vazia: {not any(BRONZE_DIR.iterdir())}")
    print(f"      Silver vazia: {not any(SILVER_DIR.iterdir())}")
    print(f"      Gold vazia: {not any(GOLD_DIR.iterdir())}")
    print(f"      DuckDB inexistente: {not DUCKDB_FILE.exists()}")

    print("\n" + "=" * 60)
    print("AMBIENTE PRONTO PARA A APRESENTAÇÃO")
    print("=" * 60)

    print("\nPróximo passo:")
    print("    python -m src.pipeline")
    print("    cd dbt")
    print("    dbt build")
    print("    cd ..")


if __name__ == "__main__":
    main()