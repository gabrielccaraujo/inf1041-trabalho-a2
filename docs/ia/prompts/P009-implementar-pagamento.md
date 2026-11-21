# P009 - Implementacao da #7: Registrar Pagamento (H2)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: 1094b88
- Objetivo: implementar a issue #7 com TDD, em branch `feat/` propria e PR com "Closes #7". Sexta issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1 e #7, `GLOSSARY.md`, `docs/adr/0004`, `0007`, `0008` e `0009` e o codigo da H0 a H3.
- Criterios de aceitacao: os da #7; teste falhando antes de cada implementacao; use cases com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004. Depois do merge do PR #14, o grupo respondeu:

```text
pronto
```

## Interacoes durante a intervencao

- Ciclos red -> green: `RegistrarPagamento` e `ListarPagamentos` (Meio e data do relogio); regras de 422 (de e para iguais, Valor nao positivo, Membro de fora) e 404; `ConsultarSaldos` passando a carregar os Pagamentos (pagar a Transferencia sugerida zera os dois, pagar todas zera o Grupo, parcial e maior que o devido, soma zero); contrato da API com despesa -> saldo -> pagamento -> saldo zerado.
- O caminho dos Pagamentos na `CalculadoraDeSaldos`, que entrou na #6 sem teste, foi verificado com uma mutacao temporaria (sinal invertido): 4 testes falharam; revertida.
- Revisao em dois eixos (`code-review`), sem bloqueios. Aplicado: a calculadora exige os Pagamentos (sem default), docstring sem "transferencia" (termo a evitar para Pagamento), teste de API com nome de comportamento e sem casos ja cobertos nos use cases.
- Para o grupo decidir: o Meio trafega em minusculas (`"pix"`, `"dinheiro"`, `"outro"`), desde a #8; `"PIX"` da 400.

## Resultado

- Resumo da resposta: `Pagamento` (raiz, declarativo), porta `PagamentoRepository` com implementacao SQLite (tabela `pagamentos`), use cases `RegistrarPagamento` (relogio injetavel) e `ListarPagamentos`, `ConsultarSaldos` com Pagamentos, rotas `POST` e `GET /api/grupos/{id}/pagamentos`.
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `infra/`, `tests/`, `README.md` e este registro.
- Testes e resultados: 165 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: 6e72990 (implementacao) e 4306bcd (correcoes da revisao)
- Observacoes: a historia 31 (ver a Chave Pix de quem recebe) ja e atendida por `GET /api/grupos/{id}`.
