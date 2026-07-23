# 📊 Finance Manager — InterFIN Local

> Gerenciador financeiro pessoal para análise de extratos bancários do Banco Inter.
> Importa CSV, classifica automaticamente as movimentações por categoria e exibe um dashboard interativo com gráficos.

---

## ✨ Funcionalidades

- **Importação de Extrato CSV** — Lê e processa o arquivo CSV do Banco Inter com validação de estrutura e deduplicação automática
- **Classificação Automática** — Categoriza as movimentações por palavras-chave (ex: "RESTAURANTE" → Alimentação, "UBER" → Transporte)
- **Reclassificação Manual** — Altere a categoria de qualquer movimentação diretamente pela tabela na interface
- **Dashboard Interativo** — Visualize suas finanças filtradas por Mês e Ano com:
  - Cards de Resumo: Receitas, Despesas, Saldo e Gasto Médio Diário
  - Donut Chart de Gastos por Categoria
  - Gráfico de Barras: Receitas vs Despesas (visão anual)
  - Gráfico de Linha: Evolução Mensal de Despesas
- **Sistema de Logs** — Todas as ações são registradas em `logs/app.log`

---

## 🏗️ Arquitetura

```
finance-manager/
│
├── main.py                   # Ponto de entrada da aplicação
├── requirements.txt          # Dependências do projeto
├── gerador_de_tema.py        # Gera o tema dark mode da UI
│
├── src/
│   ├── database/
│   │   ├── conexao.py        # Engine SQLAlchemy + get_db() context manager
│   │   └── seed.py           # Categorias e palavras-chave iniciais
│   │
│   ├── models/               # Modelos SQLAlchemy (tabelas do banco)
│   │   ├── base.py
│   │   ├── categoria.py
│   │   ├── importacao.py
│   │   ├── movimentacao.py
│   │   ├── palavra_chave.py
│   │   └── resumo_mensal.py
│   │
│   ├── services/             # Regras de negócio
│   │   ├── importador.py     # Leitura, validação e salvamento do CSV
│   │   ├── classificador.py  # Classificação por palavras-chave
│   │   ├── analisador.py     # Cálculos de resumos e gráficos
│   │   ├── resumo_service.py # Geração/atualização do resumo mensal
│   │   └── movimentacao_service.py  # Atualização de categoria
│   │
│   ├── ui/
│   │   ├── app.py            # Janela principal (App)
│   │   ├── theme.json        # Tema "Dark Mode Trader" (gerado pelo gerador_de_tema.py)
│   │   └── components/
│   │       ├── cards.py      # Cards de Resumo (Receitas, Despesas, Saldo)
│   │       ├── filtros.py    # Dropdowns de Mês e Ano
│   │       ├── graficos.py   # GraficoPizza, GraficoBarras, GraficoLinha
│   │       └── tabela.py     # Tabela de Movimentações com dropdown de categoria
│   │
│   └── utils/
│       └── logger.py         # Configuração do sistema de logs
│
├── tests/                    # Testes automatizados (pytest)
│   ├── test_importador.py    # Testes de validação, normalização e extração do CSV
│   ├── test_classificador.py # Testes de classificação por palavras-chave
│   └── test_analisador.py    # Testes de cálculos financeiros (banco em memória)
│
└── logs/
    └── app.log               # Log gerado automaticamente na primeira execução
```

---

## 🛠️ Pré-requisitos

- **Python 3.10+**
- As dependências listadas em `requirements.txt`

```
sqlalchemy>=2.0
pandas>=2.0
customtkinter>=5.2
matplotlib>=3.7
pytest>=7.0
```

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/finance-manager.git
cd finance-manager
```

### 2. Crie e ative o ambiente virtual

```bash
# Criar
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Linux / macOS)
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Gere o tema da interface

```bash
python gerador_de_tema.py
```

> Isso cria o arquivo `src/ui/theme.json` com o tema **Dark Mode Trader**. Este passo é necessário antes de rodar o app pela primeira vez.

### 5. Execute o aplicativo

```bash
python main.py
```

O banco de dados `finance_manager.db` e a pasta `logs/` serão criados automaticamente na primeira execução.

---

## 📖 Como Usar

1. **Abrir o app**: Execute `python main.py`. A janela abrirá maximizada.
2. **Importar extrato**: Clique em **📥 Importar Extrato (CSV)** e selecione o arquivo CSV do Banco Inter.
3. **Filtrar por período**: Use os dropdowns de **Mês** e **Ano** no canto superior direito para navegar entre períodos.
4. **Reclassificar movimentações**: Na tabela, clique no dropdown da coluna **Categoria** de qualquer linha para alterar a classificação.
5. **Verificar logs**: Abra `logs/app.log` para ver o histórico completo de ações do sistema.

---

## 📄 Formato do CSV Esperado

