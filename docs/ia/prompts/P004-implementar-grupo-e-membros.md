# P004 - Implementacao da #3: Grupo e Membros (H0)

- Data: 2026-11-20
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: 772e8b9
- Objetivo: implementar a issue #3 (primeira fatia vertical, H0) com TDD, em branch `feat/` propria e PR com "Closes #3". Primeira de uma sequencia (#3 -> #4 -> #5, #6, #8 -> #7 -> #9), uma issue por PR.
- Arquivos e contexto fornecidos: issues #1 e #3, `GLOSSARY.md`, `docs/adr/0001` a `0009` e o codigo atual (placeholder `Task`, `create_app`, testes existentes).
- Criterios de aceitacao: os da #3; teste falhando antes de cada implementacao; use cases testados com repositorio falso em memoria; PEP-8; suite inteira passando.

## Prompt integral

```text
/mattpocock-skills:implement Implemente a sequência de issues do RachAÍ na ordem de dependência:
#3 → #4 → #5, #6, #8 → #7 → #9.

Para cada uma: branch feat/ a partir da main, TDD com teste falhando primeiro,
use case testado com repositório falso em memória, PEP-8, suíte inteira passando,
e abra o PR com "Closes #N".

Use os termos do GLOSSARY.md e respeite as ADRs. Uma issue por PR.
Quando o PR estiver aberto, me avise para eu mesclar, e siga para a próxima
assim que eu confirmar.

Comece pela #3.
```

## Interacoes durante a intervencao

- Seams de teste: os definidos na spec (#1, "Testing Decisions"), sem nova consulta: use cases com `GrupoRepositoryEmMemoria` (regras) e API via `create_app(":memory:")` (status, formato `{"erro"}`, persistencia de ida e volta).
- Ciclos red -> green: `CriarGrupo`; `AdicionarMembro`; regras do Membro (nome vazio, nome repetido sem diferenciar maiusculas, Chave Pix aparada, em branco vira ausente, limite de 77) e Grupo inexistente; `ConsultarGrupo`; contrato da API.
- Revisao em dois eixos (`code-review`: padroes e spec) antes do PR. Aplicado: erros HTTP do Flask (404 de rota, 405) no formato `{"erro"}`; leitura do corpo separada em `app/routes/requisicao.py`; helper renomeado para `obter_grupo_ou_falhar` (`use_cases/comum.py`); unicidade de nome tambem na construcao do Grupo; insercao atomica de Grupo e Membros. Mantido de proposito: nome de Membro unico sem diferenciar maiusculas ("Ana" e "ana" confundem, que e o que a historia 4 quer evitar); `Grupo.pertence` fica para a #4, que e quem o usa; o teste de concorrencia do `Database` segue chamando o repositorio direto, porque verifica a seguranca entre threads e nao comportamento de repositorio.

## Resultado

- Resumo da resposta: dominio `Grupo`/`Membro` com porta `GrupoRepository` (`Protocol`), excecoes `RegraDeDominioViolada` (422) e `NaoEncontrado` (404), use cases `CriarGrupo`, `AdicionarMembro` e `ConsultarGrupo`, repositorio SQLite (tabelas `grupos` e `membros`), rotas sob `/api/grupos` com traducao de erros em `app/routes/erros.py`. Placeholder `Task` removido; health check mantido.
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `infra/`, `tests/`, `README.md` e este registro.
- Testes e resultados: 40 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: 44a58f3 (implementacao) e ccb84a4 (correcoes da revisao)
- Observacoes: o teste de concorrencia do `Database` passou a usar o repositorio de Grupo no lugar do de `Task`.
