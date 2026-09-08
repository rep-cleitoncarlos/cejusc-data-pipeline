# CEJUSC Data Pipeline

Pipeline de Engenharia de Dados desenvolvido para tratamento e análise de dados de sessões de conciliação do CEJUSC.

O projeto implementa um fluxo de dados em camadas, utilizando **Python, Pandas, Delta Lake, dbt e DuckDB**, com uma aplicação **Streamlit** para visualização dos indicadores.

---

## 1. Pergunta de negócio

> **Qual é a taxa de acordos realizados nas sessões de conciliação e qual é o percentual médio de redução do valor reclamado nos acordos, por tipo de reclamação e por período?**

### Taxa de acordo

```text
Taxa de acordo = (acordos / sessões realizadas) × 100
```

São consideradas sessões realizadas:

- `ACORDO`
- `NAO_ACORDO`

Não entram no denominador:

- `AUSENTE_RECLAMANTE`
- `AUSENTE_RECLAMADO`

### Redução média do valor reclamado

```text
Redução percentual =
((valor reclamado - valor do acordo) / valor reclamado) × 100
```

O cálculo considera somente acordos com valor reclamado maior que zero e valor do acordo informado.

### Dimensões de análise

- tipo de reclamação;
- ano;
- mês;
- combinações dessas dimensões.

---

## 2. Arquitetura
```text
┌─────────────────────────────────────┐
│             FONTES                  │
│                                     │
│ reclamacoes.csv                     │
│ sessoes_conciliacao.json            │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│        INGESTÃO - PYTHON            │
│             Pandas                  │
│                                     │
│ Leitura das fontes                  │
│ Inclusão de metadados técnicos      │
│ Sem regras de negócio               │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         BRONZE - DELTA LAKE         │
│                                     │
│ Dados preservados                   │
│ Defeitos mantidos                   │
│ Histórico de versões                │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           SILVER - dbt              │
│             DuckDB                  │
│                                     │
│ Limpeza                             │
│ Tipagem                             │
│ Padronização                        │
│ Integração                          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            GOLD - dbt               │
│             DuckDB                  │
│                                     │
│ dim_tempo                           │
│ dim_tipo_reclamacao                 │
│ fato_conciliacao                    │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          CONSUMO - dbt              │
│                                     │
│ resumo_conciliacao                  │
│ indicadores_gerais                  │
│ indicadores_dashboard              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│             STREAMLIT               │
│                                     │
│ KPIs                                │
│ Gráficos                            │
│ Filtros                             │
│ Tabelas                             │
└─────────────────────────────────────┘
```
---

## 3. Tecnologias

- Python
- Pandas
- PyArrow
- Delta Lake
- `deltalake`
- dbt Core
- dbt-duckdb
- DuckDB
- Streamlit
- Plotly

---

## 4. Estrutura do projeto
```text
cejusc-data-pipeline/
│
├── app/
│   └── streamlit_app.py
│
├── data/
│   ├── raw/
│   │   ├── reclamacoes.csv
│   │   └── sessoes_conciliacao.json
│   │
│   ├── bronze/
│   │   ├── reclamacoes/
│   │   └── sessoes_conciliacao/
│   │
│   ├── silver/
│   │   └── .gitkeep
│   │
│   ├── gold/
│   │   └── .gitkeep
│   │
│   └── quarantine/
│       └── .gitkeep
│
├── src/
│   └── ...
│
├── tests/
│   ├── criar_versao_delta.py
│   ├── time_travel.py
│   └── ...
│
├── sql/
│   └── consulta_final.sql
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   │
│   ├── macros/
│   │   ├── delta_scan.sql
│   │   └── register_delta.sql
│   │
│   └── models/
│       ├── sources.yml
│       │
│       ├── silver/
│       │   ├── stg_reclamacoes.sql
│       │   ├── stg_sessoes.sql
│       │   └── schema.yml
│       │
│       ├── gold/
│       │   ├── dim_tempo.sql
│       │   ├── dim_tipo_reclamacao.sql
│       │   ├── fato_conciliacao.sql
│       │   └── schema.yml
│       │
│       └── consumo/
│           ├── resumo_conciliacao.sql
│           ├── indicadores_gerais.sql
│           ├── indicadores_dashboard.sql
│           └── schema.yml
│
├── DECISOES.md
├── README.md
├── requirements.txt
└── .gitignore
```
---

