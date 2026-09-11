# Decisões de Arquitetura e Dados

## 1. Arquitetura de armazenamento

O pipeline utiliza uma arquitetura em camadas, seguindo o modelo Medallion:

- `data/raw`: arquivos CSV e JSON recebidos das fontes.
- `data/bronze`: dados preservados em Delta Lake.
- `dbt/models/silver`: dados tratados, tipados e padronizados.
- `dbt/models/gold`: modelo dimensional para análise.
- `dbt/models/consumo`: modelos orientados à pergunta de negócio.

A ingestão é realizada em Python com Pandas.

As transformações analíticas são realizadas com dbt e DuckDB.

O Delta Lake foi utilizado na camada Bronze para permitir
versionamento e Time Travel dos dados.

### Justificativa

A separação em camadas permite preservar os dados originais,
isolar as transformações e facilitar a reexecução do pipeline.

A camada Raw representa as fontes de entrada e mantém os arquivos
originais utilizados pelo pipeline.

A Bronze preserva os dados capturados em formato Delta Lake,
mantendo os registros próximos ao formato recebido e permitindo
a recuperação de versões anteriores.

A Silver concentra os tratamentos necessários para tornar os
dados adequados ao uso analítico, como limpeza, conversão de tipos
e padronização de valores.

A Gold organiza os dados em um modelo dimensional, separando fatos
e dimensões.

A camada de Consumo contém os indicadores e agregações necessários
para responder à pergunta de negócio, evitando que a camada de
apresentação precise implementar regras de negócio.

Essa separação também permite que cada etapa seja executada e
validada de forma independente.

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

### Escolha entre estrela e tabela larga

Foi escolhido o modelo dimensional em estrela porque a análise
possui recortes por período e tipo de reclamação.

A separação entre fato e dimensões reduz a repetição de atributos
descritivos e facilita a expansão futura das análises para outras
dimensões, como conciliador ou canal.

Uma tabela larga seria possível, porém concentraria atributos
descritivos e métricas no mesmo modelo, aumentando a repetição
dos dados e misturando diferentes responsabilidades.

### O que ficou de fora

A fato não possui uma linha para cada reclamação isoladamente,
pois o foco da pergunta de negócio está nas sessões de conciliação.

Também não foi criado um fato separado exclusivamente para as
reclamações, pois os indicadores analisados dependem da ocorrência
e do resultado das sessões.

Os indicadores agregados, como taxa de acordo e redução média,
também não fazem parte da fato.

Esses indicadores são calculados na camada de Consumo, pois dependem
do agrupamento por período e tipo de reclamação.

Dessa forma, a fato mantém os dados no nível de uma sessão, enquanto
a camada de Consumo realiza as agregações necessárias para responder
à pergunta de negócio.

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

A regra adotada considera que diferenças de capitalização,
acentuação e pequenas variações textuais não representam categorias
de negócio diferentes nesses casos.

A decisão de equivalência pertence ao domínio de negócio
do CEJUSC/TJMS.

O pipeline não decide conceitualmente se duas categorias são
equivalentes. Ele apenas implementa tecnicamente a regra definida
para este PoC.

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

Essa decisão evita criar um valor financeiro que não estava
presente na fonte.

---

## 5. Registros inválidos

A Bronze preserva os registros exatamente como recebidos,
inclusive registros que apresentem defeitos de formato ou
inconsistências.

Durante a transformação para a Silver, os dados são tratados
conforme regras de limpeza e padronização documentadas nos
modelos dbt.

Defeitos que puderem ser corrigidos com segurança permanecem
no fluxo normal do pipeline.

### Destino escolhido para registros inválidos

O destino definido pela equipe para um registro que não puder
ser interpretado ou corrigido com segurança é a **quarentena**.

Nesse caso, o registro deverá ser direcionado para:

`data/quarantine/`

juntamente com a identificação do motivo da rejeição.

A escolha pela quarentena evita descartar informações que podem
ser importantes para auditoria ou correção futura.

A quarentena também permite separar registros que não possuem
qualidade suficiente para seguir para a camada Silver, sem
contaminar os dados analíticos.

A quarentena não substitui a Bronze.

A Bronze continua sendo a cópia histórica dos dados recebidos
e preserva os dados originais para auditoria e eventual
reprocessamento.

### Situação neste PoC

