# Roadmap — Finance Manager

## Status do Projeto

- **Versão 1.0 (Legada)**: ✅ Concluída (Monólito Funcional)
- **Versão 2.0 (Atual)**: ✅ **100% Refatorada & Documentada** (Arquitetura em 4 Camadas, Repositórios, Unit of Work, Strategy Pattern, MVVM, Alembic)

---

## Histórico de Etapas da Refatoração v2.0

### Etapa 0: Housekeeping & Preparação ✅
- Organização do repositório, criação do ambiente virtual e estruturação inicial.

### Etapa 1: Versionamento com Alembic ✅
- Configuração do Alembic para migrações de schema de banco de dados.
- Integração programática em `conexao.py` para automação no startup.

### Etapa 2: Repository Pattern & Unit of Work ✅
- Implementação de `BaseRepository[T]` e repositórios concretos (`MovimentacaoRepository`, `CategoriaRepository`, etc.).
- Implementação do `UnitOfWork` como Context Manager para controle transacional atômico.

### Etapa 3: Strategy Pattern & Refatoração dos Serviços ✅
- Decomposição do módulo de importação em `parsers/`, `validators/` e `normalizers/`.
- Criação da interface `EstrategiaImportacao` e implementação de `EstrategiaCSVInter`.
- Refatoração dos serviços (`ClassificadorService`, `AnalisadorService`, `ResumoService`, `MovimentacaoService`).

### Etapa 4: Camada ViewModel & Desacoplamento da UI ✅
- Criação das ViewModels (`DashboardViewModel`, `ImportacaoViewModel`, `LixeiraViewModel`).
- Remoção de todas as instâncias de `get_db()` e queries SQLAlchemy de dentro dos componentes visuais.
- Comunicação View $\longleftrightarrow$ ViewModel via DTOs/Dicionários simples.

### Etapa 5: Testes Unitários, Integração e Garantia de Qualidade ✅
- Criação de suíte de testes com `pytest` utilizando banco SQLite em memória (`sqlite:///:memory:`).
- Cobertura de repositórios, estratégias de importação, serviços e ViewModels.

### Etapa 6: Documentação Abrangente v2.0 ✅
- Elaboração de `arquitetura_v2.md`, `design_patterns.md`, `migracoes_alembic.md`.
- Atualização de `estrutura_projeto.md`, `roadmap.md`, `Visao_Geral.md` e `README.md`.

### Etapa 7: Ajustes Finais e Correções ✅
- Correção da atualização em tempo real dos gráficos na reclassificação.
- Proteção das categorias alteradas manualmente contra sobrescrita na reimportação.
- Validação e sincronização da classificação por palavras-chave com `flush()`.

### Etapa 8: Empacotamento, Distribuição & Release v1.0.0 ✅
- Empacotamento executável standalone via PyInstaller (`.spec`).
- Criação do instalador executável `.exe` via Inno Setup (`installer.iss`).
- **Release oficial Version 1.0.0 divulgada e disponível no GitHub!**

---

## Evolução Futura (Roadmap v2.1+)

### v2.1 — Extensibilidade de Extratos
- [ ] Implementação de `EstrategiaOFX` (suporte a extratos em formato padrão OFX).
- [ ] Implementação de `EstrategiaNubank` e `EstrategiaItau`.

### v2.2 — Relatórios e Exportação
- [ ] Exportação de relatórios financeiros consolidados em PDF e Excel.
- [ ] Gráficos comparativos entre múltiplos anos.

### v3.0 — Recursos Avançados
- [ ] Orçamentos mensais por categoria com alertas de limite.
- [ ] Leitura automatizada via OCR/PDF.