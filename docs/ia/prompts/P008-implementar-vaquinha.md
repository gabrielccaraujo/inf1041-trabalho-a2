# P008 - Implementacao da #8: Vaquinha (H3)

- Data: 2026-11-21
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `implement`, `tdd` e `code-review`)
- Commit anterior: 044ab70
- Objetivo: implementar a issue #8 com TDD, em branch `feat/` propria e PR com "Closes #8". Quinta issue da sequencia iniciada no P004.
- Arquivos e contexto fornecidos: issues #1 e #8, `GLOSSARY.md`, `docs/adr/0005`, `0007`, `0008` e `0009` e o codigo da H0 a H2.
- Criterios de aceitacao: os da #8, incluindo o de Saldos (a #6 ja tinha entrado); teste falhando antes de cada implementacao; use cases com repositorios falsos em memoria; PEP-8; suite inteira passando.

## Prompt integral

O mesmo prompt do P004. Depois do merge do PR #13, o grupo respondeu:

```text
pronto
```

## Interacoes durante a intervencao

- Ciclos red -> green: `CriarVaquinha` (Meta positiva, titulo, Beneficiario do Grupo, Grupo inexistente); `Contribuir` (total arrecadado, acima da Meta sem encerrar, Beneficiario, Membro de fora, Valor nao positivo, Vaquinha inexistente ou de outro Grupo); `EncerrarVaquinha` (encerrada nao aceita Contribuicao, encerrar duas vezes); `ListarVaquinhas` e Saldos; contrato da API.
- A verificacao de pertinencia ao Grupo, antes so em `LancarDespesa`, foi extraida para `use_cases/comum.py` (`garantir_membros_do_grupo`) e reaproveitada.
- Revisao em dois eixos (`code-review`). Os dois revisores apontaram o mesmo defeito: o teste "Contribuicoes nao alteram os Saldos" nao tinha Despesa, entao nao podia falhar. Corrigido: lanca uma Despesa, compara os Saldos antes e depois das Contribuicoes (na API, com Vaquinhas e Despesas no mesmo banco). Tambem aplicado: `descricao` obrigatoria, como no contrato da #1; o POST de contribuicao responde 201 com a Contribuicao criada ("Criacao responde 201 com o recurso criado"); Contribuicoes guardadas em tupla, append-only por construcao; nomes de teste com o resultado esperado.

## Resultado

- Resumo da resposta: `Vaquinha` com `Contribuicao` (VO) e `Meio` (enumeracao), porta `VaquinhaRepository` com implementacao SQLite (tabelas `vaquinhas` e `contribuicoes`), use cases `CriarVaquinha`, `Contribuir` (relogio injetavel), `EncerrarVaquinha` e `ListarVaquinhas`, rotas sob `/api/grupos/{id}/vaquinhas`. Total arrecadado derivado, nao persistido.
- Arquivos alterados: `app/`, `domain/`, `use_cases/`, `infra/`, `tests/`, `README.md` e este registro.
- Testes e resultados: 144 testes verdes com `python -m pytest`; `pycodestyle` sem apontamentos.
- Commit resultante: 450c1de (implementacao) e 055b102 (correcoes da revisao)
- Observacoes: encerrar responde 200 com a Vaquinha; a spec nao fixa o status.
