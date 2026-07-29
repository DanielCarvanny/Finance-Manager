from utils.logger import logger
from infrastructure.database.unit_of_work import UnitOfWork
from application.movimentacao_service import MovimentacaoService
from domain.exceptions import ArquivamentoEstornoError

class LixeiraViewModel:
    def __init__(self):
        self.mov_service = MovimentacaoService()
        
    def arquivar_movimentacoes(self, ids: list[int]) -> int:
        """Move movimentações ativas para a lixeira."""
        try:
            with UnitOfWork() as uow:
                dados = self.mov_service.arquivar_movimentacoes(uow, ids)
                uow.commit()
                return dados
        except ArquivamentoEstornoError as erro:
            logger.error("Movimentações vinculadas", str(erro))
            raise
        except Exception as e:
            logger.error("Erro ao arquivar movimentações.", exc_info=True)
            return 0
        
    def listar_movimentacoes_lixeira(self) -> list[dict]:
        """
        """
        with UnitOfWork() as uow:
            movs_orm = uow.movimentacoes.listar_excluidas()
            return[
                {
                    "id": movs.id,
                    "data_lancamento": movs.data_lancamento,
                    "descricao": movs.descricao,
                    "valor": movs.valor,
                    "categoria_nome": movs.categoria.nome if movs.categoria else "Sem categoria",
                    "excluida_em": movs.excluida_em
                }
                for movs in movs_orm
            ]
        
    def restaurar_da_lixeira(self, ids: list[int]):
            try:
                with UnitOfWork() as uow:
                    quantidade = self.mov_service.restaurar_movimentacoes(uow, ids)
                    uow.commit()
                    return quantidade
            except Exception as e:
                logger.error("Erro ao restaurar movimentações da lixeira.", exc_info=True)
                return