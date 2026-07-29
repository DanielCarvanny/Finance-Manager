import customtkinter as ctk
from utils.logger import logger
class TabelaMovimentacoes(ctk.CTkScrollableFrame):
    """Tabela de movimentações com alinhamento perfeito de colunas e seleção visual."""

    COR_LINHA_SELECIONADA = "#1F3B5B"

    def __init__(
        self,
        master,
        ao_categoria_alterada=None,
        ao_selecao_alterada=None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.ao_categoria_alterada = ao_categoria_alterada
        self.ao_selecao_alterada = ao_selecao_alterada
        self.movimentacoes_selecionadas = set()
        self.linhas_por_movimentacao = {}
        self.mapa_categoria = {}
        self.criar_cabecalho()

    def criar_cabecalho(self):
        """Cria o cabeçalho com pesos e alinhamento unificados para a tabela."""
        self.grid_columnconfigure(0, weight=0, minsize=40)
        self.grid_columnconfigure(1, weight=1, minsize=100)
        self.grid_columnconfigure(2, weight=4, minsize=320)
        self.grid_columnconfigure(3, weight=2, minsize=160)
        self.grid_columnconfigure(4, weight=1, minsize=120)

        ctk.CTkLabel(self, text="").grid(row=0, column=0, padx=(10, 5), pady=8)
        ctk.CTkLabel(self, text="Data", font=("Arial", 14, "bold"), anchor="w").grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self, text="Descrição", font=("Arial", 14, "bold"), anchor="w").grid(row=0, column=2, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self, text="Categoria", font=("Arial", 14, "bold"), anchor="w").grid(row=0, column=3, padx=5, pady=8, sticky="ew")
        ctk.CTkLabel(self, text="Valor", font=("Arial", 14, "bold"), anchor="e").grid(row=0, column=4, padx=(5, 10), pady=8, sticky="ew")

    def atualizar_dados(self, movimentacoes: list[dict], categorias: list[dict]):
        """Redesenha as linhas do período mantendo o alinhamento unificado."""
        for widget in self.winfo_children():
            info = widget.grid_info()
            if info and info["row"] > 0:
                widget.destroy()

        self.movimentacoes_selecionadas.clear()
        self.linhas_por_movimentacao.clear()
        
        self.mapa_categoria = {cat["nome"]: cat["id"] for cat in categorias}
        lista_nomes_categorias = list(self.mapa_categoria.keys())

        for index, mov in enumerate(movimentacoes, start=1):
            self._criar_linha(index, mov, lista_nomes_categorias)

        self._notificar_selecao()

    def _criar_linha(self, index, movimentacao: dict, lista_nomes_categorias: list[str]):
        """Insere os elementos da linha diretamente no grid da tabela para alinhamento perfeito."""
        valor = movimentacao["valor"]
        cor_valor = "#32CD32" if valor > 0 else "#FF6347"
        valor_formatado = f"R$ {abs(valor):.2f}"
        
        data_obj = movimentacao["data_lancamento"]
        data_formatada = data_obj.strftime("%d/%m/%Y") if hasattr(data_obj, "strftime") else str(data_obj)
        
        id_m = movimentacao["id"]

        checkbox = ctk.CTkCheckBox(
            self,
            text="",
            width=24,
            command=lambda mov_id=id_m: self.alternar_selecao(mov_id),
        )
        checkbox.grid(row=index, column=0, padx=(10, 5), pady=4)

        lbl_data = ctk.CTkLabel(self, text=data_formatada, anchor="w")
        lbl_data.grid(row=index, column=1, padx=5, pady=4, sticky="ew")

        lbl_desc = ctk.CTkLabel(
            self,
            text=movimentacao["descricao"],
            wraplength=380,
            justify="left",
            anchor="w",
        )
        lbl_desc.grid(row=index, column=2, padx=5, pady=4, sticky="ew")

        combo_categoria = ctk.CTkComboBox(
            self,
            values=lista_nomes_categorias,
            command=lambda escolha, mov_id=id_m: self.ao_mudar_categoria(mov_id, escolha),
        )
        combo_categoria.set(movimentacao["categoria_nome"])
        combo_categoria.grid(row=index, column=3, padx=5, pady=4, sticky="ew")

        lbl_valor = ctk.CTkLabel(self, text=valor_formatado, text_color=cor_valor, anchor="e")
        lbl_valor.grid(row=index, column=4, padx=(5, 10), pady=4, sticky="ew")

        self.linhas_por_movimentacao[id_m] = (checkbox, lbl_data, lbl_desc, combo_categoria, lbl_valor)

    def alternar_selecao(self, movimentacao_id: int):
        """Alterna a seleção e destaca os widgets da linha correspondente."""
        widgets_linha = self.linhas_por_movimentacao[movimentacao_id]
        if movimentacao_id in self.movimentacoes_selecionadas:
            self.movimentacoes_selecionadas.remove(movimentacao_id)
            cor_fundo = "transparent"
        else:
            self.movimentacoes_selecionadas.add(movimentacao_id)
            cor_fundo = self.COR_LINHA_SELECIONADA

        for widget in widgets_linha[1:]:
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(fg_color=cor_fundo)

        self._notificar_selecao()

    def _notificar_selecao(self):
        if self.ao_selecao_alterada:
            self.ao_selecao_alterada(len(self.movimentacoes_selecionadas))

    def ao_mudar_categoria(self, mov_id, novo_nome_categoria):
        """Solicita a alteração à App, que é responsável pelo acesso ao banco."""
        nova_categoria_id = self.mapa_categoria[novo_nome_categoria]
        try:
            if self.ao_categoria_alterada:
                self.ao_categoria_alterada(mov_id, nova_categoria_id)
            logger.info(
                "Usuário solicitou categoria '%s' para a movimentação ID %s.",
                novo_nome_categoria,
                mov_id,
            )
        except Exception:
            logger.error("Não foi possível alterar a categoria da movimentação.", exc_info=True)
