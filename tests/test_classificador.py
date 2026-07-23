import sys
import os
import pytest
from unittest.mock import MagicMock

# Garante que o Python ache a pasta src
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, caminho_src)

from application.classificador_service import classificar_movimentacao


# ─────────────────────────────────────────────
# FIXTURE: Palavras-chave simuladas em memória
# ─────────────────────────────────────────────

def criar_palavra_chave(texto: str, tipo: str, categoria_id: int, categoria_nome: str):
    """Cria um objeto PalavraChave simulado (mock) para usar nos testes sem banco."""
    chave = MagicMock()
    chave.texto = texto
    chave.tipo_movimentacao = tipo
    chave.categoria = MagicMock()
    chave.categoria.id = categoria_id
    chave.categoria.nome = categoria_nome
    return chave


@pytest.fixture
def palavras_chave_banco():
    """Fixture com uma lista de palavras-chave simuladas para os testes."""
    return [
        criar_palavra_chave("RESTAURANTE", "despesa", 1, "Alimentação"),
        criar_palavra_chave("MERCADO",     "despesa", 1, "Alimentação"),
        criar_palavra_chave("IFOOD",       "despesa", 1, "Alimentação"),
        criar_palavra_chave("UBER",        "despesa", 2, "Transporte"),
        criar_palavra_chave("SALARIO",     "receita", 3, "Receita"),
        criar_palavra_chave("PIX RECEBIDO","receita", 3, "Receita"),
        criar_palavra_chave("ESTORNO",     "ambos",   4, "Outros"),
    ]


# ─────────────────────────────────────────────
# TESTES: classificar_movimentacao()
# ─────────────────────────────────────────────

def test_classifica_palavra_chave_exata(palavras_chave_banco):
    """Descrição contendo a palavra-chave exata deve retornar a categoria correta."""
    resultado = classificar_movimentacao("RESTAURANTE DA DONA MARIA", "despesa", palavras_chave_banco)
    assert resultado == 1  # ID da categoria Alimentação

def test_classifica_case_insensitive(palavras_chave_banco):
    """Correspondência deve ser case-insensitive (minúsculas vs maiúsculas)."""
    resultado = classificar_movimentacao("restaurante da esquina", "despesa", palavras_chave_banco)
    assert resultado == 1

def test_classifica_palavra_chave_no_meio(palavras_chave_banco):
    """Palavra-chave no meio da descrição deve ser reconhecida."""
    resultado = classificar_movimentacao("COMPRA IFOOD APP 12345", "despesa", palavras_chave_banco)
    assert resultado == 1

def test_sem_match_retorna_none(palavras_chave_banco):
    """Descrição sem nenhuma palavra-chave conhecida deve retornar None."""
    resultado = classificar_movimentacao("TARIFA BANCARIA DESCONHECIDA", "despesa", palavras_chave_banco)
    assert resultado is None

def test_filtra_tipo_incorreto(palavras_chave_banco):
    """Palavra-chave de tipo 'receita' NÃO deve classificar uma 'despesa'."""
    resultado = classificar_movimentacao("SALARIO MENSAL", "despesa", palavras_chave_banco)
    assert resultado is None

def test_filtra_tipo_correto(palavras_chave_banco):
    """Palavra-chave de tipo 'receita' deve classificar uma 'receita' normalmente."""
    resultado = classificar_movimentacao("SALARIO MENSAL", "receita", palavras_chave_banco)
    assert resultado == 3  # ID da categoria Receita

def test_tipo_ambos_classifica_despesa(palavras_chave_banco):
    """Palavra-chave com tipo 'ambos' deve classificar uma 'despesa'."""
    resultado = classificar_movimentacao("ESTORNO TARIFA", "despesa", palavras_chave_banco)
    assert resultado == 4

def test_tipo_ambos_classifica_receita(palavras_chave_banco):
    """Palavra-chave com tipo 'ambos' deve classificar uma 'receita'."""
    resultado = classificar_movimentacao("ESTORNO TARIFA", "receita", palavras_chave_banco)
    assert resultado == 4

def test_lista_vazia_retorna_none():
    """Com lista de palavras-chave vazia, deve retornar None sem erros."""
    resultado = classificar_movimentacao("RESTAURANTE DA MARIA", "despesa", [])
    assert resultado is None
