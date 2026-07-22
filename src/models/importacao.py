from sqlalchemy import Column, Integer, String, DateTime, Index, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from models.base import Base

class Importacao(Base):
    __tablename__ = 'importacao'  # Nome da tabela no banco de dados

    # Colunas
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome_arquivo = Column(String(255), nullable=False)
    data_importacao = Column(DateTime, nullable=False, default=func.now())  # Data e hora da importação
    periodo_inicio = Column(Date, nullable=False)  # Período de início do extrato
    periodo_fim = Column(Date, nullable=False)  # Período de fim do extrato
    status = Column(String(20), nullable=False)  # Status da importação
    total_movimentacoes = Column(Integer, nullable=False)  # Total de movimentações importadas

    # Relacionamento
    movimentacoes = relationship('Movimentacao', back_populates='importacao')

    __table_args__ = (
        CheckConstraint("status IN ('sucesso', 'erro')", name='check_status_importacao'),  # Restringe os valores possíveis para o status
        CheckConstraint('total_movimentacoes >= 0', name='check_total_movimentacoes'),  # Garante que o total de movimentações seja não-negativo
        Index('idx_importacao_data', 'data_importacao'),
        Index('idx_importacao_status', 'status'),
    )

