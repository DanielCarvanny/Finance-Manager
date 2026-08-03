import os
import pandas as pd

class InterValidator():
    def validar_arquivo(self, caminho_arquivo: str) -> None:
        """
        Valida a existência, extensão e tamanho do arquivo antes de qualquer leitura.
        Lança excepcoes com mensagens amigáveis ao invés de erros técnicos do Python/Pandas.
        """
        if not os.path.exists(caminho_arquivo):
            raise FileNotFoundError(f"Arquivo não encontrado: '{os.path.basename(caminho_arquivo)}'. Verifique se o arquivo ainda existe no local selecionado.")

        if not caminho_arquivo.lower().endswith('.csv'):
            extensao = os.path.splitext(caminho_arquivo)[1] or 'desconhecida'
            raise ValueError(f"Formato inválido: o arquivo selecionado é '{extensao}'. Por favor, selecione um arquivo no formato '.csv'.")

        if os.path.getsize(caminho_arquivo) == 0:
            raise ValueError(f"O arquivo '{os.path.basename(caminho_arquivo)}' está vazio (0 bytes). Selecione um extrato válido.")
    
    def validar_estrutura(self, df: pd.DataFrame) -> tuple[bool, str | None]:
        """
        Verifica se a estrutura do DataFrame (lido do CSV) é válida.
        Retorna (True, None) se estiver correto, ou (False, "mensagem de erro").
        """
        # Verifica se o arquivo não está vazio
        if df.empty:
            return False, "O arquivo do extrato não contém dados de movimentação ou está vazio."
        
        # Verifica as colunas obrigatórias
        colunas_obrigatorias = ['Data Lançamento', 'Descrição', 'Valor', 'Saldo']

        for col in colunas_obrigatorias:
            if col not in df.columns:
                return False, f"Coluna obrigatória não encontrada: '{col}'. Verifique o cabeçalho do CSV."
        
        # Verifica compatibilidade de tipos (Data e Numérico) fazendo um teste na primeira linha
        try:
            primeira_linha = df.iloc[0]
            # Tenta converter a data
            pd.to_datetime(primeira_linha['Data Lançamento'], format= '%d/%m/%Y', dayfirst=True)

            # Tenta converter o valor
            valor_str = str(primeira_linha['Valor']).replace('.', '').replace(',', '.')
            float(valor_str)
        except Exception:
            return False, "Tipos de dados incompatíveis. A data deve ser DD/MM/AAAA e o valor deve ser numérico."
        
        # Se passou por tudo, está validado
        return True, None