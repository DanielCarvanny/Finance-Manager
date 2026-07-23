from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Classe base para todos os modelos do sistema.
    Herdar dela garante que as classes sejam mapeadas
    para tabelas do banco de dados automaticamente.
    """
    pass