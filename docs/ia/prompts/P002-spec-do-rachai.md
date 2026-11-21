# P002 - Spec do RachAI a partir do grill (to-spec)

- Data: 2026-11-20
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skill `to-spec`)
- Commit anterior: e90c380
- Objetivo: transformar as decisoes do P001 em uma spec publicada como issue no GitHub, pronta para virar tickets.
- Arquivos e contexto fornecidos: conversa do P001, `GLOSSARY.md`, `docs/adr/0001` a `0009`, `docs/agents/issue-tracker.md`, `docs/agents/triage-labels.md` e os testes existentes como referencia (`tests/use_cases/test_task_use_case.py`, `tests/app/test_health_routes.py`).
- Criterios de aceitacao: spec no template da skill (problema, solucao, historias, decisoes de implementacao, decisoes de teste, fora de escopo), usando o vocabulario do glossario e respeitando os ADRs; publicada como issue com o label `ready-for-agent`.

## Prompt integral

```text
/mattpocock-skills:to-spec ok, agora com base nesse contexto do grill, monte uma spec
```

## Interacoes durante a intervencao

- A IA propos os pontos de teste (seams) e perguntou ao grupo. Opcoes: so use cases; use cases + API; use cases + dominio + API. Escolha do grupo: **use cases + API** (recomendacao da IA). Os use cases com repositorios falsos em memoria carregam as regras; alguns testes por historia via `create_app(":memory:")` verificam o contrato HTTP e o SQLite.
- O `gh` estava sem login; o responsavel autenticou com `gh auth login` antes da publicacao.
- O label `ready-for-agent` nao existia no repositorio e foi criado pela IA.

## Resultado

- Resumo da resposta: spec com 51 historias de usuario (H0 habilitadora, H1 a H4 e transversais), modulos de dominio, use cases, portas, infra e contrato completo da API, decisoes de teste nos dois seams escolhidos, fora de escopo e notas sobre SOLID e ordem de implementacao.
- Detalhes preenchidos pela IA alem do grill: criacao responde 201; a data atual chega aos use cases por um relogio injetavel; Contribuicoes em Vaquinhas encerradas continuam contando no ranking; encerrar Vaquinha ja encerrada gera erro 422.
- Publicacao: issue #1 (https://github.com/gabrielccaraujo/inf1041-trabalho-a2/issues/1), label `ready-for-agent`.
- Arquivos alterados: este registro (a spec vive na issue, nao no repositorio).
- Testes e resultados: nao se aplica (nenhum codigo alterado).
- Commit resultante: (preencher apos o commit)
- Observacoes: proximo passo do fluxo e `/to-tickets` sobre a issue #1.
