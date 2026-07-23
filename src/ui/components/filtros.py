import customtkinter as ctk
from domain.models.movimentacao import Movimentacao
from sqlalchemy import extract, distinct
from datetime import date


class FiltrosDashboard(ctk.CTkFrame):
    def ao_alterar(self, escolha_ignorada):
        """Dispara quando o usuário muda qualquer dropdown"""
        mes_nome= self.combo_mes.get()
        ano_texto = self.combo_ano.get()
        
        # Traduz de "Agosto" para 8 e dispara o gatilho lá pro App principal!
        mes_numero = self.meses[mes_nome]
        self.comando_atualizar(int(ano_texto), mes_numero)

    def __init__(self, master, comando_atualizar, session, **kwargs):
        super().__init__(master, **kwargs)
        self.comando_atualizar = comando_atualizar # Guarda o gatilho

        # Dicionário de meses para facilitar a vida do usuário
        self.meses = {
            "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4, "Maio": 5, "Junho": 6, 
            "Julho": 7, "Agosto": 8, "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
        }

        # Busca os anos dinamicamente do banco de dados
        anos_disponiveis = self._buscar_anos(session)


        ctk.CTkLabel(self, text="Mês:").pack(side="left", padx=5)
        self.combo_mes = ctk.CTkComboBox(self, values=list(self.meses.keys()), command=self.ao_alterar)
        self.combo_mes.pack(side="left", padx=5)
        
        ctk.CTkLabel(self, text="Ano:").pack(side="left", padx=5)
        self.combo_ano = ctk.CTkComboBox(self, values=anos_disponiveis, command=self.ao_alterar)
        self.combo_ano.pack(side="left", padx=5)

    def _buscar_anos(self, session):
        """Busca os anos distintos que existem no banco de dados"""
        resultados = session.query(
            distinct(extract('year', Movimentacao.data_lancamento))
        ).filter(
            Movimentacao.excluida.is_(False)
        ).order_by(
            extract('year', Movimentacao.data_lancamento).desc()
        ).all()

        # Converte de [(2026.0,), (2025.0,)] para ["2026", "2025"]
        anos = [str(int(r[0])) for r in resultados if r[0] is not None]

        # Se o banco estiver vazio, mostra o ano atual como fallback
        if not anos:
            anos = [str(date.today().year)]
            
        return anos

    def atualizar_anos(self, session):
        """Atualiza a lista de anos após importar, arquivar ou restaurar dados."""
        anos = self._buscar_anos(session)
        ano_atual = self.combo_ano.get()
        self.combo_ano.configure(values=anos)
        if ano_atual not in anos:
            self.combo_ano.set(anos[0])
