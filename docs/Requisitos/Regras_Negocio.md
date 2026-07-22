## Regras de Negócio:
**Regras Financeiras:**
- O sistema deve identificar PIX recebido como receita.    
- O sistema deve identificar PIX enviado é despesa.    
- Quando uma movimentação for identificada como estorno e houver uma movimentação compatível previamente cadastrada, o sistema deverá permitir associá-las para fins de análise estatística.

**Regras de Criação e Categorização:**
- O sistema deve validar se o arquivo segue o padrão esperado.
- O sistema deve possuir as seguintes categorias:
	- Alimentação
	- Transporte
	- Lazer
	- Moradia
	- Saúde
	- Investimentos
	- Sem categoria
- Caso nenhuma regra de categorização seja encontrada, a movimentação deverá receber a categoria "Sem categoria"
- O sistema deve permitir cadastro e edição individual de movimentações, solicitando apenas os dados que são utilizados pelo banco de dados.
- Regra de Tolerância Zero na Importação: Nenhuma transação com Data ou Valor inválido será ignorada silenciosamente. O sistema suspenderá a importação e acionará um fluxo de correção manual pela Interface Gráfica, sem obrigar o usuário a refazer o upload.

**Regras de Dados e persistência:**
- O sistema deve capturar os dados do modelo de arquivo `.csv`.
- O sistema deverá armazenar em uma tabela as estatísticas calculadas para cada período analisado e seus relativos anos.
- Uma movimentação não pode ser cadastrada duas vezes.
- Cada movimentação deve possuir um identificador único.
- Toda movimentação deve possuir uma categoria.
- A categoria pode ser alterada posteriormente pelo usuário.
- Toda alteração manual deve ser salva permanentemente.
- O valor da movimentação não pode ser nulo.
- A data deve ser válida.
- O saldo deve ser numérico.
- O sistema não deve aceitar arquivos sem as colunas obrigatórias.
- Uma categoria não pode ser excluída enquanto existir movimentação vinculada.
- O sistema deverá permitir importar mais de um extrato, preservando o histórico das importações.
- Movimentações arquivadas não aparecem na interface padrão e não participam de indicadores, gráficos ou resumos; permanecem disponíveis apenas para restauração na lixeira.


**Regras de análise estatística:**
- O sistema deve calcular o gasto total do mês, realizando um somatório de todos os valores das movimentações, positivos e negativos. Ao final criar um dado que irá conter esse valor para o mês em específico selecionado.
- O sistema deverá calcular o gasto médio diário do período analisado.
- O sistema deverá calcular o total gasto por categoria e identificar a categoria com maior e menor gasto no período.
- O sistema deve fazer um cálculo que será apresentado dentro de um gráfico que apresentará a evolução dos gastos durantes os atuais meses do ano.
- O Sistema deve calcular e apresentar o saldo do período.
- O sistema deve calcular a porcentagem de gasto e recebimento por categoria.

**Regras de UI:**
- Deve haver um dropdown que conterá os meses e os anos que o usuário pode selecionar para analisar as informações.
- Deve haver gráficos ou planilhas que apresentem as comparações estatísticas que o sistema está realizando e que devem ser atualizados em tempo real.
