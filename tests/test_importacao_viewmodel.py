"""
test_importacao_viewmodel.py — Testes unitários do ImportacaoViewModel.
Valida o tratamento de erros e a montagem de mensagens amigáveis para a UI.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ui.viewmodels.importacao_view_model import ImportacaoViewModel
from domain.exceptions import ImportacaoPendenteError


@pytest.fixture
def vm():
    return ImportacaoViewModel()


# ─────────────────────────────────────────────────────────────────────────────
# 1. VALIDAÇÕES DE ENTRADA
# ─────────────────────────────────────────────────────────────────────────────

def test_caminho_vazio_retorna_falha(vm):
    """Caminho de arquivo vazio deve retornar dict com sucesso=False."""
    resultado = vm.executar_importacao("")
    assert resultado["sucesso"] is False
    assert "selecionado" in resultado["mensagem"].lower()


def test_caminho_none_retorna_falha(vm):
    """Caminho None deve retornar dict com sucesso=False."""
    resultado = vm.executar_importacao(None)
    assert resultado["sucesso"] is False


# ─────────────────────────────────────────────────────────────────────────────
# 2. FORMATO NÃO SUPORTADO
# ─────────────────────────────────────────────────────────────────────────────

def test_formato_nao_suportado_retorna_falha(vm):
    """Arquivo em formato não reconhecido por nenhuma estratégia deve retornar sucesso=False."""
    # Mocka todas as estratégias para retornar False em pode_processar
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=False)

    resultado = vm.executar_importacao("/qualquer/caminho/arquivo.csv")
    assert resultado["sucesso"] is False
    assert "suportado" in resultado["mensagem"].lower() or "reconhecido" in resultado["mensagem"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 3. ERROS CAPTURADOS E CONVERTIDOS
# ─────────────────────────────────────────────────────────────────────────────

def test_file_not_found_retorna_mensagem_amigavel(vm):
    """FileNotFoundError deve ser capturado e retornar mensagem amigável."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=True)

    vm.importar.importar_extrato_completo = MagicMock(side_effect=FileNotFoundError("Arquivo não encontrado"))

    resultado = vm.executar_importacao("/nao/existe.csv")
    assert resultado["sucesso"] is False
    assert "não encontrado" in resultado["mensagem"].lower() or "encontrado" in resultado["mensagem"]


def test_value_error_retorna_mensagem_amigavel(vm):
    """ValueError deve ser capturado e retornar mensagem de validação."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=True)

    vm.importar.importar_extrato_completo = MagicMock(
        side_effect=ValueError("Estrutura inválida no arquivo.")
    )

    resultado = vm.executar_importacao("/qualquer/arquivo.csv")
    assert resultado["sucesso"] is False
    assert "validação" in resultado["mensagem"].lower() or "inválid" in resultado["mensagem"].lower()


def test_importacao_pendente_error_retorna_mensagem_amigavel(vm):
    """ImportacaoPendenteError deve ser capturado e retornar mensagem de atenção."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=True)

    erro = ImportacaoPendenteError(
        mensagem="Dados corrompidos na coluna valor.",
        df_incompleto=None,
        colunas_com_erro=["valor"],
        linhas_com_erro=[3, 7]
    )
    vm.importar.importar_extrato_completo = MagicMock(side_effect=erro)

    resultado = vm.executar_importacao("/qualquer/arquivo.csv")
    assert resultado["sucesso"] is False
    assert "atenção" in resultado["mensagem"].lower() or "corrompidos" in resultado["mensagem"].lower()


def test_excecao_generica_retorna_mensagem_de_erro_inesperado(vm):
    """Exception genérica deve ser capturada e retornar mensagem de erro inesperado."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=True)

    vm.importar.importar_extrato_completo = MagicMock(
        side_effect=RuntimeError("Erro de runtime inesperado")
    )

    resultado = vm.executar_importacao("/qualquer/arquivo.csv")
    assert resultado["sucesso"] is False
    assert "inesperado" in resultado["mensagem"].lower()


# ─────────────────────────────────────────────────────────────────────────────
# 4. FLUXO DE SUCESSO
# ─────────────────────────────────────────────────────────────────────────────

def test_importacao_sucesso_retorna_estrutura_correta(vm):
    """Importação bem-sucedida deve retornar dict com sucesso=True e contadores."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=True)

    vm.importar.importar_extrato_completo = MagicMock(return_value={
        "sucesso": True,
        "novas_importadas": 25,
        "ignoradas_duplicatas": 5,
        "mensagem": "25 novas movimentações importadas. 5 já existiam e foram ignoradas."
    })

    resultado = vm.executar_importacao("/qualquer/extrato.csv")
    assert resultado["sucesso"] is True
    assert resultado["novas_importadas"] == 25
    assert resultado["ignoradas_duplicatas"] == 5
    assert "mensagem" in resultado


def test_selecionar_estrategia_retorna_none_quando_nenhuma_aceita(vm):
    """_selecionar_estrategia deve retornar None se nenhuma estratégia aceitar o arquivo."""
    for estrategia in vm.estrategias_suportadas:
        estrategia.pode_processar = MagicMock(return_value=False)

    resultado = vm._selecionar_estrategia("/arquivo/qualquer.csv")
    assert resultado is None
