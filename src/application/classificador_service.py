from domain.models.movimentacao import Movimentacao
from domain.models.palavra_chave import PalavraChave
from domain.models.categoria import Categoria
from infrastructure.database.unit_of_work import UnitOfWork

class ClassificadorService:
    def buscar_palavras_chave(self, uow: UnitOfWork):
        """
        Retornar todas as palavras-chave do banco com sua categoria associada
        """
        return uow.palavras_chave.listar_com_categorias()

    def classificar_movimentacao(self, descricao_mov: str, tipo: str, palavras_chave: list[PalavraChave]):
        """
        Verifica se para cada palavra-chave, o texto está contido na descricao.
        Filtra o tipo de movimentacao compatível (receita/despesa/ambos).
        Retornar o id da categoria correspondente ou None se não encontrar.
        """

        # Verificação se texto está contido em descricao
        for chave in palavras_chave:
            if chave.texto.lower() in descricao_mov.lower():
                if chave.tipo_movimentacao == 'ambos' or chave.tipo_movimentacao == tipo:
                    return chave.categoria.id

        return None

    def classificar_todas_movimentacoes(self, uow: UnitOfWork):
        """
        Classificar as movimentações que estão na categoria "Sem Categoria"
        """
        # Pega o ID da categoria "Sem categoria"
        cat_padrao = uow.categorias.buscar_por_nome('Sem categoria')
        if not cat_padrao:
            return
        
        # Filtra as movimentações usando o ID correto
        movimentacao = uow.movimentacoes.listar_por_categoria(cat_padrao.id)

        # Busca as palavras-chave APENAS UMA VEZ
        palavras_chave_banco = uow.palavras_chave.listar_com_categorias()

        for mov in movimentacao:
            nova_categoria_id = self.classificar_movimentacao(str(mov.descricao), str(mov.tipo), palavras_chave_banco)
            if nova_categoria_id:
                mov.categoria_id = nova_categoria_id
