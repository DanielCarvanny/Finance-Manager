import customtkinter as ctk

class PainelResumo(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Distribui 4 colunas de largura idêntica (25% cada uma) para centralizar os textos
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Textos iniciais zerados centralizados em cada coluna
        self.lbl_receitas = ctk.CTkLabel(self, text="Receitas: R$ 0.00", text_color="#32CD32", font=("Arial", 16, "bold"))
        self.lbl_receitas.grid(row=0, column=0, padx=15, pady=15)

        self.lbl_despesas = ctk.CTkLabel(self, text="Despesas: R$ 0.00", text_color="#FF6347", font=("Arial", 16, "bold"))
        self.lbl_despesas.grid(row=0, column=1, padx=15, pady=15)

        self.lbl_saldo = ctk.CTkLabel(self, text="Saldo: R$ 0.00", font=("Arial", 16, "bold"))
        self.lbl_saldo.grid(row=0, column=2, padx=15, pady=15)

        self.lbl_gasto_medio = ctk.CTkLabel(self, text="Gasto Médio Diário: R$ 0.00", text_color="#FF6347", font=("Arial", 16, "bold"))
        self.lbl_gasto_medio.grid(row=0, column=3, padx=15, pady=15)

    
    def atualizar_valores(self, receitas, despesas, saldo, gasto_medio):
        """Atualiza os textos e pinta o saldo de verde/vermelho baseado no número"""
        
        self.lbl_receitas.configure(text=f"Receitas: R$ {receitas:.2f}")
        self.lbl_despesas.configure(text=f"Despesas: R$ {despesas:.2f}")

        cor_saldo = "#32CD32" if saldo >= 0 else "#FF6347"
        self.lbl_saldo.configure(text=f"Saldo: R$ {saldo:.2f}", text_color=cor_saldo)

        self.lbl_gasto_medio.configure(text=f"Gasto Médio Diário: R$ {gasto_medio:.2f}")