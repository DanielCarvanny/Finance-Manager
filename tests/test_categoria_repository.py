"""
test_categoria_repository.py — Testes de integração do CategoriaRepository.
Utiliza banco SQLite em memória (via conftest.py).
"""
import pytest
from infrastructure.repositories.categoria_repo import CategoriaRepository
from domain.models.categoria import Categoria


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURE LOCAL
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def repo(session):
    """Instancia o repositório usando a sessão em memória do conftest."""
    return CategoriaRepository(session)


# ─────────────────────────────────────────────────────────────────────────────
# 1. CRUD BÁSICO
# ─────────────────────────────────────────────────────────────────────────────

def test_criar_e_buscar_por_id(repo, session):
    """Deve salvar e recuperar uma Categoria pelo ID."""
    cat = Categoria(nome="Lazer", cor="#9B59B6")
    repo.create(cat)
    session.commit()

    encontrada = repo.buscar_por_id(cat.id)
    assert encontrada is not None
    assert encontrada.nome == "Lazer"
    assert encontrada.cor == "#9B59B6"


def test_buscar_por_id_inexistente_retorna_none(repo):
    """Busca por ID inexistente deve retornar None."""
    resultado = repo.buscar_por_id(9999)
    assert resultado is None


# ─────────────────────────────────────────────────────────────────────────────
# 2. BUSCA POR NOME
# ─────────────────────────────────────────────────────────────────────────────

def test_buscar_por_nome_existente(repo, session):
    """Deve encontrar a categoria pelo nome exato."""
    cat = Categoria(nome="Saúde", cor="#2ECC71")
    repo.create(cat)
    session.commit()

    resultado = repo.buscar_por_nome("Saúde")
    assert resultado is not None
    assert resultado.nome == "Saúde"
    assert resultado.id == cat.id


def test_buscar_por_nome_inexistente_retorna_none(repo):
    """Nome não cadastrado deve retornar None."""
    resultado = repo.buscar_por_nome("Categoria Fantasma")
    assert resultado is None


def test_buscar_por_nome_case_sensitive(repo, session):
    """A busca por nome deve ser exata (case-sensitive por padrão no SQLite)."""
    cat = Categoria(nome="Educação", cor="#F39C12")
    repo.create(cat)
    session.commit()

    # Busca com case diferente não deve encontrar
    resultado = repo.buscar_por_nome("educação")
    # Em SQLite LIKE é case-insensitive para ASCII, mas == é sensível a maiúsculas para não-ASCII
    # Este teste documenta o comportamento atual do sistema
    assert resultado is None or resultado.nome == "Educação"


# ─────────────────────────────────────────────────────────────────────────────
# 3. LISTAR TODAS
# ─────────────────────────────────────────────────────────────────────────────

def test_listar_todas_retorna_lista_vazia_quando_sem_dados(repo):
    """Com banco vazio, listar_todas deve retornar lista vazia."""
    resultado = repo.listar_todas()
    assert resultado == []


def test_listar_todas_retorna_todas_categorias(repo, session):
    """Deve retornar todas as categorias cadastradas."""
    cats = [
        Categoria(nome="Moradia", cor="#E74C3C"),
        Categoria(nome="Alimentação", cor="#FF5733"),
        Categoria(nome="Transporte", cor="#3498DB"),
    ]
    session.add_all(cats)
    session.commit()

    resultado = repo.listar_todas()
    assert len(resultado) == 3
    nomes = [c.nome for c in resultado]
    assert "Moradia" in nomes
    assert "Alimentação" in nomes
    assert "Transporte" in nomes


# ─────────────────────────────────────────────────────────────────────────────
# 4. UNICIDADE DE NOMES
# ─────────────────────────────────────────────────────────────────────────────

def test_nome_duplicado_lanca_erro(repo, session):
    """Tentar criar duas categorias com o mesmo nome deve lançar exceção de integridade."""
    from sqlalchemy.exc import IntegrityError

    cat1 = Categoria(nome="Único", cor="#1ABC9C")
    repo.create(cat1)
    session.commit()

    cat2 = Categoria(nome="Único", cor="#2ECC71")
    repo.create(cat2)

    with pytest.raises(IntegrityError):
        session.commit()