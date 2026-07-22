from models.movimentacao import Movimentacao
from sqlalchemy.orm import Session
from utils.logger import logger
from datetime import datetime
from services.resumo_service import sincronizar_resumo


class ArquivamentoEstornoError(ValueError):
    """Impede arquivar apenas uma ponta de uma movimentação de estorno."""

def atualizar_categoria(session: Session, mov_id: int, nova_categoria_id: int):
    """
    Busca a movimentação no banco e atualiza a sua categoria.
    """
    mov = session.query(Movimentacao).filter_by(excluida=False, id=mov_id).first()

    if mov:
        # Atualiza a categoria
        mov.categoria_id = nova_categoria_id
        session.commit()
        logger.info(f"Movimentação ID {mov_id} reclassificada para categoria_id={nova_categoria_id} pelo usuário.")
        return True
    else:
        return False

def _validar_estornos_para_arquivamento(session: Session, movimentacoes) -> None:
    """Exige que as duas pontas ativas de um estorno sejam arquivadas juntas."""
    ids_selecionados = {mov.id for mov in movimentacoes}

    for mov in movimentacoes:
        if mov.estorno_id:
            original = session.get(Movimentacao, mov.estorno_id)
            if original and not original.excluida and original.id not in ids_selecionados:
                raise ArquivamentoEstornoError(
                    "Selecione também a movimentação original vinculada ao estorno."
                )

    estornos_ativos = session.query(Movimentacao).filter(
        Movimentacao.estorno_id.in_(ids_selecionados),
        Movimentacao.excluida.is_(False),
    ).all()
    if any(estorno.id not in ids_selecionados for estorno in estornos_ativos):
        raise ArquivamentoEstornoError(
            "Selecione também todos os estornos ativos vinculados à movimentação."
        )


def _sincronizar_periodos_afetados(session: Session, movimentacoes) -> None:
    for ano, mes in {
        (mov.data_lancamento.year, mov.data_lancamento.month)
        for mov in movimentacoes
    }:
        sincronizar_resumo(session, ano, mes)


def arquivar_movimentacoes(session: Session, ids: list[int]) -> int:
    """Move movimentações ativas para a lixeira e atualiza seus resumos."""
    if not ids:
        return 0

    movs = (
        session.query(Movimentacao)
        .filter(
            Movimentacao.id.in_(ids),
            Movimentacao.excluida.is_(False)
        )
        .all()
    )

    _validar_estornos_para_arquivamento(session, movs)

    try:
        data_arquivamento = datetime.now()
        for mov in movs:
            mov.excluida = True
            mov.excluida_em = data_arquivamento

        _sincronizar_periodos_afetados(session, movs)
        session.commit()
    except Exception:
        session.rollback()
        raise

    logger.info("%s movimentação(ões) movida(s) para a lixeira.", len(movs))
    return len(movs)

def restaurar_movimentacoes(session: Session, ids: list[int]) -> int:
    """Restaura movimentações arquivadas e atualiza seus resumos."""
    if not ids:
        return 0

    movs = session.query(Movimentacao).filter(
            Movimentacao.id.in_(ids),
            Movimentacao.excluida.is_(True)
        ).all()

    try:
        for mov in movs:
            mov.excluida = False
            mov.excluida_em = None

        _sincronizar_periodos_afetados(session, movs)
        session.commit()
    except Exception:
        session.rollback()
        raise

    logger.info("%s movimentação(ões) restaurada(s) da lixeira.", len(movs))
    return len(movs)
