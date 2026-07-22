from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from models.movimentacao import Movimentacao
from models.resumo_mensal import ResumoMensal
from models.categoria import Categoria
import calendar

def filtrar_movimentacoes_ativas(query):
    """Remove movimentações arquivadas das consultas usuais do dashboard."""
    return query.filter(Movimentacao.excluida.is_(False))

def filtrar_por_mes(query, ano, mes):
    """Função utilitária para não repetir o filtro de data em toda consulta"""
    return filtrar_movimentacoes_ativas(query).filter(
        extract('year', Movimentacao.data_lancamento) == ano,
        extract('month', Movimentacao.data_lancamento) == mes,
    ) 

def calcular_resumo_mensal(session: Session, ano: int, mes: int):
    """
    Calcula o total de Receitas e Despesas do período.
    Calcula o Gasto médio diário do período.
    Busca a Categoria com maior e menor soma de despesas
    """
    # Cálculo do total de receitas
    query_receitas = session.query(func.sum(Movimentacao.valor)).filter(Movimentacao.tipo == 'receita')
    total_receitas = filtrar_por_mes(query_receitas, ano, mes).scalar() or 0.0

    # Cálculo do total de despesas (Garante que volte como número positivo usando abs())
    query_despesas = session.query(func.sum(Movimentacao.valor)).filter(Movimentacao.tipo == 'despesa')
    soma_despesas  = filtrar_por_mes(query_despesas, ano, mes).scalar() or 0.0
    total_despesas = abs(float(soma_despesas))

    # saldo do período
    saldo_periodo = float(total_receitas) - total_despesas

    # Gasto médio diário do período
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    gasto_medio_diario = total_despesas / dias_no_mes

    query_categorias = session.query(
        Movimentacao.categoria_id,
        func.sum(Movimentacao.valor).label('total_gastos') 
    ).filter(Movimentacao.tipo == 'despesa').group_by(Movimentacao.categoria_id)

    query_categorias = filtrar_por_mes(query_categorias, ano, mes)

    # Categoria com maior soma de despesas (asc) para pegar o pior gasto!
    categoria_maior_gasto= query_categorias.order_by(func.sum(Movimentacao.valor).asc()).first()

    # Categoria com menor soma de despesas (desc) para pegar o melhor gasto!
    categoria_menor_gasto = query_categorias.order_by(func.sum(Movimentacao.valor).desc()).first()

    return {
        "total_receitas": float(total_receitas),
        "total_despesas": total_despesas,
        "saldo_periodo": saldo_periodo,
        "gasto_medio_diario": gasto_medio_diario,
        # Salva apenas o ID da categoria (se existir alguma)
        "categoria_maior_gasto_id": categoria_maior_gasto.categoria_id if categoria_maior_gasto else None,
        "categoria_menor_gasto_id": categoria_menor_gasto.categoria_id if categoria_menor_gasto else None
    }

def percentual_por_categoria(session: Session, ano: int, mes: int):
    """
    Calcula o percentual de gasto por categoria
    Retorna: {"Alimentação": 45.50, "Transporte": 20.00}
    """
    
    # Total de despesas do mês
    query_total = session.query(func.sum(Movimentacao.valor)).filter(Movimentacao.tipo == 'despesa')
    soma_total = filtrar_por_mes(query_total, ano, mes).scalar() or 0.0
    total_despesas = abs(float(soma_total))

    if total_despesas == 0:
        return{}
    
    # Buscamos o total de gastos agrupado por categoria
    query_agrupada = session.query(
        Categoria.nome, func.sum(Movimentacao.valor)
        ).join(Movimentacao.categoria).filter(Movimentacao.tipo == 'despesa').group_by(Categoria.nome)
    
    # Executa a busca aplicando o filtro do mês
    resultados = filtrar_por_mes(query_agrupada, ano, mes).all()

    dicionario_percentual = {}

    for nome_categoria, soma_categoria in resultados:
        valor_categoria = abs(float(soma_categoria))

        # Matemática: (Parte / Todo) * 100
        percentual = (valor_categoria / total_despesas)*100

        # Guarda no dicionário arredondando para 2 casas decimais
        dicionario_percentual[nome_categoria] = round(percentual, 2)

    return dicionario_percentual

def evolucao_mensal(session: Session, ano: int):
    """
    Retorna a lista de totais de despesas por mês do ano para Gráficos de Linha.
    """
    query = session.query(
        extract('month', Movimentacao.data_lancamento).label('mes'),
        func.sum(Movimentacao.valor).label('total_despesas')
    ).filter(
        extract('year', Movimentacao.data_lancamento) == ano,
        Movimentacao.tipo == 'despesa',
        Movimentacao.excluida.is_(False),
    ).group_by(extract('month', Movimentacao.data_lancamento))

    resultado = query.all()

    eixo_x = []
    eixo_y = []

    for mes, total_despesas in resultado:
        eixo_x.append(mes)
        eixo_y.append(abs(float(total_despesas))) 

    return {
        "mes": eixo_x, 
        "total_despesas": eixo_y
    }

def receitas_vs_despesas_mensal(session: Session, ano: int):
    """
    Retorna dois dicionários com os totais de receitas e despesas de cada mês do ano.
    Formato: 
        receitas = {"Jan": 4500.0, "Fev": 3000.0, ...}
        despesas = {"Jan": 1200.0, "Fev": 2100.0, ...}
    """

    nomes_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    # Inicializa todos os 12 meses zerados
    receitas_por_mes = {mes: 0.0 for mes in nomes_meses}
    despesas_por_mes = {mes: 0.0 for mes in nomes_meses}

    
    # Cálculo do total de receitas
    query_receitas = session.query(
        extract('month', Movimentacao.data_lancamento).label('mes'),
        func.sum(Movimentacao.valor).label('total_receitas')
    ).filter(
        extract('year', Movimentacao.data_lancamento) == ano,
        Movimentacao.tipo == 'receita',
        Movimentacao.excluida.is_(False),
    ).group_by(extract('month', Movimentacao.data_lancamento))

    resultado_receitas = query_receitas.all()

    for mes_num, total_receitas in resultado_receitas:
        if mes_num and 1 <= int(mes_num) <= 12:
            nome_mes = nomes_meses[int(mes_num) - 1]
            receitas_por_mes[nome_mes] = abs(float(total_receitas or 0.0))

    # Cálculo do total de despesas (Garante que volte como número positivo usando abs())
    query_despesas = session.query(
        extract('month', Movimentacao.data_lancamento).label('mes'),
        func.sum(Movimentacao.valor).label('total_despesas')
    ).filter(
        extract('year', Movimentacao.data_lancamento) == ano,
        Movimentacao.tipo == 'despesa',
        Movimentacao.excluida.is_(False),
    ).group_by(extract('month', Movimentacao.data_lancamento))

    resultado_despesas = query_despesas.all()

    for mes_num, total_despesas in resultado_despesas:
        if mes_num and 1 <= int(mes_num) <= 12:
            nome_mes = nomes_meses[int(mes_num) - 1]
            despesas_por_mes[nome_mes] = abs(float(total_despesas or 0.0)) 

    return receitas_por_mes, despesas_por_mes
