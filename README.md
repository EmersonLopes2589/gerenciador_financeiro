# Gerenciador de Finanças

Uma API simples para gerenciar finanças pessoais: importar transações via CSV, categorizar automaticamente, consultar resumos por categoria e por mês, e gerenciar orçamentos mensais por categoria.

---

## Status
Protótipo funcional. Código backend em Python (FastAPI). Banco padrão: SQLite (`transacoes.db`) incluído como exemplo. Há exemplos de testes e um CSV de exemplo.

## Recursos
- Importação de transações a partir de arquivo CSV (ver formato esperado).
- Deduplicação automática (uniqueness por data+descrição+valor).
- Categorização automática das transações.
- Resumo de receitas/despesas por categoria e por mês.
- Definição e consulta de orçamentos mensais por categoria.
- Interface estática servida a partir da pasta `static/`.

## Tecnologias
- Python + FastAPI
- SQLite (padrão, via arquivo `transacoes.db` ou variável de ambiente)
- Requisitos listados em `Gerenciador_Financas/requirements.txt`:
  - fastapi
  - uvicorn
  - python-multipart
  - pytest
  - httpx

## Requisitos
- Python 3.10+ (recomendado)
- Git
- Opcional: Docker

## Instalação (local)
1. Clone o repositório:
   ```bash
   git clone https://github.com/EmersonLopes2589/gerenciador_financeiro.git
   cd gerenciador_financeiro/Gerenciador_Financas
   ```

2. Crie e ative um virtualenv, instale dependências:
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```

3. (Opcional) Configure o caminho do banco via variável de ambiente:
   ```bash
   export FINANCAS_DB=/caminho/para/transacoes.db
   # Windows (PowerShell):
   # $env:FINANCAS_DB = "C:\\caminho\\transacoes.db"
   ```

## Como executar
Inicie a API com Uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- A aplicação cria as tabelas no arranque se não existirem.
- A pasta `static/` é montada na raiz (`/`) e serve arquivos estáticos.

## Limites / Observações
- Limite de upload para importação: ~5 MB.
- Banco padrão: arquivo `transacoes.db` no diretório (ou ajuste via `FINANCAS_DB`).

## API (principais endpoints)
- POST /transacoes/importar
  - Descrição: importa um CSV multipart/form-data (campo `file`).
  - Cabeçalho CSV esperado: `data,descricao,valor` (ex.: `2026-07-01,Salário,5200.00`)
  - Resposta: resumo de importação (importadas, duplicadas, erros).
  - Erros:
    - 400 quando o arquivo tem erros de validação (ex.: cabeçalho inválido, linhas mal-formadas).
    - 413 quando o arquivo excede 5 MB.

  Exemplo (cURL):
  ```bash
  curl -F "file=@transacoes_exemplo.csv" http://localhost:8000/transacoes/importar
  ```

- GET /resumo/categorias
  - Retorna lista com totais por categoria: receitas, despesas e líquido.

- GET /resumo/meses
  - Retorna lista com totais por mês (formato `YYYY-MM`): receitas, despesas e líquido.

- POST /orcamentos
  - Define/atualiza o limite mensal de uma categoria.
  - Corpo (JSON): { "categoria": "Alimentação", "mes": "2026-10", "limite": 1500.00 }
  - Retorna status do orçamento (limite, gasto, percentual, alerta).

- GET /orcamentos/{mes}
  - Lista o status dos orçamentos para o mês informado (YYYY-MM).

## Formato CSV esperado
- Encoded em UTF-8 (ou UTF-8-sig)
- Cabeçalho exato:
  ```
  data,descricao,valor
  ```
- Exemplo de linha:
  ```
  2026-07-01,Salário empresa XYZ,5200.00
  ```
- Arquivo de exemplo incluído: `transacoes_exemplo.csv`

## Banco de dados
- Estrutura principal (SQLite):
  - tabela `transacoes` (id, data, descricao, valor_centavos, categoria) — UNIQUE (data, descricao, valor_centavos)
  - tabela `orcamentos` (id, categoria, mes, limite_centavos) — UNIQUE (categoria, mes)
- Valores monetários são armazenados em centavos (inteiro) internamente.

## Testes
- Testes automatizados estão na pasta `tests/` (se presentes).
- Executar:
  ```bash
  pytest
  ```

## Estrutura do projeto (resumida)
- app/                — código fonte (FastAPI)
  - main.py           — rotas e ponto de entrada
  - db.py             — camada de persistência (SQLite)
  - importer.py       — parser/validador do CSV
  - categorizer.py    — lógica de categorização de descrição -> categoria
  - models.py         — Pydantic models/respostas
- static/             — arquivos estáticos servidos pela aplicação
- tests/              — testes
- transacoes.db       — banco SQLite de exemplo (opcional)
- transacoes_exemplo.csv — CSV de exemplo
- requirements.txt

## Contribuição
1. Fork e clone este repositório.
2. Crie uma branch descritiva: `git checkout -b feature/minha-melhoria`.
3. Adicione testes e documente mudanças.
4. Abra um Pull Request descrevendo o que foi alterado.

## Licença
Adicionar um arquivo `LICENSE` com a licença desejada (ex.: MIT). Se preferir, posso sugerir um template.

## Contato
Emerson Lopes — https://github.com/EmersonLopes2589
