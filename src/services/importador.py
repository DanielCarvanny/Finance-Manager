from models.importacao import Importacao
from models.movimentacao import Movimentacao
from models.categoria import Categoria
import pandas as pd
import os
import re
from datetime import datetime, date
from typing import List, Dict
from sqlalchemy.orm import Session
from services.classificador import classificar_todas_movimentacoes
from utils.logger import logger


class ImportacaoPendenteError(Exception):
    """
    Exceção lançada quando a importação possui dados corrompidos.
    Carrega o DataFrame incompleto para que a UI possa solicitar a correção manual.
    """
    def __init__(self, mensagem, df_incompleto, colunas_com_erro, linhas_com_erro):
        self.mensagem = mensagem
        self.df_incompleto = df_incompleto
        self.colunas_com_erro = colunas_com_erro
        self.linhas_com_erro = linhas_com_erro
        super().__init__(self.mensagem)


def validar_arquivo(caminho_arquivo: str) -> None:
    """
    Valida a existência, extensão e tamanho do arquivo antes de qualquer leitura.
    Lança excepcoes com mensagens amigáveis ao invés de erros técnicos do Python/Pandas.
    """
    if not os.path.exists(caminho_arquivo):
        raise FileNotFoundError(f"Arquivo não encontrado: '{os.path.basename(caminho_arquivo)}'. Verifique se o arquivo ainda existe no local selecionado.")

    if not caminho_arquivo.lower().endswith('.csv'):
        extensao = os.path.splitext(caminho_arquivo)[1] or 'desconhecida'
        raise ValueError(f"Formato inválido: o arquivo selecionado é '{extensao}'. Por favor, selecione um arquivo no formato '.csv'.")

    if os.path.getsize(caminho_arquivo) == 0:
        raise ValueError(f"O arquivo '{os.path.basename(caminho_arquivo)}' está vazio (0 bytes). Selecione um extrato válido.")


def _ler_linhas_iniciais(caminho_arquivo, quantidade: int = 10) -> list[str]:
    """Lê as primeiras linhas preservando suporte a caminhos e arquivos em memória."""
    if hasattr(caminho_arquivo, 'read'):
        posicao = caminho_arquivo.tell() if hasattr(caminho_arquivo, 'tell') else None
        if hasattr(caminho_arquivo, 'seek'):
            caminho_arquivo.seek(0)
        linhas = [caminho_arquivo.readline() for _ in range(quantidade)]
        if posicao is not None and hasattr(caminho_arquivo, 'seek'):
            caminho_arquivo.seek(posicao)
        return linhas

    for encoding in ('utf-8', 'latin1'):
        try:
            with open(caminho_arquivo, encoding=encoding) as arquivo:
                return [arquivo.readline() for _ in range(quantidade)]
        except UnicodeDecodeError:
            continue

    raise ValueError("Não foi possível ler o arquivo do extrato.")


def extrair_periodo(caminho_arquivo: str):
    """
    Lê o cabeçalho do arquivo para encontrar as datas de início e fim do período.
    Retorna uma tupla (periodo_inicio, periodo_fim) como objetos datetime.date.
    """
    try:
        linhas = _ler_linhas_iniciais(caminho_arquivo, 15)
        # Primeiro busca linha identificada como período
        for linha in linhas:
            if 'período' in linha.lower() or 'periodo' in linha.lower():
                datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', linha)
                if len(datas) >= 2:
                    periodo_inicio = datetime.strptime(datas[0], '%d/%m/%Y').date()
                    periodo_fim = datetime.strptime(datas[1], '%d/%m/%Y').date()
                    return periodo_inicio, periodo_fim

        # Fallback: busca qualquer linha inicial com duas datas DD/MM/AAAA
        for linha in linhas:
            datas = re.findall(r'\b\d{2}/\d{2}/\d{4}\b', linha)
            if len(datas) >= 2:
                periodo_inicio = datetime.strptime(datas[0], '%d/%m/%Y').date()
                periodo_fim = datetime.strptime(datas[1], '%d/%m/%Y').date()
                return periodo_inicio, periodo_fim

        raise ValueError
    except Exception:
        raise ValueError("O arquivo não possui o cabeçalho padrão esperado. Não foi possível encontrar o Período.")


def localizar_cabecalho_e_delimitador(caminho_arquivo: str) -> tuple[int, str]:
    """Localiza o cabeçalho de movimentações e seu delimitador (`,` ou `;`)."""
    linhas = _ler_linhas_iniciais(caminho_arquivo, 20)
    for indice, linha in enumerate(linhas):
        linha_lower = linha.lower()
        if 'data' in linha_lower and ('descrição' in linha_lower or 'descricao' in linha_lower):
            delimitador = ';' if linha.count(';') >= linha.count(',') else ','
            return indice, delimitador

    raise ValueError("O arquivo não possui o cabeçalho de movimentações esperado.")
