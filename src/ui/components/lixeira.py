import customtkinter as ctk


class JanelaLixeira(ctk.CTkToplevel):
    """Mostra movimentações arquivadas e permite selecioná-las para restauração."""

    def __init__(self, master, movimentacoes, ao_restaurar):
        super().__init__(master)
        self.title("Lixeira de movimentações")
        self.geometry("900x560")
        self.minsize(700, 400)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)
        self.ao_restaurar = ao_restaurar
        self.selecionadas = set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self,
            text="Lixeira de movimentações",
            font=("Arial", 18, "bold"),
        ).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        self.lista = ctk.CTkScrollableFrame(self)
        self.lista.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.lista.grid_columnconfigure(2, weight=1)

        self.botao_restaurar = ctk.CTkButton(
            self,
            text="Restaurar selecionadas (0)",
            state="disabled",
            command=self.restaurar_selecionadas,
        )
        self.botao_restaurar.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="e")

        self.atualizar_dados(movimentacoes)

    def ao_fechar(self):
        """Libera a interação da janela principal ao fechar a lixeira."""
        self.grab_release()
        self.destroy()

    def atualizar_dados(self, movimentacoes):
        for widget in self.lista.winfo_children():
            widget.destroy()

        self.selecionadas.clear()
        self.botao_restaurar.configure(text="Restaurar selecionadas (0)", state="disabled")

        if not movimentacoes:
            ctk.CTkLabel(self.lista, text="A lixeira está vazia.").grid(row=0, column=0, padx=20, pady=20)
            return

        for indice, mov in enumerate(movimentacoes):
            data = mov.data_lancamento.strftime("%d/%m/%Y")
            data_arquivamento = mov.excluida_em.strftime("%d/%m/%Y %H:%M") if mov.excluida_em else "—"
            checkbox = ctk.CTkCheckBox(
                self.lista,
                text="",
                width=24,
                command=lambda mov_id=mov.id: self.alternar_selecao(mov_id),
            )
            checkbox.grid(row=indice, column=0, padx=(10, 4), pady=6)
            ctk.CTkLabel(self.lista, text=data, width=90).grid(row=indice, column=1, padx=5, pady=6)
            ctk.CTkLabel(
                self.lista,
                text=mov.descricao,
                anchor="w",
                justify="left",
                wraplength=420,
            ).grid(row=indice, column=2, padx=8, pady=6, sticky="ew")
            ctk.CTkLabel(self.lista, text=f"Arquivada em: {data_arquivamento}").grid(row=indice, column=3, padx=8, pady=6)

    def alternar_selecao(self, movimentacao_id):
        if movimentacao_id in self.selecionadas:
            self.selecionadas.remove(movimentacao_id)
        else:
            self.selecionadas.add(movimentacao_id)

        quantidade = len(self.selecionadas)
        self.botao_restaurar.configure(
            text=f"Restaurar selecionadas ({quantidade})",
            state="normal" if quantidade else "disabled",
        )

    def restaurar_selecionadas(self):
        if not self.selecionadas:
            return
        self.ao_restaurar(sorted(self.selecionadas))