## 5. Fontes de dados

O projeto utiliza duas fontes sintéticas em formatos diferentes.

### Reclamações

Arquivo:

```text
data/raw/reclamacoes.csv
```

Formato: CSV.

Principais campos:

- `id_reclamacao`
- `id_processo`
- `data_reclamacao`
- `tipo_reclamacao`
- `valor_reclamado`
- `canal`
- `conciliador_id`
- `modalidade_preferida`

### Sessões de conciliação

Arquivo:

```text
data/raw/sessoes_conciliacao.json
```

Formato: JSON.

Principais campos:

- `id_sessao`
- `id_reclamacao`
- `data_sessao`
- `resultado`
- `valor_acordo`
- `parcelas`
- `tempo_sessao_minutos`
- `observacao`

As fontes são sintéticas e não contêm dados pessoais reais.

---

## 6. Defeitos presentes nas fontes

Foram inseridas inconsistências propositalmente para simular dados reais.

### CSV

Exemplos:

```text
Cobrança indevida
cobranca indevida
COBRANÇA INDEVIDA
```

Também existem:

- valor ausente;
- número decimal utilizando vírgula;
- variações de nomenclatura.

### JSON

Exemplos:

```text
Não Acordo
NAO_ACORDO
```

Também existem:

- data em formato `dd/mm/YYYY`;
- número de parcelas armazenado como texto;
- valor de acordo utilizando vírgula decimal.

Esses defeitos são preservados na Bronze e corrigidos/padronizados posteriormente na Silver.

---

## 7. Preservação dos dados

A camada `Raw` representa os arquivos de origem.

A camada `Bronze` preserva os dados recebidos sem aplicar regras de negócio ou correções de conteúdo.

São adicionados somente metadados técnicos necessários ao controle da ingestão, como:

- arquivo de origem;
- momento da ingestão;
- posição do registro.

Isso permite auditoria, rastreabilidade, reprocessamento e demonstração de Time Travel.

---

## 8. Ingestão

A ingestão é realizada em Python utilizando Pandas.

```bash
python -m src.pipeline
```

O processo:

1. lê o CSV;
2. lê o JSON;
3. adiciona metadados técnicos;
4. grava os dados na camada Bronze;
5. utiliza Delta Lake para armazenamento.

A ingestão não implementa regras de negócio.

---

## 9. Bronze — Delta Lake

Estrutura:

```text
data/bronze/
├── reclamacoes/
└── sessoes_conciliacao/
```

Cada tabela Delta possui seu próprio histórico de versões.

Estado atual:

```text
reclamacoes
versão atual: 8

sessoes_conciliacao
versão atual: 5
```

As versões não precisam possuir o mesmo número, pois cada tabela possui seu próprio histórico transacional.

---

## 10. Silver

A camada Silver é construída pelo dbt e materializada no DuckDB.

### `stg_reclamacoes`

Responsabilidades:

- converter datas;
- converter valores monetários;
- tratar separador decimal;
- padronizar tipos de reclamação;
- remover espaços desnecessários;
- preservar valores ausentes;
- manter metadados de origem.

Exemplo:

```text
Cobrança indevida
cobranca indevida
COBRANÇA INDEVIDA
```

passam a representar:

```text
cobranca_indevida
```

### `stg_sessoes`

Responsabilidades:

- converter datas;
- padronizar resultado;
- converter valores monetários;
- converter parcelas para inteiro;
- converter duração para inteiro;
- preservar valores ausentes.

Exemplo:

```text
Não Acordo
```

