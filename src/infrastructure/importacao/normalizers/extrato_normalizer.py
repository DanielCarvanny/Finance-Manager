import pandas as pd
from domain.exceptions import ImportacaoPendenteError

class ExtratoNormalizer():
    def normalizar_dados(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e formata as colunas para o padrão Python.
        Bloqueia a importação se encontrar dados corrompidos.
        Retorna o DataFrame normalizado.
        """

        # Renomeia as colunas
        df.columns= ['data_lancamento', 'descricao', 'valor', 'saldo']

        # Limpeza dos números
        texto_limpo_valor = df['valor'].astype(str).str.replace('.', '').str.replace(',', '.') 
        df['valor'] = pd.to_numeric(texto_limpo_valor, errors= 'coerce')

        texto_limpo_saldo = df['saldo'].astype(str).str.replace('.', '').str.replace(',', '.')
        df['saldo'] = pd.to_numeric(texto_limpo_saldo, errors='coerce')
        
        # Validação do Valor
        if df['valor'].isna().any():
            linhas_invalidas = df[df['valor'].isna()].index.tolist()

            raise ImportacaoPendenteError(
                "Existem transações com o campo 'Valor' em branco ou inválido. Insira o valor correto.",
                df_incompleto=df,
                colunas_com_erro=['valor'],
                linhas_com_erro=linhas_invalidas
            )

        # Limpeza das datas
        df['data_lancamento'] = pd.to_datetime(
            df['data_lancamento'], 
            format='mixed', 
            dayfirst=True,
            errors= 'coerce'
            ).dt.date
        
        if df['data_lancamento'].isna().any():
            linhas_invalidas = df[df['data_lancamento'].isna()].index.tolist()
            raise ImportacaoPendenteError(
                "Existem transações com a Data corrompida ou em branco.",
                df_incompleto=df,
                colunas_com_erro=['data_lancamento'],
                linhas_com_erro=linhas_invalidas
            )

        return df