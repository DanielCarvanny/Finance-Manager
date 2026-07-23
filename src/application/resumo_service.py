from sqlalchemy.orm import Session
from application.analisador_service import calcular_resumo_mensal
from domain.models.resumo_mensal import ResumoMensal
from utils.logger import logger

def gerar_resumo(session: Session, novo_ano: int, novo_mes: int):
    """
    Gera um novo resumo mensal com base nas movimentações atuais.
    Se o resumo já existir no banco de dados, redireciona o fluxo para a 
    função de atualização, protegendo o sistema contra registros duplicados.
    """
    # Verifica se já existe
    resumo_existente = session.query(ResumoMensal).filter_by(ano=novo_ano, mes=novo_mes).first()
    if resumo_existente:
        logger.info(f"Resumo mensal existente encontrado para {novo_ano}/{novo_mes:02d}. Recalculando e atualizando métricas...")
        return atualizar_resumo(session, novo_ano, novo_mes)
    
    novo_resumo = sincronizar_resumo(session, novo_ano, novo_mes)
    session.commit()
    
    return novo_resumo

def obter_resumo(session: Session, ano: int, mes: int):
    """
    Busca o resumo mensal no banco de dados.
    Caso o resumo ainda não exista para aquele mês, ele calcula e cria 
    automaticamente, garantindo que a tela sempre tenha dados válidos.
    """
    
    resumo = session.query(ResumoMensal).filter_by(ano=ano, mes=mes).first()
    if resumo:
        return atualizar_resumo(session, ano, mes)
    else:
        return gerar_resumo(session, ano, mes)

def atualizar_resumo(session: Session, ano: int, mes: int):
    """
    Força o recalculo de todas as métricas do mês (receitas, despesas, saldo)
    usando as transações mais recentes, e aplica os novos valores no registro 
    já existente no banco de dados de forma dinâmica.
    """
    resumo_atualizado = sincronizar_resumo(session, ano, mes)
    session.commit()
    return resumo_atualizado


def sincronizar_resumo(session: Session, ano: int, mes: int) -> ResumoMensal:
    """Calcula e aplica o resumo sem confirmar a transação.

    Permite que alterações em movimentações e no resumo mensal sejam salvas
    juntas, evitando indicadores persistidos desatualizados após arquivar ou
    restaurar lançamentos.
    """
    resumo_existente = session.query(ResumoMensal).filter_by(ano=ano, mes=mes).first()
    novos_valores = calcular_resumo_mensal(session, ano, mes)

    if resumo_existente:
        for chave, valor in novos_valores.items():
            setattr(resumo_existente, chave, valor)
        return resumo_existente

    novo_resumo = ResumoMensal(ano=ano, mes=mes, **novos_valores)
    session.add(novo_resumo)
    return novo_resumo