é padronizado para:

```text
NAO_ACORDO
```

---

## 11. Gold

### Escolha entre estrela e tabela larga

Foi escolhido o modelo dimensional em estrela porque a pergunta
possui recortes por período e tipo de reclamação.

A separação entre fato e dimensões evita repetir atributos de
dimensões na fato e facilita a expansão futura da análise para
outras dimensões, como conciliador ou canal.

Uma tabela larga seria possível, mas aumentaria a repetição de
atributos e misturaria diferentes responsabilidades no mesmo modelo.

### `dim_tempo`

Granularidade:

> Uma linha representa um dia do calendário utilizado pelas sessões.

Campos:

```text
data_sk
data
ano
mes
nome_mes
```

### `dim_tipo_reclamacao`

Granularidade:

> Uma linha representa um tipo de reclamação padronizado.

### `fato_conciliacao`

Granularidade:

> Uma linha representa uma sessão de conciliação associada a uma reclamação.

Principais campos:

```text
sessao_id
reclamacao_id
data_sessao_sk
tipo_reclamacao_sk
conciliador_id
resultado
valor_reclamado
valor_acordo
parcelas
tempo_sessao_minutos
sessao_realizada
houve_acordo
```

Regras:

```text
Sessão realizada:
ACORDO       → 1
NAO_ACORDO   → 1
AUSENTE_*    → 0

Acordo:
ACORDO → 1
demais → 0
```

A redução percentual não é armazenada na fato. Ela é calculada na camada de consumo.

---

## 12. Camada de consumo

A camada de consumo possui três modelos.

### `resumo_conciliacao`

Granularidade:

> Uma linha representa o resultado agregado de um mês e um tipo de reclamação.

Campos:

```text
ano
mes
nome_mes
tipo_reclamacao
sessoes_realizadas
acordos
taxa_acordo
reducao_media_percentual
```

### `indicadores_gerais`

Granularidade:

> Uma linha representa o resultado consolidado de todo o conjunto de sessões disponíveis.

Campos:

```text
sessoes_realizadas
acordos
taxa_acordo
reducao_media_percentual
```

### `indicadores_dashboard`

Modelo preparado para consumo pelo Streamlit.

Permite filtros por:

- ano;
- mês;
- tipo de reclamação;
- combinações dessas dimensões;
- total geral.

A aplicação não precisa recalcular as regras de negócio.

### O que ficou de fora

A fato não possui uma linha para cada reclamação isoladamente,
pois o foco da pergunta de negócio está nas sessões de conciliação.

Também não são armazenados na fato indicadores agregados como
taxa de acordo ou redução média, pois esses indicadores dependem
do agrupamento por período e tipo de reclamação e são calculados
na camada de Consumo.

A separação entre dimensões e fato foi escolhida porque permite
analisar as sessões por diferentes dimensões, especialmente tempo
e tipo de reclamação, sem duplicar essas informações na tabela fato.

---

## 13. Testes do dbt

São utilizados:

- `not_null`
- `unique`
- `accepted_values`
- `relationships`

Quantidade atual:

```text
36 testes de dados
```

Resultado atual:

```text
PASS=45
WARN=0
ERROR=0
SKIP=0
NO-OP=0
REUSED=0
TOTAL=45
```

O build contempla:

```text
8 modelos
1 operação
2 fontes
36 testes de dados
```

---

## 14. Delta Lake Time Travel

O projeto demonstra o histórico de versões do Delta Lake.

Estado inicial:

```text
Versão 6
120 registros
```

Foi executado um teste que adicionou:

```text
REC-TIME-TRAVEL
```

Resultado:

```text
Versão 7
121 registros
```

Posteriormente, o pipeline foi executado novamente a partir dos arquivos Raw:

```text
Versão 8
120 registros
```

Comparação:

```text
Versão 6
120 registros
REC-TIME-TRAVEL: ausente

Versão 7
121 registros
REC-TIME-TRAVEL: presente

Versão 8
120 registros
REC-TIME-TRAVEL: ausente
```

