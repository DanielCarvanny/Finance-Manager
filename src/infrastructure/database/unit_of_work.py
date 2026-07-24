from sqlalchemy.orm import Session
from infrastructure.database.conexao import SessionLocal
from infrastructure.repositories.movimentacao_repo import MovimentacaoRepository
from infrastructure.repositories.categoria_repo import CategoriaRepository
from infrastructure.repositories.resumo_repo import ResumoMensalRepository
from infrastructure.repositories.palavra_chave_repo import PalavraChaveRepository
from utils.logger import logger
from typing import Optional

class UnitOfWork:
    """
    Gerenciador de transações que garante que múltiplos repositórios
    compartilhem a mesma sessão e transação do SQLAlchemy.
    """
    def __init__(self, session_factory=SessionLocal):
        self._factory = session_factory
        self._session: Optional[Session] = None

    def __enter__(self):
        # 1. Abre a sessão com o banco de dados
        self._session = self._factory()

        # 2. Instancia todos os repositórios compartilhando a MESMA sessão
        self.movimentacoes = MovimentacaoRepository(self._session)
        self.categorias = CategoriaRepository(self._session)
        self.resumos = ResumoMensalRepository(self._session)
        self.palavras_chave = PalavraChaveRepository(self._session)

        return self

    def commit(self):
        """Confirma permanentemente todas as alterações realizadas no bloco."""
        if self._session:
            self._session.commit()

    def rollback(self):
        """Desfaz todas as alterações realizadas se houver erro."""
        if self._session:
            self._session.rollback()
            
    @property
    def session(self) -> Session:
        """Expõe a sessão ativa de forma controlada. Lança erro se chamado fora de um bloco 'with'."""
        if self._session is None:
            raise RuntimeError("UnitOfWork não está ativo. Use-o dentro de um bloco 'with UnitOfWork() as uow'.")
        return self._session
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Executado automaticamente ao sair do bloco 'with'.
        Se houve exceção (exc_type != None), faz rollback automático e fecha a sessão.
        """
        try:
            if exc_type is not None:
                logger.warning(f"Exceção detectada durante a transação ({exc_val}). Realizando rollback.")
                self.rollback()
        finally:
            if self._session:
                self._session.close()