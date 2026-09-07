from src.ingest import run_ingestion


def main():
    print("========================================")
    print("INÍCIO DO PIPELINE")
    print("========================================")

    run_ingestion()

    print("========================================")
    print("PIPELINE FINALIZADO COM SUCESSO")
    print("========================================")


if __name__ == "__main__":
    main()