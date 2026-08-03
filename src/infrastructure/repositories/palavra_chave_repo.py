from infrastructure.repositories.base import BaseRepository
from domain.models.categoria import Categoria
from domain.models.palavra_chave import PalavraChave 
from typing import List
from sqlalchemy.orm import joinedload

class PalavraChaveRepository(BaseRepository[PalavraChave]):
    def __init__(self, session):
        super().__init__(session,PalavraChave)

    def listar_com_categorias(self) -> List[PalavraChave]:
        return (
            self._session.query(PalavraChave)
            .options(joinedload(PalavraChave.categoria))
            .all()
        )