O sistema foi desenvolvido para o extrato CSV do **Banco Inter**. O arquivo deve seguir este formato:

| Característica | Valor |
|---|---|
| Linhas de cabeçalho (ignoradas) | 5 (`skiprows=5`) |
| Encoding | UTF-8 (fallback automático para latin1) |
| Separador de milhar | `.` (ponto) |
| Separador decimal | `,` (vírgula) |
| Formato de data | `DD/MM/AAAA` |

**Colunas obrigatórias** (linha 6 em diante):

| Coluna | Tipo | Exemplo |
|---|---|---|
| `Data Lançamento` | Data (DD/MM/AAAA) | `15/06/2026` |
| `Descrição` | Texto | `RESTAURANTE DA MARIA` |
| `Valor` | Numérico (R$) | `-35,50` |
| `Saldo` | Numérico (R$) | `4.964,50` |

---

## 🧪 Executar Testes

```bash
# Rodar todos os testes automatizados
pytest tests/test_importador.py tests/test_classificador.py tests/test_analisador.py -v
```

**Descrição dos arquivos de teste:**

| Arquivo | O que testa |
|---|---|
| `test_importador.py` | Validação de arquivo, estrutura do CSV, normalização de dados e extração de transações |
| `test_classificador.py` | Correspondência de palavras-chave, case-insensitive, filtro por tipo (receita/despesa/ambos) |
| `test_analisador.py` | Cálculos de receitas, despesas, saldo, gasto médio diário, percentuais por categoria e evolução mensal |

> Os testes de `test_classificador.py` usam **mocks em memória** (sem banco de dados).
> Os testes de `test_analisador.py` usam **banco SQLite em memória** (`sqlite:///:memory:`) — isolados e sem efeito no banco real.

---

## 📝 Sistema de Logs

Todos os eventos do sistema são registrados automaticamente em `logs/app.log`:

| Nível | Quando é usado |
|---|---|
| `INFO` | Inicialização do banco, importação bem-sucedida, reclassificação de categoria, encerramento do app |
| `WARNING` | Movimentações ignoradas por duplicidade, fallback de encoding latin1 |
| `ERROR` | Falhas críticas na importação, erros de UI, exceções globais |

**Exemplo de log:**

```
[2026-07-20 14:30:15] [INFO]    [main.py:17]        - 🚀 Inicializando o Finance Manager...
[2026-07-20 14:30:16] [INFO]    [conexao.py:25]     - Banco de dados SQLite inicializado com sucesso.
[2026-07-20 14:30:22] [INFO]    [app.py:117]        - Usuário selecionou o arquivo para importação: junho.csv
[2026-07-20 14:30:23] [INFO]    [importador.py:292] - Iniciando importação do extrato: junho.csv
[2026-07-20 14:30:23] [INFO]    [importador.py:316] - 13 novas movimentações importadas com sucesso do arquivo 'junho.csv'.
[2026-07-20 14:30:23] [WARNING] [importador.py:318] - 2 movimentações ignoradas por duplicidade.
[2026-07-20 14:31:05] [INFO]    [app.py:180]        - Aplicativo encerrado pelo usuário via botão fechar.
[2026-07-20 14:31:05] [INFO]    [conexao.py:52]     - Banco de dados salvo e criptografado com sucesso.
```

---

## 🔐 Segurança e Privacidade dos Dados

O Finance Manager foi projetado com foco na proteção dos seus dados financeiros pessoais.

### Criptografia do Banco de Dados

O banco de dados é protegido com **criptografia AES-256 (Fernet)**:

- Durante o uso do aplicativo, o banco fica temporariamente como `finance_manager.db` na pasta do programa
- Ao **fechar o aplicativo**, o banco é automaticamente criptografado em `finance_manager.db.enc` e a versão sem criptografia é removida do disco
- A chave de descriptografia é gerada automaticamente e salva em:
  ```
  %APPDATA%\FinanceManager\secret.key
  ```

> **⚠️ Atenção:** Nunca compartilhe o arquivo `secret.key`. Sem ele, é impossível acessar o banco de dados.

### Recomendações de Instalação

- ✅ Instale em uma pasta local, como `C:\Programas\FinanceManager\`
- ❌ **Evite** instalar em pastas sincronizadas com nuvem (Google Drive, OneDrive, Dropbox)
  - O arquivo `finance_manager.db.enc` (criptografado) seria enviado para os servidores dessas plataformas
  - O arquivo `secret.key` em `%APPDATA%` **não** é sincronizado automaticamente pelo Windows — nunca o envie manualmente
- ✅ O arquivo de log `logs/app.log` **não registra caminhos completos** do seu computador, apenas os nomes dos arquivos importados

---

## 📜 Licença

Projeto pessoal para fins de estudo e uso próprio.
