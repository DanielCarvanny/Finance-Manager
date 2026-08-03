
class ImportacaoPendenteError(Exception):
    """
    Exceção lançada quando a importação possui dados corrompidos.
    Carrega o DataFrame incompleto para que a UI possa solicitar a correção manual.
    """
    def __init__(self, mensagem, df_incompleto, colunas_com_erro, linhas_com_erro):
        self.mensagem = mensagem
        self.df_incompleto = df_incompleto
        self.colunas_com_erro = colunas_com_erro
        self.linhas_com_erro = linhas_com_erro
        super().__init__(self.mensagem)
        

class ArquivamentoEstornoError(ValueError):
    """Impede arquivar apenas uma ponta de uma movimentação de estorno."""
    
    def __init__(self, mensagem):
        super().__init__(mensagem)