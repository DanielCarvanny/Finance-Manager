import os
import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from domain.models import base, categoria, importacao, movimentacao, palavra_chave
from domain.models import resumo_mensal
from infrastructure.database import seed
from contextlib import contextmanager
from utils.logger import logger
from infrastructure.security.security import descriptografar_banco, criptografar_banco
from alembic.config import Config
from alembic import command

# ---------------------------------------------------------------------------
# Caminhos de dados — sempre em %APPDATA%\FinanceManager\ para garantir
# acesso de escrita tanto ao rodar como script quanto como .exe empacotado.
# ---------------------------------------------------------------------------
PASTA_DADOS = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "FinanceManager",
)
os.makedirs(PASTA_DADOS, exist_ok=True)

CAMINHO_DB_PLANO = os.path.join(PASTA_DADOS, 'finance_manager.db')
CAMINHO_DB_ENC   = os.path.join(PASTA_DADOS, 'finance_manager.db.enc')

DATABASE_URL = f"sqlite:///{CAMINHO_DB_PLANO}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def executar_migracoes_alembic():
    """Executa automaticamente as migrações do Alembic para manter o schema atualizado."""
    try:
        caminho_projeto = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        caminho_ini = os.path.join(caminho_projeto, 'alembic.ini')
        caminho_migrations = os.path.join(caminho_projeto, 'src', 'infrastructure', 'database', 'migrations')

        alembic_cfg = Config(caminho_ini)
        alembic_cfg.set_main_option('script_location', caminho_migrations)

        # Se a tabela 'movimentacao' já existe (banco v1.0 pré-alembic), carimba a baseline sem tentar recriar tabelas
        inspetor = inspect(engine)
        tabelas = inspetor.get_table_names()

        if 'movimentacao' in tabelas and 'alembic_version' not in tabelas:
            logger.info("Banco de dados existente detectado. Marcando como baseline do Alembic...")
            command.stamp(alembic_cfg, 'head')
        elif 'movimentacao' not in tabelas:
            command.upgrade(alembic_cfg, 'head')

        logger.info("Migrações de banco de dados (Alembic) aplicadas com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao executar migrações do Alembic: {e}", exc_info=True)
        raise
    finally:
        # Libera qualquer conexão do Alembic antes que a aplicação abra sessões.
        engine.dispose()


def inicializar_banco_de_dados():
    if os.path.exists(CAMINHO_DB_PLANO):
        logger.warning(
            "Banco em texto plano encontrado após possível encerramento inesperado. "
            "Usando-o para recuperar as alterações mais recentes."
        )
    elif os.path.exists(CAMINHO_DB_ENC):
        # Descriptografa o banco criptografado (se existir) antes de conectar
        descriptografar_banco(CAMINHO_DB_ENC, CAMINHO_DB_PLANO)

    # Inicializa as tabelas e roda as migrações do Alembic
    base.Base.metadata.create_all(bind=engine)
    executar_migracoes_alembic()

    logger.info("Banco de dados SQLite inicializado com sucesso.")

    #  Executa o seed
    db = SessionLocal()

    try:
        seed.verificar_populacao_inicial(db)
        logger.info("Seed inicial concluída.")
    except Exception as e:
        logger.error(f"Erro ao verificar população inicial do banco: {e}", exc_info=True)
    finally:
        db.close()


def salvar_e_criptografar_banco():
    """Garante que a versão mais recente seja criptografada em disco."""
    try:
        engine.dispose()  # Libera os locks de conexões abertas no SQLite
        criptografar_banco(CAMINHO_DB_PLANO, CAMINHO_DB_ENC)
        # Apaga a cópia sem criptografia ao encerrar para não deixar rastros
        if os.path.exists(CAMINHO_DB_PLANO):
            os.remove(CAMINHO_DB_PLANO)
        logger.info("Banco de dados salvo e criptografado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criptografar o banco de dados: {e}", exc_info=True)
