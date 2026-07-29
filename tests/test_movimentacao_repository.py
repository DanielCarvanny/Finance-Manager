"""
test_movimentacao_repository.py — Testes de integração da camada de persistência.
Utiliza banco SQLite em memória (via conftest.py) para isolar cada teste completamente.
"""
import pytest
from datetime import date, datetime
from infrastructure.repositories.movimentacao_repo import MovimentacaoRepository
from domain.models.movimentacao import Movimentacao


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURE LOCAL
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def repo(session):
    """Instancia o repositório usando a sessão em memória do conftest."""
    return MovimentacaoRepository(session)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CRUD BÁSICO
# ─────────────────────────────────────────────────────────────────────────────

def test_criar_e_buscar_por_id(repo, session, importacao_base, categoria_alimentacao):
    """Deve salvar uma movimentação e recuperá-la pelo ID corretamente."""
    mov = Movimentacao(
        data_lancamento=date(2026, 6, 10),
        descricao="Restaurante Teste",
        valor=-75.50,
        saldo=924.50,
        tipo="despesa",
        importacao_id=importacao_base.id,
        categoria_id=categoria_alimentacao.id,
    )
    repo.create(mov)
    session.commit()

    encontrada = repo.buscar_por_id(mov.id)
    assert encontrada is not None
    assert encontrada.descricao == "Restaurante Teste"
    assert float(encontrada.valor) == -75.50
    assert encontrada.tipo == "despesa"


# ─────────────────────────────────────────────────────────────────────────────
# 2. FILTROS POR PERÍODO
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_por_periodo_retorna_apenas_mes_correto(repo, movimentacoes_base):
    """Deve retornar somente as movimentações do mês solicitado (Junho/2026)."""
    resultado = repo.listar_por_periodo(2026, 6)
    # Fixture tem 2 em junho e 1 em julho
    assert len(resultado) == 2
    for mov in resultado:
        assert mov.data_lancamento.month == 6
        assert mov.data_lancamento.year == 2026


def test_listar_por_periodo_mes_vazio(repo, movimentacoes_base):
    """Busca num mês sem movimentações deve retornar lista vazia."""
    resultado = repo.listar_por_periodo(2025, 1)
    assert resultado == []


def test_listar_por_periodo_exclui_arquivadas(repo, session, movimentacoes_base):
    """Movimentações excluídas (lixeira) não devem aparecer na listagem do período."""
    mov_excluida = movimentacoes_base[0]
    mov_excluida.excluida = True
    mov_excluida.excluida_em = datetime.now()
    session.commit()

    resultado = repo.listar_por_periodo(2026, 6)
    ids_resultado = [m.id for m in resultado]
    assert mov_excluida.id not in ids_resultado


# ─────────────────────────────────────────────────────────────────────────────
# 3. LIXEIRA
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_excluidas_retorna_apenas_arquivadas(repo, session, movimentacoes_base):
    """Deve retornar somente movimentações com excluida=True."""
    # Arquiva a primeira movimentação
    mov_excluida = movimentacoes_base[0]
    mov_excluida.excluida = True
    mov_excluida.excluida_em = datetime.now()
    session.commit()

    excluidas = repo.listar_excluidas()
    assert len(excluidas) == 1
    assert excluidas[0].id == mov_excluida.id


def test_listar_excluidas_vazio(repo, movimentacoes_base):
    """Sem movimentações arquivadas, deve retornar lista vazia."""
    result = repo.listar_excluidas()
    assert result == []


def test_listar_excluidas_por_ids(repo, session, movimentacoes_base):
    """Deve retornar somente as excluídas cujos IDs foram fornecidos."""
    mov1 = movimentacoes_base[0]
    mov2 = movimentacoes_base[1]
    mov1.excluida = True
    mov1.excluida_em = datetime.now()
    mov2.excluida = True
    mov2.excluida_em = datetime.now()
    session.commit()

    resultado = repo.listar_excluidas_por_ids([mov1.id])
    assert len(resultado) == 1
    assert resultado[0].id == mov1.id


# ─────────────────────────────────────────────────────────────────────────────
# 4. AGREGAÇÕES FINANCEIRAS
# ─────────────────────────────────────────────────────────────────────────────

def test_calcular_total_receitas_com_periodo(repo, movimentacoes_base):
    """Deve somar apenas as receitas do mês de junho/2026."""
    total = repo.calcular_total_receitas(ano=2026, mes=6)
    assert total == pytest.approx(5000.00)


