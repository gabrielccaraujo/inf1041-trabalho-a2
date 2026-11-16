# P002 — Persistência SQLite e API Flask

- Data: 2026-11-16
- Responsável: Gabriel com apoio do Codex nesta conversa
- Ferramenta/modelo: Codex, modelo da conversa
- Commit anterior: `b0e125f70d9bf4acdf57ca2fd4bb7ad569903c67`
- Commit de código resultante: `0bdc8fab935301abf0372a5535726b7dcd1102eb`
- Objetivo: expor os casos de uso a um frontend React e persistir os dados
- Fontes consultadas: PDFs da A1 e A2; código e porta de repositório do P001

## Pedido integral do usuário

```text
Pode fazer los entao, seguindo os padroes de uso de IA. Tente implementar a estrutura "Sugestão de Estrutura de Pastas - Clean Architecture em Flask" Como eu abro o projeto no vs code? "CLone repository"?
```

## Especificação operacional da etapa

```text
Continue a partir do commit do P001. Implemente infra/db/ e
infra/repositories/ com SQLite e transações para grupo+membro e
despesa+partes. Faça app/main.py como ponto de composição e app/routes/
como adaptador Flask. Exponha cadastro, login, usuário atual, criar/listar/
entrar em grupo, obter membros, criar/listar despesas e consultar saldos.
Use JSON, token Bearer e erros HTTP estruturados. Habilite CORS local para
o React em Vite. Documente os endpoints, tipos monetários, regras e como
abrir/rodar o projeto no VS Code. Mantenha os repositórios backend e frontend
independentes e adjacentes. Escreva teste de integração com banco temporário
que percorra o fluxo completo e cenários de erro. Não coloque senha, token
em claro ou banco local no Git. Vincule o resultado a este prompt.
```

Esta especificação detalha o pedido recebido e registra as decisões usadas na intervenção; não representa uma chamada separada ao modelo.

## Resultado

- Arquivos: `app/`, `infra/`, `tests/test_api.py`, `README.md`, `docs/arquitetura.md`, `.gitignore`; removido marcador antigo `backend/README.md`.
- Contrato HTTP: `/api/v1`, JSON, Bearer, CORS local; dados em `instance/rachai.sqlite3`.
- Verificação: `python -m pytest -q` → 12 testes passaram; `git diff --check` sem erros após revisão.
- Para reproduzir o estado desta etapa: `git checkout 0bdc8fab935301abf0372a5535726b7dcd1102eb`.
