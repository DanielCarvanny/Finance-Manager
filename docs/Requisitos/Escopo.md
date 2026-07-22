## Escopo inicial
- apenas o Banco Inter será suportado inicialmente;
- o sistema não será uma aplicação web;
- será executado localmente;
- poderá futuramente ser distribuído como executável.

## MVP
O sistema precisa realizar 5 funções principais:
#### 1. Importação
1.1) Receber um arquivo csv de extrato bancário.
- extrato.csv
1.2) validar se o arquivo segue o padrão esperado.
#### 2. Processamento
Interpretar e normalizar os dados do arquivo CSV:
- Data de lançamento
- Descrição
- Valor
- Saldo
- Período do Extrato
#### 3. Classificação
Classificar automaticamente as movimentações utilizando regras de categorização baseadas na descrição da transação:
- Alimentação
- Transporte
- Lazer
- Moradia
- Saúde
- Investimentos
- Sem categoria
#### 4. Análise
Gerar indicadores:
- Total gasto no mês
- Total recebido: Somatório de salário e movimentações de recebi
- Gasto de média diária;
- Categoria com maior gasto;
- Categoria com menor gasto;
- Evolução dos gastos mensal;
- saldo do período;
- percentual de gastos e recebimentos por categoria.
#### 5. Visualização
A interface deverá permitir:
- visualizar movimentações;
- visualizar gráficos;
- visualizar indicadores;
- filtrar por período;
- consultar gastos por categoria.