import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Garante que a pasta 'src' esteja no sys.path para resolução de imports
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if caminho_src not in sys.path:
    sys.path.insert(0, caminho_src)

# Importa o Base com todas as entidades registradas e as configurações de conexão
from domain.models import Base
from infrastructure.database.conexao import DATABASE_URL, engine

# Objeto de configuração do Alembic (lido a partir do alembic.ini)
config = context.config

# Interpreta o arquivo de configuração de log do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Define o target_metadata para suporte a autogenerate das migrações
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'.

    Configura o contexto apenas com uma URL de banco e não com uma Engine.
    Chamadas para context.execute() enviam a string dada para a saída da migração.
    """
    url = config.get_main_option("sqlalchemy.url", DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Necessário para alteração de tabelas no SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migrações no modo 'online'.

    Neste cenário criamos uma Engine e associamos uma conexão ao contexto.
    """
    # Usa a engine existente do projeto ou cria a partir da URL
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Suporte completo para migrações em SQLite (ALTER TABLE)
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