def validar_estrutura(df: pd.DataFrame) -> tuple[bool, str | None]:
    """
    Verifica se a estrutura do DataFrame (lido do CSV) é válida.
    Retorna (True, None) se estiver correto, ou (False, "mensagem de erro").
    """
    # Verifica se o arquivo não está vazio
    if df.empty:
        return False, "O arquivo do extrato não contém dados de movimentação ou está vazio."
    
    # Verifica as colunas obrigatórias
    colunas_obrigatorias = ['Data Lançamento', 'Descrição', 'Valor', 'Saldo']

    for col in colunas_obrigatorias:
        if col not in df.columns:
            return False, f"Coluna obrigatória não encontrada: '{col}'. Verifique o cabeçalho do CSV."
    
    # Verifica compatibilidade de tipos (Data e Numérico) fazendo um teste na primeira linha
    try:
        primeira_linha = df.iloc[0]
        # Tenta converter a data
        pd.to_datetime(primeira_linha['Data Lançamento'], format= '%d/%m/%Y', dayfirst=True)

        # Tenta converter o valor
        valor_str = str(primeira_linha['Valor']).replace('.', '').replace(',', '.')
        float(valor_str)
    except Exception:
        return False, "Tipos de dados incompatíveis. A data deve ser DD/MM/AAAA e o valor deve ser numérico."
    
    # Se passou por tudo, está validado
    return True, None

