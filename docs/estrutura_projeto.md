# Estrutura do Projeto — Finance Manager v2.0

## Arquitetura em 4 Camadas (Clean / Layered Architecture)

O sistema segue uma arquitetura em 4 camadas bem delimitadas, implementando o padrão **MVVM** na camada de apresentação e **Repository + Unit of Work** na persistência:

```
┌──────────────────────────────────────────────────────────┐
│              UI / APRESENTAÇÃO (MVVM)                    │
│   src/ui/views/app.py                                    │
│   src/ui/viewmodels/ (Dashboard, Importação, Lixeira)    │
│   src/ui/components/ (Cards, Tabela, Gráficos, Filtros)  │
├──────────────────────────────────────────────────────────┤
│              APLICAÇÃO / SERVIÇOS                        │
│   src/application/ (Importacao, Classificador, etc.)     │
├──────────────────────────────────────────────────────────┤
│              INFRAESTRUTURA                              │
│   src/infrastructure/database/ (Conexão, UnitOfWork)    │
│   src/infrastructure/repositories/ (Repositories)        │
│   src/infrastructure/importacao/ (Parsers/Validators)  │
├──────────────────────────────────────────────────────────┤
│              DOMÍNIO                                     │
│   src/domain/models/ (Movimentacao, Categoria, etc.)     │
│   src/domain/exceptions.py (Exceções de Negócio)         │
└──────────────────────────────────────────────────────────┘
```

---

## Árvore Completa de Diretórios do Repositório

```
finance-manager/
├── alembic/                         # Versionamento de schema do banco de dados (Alembic)
│   ├── versions/                    # Scripts de revisão/migração
│   ├── env.py                       # Conexão do Alembic aos Models SQLAlchemy
│   └── script.py.mako
├── alembic.ini                      # Configuração do Alembic
│
├── main.py                          # Ponto de entrada da aplicação
├── gerador_de_tema.py               # Utilitário para gerar o tema da UI (Dark Mode)
├── requirements.txt                 # Dependências do projeto
│
├── src/                             # Código-fonte principal em 4 camadas
│   ├── domain/                      # CAMADA 1: DOMÍNIO
│   │   ├── models/                  # Entidades SQLAlchemy (Mapeamento ORM)
│   │   │   ├── base.py
│   │   │   ├── categoria.py
│   │   │   ├── importacao.py
│   │   │   ├── movimentacao.py
│   │   │   ├── palavra_chave.py
│   │   │   └── resumo_mensal.py
│   │   └── exceptions.py            # Exceções desacopladas de regras de negócio
│   │
│   ├── infrastructure/              # CAMADA 2: INFRAESTRUTURA
│   │   ├── database/                # Persistência e Transações
│   │   │   ├── conexao.py           # Conexão SQLite, Fernet AES-256 e Alembic
│   │   │   ├── unit_of_work.py      # Pattern Unit of Work (Context Manager)
│   │   │   └── seed.py              # Carga inicial de dados
│   │   ├── repositories/            # Pattern Repository (Acesso ao Banco)
│   │   │   ├── base.py              # BaseRepository[T] Genérico
│   │   │   ├── categoria_repo.py
│   │   │   ├── movimentacao_repo.py
│   │   │   ├── palavra_chave_repo.py
│   │   │   └── resumo_repo.py
│   │   └── importacao/              # Sub-módulos de Leitura de Extratos
│   │       ├── parsers/             # Extratores de formato (CSVParser)
│   │       ├── validators/          # Validações físicas e colunas (InterValidator)
│   │       └── normalizers/         # Limpeza e parsing de valores (ExtratoNormalizer)
│   │
│   ├── application/                 # CAMADA 3: APLICAÇÃO / SERVIÇOS
│   │   ├── importacao/              # Orquestração de Importação (Strategy Pattern)
│   │   │   ├── importacao_service.py
│   │   │   └── strategies/          # Estratégias por banco (EstrategiaCSVInter)
│   │   ├── classificador_service.py # Categorização automática por palavras-chave
│   │   ├── analisador_service.py    # Cálculos e distribuições de gráficos
│   │   ├── resumo_service.py        # Consolidação de resumos mensais
│   │   └── movimentacao_service.py  # Gestão de lixeira, estornos e categorias
│   │
│   └── ui/                          # CAMADA 4: APRESENTAÇÃO (MVVM)
│       ├── views/
│       │   └── app.py               # Janela Principal CustomTkinter
│       ├── viewmodels/              # Camada ViewModel (Exposição de DTOs)
│       │   ├── dashboard_view_model.py
│       │   ├── importacao_view_model.py
│       │   └── lixeira_view_model.py
│       ├── components/              # Componentes de Interface
│       │   ├── cards.py
│       │   ├── filtros.py
│       │   ├── graficos.py
│       │   ├── lixeira.py
│       │   └── tabela.py
│       └── theme.json               # Tema visual Dark Mode
│
├── tests/                           # Suíte de Testes Automatizados (pytest)
│   ├── conftest.py                  # Fixtures globais SQLite em memória
│   ├── test_movimentacao_repository.py
│   ├── test_categoria_repository.py
│   ├── test_classificador.py
│   ├── test_estrategia_csv_inter.py
│   ├── test_dashboard_viewmodel.py
│   ├── test_importacao_viewmodel.py
│   └── test_lixeira_viewmodel.py
│
├── docs/                            # Documentação Técnica do Projeto
│   ├── arquitetura_v2.md            # Arquitetura em 4 camadas
│   ├── design_patterns.md           # Padrões Repository, UoW, Strategy, MVVM
│   ├── migracoes_alembic.md         # Guia do Alembic
│   ├── estrutura_projeto.md         # Este arquivo
│   ├── Visao_Geral.md               # Visão geral do sistema
│   └── roadmap.md                   # Roadmap de desenvolvimento
│
└── logs/                            # Arquivos de Log da Aplicação
    └── app.log
```