from application.importacao.strategies.base import EstrategiaImportacao
from infrastructure.importacao.parsers.csv_parser import CSVParser
from infrastructure.importacao.validators.inter_validator import InterValidator
from infrastructure.importacao.normalizers.extrato_normalizer import ExtratoNormalizer
import pandas as pd

class EstrategiaCSVInter(EstrategiaImportacao):
    """Estratégia de importação para extratos CSV do Banco Inter."""
    
    def __init__(self):
        self.parser = CSVParser()
        self.validator = InterValidator()
        self.normalizer = ExtratoNormalizer()
    
    def pode_processar(self, caminho_arquivo: str) -> bool:
        try:
            self.validator.validar_arquivo(caminho_arquivo)
            return True
        except (FileNotFoundError, ValueError):
            return False
    
    def processar(self, caminho_arquivo: str) -> dict:
        # Valida o arquivo físico (existência, extensão, tamanho)
        self.validator.validar_arquivo(caminho_arquivo)
        
        # Extrai o período do cabeçalho
        periodo_inicio, periodo_fim = self.parser.extrair_periodo(caminho_arquivo)
        
        # Localiza o cabeçalho das movimentações e o delimitador
        indice_cabecalho, delimitador = self.parser.localizar_cabecalho_e_delimitador(caminho_arquivo)
        
        # Lê o CSV bruto como DataFrame
        try:
            df = pd.read_csv(caminho_arquivo, skiprows= indice_cabecalho, sep= delimitador, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(caminho_arquivo, skiprows= indice_cabecalho, sep= delimitador, encoding='latin1')
        
        # Valida a estrutura do DataFrame (colunas obrigatórias)
        valido, erro = self.validator.validar_estrutura(df)
        if not valido:
            raise ValueError(f"Estrutura inválida: {erro}")
        
        # Normaliza os dados (tipos, datas, valores)
        df = self.normalizer.normalizar_dados(df)
        
        # Extrai as movimentações como lista de dicionários
        movs = self.parser.extrair_dados(df)
        
        # Retorna o dicionário padronizado
        return{
            "metadados":{
                "periodo_inicio": periodo_inicio,
                "periodo_fim": periodo_fim,
                "total_movimentacoes": len(movs)
            },
            "movimentacoes": movs
        }