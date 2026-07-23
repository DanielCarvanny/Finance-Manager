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


def inicializar_banco_de_dados():
    if os.path.exists(CAMINHO_DB_PLANO):
        logger.warning(
            "Banco em texto plano encontrado após possível encerramento inesperado. "
            "Usando-o para recuperar as alterações mais recentes."
        )
    elif os.path.exists(CAMINHO_DB_ENC):
        # Descriptografa o banco criptografado (se existir) antes de conectar
        descriptografar_banco(CAMINHO_DB_ENC, CAMINHO_DB_PLANO)

    # Inicializa as tabelas
    base.Base.metadata.create_all(bind=engine)
    migrar_colunas_lixeira(engine)

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


def migrar_colunas_lixeira(engine_alvo=None) -> None:
    """Adiciona as colunas de lixeira aos bancos existentes sem recriar tabelas.

    A migração atua somente no banco em texto plano da sessão. A cópia
    criptografada permanece intacta até um encerramento normal e bem-sucedido.
    """
    engine_migracao = engine_alvo or engine
    inspetor = inspect(engine_migracao)

    if 'movimentacao' not in inspetor.get_table_names():
        return

    colunas_existentes = {
        coluna['name'] for coluna in inspetor.get_columns('movimentacao')
    }
    comandos = []
    if 'excluida' not in colunas_existentes:
        comandos.append(
            "ALTER TABLE movimentacao "
            "ADD COLUMN excluida BOOLEAN NOT NULL DEFAULT 0"
        )
    if 'excluida_em' not in colunas_existentes:
        comandos.append(
            "ALTER TABLE movimentacao ADD COLUMN excluida_em DATETIME"
        )

    indices_existentes = {indice['name'] for indice in inspetor.get_indexes('movimentacao')}
    if 'idx_mov_excluida' not in indices_existentes:
        comandos.append(
            "CREATE INDEX IF NOT EXISTS idx_mov_excluida "
            "ON movimentacao (excluida)"
        )

    if not comandos:
        return

    try:
        with engine_migracao.begin() as conexao:
            for comando in comandos:
                conexao.execute(text(comando))
    except Exception:
        logger.error(
            "Falha ao migrar as colunas de lixeira. O banco criptografado não foi alterado.",
            exc_info=True,
        )
        raise

    logger.info("Migração da lixeira concluída com sucesso.")


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