def normalizar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpa e formata as colunas para o padrão Python.
    Bloqueia a importação se encontrar dados corrompidos.
    Retorna o DataFrame normalizado.
    """

    # Renomeia as colunas
    df.columns= ['data_lancamento', 'descricao', 'valor', 'saldo']

    # Limpeza dos números
    texto_limpo_valor = df['valor'].astype(str).str.replace('.', '').str.replace(',', '.') 
    df['valor'] = pd.to_numeric(texto_limpo_valor, errors= 'coerce')

    texto_limpo_saldo = df['saldo'].astype(str).str.replace('.', '').str.replace(',', '.')
    df['saldo'] = pd.to_numeric(texto_limpo_saldo, errors='coerce')
    
    # Validação do Valor
    if df['valor'].isna().any():
        linhas_invalidas = df[df['valor'].isna()].index.tolist()

        raise ImportacaoPendenteError(
            "Existem transações com o campo 'Valor' em branco ou inválido. Insira o valor correto.",
            df_incompleto=df,
            colunas_com_erro=['valor'],
            linhas_com_erro=linhas_invalidas
        )

    # Limpeza das datas
    df['data_lancamento'] = pd.to_datetime(
        df['data_lancamento'], 
        format='mixed', 
        dayfirst=True,
        errors= 'coerce'
        ).dt.date
    
    if df['data_lancamento'].isna().any():
        linhas_invalidas = df[df['data_lancamento'].isna()].index.tolist()
        raise ImportacaoPendenteError(
            "Existem transações com a Data corrompida ou em branco.",
            df_incompleto=df,
            colunas_com_erro=['data_lancamento'],
            linhas_com_erro=linhas_invalidas
        )

    return df

def extrair_dados(df: pd.DataFrame) -> list[dict]:
    """
    Extrai os dados do DataFrame e retorna uma lista de dicionários.
    Cada dicionário representa uma movimentação.
    """
    movimentacoes_validadas = []

    for index, row in df.iterrows():
        valor = float(row['valor'])

        if valor == 0:
            continue  # Ignora movimentações com valor zero

        movimentacoes_validadas.append({
            'data_lancamento': row['data_lancamento'],
            'descricao': str(row['descricao']).strip(),
            'valor': valor,
            'saldo': float(row['saldo']) if not pd.isna(row['saldo']) else None,
            'tipo': 'despesa' if valor < 0 else 'receita'
        })
        
    return movimentacoes_validadas
       

def processar_csv_extrato(caminho_arquivo: str) -> dict:
    """
    Função principal que orquestra a leitura, validação, normalização e extração dos dados do extrato.
    Retorna uma lista de dicionários prontos para o banco de dados.
    """

    # Valida existência, extensão e tamanho ANTES de qualquer leitura
    validar_arquivo(caminho_arquivo)

    # Extrai o período do extrato
    periodo_inicio, periodo_fim = extrair_periodo(caminho_arquivo)

    # Localiza o cabeçalho em vez de pressupor um delimitador ou número fixo de linhas.
    indice_cabecalho, delimitador = localizar_cabecalho_e_delimitador(caminho_arquivo)

    # Lê o arquivo CSV a partir do cabeçalho de movimentações.
    try:
        df = pd.read_csv(
            caminho_arquivo,
            skiprows=indice_cabecalho,
            sep=delimitador,
            encoding='utf-8'
        )
    except UnicodeDecodeError:
        logger.warning(f"Encoding UTF-8 falhou para '{os.path.basename(caminho_arquivo)}'. Usando fallback latin1.")
        df = pd.read_csv(
            caminho_arquivo,
            skiprows=indice_cabecalho,
            sep=delimitador,
            encoding='latin1'
        )
    
    # Valida a estrutura do DataFrame
    is_valido, erro_msg = validar_estrutura(df)

    if not is_valido:
        raise ValueError(f"Falha na validação do CSV: {erro_msg}")
    
    # Normaliza os dados
    df = normalizar_dados(df)

    # Validação da movimentação
    movimentacoes_validadas = extrair_dados(df)

    # EMPACOTANDO O RETORNO
    # Retornamos um dicionário contendo TUDO que a model 'Importacao' e 'Movimentacao' precisam
    return {
        "metadados": {
            "periodo_inicio": periodo_inicio,
            "periodo_fim": periodo_fim,
            "total_movimentacoes": len(movimentacoes_validadas) # Atendendo a sua regra de negócio!
        },
        "movimentacoes": movimentacoes_validadas
    }

def registrar_importacao(session: Session, nome: str, periodo_inicio: date, periodo_fim: date, total_movimentacoes: int) -> Importacao:
    """
    Registra a importação no banco de dados.
    """
    nova_importacao = Importacao(
        nome_arquivo= nome,
        periodo_inicio= periodo_inicio,
        periodo_fim= periodo_fim,
        status= 'sucesso',
        data_importacao= datetime.now(),
        total_movimentacoes= total_movimentacoes
    )

    session.add(nova_importacao)

    session.flush()  # Garante que o ID seja gerado antes do commit

    return nova_importacao

def salvar_movimentacoes(session: Session, dados: list[dict], importacao_id: int, categoria_padrao_id: int) -> tuple[int, int]:
    """
    Verifica duplicatas e salva as novas movimentações em lote.
    Retorna a quantidade de (novas_inseridas, duplicadas_ignoradas)
    """
    novas = 0
    ignoradas = 0
    movimentacoes_para_salvar = []

    # Busca assinaturas existentes no banco (apenas para comparar)
    existentes = session.query(
        Movimentacao.data_lancamento,
        Movimentacao.descricao,
        Movimentacao.valor,
        Movimentacao.saldo,
    ).all()

    # Converte o valor do banco (que pode vir como Decimal) para Float,
    assinaturas_existentes = {
        (
            str(data), 
            desc, 
            f"{float(valor):.2f}", 
            f"{float(saldo):.2f}" if saldo is not None else "None"
        )
        for data, desc, valor, saldo in existentes
    }

    for mov in dados:
        # Cria a assinatura da linha atual
        assinatura_atual = (
            str(mov['data_lancamento']), 
            mov['descricao'], 
            f"{float(mov['valor']):.2f}", 
            f"{float(mov['saldo']):.2f}" if mov['saldo'] is not None else "None"
        )

        # Ignora as que já existem no banco
        if assinatura_atual in assinaturas_existentes:
            ignoradas += 1
        else:
            nova_mov = Movimentacao(
                data_lancamento= mov['data_lancamento'],
                descricao= mov['descricao'],
                valor= mov['valor'],
                saldo= mov['saldo'],
                tipo= mov['tipo'],
                importacao_id= importacao_id,
                categoria_id= categoria_padrao_id
            )
            movimentacoes_para_salvar.append(nova_mov)
            novas += 1
    
    # Insere as novas em lote (muito mais rápido do que uma por uma)
    if movimentacoes_para_salvar:
        session.add_all(movimentacoes_para_salvar)
        session.flush() # Manda pro banco, mas ainda não assina (commit)
    
    return novas, ignoradas

def importar_extrato_completo(session: Session, caminho_arquivo: str) -> dict:
    """
    Esta é a única função que a sua Interface (Telas) vai precisar chamar.
    """
    try:
        logger.info(f"Iniciando importação do extrato: {os.path.basename(caminho_arquivo)}")

        # Processar e validar o CSV (se tiver erro, ele levanta o ImportacaoPendenteError)
        resultado = processar_csv_extrato(caminho_arquivo)
        metadados = resultado['metadados']
        dados = resultado['movimentacoes']

        # Salva o registro "Pai" (A Importação)
        importacao = registrar_importacao(session, caminho_arquivo, metadados['periodo_inicio'], metadados['periodo_fim'], metadados['total_movimentacoes'])

        # Busca a Categoria Padrão no Banco ("Sem Categoria")
        categoria_padrao = session.query(Categoria).filter_by(nome= 'Sem categoria').first()

        if not categoria_padrao:
            raise ValueError("Categoria padrão 'Sem categoria' não existe no banco. Rode o Seed primeiro.")
        
        # Salva as movimentações "Filhas" deduplicando o que for necessário
        novas, ignoradas = salvar_movimentacoes(session, dados, int(importacao.id), int(categoria_padrao.id))

        classificar_todas_movimentacoes(session)

        # SUCESSO ABSOLUTO (Tudo ou Nada) -> Grava definitivamente no banco de dados
        session.commit()

        logger.info(f"{novas} novas movimentações importadas com sucesso do arquivo '{os.path.basename(caminho_arquivo)}'.")
        if ignoradas > 0:
            logger.warning(f"{ignoradas} movimentações ignoradas por duplicidade.")

        return {
            "sucesso": True,
            "novas_importadas": novas,
            "ignoradas_duplicatas": ignoradas,
            "mensagem": f"{novas} novas movimentações importadas. {ignoradas} já existiam e foram ignoradas."
        }
    except Exception as e:
        session.rollback()
        logger.error(f"Falha crítica na importação do arquivo '{caminho_arquivo}': {e}", exc_info=True)
        raise e
