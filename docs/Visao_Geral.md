# Visão Geral do Sistema — Finance Manager v2.0

## O que é o projeto?
O **Finance Manager v2.0** é um aplicativo desktop de gestão financeira pessoal desenvolvido em Python com **CustomTkinter**, **SQLAlchemy** e **Matplotlib**. Ele automatiza a leitura de extratos bancários, categoriza lançamentos por inteligência de regras, gerencia arquivamento na lixeira (com integridade de estornos) e apresenta um dashboard analítico interativo.

---

## Principais Recursos da Versão 2.0

- 📥 **Importação Extensível via Strategy Pattern**: Leitura e validação de extratos com deduplicação de movimentações por assinatura única.
- 🏷️ **Classificação Automática & Reclassificação Manual**: Categorização automática baseada em palavras-chave e reclassificação interativa na tabela.
- 🗑️ **Lixeira Inteligente (Soft Delete)**: Arquivamento e restauração com garantia de consistência de estornos vinculados.
- 📊 **Dashboard Analítico**: Indicadores de Receitas, Despesas, Saldo, Gasto Diário Médio e gráficos interativos (Pizza, Barras Anuais, Linha de Evolução).
- 🔒 **Persistência Transacional & Criptografia**: Controle de transação atômico via `UnitOfWork` e criptografia AES-256 (Fernet) do banco SQLite em repouso.
- 🧱 **Arquitetura Desacoplada (MVVM + 4 Camadas)**: Separação rigorosa entre Apresentação, Aplicação, Infraestrutura e Domínio.

---

## Arquitetura em 4 Camadas (v2.0)

```
┌──────────────────────────────────────────────────────────────┐
│  CAMADA DE APRESENTAÇÃO (UI / MVVM)                          │
│  CustomTkinter Views (App, JanelaLixeira) & ViewModels       │
├──────────────────────────────┬───────────────────────────────┤
│                              │ DTOs (Dicionários/Primitivos) │
│                              ▼                               │
│  CAMADA DE APLICAÇÃO (Services)                              │
│  ImportacaoService, ClassificadorService, ResumoService, etc.│
├──────────────────────────────┬───────────────────────────────┤
│                              │ UnitOfWork & Repositórios     │
│                              ▼                               │
│  CAMADA DE INFRAESTRUTURA                                    │
│  UnitOfWork, Database (conexao.py), Repositories, Parsers    │
├──────────────────────────────┬───────────────────────────────┤
│                              │ Entidades SQLAlchemy          │
│                              ▼                               │
│  CAMADA DE DOMÍNIO                                           │
│  Models (Movimentacao, Categoria, etc.) & Exceptions         │
└──────────────────────────────────────────────────────────────┘
```

---

## Público-alvo e Modo de Operação
- **Uso pessoal e local**: Execução local sem dependência de servidores web externos.
- **Segurança de dados**: O banco de dados fica criptografado localmente no disco do usuário.