Isso demonstra que:

1. o estado atual pode ser reconstruído a partir da fonte Raw;
2. o Delta Lake mantém o histórico das versões anteriores.

---

## 15. Reprocessamento

Para reconstruir a Bronze a partir dos arquivos Raw:

```bash
python -m src.pipeline
```

Em seguida:

```bash
cd dbt
dbt build
```

O processo permite reconstruir as camadas derivadas sem alterações manuais.

---

## 16. Quarentena

A arquitetura prevê:

```text
data/quarantine/
```

Registros que não puderem ser interpretados com segurança podem ser direcionados para essa área juntamente com o motivo da rejeição.

No PoC atual, os defeitos inseridos são corrigíveis na Silver e, portanto, não existem registros efetivamente enviados para quarentena.

---

## 17. Decisões de projeto

As principais decisões estão documentadas em:

```text
DECISOES.md
```

Entre elas:

- arquitetura de armazenamento;
- granularidade da fato;
- tratamento de dados ambíguos;
- tratamento de valores ausentes;
- tratamento de registros inválidos;
- definição de sessão realizada;
- definição de acordo;
- definição dos indicadores;
- localização das regras de negócio;
- estratégia de reprocessamento.

---

## 18. Regras de negócio

A distribuição das responsabilidades é:

```text
Python
→ ingestão e metadados técnicos

Bronze
→ preservação dos dados

Silver
→ limpeza, tipagem e padronização

Gold
→ modelagem e regras necessárias

Consumo
→ cálculo dos indicadores orientados à pergunta

Streamlit
→ apresentação
```

A aplicação Streamlit consome indicadores já calculados pela camada de consumo.

---

## 19. DuckDB

O DuckDB é utilizado como banco analítico local.

Os modelos Silver, Gold e Consumo são materializados pelo dbt em:

```text
data/cejusc.duckdb
```

Os diretórios:

```text
data/silver/
data/gold/
```

servem como organização física do projeto, enquanto as tabelas analíticas são materializadas no DuckDB.

---

## 20. Resultado atual

Com os dados sintéticos atuais:
-
| Ano       | Sessões realizadas | Acordos | Taxa de acordo | Redução média |
| --------- | -----------------: | ------: | -------------: | ------------: |
| 2024      |                 28 |       8 |         28,57% |        32,32% |
| 2025      |                 29 |      10 |         34,48% |        32,18% |
| 2026      |                 28 |       9 |         32,14% |        31,11% |
| **Total** |             **85** |  **27** |     **31,76%** |    **31,87%** |

A taxa de acordo considera somente as sessões realizadas.

---

## 21. Resultado por ano

| Ano       | Sessões realizadas | Acordos | Taxa de acordo | Redução média |
| --------- | -----------------: | ------: | -------------: | ------------: |
| 2024      |                 28 |       8 |         28,57% |        32,32% |
| 2025      |                 29 |      10 |         34,48% |        32,18% |
| 2026      |                 28 |       9 |         32,14% |        31,11% |
| **Total** |             **85** |  **27** |     **31,76%** |    **31,87%** |


---

## 22. Resultado por tipo de reclamação

| Tipo de reclamação      | Sessões realizadas | Acordos | Taxa de acordo | Redução média |
| ----------------------- | -----------------: | ------: | -------------: | ------------: |
| cancelamento de serviço |                 18 |       7 |         38,89% |        30,30% |
| cobranca_indevida       |                 27 |       6 |         22,22% |        33,33% |
| falha_servico           |                 19 |       7 |         36,84% |        25,78% |
| problema contratual     |                 21 |       7 |         33,33% |        38,26% |


---

## 23. Consulta final

A consulta utilizada para responder à pergunta de negócio está em:

```text
sql/consulta_final.sql
```

Ela consulta a camada de consumo e não acessa diretamente os dados Raw.

