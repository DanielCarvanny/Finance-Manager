import sys
import os
from datetime import date

# Garante que o Python ache a pasta src
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, caminho_src)

from infrastructure.database.conexao import inicializar_banco_de_dados, get_db
from application.importacao.importacao_service import importar_extrato_completo
from domain.models.importacao import Importacao
from domain.models.movimentacao import Movimentacao

def testar_integracao_banco():
    print("1. Preparando o Banco de Dados (Tabelas e Seeds)...")
    inicializar_banco_de_dados()

    #caminho_csv = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Exemplo_CSV', 'Extrato-Exemplo-CSV.csv')
    caminho_csv = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Exemplo_CSV', 'Extrato-Realista.csv')

    
    # Valida se o arquivo de exemplo existe
    if not os.path.exists(caminho_csv):
        print(f"❌ Arquivo de teste não encontrado: {caminho_csv}")
        return

    print("\n2. Simulando a Importação via Orquestrador...")
    
    with get_db() as db:
        # A) Importação Inicial (Caminho Feliz)
        try:
            resultado1 = importar_extrato_completo(db, caminho_csv)
            print(f"✅ Primeira Importação: {resultado1['mensagem']}")
        except Exception as e:
            print(f"❌ Falha na primeira importação: {e}")
            return

        # B) Teste de Duplicatas (O mesmo extrato importado de novo)
        print("\n3. Simulando a Importação DUPLICADA (Mesmo arquivo, mesmo mês)...")
        try:
            resultado2 = importar_extrato_completo(db, caminho_csv)
            print(f"✅ Segunda Importação (Filtro de Duplicatas): {resultado2['mensagem']}")
            
            # Validação forte
            if resultado2['novas_importadas'] == 0 and resultado2['ignoradas_duplicatas'] > 0:
                print("   ↳ SUCESSO! O sistema identificou e ignorou os dados que já existiam.")
            else:
                print("   ❌ FALHA: O sistema inseriu dados duplicados ou contou errado!")
        except Exception as e:
            print(f"❌ Falha na segunda importação: {e}")

        # C) Prova Real: Consultando as tabelas fisicamente
        print("\n4. Consultando o Banco de Dados...")
        todas_importacoes = db.query(Importacao).all()
        todas_movimentacoes = db.query(Movimentacao).all()
        
        print(f"Total de Registros Pais (Importações): {len(todas_importacoes)}")
        print(f"Total de Registros Filhos (Movimentações): {len(todas_movimentacoes)}")

        # Pega a última movimentação só para mostrar na tela
        if todas_movimentacoes:
            ultima = todas_movimentacoes[-1]
            print(f"\nExemplo gravado no banco -> [{ultima.tipo.upper()}] {ultima.descricao}: R$ {ultima.valor} (Data: {ultima.data_lancamento})")

        print("\n🏁 TESTE DE INTEGRAÇÃO COM BANCO FINALIZADO! 🏁")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTES DO IMPORTADOR (SQLALCHEMY) 🚀")
    testar_integracao_banco()
