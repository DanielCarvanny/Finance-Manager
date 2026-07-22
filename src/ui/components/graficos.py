import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Cores mais escuras e saturadas para dar alto contraste com o texto branco
cores_interfin = ['#E63946', '#2A9D8F', '#E76F51', '#3A86FF', '#8338EC', '#D4A373']

class GraficoPizza(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Fundo #1E2329 alinhado com o container do sistema
        self.fig, self.ax = plt.subplots(figsize=(5, 4), facecolor='#1E2329')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def atualizar_grafico(self, dicionario_percentual):
        self.ax.clear()
        self.ax.set_facecolor('#1E2329')

        # Título do Gráfico
        self.ax.set_title("Gastos por Categoria", color='#EAECEF', fontsize=12, fontweight='bold', pad=15)

        if not dicionario_percentual:
            self.ax.text(0.5, 0.5, "Sem gastos neste mês", color='#EAECEF', ha='center', va='center')
        else:
            categorias = list(dicionario_percentual.keys())
            valores = list(dicionario_percentual.values())

            # Modelo Donut Chart + Espaçamento entre Rótulos
            self.ax.pie(
                valores, 
                labels=categorias, 
                autopct='%1.1f%%', 
                colors=cores_interfin, 
                textprops={'color': "#EAECEF", 'fontsize': 8, 'fontweight': 'bold'},
                pctdistance=0.70,      # Afasta a porcentagem do centro
                labeldistance=1.18,    # Afasta os nomes das categorias
                wedgeprops=dict(width=0.42, edgecolor='#1E2329', linewidth=5) # Divisão visível (3px) entre fatias
            )

        self.fig.tight_layout()
        self.canvas.draw()


class GraficoBarras(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.fig, self.ax = plt.subplots(figsize=(6, 3), facecolor='#1E2329')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
    
    def atualizar_grafico(self, receitas_por_mes, despesas_por_mes):
        self.ax.clear()
        self.ax.set_facecolor('#1E2329')

        meses = list(receitas_por_mes.keys())
        vals_receita = list(receitas_por_mes.values())
        vals_despesa = list(despesas_por_mes.values())

        x = range(len(meses))
        largura = 0.35

        # Barras de Receita (Verde) e Despesa (Vermelho)
        self.ax.bar([i - largura/2 for i in x], vals_receita, largura, label='Receitas', color='#32CD32')
        self.ax.bar([i + largura/2 for i in x], vals_despesa, largura, label='Despesas', color='#FF6347')
        
        self.ax.set_xticks(list(x))
        self.ax.set_xticklabels(meses, color='#EAECEF', fontsize=8)
        self.ax.tick_params(axis='y', colors='#EAECEF')
        
        # Rótulos dos Eixos X e Y + Título
        self.ax.set_title("Receitas vs Despesas", color='#EAECEF', fontsize=12, fontweight='bold', pad=10)
        self.ax.set_xlabel("Mês do Ano", color='#EAECEF', fontsize=9, labelpad=5)
        self.ax.set_ylabel("Valor (R$)", color='#EAECEF', fontsize=9, labelpad=5)
        
        self.ax.legend(facecolor='#1E2329', labelcolor='#EAECEF', edgecolor='none')
        self.fig.tight_layout()
        self.canvas.draw()


class GraficoLinha(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.fig, self.ax = plt.subplots(figsize=(6, 3), facecolor='#1E2329')
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)

    def atualizar_grafico(self, dados_evolucao):
        self.ax.clear()
        self.ax.set_facecolor('#1E2329')

        # Rótulos dos Eixos X e Y + Título
        self.ax.set_title("Evolução Mensal de Despesas", color='#EAECEF', fontsize=12, fontweight='bold', pad=10)
        self.ax.set_xlabel("Mês do Ano", color='#EAECEF', fontsize=9, labelpad=5)
        self.ax.set_ylabel("Total Despesas (R$)", color='#EAECEF', fontsize=9, labelpad=5)

        if not dados_evolucao or not dados_evolucao.get('mes'):
            self.ax.text(0.5, 0.5, "Sem dados no ano", color='#EAECEF', ha='center', va='center')
        else:
            meses = dados_evolucao['mes']
            valores = dados_evolucao['total_despesas']
            
            self.ax.plot(meses, valores, color='#635BFF', marker='o', linewidth=2, markersize=5)
            self.ax.fill_between(meses, valores, alpha=0.2, color='#635BFF')
            self.ax.tick_params(colors='#EAECEF')

        self.fig.tight_layout()
        self.canvas.draw()