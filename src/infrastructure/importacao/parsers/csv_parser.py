from typing import Optional, List, Dict
import re
from datetime import datetime, date
import pandas as pd

class CSVParser():
    """
    Extrai os dados brutos do CSV"
    """
    def _ler_linhas_iniciais(self,caminho_arquivo, quantidade: int = 10) -> list[str]:
        """
        Lê as primeiras linhas preservando suporte a caminhos e arquivos em memória.
        """
        if hasattr(caminho_arquivo, 'read'):
            posicao = caminho_arquivo.tell() if hasattr(caminho_arquivo, 'tell') else None
            if hasattr(caminho_arquivo, 'seek'):
                caminho_arquivo.seek(0)
            linhas = [caminho_arquivo.readline() for _ in range(quantidade)]
            if posicao is not None and hasattr(caminho_arquivo, 'seek'):
                caminho_arquivo.seek(posicao)
            return linhas

        for encoding in ('utf-8', 'latin1'):
            try:
                with open(caminho_arquivo, encoding=encoding) as arquivo:
                    return [arquivo.readline() for _ in range(quantidade)]
            except UnicodeDecodeError:
                continue

        raise ValueError("Não foi possível ler o arquivo do extrato.")
    
    def extrair_periodo(self,caminho_arquivo: str):
        """
        Lê o cabeçalho do arquivo para encontrar as datas de início e fim do período.
        Retorna uma tupla (periodo_inicio, periodo_fim) como objetos datetime.date.
        """
        try:
            linhas = self._ler_linhas_iniciais(caminho_arquivo, 15)
            # Primeiro busca linha identificada como período
            for linha in linhas:
                if 'período' in linha.lower() or 'periodo' in linha.lower():
                    datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', linha)
                    if len(datas) >= 2:
                        periodo_inicio = datetime.strptime(datas[0], '%d/%m/%Y').date()
                        periodo_fim = datetime.strptime(datas[1], '%d/%m/%Y').date()
                        return periodo_inicio, periodo_fim

            # Fallback: busca qualquer linha inicial com duas datas DD/MM/AAAA
            for linha in linhas:
                datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', linha)
                if len(datas) >= 2:
                    periodo_inicio = datetime.strptime(datas[0], '%d/%m/%Y').date()
                    periodo_fim = datetime.strptime(datas[1], '%d/%m/%Y').date()
                    return periodo_inicio, periodo_fim

            raise ValueError
        except Exception:
            raise ValueError("O arquivo não possui o cabeçalho padrão esperado. Não foi possível encontrar o Período.")
        
    def localizar_cabecalho_e_delimitador(self, caminho_arquivo: str) -> tuple[int, str]:
        """Localiza o cabeçalho de movimentações e seu delimitador (`,` ou `;`)."""
        linhas = self._ler_linhas_iniciais(caminho_arquivo, 20)
        for indice, linha in enumerate(linhas):
            linha_lower = linha.lower()
            if 'data' in linha_lower and ('descrição' in linha_lower or 'descricao' in linha_lower):
                delimitador = ';' if linha.count(';') >= linha.count(',') else ','
                return indice, delimitador
        raise ValueError("O arquivo não possui o cabeçalho de movimentações esperado.")
    
    def extrair_dados(self, df: pd.DataFrame) -> list[dict]:
        """
        Extrai os dados do DataFrame e retorna uma lista de dicionários.
        Cada dicionário representa uma movimentação.
        """
        movimentacoes_validadas = []

        for index, row in df.iterrows():
            valor = float(row['valor'])

            if valor == 0:
                continue  # Ignora movimentações com valor zero

            movimentacoes_validadas.append({
                'data_lancamento': row['data_lancamento'],
                'descricao': str(row['descricao']).strip(),
                'valor': valor,
                'saldo': float(row['saldo']) if not pd.isna(row['saldo']) else None,
                'tipo': 'despesa' if valor < 0 else 'receita'
            })
            
        return movimentacoes_validadas