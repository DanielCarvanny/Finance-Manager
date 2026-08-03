import pytest
import pandas as pd
from datetime import date
from infrastructure.importacao.parsers.csv_parser import CSVParser
from infrastructure.importacao.validators.inter_validator import InterValidator
from infrastructure.importacao.normalizers.extrato_normalizer import ExtratoNormalizer
from domain.exceptions import ImportacaoPendenteError


@pytest.fixture
def parser():
    return CSVParser()


@pytest.fixture
def validator():
    return InterValidator()


@pytest.fixture
def normalizer():
    return ExtratoNormalizer()


class TestInterValidatorArquivo:
    def test_validar_arquivo_inexistente_lanca_file_not_found(self, validator):
        with pytest.raises(FileNotFoundError, match="não encontrado"):
            validator.validar_arquivo("/caminho/que/nao/existe/arquivo.csv")

    def test_validar_arquivo_extensao_errada_lanca_value_error(
        self, validator, tmp_path
    ):
        arquivo = tmp_path / "extrato.xlsx"
        arquivo.write_text("conteudo qualquer")
        with pytest.raises(ValueError, match="Formato inválido"):
            validator.validar_arquivo(str(arquivo))

    def test_validar_arquivo_vazio_lanca_value_error(self, validator, tmp_path):
        arquivo = tmp_path / "vazio.csv"
        arquivo.write_text("")
        with pytest.raises(ValueError, match="vazio"):
            validator.validar_arquivo(str(arquivo))

    def test_validar_arquivo_valido_nao_lanca_excecao(self, validator, tmp_path):
        arquivo = tmp_path / "extrato.csv"
        arquivo.write_text("Extrato,,,\nDados,,,\n")
        validator.validar_arquivo(str(arquivo))


class TestInterValidatorEstrutura:
    def test_validar_estrutura_df_vazio_retorna_false(self, validator):
        df_vazio = pd.DataFrame()
        valido, _ = validator.validar_estrutura(df_vazio)
        assert not valido

    def test_validar_estrutura_coluna_faltante_retorna_false(self, validator):
        df = pd.DataFrame({"Data Lançamento": ["01/01/2026"], "Valor": [100]})
        valido, erro = validator.validar_estrutura(df)
        assert not valido
        assert "obrigatória" in erro.lower()

    def test_validar_estrutura_tipos_incompativeis_retorna_false(self, validator):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["01/01/2026"],
                "Descrição": ["Teste"],
                "Valor": ["Cem Reais"],
                "Saldo": ["100"],
            }
        )
        valido, _ = validator.validar_estrutura(df)
        assert not valido

    def test_validar_estrutura_valida_retorna_true(self, validator):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["01/01/2026"],
                "Descrição": ["Teste"],
                "Valor": ["-10,50"],
                "Saldo": ["1.000,00"],
            }
        )
        valido, erro = validator.validar_estrutura(df)
        assert valido
        assert erro is None


class TestExtratoNormalizer:
    def test_normalizar_valor_invalido_lanca_importacao_pendente(self, normalizer):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["15/06/2026"],
                "Descrição": ["Compra"],
                "Valor": ["Lixo Texto"],
                "Saldo": ["1.000,00"],
            }
        )
        with pytest.raises(ImportacaoPendenteError) as exc_info:
            normalizer.normalizar_dados(df)
        assert "valor" in exc_info.value.colunas_com_erro

    def test_normalizar_data_invalida_lanca_importacao_pendente(self, normalizer):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["Data Errada"],
                "Descrição": ["Erro"],
                "Valor": ["-1.500,75"],
                "Saldo": ["1.000,00"],
            }
        )
        with pytest.raises(ImportacaoPendenteError) as exc_info:
            normalizer.normalizar_dados(df)
        assert "data_lancamento" in exc_info.value.colunas_com_erro

    def test_normalizar_valor_negativo_convertido_corretamente(self, normalizer):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["15/06/2026"],
                "Descrição": ["Compra"],
                "Valor": ["-1.500,75"],
                "Saldo": ["1.000,00"],
            }
        )
        df_limpo = normalizer.normalizar_dados(df)
        assert df_limpo.iloc[0]["valor"] == -1500.75

    def test_normalizar_valor_positivo_convertido_corretamente(self, normalizer):
        df = pd.DataFrame(
            {
                "Data Lançamento": ["15/06/2026"],
                "Descrição": ["Salário"],
                "Valor": ["5.000,00"],
                "Saldo": ["5.000,00"],
            }
        )
        df_limpo = normalizer.normalizar_dados(df)
        assert df_limpo.iloc[0]["valor"] == 5000.00


