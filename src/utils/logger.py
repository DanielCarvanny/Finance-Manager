import logging
import os
from datetime import datetime
def configurar_logger():
    """
    Configura o sistema de logs para gravar em arquivo (logs/app.log) 
    e simultaneamente exibir no terminal.
    """
    # Descobre a raiz do projeto e garante que a pasta 'logs' exista
    raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    pasta_logs = os.path.join(raiz, 'logs')

    os.makedirs(pasta_logs, exist_ok=True)

    caminho_log = os.path.join(pasta_logs, 'app.log')

    # Define o formato da mensagem (Data/Hora | Nível | Arquivo:Linha | Mensagem)
    formato = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Criador do Logger Principal
    logger = logging.getLogger("FinanceManager")
    logger.setLevel(logging.DEBUG)

    # Se já tiver manipuladores de log configurados, evita duplicar mensagens
    if logger.hasHandlers():
        logger.handlers.clear()

    # Manipulador 1: Grava no arquivo logs/app.log (Encoding utf-8)
    file_handler = logging.FileHandler(caminho_log, encoding='utf-8')
    file_handler.setFormatter(formato)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    # Manipulador 2: Exibe no terminal/console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger

# Instância global do logger pronta para uso em qualquer arquivo do projeto!
logger = configurar_logger()