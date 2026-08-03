from domain.models.movimentacao import Movimentacao
from utils.logger import logger
from datetime import datetime
from application.resumo_service import ResumoService
from infrastructure.database.unit_of_work import UnitOfWork
from domain.exceptions import ArquivamentoEstornoError

class MovimentacaoService:
    def atualizar_categoria(self, uow: UnitOfWork, mov_id: int, nova_categoria_id: int):
        """
        Busca a movimentação no banco e atualiza a sua categoria.
        """
        mov = uow.movimentacoes.buscar_por_id(mov_id)

        if mov:
            # Atualiza a categoria
            mov.categoria_id = nova_categoria_id
            logger.info(f"Movimentação ID {mov_id} reclassificada para categoria_id={nova_categoria_id} pelo usuário.")
            return True
        
        logger.error(f"Movimentação ID {mov_id} não encontrada.")
        return False

    def _validar_estornos_para_arquivamento(self, uow: UnitOfWork, movimentacoes) -> None:
        """Exige que as duas pontas ativas de um estorno sejam arquivadas juntas."""
        ids_selecionados = {mov.id for mov in movimentacoes}

        for mov in movimentacoes:
            if mov.estorno_id:
                original = uow.movimentacoes.buscar_por_id(mov.estorno_id)
                if original and not original.excluida and original.id not in ids_selecionados:
                    raise ArquivamentoEstornoError("Selecione também a movimentação original vinculada ao estorno.")

        estornos_ativos = uow.movimentacoes.listar_estornos_ativos(ids_selecionados)
        if any(estorno.id not in ids_selecionados for estorno in estornos_ativos):
            raise ArquivamentoEstornoError("Selecione também todos os estornos ativos vinculados à movimentação.")


    def _sincronizar_periodos_afetados(self, uow: UnitOfWork, movimentacoes) -> None:
        """Sincroniza os resumos mensais dos períodos das movimentações alteradas."""
        
        resumo = ResumoService()
        for ano, mes in {
            (mov.data_lancamento.year, mov.data_lancamento.month)
            for mov in movimentacoes
        }:
            resumo.sincronizar_resumo(uow, ano, mes)


    def arquivar_movimentacoes(self, uow: UnitOfWork, ids: list[int]) -> int:
        """Move movimentações ativas para a lixeira e atualiza seus resumos."""
        if not ids:
            return 0
        
        movs = uow.movimentacoes.listar_movimentacoes_por_ids(ids)

        self._validar_estornos_para_arquivamento(uow, movs)

        data_arquivamento = datetime.now()
        for mov in movs:
            mov.excluida = True
            mov.excluida_em = data_arquivamento

        self._sincronizar_periodos_afetados(uow, movs)
        logger.info("%s movimentação(ões) movida(s) para a lixeira.", len(movs))
        return len(movs)

    def restaurar_movimentacoes(self, uow: UnitOfWork, ids: list[int]) -> int:
        """Restaura movimentações arquivadas e atualiza seus resumos."""
        if not ids:
            return 0

        movs = uow.movimentacoes.listar_excluidas_por_ids(ids)

        for mov in movs:
            mov.excluida = False
            mov.excluida_em = None

        self._sincronizar_periodos_afetados(uow, movs)
        logger.info("%s movimentação(ões) restaurada(s) da lixeira.", len(movs))
        return len(movs)
