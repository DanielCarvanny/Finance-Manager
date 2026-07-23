from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from domain.models.base import Base

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    """
    Repositório genérico reutilizável com operações básicas de CRUD.
    """
    def __init__(self, session: Session, model_cls: Type[T]):
        self._session = session
        self._model_cls = model_cls

    def create(self, entidade: T) -> T:
        """Cria uma nova entidade no banco de dados."""
        self._session.add(entidade)
        return entidade

    def create_all(self, entidades: List[T]) -> List[T]:
        """Cria várias entidades no banco de dados."""
        self._session.add_all(entidades)
        return entidades

    def get_by_id(self, id_entidade: int)-> Optional[T]:
        """Retorna uma entidade pelo seu ID."""
        return self._session.get(self._model_cls, id_entidade)

    def get_all(self) -> List[T]:
        """Retorna todas as entidades do modelo."""
        return self._session.query(self._model_cls).all()

    def delete(self, entidade: T) -> None:
        """Exclui uma entidade do banco de dados."""
        self._session.delete(entidade)