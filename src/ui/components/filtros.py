import customtkinter as ctk
from datetime import date

class FiltrosDashboard(ctk.CTkFrame):
    def ao_alterar(self, escolha_ignorada):
        """Dispara quando o usuário muda qualquer dropdown"""
        mes_nome= self.combo_mes.get()
        ano_texto = self.combo_ano.get()
        
        # Traduz de "Agosto" para 8 e dispara o gatilho lá pro App principal!
        mes_numero = self.meses[mes_nome]
        self.comando_atualizar(int(ano_texto), mes_numero)

    def __init__(self, master, comando_atualizar, anos_disponiveis: list[str], **kwargs):
        super().__init__(master, **kwargs)
        self.comando_atualizar = comando_atualizar # Guarda o gatilho

        # Dicionário de meses para facilitar a vida do usuário
        self.meses = {
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, 
            "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }

        # Busca os anos dinamicamente do banco de dados
        ctk.CTkLabel(self, text="Mês:").pack(side="left", padx=5)
        self.combo_mes = ctk.CTkComboBox(self, values=list(self.meses.keys()), command=self.ao_alterar)
        self.combo_mes.pack(side="left", padx=5)
        
        ctk.CTkLabel(self, text="Ano:").pack(side="left", padx=5)
        self.combo_ano = ctk.CTkComboBox(self, values=anos_disponiveis, command=self.ao_alterar)
        self.combo_ano.pack(side="left", padx=5)

    def atualizar_anos(self, novos_anos: list[str]):
        """Atualiza a lista de anos após importar, arquivar ou restaurar dados."""
        ano_atual = self.combo_ano.get()
        self.combo_ano.configure(values=novos_anos)
        if ano_atual not in novos_anos:
            self.combo_ano.set(novos_anos[0])
