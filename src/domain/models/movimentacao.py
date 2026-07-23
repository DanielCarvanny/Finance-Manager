from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from domain.models.base import Base
from sqlalchemy import Boolean, DateTime
from datetime import datetime



class Movimentacao(Base):
    __tablename__ = 'movimentacao'  # Nome da tabela no banco de dados

    # Colunas
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_lancamento = Column(Date, nullable=False)  # Data do lançamento
    descricao = Column(String(255), nullable=False)  # Descrição do lançamento
    valor = Column(Numeric(10, 2), nullable=False)  # Valor do lançamento
    saldo = Column(Numeric(10, 2), nullable=True)  # Saldo do lançamento
    tipo = Column(String(8), nullable=False)  # Tipo do lançamento (receita ou despesa)
    estorno_id = Column(Integer, ForeignKey('movimentacao.id'), nullable=True)  # Referência a outro lançamento (para estorno)
    importacao_id= Column(Integer, ForeignKey('importacao.id'), nullable=False)  # Referência à importação
    categoria_id = Column(Integer, ForeignKey('categoria.id'), nullable=False)  # Referência à categoria
    excluida = Column(Boolean, nullable=False, default=False)
    excluida_em = Column(DateTime, nullable=True)

    # Relacionamentos
    categoria = relationship('Categoria', back_populates='movimentacoes')
    importacao = relationship('Importacao', back_populates='movimentacoes')
    movimentacao_original  = relationship('Movimentacao', remote_side=[id], back_populates='estornos_vinculados')
    estornos_vinculados = relationship('Movimentacao', back_populates='movimentacao_original')
    
    __table_args__ = (
        CheckConstraint("valor != 0", name='check_valor_movimentacao'),  # Restringe o valor para ser não-negativo
        CheckConstraint("tipo IN ('receita', 'despesa')", name='check_tipo_movimentacao'), # Restringe os valores possíveis para o tipo
        UniqueConstraint('data_lancamento', 'descricao', 'valor', 'saldo', name='uq_mov_deduplicacao'),
        Index('idx_mov_data', 'data_lancamento'),
        Index('idx_mov_categoria', 'categoria_id'),
        Index('idx_mov_tipo', 'tipo'),
        Index('idx_mov_importacao', 'importacao_id'),
        Index('idx_mov_excluida', 'excluida'),

    )
