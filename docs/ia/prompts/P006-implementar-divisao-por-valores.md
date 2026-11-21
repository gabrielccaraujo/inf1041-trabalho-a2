# P006 - Implementacao da #5: Divisao por valores (H1)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: d00d8f8
- Objetivo: implementar a issue #5 com TDD, em branch `feat/` propria e PR com "Closes #5". Terceira issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1 e #5, `GLOSSARY.md`, `docs/adr/0003` e `0008` e o codigo da H1 (#4).
- Criterios de aceitacao: os da #5; teste falhando antes de cada implementacao; use cases testados com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004. Depois do merge do PR #11, o grupo respondeu:

```text
pronto
```

## Interacoes durante a intervencao

- Ciclos red -> green: use case com `DivisaoPorValores` (Cotas informadas, soma diferente do Valor, Cota zero ou negativa, Membro repetido, Membro de fora do Grupo, sem Cotas); contrato da API (201 com listagem, 422, 400 para Cotas malformadas).
- O criterio "Se o ticket de Saldos ja tiver entrado" nao se aplica: a #6 ainda nao entrou. Fica para a #6 cobrir os Saldos com Divisao por valores.
- Revisao em dois eixos (`code-review`), sem bloqueios. Aplicado: `Divisao.por_valores` recebe `Cota`s; teste de API para as regras de 422; helpers de teste sem argumento vazio sem sentido.

## Resultado

- Resumo da resposta: fabrica `Divisao.por_valores` (Cota positiva), pedido `DivisaoPorValores` e leitor `por_valores` no mapa de modos da rota. `LancarDespesa` e `Despesa` nao mudaram (OCP, ADR 0003).
- Arquivos alterados: `app/routes/`, `domain/despesa.py`, `use_cases/lancar_despesa.py`, `tests/`, `README.md` e este registro.
- Testes e resultados: 94 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: a44b93d (implementacao) e dc3fdba (correcoes da revisao)
- Observacoes: nenhuma.
