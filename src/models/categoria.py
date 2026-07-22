from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models.base import Base

class Categoria(Base):
    __tablename__ =  'categoria' # Nome da tabela no banco de dados

    # Colunas
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), unique=True, nullable=False)
    cor = Column(String(7), default='#808080')  # Cor padrão cinza
    descricao = Column(Text)

    # Relacionamentos
    movimentacoes = relationship('Movimentacao', back_populates='categoria')
    palavras_chave = relationship('PalavraChave', back_populates='categoria')

    def __repr__(self):
        """Representação amigável para debug"""
        return f"<Categoria(id={self.id}, nome='{self.nome}', cor='{self.cor}')>"