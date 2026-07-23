"""initial_schema

Revision ID: 2026_07_23_1200
Revises: 
Create Date: 2026-07-23 12:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2026_07_23_1200'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela Categoria
    op.create_table(
        'categoria',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('cor', sa.String(length=7), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )

    # 2. Tabela Importacao
    op.create_table(
        'importacao',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nome_arquivo', sa.String(length=255), nullable=False),
        sa.Column('data_importacao', sa.DateTime(), nullable=False),
        sa.Column('periodo_inicio', sa.Date(), nullable=False),
        sa.Column('periodo_fim', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_movimentacoes', sa.Integer(), nullable=False),
        sa.CheckConstraint("status IN ('sucesso', 'erro')", name='check_status_importacao'),
        sa.CheckConstraint('total_movimentacoes >= 0', name='check_total_movimentacoes'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_importacao_data', 'importacao', ['data_importacao'], unique=False)
    op.create_index('idx_importacao_status', 'importacao', ['status'], unique=False)

    # 3. Tabela PalavraChave
    op.create_table(
        'palavra_chave',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('texto', sa.String(length=100), nullable=False),
        sa.Column('tipo_movimentacao', sa.String(length=8), nullable=True),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("tipo_movimentacao IN ('receita', 'despesa', 'ambos')", name='check_tipo_palavra_chave'),
        sa.ForeignKeyConstraint(['categoria_id'], ['categoria.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('texto', 'tipo_movimentacao', name='uq_palavra_texto')
    )
    op.create_index('idx_palavra_categoria', 'palavra_chave', ['categoria_id'], unique=False)

    # 4. Tabela Movimentacao
    op.create_table(
        'movimentacao',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('data_lancamento', sa.Date(), nullable=False),
        sa.Column('descricao', sa.String(length=255), nullable=False),
        sa.Column('valor', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('saldo', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('tipo', sa.String(length=8), nullable=False),
        sa.Column('estorno_id', sa.Integer(), nullable=True),
        sa.Column('importacao_id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.Column('excluida', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('excluida_em', sa.DateTime(), nullable=True),
        sa.CheckConstraint("valor != 0", name='check_valor_movimentacao'),
        sa.CheckConstraint("tipo IN ('receita', 'despesa')", name='check_tipo_movimentacao'),
        sa.ForeignKeyConstraint(['categoria_id'], ['categoria.id'], ),
        sa.ForeignKeyConstraint(['estorno_id'], ['movimentacao.id'], ),
        sa.ForeignKeyConstraint(['importacao_id'], ['importacao.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('data_lancamento', 'descricao', 'valor', 'saldo', name='uq_mov_deduplicacao')
    )
    op.create_index('idx_mov_categoria', 'movimentacao', ['categoria_id'], unique=False)
    op.create_index('idx_mov_data', 'movimentacao', ['data_lancamento'], unique=False)
    op.create_index('idx_mov_excluida', 'movimentacao', ['excluida'], unique=False)
    op.create_index('idx_mov_importacao', 'movimentacao', ['importacao_id'], unique=False)
    op.create_index('idx_mov_tipo', 'movimentacao', ['tipo'], unique=False)

    # 5. Tabela ResumoMensal
    op.create_table(
        'resumo_mensal',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('mes', sa.Integer(), nullable=False),
        sa.Column('total_receitas', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('total_despesas', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('saldo_periodo', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('gasto_medio_diario', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('categoria_maior_gasto_id', sa.Integer(), nullable=True),
        sa.Column('categoria_menor_gasto_id', sa.Integer(), nullable=True),
        sa.CheckConstraint("mes > 0 AND mes <= 12", name='check_mes_resumo_mensal'),
        sa.ForeignKeyConstraint(['categoria_maior_gasto_id'], ['categoria.id'], ),
        sa.ForeignKeyConstraint(['categoria_menor_gasto_id'], ['categoria.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ano', 'mes', name='uq_resumo_ano_mes')
    )
    op.create_index('idx_resumo_maior_cat', 'resumo_mensal', ['categoria_maior_gasto_id'], unique=False)
    op.create_index('idx_resumo_menor_cat', 'resumo_mensal', ['categoria_menor_gasto_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_resumo_menor_cat', table_name='resumo_mensal')
    op.drop_index('idx_resumo_maior_cat', table_name='resumo_mensal')
    op.drop_table('resumo_mensal')
    
    op.drop_index('idx_mov_tipo', table_name='movimentacao')
    op.drop_index('idx_mov_importacao', table_name='movimentacao')
    op.drop_index('idx_mov_excluida', table_name='movimentacao')
    op.drop_index('idx_mov_data', table_name='movimentacao')
    op.drop_index('idx_mov_categoria', table_name='movimentacao')
    op.drop_table('movimentacao')
    
    op.drop_index('idx_palavra_categoria', table_name='palavra_chave')
    op.drop_table('palavra_chave')
    
    op.drop_index('idx_importacao_status', table_name='importacao')
    op.drop_index('idx_importacao_data', table_name='importacao')
    op.drop_table('importacao')
    
    op.drop_table('categoria')
