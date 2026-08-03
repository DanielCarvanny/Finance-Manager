from infrastructure.database.unit_of_work import UnitOfWork
from domain.models.movimentacao import Movimentacao
from domain.models.resumo_mensal import ResumoMensal
from domain.models.categoria import Categoria
import calendar

class AnalisadorService:
    def filtrar_movimentacoes_ativas(self, uow: UnitOfWork):
        """Remove movimentações arquivadas das consultas usuais do dashboard."""
        return uow.movimentacoes.listar_movimentacoes_ativas()

    def filtrar_por_mes(self, uow: UnitOfWork, ano, mes):
        """Função utilitária para não repetir o filtro de data em toda consulta"""
        return uow.movimentacoes.listar_por_periodo(ano, mes)

    def calcular_resumo_mensal(self, uow: UnitOfWork, ano: int, mes: int):
        """
        Calcula o total de Receitas e Despesas do período.
        Calcula o Gasto médio diário do período.
        Busca a Categoria com maior e menor soma de despesas
        """
        # Cálculo do total de receitas
        total_receitas = uow.movimentacoes.calcular_total_receitas(ano, mes)

        # Cálculo do total de despesas (Garante que volte como número positivo usando abs())
        total_despesas = uow.movimentacoes.calcular_total_despesas(ano, mes)

        # saldo do período
        saldo_periodo = float(total_receitas) - total_despesas

        # Gasto médio diário do período
        dias_no_mes = calendar.monthrange(ano, mes)[1]
        gasto_medio_diario = total_despesas / dias_no_mes

        # Categoria com maior soma de despesas (asc) para pegar o pior gasto!
        categoria_maior_gasto= uow.movimentacoes.calcular_categoria_com_maior_gasto(ano, mes)

        # Categoria com menor soma de despesas (desc) para pegar o melhor gasto!
        categoria_menor_gasto = uow.movimentacoes.calcular_categoria_com_menor_gasto(ano, mes)

        return {
            "total_receitas": float(total_receitas),
            "total_despesas": total_despesas,
            "saldo_periodo": saldo_periodo,
            "gasto_medio_diario": gasto_medio_diario,
            # Salva apenas o ID da categoria (se existir alguma)
            "categoria_maior_gasto_id": categoria_maior_gasto[0] if categoria_maior_gasto else None,
            "categoria_menor_gasto_id": categoria_menor_gasto[0] if categoria_menor_gasto else None
        }

    def percentual_por_categoria(self, uow: UnitOfWork, ano: int, mes: int):
        """
        Calcula o percentual de gasto por categoria
        Retorna: {"Alimentação": 45.50, "Transporte": 20.00}
        """
        
        # Total de despesas do mês
        total_despesas = uow.movimentacoes.calcular_total_despesas(ano, mes)

        if total_despesas == 0:
            return{}
        
        # Buscamos o total de gastos agrupado por categoria & Executamos a busca aplicando o filtro do mês
        resultados = uow.movimentacoes.buscar_total_de_gastos_por_categoria(ano, mes)

        dicionario_percentual = {}

        for nome_categoria, soma_categoria in resultados:
            valor_categoria = abs(float(soma_categoria))

            # Matemática: (Parte / Todo) * 100
            percentual = (valor_categoria / total_despesas)*100

            # Guarda no dicionário arredondando para 2 casas decimais
            dicionario_percentual[nome_categoria] = round(percentual, 2)

        return dicionario_percentual

    def evolucao_mensal(self, uow: UnitOfWork, ano: int):
        """
        Retorna a lista de totais de despesas por mês do ano para Gráficos de Linha.
        """
        resultado = uow.movimentacoes.listar_totais_despesas_por_mês_do_ano(ano)

        eixo_x = []
        eixo_y = []

        for mes, total_despesas in resultado:
            eixo_x.append(mes)
            eixo_y.append(abs(float(total_despesas))) 

        return {
            "mes": eixo_x, 
            "total_despesas": eixo_y
        }

    def receitas_vs_despesas_mensal(self, uow: UnitOfWork, ano: int):
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
        

        resultado_receitas = uow.movimentacoes.listar_totais_receitas_por_mês_do_ano(ano)

        for mes_num, total_receitas in resultado_receitas:
            if mes_num and 1 <= int(mes_num) <= 12:
                nome_mes = nomes_meses[int(mes_num) - 1]
                receitas_por_mes[nome_mes] = abs(float(total_receitas or 0.0))

        # Cálculo do total de despesas (Garante que volte como número positivo usando abs())
        
        
        resultado_despesas = uow.movimentacoes.listar_totais_despesas_por_mês_do_ano(ano)
        
        for mes_num, total_despesas in resultado_despesas:
            if mes_num and 1 <= int(mes_num) <= 12:
                nome_mes = nomes_meses[int(mes_num) - 1]
                despesas_por_mes[nome_mes] = abs(float(total_despesas or 0.0)) 

        return receitas_por_mes, despesas_por_mes