A consulta final apenas seleciona os indicadores já calculados na camada de Consumo. Não contém regras de negócio, filtros de negócio ou cálculos de métricas.

---

## 24. Dashboard

A aplicação Streamlit está em:

```text
app/streamlit_app.py
```

O dashboard apresenta:

- título;
- filtros;
- cards de indicadores;
- gráficos;
- tabela detalhada.

Os filtros permitem analisar:

- ano;
- mês;
- tipo de reclamação.

Os indicadores são obtidos da camada:

```text
indicadores_dashboard
```

A aplicação não recalcula as regras de negócio.

---

## 25. Execução

### Instalação

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Instalação das dependências:

```bash
pip install -r requirements.txt
```

### Ingestão

Na raiz do projeto:

```bash
python -m src.pipeline
```

### dbt

```bash
cd dbt
dbt build
```

### Dashboard

Na raiz do projeto:

```bash
streamlit run app/streamlit_app.py
```

---

## 26. Documentação do dbt

Gerar documentação:

```bash
cd dbt
dbt docs generate
```

Executar servidor:

```bash
dbt docs serve
```

A documentação permite visualizar:

- modelos;
- fontes;
- testes;
- descrições;
- dependências;
- lineage.

---

## 27. Time Travel

Criar uma nova versão:

```bash
python tests/criar_versao_delta.py
```

Consultar o histórico:

```bash
python tests/time_travel.py
```

A demonstração compara a versão atual com a anterior e verifica a presença do registro utilizado no teste.

---

## 28. Repositório

O projeto deve conter:

```text
Código do pipeline
README.md
DECISOES.md
Fontes ou instruções para geração das fontes
Modelos dbt
Testes
Scripts de Time Travel
Dashboard
Histórico Delta
```

Não são utilizados dados pessoais reais.

---

## 29. Critérios de aceite

O projeto deve ser capaz de ser reconstruído a partir de um clone limpo.

Fluxo esperado:

```bash
python -m src.pipeline
```

seguido de:

```bash
cd dbt
dbt build
```

O resultado esperado é a reconstrução das camadas analíticas sem necessidade de intervenção manual.

---

## 30. Apresentação

Sugestão de roteiro:

### 1. Pergunta de negócio

Apresentar a pergunta definida no projeto.

### 2. Fontes

Mostrar:

```text
CSV
JSON
```

e os defeitos propositalmente inseridos.

### 3. Pipeline

Demonstrar:

```text
Raw
 ↓
Python
 ↓
Bronze / Delta
 ↓
Silver / dbt
 ↓
Gold / dbt
 ↓
Consumo
 ↓
Streamlit
```

### 4. dbt

Executar:

```bash
dbt build
```

e demonstrar os testes passando.

### 5. Lineage

Mostrar o DAG de dependências dos modelos.

### 6. Delta Time Travel

Demonstrar:

```text
Versão 6 → 120 registros
Versão 7 → 121 registros
Versão 8 → 120 registros
```

e consultar:

```text
REC-TIME-TRAVEL
```

### 7. DECISOES.md

Apresentar pelo menos duas decisões importantes:

- granularidade da fato;
- tratamento do dado ambíguo;
- tratamento de registros inválidos;
- definição de sessão realizada.

### 8. Resultado

Apresentar:

```text
85 sessões realizadas
27 acordos
31,76% de taxa de acordo
31,87% de redução média
```

### 9. Significado para o negócio

A partir dos dados sintéticos atuais:

- aproximadamente 31,76% das sessões realizadas resultaram em acordo;
- os acordos apresentaram redução média de aproximadamente 31,87% sobre o valor reclamado;
- a análise pode ser detalhada por tipo de reclamação e período.

---

## 31. Estado da documentação

Esta documentação representa o estado consolidado do projeto em **setembro de 2026**.

Os resultados numéricos apresentados neste README correspondem aos dados sintéticos atualmente presentes no projeto.

Alterações futuras nas fontes, regras de transformação ou dados podem alterar os resultados apresentados.
