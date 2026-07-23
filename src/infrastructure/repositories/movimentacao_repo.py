from infrastructure.repositories.base import BaseRepository
from domain.models.movimentacao import Movimentacao
from sqlalchemy import extract
from typing import Optional

class MovimentacaoRepository(BaseRepository[Movimentacao]):
    def __init__(self, session):
        super().__init__(session,Movimentacao)

    def listar_por_periodo(self,ano: int, mes: int)-> list[Movimentacao]:

        return self._session.query(Movimentacao).filter(
            extract('year', Movimentacao.data_lancamento) == ano,
            extract('month', Movimentacao.data_lancamento) == mes,
            Movimentacao.excluida.is_(False)
        ).all()

    def listar_excluidas(self)-> list[Movimentacao]:
        """Retorna todas as movimentações arquivadas na lixeira ordenadas pela data de exclusão."""
        return self._session.query(Movimentacao).filter(
            Movimentacao.excluida.is_(True)
            ).order_by(Movimentacao.excluida_em.desc()).all()

    def buscar_por_id(self, id: int)-> Optional[Movimentacao]:
        return self.get_by_id(id)

    def salvar_lote(self, movimentacoes: list[Movimentacao]):
        resultado = self.create_all(movimentacoes)
        return resultado

    def obter_assinaturas_existentes(self) -> set[tuple]:
        """
        Retorna um conjunto (set) de assinaturas únicas das movimentações já salvas no banco
        no formato: (data_str, descricao, valor_str, saldo_str).
        """
        existentes = self._session.query(
            Movimentacao.data_lancamento,
            Movimentacao.descricao,
            Movimentacao.valor,
            Movimentacao.saldo,
        ).filter(
            Movimentacao.excluida.is_(False)
        ).all()

        return {
            (
                str(data),
                desc,
                f"{float(valor):.2f}",
                f"{float(saldo):.2f}" if saldo is not None else "None"
            )
            for data, desc, valor, saldo in existentes
        }
