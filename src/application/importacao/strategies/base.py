from abc import ABC, abstractmethod
from typing import Dict, Any

class EstrategiaImportacao(ABC):
    """
    Interface abstrata que estabelece o contrato para qualquer leitor de extrato bancário.
    """

    @abstractmethod
    def pode_processar(self, caminho_arquivo: str) -> bool:
        """
        Retorna True se a estratégia for capaz de ler o arquivo fornecido.
        """
        pass

    @abstractmethod
    def processar(self, caminho_arquivo: str) -> Dict[str, Any]:
        """
        Lê, valida e normaliza o extrato, retornando o dicionário com metadados e movimentações.
        """
        pass