from infrastructure.repositories.base import BaseRepository
from domain.models.categoria import Categoria 
from typing import Optional, List

class CategoriaRepository(BaseRepository[Categoria]):
    def __init__(self, session):
        super().__init__(session,Categoria)

    def buscar_por_nome(self, nome: str) -> Optional[Categoria]:
        return self._session.query(Categoria).filter(Categoria.nome == nome).first()

    def listar_todas(self) -> List[Categoria]:
        return self.get_all()
    
    def buscar_por_id(self, id: int)-> Optional[Categoria]:
            return self.get_by_id(id)