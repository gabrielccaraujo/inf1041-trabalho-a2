# P003 - Quebra da spec em tickets (to-tickets)

- Data: 2026-11-20
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skill `to-tickets`)
- Commit anterior: 5862641
- Objetivo: quebrar a spec (issue #1) em tickets de fatia vertical, cada um com seus bloqueios, publicados como sub-issues no GitHub.
- Arquivos e contexto fornecidos: issue #1, `GLOSSARY.md`, `docs/adr/0001` a `0009`, `docs/agents/issue-tracker.md` e o codigo atual (placeholder `Task`, `create_app`, testes existentes).
- Criterios de aceitacao: cada ticket atravessa todas as camadas (dominio, use case, SQLite, rota, testes) e e verificavel sozinho; dependencias minimas; sub-issues da #1 com dependencias nativas e label `ready-for-agent`; a #1 nao e alterada.

## Prompt integral

```text
/mattpocock-skills:to-tickets
```

## Interacoes durante a intervencao

- A IA propos 7 tickets e o grafo de dependencias abaixo, com duas escolhas explicitas: (1) o VO `Valor` nasce no ticket de Despesa, nao num ticket isolado de preparacao, porque sozinho nao seria testavel pelo seam dos use cases; (2) Saldos nao depende da Divisao por valores, para permitir trabalho em paralelo.
- Resposta do grupo: "granularidade esta boa, dependencias corretas e pode publicar os subissues sim".

```text
#3 -> #4 -+-> #5
          +-> #6 -> #7
          +-> #8 -> #9
```

## Resultado

- Tickets publicados (sub-issues da #1, label `ready-for-agent`, dependencias nativas do GitHub):
  - #3 Grupo e Membros de ponta a ponta (H0): inclui a traducao de erros 400/404/422 e a remocao do placeholder `Task`. Sem bloqueio.
  - #4 Lancar Despesa com Divisao igualitaria (H1): `Valor`, Divisao, relogio injetavel. Bloqueado por #3.
  - #5 Divisao por valores (H1). Bloqueado por #4.
  - #6 Consultar Saldos e Transferencias sugeridas (H2). Bloqueado por #4.
  - #7 Registrar Pagamento (H2). Bloqueado por #6.
  - #8 Vaquinha: criar, contribuir, encerrar e listar (H3). Bloqueado por #4.
  - #9 Reconhecimento de ajuda: ranking de Apoiadores (H4). Bloqueado por #8.
- Arquivos alterados: este registro (os tickets vivem no GitHub).
- Testes e resultados: nao se aplica (nenhum codigo alterado).
- Commit resultante: (preencher apos o commit)
- Observacoes: o label `ready-for-agent` foi criado no P002. Proximo passo: `/implement` na #3.
