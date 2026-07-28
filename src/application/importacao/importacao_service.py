import os
from datetime import datetime, date
from domain.models.importacao import Importacao
from domain.models.movimentacao import Movimentacao
from application.importacao.strategies.base import EstrategiaImportacao
from infrastructure.database.unit_of_work import UnitOfWork
from application.classificador_service import ClassificadorService
from utils.logger import logger

class ImportacaoService:
    """
    Orquestra a importação de extratos bancários de forma genérica.
    """
    def registrar_importacao(self, uow: UnitOfWork, nome: str, periodo_inicio: date, periodo_fim: date, total_movimentacoes: int) -> Importacao:
        """
        Registra a entidade pai Importacao no banco de dados.
        """
        nova_importacao = Importacao(
            nome_arquivo= nome,
            periodo_inicio= periodo_inicio,
            periodo_fim= periodo_fim,
            status= 'sucesso',
            data_importacao= datetime.now(),
            total_movimentacoes= total_movimentacoes
        )
        uow.session.add(nova_importacao)
        uow.session.flush()
        return nova_importacao

    def importar_extrato_completo(self, caminho_arquivo: str, estrategia: EstrategiaImportacao) -> dict:
        """
        Função principal invocada pela UI / ViewModel.
        Recebe qualquer estratégia (Inter, Nubank, OFX) e o caminho do arquivo.
        """
        classificador = ClassificadorService()
        
        try:
            logger.info(f"Iniciando importação do extrato: {os.path.basename(caminho_arquivo)}")

            # Leitura, Validação e Normalização via Strategy Pattern (Sem DB)
            dados_extrato = estrategia.processar(caminho_arquivo)
            metadados = dados_extrato["metadados"]
            movimentacoes_brutas = dados_extrato["movimentacoes"]

            # Persistência Atômica via UnitOfWork
            with UnitOfWork() as uow:
                # Busca categoria padrão 'Sem categoria'
                cat_padrao = uow.categorias.buscar_por_nome('Sem categoria')
                if not cat_padrao:
                    raise ValueError("Categoria padrão 'Sem categoria' não existe no banco. Rode o Seed primeiro.")
                
                # Registra a importação (Registro Pai)
                importacao = self.registrar_importacao(
                    uow,
                    os.path.basename(caminho_arquivo),
                    metadados["periodo_inicio"],
                    metadados["periodo_fim"],
                    metadados["total_movimentacoes"]
                )
                
                # Busca movimentações existentes para deduplicação
                existentes = uow.movimentacoes.obter_assinaturas_existentes()
                
                novas_mov = []
                ignoradas = 0
                
                for mov in movimentacoes_brutas:
                    assinatura = (
                        str(mov["data_lancamento"]),
                        mov["descricao"],
                        f"{float(mov['valor']):.2f}",
                        f"{float(mov['saldo']):.2f}" if mov["saldo"] is not None else "None"
                    )
                    if assinatura in existentes:
                        ignoradas += 1
                    else:
                        novas_mov.append(Movimentacao(
                            data_lancamento=mov["data_lancamento"],
                            descricao=mov["descricao"],
                            valor=mov["valor"],
                            saldo=mov["saldo"],
                            tipo=mov["tipo"],
                            importacao_id=importacao.id,
                            categoria_id=cat_padrao.id
                        ))
                # Salva as novas movimentações em lote
                if novas_mov:
                    uow.movimentacoes.salvar_lote(novas_mov)
                    
                # Executa a classificação automática de categorias por palavras-chave
                classificador.classificar_todas_movimentacoes(uow)
                
                # Confirma toda a transação bancária (Tudo ou Nada)
                uow.commit()
            logger.info(f"{len(novas_mov)} novas movimentações importadas do arquivo '{os.path.basename(caminho_arquivo)}'.")

            return {
                "sucesso": True,
                "novas_importadas": len(novas_mov),
                "ignoradas_duplicatas": ignoradas,
                "mensagem": f"{len(novas_mov)} novas movimentações importadas. {ignoradas} já existiam e foram ignoradas."
            }
        except Exception as e:
            logger.error(f"Falha na importação do arquivo '{caminho_arquivo}': {e}", exc_info=True)
            raise e
