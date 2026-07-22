import sys
import os
import pandas as pd
from datetime import date
import io
import pytest

# Garante que o Python ache a pasta src
caminho_src = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, caminho_src)

from services.importador import (
    validar_arquivo,
    extrair_periodo,
    processar_csv_extrato,
    validar_estrutura,
    normalizar_dados,
    extrair_dados,
    ImportacaoPendenteError
)


# ─────────────────────────────────────────────
# TESTES: validar_arquivo()
# ─────────────────────────────────────────────

def test_validar_arquivo_nao_encontrado(tmp_path):
    """Arquivo em path inexistente deve lançar FileNotFoundError amigável."""
    caminho_falso = str(tmp_path / "nao_existe.csv")
    with pytest.raises(FileNotFoundError, match="Arquivo não encontrado"):
        validar_arquivo(caminho_falso)

def test_validar_arquivo_extensao_errada(tmp_path):
    """Arquivo com extensão .xlsx deve lançar ValueError amigável."""
    arquivo_xlsx = tmp_path / "extrato.xlsx"
    arquivo_xlsx.write_text("conteúdo qualquer")
    with pytest.raises(ValueError, match="Formato inválido"):
        validar_arquivo(str(arquivo_xlsx))

def test_validar_arquivo_vazio(tmp_path):
    """Arquivo CSV com 0 bytes deve lançar ValueError amigável."""
    arquivo_vazio = tmp_path / "vazio.csv"
    arquivo_vazio.write_text("")
    with pytest.raises(ValueError, match="vazio"):
        validar_arquivo(str(arquivo_vazio))

def test_validar_arquivo_valido(tmp_path):
    """Arquivo CSV com conteúdo deve passar sem exceções."""
    arquivo_valido = tmp_path / "extrato.csv"
    arquivo_valido.write_text("Extrato,,,\nDados,,,\n")
    # Não deve lançar nenhuma exceção
    validar_arquivo(str(arquivo_valido))


# ─────────────────────────────────────────────
# TESTES: validar_estrutura()
# ─────────────────────────────────────────────

def test_validar_estrutura_vazia():
    """DataFrame vazio deve ser bloqueado."""
    df_vazio = pd.DataFrame()
    valido, _ = validar_estrutura(df_vazio)
    assert not valido

def test_validar_estrutura_coluna_faltante():
    """DataFrame sem coluna obrigatória deve ser bloqueado."""
    df = pd.DataFrame({'Data Lançamento': ['01/01/2026'], 'Valor': [100]})
    valido, erro = validar_estrutura(df)
    assert not valido
    assert "Coluna obrigatória" in erro or "obrigatória" in erro.lower()

def test_validar_estrutura_tipos_errados():
    """DataFrame com valor em texto onde devia ser número deve ser bloqueado."""
    df = pd.DataFrame({
        'Data Lançamento': ['01/01/2026'],
        'Descrição': ['Teste'],
        'Valor': ['Cem Reais'],
        'Saldo': ['100']
    })
    valido, _ = validar_estrutura(df)
    assert not valido

def test_validar_estrutura_valida():
    """DataFrame com estrutura correta deve ser aceito."""
    df = pd.DataFrame({
        'Data Lançamento': ['01/01/2026'],
        'Descrição': ['Teste'],
        'Valor': ['-10,50'],
        'Saldo': ['1.000,00']
    })
    valido, erro = validar_estrutura(df)
    assert valido
    assert erro is None


# ─────────────────────────────────────────────
# TESTES: normalizar_dados()
# ─────────────────────────────────────────────

def test_normalizar_valor_invalido():
    """Valor em texto deve lançar ImportacaoPendenteError com as linhas corretas."""
    df = pd.DataFrame({
        'Data Lançamento': ['15/06/2026'],
        'Descrição': ['Compra'],
        'Valor': ['Lixo Texto'],
        'Saldo': ['1.000,00']
    })
    with pytest.raises(ImportacaoPendenteError) as exc_info:
        normalizar_dados(df)
    assert 'valor' in exc_info.value.colunas_com_erro

def test_normalizar_data_invalida():
    """Data em formato incorreto deve lançar ImportacaoPendenteError."""
    df = pd.DataFrame({
        'Data Lançamento': ['Data Errada'],
        'Descrição': ['Erro'],
        'Valor': ['-1.500,75'],
        'Saldo': ['1.000,00']
    })
    with pytest.raises(ImportacaoPendenteError) as exc_info:
        normalizar_dados(df)
    assert 'data_lancamento' in exc_info.value.colunas_com_erro

