import os
from typing import Optional
from application.importacao.importacao_service import ImportacaoService
from application.importacao.strategies.csv_inter import EstrategiaCSVInter
from application.importacao.strategies.base import EstrategiaImportacao
from domain.exceptions import ImportacaoPendenteError
from utils.logger import logger


class ImportacaoViewModel:
    def __init__(self):
        self.importar = ImportacaoService()
        # Lista de estratégias de extrato suportadas
        self.estrategias_suportadas: list[EstrategiaImportacao]= [
            EstrategiaCSVInter()
        ]
        
    def _selecionar_estrategia(self, caminho_arquivo: str) -> Optional[EstrategiaImportacao]:
        """Inspeciona o arquivo e descobre qual estratégia é capaz de processá-lo."""
        for estrategia in self.estrategias_suportadas:
            if estrategia.pode_processar(caminho_arquivo):
                return estrategia
        
        return None
        
    def executar_importacao(self, caminho_arquivo: str) -> dict:
        """
        Orquestra a importação, selecionando a estratégia e convertendo erros em mensagens amigáveis.
        """
        if not caminho_arquivo:
            return {"sucesso": False, "mensagem": "Nenhum arquivo foi selecionado."}
        
        try:
            logger.info(f"ImportacaoViewModel iniciando arquivo: {os.path.basename(caminho_arquivo)}")
            
            # Identifica a estratégia adequada
            estrategia = self._selecionar_estrategia(caminho_arquivo)
            if not estrategia:
                return {
                    "sucesso": False,
                    "mensagem": f"Formato não suportado: Layout do arquivo '{os.path.basename(caminho_arquivo)}' não reconhecido."
                }
            
            # Executa a importação no serviço
            resultado = self.importar.importar_extrato_completo(caminho_arquivo, estrategia)
            
            return {
                "sucesso": True,
                "mensagem": resultado["mensagem"],
                "novas_importadas": resultado["novas_importadas"],
                "ignoradas_duplicatas": resultado["ignoradas_duplicatas"]
            }
        except ImportacaoPendenteError as e:
            logger.warning(f"Importação pendente por dados corrompidos: {e.mensagem}")
            return {"sucesso": False, "mensagem": f"Atenção: {e.mensagem}"}
        except FileNotFoundError:
            return {"sucesso": False, "mensagem": f"Arquivo não encontrado: '{os.path.basename(caminho_arquivo)}'."}
        except ValueError as e:
            return {"sucesso": False, "mensagem": f"Erro de validação: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro inesperado no ImportacaoViewModel: {e}", exc_info=True)
            return {"sucesso": False, "mensagem": f"Erro inesperado ao importar: {str(e)}"}