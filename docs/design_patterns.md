# Padrões de Projeto (Design Patterns) — Finance Manager v2.0

> Documentação técnica dos padrões de software adotados no sistema para garantir manutenibilidade, extensibilidade e testabilidade.

---

## 🎯 Resumo dos Padrões Adotados

| Padrão | Categoria | Onde é Aplicado | Benefício Principal |
|---|---|---|---|
| **Repository Pattern** | Arquitetural / Acesso a Dados | `src/infrastructure/repositories/` | Isola consultas SQLAlchemy da regra de negócio |
| **Unit of Work Pattern** | Transacional | `src/infrastructure/database/unit_of_work.py` | Garante transações atômicas compartilhando a mesma sessão |
| **Strategy Pattern** | Comportamental | `src/application/importacao/strategies/` | Permite adicionar novos bancos/extratos sem alterar o código |
| **MVVM Leve** | Apresentação | `src/ui/viewmodels/` | Desacopla a interface Tkinter dos modelos do banco de dados |
| **Single Responsibility Helpers** | Estrutural / Utilitário | `src/infrastructure/importacao/{parsers,validators,normalizers}` | Separa parsing, validação e conversão de dados |

---

## 1. Repository Pattern (Padrão Repositório)

O padrão Repositório atua como uma coleção em memória entre a camada de domínio e a persistência física.

- **Classe Base Genérica**:
  ```python
  class BaseRepository(Generic[T]):
      def create(self, entidade: T) -> T: ...
      def get_by_id(self, id_entidade: int) -> Optional[T]: ...
      def get_all(self) -> List[T]: ...
      def delete(self, entidade: T) -> None: ...
  ```
- **Repositórios Específicos**:
  - `MovimentacaoRepository`: Encapsula queries como `listar_por_periodo()`, `calcular_total_receitas()`, `obter_anos_disponiveis()`.
  - `CategoriaRepository`: Encapsula busca por nome (`buscar_por_nome()`).
  - `ResumoMensalRepository`: Gerencia a tabela de resumos consolidados.
  - `PalavraChaveRepository`: Carrega palavras-chave com join eager nas categorias.

---

## 2. Unit of Work Pattern (Unidade de Trabalho)

O `UnitOfWork` gerencia as transações do banco de dados, garantindo que múltiplos repositórios compartilhem exatamente a mesma sessão do SQLAlchemy.

```python
with UnitOfWork() as uow:
    cat = uow.categorias.buscar_por_nome('Sem categoria')
    uow.movimentacoes.salvar_lote(novas_movimentacoes)
    uow.commit() # Confirmação explícita
```

- **Rollback Automático**: Caso ocorra qualquer exceção dentro do bloco `with`, o método `__exit__` executa `uow.rollback()` automaticamente.

---

## 3. Strategy Pattern (Padrão Estratégia)

O processamento de extratos bancários varia por instituição (Banco Inter, Nubank, Itaú, OFX). O Strategy Pattern encapsula cada algoritmo de parsing em uma classe independente.

- **Interface Base (`EstrategiaImportacao`)**:
  ```python
  class EstrategiaImportacao(ABC):
      @abstractmethod
      def pode_processar(self, caminho_arquivo: str) -> bool: ...

      @abstractmethod
      def processar(self, caminho_arquivo: str) -> dict: ...
  ```
- **Estratégia Concreta (`EstrategiaCSVInter`)**:
  Implementa a leitura de extratos CSV do Banco Inter usando componentes especializados (`CSVParser`, `InterValidator`, `ExtratoNormalizer`).

---

## 4. MVVM Leve (Model-View-ViewModel)

Para evitar vazamento de objetos SQLAlchemy (instâncias com estado ativo/detached) para os componentes visuais, adota-se a camada ViewModel.

- **Fluxo de Dados**:
  $$\text{View (CustomTkinter)} \longleftrightarrow \text{ViewModel (Python DTOs)} \longleftrightarrow \text{Services / UnitOfWork}$$
- **Benefícios**:
  - A interface gráfica trata apenas dicionários e tipos primitivos (`int`, `float`, `str`).
  - Os ViewModels podem ser testados unitariamente sem carregar widgets gráficos do Tkinter.

---

## 5. Decomposição de Componentes em Infraestrutura

O processamento de extratos foi decomposto em três sub-responsabilidades:

1. **Parsers (`CSVParser`)**: Leitura do arquivo e localização de cabeçalhos/delimitadores.
2. **Validators (`InterValidator`)**: Validação de existência física, extensões e integridade de colunas.
3. **Normalizers (`ExtratoNormalizer`)**: Limpeza de formato monetário (ex: `'-1.500,75'` $\rightarrow$ `-1500.75`) e parsing de datas.
