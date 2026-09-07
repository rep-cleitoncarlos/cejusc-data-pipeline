# CEJUSC Data Pipeline

Pipeline de dados para análise de sessões de conciliação do CEJUSC.

O projeto foi desenvolvido como uma Prova de Conceito (PoC) de um
pipeline de dados utilizando Python, Pandas, Delta Lake, DuckDB e dbt.

---

## 1. Pergunta de negócio

> Qual é a taxa de acordos realizados nas sessões de conciliação
> e qual é o percentual médio de redução do valor reclamado nos
> acordos, por tipo de reclamação e por período?

A análise considera dois eixos:

- tipo de reclamação;
- período (ano/mês).

---

## 2. Métricas

### Taxa de acordo

A taxa de acordo é calculada por:

    acordos / sessões realizadas × 100

São consideradas sessões realizadas aquelas cujo resultado é:

- ACORDO;
- NAO_ACORDO.

Ausências do reclamante ou do reclamado não entram no denominador.

### Redução média percentual

Para cada acordo:

    (valor reclamado - valor do acordo)
    / valor reclamado × 100

A média considera somente acordos com:

- valor reclamado maior que zero;
- valor de acordo informado.

---

## 3. Arquitetura

O pipeline utiliza uma arquitetura em camadas:

    Fontes
      │
      ├── reclamacoes.csv
      └── sessoes_conciliacao.json
             │
             ▼
      Python + Pandas
             │
             ▼
      Bronze — Delta Lake
             │
             ▼
      Silver — dbt
       ├── stg_reclamacoes
       └── stg_sessoes
             │
             ▼
      Gold — dbt
       ├── dim_tempo
       ├── dim_tipo_reclamacao
       └── fato_conciliacao
             │
             ▼
      Consumo — dbt
       └── resumo_conciliacao
             │
             ▼
      SQL final
             │
             ▼
      Resposta da pergunta de negócio

---

## 4. Tecnologias

- Python 3.11
- Pandas
- PyArrow
- Delta Lake
- deltalake
- DuckDB
- dbt Core
- dbt-duckdb

---

## 5. Fontes de dados

O projeto utiliza duas fontes sintéticas em formatos diferentes.

### Reclamações

Arquivo:

    data/raw/reclamacoes.csv

Formato:

    CSV

Principais atributos:

- id_reclamacao;
- id_processo;
- data_reclamacao;
- tipo_reclamacao;
- valor_reclamado;
- canal;
- conciliador_id;
- modalidade_preferida.

### Sessões de conciliação

Arquivo:

    data/raw/sessoes_conciliacao.json

Formato:

    JSON

Principais atributos:

- id_sessao;
- id_reclamacao;
- data_sessao;
- resultado;
- valor_acordo;
- parcelas;
- tempo_sessao_minutos;
- observacao.

Todos os dados são sintéticos e não representam pessoas ou
processos reais.

---

## 6. Defeitos intencionais nas fontes

Para simular uma situação real de engenharia de dados, as fontes
contêm inconsistências propositalmente inseridas.

### CSV

Foram inseridas variações de classificação:

    Cobrança indevida
    cobranca indevida
    COBRANÇA INDEVIDA

Também existem variações para falha de serviço:

    Falha no servico
    Falha na prestação de serviço

Outros problemas:

- valor reclamado ausente;
- valor monetário utilizando vírgula como separador decimal.

### JSON

Foram inseridas variações e problemas como:

- `Não Acordo` em vez de `NAO_ACORDO`;
- data em formato `dd/mm/YYYY`;
- quantidade de parcelas como texto;
- valor de acordo utilizando vírgula como separador decimal.

Os defeitos são preservados na Bronze e tratados nas etapas
posteriores do pipeline.

---

## 7. Camada Raw

A camada Raw contém os arquivos exatamente como recebidos.

Local:

    data/raw/

A ingestão não aplica regras de negócio aos dados.

---

## 8. Camada Bronze

A Bronze utiliza Delta Lake.

Local:

    data/bronze/

Os dados são preservados com seus defeitos originais.

Também são adicionados metadados técnicos:

- `_source_file`;
- `_source_row`;
- `_ingested_at`.

A Bronze permite versionamento dos dados e Time Travel.

---

## 9. Camada Silver

A Silver é construída com dbt.

Modelos:

    stg_reclamacoes
    stg_sessoes

Responsabilidades:

- conversão de tipos;
- tratamento de separadores decimais;
- padronização de datas;
- padronização de categorias;
- normalização dos resultados;
- integração das estruturas para as próximas camadas.

As regras de negócio utilizadas para a análise são documentadas
nos próprios modelos.

---

## 10. Camada Gold

A Gold utiliza um modelo dimensional.

### Dimensão de tempo

    dim_tempo

Grão:

> Uma linha representa um dia do calendário utilizado pelas sessões.

### Dimensão de tipo de reclamação

    dim_tipo_reclamacao

Grão:

> Uma linha representa um tipo de reclamação padronizado.

### Fato de conciliação

    fato_conciliacao

Grão:

> Uma linha representa uma sessão de conciliação associada a uma reclamação.

A fato contém os indicadores:

- `sessao_realizada`;
- `houve_acordo`.

---

## 11. Camada de Consumo

