from sqlalchemy import Column, Integer, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from domain.models.base import Base

class ResumoMensal(Base): 
    __tablename__ = 'resumo_mensal'  # Nome da tabela no banco de dados
    id = Column(Integer, primary_key=True, autoincrement=True)
    ano = Column(Integer, nullable=False)  # Ano do resumo mensal
    mes = Column(Integer, nullable=False)  # Mês do resumo mensal
    total_receitas = Column(Numeric(12, 2), nullable=False, default=0.0)  # Total de receitas do mês
    total_despesas = Column(Numeric(12, 2), nullable=False, default=0.0)  # Total de despesas do mês
    saldo_periodo = Column(Numeric(12, 2), nullable=False, default=0.0)  # Saldo do período (receitas - despesas)
    gasto_medio_diario = Column(Numeric(12,2), nullable=True, default=0.0)  # Gasto médio diário do mês
    categoria_maior_gasto_id = Column(Integer, ForeignKey('categoria.id'), nullable=True)  # Referência à categoria com maior gasto no mês
    categoria_menor_gasto_id = Column(Integer, ForeignKey('categoria.id'), nullable=True)  # Referência à categoria com menor gasto no mês

    # Relacionamentos
    categoria_maior_gasto = relationship('Categoria', foreign_keys=[categoria_maior_gasto_id])
    categoria_menor_gasto = relationship('Categoria', foreign_keys=[categoria_menor_gasto_id])

    __table_args__ = (
        CheckConstraint("mes > 0 AND mes <= 12", name='check_mes_resumo_mensal'), 
        UniqueConstraint('ano', 'mes', name='uq_resumo_ano_mes'),
        Index('idx_resumo_maior_cat', 'categoria_maior_gasto_id'),
        Index('idx_resumo_menor_cat', 'categoria_menor_gasto_id'),

    )
