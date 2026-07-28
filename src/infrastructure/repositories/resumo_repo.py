from infrastructure.repositories.base import BaseRepository
from domain.models.resumo_mensal import ResumoMensal 
from typing import Optional

class ResumoMensalRepository(BaseRepository[ResumoMensal]):
    def __init__(self, session):
        super().__init__(session,ResumoMensal)

    def obter_por_periodo(self,ano: int, mes: int)-> Optional[ResumoMensal]:
        """
        Busca o resumo mensal no banco de dados.
        """
        return self._session.query(ResumoMensal).filter(
            ResumoMensal.ano == ano,
            ResumoMensal.mes == mes,
        ).first()

    def salvar_ou_atualizar(self, resumo: ResumoMensal)-> ResumoMensal:
        """
        Salva um novo resumo mensal se não existir, ou atualiza o existente no banco.
        """
        existente = self._session.query(ResumoMensal).filter(
            ResumoMensal.ano == resumo.ano,
            ResumoMensal.mes == resumo.mes,
        ).first()

        if existente:
            # Atualiza os valores do registro existente
            existente.total_receitas = resumo.total_receitas
            existente.total_despesas = resumo.total_despesas
            existente.saldo_periodo = resumo.saldo_periodo
            existente.gasto_medio_diario = resumo.gasto_medio_diario
            existente.categoria_maior_gasto_id = resumo.categoria_maior_gasto_id
            existente.categoria_menor_gasto_id = resumo.categoria_menor_gasto_id
            return existente
        else:
            return self.create(resumo)


        