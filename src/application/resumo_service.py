from infrastructure.database.unit_of_work import UnitOfWork
from application.analisador_service import AnalisadorService
from domain.models.resumo_mensal import ResumoMensal
from utils.logger import logger

class ResumoService:
    def gerar_resumo(self, uow: UnitOfWork, novo_ano: int, novo_mes: int):
        """
        Gera um novo resumo mensal com base nas movimentações atuais.
        Se o resumo já existir no banco de dados, redireciona o fluxo para a 
        função de atualização, protegendo o sistema contra registros duplicados.
        """
        # Verifica se já existe
        resumo_existente = uow.resumos.obter_por_periodo(novo_ano, novo_mes)
        if resumo_existente:
            logger.info(f"Resumo mensal existente encontrado para {novo_ano}/{novo_mes:02d}. Recalculando e atualizando métricas...")
            return self.atualizar_resumo(uow, novo_ano, novo_mes)
        
        novo_resumo = self.sincronizar_resumo(uow, novo_ano, novo_mes)
        
        return novo_resumo

    def obter_resumo(self, uow: UnitOfWork, ano: int, mes: int):
        """
        Busca o resumo mensal no banco de dados (Cache).
        Se o resumo já existir, retorna imediatamente sem recalcular.
        Se ainda não existir para aquele mês, calcula e salva pela primeira vez.
        """
        
        resumo = uow.resumos.obter_por_periodo(ano, mes)
        
        if resumo:
            return resumo
        else:
            return self.sincronizar_resumo(uow, ano, mes)

    def atualizar_resumo(self, uow: UnitOfWork, ano: int, mes: int):
        """
        Força o recalculo de todas as métricas do mês (receitas, despesas, saldo)
        usando as transações mais recentes, e aplica os novos valores no registro 
        já existente no banco de dados de forma dinâmica.
        """
        resumo_atualizado = self.sincronizar_resumo(uow, ano, mes)
        
        return resumo_atualizado


    def sincronizar_resumo(self, uow: UnitOfWork, ano: int, mes: int) -> ResumoMensal:
        """
        Recalcula as métricas do período e atualiza no banco.
        Deve ser chamado SEMPRE que houver alteração em movimentações do mês (importação, lixeira, reclassificação).
        """
        analisador = AnalisadorService()
        resumo_existente = uow.resumos.obter_por_periodo(ano, mes)
        novos_valores = analisador.calcular_resumo_mensal(uow, ano, mes)

        if resumo_existente:
            for chave, valor in novos_valores.items():
                setattr(resumo_existente, chave, valor)
            return resumo_existente

        novo_resumo = ResumoMensal(ano=ano, mes=mes, **novos_valores)
        uow.resumos.salvar_ou_atualizar(novo_resumo)
        return novo_resumo
