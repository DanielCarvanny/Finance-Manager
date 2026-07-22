from sqlalchemy import Column, Integer, String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint
from models.base import Base

class PalavraChave(Base):
    __tablename__ = 'palavra_chave'  # Nome da tabela no banco de dados
    id = Column(Integer, primary_key=True, autoincrement=True)
    texto = Column(String(100), nullable=False)  # Texto da palavra-chave
    tipo_movimentacao = Column(String(8), nullable=True)  # Tipo de movimentação associada à palavra-chave (receita ou despesa)
    categoria_id = Column(Integer, ForeignKey('categoria.id'), nullable=True)  # Referência à categoria associada à palavra-chave

    # Relacionamentos
    categoria = relationship('Categoria', back_populates='palavras_chave')

    __table_args__ = (
        CheckConstraint("tipo_movimentacao IN ('receita', 'despesa', 'ambos')", name='check_tipo_palavra_chave'), 
        Index('idx_palavra_categoria', 'categoria_id'),
        UniqueConstraint('texto', 'tipo_movimentacao', name='uq_palavra_texto'),         
    )
