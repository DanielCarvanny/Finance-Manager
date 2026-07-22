import customtkinter as ctk
import matplotlib.pyplot as plt
import os
import datetime

from utils.logger import logger
from tkinter import filedialog, messagebox
from ui.components.tabela import TabelaMovimentacoes
from ui.components.lixeira import JanelaLixeira
from services.importador import importar_extrato_completo
from services.movimentacao_serivce import (
    ArquivamentoEstornoError,
    arquivar_movimentacoes,
    atualizar_categoria,
    restaurar_movimentacoes,
)
from database.conexao import get_db, salvar_e_criptografar_banco
from models.movimentacao import Movimentacao
from sqlalchemy.orm import joinedload
from models.categoria import Categoria
from ui.components.filtros import FiltrosDashboard
from ui.components.cards import PainelResumo
from ui.components.graficos import GraficoPizza, GraficoBarras, GraficoLinha
from services.resumo_service import obter_resumo
from services.analisador import percentual_por_categoria, evolucao_mensal, receitas_vs_despesas_mensal
from sqlalchemy import extract
from models.categoria import Categoria

# Configurações globais de design
caminho_tema = os.path.join(os.path.dirname(__file__), "theme.json")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(caminho_tema)

class App (ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Finance Manager — InterFIN Local")
        self.after(10, lambda: self.state('zoomed')) # Abre maximizado

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

        # Direita: Filtros de Período (Mês / Ano)
        with get_db() as db:
            self.filtros = FiltrosDashboard(self.topbar, comando_atualizar=self.recalcular_dashboard, session=db)
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
        #hoje = datetime.datetime.now()
        self.recalcular_dashboard(hoje.year, hoje.month)
        
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

    def atualizar_dashboard_apos_reclassificacao(self):
        ano = int(self.filtros.combo_ano.get())
        mes = self.filtros.meses[self.filtros.combo_mes.get()]
        self.recalcular_dashboard(ano, mes)

    def alterar_categoria(self, movimentacao_id, categoria_id):
        """Altera uma categoria pela camada de serviço e atualiza o dashboard."""
        with get_db() as db:
            if not atualizar_categoria(db, movimentacao_id, categoria_id):
                raise ValueError("A movimentação não está disponível para reclassificação.")
        self.atualizar_dashboard_apos_reclassificacao()

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
            with get_db() as db:
                quantidade = arquivar_movimentacoes(db, ids)
                self.filtros.atualizar_anos(db)
        except ArquivamentoEstornoError as erro:
            messagebox.showwarning("Movimentações vinculadas", str(erro))
            return
        except Exception as erro:
            logger.error("Erro ao mover movimentações para a lixeira.", exc_info=True)
            messagebox.showerror("Erro", f"Não foi possível mover as movimentações: {erro}")
            return

        self.label_resultado.configure(
            text=f"🗑 {quantidade} movimentação(ões) movida(s) para a lixeira.",
            text_color="orange",
        )
        self.atualizar_dashboard_apos_reclassificacao()

    def abrir_lixeira(self):
        """Abre uma janela com as movimentações disponíveis para restauração."""
        with get_db() as db:
            movimentacoes = db.query(Movimentacao).options(
                joinedload(Movimentacao.categoria)
            ).filter(
                Movimentacao.excluida.is_(True)
            ).order_by(Movimentacao.excluida_em.desc()).all()

        JanelaLixeira(self, movimentacoes, self.restaurar_da_lixeira)

    def restaurar_da_lixeira(self, ids):
        try:
            with get_db() as db:
                quantidade = restaurar_movimentacoes(db, ids)
                self.filtros.atualizar_anos(db)
        except Exception as erro:
            logger.error("Erro ao restaurar movimentações da lixeira.", exc_info=True)
            messagebox.showerror("Erro", f"Não foi possível restaurar as movimentações: {erro}")
            return

        self.label_resultado.configure(
            text=f"✅ {quantidade} movimentação(ões) restaurada(s).",
            text_color="green",
        )
        self.atualizar_dashboard_apos_reclassificacao()
    
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
        try:
            with get_db() as db:
                resultado = importar_extrato_completo(db, caminho_arquivo)

                # Sucesso! Mostra a mensagem e atualiza a tabela
                self.label_resultado.configure(text=f"✅ {resultado['mensagem']}", text_color="green")
                
                ano_selecionado = int(self.filtros.combo_ano.get())
                mes_selecionado = self.filtros.meses[self.filtros.combo_mes.get()]
                self.filtros.atualizar_anos(db)

                # Manda o Dashboard recalcular tudo para aquele mês
                self.recalcular_dashboard(ano_selecionado, mes_selecionado)

        except Exception as e:
            # Em caso de erro (como um CSV corrompido), mostra na tela
            logger.error(f"Erro ao importar arquivo CSV na UI: {e}", exc_info=True)
            self.label_resultado.configure(text=f"❌ Erro: {str(e)}", text_color="red")
        finally:
            # Independente de sucesso ou erro, para a barra de progresso
            self.barra_progresso.stop()
            self.barra_progresso.pack_forget() # Esconde a barra 

    def recalcular_dashboard(self, ano, mes):
        """Dispara quando o filtro muda ou uma importação acaba"""
        with get_db() as db:
            # Atualiza os Cards
            resumo = obter_resumo(db, ano, mes)

            if resumo:
                self.cards.atualizar_valores(resumo.total_receitas, resumo.total_despesas, resumo.saldo_periodo, resumo.gasto_medio_diario)

                # Gráfico de Linha: evolução das despesas no ano selecionado
                dados_linha = evolucao_mensal(db, ano)
                self.grafico_linha.atualizar_grafico(dados_linha)

                # Gráfico de Barras: receitas vs despesas
                rec_mes, desp_mes = receitas_vs_despesas_mensal(db, ano)
                self.grafico_barras.atualizar_grafico(rec_mes, desp_mes)

                # Atualiza o Gráfico de Pizza
                dados_pizza = percentual_por_categoria(db, ano, mes)
                self.grafico_pizza.atualizar_grafico(dados_pizza)

                # Atualiza a Tabela para mostrar só as daquele mês/ano
                movs_filtradas = db.query(Movimentacao).options(joinedload(Movimentacao.categoria)).filter(
                    Movimentacao.excluida.is_(False),
                    extract('year', Movimentacao.data_lancamento) == ano,
                    extract('month', Movimentacao.data_lancamento) == mes
                ).all()

                todas_categorias = db.query(Categoria).all()
                
                self.tabela.atualizar_dados(movs_filtradas, todas_categorias)

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



if __name__ == "__main__":
    app = App()
    app.mainloop()