Modelo:

    resumo_conciliacao

Grão:

> Uma linha representa o resultado agregado de um mês e um tipo
> de reclamação.

O modelo disponibiliza:

- ano;
- mês;
- nome do mês;
- tipo de reclamação;
- sessões realizadas;
- acordos;
- taxa de acordo;
- redução média percentual.

Essa camada é orientada diretamente à pergunta de negócio.

---

## 12. Testes de qualidade

O projeto utiliza testes nativos do dbt.

São utilizados:

- `not_null`;
- `unique`;
- `accepted_values`;
- `relationships`.

Os testes verificam aspectos como:

- identificadores obrigatórios;
- unicidade das chaves;
- valores permitidos;
- integridade referencial.

Resultado atual:

    PASS=43
    WARN=0
    ERROR=0

---

## 13. Linhagem

A linhagem pode ser consultada pelo dbt.

Exemplo de dependência:

    source:bronze.sessoes_conciliacao
        ↓
    stg_sessoes
        ↓
    fato_conciliacao
        ↓
    resumo_conciliacao

A utilização de `ref()` e `source()` permite ao dbt conhecer as
dependências entre as etapas.

---

## 14. Delta Lake e Time Travel

A tabela Bronze de reclamações possui duas versões.

Versão atual:

    1

Versão anterior:

    0

A mesma consulta foi executada sobre as duas versões.

Resultado:

    Versão anterior:
    quantidade_registros = 40
    reclamacoes_distintas = 40

    Versão atual:
    quantidade_registros = 40
    reclamacoes_distintas = 40

A alteração entre as versões foi realizada no metadado
`_ingested_at`, mantendo os dados de negócio.

O teste pode ser executado com:

    python tests/time_travel.py

---

## 15. Execução do projeto

### 15.1 Criar ambiente virtual

Windows PowerShell:

    python -m venv .venv

Ativar:

    .\.venv\Scripts\Activate.ps1

---

### 15.2 Instalar dependências

    pip install -r requirements.txt

O dbt-duckdb também deve estar instalado:

    pip install dbt-duckdb

---

### 15.3 Executar ingestão

A partir da raiz do projeto:

    python -m src.pipeline

A execução lê os arquivos da Raw e grava as tabelas Delta na Bronze.

---

### 15.4 Executar o dbt

Entrar no diretório:

    cd dbt

Executar:

    dbt build

O comando executa:

- models;
- testes;
- hook de preparação das fontes Delta.

---

### 15.5 Executar a consulta final

A consulta final está em:

    sql/consulta_final.sql

Como o ambiente utilizado é Windows PowerShell, a consulta pode
ser validada diretamente pelo Python/DuckDB ou utilizando o
cliente DuckDB quando disponível.

Exemplo:

    python -c "import duckdb; conn=duckdb.connect('data/cejusc.duckdb'); print(conn.execute('SELECT * FROM main.resumo_conciliacao ORDER BY ano, mes, tipo_reclamacao').fetchdf().to_string(index=False)); conn.close()"

---

## 16. Validações

### Validar Bronze

    python tests/validar_bronze.py

### Validar Gold

    python tests/validar_gold.py

### Validar histórico Delta

    python tests/validar_delta.py

### Demonstrar Time Travel

    python tests/time_travel.py

---

## 17. Documentação de decisões

As principais decisões de arquitetura e tratamento dos dados
estão documentadas em:

    DECISOES.md

O documento registra:

- arquitetura de armazenamento;
- granularidade da fato;
- tratamento de dados ambíguos;
- tratamento de valores ausentes;
- destino de registros inválidos;
- definição de sessão realizada;
- definição de acordo;
- definição das métricas;
- localização das regras de negócio.

---

## 18. Privacidade

Todos os dados utilizados neste projeto são sintéticos.

Não são utilizados:

- nomes reais;
- CPF;
- dados pessoais reais;
- números reais de processos;
- dados reais de clientes.

---

## 19. Estrutura do projeto

    cejusc-data-pipeline/
    │
    ├── data/
    │   ├── raw/
    │   │   ├── reclamacoes.csv
    │   │   └── sessoes_conciliacao.json
    │   │
    │   └── bronze/
    │       ├── reclamacoes/
    │       └── sessoes_conciliacao/
    │
    ├── dbt/
    │   ├── dbt_project.yml
    │   ├── profiles.yml
    │   ├── macros/
    │   └── models/
    │       ├── silver/
    │       ├── gold/
    │       └── consumo/
    │
    ├── src/
    │   ├── ingest.py
    │   └── pipeline.py
    │
    ├── tests/
    │   ├── validar_bronze.py
    │   ├── validar_gold.py
    │   ├── validar_delta.py
    │   ├── criar_versao_delta.py
    │   └── time_travel.py
    │
    ├── sql/
    │   └── consulta_final.sql
    │
    ├── DECISOES.md
    ├── README.md
    └── requirements.txt

---

## 20. Resultado

O pipeline permite responder à pergunta de negócio utilizando
somente a camada de Consumo.

O resultado apresenta a taxa de acordos e a redução média
percentual por tipo de reclamação e por período.

A consulta final não acessa os dados Raw ou Bronze e não
reimplementa as regras de negócio.