# Registro de prompts

Cada intervenção apoiada por IA ganha um ID sequencial. Os registros guardam o pedido integral do usuário, a especificação operacional adotada, fontes, resultado e os hashes exatos antes/depois. Essas especificações detalham o pedido nesta conversa; não são chamadas separadas ao modelo. Correções futuras devem receber novo ID e novo commit, preservando os registros anteriores.

| ID | Etapa | Commit de código |
| --- | --- | --- |
| [P001](P001-dominio-casos-de-uso.md) | Domínio e casos de uso | `b0e125f70d9bf4acdf57ca2fd4bb7ad569903c67` |
| [P002](P002-api-sqlite.md) | SQLite, Flask, contrato e integração | `0bdc8fab935301abf0372a5535726b7dcd1102eb` |

Copie [P000-modelo.md](P000-modelo.md) para iniciar o próximo registro. Use `git show <hash>` para revisar a alteração e `git checkout <hash>` apenas em uma árvore de trabalho limpa para inspecionar o estado daquela etapa.
