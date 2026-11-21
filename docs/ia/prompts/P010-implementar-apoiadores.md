# P010 - Implementacao da #9: ranking de Apoiadores (H4)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: ebd2b4b
- Objetivo: implementar a issue #9 com TDD, em branch `feat/` propria e PR com "Closes #9". Ultima issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1 e #9, `GLOSSARY.md`, `docs/adr/0006`, `0008` e `0009` e o codigo da H0 a H3.
- Criterios de aceitacao: os da #9; teste falhando antes de cada implementacao; use cases com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004. Depois do merge do PR #15, o grupo respondeu:

```text
pronto
```

## Interacoes durante a intervencao

- Ciclos red -> green: ranking com um cenario que exercita os tres criterios (total, Vaquinhas apoiadas, nome), com Membros cadastrados fora da ordem alfabetica para que o desempate por nome nao coincida com a ordem dos ids; contrato da API.
- Os testes de Membro sem Contribuicao, Vaquinha encerrada, varias Contribuicoes na mesma Vaquinha e Grupo sem Contribuicoes passaram ja com o codigo do primeiro ciclo. Seis mutacoes temporarias (cada criterio de ordem invertido ou trocado, contagem de Vaquinhas, filtro de quem nunca contribuiu, contagem por Contribuicao) foram pegas pelos testes e revertidas. Na primeira tentativa o script de mutacao nao restaurou o arquivo (ainda nao versionado); o arquivo foi reescrito e as mutacoes refeitas uma a uma.
- "Despesas e Pagamentos nao contam" e verificado pela API: Carla so paga uma Despesa e faz um Pagamento e nao aparece no ranking.
- Revisao em dois eixos (`code-review`), sem bloqueios. Aplicado: acumulador unico por Membro; GLOSSARY alinhado ao ADR 0006 (desempate por nome); fixture mais legivel. Nao aplicado: `membro_id` como ultimo criterio, porque o Grupo ja garante nome unico (sem diferenciar maiusculas).

## Resultado

- Resumo da resposta: servico puro `ReconhecimentoDeAjuda` (recebe Membros e Vaquinhas; os Membros dao o nome do Apoiador), use case `ConsultarApoiadores`, rota `GET /api/grupos/{id}/apoiadores`. Nada persistido (ADR 0006).
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `tests/`, `README.md`, `GLOSSARY.md` e este registro.
- Testes e resultados: 174 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: ef7111f (implementacao) e b24dd31 (correcoes da revisao)
- Observacoes: com esta issue, a sequencia #3 a #9 da spec (#1) fica completa.
