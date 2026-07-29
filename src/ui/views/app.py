import customtkinter as ctk
import matplotlib.pyplot as plt
import os
import datetime
from infrastructure.database.conexao import salvar_e_criptografar_banco
from utils.logger import logger
from tkinter import filedialog, messagebox
from ui.components.tabela import TabelaMovimentacoes
from ui.components.lixeira import JanelaLixeira
from ui.components.filtros import FiltrosDashboard
from ui.components.cards import PainelResumo
from ui.components.graficos import GraficoPizza, GraficoBarras, GraficoLinha
from ui.viewmodels.dashboard_view_model import DashboardViewModel
from ui.viewmodels.lixeira_view_model import LixeiraViewModel
from ui.viewmodels.importacao_view_model import ImportacaoViewModel
from domain.exceptions import ArquivamentoEstornoError


# Configurações globais de design
caminho_tema = os.path.join(os.path.dirname(__file__), "theme.json")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(caminho_tema)

class App (ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Manager — InterFIN Local")
        self.after(10, lambda: self.state('zoomed')) # Abre maximizado
        
        # Instancia os ViewModels
        self.dashboard_viewmodel = DashboardViewModel()
        self.lixeira_viewmodel = LixeiraViewModel()
        self.importacao_viewmodel = ImportacaoViewModel()

        # ─────────────────────────────────────────────────
        # ESQUELETO PRINCIPAL: 1 coluna x 2 linhas
        # ─────────────────────────────────────────────────
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Topbar: Altura fixa
        self.grid_rowconfigure(1, weight=1) # Conteúdo: Expande e rola


        # ── 1. TOPBAR / CABEÇALHO SUPERIOR (Linha 0) ─────
        self.topbar = ctk.CTkFrame(self, fg_color="#0A2540", height=60, corner_radius=0)
        self.topbar.grid(row=0, column=0, sticky="ew")
        # Esquerda: Logo do App
        self.lbl_logo = ctk.CTkLabel(
            self.topbar, 
            text="📊 InterFIN Local", 
            font=("Arial", 18, "bold"), 
            text_color="#635BFF"
        )
        self.lbl_logo.pack(side="left", padx=20, pady=15)
        # Centro-Esquerda: Botão de Importação + Status
        self.btn_importar = ctk.CTkButton(
            self.topbar, 
            text="📥 Importar Extrato (CSV)", 
            command=self.acao_importar,
            font=("Arial", 13, "bold")
        )
        self.btn_importar.pack(side="left", padx=15, pady=12)
        self.barra_progresso = ctk.CTkProgressBar(self.topbar, mode="indeterminate", width=120)
        self.label_resultado = ctk.CTkLabel(self.topbar, text="", font=("Arial", 12))
        self.label_resultado.pack(side="left", padx=10)
        self.btn_lixeira = ctk.CTkButton(
            self.topbar,
            text="🗑 Lixeira",
            command=self.abrir_lixeira,
            fg_color="#4B5563",
            hover_color="#374151",
        )
        self.btn_lixeira.pack(side="left", padx=6)
        self.btn_arquivar = ctk.CTkButton(
            self.topbar,
            text="Mover para lixeira (0)",
            command=self.confirmar_arquivamento,
            fg_color="#C0392B",
            hover_color="#922B21",
        )

        # Carrega o período inicial
        anos_disponiveis = self.dashboard_viewmodel.listar_anos()
        self.filtros = FiltrosDashboard(self.topbar, comando_atualizar=self.carregar_e_renderizar_periodo, anos_disponiveis=anos_disponiveis)
        
        self.filtros.pack(side="right", padx=20, pady=10)

        # ── ÁREA DE CONTEÚDO (Coluna 1) ─────────────────
        self.area_conteudo = ctk.CTkScrollableFrame(self, fg_color="#0B0E11", corner_radius=0)
        self.area_conteudo.grid(row=1, column=0, sticky="nsew")

        #  Configura as 2 colunas internas da área de conteúdo
        self.area_conteudo.grid_columnconfigure(0, weight=1)
        self.area_conteudo.grid_columnconfigure(1, weight=1)

        # ── SEÇÃO A: Cards de Resumo (Largura Total) ─────
        self.cards = PainelResumo(self.area_conteudo)
        self.cards.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")

        # ── SEÇÃO B: Tabela de Movimentações (Largura Total)
        self.tabela = TabelaMovimentacoes(
            self.area_conteudo, 
            height=350,
            ao_categoria_alterada=self.alterar_categoria,
            ao_selecao_alterada=self.atualizar_botao_arquivamento,
        )
        self.tabela.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 25), sticky="ew")

        # ── SEÇÃO C: Gráficos Lado a Lado ────────────────
        self.grafico_barras = GraficoBarras(self.area_conteudo)
        self.grafico_barras.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="nsew")
        self.grafico_pizza = GraficoPizza(self.area_conteudo)
        self.grafico_pizza.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="nsew")

        # ── SEÇÃO D: Gráfico de Linha (Largura Total) ────
        self.grafico_linha = GraficoLinha(self.area_conteudo)
        self.grafico_linha.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        # ── INICIALIZAÇÃO ──
        # Configurar scroll rápido
        self.configurar_scroll_rapido(velocidade=40)

        hoje = datetime.date.today()
        self.carregar_e_renderizar_periodo(hoje.year, hoje.month)
        
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def alterar_categoria(self, movimentacao_id, nova_categoria_id, ano, mes):
        """Callback disparado quando o usuário altera a categoria na tabela."""
        dados = self.dashboard_viewmodel.alterar_categoria_movimentacao(movimentacao_id, nova_categoria_id, ano, mes)
        self.cards.atualizar_valores(
            dados["cards"]["total_receitas"],
            dados["cards"]["total_despesas"],
            dados["cards"]["saldo_periodo"],
            dados["cards"]["gasto_medio_diario"]
        )
        
        self.grafico_pizza.atualizar_grafico(dados["graficos"]["pizza"])
        self.grafico_linha.atualizar_grafico(dados["graficos"]["linha"])
        self.grafico_barras.atualizar_grafico(
            dados["graficos"]["barras_receitas"],
            dados["graficos"]["barras_despesas"],
        )
        self.tabela.atualizar_dados(
            dados["tabela"]["movimentacoes"],
            dados["tabela"]["categorias"]
        )

    def atualizar_botao_arquivamento(self, quantidade):
        """Exibe a ação destrutiva somente quando há linhas selecionadas."""
        if quantidade:
            self.btn_arquivar.configure(text=f"Mover para lixeira ({quantidade})")
            if not self.btn_arquivar.winfo_manager():
                self.btn_arquivar.pack(side="left", padx=6)
        else:
            self.btn_arquivar.pack_forget()

    def confirmar_arquivamento(self):
        ids = sorted(self.tabela.movimentacoes_selecionadas)
        if not ids:
            return

        confirmou = messagebox.askyesno(
            "Mover para lixeira",
            f"Deseja mover {len(ids)} movimentação(ões) para a lixeira?\n\n"
            "Elas deixarão de aparecer nos indicadores e poderão ser restauradas depois.",
            icon="warning",
        )
        if not confirmou:
            return
        
        try:
            qtd = self.lixeira_viewmodel.arquivar_movimentacoes(ids)
            if qtd == 0:
                messagebox.showwarning("Erro", "Não foi possível mover para a lixeira. Verifique se não há estornos vinculados.")
                return
        except ArquivamentoEstornoError as e:
            messagebox.showwarning("Movimentações vinculadas", str(e))
            return
            
        self.label_resultado.configure(
            text=f"🗑 {qtd} movimentação(ões) movida(s) para a lixeira.",
            text_color="orange",
        )
        ano= int(self.filtros.combo_ano.get())
        mes= self.filtros.meses[self.filtros.combo_mes.get()]
        self.carregar_e_renderizar_periodo(ano, mes)

    def abrir_lixeira(self):
        """Abre a lixeira em primeiro plano sobre a janela principal."""
        movimentacoes = self.lixeira_viewmodel.listar_movimentacoes_lixeira()

        if hasattr(self, "janela_lixeira") and self.janela_lixeira.winfo_exists():
            self.janela_lixeira.focus_force()
            return

        self.janela_lixeira = JanelaLixeira(self, movimentacoes, self.restaurar_da_lixeira)
        self.janela_lixeira.grab_set()
        self.janela_lixeira.focus_force()
        
    def restaurar_da_lixeira(self, ids):
        try:
            quantidade = self.lixeira_viewmodel.restaurar_da_lixeira(ids)
            
            if quantidade == 0:
                messagebox.showerror("Erro", f"Não foi possível restaurar as movimentações. ")
                return
        except Exception as e:
            logger.error("Erro ao restaurar movimentações da lixeira.", exc_info=True)
            messagebox.showerror("Erro", f"Não foi possível restaurar as movimentações: {e}")
            return

        self.label_resultado.configure(
            text=f"✅ {quantidade} movimentação(ões) restaurada(s).",
            text_color="green",
        )
        ano= int(self.filtros.combo_ano.get())
        mes= self.filtros.meses[self.filtros.combo_mes.get()]
        self.carregar_e_renderizar_periodo(ano, mes)
        
    
    def acao_importar(self):
        """
        Ação que acontece quando o usuário clica no Botão
        """
        # Pede para o usuário escolher o arquivo
        caminho_arquivo = filedialog.askopenfilename(
            title= "Selecione o Extrato do Banco Inte",
            filetypes=(("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*"))
        )

        # Se o usuário clicar em "Cancelar", não fazemos nada
        if not caminho_arquivo:
            return
        
        logger.info(f"Usuário selecionou o arquivo para importação: {os.path.basename(caminho_arquivo)}")

        #  Mostra a barra de progresso girando
        self.barra_progresso.pack(pady=10)
        self.barra_progresso.start()
        self.label_resultado.configure(text="Importando... Aguarde.", text_color="yellow")
        self.update() # Força a tela a se desenhar antes da importação "congelar"

        # Manda para a nossa regra de negócios 
        resultado = self.importacao_viewmodel.executar_importacao(caminho_arquivo)
        if resultado["sucesso"]:
            # Sucesso! Mostra a mensagem e atualiza a tabela
            self.label_resultado.configure(text=f"✅ {resultado['mensagem']}", text_color="green")
            
            novos_anos = self.dashboard_viewmodel.listar_anos()
            self.filtros.atualizar_anos(novos_anos)

            # Manda o Dashboard recalcular tudo para aquele mês
            ano= int(self.filtros.combo_ano.get())
            mes= self.filtros.meses[self.filtros.combo_mes.get()]
            self.carregar_e_renderizar_periodo(ano, mes)
        else:
            # Em caso de erro (como um CSV corrompido), mostra na tela
            logger.error(f"Erro ao importar arquivo CSV na UI. {resultado['mensagem']}", exc_info=True)
            self.label_resultado.configure(text=f"❌ {resultado['mensagem']}", text_color="red")
        
        # Independente de sucesso ou erro, para a barra de progresso
        self.barra_progresso.stop()
        self.barra_progresso.pack_forget() # Esconde a barra 

    def ao_fechar(self):
        """Executada quando o usuário clica no 'X' da janela"""
        logger.info("Aplicativo encerrado pelo usuário via botão fechar.")
        plt.close('all') # 1. Destroi todas as figuras do Matplotlib da memória RAM

        # Salva e criptografa o arquivo de banco de dados
        salvar_e_criptografar_banco()

        self.quit()      # 2. Interrompe o loop do Tkinter (mainloop)
        self.destroy()   # 3. Destroi a janela fisicamente

    def configurar_scroll_rapido(self, velocidade=3):
        """Configura a velocidade do scroll no frame de conteúdo"""
        
        def on_mousewheel(event):
            try:
                self.area_conteudo._parent_canvas.yview_scroll(
                    int(-1 * (event.delta / 120) * velocidade), 
                    "units"
                )
            except:
                pass
        
        # Vincular ao canvas e frame
        self.area_conteudo._parent_canvas.bind("<MouseWheel>", on_mousewheel, add="+")
        self.area_conteudo.bind("<MouseWheel>", on_mousewheel, add="+")
        
        # Foco automático
        self.area_conteudo.bind("<Enter>", 
            lambda e: self.area_conteudo._parent_canvas.focus_set())
        
        # Vincular a todos os widgets depois que tudo carregar
        def vincular_tudo():
            for widget in self.area_conteudo.winfo_children():
                try:
                    widget.bind("<MouseWheel>", on_mousewheel, add="+")
                    for filho in widget.winfo_children():
                        filho.bind("<MouseWheel>", on_mousewheel, add="+")
                except:
                    pass
        
        self.after(1500, vincular_tudo)
        # Configurar também os gráficos
        self.after(2000, lambda: self.configurar_scroll_graficos(velocidade))


    def configurar_scroll_graficos(self, velocidade=3):
        """Desabilita o scroll do Matplotlib e redireciona para o frame"""
        
        def on_mousewheel_grafico(event):
            """Redireciona o scroll do gráfico para o frame"""
            self.area_conteudo._parent_canvas.yview_scroll(
                int(-1 * (event.delta / 120) * velocidade), 
                "units"
            )
        
        graficos = [self.grafico_barras, self.grafico_pizza, self.grafico_linha]
        
        for grafico in graficos:
            try:
                # Desconectar eventos de scroll do Matplotlib
                for conn in grafico.fig.canvas.callbacks.callbacks.get('scroll_event', {}).copy():
                    grafico.fig.canvas.mpl_disconnect(conn)
                
                # Vincular nosso scroll
                widget_tk = grafico.fig.canvas.get_tk_widget()
                widget_tk.bind("<MouseWheel>", on_mousewheel_grafico)
            except:
                pass
            
    def carregar_e_renderizar_periodo(self, ano, mes):
        """Pega os dados limpos do ViewModel e aplica nos componentes visuais."""
        
        dados = self.dashboard_viewmodel.carregar_periodo(ano, mes)
        self.cards.atualizar_valores(
            dados["cards"]["total_receitas"],
            dados["cards"]["total_despesas"],
            dados["cards"]["saldo_periodo"],
            dados["cards"]["gasto_medio_diario"]
        )
        
        self.grafico_pizza.atualizar_grafico(dados["graficos"]["pizza"])
        self.grafico_linha.atualizar_grafico(dados["graficos"]["linha"])
        self.grafico_barras.atualizar_grafico(
            dados["graficos"]["barras_receitas"],
            dados["graficos"]["barras_despesas"],
        )
        self.tabela.atualizar_dados(
            dados["tabela"]["movimentacoes"],
            dados["tabela"]["categorias"]
        )
        

if __name__ == "__main__":
    app = App()
    app.mainloop()
