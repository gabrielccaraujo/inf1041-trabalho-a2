# P007 - Implementacao da #6: Saldos e Transferencias sugeridas (H2)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: dfbf108
- Objetivo: implementar a issue #6 com TDD, em branch `feat/` propria e PR com "Closes #6". Quarta issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1, #5 e #6, `GLOSSARY.md`, `docs/adr/0004` e `0008` e o codigo da H1.
- Criterios de aceitacao: os da #6 e o criterio de Saldos pendente da #5; teste falhando antes de cada implementacao; use cases com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004. Depois do merge do PR #12, o grupo respondeu:

```text
pronto
```

## Interacoes durante a intervencao

- Ciclos red -> green: `ConsultarSaldos` (Grupo sem Despesas; Saldo com sobra de centavos e Transferencias), que trouxe a `CalculadoraDeSaldos` inteira; contrato da API.
- Os testes de cenario misto (igualitaria com sobra, por valores, Pagador fora da Divisao), N-1, Saldos zerados e empate passaram ja no primeiro verde, porque o algoritmo guloso entrou inteiro. Para checar que nao eram vacuos, duas mutacoes temporarias (desempate invertido; devedor qualquer em vez do maior) foram pegas pelos testes e revertidas.
- Revisao em dois eixos (`code-review`), sem bloqueios. O revisor de spec rodou 20.000 historicos aleatorios contra a calculadora (soma zero, Transferencias positivas que zeram tudo, no maximo N-1, independencia da ordem). Aplicado: soma zero verificada em varios cenarios, teste isolado de Divisao por valores e troca de um teste quase tautologico.
- Fica para a #7: o caminho dos Pagamentos na calculadora (parametro pedido pela #6) ainda nao e exercitado por teste.

## Resultado

- Resumo da resposta: servico puro `CalculadoraDeSaldos` (Saldos e Transferencias sugeridas, desempate pela ordem dos Membros), use case `ConsultarSaldos`, rota `GET /api/grupos/{id}/saldos`. Saldo nao e persistido (ADR 0004).
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `tests/`, `README.md` e este registro.
- Testes e resultados: 105 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: 76dc1ff (implementacao) e d3e1845 (testes reforcados na revisao)
- Observacoes: nenhuma.