def test_calcular_total_despesas_com_periodo(repo, movimentacoes_base):
    """Deve somar apenas as despesas do mês de junho/2026 (valor absoluto)."""
    total = repo.calcular_total_despesas(ano=2026, mes=6)
    assert total == pytest.approx(50.00)


def test_calcular_total_receitas_sem_dados(repo):
    """Sem dados, o total de receitas deve ser 0.0."""
    total = repo.calcular_total_receitas(ano=2024, mes=1)
    assert total == 0.0


def test_calcular_total_despesas_exclui_arquivadas(repo, session, movimentacoes_base):
    """Movimentações arquivadas não devem entrar no cálculo de despesas."""
    mov_despesa = movimentacoes_base[0]  # R$ -50.00
    mov_despesa.excluida = True
    mov_despesa.excluida_em = datetime.now()
    session.commit()

    total = repo.calcular_total_despesas(ano=2026, mes=6)
    assert total == pytest.approx(0.00)


# ─────────────────────────────────────────────────────────────────────────────
# 5. ANOS DISPONÍVEIS
# ─────────────────────────────────────────────────────────────────────────────

def test_obter_anos_disponiveis_retorna_anos_distintos(repo, movimentacoes_base):
    """Deve retornar [2026, ...] pois há movimentações nos anos presentes na fixture."""
    anos = repo.obter_anos_disponiveis()
    assert 2026 in anos


def test_obter_anos_disponiveis_sem_dados_retorna_ano_atual(repo):
    """Sem movimentações ativas, deve retornar o ano atual como fallback."""
    from datetime import date
    anos = repo.obter_anos_disponiveis()
    assert date.today().year in anos


def test_obter_anos_disponiveis_ordem_decrescente(repo, movimentacoes_base):
    """Os anos devem estar em ordem decrescente (mais recente primeiro)."""
    anos = repo.obter_anos_disponiveis()
    assert anos == sorted(anos, reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# 6. DEDUPLICAÇÃO (ASSINATURAS)
# ─────────────────────────────────────────────────────────────────────────────

def test_obter_assinaturas_existentes(repo, movimentacoes_base):
    """Deve retornar um set de tuplas com as assinaturas das movimentações ativas."""
    assinaturas = repo.obter_assinaturas_existentes()
    assert isinstance(assinaturas, set)
    assert len(assinaturas) == 3  # 3 movimentações na fixture (todas ativas)


def test_obter_assinaturas_nao_inclui_excluidas(repo, session, movimentacoes_base):
    """Movimentações excluídas não devem entrar no conjunto de assinaturas."""
    mov = movimentacoes_base[0]
    mov.excluida = True
    mov.excluida_em = datetime.now()
    session.commit()

    assinaturas = repo.obter_assinaturas_existentes()
    assert len(assinaturas) == 2


# ─────────────────────────────────────────────────────────────────────────────
# 7. LISTAGENS POR IDS E CATEGORIA
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_movimentacoes_por_ids(repo, movimentacoes_base):
    """Deve retornar somente as movimentações cujos IDs foram solicitados."""
    ids = [movimentacoes_base[0].id, movimentacoes_base[1].id]
    resultado = repo.listar_movimentacoes_por_ids(ids)
    assert len(resultado) == 2


def test_listar_por_categoria(repo, movimentacoes_base, categoria_alimentacao):
    """Deve retornar todas as movimentações de uma categoria específica."""
    resultado = repo.listar_por_categoria(categoria_alimentacao.id)
    assert len(resultado) == 3  # Todas as fixtures usam categoria_alimentacao


def test_listar_estornos_ativos(repo, session, movimentacoes_base, importacao_base, categoria_alimentacao):
    """Deve identificar movimentações de estorno vinculadas aos IDs selecionados."""
    mov_original = movimentacoes_base[0]
    estorno = Movimentacao(
        data_lancamento=date(2026, 6, 20),
        descricao="Estorno Restaurante",
        valor=50.00,
        saldo=1000.00,
        tipo="receita",
        importacao_id=importacao_base.id,
        categoria_id=categoria_alimentacao.id,
        estorno_id=mov_original.id,
        excluida=False,
    )
    session.add(estorno)
    session.commit()

    estornos = repo.listar_estornos_ativos({mov_original.id})
    assert len(estornos) == 1
    assert estornos[0].estorno_id == mov_original.id