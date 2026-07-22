# Estrutura do Projeto — Sistema de Organização Financeira
## Arquitetura em Camadas

O sistema segue o padrão de arquitetura em camadas, onde cada camada tem uma responsabilidade bem definida:

┌─────────────────────────────────────────┐
│              UI (CustomTkinter)         │  ← Apresentação: telas, gráficos, eventos
├─────────────────────────────────────────┤
│           Controller (main.py)          │  ← Orquestração: liga UI aos serviços
├─────────────────────────────────────────┤
│              Service (services/)        │  ← Lógica de negócio: importar, classificar, analisar
├─────────────────────────────────────────┤
│           Repository (models/)          │  ← Acesso a dados: SQLAlchemy ORM
├─────────────────────────────────────────┤
│              SQLite (database/)         │  ← Persistência: banco de dados local
└─────────────────────────────────────────┘

### Responsabilidade de Cada Camada

| Camada | O que faz | O que NÃO faz |
|--------|-----------|---------------|
| **UI** | Exibe dados, captura eventos do usuário, desenha gráficos | Não acessa banco direto, não calcula indicadores |
| **Controller** | Inicia a aplicação, conecta eventos da UI aos serviços | Não contém regras de negócio |
| **Service** | Valida CSV, classifica movimentações, calcula estatísticas | Não acessa banco direto, não renderiza telas |
| **Repository** | Consulta, insere, atualiza e deleta no banco via SQLAlchemy | Não contém regras de negócio |
| **SQLite** | Armazena e recupera dados fisicamente | Não toma decisões |

---

## Estrutura de Pastas
sistema_financeiro/
│
├── venv/                          # Ambiente virtual Python (não versionado)
│
├── src/                           # Código fonte principal
│   ├── __init__.py
│   │
│   ├── models/                    # Camada Repository — Classes SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                # Base declarativa (DeclarativeBase)
│   │   ├── importacao.py          # Tabela importacao
│   │   ├── movimentacao.py        # Tabela movimentacao
│   │   ├── categoria.py           # Tabela categoria
│   │   ├── palavra_chave.py       # Tabela palavra_chave
│   │   └── resumo_mensal.py       # Tabela resumo_mensal
│   │
│   ├── database/                  # Configuração de conexão com o banco
│   │   ├── __init__.py
│   │   ├── conexao.py             # Engine, Session, create_all
│   │   └── seed.py                # Dados iniciais (categorias e palavras-chave)
│   │
│   ├── services/                  # Camada Service — Lógica de negócio
│   │   ├── __init__.py
│   │   ├── importador.py          # Leitura e validação do CSV
│   │   ├── classificador.py       # Categorização automática
│   │   ├── analisador.py          # Cálculo de indicadores financeiros
│   │   └── resumo_service.py      # Geração e consulta de resumos mensais
│   │
│   └── ui/                        # Camada UI — Interface gráfica
│       ├── __init__.py
│       ├── app.py                 # Janela principal (CustomTkinter)
│       ├── components/
│       │   ├── __init__.py
│       │   ├── tabela.py          # Tabela de movimentações
│       │   ├── graficos.py        # Gráficos com Matplotlib
│       │   ├── filtros.py         # Dropdowns de período
│       │   └── importacao_ui.py   # Tela de importação de CSV
│       └── estilos.py             # Cores, fontes e temas
│
├── data/                          # Arquivos de extrato para teste
│   └── extrato-exemplo.csv
│
├── docs/                          # Documentação do projeto
│   ├── Modelagem/
│   │   ├── Modelo_Dominio.md          # Entidades, atributos e relacionamentos
│   │   └── Banco_Dados.md             # Documentação técnica das tabelas
│   ├── Requisitos/
│   │   ├── Dados_de_Entrada.md        
│   │   ├── Escopo.md
│   │   ├── Regras_Negocio.md
│   │   ├── Requisitos_Funcionais.md
│   │   └── Requisitos_Nao_Funcionais.md
│   ├── estrutura_projeto.md       # Este documento
│   ├── Visao_Geral.md
│   └── roadmap.md                 # Roadmap de desenvolvimento
│
├── tests/                         # Testes automatizados (Fase 8)
│   ├── __init__.py
│   ├── test_importador.py
│   ├── test_classificador.py
│   └── test_analisador.py
│
├── requirements.txt               # Dependências do projeto
├── README.md                      # Documentação para GitHub
├── main.py                    # Camada Controller — Ponto de entrada
└── .gitignore                     # Arquivos ignorados pelo Gi

---

## Dependências (requirements.txt)
# Banco de Dados
sqlalchemy>=2.0

# Manipulação de Dados
pandas>=2.0

# Interface Gráfica
customtkinter>=5.2

# Gráficos
matplotlib>=3.7

# Empacotamento (apenas na Fase 9)
pyinstaller>=6.

---

## Fluxo de Dados

### Importação de CS
Arquivo CSV (data/)
    ↓
importador.py (lê e valida com Pandas)
    ↓
Lista de dicionários (dados validados)
    ↓
classificador.py (atribui categoria via PalavraChave)
    ↓
Objetos Movimentacao (models)
    ↓
conexao.py (sessão SQLAlchemy)
    ↓
SQLite (persistência)

### Exibição no Dashboard
SQLite
    ↓
analisador.py (consulta via SQLAlchemy)
    ↓
Dicionário de indicadores
    ↓
ui/graficos.py (Matplotlib)
    ↓
ui/app.py (CustomTkinter)
    ↓
Tela do usuário

---

## Convenções de Código

| Regra | Exemplo |
|-------|---------|
| Nomes de arquivos: snake_case | `palavra_chave.py` |
| Nomes de classes: PascalCase | `class PalavraChave(Base):` |
| Nomes de funções: snake_case | `def calcular_total():` |
| Nomes de variáveis: snake_case | `total_receitas = 0` |
| Constantes: UPPER_SNAKE_CASE | `CATEGORIAS_PADRAO = [...]` |
| Docstrings em todas as funções | `"""Retorna o total de despesas do mês."""` |
| Tipagem estática (type hints) | `def importar(caminho: str) -> list[dict]:` |