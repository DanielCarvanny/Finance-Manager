from infrastructure.database.unit_of_work import UnitOfWork
from application.resumo_service import ResumoService
from application.analisador_service import AnalisadorService
from application.movimentacao_service import MovimentacaoService

class DashboardViewModel:
    def __init__(self):
        self.resumo_service = ResumoService()
        self.analisador = AnalisadorService()
        self.mov_service = MovimentacaoService()

        
    def carregar_periodo(self, ano, mes) -> dict:
        """Dispara quando o filtro muda ou uma importação acaba"""
        with UnitOfWork() as uow:
            # Pega os dados dos Cards (Receitas, Despesas, Saldo, Gasto Diário)
            resumo = self.resumo_service.obter_resumo(uow, ano, mes)
            
            # Pega os dados dos Gráficos
            dados_pizza = self.analisador.percentual_por_categoria(uow, ano, mes)
            dados_linha = self.analisador.evolucao_mensal(uow, ano)
            rec_mes, desp_mes = self.analisador.receitas_vs_despesas_mensal(uow, ano)
            
            # Pega a lista de movimentações e converte para dicionários simples (DTOs)
            movs_orm = uow.movimentacoes.listar_por_periodo(ano, mes)
            movs_dto = [
                {
                    "id": movs.id,
                    "data_lancamento": movs.data_lancamento,
                    "descricao": movs.descricao,
                    "valor": movs.valor,
                    "categoria_id": movs.categoria_id,
                    "categoria_nome": movs.categoria.nome if movs.categoria else "Sem categoria"
                }
                for movs in movs_orm
            ]
            
            # Pega as categorias para o dropdown da tabela
            cats_orm = uow.categorias.listar_todas()
            cats_dto = [
                {
                    "nome": cats.nome,
                    "id": cats.id
                }
                for cats in cats_orm
            ]
        
        return {
            "cards": {
                "total_receitas": float(resumo.total_receitas),
                "total_despesas": float(resumo.total_despesas),
                "saldo_periodo": float(resumo.saldo_periodo),
                "gasto_medio_diario": float(resumo.gasto_medio_diario)
            },
            "graficos": {
                "pizza": dados_pizza,
                "linha": dados_linha,
                "barras_receitas": rec_mes,
                "barras_despesas": desp_mes
            },
            "tabela": {
                "movimentacoes": movs_dto,
                "categorias": cats_dto
            }
        }
                    
    def alterar_categoria_movimentacao(self, movimentacao_id: int, categoria_id: int, ano: int, mes: int) -> dict:
        """
        Altera a categoria de uma movimentação, atualiza os resumos do mês,
        salva no banco (commit) e retorna os dados atualizados do dashboard.
        """        
        with UnitOfWork() as uow:
            # Altera a categoria via serviço
            sucess = self.mov_service.atualizar_categoria(uow, movimentacao_id, categoria_id)
            
            if not sucess:
                raise ValueError("A movimentação não está disponível para reclassificação.")
            
            # Atualiza as métricas do resumo do mês afetado
            self.resumo_service.atualizar_resumo(uow, ano, mes)
            
            # Confirma as alterações no banco de dados
            uow.commit()
            
        # Recarrega e retorna os dados já atualizados para a UI
        return self.carregar_periodo(ano, mes)
        
    def listar_anos(self)-> list[str]:
        """
        Retorna uma lista de anos (como strings) que possuem movimentações ativas.
        """
        with UnitOfWork() as uow:
            anos_disp = [str(a) for a in uow.movimentacoes.obter_anos_disponiveis()]
        
        return anos_disp