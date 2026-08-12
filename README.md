# 📊 Finance Manager — InterFIN Local

> Gerenciador financeiro pessoal desktop construído em Python com **CustomTkinter**, **SQLAlchemy**, **Alembic** e **Matplotlib**.
> Importa extratos bancários, categoriza movimentações automaticamente por regras de palavras-chave, gerencia lixeira com proteção de estornos e exibe um dashboard interativo.

---

## ✨ Funcionalidades

- 📥 **Importação Extensível (Strategy Pattern)** — Processa extratos bancários CSV com validação estrutural e deduplicação por assinatura única.
- 🏷️ **Classificação Automática** — Categoriza lançamentos por palavras-chave (ex: *"RESTAURANTE"* $\rightarrow$ Alimentação, *"UBER"* $\rightarrow$ Transporte).
- 🔄 **Reclassificação Manual** — Altere a categoria de qualquer lançamento diretamente na tabela com recálculo instantâneo dos indicadores.
- 🗑️ **Sistema de Lixeira (Soft Delete)** — Arquive e restaure lançamentos com proteção que obriga a seleção conjunta de estornos vinculados.
- 📊 **Dashboard Interativo** — Filtragem dinâmica por Mês e Ano:
  - Cards de Resumo: Receitas, Despesas, Saldo do Período e Gasto Médio Diário.
  - Gráfico Donut: Distribuição de Gastos por Categoria.
  - Gráfico de Barras: Comparativo de Receitas vs Despesas (visão anual).
  - Gráfico de Linha: Evolução Mensal de Gastos.
- 🔒 **Criptografia Fernet (AES-256)** — Proteção do banco SQLite em repouso ao encerrar o aplicativo.
- 🛠️ **Migrações Automáticas (Alembic)** — Versionamento de schema de banco integrado no startup do aplicativo.

---

## 🏗️ Arquitetura do Sistema

O projeto adota uma **Arquitetura em 4 Camadas (Clean Architecture)** com o padrão **MVVM** na camada de apresentação:

```
finance-manager/
├── alembic/                         # Versionamento de schema de banco (Alembic)
├── docs/                            # Documentação técnica do projeto
│   ├── arquitetura_v2.md            # Arquitetura em 4 camadas
│   ├── design_patterns.md           # Padrões Repository, Unit of Work, Strategy, MVVM
│   ├── migracoes_alembic.md         # Guia técnico do Alembic
│   ├── estrutura_projeto.md         # Árvore completa de diretórios
│   ├── Visao_Geral.md               # Visão geral do sistema
│   └── roadmap.md                   # Roadmap de desenvolvimento
│
├── main.py                          # Ponto de entrada da aplicação
├── gerador_de_tema.py               # Utilitário para gerar o tema visual
├── requirements.txt                 # Dependências do projeto
│
├── src/
│   ├── domain/                      # CAMADA 1: DOMÍNIO
│   │   ├── models/                  # Entidades SQLAlchemy (Movimentacao, Categoria, etc.)
│   │   └── exceptions.py            # Exceções de negócio desacopladas
│   │
│   ├── infrastructure/              # CAMADA 2: INFRAESTRUTURA
│   │   ├── database/                # Conexão SQLite, UnitOfWork e Seed
│   │   ├── repositories/            # Repository Pattern (Queries centralizadas)
│   │   └── importacao/              # Sub-módulos Parsers, Validators e Normalizers
│   │
│   ├── application/                 # CAMADA 3: APLICAÇÃO / SERVIÇOS
│   │   ├── importacao/              # Strategy Pattern para Extratos (EstrategiaCSVInter)
│   │   ├── classificador_service.py
│   │   ├── analisador_service.py
│   │   ├── resumo_service.py
│   │   └── movimentacao_service.py
│   │
│   └── ui/                          # CAMADA 4: APRESENTAÇÃO (MVVM)
│       ├── views/                   # Janelas CustomTkinter (app.py)
│       ├── viewmodels/              # ViewModels DTO (Dashboard, Importação, Lixeira)
│       └── components/              # Tabela, Cards, Gráficos, Filtros, Lixeira
│
└── tests/                           # Suíte de Testes Automatizados (pytest)
    ├── conftest.py                  # Fixtures SQLite em memória
    ├── test_movimentacao_repository.py
    ├── test_categoria_repository.py
    ├── test_classificador.py
    ├── test_estrategia_csv_inter.py
    ├── test_dashboard_viewmodel.py
    ├── test_importacao_viewmodel.py
    └── test_lixeira_viewmodel.py
```

---

## 🛠️ Pré-requisitos e Instalação

- **Python 3.10+**
- Instalação das dependências do `requirements.txt`:

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/finance-manager.git
cd finance-manager

# 2. Crie e ative o ambiente virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Gere o tema visual (executado uma única vez)
python gerador_de_tema.py

# 5. Execute a aplicação
python main.py
```

---

## 🧪 Execução de Testes Automatizados

A suíte de testes utiliza banco SQLite isolado em memória (`sqlite:///:memory:`) e mocks de serviços para testar todas as camadas do sistema:

```bash
# Executar todos os testes com saída detalhada
python -m pytest tests/ -v --tb=short

# Executar medição de cobertura de código
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 📦 Empacotamento e Distribuição

O aplicativo pode ser empacotado como um executável autônomo para Windows (`.exe`) sem necessidade de instalação prévia do Python.

- **PyInstaller**: Utilizado para empacotar o ambiente Python, código-fonte e dependências em um executável standalone.
- **Inno Setup**: Utilizado para gerar o instalador com assistente de instalação (`FinanceManager_Setup_v1.0.exe`).

---

## 🔒 Segurança e Criptografia dos Dados

- **Criptografia Fernet (AES-256)**: Ao fechar o aplicativo pelo botão "X", o arquivo do banco `finance_manager.db` é automaticamente encriptado como `finance_manager.db.enc`.
- A chave de descriptografia é gerada no primeiro uso em:
  ```
  %APPDATA%\FinanceManager\secret.key
  ```

> ⚠️ **Importante**: Nunca compartilhe ou exclua a sua `secret.key`. Sem ela, o banco encriptado não poderá ser lido.

---

## 📜 Créditos e Agradecimentos

- **Inno Setup**: O instalador do sistema foi construído utilizando a ferramenta **Inno Setup** (Copyright © 1997-2026 Jordan Russell / Martijn Laan). Agradecemos aos criadores pelo excelente software de instalação open-source.
- **CustomTkinter**: Interface gráfica moderna desenvolvida com a biblioteca CustomTkinter de Tom Schimansky.