def test_normalizar_sucesso():
    """'-1.500,75' deve ser convertido corretamente para -1500.75."""
    df = pd.DataFrame({
        'Data Lançamento': ['15/06/2026'],
        'Descrição': ['Compra'],
        'Valor': ['-1.500,75'],
        'Saldo': ['1.000,00']
    })
    df_limpo = normalizar_dados(df)
    assert df_limpo.iloc[0]['valor'] == -1500.75

def test_normalizar_valor_positivo():
    """Valor sem sinal negativo deve ser convertido corretamente."""
    df = pd.DataFrame({
        'Data Lançamento': ['15/06/2026'],
        'Descrição': ['Salário'],
        'Valor': ['5.000,00'],
        'Saldo': ['5.000,00']
    })
    df_limpo = normalizar_dados(df)
    assert df_limpo.iloc[0]['valor'] == 5000.00


# ─────────────────────────────────────────────
# TESTES: extrair_dados()
# ─────────────────────────────────────────────

def test_extrair_dados_ignora_zero():
    """Transação com valor zero deve ser ignorada."""
    df = pd.DataFrame({
        'data_lancamento': [date(2026, 6, 15), date(2026, 6, 16), date(2026, 6, 17)],
        'descricao': ['Restaurante', 'Salário', 'Ignorar'],
        'valor': [-35.0, 5000.0, 0.0],
        'saldo': [100.0, 5100.0, 5100.0]
    })
    resultado = extrair_dados(df)
    assert len(resultado) == 2

def test_extrair_dados_tipo_despesa():
    """Valor negativo deve gerar tipo='despesa'."""
    df = pd.DataFrame({
        'data_lancamento': [date(2026, 6, 15)],
        'descricao': ['Restaurante'],
        'valor': [-35.0],
        'saldo': [100.0]
    })
    resultado = extrair_dados(df)
    assert resultado[0]['tipo'] == 'despesa'

def test_extrair_dados_tipo_receita():
    """Valor positivo deve gerar tipo='receita'."""
    df = pd.DataFrame({
        'data_lancamento': [date(2026, 6, 15)],
        'descricao': ['Salário'],
        'valor': [5000.0],
        'saldo': [5000.0]
    })
    resultado = extrair_dados(df)
    assert resultado[0]['tipo'] == 'receita'

def test_extrair_dados_strip_descricao():
    """Espaços nas bordas da descrição devem ser removidos."""
    df = pd.DataFrame({
        'data_lancamento': [date(2026, 6, 15)],
        'descricao': ['   Restaurante   '],
        'valor': [-35.0],
        'saldo': [100.0]
    })
    resultado = extrair_dados(df)
    assert resultado[0]['descricao'] == 'Restaurante'


# ─────────────────────────────────────────────
# TESTES: extrair_periodo()
# ─────────────────────────────────────────────

def test_extrair_periodo_valido():
    """Deve extrair as datas corretamente de um cabeçalho padrão."""
    csv_bom = io.StringIO(
        'Extrato Conta,,,\nConta,111111,,\nPeríodo,01/06/2026 a 30/06/2026,,\nSaldo:,"779,33",,\n'
    )
    inicio, fim = extrair_periodo(csv_bom)
    assert inicio == date(2026, 6, 1)
    assert fim == date(2026, 6, 30)

def test_extrair_periodo_invalido():
    """Cabeçalho corrompido deve lançar ValueError."""
    csv_ruim = io.StringIO("Extrato Conta\nSó duas linhas\n")
    with pytest.raises(ValueError, match="cabeçalho padrão"):
        extrair_periodo(csv_ruim)


def test_processar_extrato_banco_inter_separado_por_ponto_e_virgula():
    """O layout atual do Banco Inter usa `;` nos metadados e movimentações."""
    caminho_csv = os.path.join(
        os.path.dirname(__file__), '..', 'docs', 'Exemplo_CSV',
        'Extrato-01-06-2026-a-30-06-2026-CSV.csv'
    )

    resultado = processar_csv_extrato(caminho_csv)

    assert resultado['metadados']['periodo_inicio'] == date(2026, 6, 1)
    assert resultado['metadados']['periodo_fim'] == date(2026, 6, 30)
    assert resultado['metadados']['total_movimentacoes'] > 0
    assert resultado['movimentacoes'][0]['descricao'].startswith('Compra no debito')
