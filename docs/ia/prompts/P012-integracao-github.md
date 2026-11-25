# P012 - Integracao das correcoes do P011 no GitHub

- Data: 2026-11-25
- Ferramenta: Codex.
- Pedido do usuario: "Cade", acompanhado da tela de pull requests; em
  seguida, o usuario confirmou a autorizacao de acesso ao repositorio.
- Objetivo: publicar as correcoes ja validadas em uma branch e abrir PR.
- Repositorio: gabrielccaraujo/inf1041-trabalho-a2.
- Branch: fix/contribuicoes-atomicas-validacao.
- Base main: 95572d74c2f9e08508a7832b8edf165f939b73e1.
- Commit de implementacao do P011:
  250638d71e71bdc540e55a8d2c5ab4688cc4b98f.

## Integracao

O patch foi aplicado sobre uma copia nova da main, sem conflitos.
A suite foi executada nessa branch: 184 testes passaram.
pycodestyle 2.15.0 nao apontou problemas; git diff --check passou.
Nao houve alteracao do frontend nem migracao do banco.

Este registro complementa o P011, preservando o relato original da entrega
por ZIP e vinculando-o ao commit real de implementacao. O PR entrega essa
implementacao e este registro complementar para revisao, sem mesclar a main.
