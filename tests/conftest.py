"""
conftest.py — Fixtures compartilhadas para toda a suíte de testes.
Configura um banco SQLite em memória limpo e isolado para cada teste.
"""
import sys
import os
import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Garante que o Python encontre o pacote src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from domain.models.base import Base
from domain.models.categoria import Categoria
from domain.models.importacao import Importacao
from domain.models.movimentacao import Movimentacao
from domain.models.palavra_chave import PalavraChave


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURE PRINCIPAL: Sessão SQLite em memória (isolada por teste)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def session():
    """
    Cria um banco SQLite em memória isolado para cada teste.
    As tabelas são criadas no início e destruídas ao final, garantindo
    total isolamento entre os testes.
    """
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    sess = SessionLocal()
    yield sess
    sess.close()
    Base.metadata.drop_all(engine)


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES DE DADOS: Entidades pré-criadas reutilizáveis
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def categoria_alimentacao(session):
    """Cria e persiste uma categoria 'Alimentação' no banco em memória."""
    cat = Categoria(nome="Alimentação", cor="#FF5733")
    session.add(cat)
    session.commit()
    return cat


@pytest.fixture
def categoria_sem_categoria(session):
    """Cria e persiste a categoria padrão 'Sem categoria' no banco em memória."""
    cat = Categoria(nome="Sem categoria", cor="#808080")
    session.add(cat)
    session.commit()
    return cat


@pytest.fixture
def categoria_transporte(session):
    """Cria e persiste uma categoria 'Transporte' no banco em memória."""
    cat = Categoria(nome="Transporte", cor="#3498DB")
    session.add(cat)
    session.commit()
    return cat


@pytest.fixture
def importacao_base(session, categoria_sem_categoria):
    """Cria e persiste um registro de Importacao base."""
    imp = Importacao(
        nome_arquivo="extrato_teste.csv",
        data_importacao=datetime(2026, 7, 1, 10, 0, 0),
        periodo_inicio=date(2026, 6, 1),
        periodo_fim=date(2026, 6, 30),
        status="sucesso",
        total_movimentacoes=3,
    )
    session.add(imp)
    session.commit()
    return imp


@pytest.fixture
def movimentacoes_base(session, importacao_base, categoria_alimentacao):
    """Cria um conjunto de movimentações para os testes."""
    movs = [
        Movimentacao(
            data_lancamento=date(2026, 6, 10),
            descricao="Restaurante da esquina",
            valor=-50.00,
            saldo=950.00,
            tipo="despesa",
            importacao_id=importacao_base.id,
            categoria_id=categoria_alimentacao.id,
            excluida=False,
        ),
        Movimentacao(
            data_lancamento=date(2026, 6, 15),
            descricao="Salário Mensal",
            valor=5000.00,
            saldo=5950.00,
            tipo="receita",
            importacao_id=importacao_base.id,
            categoria_id=categoria_alimentacao.id,
            excluida=False,
        ),
        Movimentacao(
            data_lancamento=date(2026, 7, 1),  # Mês diferente (julho)
            descricao="Compra Julho",
            valor=-100.00,
            saldo=5850.00,
            tipo="despesa",
            importacao_id=importacao_base.id,
            categoria_id=categoria_alimentacao.id,
            excluida=False,
        ),
    ]
    session.add_all(movs)
    session.commit()
    return movs
