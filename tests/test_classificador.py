"""
test_classificador.py (v2.0) — Testes unitários do ClassificadorService.
Utiliza MagicMock para isolar completamente a camada de banco de dados.
"""
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from application.classificador_service import ClassificadorService


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def criar_palavra_chave(texto: str, tipo: str, categoria_id: int, categoria_nome: str = "Categoria Teste"):
    """Cria um objeto PalavraChave simulado para uso nos testes sem banco."""
    chave = MagicMock()
    chave.texto = texto
    chave.tipo_movimentacao = tipo
    chave.categoria = MagicMock()
    chave.categoria.id = categoria_id
    chave.categoria.nome = categoria_nome
    return chave


@pytest.fixture
def palavras_chave():
    """Lista de palavras-chave simuladas para os testes."""
    return [
        criar_palavra_chave("RESTAURANTE", "despesa", 1, "Alimentação"),
        criar_palavra_chave("MERCADO",     "despesa", 1, "Alimentação"),
        criar_palavra_chave("IFOOD",       "despesa", 1, "Alimentação"),
        criar_palavra_chave("UBER",        "despesa", 2, "Transporte"),
        criar_palavra_chave("SALARIO",     "receita", 3, "Receita"),
        criar_palavra_chave("PIX RECEBIDO", "receita", 3, "Receita"),
        criar_palavra_chave("ESTORNO",     "ambos",   4, "Outros"),
    ]


@pytest.fixture
def service():
    return ClassificadorService()


# ─────────────────────────────────────────────────────────────────────────────
# 1. CLASSIFICAR_MOVIMENTACAO — LÓGICA DE MATCHING
# ─────────────────────────────────────────────────────────────────────────────

def test_classifica_palavra_chave_exata(service, palavras_chave):
    """Descrição contendo a palavra-chave exata deve retornar a categoria correta."""
    resultado = service.classificar_movimentacao("RESTAURANTE DA DONA MARIA", "despesa", palavras_chave)
    assert resultado == 1


def test_classifica_case_insensitive(service, palavras_chave):
    """Correspondência deve ser case-insensitive."""
    resultado = service.classificar_movimentacao("restaurante da esquina", "despesa", palavras_chave)
    assert resultado == 1


def test_classifica_palavra_chave_no_meio_da_descricao(service, palavras_chave):
    """Palavra-chave no meio da descrição deve ser reconhecida."""
    resultado = service.classificar_movimentacao("COMPRA IFOOD APP 12345", "despesa", palavras_chave)
    assert resultado == 1


def test_sem_match_retorna_none(service, palavras_chave):
    """Descrição sem nenhuma palavra-chave conhecida deve retornar None."""
    resultado = service.classificar_movimentacao("TARIFA BANCARIA DESCONHECIDA", "despesa", palavras_chave)
    assert resultado is None


def test_lista_vazia_retorna_none(service):
    """Com lista de palavras-chave vazia, deve retornar None sem erros."""
    resultado = service.classificar_movimentacao("RESTAURANTE DA MARIA", "despesa", [])
    assert resultado is None


# ─────────────────────────────────────────────────────────────────────────────
# 2. FILTRO POR TIPO DE MOVIMENTAÇÃO
# ─────────────────────────────────────────────────────────────────────────────

def test_nao_classifica_tipo_incorreto(service, palavras_chave):
    """Palavra-chave de tipo 'receita' NÃO deve classificar uma 'despesa'."""
    resultado = service.classificar_movimentacao("SALARIO MENSAL", "despesa", palavras_chave)
    assert resultado is None


def test_classifica_tipo_correto_receita(service, palavras_chave):
    """Palavra-chave de tipo 'receita' deve classificar uma 'receita'."""
    resultado = service.classificar_movimentacao("SALARIO MENSAL", "receita", palavras_chave)
    assert resultado == 3


def test_tipo_ambos_classifica_despesa(service, palavras_chave):
    """Palavra-chave com tipo 'ambos' deve classificar uma 'despesa'."""
    resultado = service.classificar_movimentacao("ESTORNO TARIFA", "despesa", palavras_chave)
    assert resultado == 4


def test_tipo_ambos_classifica_receita(service, palavras_chave):
    """Palavra-chave com tipo 'ambos' deve classificar uma 'receita'."""
    resultado = service.classificar_movimentacao("ESTORNO TARIFA", "receita", palavras_chave)
    assert resultado == 4


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLASSIFICAR_TODAS_MOVIMENTACOES — ORQUESTRAÇÃO VIA UOW MOCK
# ─────────────────────────────────────────────────────────────────────────────

def test_classificar_todas_atualiza_categoria_da_movimentacao(service):
    """Deve atualizar a categoria_id das movimentações sem categoria."""
    uow = MagicMock()

    # Categoria padrão
    cat_sem_cat = MagicMock()
    cat_sem_cat.id = 99
    uow.categorias.buscar_por_nome.return_value = cat_sem_cat

    # Movimentação sem categoria que deve ser classificada
    mov = MagicMock()
    mov.descricao = "RESTAURANTE DA MARIA"
    mov.tipo = "despesa"
    uow.movimentacoes.listar_por_categoria.return_value = [mov]

    # Palavras-chave disponíveis
    uow.palavras_chave.listar_com_categorias.return_value = [
        criar_palavra_chave("RESTAURANTE", "despesa", 1)
    ]

    service.classificar_todas_movimentacoes(uow)

    assert mov.categoria_id == 1


def test_classificar_todas_nao_altera_sem_match(service):
    """Movimentação sem palavra-chave correspondente não deve ter categoria alterada."""
    uow = MagicMock()

    cat_sem_cat = MagicMock()
    cat_sem_cat.id = 99
    uow.categorias.buscar_por_nome.return_value = cat_sem_cat

    mov = MagicMock()
    mov.descricao = "TARIFA DESCONHECIDA"
    mov.tipo = "despesa"
    # Guarda o valor original para comparar depois
    mov.categoria_id = 99
    uow.movimentacoes.listar_por_categoria.return_value = [mov]
    uow.palavras_chave.listar_com_categorias.return_value = []

    service.classificar_todas_movimentacoes(uow)

    # Categoria não deve ter mudado
    assert mov.categoria_id == 99


def test_classificar_todas_sem_categoria_padrao_nao_falha(service):
    """Se 'Sem categoria' não existir, deve encerrar silenciosamente sem erros."""
    uow = MagicMock()
    uow.categorias.buscar_por_nome.return_value = None

    # Não deve lançar exceção
    service.classificar_todas_movimentacoes(uow)

    # Nenhum repositório adicional deve ter sido chamado
    uow.movimentacoes.listar_por_categoria.assert_not_called()