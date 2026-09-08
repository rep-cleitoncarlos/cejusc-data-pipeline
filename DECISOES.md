# Decisões de Arquitetura e Dados

## 1. Arquitetura de armazenamento

O pipeline utiliza uma arquitetura em camadas:

- `data/raw`: arquivos CSV e JSON recebidos das fontes.
- `data/bronze`: dados preservados em Delta Lake.
- `dbt/Silver`: dados tratados, tipados e padronizados.
- `dbt/Gold`: modelo dimensional para análise.
- `dbt/Consumo`: modelo orientado à pergunta de negócio.

A ingestão é realizada em Python com Pandas.

As transformações analíticas são realizadas com dbt e DuckDB.

O Delta Lake foi utilizado na camada Bronze para permitir
versionamento e Time Travel dos dados.

### Justificativa

A separação em camadas permite preservar os dados originais,
isolar as transformações e facilitar a reexecução do pipeline.

A Bronze mantém os dados próximos ao formato original, enquanto
Silver e Gold concentram o tratamento e a modelagem necessários
para análise.

---

## 2. Granularidade da fato

A tabela `fato_conciliacao` possui a seguinte granularidade:

> Uma linha representa uma sessão de conciliação associada a uma reclamação.

Essa granularidade foi escolhida porque a pergunta de negócio
analisa os resultados das sessões de conciliação e seus valores
de acordo.

Cada sessão possui uma reclamação associada por meio de
`id_reclamacao`.

A chave da sessão (`sessao_id`) é única na fato.

---

## 3. Tratamento de dado ambíguo

Foi identificado que o tipo de reclamação apresentava diferentes
representações para o mesmo conceito.

Exemplos encontrados nas fontes:

- `Cobrança indevida`
- `cobranca indevida`
- `COBRANÇA INDEVIDA`

Também foram identificadas variações para falha na prestação
do serviço:

- `Falha no servico`
- `Falha na prestação de serviço`

### Decisão

Essas representações foram consideradas equivalentes e
padronizadas para valores canônicos:

- `cobranca_indevida`
- `falha_servico`

A decisão de equivalência pertence ao domínio de negócio
do CEJUSC/TJMS.

O pipeline apenas implementa tecnicamente essa decisão de
padronização.

Essa regra está documentada e implementada na camada Silver,
não na ingestão.

---

## 4. Tratamento de valores ausentes

Foi identificado um registro com `valor_reclamado` ausente:

- `REC-0013`

Esse registro possui resultado `NAO_ACORDO`.

### Decisão

O valor ausente não é preenchido artificialmente.

O valor permanece `NULL` na camada analítica.

Como o registro não possui acordo, ele não participa do cálculo
de redução percentual.

O registro permanece disponível na fato para preservar a
informação da sessão.

---

## 5. Registros inválidos

A Bronze preserva os registros exatamente como recebidos, inclusive
registros que apresentem defeitos de formato ou inconsistências.

Durante a transformação para a Silver, os dados são tratados conforme
regras de limpeza e padronização documentadas nos modelos dbt. Defeitos
que puderem ser corrigidos com segurança permanecem no fluxo normal do
pipeline.

Quando um registro não puder ser interpretado ou corrigido com segurança,
ele deverá ser direcionado para `data/quarantine/`, juntamente com a
identificação do motivo da rejeição, para análise da qualidade dos dados.

A quarentena não substitui a Bronze. A Bronze continua sendo a cópia
histórica dos dados recebidos e preserva os dados originais para auditoria
e eventual reprocessamento.

Neste PoC, os defeitos introduzidos nas fontes são corrigíveis pelas regras
de transformação da Silver. Portanto, não há registros efetivamente
direcionados para a quarentena.

---

## 6. Definição de sessão realizada

Para responder à pergunta de negócio, foi adotada a seguinte
definição:

Uma sessão é considerada realizada quando o resultado é:

- `ACORDO`
- `NAO_ACORDO`

Uma sessão não é considerada realizada quando o resultado é:

- `AUSENTE_RECLAMANTE`
- `AUSENTE_RECLAMADO`

Essa decisão é necessária para definir o denominador da taxa
de acordos.

---

## 7. Definição de acordo

Uma sessão possui acordo quando:

```text
resultado = ACORDO