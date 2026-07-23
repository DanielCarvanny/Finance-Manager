import sys
import os
import traceback

#  Garante que o Python reconheça a pasta 'src' como raiz dos módulos
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src'))
if caminho_src not in sys.path:
    sys.path.insert(0, caminho_src)

from infrastructure.database.conexao import inicializar_banco_de_dados, get_db
from infrastructure.database.seed import verificar_populacao_inicial
from utils.logger import logger


def main():
    try:
        logger.info("🚀 Inicializando o Finance Manager...")
        
        logger.info("Conectando e verificando Banco de Dados...")
        inicializar_banco_de_dados()

        logger.info("✅ Banco de dados e sementes inicializados com sucesso.")

            
        logger.info("Abrindo Interface Gráfica...")
        # Importamos a janela só AGORA, depois que o banco já está pronto!
        from ui.views.app import App
        
        # Instancia a janela e diz para ela ficar aberta (mainloop)
        aplicativo = App()
        aplicativo.mainloop()

        logger.info("👋 Aplicativo encerrado pelo usuário.")
        sys.exit(0)        
    except Exception as e:
        # Tratamento de Exceção Global (Caso algo exploda de forma catastrófica)
        logger.error(f"❌ ERRO CRÍTICO NO SISTEMA: {e}", exc_info=True)

if __name__ == "__main__":
    main()