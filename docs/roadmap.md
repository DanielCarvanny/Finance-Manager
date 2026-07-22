# Roadmap — Sistema de Organização Financeira

## Fase 1 — Descoberta (Análise)

### 1.1 — Definição do Escopo ✅
- Objetivo: Importar extratos, classificar, analisar e visualizar finanças
- Limitações: Apenas Banco Inter, uso local, usuário único
- Funcionalidades: 5 principais (Importação, Processamento, Classificação, Análise, Visualização)

### 1.2 — Análise do Extrato (Banco Inter)
- Data (Date, Obrigatório)
- Descrição (String, Obrigatório)
- Valor (Decimal, Obrigatório)
- Saldo (Decimal, Obrigatório)
- Período do Extrato (extraído do arquivo)

### 1.3 — Regras de Negócio ✅

#### Regras Financeiras
- PIX recebido é receita
- PIX enviado é despesa
- Estorno deve ser associado à movimentação original
- Transferências entre contas próprias não contam como gasto (futuro)

#### Regras de Categorização
- Categorias obrigatórias: Alimentação, Transporte, Lazer, Moradia, Saúde, Investimentos, Sem categoria
- Categorização por palavras-chave na descrição
- Movimentação sem correspondência recebe "Sem categoria"
- Usuário pode alterar categoria manualmente (persistente)

#### Regras de Dados
- Movimentação não pode ser duplicada (mesma data + descrição + valor)
- Toda movimentação deve ter categoria
- Valor não pode ser nulo ou zero
- Data deve ser válida
- Saldo deve ser numérico
- Categoria não pode ser excluída se tiver movimentações vinculadas
- Permitir múltiplas importações preservando histórico

#### Regras de Análise
- Gasto total do mês (somatório de todos os valores)
- Gasto médio diário do período
- Total por categoria com identificação de maior/menor gasto
- Evolução mensal dos gastos no ano
- Saldo do período
- Percentual de gastos e recebimentos por categoria

#### Regras de Interface
- Dropdown com meses/anos para filtrar análises
- Gráficos atualizados conforme filtro selecionado
- Visualização de movimentações em tabela

---

## Fase 2 — Modelagem

### 2.1 — Modelagem do Domínio ✅
Entidades definidas:
- Extrato (Importacao)
- Movimentacao
- Categoria
- PalavraChave
- ResumoMensal

Atributos, tipos e relacionamentos documentados.
Ver documentação completa em: docs/Modelo_Dominio.md

### 2.2 — Banco de Dados ✅
DER e documentação técnica concluídos:
- 5 tabelas com colunas, tipos, constraints e índices
- Mapeamento Domínio → SQL → SQLAlchemy
- Índices de performance e unicidade
- Dados iniciais (seed) para categorias e palavras-chave

Ver documentação completa em: docs/Banco_Dados.md

### 2.3 — Arquitetura do Sistema ✅
Camadas definidas:
- UI (CustomTkinter) — Apresentação
- Controller — Orquestração da interface
- Service — Lógica de negócio (importação, classificação, análise)
- Repository/DAO — Acesso a dados (SQLAlchemy)
- SQLite — Persistência

Tecnologias por camada:
- UI: CustomTkinter, Matplotlib
- Service: Pandas (leitura CSV), Python puro (regras)
- Repository: SQLAlchemy ORM
- Database: SQLite (arquivo local)

Estrutura de pastas definida em: docs/estrutura_projeto.md

---

## Fase 3 — Protótipo (Importação sem BD)
- Selecionar arquivo CSV
- Ler com Pandas
- Exibir dados no terminal/tela simples
- Validar estrutura do arquivo

---

## Fase 4 — Persistência
- Implementar models SQLAlchemy
- Criar banco SQLite
- Popular tabelas a partir do CSV
- Garantir que não haja duplicatas

---

## Fase 5 — Classificação
### 5.1 — Classificação Básica
- Percorrer palavras-chave cadastradas
- Buscar correspondência na descrição da movimentação
- Atribuir categoria correspondente
- Fallback: "Sem categoria"

### 5.2 — Cadastro de Regras
- Interface para adicionar palavra-chave
- Vincular a uma categoria existente
- Definir tipo (receita/despesa/ambos)

### 5.3 — Aprendizado Interativo (futuro)
- Sistema pergunta categoria para movimentações não classificadas
- Salva regra automaticamente
- Nunca mais pergunta para o mesmo padrão

---

## Fase 6 — Estatísticas
- Cálculo de indicadores (totais, médias, percentuais)
- Armazenamento em ResumoMensal
- Identificação de categorias dominantes
- Comparação mensal

---

## Fase 7 — Dashboard
- Interface com CustomTkinter
- Tabela de movimentações com filtros
- Gráficos com Matplotlib (pizza, barras, linha)
- Dropdown de período (mês/ano)
- Atualização dinâmica

---

## Fase 8 — Refatoração
- Revisão de código
- Testes unitários (importação, classificação, cálculos)
- Documentação de código (docstrings)
- Tratamento de erros robusto

---

## Fase 9 — Versão 1.0
- Empacotamento com PyInstaller (Windows/Linux)
- README.md completo
- Manual de uso
- Tag v1.0 no GitHub

---

## Evolução Futura (v1.1+)
- OCR para PDF
- Suporte a outros bancos
- Classificação por IA/ML
- Metas e objetivos financeiros
- Comparação entre meses/anos
- Previsão de gastos
- Importação automática via API

---
## Status Atual do Projeto

✅ Fase 1 (Descoberta): 100% concluída
✅ Fase 2.1 (Modelagem do Domínio): 100% concluída
✅ Fase 2.2 (Banco de Dados): 100% concluída (documentação pronta)
✅ Fase 2.3 (Arquitetura): 100% concluída
✅ Fase 3 (Protótipo): 100% concluída
✅ Fase 4 (Persistência): 100% concluída
✅ Fase 5 (Classificação): 100% concluída
✅ Fase 6 (UI): 100% concluída
🔄 Fase 7 (Estatísticas): Pendente
⏳ Fase 8 (Dashboard): Pendente
⏳ Fase 9 (Refatoração): Pendente
⏳ Fase 10 (Versão 1.0): Pendente
