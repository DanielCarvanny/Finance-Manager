import os
import tempfile
from cryptography.fernet import Fernet


class ErroCriptografiaBanco(Exception):
    """Falha ao gerar ou gravar a cópia criptografada do banco."""

def obter_ou_criar_chave() -> bytes:
    """Gera ou recupera a chave AES-256 do usuário no APPDATA."""
    pasta_appdata = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), 'FinanceManager')
    os.makedirs(pasta_appdata, exist_ok=True)
    caminho_chave = os.path.join(pasta_appdata, 'secret.key')

    if not os.path.exists(caminho_chave):
        chave = Fernet.generate_key()

        with open(caminho_chave, 'wb') as f:
            f.write(chave)
        return chave
    with open(caminho_chave, 'rb') as f:
        return f.read().strip()
    
def criptografar_banco(caminho_db_plano: str, caminho_db_enc: str) -> None:
    """Criptografa o arquivo .db para .db.enc usando AES-256."""
    if not os.path.exists(caminho_db_plano):
        raise FileNotFoundError(
            f"Banco em texto plano não encontrado: {caminho_db_plano}"
        )
    try:
        chave = obter_ou_criar_chave()
        fernet = Fernet(chave)

        with open(caminho_db_plano, 'rb') as f:
            dados = f.read()

        dados_criptografados = fernet.encrypt(dados)
        salvar_arquivo_atomicamente(caminho_db_enc, dados_criptografados)

    except (OSError, ValueError) as erro:
        raise ErroCriptografiaBanco(
            "Não foi possível criar a cópia criptografada do banco. "
            "A cópia em texto plano foi mantida para evitar perda de dados."
        ) from erro

def descriptografar_banco(caminho_db_enc: str, caminho_db_plano: str):
    """Descriptografa o arquivo .db.enc para uso da sessão."""
    if not os.path.exists(caminho_db_enc):
        return
    
    chave = obter_ou_criar_chave()
    fernet = Fernet(chave)

    with open(caminho_db_enc, 'rb') as f:
        dados_criptografados = f.read()
        
    dados_planos = fernet.decrypt(dados_criptografados)

    salvar_arquivo_atomicamente(caminho_db_plano, dados_planos)

def salvar_arquivo_atomicamente(caminho: str, conteudo: bytes) -> None:
    """Grava um arquivo sem substituir uma versão válida por uma gravação parcial."""
    pasta = os.path.dirname(caminho)
    caminho_temp = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=pasta,
            delete=False,
            prefix="finance_manager_",
            suffix=".tmp",
        ) as arquivo_temporario:
            arquivo_temporario.write(conteudo)
            arquivo_temporario.flush()
            os.fsync(arquivo_temporario.fileno())
            caminho_temp = arquivo_temporario.name

        os.replace(caminho_temp, caminho)
    except OSError:
        if caminho_temp and os.path.exists(caminho_temp):
            try:
                os.remove(caminho_temp)
            except OSError:
                pass
        raise
