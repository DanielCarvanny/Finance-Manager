
## Objetos:

```
- Extrato
- Movimentacao
- Categoria
- ResumoMensal
- PalavraChave
```
Representam o domínio financeiro do sistema.
### Perguntas:

#### `Extrato`
**O que é um Extrato?**
> É o arquivo que fornecerá os dados utilizados para montar as tabelas de dados e realizar os cálculos para análise.


**Quais informações ela possui?**

|      Atributo       |   Tipo    |        Descrição        |     Regra de Negócio      |
| :-----------------: | :-------: | :---------------------: | :-----------------------: |
|         id          |  inteiro  |   Identificador único   |  Gerado automaticamente   |
|    nome_arquivo     |   texto   |  Nome do CSV original   | Ex: "extrato-2025-01.csv" |
|   data_importacao   | data/hora |  Momento da importação  |    Registro automático    |
|   periodo_inicio    |   data    | Data inicial do extrato |      Extraído do CSV      |
|     periodo_fim     |   data    |  Data final do extrato  |      Extraído do CSV      |
|       status        |   texto   |   "sucesso" ou "erro"   |   Para rastrear falhas    |
| total_movimentacoes |  inteiro  | Quantidade de registros |      Para validação       |

---
#### `Movimentacao`
**O que é uma Movimentação?**
> Representa uma transação financeira importada do extrato.

**Quais informações ela possui?**

|    Atributo     |  Tipo   | Descrição                                             | Regra de Negócio                 |
| :-------------: | :-----: | :---------------------------------------------------- | :------------------------------- |
|       id        | inteiro | Identificador único                                   | Nunca se repete                  |
| data_lancamento |  data   | Data que ocorreu a movimentação                       | Obrigatória e válida             |
|    descricao    |  texto  | Descrição original do banco                           | Ex: "PIX ENVIADO - MERCADO PAGO" |
|      valor      | decimal | Valor da transação                                    | Não pode ser nulo                |
|      saldo      | decimal | Saldo após transação                                  | Numérico                         |
|      tipo       |  texto  | "receita" ou "despesa"                                | Calculado automaticamente        |
|   estorno_id    | inteiro | ID da movimentação original (nulo se não for estorno) | Pode ser nulo                    |
|   extrato_id    | inteiro | FK para Extrato                                       |                                  |
|  categoria_id   | inteiro | FK para Categoria                                     |                                  |
|    excluida     | booleano | Indica se a movimentação está na lixeira             | Padrão: `false`                  |
|   excluida_em   | data/hora | Momento do arquivamento                              | Nulo enquanto estiver ativa      |

**Relacionamentos:**
- Pertence a **1 Extrato** (Muitas `Movimentacoes` → 1 `Extrato`)    
- Pertence a **1 Categoria** (Obrigatório)    
- Pode estar vinculada a **1 `Movimentacao`** como **estorno** (`autorrelacionamento`)

**Arquivamento (lixeira):**
- Movimentações arquivadas não aparecem na interface padrão e não participam de indicadores, gráficos ou resumos.
- Elas permanecem armazenadas para que o usuário possa restaurá-las pela lixeira.

---
#### Categoria
**O que é uma Categoria?**
> Representa uma classificação de um tipo específico dada a movimentações com informações em comum.

**Quais informações ela possui?**

| Atributo  |  Tipo   |       Descrição       |    Regra de Negócio     |
| :-------: | :-----: | :-------------------: | :---------------------: |
|    id     | inteiro |  Identificador único  | Gerado automaticamente  |
|   Nome    |  texto  |   Nome da categoria   |    Ex: "Alimentação"    |
|    cor    |  texto  |   Cor para gráficos   |      Ex: "#FF5733"      |
| descricao |  texto  | Detalhamento opcional | Para o usuário entender |

**Relacionamentos:**
- Possui muitas **`Movimentacao`** (1 Categoria → N `Movimentacoes`)
- Possui muitas **`PalavraChave`** (1 Categoria → N `PalavraChave`)    
- **Não pode ser excluída** se houver movimentações vinculadas

---
#### `PalavraChave`
**O que é uma Palavra Chave?**
> Representa uma regra de categorização automática.

**Quais informações ela possui?**

|     Atributo      |  Tipo   |       Descrição        |    Regra de Negócio    |
| :---------------: | :-----: | :--------------------: | :--------------------: |
|        id         | inteiro |  Identificador único   | Gerado automaticamente |
|       texto       |  texto  | Palavra a ser buscada  | "UBER", "PIX ENVIADO"  |
| tipo_movimentacao |  texto  | "receita" ou "despesa" |   Para refinar busca   |
|   categoria_id    | inteiro |  Categoria vinculada   |   FK para Categoria    |

---
#### `ResumoMensal`
**O que é um Resumo Mensal?**
> É a análise dos cálculos estatísticos que serão feitos pelo sistema para serem apresentados para a análise do usuário.

**Quais informações ela possui?**

|         Atributo         |  Tipo   |          Descrição           |
| :----------------------: | :-----: | :--------------------------: |
|            id            | inteiro |     Identificador único      |
|           ano            | inteiro |      Ano de referência       |
|           mes            | inteiro |   Mês de referência (1-12)   |
|      total_receitas      | decimal |       Soma de receitas       |
|      total_despesas      | decimal |       Soma de despesas       |
|      saldo_periodo       | decimal |     Receitas - Despesas      |
|    gasto_medio_diario    | decimal | Total despesas / dias do mês |
| categoria_maior_gasto_id | inteiro |      FK para Categoria       |
| categoria_menor_gasto_id | inteiro |      FK para Categoria       |