class TestCSVParserExtrairPeriodo:
    def test_extrair_periodo_valido(self, parser, tmp_path):
        arquivo = tmp_path / "extrato.csv"
        arquivo.write_text(
            "Extrato Conta,,,\n"
            "Conta,111111,,\n"
            "Período,01/06/2026 a 30/06/2026,,\n"
            'Saldo:,"779,33",,\n'
        )
        inicio, fim = parser.extrair_periodo(str(arquivo))
        assert inicio == date(2026, 6, 1)
        assert fim == date(2026, 6, 30)

    def test_extrair_periodo_invalido_lanca_value_error(self, parser, tmp_path):
        arquivo = tmp_path / "extrato.csv"
        arquivo.write_text("Extrato Conta\nSo duas linhas\n")
        with pytest.raises(ValueError, match="cabeçalho padrão"):
            parser.extrair_periodo(str(arquivo))

    def test_localizar_cabecalho_e_delimitador_ponto_e_virgula(self, parser, tmp_path):
        arquivo = tmp_path / "extrato.csv"
        arquivo.write_text(
            "Extrato Conta,,,\n"
            "Período,01/06/2026 a 30/06/2026,,\n"
            "Data;Descrição;Valor;Saldo\n"
            "10/06/2026;Compra;-50,00;950,00\n"
        )
        indice, delimitador = parser.localizar_cabecalho_e_delimitador(str(arquivo))
        assert indice == 2
        assert delimitador == ";"


class TestCSVParserExtrairDados:
    def test_extrair_dados_ignora_valor_zero(self, parser):
        df = pd.DataFrame(
            {
                "data_lancamento": [
                    date(2026, 6, 15),
                    date(2026, 6, 16),
                    date(2026, 6, 17),
                ],
                "descricao": ["Restaurante", "Salário", "Ignorar"],
                "valor": [-35.0, 5000.0, 0.0],
                "saldo": [100.0, 5100.0, 5100.0],
            }
        )
        resultado = parser.extrair_dados(df)
        assert len(resultado) == 2

    def test_extrair_dados_tipo_despesa(self, parser):
        df = pd.DataFrame(
            {
                "data_lancamento": [date(2026, 6, 15)],
                "descricao": ["Restaurante"],
                "valor": [-35.0],
                "saldo": [100.0],
            }
        )
        resultado = parser.extrair_dados(df)
        assert resultado[0]["tipo"] == "despesa"

    def test_extrair_dados_tipo_receita(self, parser):
        df = pd.DataFrame(
            {
                "data_lancamento": [date(2026, 6, 15)],
                "descricao": ["Salário"],
                "valor": [5000.0],
                "saldo": [5000.0],
            }
        )
        resultado = parser.extrair_dados(df)
        assert resultado[0]["tipo"] == "receita"

    def test_extrair_dados_strip_descricao(self, parser):
        df = pd.DataFrame(
            {
                "data_lancamento": [date(2026, 6, 15)],
                "descricao": ["   Restaurante   "],
                "valor": [-35.0],
                "saldo": [100.0],
            }
        )
        resultado = parser.extrair_dados(df)
        assert resultado[0]["descricao"] == "Restaurante"
