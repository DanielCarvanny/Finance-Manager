from domain.models.palavra_chave import PalavraChave
from domain.models.categoria import Categoria
from utils.logger import logger

PALAVRAS_CHAVE_INICIAIS = [
    # Alimentação
    {"texto": "RESTAURANTE", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "MERCADO", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "IFOOD", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "LANCHES", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "CAFE", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "BURGER KING", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "HORTIFRUTI", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "BAR", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "PIZZARIA", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "KFC", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "MCDONALDS", "tipo": "despesa", "categoria": "Alimentação"},
    {"texto": "CHOP", "tipo": "despesa", "categoria": "Alimentação"},
    
    
    # Transporte
    {"texto": "UBER", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "POSTO", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "ESTACIONAMENTO", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "99* POP", "tipo": "despesa", "categoria": "Transporte"},
    {"texto": "BILHETE DIGITAL", "tipo": "despesa", "categoria": "Transporte"},
    
    # Receitas
    {"texto": "PIX RECEBIDO", "tipo": "receita", "categoria": "Receita"},
    {"texto": "SALARIO", "tipo": "receita", "categoria": "Receita"},
    {"texto": "TRANSFERENCIA RECEBIDA", "tipo": "receita", "categoria": "Receita"},

    # Saúde
    {"texto": "FARMACIA", "tipo": "despesa", "categoria": "Saúde"},
    {"texto": "TOTAL PASS", "tipo": "despesa", "categoria": "Saúde"},

    # Educação
    {"texto": "CURSO", "tipo": "despesa", "categoria": "Educação"},
    {"texto": "ESCOLA", "tipo": "despesa", "categoria": "Educação"},
    {"texto": "AUTOESCOLA", "tipo": "despesa", "categoria": "Educação"},

]

CATEGORIAS_PADRAO = [
    {"nome": "Alimentação", "cor": "#FF6384", "descricao": "Restaurantes, mercado, delivery"},
    {"nome": "Transporte", "cor": "#36A2EB", "descricao": "Combustível, ônibus, metrô, apps"},
    {"nome": "Lazer", "cor": "#FFCE56", "descricao": "Cinema, streaming, viagens, jogos"},
    {"nome": "Moradia", "cor": "#4BC0C0", "descricao": "Aluguel, condomínio, contas de casa"},
    {"nome": "Saúde", "cor": "#9966FF", "descricao": "Farmácia, consultas, plano de saúde"},
    {"nome": "Investimentos", "cor": "#FF9F40", "descricao": "Ações, renda fixa, cripto"},
    {"nome": "Educação", "cor": "#BC23F8", "descricao": "Ações, renda fixa, cripto"},
    {"nome": "Sem categoria", "cor": "#C9CBCF", "descricao": "Movimentações não classificadas"},
    {"nome": "Receita", "cor": "#0AA10A", "descricao": "Salário, bônus, rendimentos"},
]

def popular_palavras_chave(session):
    """
    Função para popular as palavras-chave iniciais no banco de dados.
    """
    for item in PALAVRAS_CHAVE_INICIAIS:
        # Verifica se a categoria já existe no banco de dados
        categoria = session.query(Categoria).filter_by(nome=item["categoria"]).first()

        if categoria:
            # Verifica se a palavra-chave já existe no banco de dados
            existing_palavra_chave = session.query(PalavraChave).filter_by(texto=item["texto"], tipo_movimentacao=item["tipo"]).first()

            if not existing_palavra_chave:
                nova_palavra = PalavraChave(
                    texto=item["texto"],
                    tipo_movimentacao=item["tipo"],
                    categoria_id=categoria.id
                )
                session.add(nova_palavra)
    session.commit()

def popular_categorias(session):
    """
    Função para popular as categorias padrão no banco de dados.
    """
    for item in CATEGORIAS_PADRAO:
        # Verifica se a categoria já existe no banco de dados
        existing_categoria = session.query(Categoria).filter_by(nome=item["nome"]).first()
        if not existing_categoria:
            nova_categoria = Categoria(
                nome=item["nome"],
                cor=item["cor"],
                descricao=item["descricao"]
            )
            session.add(nova_categoria)
    session.commit()


def executar_populacao_inicial(session, op: str):
    """
    Função para executar a população inicial do banco de dados.
    """
    if op == "cat":
        popular_categorias(session)
    elif op == "chave":
        popular_palavras_chave(session)
    elif op == "ambas":
        popular_categorias(session)
        popular_palavras_chave(session)

    logger.info("Categorias e palavras-chave verificadas e populadas.")

def verificar_populacao_inicial(session):
    """
    Verifica de forma eficiente se categorias e palavras-chave já foram inicializadas.
    """
    tem_categorias = session.query(Categoria.id).first() is not None
    tem_palavras_chave = session.query(PalavraChave.id).first() is not None

    if not tem_categorias and not tem_palavras_chave:
        executar_populacao_inicial(session, "ambas")
        logger.info("População inicial de categorias e palavras-chave executada.")
    elif not tem_categorias:
        executar_populacao_inicial(session, "cat")
        logger.info("População inicial de categorias executada.")
    elif not tem_palavras_chave:
        executar_populacao_inicial(session, "chave")
        logger.info("População inicial de palavras-chave executada.")
    else:
        logger.info("População inicial de banco de dados já verificada e em dia.")
