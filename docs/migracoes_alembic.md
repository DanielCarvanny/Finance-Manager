# Guia de Migrações de Banco de Dados com Alembic — Finance Manager v2.0

> Manual técnico sobre o versionamento de schema de banco de dados utilizando Alembic.

---

## 💡 Por que o Alembic foi Adotado?

Na v1.0, alterações de estrutura de banco (schema) eram feitas manualmente via script ou comandos raw `ALTER TABLE` no arquivo `conexao.py`. Isso gerava inconsistências, falhas de sincronização e impossibilidade de rollback.

Com o **Alembic**, todas as alterações de schema do banco de dados são versionadas em scripts Python dentro da pasta `alembic/versions/`.

---

## 📁 Estrutura de Arquivos do Alembic

```
finance-manager/
├── alembic.ini                    # Arquivo de configuração global do Alembic
└── alembic/
    ├── env.py                     # Script de ambiente que conecta o Alembic aos Models SQLAlchemy
    ├── script.py.mako             # Template para geração de novas migrações
    └── versions/                  # Pasta contendo os arquivos de revisão versionados
        └── 2026_07_20_..._inicial.py
```

---

## ⚙️ Execução Automática na Inicialização

O sistema **não exige** que o usuário final execute comandos CLI para aplicar as migrações. A função `inicializar_banco()` no arquivo `src/infrastructure/database/conexao.py` executa o upgrade automaticamente na inicialização do aplicativo:

```python
from alembic.config import Config
from alembic import command

alembic_cfg = Config("alembic.ini")
alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
command.upgrade(alembic_cfg, "head")
```

---

## 🛠️ Comandos CLI para Desenvolvedores

Ao alterar qualquer modelo SQLAlchemy em `src/domain/models/`, o desenvolvedor deve gerar e aplicar uma nova migração.

### 1. Gerar uma Nova Migração Autogerada
```bash
alembic revision --autogenerate -m "descricao_da_alteracao"
```
O Alembic compara os modelos Python em `src/domain/models/` com a estrutura atual do banco SQLite e gera um novo script em `alembic/versions/`.

### 2. Aplicar Migrações Pendentes
```bash
alembic upgrade head
```
Aplica todas as migrações até a versão mais recente.

### 3. Reverter a Última Migração (Rollback)
```bash
alembic downgrade -1
```
Reverte a versão do schema em 1 passo.

### 4. Verificar o Histórico de Versões
```bash
alembic history --verbose
```
Lista todas as revisões aplicadas e pendentes.
