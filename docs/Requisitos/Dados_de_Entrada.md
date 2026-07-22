## Dados do CSV
- Data de lançamento
- Descrição
- Valor
- Saldo
- Período do Extrato

---
## Tipo dos dados
|   Campo   |  Tipo   | Obrigatório |
| :-------: | :-----: | :---------: |
|   Data    |  Date   |     SIM     |
| Descrição | String  |     SIM     |
|   Valor   | Decimal |     SIM     |
|   Saldo   | Decimal |     SIM     |
|  Período  | String  |     SIM     |

---
## Descrição
- **Data de lançamento**: Data que ocorreu a movimentação.

- **Descrição**: Texto fornecido pelo Banco Inter contendo informações sobre a natureza da movimentação (compra, PIX, estorno, TED etc.) e, quando disponível, o estabelecimento ou favorecido relacionado à transação.

- **Valor**: Valor monetário da movimentação. Valores negativos representam saídas de recursos (despesas) e valores positivos representam entradas (receitas).
  
- **Saldo**: Saldo disponível na conta imediatamente após o processamento da movimentação.
  
- **Período**: Intervalo de datas correspondente ao extrato importado. Essa informação é utilizada para identificar o período de referência da importação.

---
## Regras de Validação
- A data deve possuir formato válido.
- O valor deve ser numérico.
- O saldo deve ser numérico.
- A descrição não pode estar vazia.
- Arquivos com colunas ausentes deverão ser rejeitados.

---

## Mapeamento dos Dados
| Campo do CSV    | Campo interno |
| --------------- | ------------- |
| Data Lançamento | data          |
| Descrição       | descricao     |
| Valor           | valor         |
| Saldo           | saldo         |