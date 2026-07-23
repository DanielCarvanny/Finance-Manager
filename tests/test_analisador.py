import sys
import os
import pytest
from datetime import date

# Garante que o Python ache a pasta src
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, caminho_src)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.models.base import Base
from domain.models.categoria import Categoria
from domain.models.movimentacao import Movimentacao
from domain.models.importacao import Importacao
from application.analisador_service import (
    calcular_resumo_mensal,
    percentual_por_categoria,
    evolucao_mensal,
)


# ─────────────────────────────────────────────
# FIXTURE: Banco SQLite em memória
# ─────────────────────────────────────────────

@pytest.fixture
def db_session():
    """
    Cria um banco SQLite em memória isolado para cada teste.
    Os dados são destruídos ao final de cada função de teste.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # ── Categorias base ──────────────────────
    cat_alimentacao = Categoria(nome="Alimentação", cor="#FF6384", descricao="Restaurantes")
    cat_transporte  = Categoria(nome="Transporte",  cor="#36A2EB", descricao="Combustível")
    cat_receita     = Categoria(nome="Receita",     cor="#0AA10A", descricao="Salário")
    session.add_all([cat_alimentacao, cat_transporte, cat_receita])
    session.flush()

    # ── Registro pai de importação ───────────
    importacao = Importacao(
        nome_arquivo="teste.csv",
        periodo_inicio=date(2026, 6, 1),
        periodo_fim=date(2026, 6, 30),
        status="sucesso",
        total_movimentacoes=4
    )
    session.add(importacao)
    session.flush()

    # ── Movimentações controladas (Junho/2026) ──
    movimentacoes = [
        Movimentacao(data_lancamento=date(2026, 6, 5),  descricao="SALARIO",         valor=5000.00, saldo=5000.00, tipo="receita", importacao_id=importacao.id, categoria_id=cat_receita.id),
        Movimentacao(data_lancamento=date(2026, 6, 10), descricao="RESTAURANTE",      valor=-200.00, saldo=4800.00, tipo="despesa", importacao_id=importacao.id, categoria_id=cat_alimentacao.id),
        Movimentacao(data_lancamento=date(2026, 6, 15), descricao="IFOOD",            valor=-100.00, saldo=4700.00, tipo="despesa", importacao_id=importacao.id, categoria_id=cat_alimentacao.id),
        Movimentacao(data_lancamento=date(2026, 6, 20), descricao="UBER",             valor=-60.00,  saldo=4640.00, tipo="despesa", importacao_id=importacao.id, categoria_id=cat_transporte.id),
    ]
    session.add_all(movimentacoes)
    session.commit()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


# ─────────────────────────────────────────────
# TESTES: calcular_resumo_mensal()
# ─────────────────────────────────────────────

def test_total_receitas(db_session):
    """Soma das receitas de junho/2026 deve ser 5000.00."""
    resumo = calcular_resumo_mensal(db_session, 2026, 6)
    assert resumo["total_receitas"] == 5000.00

def test_total_despesas(db_session):
    """Soma das despesas de junho/2026 deve ser 360.00 (positivo)."""
    resumo = calcular_resumo_mensal(db_session, 2026, 6)
    assert resumo["total_despesas"] == 360.00

def test_saldo_periodo(db_session):
    """Saldo deve ser receitas - despesas = 5000 - 360 = 4640.00."""
    resumo = calcular_resumo_mensal(db_session, 2026, 6)
    assert resumo["saldo_periodo"] == pytest.approx(4640.00, rel=1e-2)

def test_gasto_medio_diario(db_session):
    """Gasto médio diário = total_despesas / 30 dias de junho."""
    resumo = calcular_resumo_mensal(db_session, 2026, 6)
    esperado = 360.00 / 30
    assert resumo["gasto_medio_diario"] == pytest.approx(esperado, rel=1e-2)

def test_mes_sem_dados_retorna_zeros(db_session):
    """Mês sem nenhuma movimentação deve retornar zeros sem lançar exceção."""
    resumo = calcular_resumo_mensal(db_session, 2025, 1)
    assert resumo["total_receitas"] == 0.0
    assert resumo["total_despesas"] == 0.0
    assert resumo["saldo_periodo"] == 0.0

def test_categoria_maior_gasto(db_session):
    """A categoria com maior despesa (Alimentação: -300) deve ser identificada."""
    resumo = calcular_resumo_mensal(db_session, 2026, 6)
    # Alimentação tem -300 (soma de -200 + -100), Transporte tem -60
    # Maior gasto = o mais negativo = Alimentação
    assert resumo["categoria_maior_gasto_id"] is not None


# ─────────────────────────────────────────────
# TESTES: percentual_por_categoria()
# ─────────────────────────────────────────────

def test_percentual_soma_100(db_session):
    """Os percentuais de todas as categorias devem somar ~100%."""
    percentuais = percentual_por_categoria(db_session, 2026, 6)
    total = sum(percentuais.values())
    assert total == pytest.approx(100.0, rel=1e-2)

def test_percentual_alimentacao(db_session):
    """Alimentação tem 300 de 360 total → ~83.33%."""
    percentuais = percentual_por_categoria(db_session, 2026, 6)
    assert percentuais.get("Alimentação") == pytest.approx(83.33, rel=1e-2)

def test_percentual_transporte(db_session):
    """Transporte tem 60 de 360 total → ~16.67%."""
    percentuais = percentual_por_categoria(db_session, 2026, 6)
    assert percentuais.get("Transporte") == pytest.approx(16.67, rel=1e-2)

def test_percentual_mes_vazio(db_session):
    """Mês sem despesas deve retornar dicionário vazio sem lançar exceção."""
    percentuais = percentual_por_categoria(db_session, 2024, 1)
    assert percentuais == {}


# ─────────────────────────────────────────────
# TESTES: evolucao_mensal()
# ─────────────────────────────────────────────

def test_evolucao_retorna_junho(db_session):
    """Deve retornar o mês 6 no eixo_x e o total de despesas no eixo_y."""
    dados = evolucao_mensal(db_session, 2026)
    assert 6 in dados["mes"]

def test_evolucao_valor_junho(db_session):
    """O total de despesas de junho deve ser 360.00."""
    dados = evolucao_mensal(db_session, 2026)
    idx = dados["mes"].index(6)
    assert dados["total_despesas"][idx] == pytest.approx(360.00, rel=1e-2)

def test_evolucao_ano_sem_dados(db_session):
    """Ano sem dados deve retornar listas vazias sem lançar exceção."""
    dados = evolucao_mensal(db_session, 2020)
    assert dados["mes"] == []
    assert dados["total_despesas"] == []
