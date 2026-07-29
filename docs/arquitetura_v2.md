# Arquitetura do Sistema — Finance Manager v2.0

> Documento técnico da arquitetura em 4 camadas, desacoplamento de exceções e responsabilidades de infraestrutura.

---

## 🏛️ Visão Geral da Arquitetura em 4 Camadas

O **Finance Manager v2.0** adota o padrão de **Clean Architecture / Layered Architecture** desacoplada em 4 camadas com responsabilidades estritamente delimitadas:

```
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE APRESENTAÇÃO (UI / MVVM)          │
│   src/ui/views (App, Windows) & src/ui/components        │
│   src/ui/viewmodels (Dashboard, Importação, Lixeira)    │
└────────────────────────────┬────────────────────────────┘
                             │ DTOs (dicionários / tipos primitivos)
                             ▼
┌─────────────────────────────────────────────────────────┐
│              CAMADA DE APLICAÇÃO (Services)             │
│   src/application (Importacao, Classificador, etc.)    │
└────────────────────────────┬────────────────────────────┘
                             │ Interfaces & Transações via UnitOfWork
                             ▼
┌─────────────────────────────────────────────────────────┐
│           CAMADA DE INFRAESTRUTURA (Infrastructure)      │
│   src/infrastructure/database (Conexão, UnitOfWork)   │
│   src/infrastructure/repositories (Repositories)        │
│   src/infrastructure/importacao (Parsers/Validators)    │
└────────────────────────────┬────────────────────────────┘
                             │ Entidades & Exceções do Domínio
                             ▼
┌─────────────────────────────────────────────────────────┐
│               CAMADA DE DOMÍNIO (Domain)                │
│   src/domain/models (Movimentacao, Categoria, etc.)     │
│   src/domain/exceptions (Exceções de Regra de Negócio)  │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 Detalhamento das Camadas

### 1. Camada de Domínio (`src/domain/`)
Contém o núcleo da aplicação. **Não possui dependências de UI ou Infraestrutura**.

- **Modelos de Entidade (`src/domain/models/`)**:
  - `Base`: Base declarativa comum do SQLAlchemy (`declarative_base()`).
  - `Movimentacao`: Lançamento financeiro com suporte a estornos, flags de exclusão lógica (lixeira) e constraints financeiras.
  - `Categoria`: Categorias de despesas e receitas.
  - `Importacao`: Registro pai de lote de extratos importados.
  - `PalavraChave`: Regras de auto-classificação de lançamentos por padrões na descrição.
  - `ResumoMensal`: Indicadores consolidados por período (mês/ano).
- **Exceções Centrais do Domínio (`src/domain/exceptions.py`)**:
  - Exceções personalizadas de regra de negócio desacopladas do ORM e da UI (ex: `ImportacaoPendenteError`, `ArquivamentoEstornoError`).

---

### 2. Camada de Infraestrutura (`src/infrastructure/`)
Fornece implementações concretas para persistência, acesso ao banco e parsing de arquivos físicos.

- **Banco de Dados & Transações (`src/infrastructure/database/`)**:
  - `conexao.py`: Gerenciamento do `SQLite`, execução automática de migrações `Alembic` na inicialização e criptografia AES-256 (Fernet) em repouso.
  - `unit_of_work.py`: Context Manager (`UnitOfWork`) que gerencia a sessão SQLAlchemy e garante atomicidade transacional ("Tudo ou Nada").
  - `seed.py`: Carga inicial de categorias e palavras-chave padrão.
- **Repositórios (`src/infrastructure/repositories/`)**:
  - `BaseRepository[T]`: CRUD genérico tipado.
  - `MovimentacaoRepository`, `CategoriaRepository`, `ResumoMensalRepository`, `PalavraChaveRepository`: Consultas específicas centralizadas.
- **Processamento de Extratos (`src/infrastructure/importacao/`)**:
  - `parsers/`: Extração de dados brutos e delimitadores (`CSVParser`).
  - `validators/`: Validação de existência, integridade física e colunas (`InterValidator`).
  - `normalizers/`: Conversão de formatos numéricos, moedas e datas (`ExtratoNormalizer`).

---

### 3. Camada de Aplicação (`src/application/`)
Orquestra os casos de uso do sistema coordenando os serviços e o `UnitOfWork`.

- **`ImportacaoService`**: Orquestra leitura via Strategy Pattern, deduplicação por assinatura única e persistência em lote.
- **`ClassificadorService`**: Executa regras de auto-categorização por palavras-chave.
- **`AnalisadorService`**: Gera consultas analíticas para composição de gráficos e distribuições financeiras.
- **`ResumoService`**: Mantém atualizada a tabela de `ResumoMensal` com otimização contra recalculações desnecessárias.
- **`MovimentacaoService`**: Regras para alteração de categoria, arquivamento na lixeira com validação de estornos vinculados e restauração.

---

### 4. Camada de Apresentação (`src/ui/`)
Responsável pela experiência visual do usuário e gestão de estado de interface. **Não possui acessos diretos ao banco de dados ou SQLAlchemy**.

- **ViewModels (`src/ui/viewmodels/`)**:
  - `DashboardViewModel`: Prepara DTOs (dicionários e tipos primitivos) para a tela principal (Cards, Tabela, Gráficos).
  - `ImportacaoViewModel`: Controla o estado e mensagens amigáveis da importação de arquivos.
  - `LixeiraViewModel`: Gerencia a listagem, arquivamento e restauração de lançamentos para a janela visual da lixeira.
- **Views & Componentes (`src/ui/views/` e `src/ui/components/`)**:
  - `App` (`app.py`): Janela principal em CustomTkinter.
  - `TabelaMovimentacoes`, `FiltrosDashboard`, `PainelResumo`, `Graficos`, `JanelaLixeira`: Componentes que consomem exclusivamente DTOs fornecidos pelos ViewModels.

---

## 🔒 Fluxo Transacional e Segurança

1. **Atomicidade**: Todas as escritas utilizam `UnitOfWork` com `uow.commit()` explícito e rollback automático em caso de exceção.
2. **Criptografia Fernet**: Ao encerrar o aplicativo, o arquivo `finance_manager.db` é encriptado como `finance_manager.db.enc` usando a chave armazenada em `%APPDATA%\FinanceManager\secret.key`.
