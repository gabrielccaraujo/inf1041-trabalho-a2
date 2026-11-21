# P005 - Implementacao da #4: Despesa com Divisao igualitaria (H1)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: 4410893
- Objetivo: implementar a issue #4 com TDD, em branch `feat/` propria e PR com "Closes #4". Segunda issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1 e #4, `GLOSSARY.md`, `docs/adr/0002`, `0003`, `0008` e `0009` e o codigo da H0.
- Criterios de aceitacao: os da #4; teste falhando antes de cada implementacao; use cases testados com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004 (sequencia #3 -> #4 -> #5, #6, #8 -> #7 -> #9). Depois do merge do PR #10, o grupo respondeu:

```text
esta tudo certo, pode seguir
```

## Interacoes durante a intervencao

- Ciclos red -> green: Divisao igualitaria com sobra de centavos para os primeiros (10000 / 3 = 3334, 3333, 3333); regras de 422 (Valor zero ou negativo, descricao vazia, Pagador ou Membro da Divisao de fora do Grupo, Divisao sem Membros, Membro repetido) e Grupo inexistente; `ListarDespesas`; contrato da API. Os testes de Pagador fora da Divisao e de data do relogio ja passaram com o codigo do primeiro ciclo e ficaram como especificacao.
- Revisao em dois eixos (`code-review`). Aplicado: a soma das Cotas passou a ser garantida pela propria `Divisao`, que carrega o Valor repartido (ADR 0003); o pedido de Divisao virou `Protocol` (`PedidoDeDivisao`) e a rota escolhe o leitor por um mapa de modos, para que a #5 so acrescente uma fabrica e um leitor (OCP); `Grupo.pertence` virou `tem_membro`; a subtracao ainda nao usada saiu de `Valor`; os testes deixaram de usar "participante", termo que o glossario manda evitar.
- Mantido de proposito: corpo malformado num Grupo inexistente da 400, porque a rota valida o formato antes do use case (ADR 0008); Cota de 0 centavo na divisao igualitaria (ex.: 2 centavos entre 3 Membros), que segue a regra da sobra e fica para decisao do grupo.

## Resultado

- Resumo da resposta: VO `Valor` (centavos, `dividir_em`), `Despesa` com `Divisao` e `Cota`, porta `DespesaRepository` com implementacao SQLite (tabelas `despesas` e `cotas`, com `posicao` para manter a ordem das Cotas), use cases `LancarDespesa` (relogio injetavel) e `ListarDespesas`, rotas `POST` e `GET /api/grupos/{id}/despesas`.
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `infra/`, `tests/`, `README.md` e este registro.
- Testes e resultados: 75 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: 6caf6f6 (implementacao) e 581013e (correcoes da revisao)
- Observacoes: nenhuma.
