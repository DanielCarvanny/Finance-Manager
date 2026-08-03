from infrastructure.repositories.base import BaseRepository
from domain.models.movimentacao import Movimentacao
from domain.models.categoria import Categoria
from sqlalchemy import extract, func, distinct
from typing import Optional
import datetime

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
        
    def listar_excluidas_por_ids(self, ids: list[int])-> list[Movimentacao]:
        """Retorna movimentações na lixeira filtradas por uma lista de IDs."""
        if not ids:
            return []
        return self._session.query(Movimentacao).filter(
            Movimentacao.id.in_(ids),
            Movimentacao.excluida.is_(True)
        ).all()

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
    
    def listar_por_categoria(self, categoria_id: int) -> list[Movimentacao]:
        """Retorna todas as movimentações ativas pertencentes a uma categoria."""
        return self._session.query(Movimentacao).filter(
            Movimentacao.categoria_id == categoria_id,
            Movimentacao.excluida.is_(False)
        ).all()
        
    def listar_estornos_ativos(self, ids_selecionados: set[int]) -> list[Movimentacao]:
        """Retorna todas as movimentações com estornos ativos."""
        if not ids_selecionados:
            return []
        return self._session.query(Movimentacao).filter(
            Movimentacao.estorno_id.in_(ids_selecionados),
            Movimentacao.excluida.is_(False),
        ).all()
        
    def listar_movimentacoes_por_ids(self, ids: list[int]) -> list[Movimentacao]:
        """Retorna movimentações ativas filtradas por uma lista de IDs."""
        if not ids:
            return []
        return self._session.query(Movimentacao).filter(
                Movimentacao.id.in_(ids),
                Movimentacao.excluida.is_(False)
            ).all()
        
    def listar_movimentacoes_ativas(self) -> list[Movimentacao]:
            """Retorna uma lista de movimentações ativas."""
            return self._session.query(Movimentacao).filter(
                    Movimentacao.excluida.is_(False)
                ).all()
            
    def calcular_total_receitas(self, ano: Optional[int]= None, mes: Optional[int]=None) -> float:
        """Calcula o somatório de todas as receitas ativas (opcionalmente filtrado por ano/mês)."""

        query = self._session.query(
            func.coalesce(func.sum(Movimentacao.valor), 0.0)
        ).filter(
            Movimentacao.tipo == 'receita',
            Movimentacao.excluida.is_(False)
        )
        if ano and mes:
            query = query.filter(
                extract('year', Movimentacao.data_lancamento) == ano,
                extract('month', Movimentacao.data_lancamento) == mes
            )
        
        # scalar() retorna diretamente o float do SUM (ou 0.0 se não houver registros)
        return float(query.scalar() or 0.0)
    
    def calcular_total_despesas(self, ano: Optional[int]= None, mes: Optional[int]=None) -> float:
        """Calcula o somatório de todas as despesas ativas (opcionalmente filtrado por ano/mês)."""

        query = self._session.query(
            func.coalesce(func.sum(Movimentacao.valor), 0.0)
        ).filter(
            Movimentacao.tipo == 'despesa',
            Movimentacao.excluida.is_(False)
        )
        if ano and mes:
            query = query.filter(
                extract('year', Movimentacao.data_lancamento) == ano,
                extract('month', Movimentacao.data_lancamento) == mes
            )
        
        # scalar() retorna diretamente o float do SUM (ou 0.0 se não houver registros)
        return abs(float(query.scalar() or 0.0))
    
    def calcular_categoria_com_maior_gasto(self, ano: Optional[int]= None, mes: Optional[int]=None) -> list[tuple[int, float]]:
        """"""
        query = self._session.query(
            Movimentacao.categoria_id,
            func.sum(Movimentacao.valor).label('total_gastos') 
        ).filter(
            Movimentacao.tipo == 'despesa', 
            Movimentacao.excluida.is_(False)
        ).group_by(Movimentacao.categoria_id)
        
        if ano and mes:
            query = query.filter(
                extract('year', Movimentacao.data_lancamento) == ano,
                extract('month', Movimentacao.data_lancamento) == mes
            )
        
        return query.order_by(func.sum(Movimentacao.valor).asc()).first()
    
    def calcular_categoria_com_menor_gasto(self, ano: Optional[int]= None, mes: Optional[int]=None) -> list[tuple[int, float]]:
        """"""
        query = self._session.query(
            Movimentacao.categoria_id,
            func.sum(Movimentacao.valor).label('total_gastos') 
        ).filter(
            Movimentacao.tipo == 'despesa', 
            Movimentacao.excluida.is_(False)
        ).group_by(Movimentacao.categoria_id)
        
        if ano and mes:
            query = query.filter(
                extract('year', Movimentacao.data_lancamento) == ano,
                extract('month', Movimentacao.data_lancamento) == mes
            )
        
        return query.order_by(func.sum(Movimentacao.valor).desc()).first()
    
    def buscar_total_de_gastos_por_categoria(self,ano: Optional[int]= None, mes: Optional[int]=None) -> list[tuple[str, float]]:
        """"""
        query = self._session.query(
            Categoria.nome, func.sum(Movimentacao.valor)
            ).join(Movimentacao.categoria).filter(
                Movimentacao.tipo == 'despesa',
                Movimentacao.excluida.is_(False)).group_by(Categoria.nome)
        
        if ano and mes:
            query = query.filter(
                extract('year', Movimentacao.data_lancamento) == ano,
                extract('month', Movimentacao.data_lancamento) == mes
            )
        
        return query.all()
    
    def listar_totais_despesas_por_mês_do_ano(self, ano: int) -> list[tuple[int, float]]:
        """"""
        query = self._session.query(
            extract('month', Movimentacao.data_lancamento).label('mes'),
            func.sum(Movimentacao.valor).label('total_despesas')
        ).filter(
            extract('year', Movimentacao.data_lancamento) == ano,
            Movimentacao.tipo == 'despesa',
            Movimentacao.excluida.is_(False),
        ).group_by(extract('month', Movimentacao.data_lancamento))
        
        return query.all()
    
    
    def listar_totais_receitas_por_mês_do_ano(self, ano: int) -> list[tuple[int, float]]:
        """"""

        query = self._session.query(
            extract('month', Movimentacao.data_lancamento).label('mes'),
            func.sum(Movimentacao.valor).label('total_receitas')
        ).filter(
            extract('year', Movimentacao.data_lancamento) == ano,
            Movimentacao.tipo == 'receita',
            Movimentacao.excluida.is_(False),
        ).group_by(extract('month', Movimentacao.data_lancamento))

        return query.all()
    
    def obter_anos_disponiveis(self) -> list[int]:
        """Retorna os anos distintos das movimentações ativas."""
        resultados = self._session.query(
            distinct(extract('year', Movimentacao.data_lancamento))
        ).filter(
            Movimentacao.excluida.is_(False)
        ).order_by(
            extract('year', Movimentacao.data_lancamento).desc()
        ).all()

        # Converte de [(2026.0,), (2025.0,)] para ["2026", "2025"]
        anos = [int(r[0]) for r in resultados if r[0] is not None]

        return sorted(anos, reverse=True) or [datetime.date.today().year]