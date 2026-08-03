"""
test_dashboard_viewmodel.py — Testes unitários do DashboardViewModel.
Mocka todos os serviços e o UnitOfWork para testar o contrato de dados com a UI.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ui.viewmodels.dashboard_view_model import DashboardViewModel


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _criar_resumo_mock(receitas=5000.0, despesas=1200.0, saldo=3800.0, gasto_diario=40.0):
    """Cria um objeto Resumo simulado com os atributos esperados pelo ViewModel."""
    resumo = MagicMock()
    resumo.total_receitas = receitas
    resumo.total_despesas = despesas
    resumo.saldo_periodo = saldo
    resumo.gasto_medio_diario = gasto_diario
    return resumo


def _criar_mov_mock(id=1, descricao="Restaurante", valor=-50.0, categoria_id=1, categoria_nome="Alimentação"):
    """Cria um objeto Movimentacao ORM simulado."""
    mov = MagicMock()
    mov.id = id
    mov.data_lancamento = date(2026, 6, 10)
    mov.descricao = descricao
    mov.valor = valor
    mov.categoria_id = categoria_id
    mov.categoria = MagicMock()
    mov.categoria.nome = categoria_nome
    return mov


def _criar_cat_mock(id=1, nome="Alimentação"):
    """Cria um objeto Categoria ORM simulado."""
    cat = MagicMock()
    cat.id = id
    cat.nome = nome
    return cat


def _montar_uow_mock(movs=None, cats=None, anos=None):
    """Monta um UnitOfWork falso com repositórios simulados."""
    uow = MagicMock()
    uow.movimentacoes.listar_por_periodo.return_value = movs or []
    uow.categorias.listar_todas.return_value = cats or []
    uow.movimentacoes.obter_anos_disponiveis.return_value = anos or [2026]
    return uow


# ─────────────────────────────────────────────────────────────────────────────
# 1. CARREGAR_PERIODO — ESTRUTURA DO RETORNO
# ─────────────────────────────────────────────────────────────────────────────

def test_carregar_periodo_retorna_chaves_obrigatorias():
    """O retorno de carregar_periodo deve conter 'cards', 'graficos' e 'tabela'."""
    vm = DashboardViewModel()
    uow_mock = _montar_uow_mock()

    vm.resumo_service.obter_resumo = MagicMock(return_value=_criar_resumo_mock())
    vm.analisador.percentual_por_categoria = MagicMock(return_value={})
    vm.analisador.evolucao_mensal = MagicMock(return_value={"meses": [], "totais": []})
    vm.analisador.receitas_vs_despesas_mensal = MagicMock(return_value=({}, {}))

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        dados = vm.carregar_periodo(2026, 6)

    assert "cards" in dados
    assert "graficos" in dados
    assert "tabela" in dados


def test_carregar_periodo_cards_contem_valores_float():
    """Os valores dos cards devem ser floats primitivos, não objetos ORM."""
    vm = DashboardViewModel()
    uow_mock = _montar_uow_mock()

    vm.resumo_service.obter_resumo = MagicMock(return_value=_criar_resumo_mock(
        receitas=5000.0, despesas=1200.0, saldo=3800.0, gasto_diario=40.0
    ))
    vm.analisador.percentual_por_categoria = MagicMock(return_value={})
    vm.analisador.evolucao_mensal = MagicMock(return_value={})
    vm.analisador.receitas_vs_despesas_mensal = MagicMock(return_value=({}, {}))

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        dados = vm.carregar_periodo(2026, 6)

    cards = dados["cards"]
    assert cards["total_receitas"] == pytest.approx(5000.0)
    assert cards["total_despesas"] == pytest.approx(1200.0)
    assert cards["saldo_periodo"] == pytest.approx(3800.0)
    assert cards["gasto_medio_diario"] == pytest.approx(40.0)

    # Verifica que são floats, não mocks ou objetos ORM
    assert isinstance(cards["total_receitas"], float)
    assert isinstance(cards["saldo_periodo"], float)


def test_carregar_periodo_tabela_movimentacoes_sao_dicts():
    """As movimentações na tabela devem ser dicionários simples, não objetos ORM."""
    vm = DashboardViewModel()
    mov_mock = _criar_mov_mock(descricao="Restaurante", valor=-75.50)
    uow_mock = _montar_uow_mock(movs=[mov_mock])

    vm.resumo_service.obter_resumo = MagicMock(return_value=_criar_resumo_mock())
    vm.analisador.percentual_por_categoria = MagicMock(return_value={})
    vm.analisador.evolucao_mensal = MagicMock(return_value={})
    vm.analisador.receitas_vs_despesas_mensal = MagicMock(return_value=({}, {}))

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        dados = vm.carregar_periodo(2026, 6)

    movs = dados["tabela"]["movimentacoes"]
    assert len(movs) == 1
    assert isinstance(movs[0], dict)
    assert "id" in movs[0]
    assert "descricao" in movs[0]
    assert "valor" in movs[0]
    assert "categoria_nome" in movs[0]


def test_carregar_periodo_tabela_categorias_sao_dicts():
    """As categorias na tabela devem ser dicionários simples {'id': ..., 'nome': ...}."""
    vm = DashboardViewModel()
    cat_mock = _criar_cat_mock(id=1, nome="Alimentação")
    uow_mock = _montar_uow_mock(cats=[cat_mock])

    vm.resumo_service.obter_resumo = MagicMock(return_value=_criar_resumo_mock())
    vm.analisador.percentual_por_categoria = MagicMock(return_value={})
    vm.analisador.evolucao_mensal = MagicMock(return_value={})
    vm.analisador.receitas_vs_despesas_mensal = MagicMock(return_value=({}, {}))

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        dados = vm.carregar_periodo(2026, 6)

    cats = dados["tabela"]["categorias"]
    assert len(cats) == 1
    assert isinstance(cats[0], dict)
    assert cats[0]["id"] == 1
    assert cats[0]["nome"] == "Alimentação"


# ─────────────────────────────────────────────────────────────────────────────
# 2. ALTERAR_CATEGORIA_MOVIMENTACAO
# ─────────────────────────────────────────────────────────────────────────────

def test_alterar_categoria_chama_commit():
    """alterar_categoria_movimentacao deve chamar uow.commit() exatamente uma vez."""
    vm = DashboardViewModel()
    uow_mock = _montar_uow_mock()

    vm.mov_service.atualizar_categoria = MagicMock(return_value=True)
    vm.resumo_service.atualizar_resumo = MagicMock()
    vm.resumo_service.obter_resumo = MagicMock(return_value=_criar_resumo_mock())
    vm.analisador.percentual_por_categoria = MagicMock(return_value={})
    vm.analisador.evolucao_mensal = MagicMock(return_value={})
    vm.analisador.receitas_vs_despesas_mensal = MagicMock(return_value=({}, {}))

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        vm.alterar_categoria_movimentacao(movimentacao_id=1, categoria_id=2, ano=2026, mes=6)

    uow_mock.commit.assert_called_once()


def test_alterar_categoria_lanca_valor_error_quando_falha():
    """Se atualizar_categoria retornar False, deve lançar ValueError."""
    vm = DashboardViewModel()
    uow_mock = _montar_uow_mock()

    vm.mov_service.atualizar_categoria = MagicMock(return_value=False)

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        with pytest.raises(ValueError, match="reclassificação"):
            vm.alterar_categoria_movimentacao(movimentacao_id=99, categoria_id=2, ano=2026, mes=6)


# ─────────────────────────────────────────────────────────────────────────────
# 3. LISTAR_ANOS
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_anos_retorna_lista_de_strings():
    """listar_anos deve converter os anos para strings."""
    vm = DashboardViewModel()
    uow_mock = MagicMock()
    uow_mock.movimentacoes.obter_anos_disponiveis.return_value = [2026, 2025]

    with patch("ui.viewmodels.dashboard_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        anos = vm.listar_anos()

    assert anos == ["2026", "2025"]
    assert all(isinstance(a, str) for a in anos)
