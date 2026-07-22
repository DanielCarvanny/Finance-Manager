from models.movimentacao import Movimentacao
from models.palavra_chave import PalavraChave
from models.categoria import Categoria
from sqlalchemy.orm import Session, joinedload


def buscar_palavras_chave(session: Session):
    """
    Retornar todas as palavras-chave do banco com sua categoria associada
    """

    palavras_chave = session.query(PalavraChave).options(joinedload(PalavraChave.categoria)).all()

    return palavras_chave

def classificar_movimentacao(descricao_mov: str, tipo: str, palavras_chave: list[PalavraChave]):
    """
    Verifica se para cada palavra-chave, o texto está contido na descricao.
    Filtra o tipo de movimentacao compatível (receita/despesa/ambos).
    Retornar o id da categoria correspondente ou None se não encontrar.
    """

    # Verificação se texto está contido em descricao
    for chave in palavras_chave:
        if chave.texto.lower() in descricao_mov.lower():
            if chave.tipo_movimentacao == 'ambos' or chave.tipo_movimentacao == tipo:
                return chave.categoria.id

    return None

def classificar_todas_movimentacoes(session: Session):
    """
    Classificar as movimentações que estão na categoria "Sem Categoria"
    """

    # Pega o ID da categoria "Sem categoria"
    cat_padrao = session.query(Categoria).filter_by(nome= 'Sem categoria').first()
    if not cat_padrao:
        return
    
    # Filtra as movimentações usando o ID correto
    movimentacao = session.query(Movimentacao).filter_by( excluida= False, categoria_id= cat_padrao.id).all()

    # Busca as palavras-chave APENAS UMA VEZ
    palavras_chave_banco = buscar_palavras_chave(session)

    for mov in movimentacao:
        nova_categoria_id = classificar_movimentacao(str(mov.descricao), str(mov.tipo), palavras_chave_banco)
        if nova_categoria_id:
            mov.categoria_id = nova_categoria_id
