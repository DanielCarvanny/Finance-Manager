import sys
import os
from datetime import date, datetime

# Garante que o Python ache a pasta src
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, caminho_src)

from database.conexao import inicializar_banco_de_dados, get_db
from models.categoria import Categoria
from models.palavra_chave import PalavraChave
from models.importacao import Importacao
from models.movimentacao import Movimentacao
from models.resumo_mensal import ResumoMensal

if __name__ == "__main__":
    print("1. Iniciando o banco de dados e as seeds...")
    inicializar_banco_de_dados()

    print("\n2. Inserindo dados de exemplo...")
    with get_db() as db:
        # Pega as categorias base criadas pela Seed
        cat_alimentacao = db.query(Categoria).filter_by(nome="Alimentação").first()
        cat_transporte = db.query(Categoria).filter_by(nome="Transporte").first()
        
        # Obs: Se você arrumou o seed.py conforme falamos, a "Receita" vai existir. 
        # Senão, uso uma categoria genérica (fallback) para não quebrar.
        cat_receita = db.query(Categoria).filter_by(nome="Receita").first()
        id_receita = cat_receita.id if cat_receita else 1
        id_alimentacao = cat_alimentacao.id if cat_alimentacao else 1
        
        # 2.1 Criar uma Importação
        importacao = Importacao(
            nome_arquivo="extrato_junho.csv",
            periodo_inicio=datetime(2023, 6, 1),
            periodo_fim=datetime(2023, 6, 30),
            status="sucesso"
        )
        db.add(importacao)
        db.commit() # Commit para gerar a ID que usaremos abaixo
        
        # 2.2 Criar Movimentações
        salario = Movimentacao(
            data_lacamento=date(2023, 6, 5), # Usando 'lacamento' caso você ainda não tenha arrumado o erro de digitação da model
            descricao="SALARIO MENSAL",
            valor=5000.00,
            saldo=5000.00,
            tipo="receita",
            importacao_id=importacao.id,
            categoria_id=id_receita
        )
        
        almoco = Movimentacao(
            data_lacamento=date(2023, 6, 6),
            descricao="RESTAURANTE DA DONA MARIA",
            valor=-35.50,
            saldo=4964.50,
            tipo="despesa",
            importacao_id=importacao.id,
            categoria_id=id_alimentacao
        )
        
        tarifa = Movimentacao(
            data_lacamento=date(2023, 6, 7),
            descricao="TARIFA BANCARIA",
            valor=-15.00,
            saldo=4949.50,
            tipo="despesa",
            importacao_id=importacao.id,
            categoria_id=1 
        )
        db.add_all([salario, almoco, tarifa])
        db.commit()
        
        # 2.3 Criar um Estorno da tarifa (Auto-relacionamento na prática!)
        estorno_tarifa = Movimentacao(
            data_lacamento=date(2023, 6, 8),
            descricao="ESTORNO TARIFA BANCARIA",
            valor=15.00,
            saldo=4964.50,
            tipo="receita",
            importacao_id=importacao.id,
            categoria_id=1,
            estorno_id=tarifa.id # Aponta para a ID da tarifa original!
        )
        db.add(estorno_tarifa)
        
        # 2.4 Criar um Resumo Mensal
        resumo = ResumoMensal(
            ano=2023,
            mes=6,
            total_receitas=5015.00,
            total_despesas=50.50,
            saldo_periodo=4964.50,
            gasto_medio_diario=1.68,
            categoria_maior_gasto_id=id_alimentacao,
            categoria_menor_gasto_id=cat_transporte.id if cat_transporte else 1
        )
        db.add(resumo)
        db.commit()

        print("Dados de exemplo inseridos com sucesso!")

    print("\n3. Lendo os dados para verificar os relacionamentos (A mágica do SQLAlchemy)...")
    with get_db() as db:
        # A) Ler a importação e suas movimentações (Graças ao back_populates!)
        imp = db.query(Importacao).first()
        print(f"\nImportação '{imp.nome_arquivo}' gerou {len(imp.movimentacoes)} movimentações:")
        
        for mov in imp.movimentacoes:
            print(f" - [{mov.tipo.upper()}] {mov.descricao}: R$ {mov.valor}")
            
            # Testa se é um estorno acessando a transação original!
            if mov.estorno_id:
                print(f"    ↳ ATENÇÃO: Isso é um estorno da transação de R$ {mov.movimentacao_original.valor}")
                
        # B) Ler o Resumo e navegar até as cores da categoria
        res = db.query(ResumoMensal).first()
        print(f"\nResumo de {res.mes}/{res.ano}:")
        print(f"Saldo: R$ {res.saldo_periodo}")
        print(f"Categoria que mais gastou: {res.categoria_maior_gasto.nome} (Sua cor é {res.categoria_maior_gasto.cor})")

    print("\nTeste completo finalizado! Tudo funcionando perfeitamente!")
