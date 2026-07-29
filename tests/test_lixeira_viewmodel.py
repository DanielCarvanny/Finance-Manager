"""
test_lixeira_viewmodel.py — Testes unitários do LixeiraViewModel.
Valida o ciclo de arquivamento, listagem (como DTOs) e restauração.
"""
import sys
import os
import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ui.viewmodels.lixeira_view_model import LixeiraViewModel
from domain.exceptions import ArquivamentoEstornoError


@pytest.fixture
def vm():
    return LixeiraViewModel()


def _criar_mov_orm(id=1, descricao="Restaurante", valor=-50.0, categoria_nome="Alimentação"):
    """Cria um objeto Movimentacao ORM simulado (como retornado da sessão SQLAlchemy)."""
    mov = MagicMock()
    mov.id = id
    mov.data_lancamento = date(2026, 6, 10)
    mov.descricao = descricao
    mov.valor = valor
    mov.categoria = MagicMock()
    mov.categoria.nome = categoria_nome
    mov.excluida_em = datetime(2026, 7, 1, 15, 30)
    return mov


# ─────────────────────────────────────────────────────────────────────────────
# 1. ARQUIVAR MOVIMENTAÇÕES
# ─────────────────────────────────────────────────────────────────────────────

def test_arquivar_retorna_quantidade_arquivada(vm):
    """arquivar_movimentacoes deve retornar a quantidade movida para a lixeira."""
    uow_mock = MagicMock()
    vm.mov_service.arquivar_movimentacoes = MagicMock(return_value=3)

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        qtd = vm.arquivar_movimentacoes([1, 2, 3])

    assert qtd == 3
    uow_mock.commit.assert_called_once()


def test_arquivar_relancar_arquivamento_estorno_error(vm):
    """ArquivamentoEstornoError deve ser relançada para a UI tratar."""
    uow_mock = MagicMock()
    vm.mov_service.arquivar_movimentacoes = MagicMock(
        side_effect=ArquivamentoEstornoError("Selecione também a movimentação vinculada.")
    )

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        with pytest.raises(ArquivamentoEstornoError):
            vm.arquivar_movimentacoes([1])


def test_arquivar_excecao_generica_retorna_zero(vm):
    """Exceções genéricas devem ser absorvidas e retornar 0."""
    uow_mock = MagicMock()
    vm.mov_service.arquivar_movimentacoes = MagicMock(
        side_effect=RuntimeError("Falha de banco genérica")
    )

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        qtd = vm.arquivar_movimentacoes([1])

    assert qtd == 0


# ─────────────────────────────────────────────────────────────────────────────
# 2. LISTAR MOVIMENTAÇÕES DA LIXEIRA
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_retorna_lista_de_dicionarios(vm):
    """listar_movimentacoes_lixeira deve retornar list[dict], nunca objetos ORM."""
    uow_mock = MagicMock()
    movs_orm = [
        _criar_mov_orm(id=1, descricao="Restaurante", valor=-50.0),
        _criar_mov_orm(id=2, descricao="UBER", valor=-30.0),
    ]
    uow_mock.movimentacoes.listar_excluidas.return_value = movs_orm

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        resultado = vm.listar_movimentacoes_lixeira()

    assert len(resultado) == 2
    assert all(isinstance(item, dict) for item in resultado)


def test_listar_dicionarios_contem_chaves_obrigatorias(vm):
    """Cada DTO da lixeira deve conter as chaves esperadas pela JanelaLixeira."""
    uow_mock = MagicMock()
    uow_mock.movimentacoes.listar_excluidas.return_value = [
        _criar_mov_orm(id=10, descricao="Supermercado", valor=-80.0)
    ]

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        resultado = vm.listar_movimentacoes_lixeira()

    item = resultado[0]
    assert "id" in item
    assert "data_lancamento" in item
    assert "descricao" in item
    assert "valor" in item
    assert "categoria_nome" in item
    assert "excluida_em" in item
    assert item["id"] == 10
    assert item["descricao"] == "Supermercado"


def test_listar_com_categoria_none_usa_sem_categoria(vm):
    """Movimentação sem categoria deve exibir 'Sem categoria' no DTO."""
    uow_mock = MagicMock()
    mov = _criar_mov_orm()
    mov.categoria = None  # Sem categoria vinculada
    uow_mock.movimentacoes.listar_excluidas.return_value = [mov]

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        resultado = vm.listar_movimentacoes_lixeira()

    assert resultado[0]["categoria_nome"] == "Sem categoria"


def test_listar_lixeira_vazia_retorna_lista_vazia(vm):
    """Com lixeira vazia, deve retornar lista vazia sem erros."""
    uow_mock = MagicMock()
    uow_mock.movimentacoes.listar_excluidas.return_value = []

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        resultado = vm.listar_movimentacoes_lixeira()

    assert resultado == []


# ─────────────────────────────────────────────────────────────────────────────
# 3. RESTAURAR DA LIXEIRA
# ─────────────────────────────────────────────────────────────────────────────

def test_restaurar_retorna_quantidade_restaurada(vm):
    """restaurar_da_lixeira deve retornar a quantidade restaurada com sucesso."""
    uow_mock = MagicMock()
    vm.mov_service.restaurar_movimentacoes = MagicMock(return_value=2)

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        qtd = vm.restaurar_da_lixeira([10, 11])

    assert qtd == 2
    uow_mock.commit.assert_called_once()


def test_restaurar_excecao_retorna_none(vm):
    """Exceção na restauração deve ser absorvida e retornar None (ou 0)."""
    uow_mock = MagicMock()
    vm.mov_service.restaurar_movimentacoes = MagicMock(
        side_effect=RuntimeError("Falha na restauração")
    )

    with patch("ui.viewmodels.lixeira_view_model.UnitOfWork") as MockUoW:
        MockUoW.return_value.__enter__.return_value = uow_mock
        MockUoW.return_value.__exit__.return_value = False

        resultado = vm.restaurar_da_lixeira([10])

    # O ViewModel atual retorna None em caso de erro genérico — documento o contrato atual
    assert resultado is None or resultado == 0