Neste PoC, os defeitos introduzidos propositalmente nas fontes
são corrigíveis pelas regras de transformação da Silver.

Por esse motivo, não há registros efetivamente direcionados
para a quarentena.

Caso fosse encontrado um registro cujo conteúdo não pudesse
ser interpretado ou corrigido com segurança, ele permaneceria
preservado na Bronze e seria direcionado para a quarentena,
acompanhado do motivo da rejeição.

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

A regra é aplicada na camada Gold, por meio do atributo
`sessao_realizada`, que representa tecnicamente essa classificação
para utilização pelas camadas analíticas e de consumo.

---

## 7. Definição de acordo

Uma sessão possui acordo quando:

```text
resultado = ACORDO
```
Nos demais resultados, a sessão é considerada sem acordo.

Essa definição é utilizada para determinar a quantidade de
acordos e calcular a taxa de acordo na camada de Consumo.

A classificação é realizada na camada Gold por meio do atributo
`houve_acordo`.

A consulta final e o dashboard não precisam reimplementar essa
regra, pois recebem o indicador já definido na camada analítica.

---

## 8. Definição dos indicadores

A pergunta de negócio definida para o projeto é:

> Qual é a taxa de acordos realizados nas sessões de conciliação e qual é
> o percentual médio de redução do valor reclamado nos acordos, por tipo
> de reclamação e por período?

Os indicadores utilizados são:

1. taxa de acordo;
2. percentual médio de redução do valor reclamado.

Os resultados são analisados por:

- tipo de reclamação;
- período.

### Taxa de acordo

A taxa de acordo é calculada como:

~~~text
acordos / sessões realizadas × 100
~~~

São consideradas sessões realizadas aquelas classificadas como
`ACORDO` ou `NAO_ACORDO`.

As sessões em que houve ausência do reclamante ou do reclamado
não entram no denominador.

### Redução percentual

Para cada acordo válido, a redução percentual é calculada como:

~~~text
(valor_reclamado - valor_acordo) / valor_reclamado × 100
~~~

A redução média considera somente acordos que possuem:

- `valor_reclamado` maior que zero;
- `valor_acordo` informado.

A média das reduções individuais é então utilizada para produzir
o indicador `reducao_media_percentual`.

As métricas são calculadas na camada de Consumo a partir dos dados
da fato, e não são obtidas como medidas prontas das fontes.

---

## 9. Responsabilidade das camadas

As responsabilidades foram separadas da seguinte forma:

### Raw

Responsável por disponibilizar as fontes originais utilizadas
pelo pipeline.

### Bronze

Responsável por preservar os dados recebidos, incluindo seus
defeitos e metadados de ingestão.

Não possui regras de negócio.

### Silver

Responsável pela limpeza, tipagem, conversão de formatos e
padronização dos dados.

As regras de tratamento são documentadas nos modelos dbt.

### Gold

Responsável pela modelagem analítica e pela aplicação das
classificações necessárias ao modelo de fatos e dimensões.

Exemplos:

- definição de sessão realizada;
- definição de ocorrência de acordo.

### Consumo

Responsável por produzir os indicadores orientados à pergunta
de negócio.

A camada de apresentação apenas consulta os indicadores
previamente calculados e aplica filtros de apresentação.

Dessa forma, as regras de negócio não ficam implementadas
diretamente no dashboard ou na consulta final utilizada para
apresentação.

---

## 10. Versionamento e Time Travel

A camada Bronze utiliza Delta Lake para preservar diferentes
versões dos dados.

O pipeline possui mais de uma versão registrada da tabela
`reclamacoes`.

A demonstração de Time Travel utiliza duas versões consecutivas
da tabela:

- uma versão anterior;
- a versão atual.

Para evidenciar a diferença entre os estados, foi utilizado o
registro técnico `REC-TIME-TRAVEL`, criado exclusivamente para
a demonstração do versionamento.

Esse registro não pertence às fontes originais do projeto e não
representa um dado de negócio do CEJUSC.

Na demonstração:

~~~text
Versão anterior → REC-TIME-TRAVEL existe
Versão atual    → REC-TIME-TRAVEL não existe
~~~

A mesma consulta de contagem também é executada nas duas versões,
demonstrando que o Delta Lake permite recuperar o estado anterior
da tabela.

O registro técnico utilizado para a demonstração não participa
da resposta da pergunta de negócio.