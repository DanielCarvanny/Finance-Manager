## 1. Mapeamento de Tipos: Domínio → SQL → SQLAlchemy

| Modelo de Domínio | Tipo SQL (SQLite) | Tipo SQLAlchemy | Exemplo |
|-------------------|-------------------|-----------------|---------|
| inteiro | `INTEGER` | `Integer` | `id` |
| texto | `VARCHAR(255)` ou `TEXT` | `String(255)` ou `Text` | `descricao` |
| data | `DATE` | `Date` | `data_lancamento` |
| data/hora | `DATETIME` | `DateTime` | `data_importacao` |
| decimal | `DECIMAL(10,2)` | `Numeric(10,2)` | `valor` |
| "receita" ou "despesa" | `VARCHAR(8)` | `String(8)` | `tipo` |

---

## 2. Documentação Técnica por Tabela

### 📄 Tabela: `importacao` (antes chamada Extrato)

> **Nota:** Renomeei de "Extrato" para "`importacao`" seguindo a convenção de nomear tabelas pelo que representam no banco, não pelo conceito físico.

| Coluna                | Restrições                                   | Tipo                           | Observação                  |
| --------------------- | -------------------------------------------- | ------------------------------ | --------------------------- |
| `id`                  | `PRIMARY KEY`, `AUTOINCREMENT`               | `Integer, primary_key=True`    | Identificador único         |
| `nome_arquivo`        | `NOT NULL`                                   | `String(255), nullable=False`  | Nome original do CSV        |
| `data_importacao`     | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP`      | `DateTime, default=func.now()` | Momento exato da importação |
| `periodo_inicio`      | `NOT NULL`                                   | `Date, nullable=False`         | Data inicial do extrato     |
| `periodo_fim`         | `NOT NULL`                                   | `Date, nullable=False`         | Data final do extrato       |
| `status`              | `NOT NULL`, `CHECK (IN ('sucesso', 'erro'))` | `String(20), nullable=False`   | Resultado da importação     |
| `total_movimentacoes` | `NOT NULL`, `CHECK (>= 0)`                   | `Integer, nullable=False`      | Quantidade de registros     |

**Índices:**
- `idx_importacao_data` em `(data_importacao)` — Para consultar importações recentes
- `idx_importacao_status` em `(status)` — Para filtrar importações com erro

**Regras de Negócio Cobertas:**
- ✅ Rastreia histórico de importações (cada arquivo gera um registro)
- ✅ Permite identificar e reprocessar arquivos com erro (`status = 'erro'`)
- ✅ Armazena período para validação de dados

---

### 📄 Tabela: `movimentacao`

| Coluna            | Restrições                                      | Tipo                                                   | Observação                             |
| ----------------- | ----------------------------------------------- | ------------------------------------------------------ | -------------------------------------- |
| `id`              | `PRIMARY KEY`, `AUTOINCREMENT`                  | `Integer, primary_key=True`                            | Identificador único                    |
| `data_lancamento` | `NOT NULL`                                      | `Date, nullable=False`                                 | Data da transação                      |
| `descricao`       | `NOT NULL`                                      | `String(255), nullable=False`                          | Descrição original do banco            |
| `valor`           | `NOT NULL`, `CHECK (valor != 0)`                | `Numeric(10,2), nullable=False`                        | Positivo = receita, Negativo = despesa |
| `saldo`           | —                                               | `Numeric(10,2)`                                        | Saldo após transação                   |
| `tipo`            | `NOT NULL`, `CHECK (IN ('receita', 'despesa'))` | `String(8), nullable=False`                            | Calculado na importação                |
| `estorno_id`      | `REFERENCES movimentacao(id)`                   | `Integer, ForeignKey('movimentacao.id')`               | Vincula estorno à original             |
| `importacao_id`   | `NOT NULL`, `REFERENCES importacao(id)`         | `Integer, ForeignKey('importacao.id'), nullable=False` | Origem do dado                         |
| `categoria_id`    | `NOT NULL`, `REFERENCES categoria(id)`          | `Integer, ForeignKey('categoria.id'), nullable=False`  | Classificação                          |

**Índices:**
- `idx_mov_data` em `(data_lancamento)` — Acelera filtros por período
- `idx_mov_categoria` em `(categoria_id)` — Acelera agrupamentos por categoria
- `idx_mov_tipo` em `(tipo)` — Acelera totais de receita/despesa
- `idx_mov_importacao` em `(importacao_id)` — Rastreia origem dos dados
- **`uq_mov_deduplicacao`** em `(data_lancamento, descricao, valor, saldo)` — **Índice único que impede duplicatas (usando o saldo para diferenciar transações idênticas no mesmo dia)!**

**Regras de Negócio Cobertas:**
- ✅ `uq_mov_deduplicacao` impede a mesma transação duas vezes
- ✅ `CHECK (valor != 0)` garante que não há transação zerada
- ✅ `CHECK (tipo IN (...))` só aceita receita ou despesa
- ✅ `estorno_id` permite rastrear estornos
- ✅ `NOT NULL` nos campos obrigatórios

---

### 📄 Tabela: `categoria`

| Coluna      | Restrições                     | Tipo                                       | Observação               |
| ----------- | ------------------------------ | ------------------------------------------ | ------------------------ |
| `id`        | `PRIMARY KEY`, `AUTOINCREMENT` | `Integer, primary_key=True`                | Identificador único      |
| `nome`      | `NOT NULL`, `UNIQUE`           | `String(100), unique=True, nullable=False` | Nome da categoria        |
| `cor`       | `DEFAULT '#808080'`            | `String(7), default='#808080'`             | Hex da cor para gráficos |
| `descricao` | —                              | `Text`                                     | Detalhamento opcional    |

**Índices:**
- `uq_categoria_nome` em `(nome)` — **Índice único** (já coberto pelo `UNIQUE`)

**Regras de Negócio Cobertas:**
- ✅ `UNIQUE` no nome evita categorias duplicadas
- ✅ Cor padrão cinza para categorias sem cor definida

**Dados Iniciais (Seed):**
```python
CATEGORIAS_PADRAO = [
    {"nome": "Alimentação", "cor": "#FF6384", "descricao": "Restaurantes, mercado, delivery"},
    {"nome": "Transporte", "cor": "#36A2EB", "descricao": "Combustível, ônibus, metrô, apps"},
    {"nome": "Lazer", "cor": "#FFCE56", "descricao": "Cinema, streaming, viagens, jogos"},
    {"nome": "Moradia", "cor": "#4BC0C0", "descricao": "Aluguel, condomínio, contas de casa"},
    {"nome": "Saúde", "cor": "#9966FF", "descricao": "Farmácia, consultas, plano de saúde"},
    {"nome": "Investimentos", "cor": "#FF9F40", "descricao": "Ações, renda fixa, cripto"},
    {"nome": "Sem categoria", "cor": "#C9CBCF", "descricao": "Movimentações não classificadas"},
]
```

---

### 📄 Tabela: `palavra_chave`

| Coluna              | Restrições                                   | Tipo                                                  | Observação                   |
| ------------------- | -------------------------------------------- | ----------------------------------------------------- | ---------------------------- |
| `id`                | `PRIMARY KEY`, `AUTOINCREMENT`               | `Integer, primary_key=True`                           | Identificador único          |
| `texto`             | `NOT NULL`                                   | `String(100), nullable=False`                         | Palavra buscada na descrição |
| `tipo_movimentacao` | `CHECK (IN ('receita', 'despesa', 'ambos'))` | `String(8)`                                           | Refina busca por tipo        |
| `categoria_id`      | `NOT NULL`, `REFERENCES categoria(id)`       | `Integer, ForeignKey('categoria.id'), nullable=False` | Categoria alvo               |

**Índices:**
- `idx_palavra_categoria` em `(categoria_id)` — Busca palavras de uma categoria
- **`uq_palavra_texto`** em `(texto, tipo_movimentacao)` — **Índice único: mesma palavra + mesmo tipo não se repete**

**Dados Iniciais Sugeridos:**
```python
PALAVRAS_CHAVE_INICIAIS = [
    # Alimentação
    {"texto": "RESTAURANTE", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "MERCADO", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "IFOOD", "tipo": "despesa", "categoria": "Alimentação"},
    
    # Transporte
    {"texto": "UBER", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "POSTO", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "ESTACIONAMENTO", "tipo": "despesa", "categoria": "Transporte"},
    
    # Receitas
    {"texto": "PIX RECEBIDO", "tipo": "receita", "categoria": "Receita"},
    {"texto": "SALARIO", "tipo": "receita", "categoria": "Receita"},
    {"texto": "TRANSFERENCIA RECEBIDA", "tipo": "receita", "categoria": "Receita"},
]
```

---

### 📄 Tabela: `resumo_mensal`

| Coluna                     | Restrições                     | Tipo                                  | Observação                  |
| -------------------------- | ------------------------------ | ------------------------------------- | --------------------------- |
| `id`                       | `PRIMARY KEY`, `AUTOINCREMENT` | `Integer, primary_key=True`           | Identificador único         |
| `ano`                      | `NOT NULL`                     | `Integer, nullable=False`             | Ano de referência           |
| `mes`                      | `NOT NULL`, `CHECK (1-12)`     | `Integer, nullable=False`             | Mês de referência           |
| `total_receitas`           | `DEFAULT 0`                    | `Numeric(12,2), default=0`            | Soma de receitas            |
| `total_despesas`           | `DEFAULT 0`                    | `Numeric(12,2), default=0`            | Soma de despesas (positivo) |
| `saldo_periodo`            | `DEFAULT 0`                    | `Numeric(12,2), default=0`            | Receitas - Despesas         |
| `gasto_medio_diario`       | —                              | `Numeric(10,2)`                       | Despesas / dias do mês      |
| `categoria_maior_gasto_id` | `REFERENCES categoria(id)`     | `Integer, ForeignKey('categoria.id')` | Categoria com mais gasto    |
| `categoria_menor_gasto_id` | `REFERENCES categoria(id)`     | `Integer, ForeignKey('categoria.id')` | Categoria com menos gasto   |

**Índices:**
- **`uq_resumo_ano_mes`** em `(ano, mes)` — **Índice único: um resumo por mês**
- `idx_resumo_maior_cat` em `(categoria_maior_gasto_id)`
- `idx_resumo_menor_cat` em `(categoria_menor_gasto_id)`

**Regras de Negócio Cobertas:**
- ✅ `uq_resumo_ano_mes` garante um registro por mês
- ✅ `CHECK` impede mês inválido
- ✅ FKs permitem navegar para detalhes da categoria

---

## 3. Diagrama de Relacionamentos Final

```
┌─────────────────┐
│   importacao    │
│  (extratos)     │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐       ┌────────────-──┐
│  movimentacao   │──────►│   categoria   │
│                 │  N:1  │               │
│  estorno_id ────┘       └───────┬───────┘
└─────────────────┘               │ 1
                                  │
                                  │ N
                          ┌───────▼───────┐
                          │ palavra_chave │
                          └───────────────┘

┌─────────────────┐       ┌──────────────┐
│  resumo_mensal  │──────►│   categoria   │
│                 │  N:1  │ (maior/menor) │
└─────────────────┘       └──────────────┘
```

---

## 4. Checklist de Validação (Antes de Codar)
 - Toda tabela tem PK autoincremento (id)
 - Toda FK está declarada como NOT NULL quando obrigatória
 - Constraints CHECK implementam regras de negócio
 - Índices únicos impedem duplicatas
 - Índices de busca cobrem filtros frequentes (data, categoria)
 - ON DELETE não definido = comportamento padrão RESTRICT (não deixa deletar)
 - Dados iniciais (seed) documentados para categorias e palavras-chave