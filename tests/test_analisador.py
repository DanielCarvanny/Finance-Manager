import pytest
from datetime import date
from infrastructure.database.unit_of_work import UnitOfWork
from application.analisador_service import AnalisadorService


@pytest.fixture
def uow(session):
    factory = lambda: session
    uow = UnitOfWork(session_factory=factory)
    uow.__enter__()
    yield uow
    uow.__exit__(None, None, None)


@pytest.fixture
def analisador():
    return AnalisadorService()


class TestCalcularResumoMensal:
    def test_total_receitas_junho(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 6)
        assert resumo["total_receitas"] == 5000.00

    def test_total_despesas_junho(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 6)
        assert resumo["total_despesas"] == 50.00

    def test_saldo_periodo_junho(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 6)
        assert resumo["saldo_periodo"] == pytest.approx(4950.00, rel=1e-2)

    def test_gasto_medio_diario_junho(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 6)
        esperado = 50.00 / 30
        assert resumo["gasto_medio_diario"] == pytest.approx(esperado, rel=1e-2)

    def test_mes_sem_dados_retorna_zeros(self, analisador, uow):
        resumo = analisador.calcular_resumo_mensal(uow, 2025, 1)
        assert resumo["total_receitas"] == 0.0
        assert resumo["total_despesas"] == 0.0
        assert resumo["saldo_periodo"] == 0.0

    def test_julho_despesas_sem_receitas(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 7)
        assert resumo["total_receitas"] == 0.0
        assert resumo["total_despesas"] == 100.00

    def test_calcular_categoria_maior_gasto(self, analisador, uow, movimentacoes_base):
        resumo = analisador.calcular_resumo_mensal(uow, 2026, 6)
        assert resumo["categoria_maior_gasto_id"] is not None


class TestPercentualPorCategoria:
    def test_percentual_alimentacao_cem_porcento(
        self, analisador, uow, movimentacoes_base
    ):
        percentuais = analisador.percentual_por_categoria(uow, 2026, 6)
        assert percentuais.get("Alimentação") == pytest.approx(100.0, rel=1e-2)

    def test_mes_sem_despesas_retorna_vazio(self, analisador, uow):
        percentuais = analisador.percentual_por_categoria(uow, 2024, 1)
        assert percentuais == {}


class TestEvolucaoMensal:
    def test_evolucao_contem_junho_e_julho(self, analisador, uow, movimentacoes_base):
        dados = analisador.evolucao_mensal(uow, 2026)
        assert 6 in dados["mes"]
        assert 7 in dados["mes"]

    def test_evolucao_valor_junho(self, analisador, uow, movimentacoes_base):
        dados = analisador.evolucao_mensal(uow, 2026)
        idx = dados["mes"].index(6)
        assert dados["total_despesas"][idx] == pytest.approx(50.00, rel=1e-2)

    def test_ano_sem_dados_retorna_listas_vazias(self, analisador, uow):
        dados = analisador.evolucao_mensal(uow, 2020)
        assert dados["mes"] == []
        assert dados["total_despesas"] == []


class TestReceitasVsDespesasMensal:
    def test_junho_contem_receita_e_despesa(self, analisador, uow, movimentacoes_base):
        rec_mes, desp_mes = analisador.receitas_vs_despesas_mensal(uow, 2026)
        assert rec_mes.get("Jun") == pytest.approx(5000.0, rel=1e-2)
        assert desp_mes.get("Jun") == pytest.approx(50.0, rel=1e-2)

    def test_julho_apenas_despesa(self, analisador, uow, movimentacoes_base):
        rec_mes, desp_mes = analisador.receitas_vs_despesas_mensal(uow, 2026)
        assert rec_mes.get("Jul") == pytest.approx(0.0, rel=1e-2)
        assert desp_mes.get("Jul") == pytest.approx(100.0, rel=1e-2)

    def test_ano_sem_dados_retorna_tudo_zero(self, analisador, uow):
        rec_mes, desp_mes = analisador.receitas_vs_despesas_mensal(uow, 2020)
        for mes in rec_mes:
            assert rec_mes[mes] == 0.0
        for mes in desp_mes:
            assert desp_mes[mes] == 0.0
