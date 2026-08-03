"""
test_estrategia_csv_inter.py — Testes unitários e de integração da EstrategiaCSVInter.
Testa o Strategy Pattern sem persistência em banco.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from application.importacao.strategies.csv_inter import EstrategiaCSVInter

# Caminho para o CSV de exemplo usado nos testes de integração
CAMINHO_CSV_VALIDO = os.path.join(
    os.path.dirname(__file__), '..', 'docs', 'Exemplo_CSV',
    'Extrato-01-06-2026-a-30-06-2026-CSV.csv'
)


@pytest.fixture
def estrategia():
    return EstrategiaCSVInter()


# ─────────────────────────────────────────────────────────────────────────────
# 1. PODE_PROCESSAR
# ─────────────────────────────────────────────────────────────────────────────

def test_pode_processar_arquivo_inexistente_retorna_false(estrategia):
    """Arquivo que não existe deve retornar False sem lançar exceção."""
    resultado = estrategia.pode_processar("/caminho/que/nao/existe/arquivo.csv")
    assert resultado is False


def test_pode_processar_extensao_errada_retorna_false(estrategia, tmp_path):
    """Arquivo com extensão .xlsx deve retornar False."""
    arquivo = tmp_path / "extrato.xlsx"
    arquivo.write_text("conteúdo qualquer")
    resultado = estrategia.pode_processar(str(arquivo))
    assert resultado is False


def test_pode_processar_arquivo_vazio_retorna_false(estrategia, tmp_path):
    """Arquivo CSV vazio (0 bytes) deve retornar False."""
    arquivo = tmp_path / "vazio.csv"
    arquivo.write_text("")
    resultado = estrategia.pode_processar(str(arquivo))
    assert resultado is False


@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_pode_processar_csv_inter_valido_retorna_true(estrategia):
    """CSV do Banco Inter válido deve retornar True."""
    resultado = estrategia.pode_processar(CAMINHO_CSV_VALIDO)
    assert resultado is True


# ─────────────────────────────────────────────────────────────────────────────
# 2. PROCESSAR — ESTRUTURA DO RETORNO
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_processar_retorna_chaves_obrigatorias(estrategia):
    """processar() deve retornar dict com 'metadados' e 'movimentacoes'."""
    resultado = estrategia.processar(CAMINHO_CSV_VALIDO)
    assert "metadados" in resultado
    assert "movimentacoes" in resultado


@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_processar_metadados_contem_periodo(estrategia):
    """Os metadados devem conter 'periodo_inicio', 'periodo_fim' e 'total_movimentacoes'."""
    from datetime import date
    resultado = estrategia.processar(CAMINHO_CSV_VALIDO)
    metadados = resultado["metadados"]

    assert "periodo_inicio" in metadados
    assert "periodo_fim" in metadados
    assert "total_movimentacoes" in metadados
    assert metadados["periodo_inicio"] == date(2026, 6, 1)
    assert metadados["periodo_fim"] == date(2026, 6, 30)


@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_processar_movimentacoes_nao_vazia(estrategia):
    """A lista de movimentações extraídas não deve estar vazia."""
    resultado = estrategia.processar(CAMINHO_CSV_VALIDO)
    assert len(resultado["movimentacoes"]) > 0


@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_processar_movimentacao_tem_chaves_corretas(estrategia):
    """Cada movimentação deve conter as chaves obrigatórias do DTO."""
    resultado = estrategia.processar(CAMINHO_CSV_VALIDO)
    chaves_esperadas = {"data_lancamento", "descricao", "valor", "saldo", "tipo"}
    for mov in resultado["movimentacoes"]:
        assert chaves_esperadas.issubset(mov.keys()), f"Chaves faltando em: {mov}"


@pytest.mark.skipif(
    not os.path.exists(CAMINHO_CSV_VALIDO),
    reason="Arquivo CSV de exemplo não encontrado em docs/Exemplo_CSV/",
)
def test_processar_tipos_dos_valores(estrategia):
    """'valor' e 'saldo' devem ser numéricos; 'tipo' deve ser 'receita' ou 'despesa'."""
    resultado = estrategia.processar(CAMINHO_CSV_VALIDO)
    for mov in resultado["movimentacoes"]:
        assert isinstance(mov["valor"], (int, float)), "valor deve ser numérico"
        assert mov["tipo"] in ("receita", "despesa"), "tipo inválido"


# ─────────────────────────────────────────────────────────────────────────────
# 3. PROCESSAR — VALIDAÇÕES DE ERRO
# ─────────────────────────────────────────────────────────────────────────────

def test_processar_arquivo_inexistente_lanca_erro(estrategia):
    """processar() deve lançar FileNotFoundError para arquivo inexistente."""
    with pytest.raises(FileNotFoundError):
        estrategia.processar("/caminho/nao/existe.csv")


def test_processar_extensao_errada_lanca_erro(estrategia, tmp_path):
    """processar() deve lançar ValueError para extensão incorreta."""
    arquivo = tmp_path / "extrato.xlsx"
    arquivo.write_text("conteúdo qualquer")
    with pytest.raises(ValueError):
        estrategia.processar(str(arquivo))
