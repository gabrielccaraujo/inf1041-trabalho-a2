# INF1041 - Trabalho A2 (backend)

Este repositorio contem o backend em Python/Flask do Trabalho A2 de Engenharia de Software. O frontend React esta em um repositorio separado: [RachAI-Frontend](https://github.com/Pedro-Consales/RachAI-Frontend).

O tema, as historias de usuario e o contrato da API serao definidos pelo grupo antes da implementacao. As regras de negocio devem ficar isoladas do Flask e da persistencia, conforme a Clean Architecture.

## Estrutura

Arquitetura em camadas: as dependencias apontam para dentro (`app` -> `use_cases` -> `domain`; `infra` implementa as portas do dominio).

```
app/
  routes/task_routes.py              # rotas HTTP de tarefas (Flask Blueprint)
  routes/health_routes.py            # GET /api/health
  main.py                            # create_app(): monta infra -> casos de uso -> rotas
domain/task.py                       # entidade Task, regras de negocio e porta TaskRepository
use_cases/task_use_case.py           # casos de uso (criar, listar, buscar, atualizar, remover)
infra/
  repositories/task_repository_sqlite.py  # implementacao SQLite do TaskRepository
  db/database.py                     # conexao SQLite (segura entre threads) e schema
tests/                               # testes por camada (domain, use_cases, infra, app)
docs/ia/prompts/                     # prompts usados no desenvolvimento, vinculados aos commits
requirements.txt
```

## Executar

```bash
python -m app.main      # sobe a API em http://127.0.0.1:5000
python -m pytest        # roda os testes
```

Endpoints: `GET /api/health` (200 se API e banco ok, 503 se o banco falhar), `GET /tasks`, `POST /tasks` (`{"title": "..."}`), `GET /tasks/<id>`, `PATCH /tasks/<id>` (`{"title": "...", "done": true}`), `DELETE /tasks/<id>`.

## Ambiente Python

Abra esta pasta no VS Code. O interpretador configurado e `.venv/Scripts/python.exe` (Windows). Para recriar o ambiente em outro computador:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No macOS/Linux: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

A pasta `.venv` fica fora do Git.

## Integracao com o frontend

Antes de conectar os repositorios, o grupo deve registrar os endpoints HTTP, os formatos de requisicao e resposta e o tratamento de erros. O frontend consome a API deste backend; cada repositorio mantem suas proprias dependencias e instrucoes de execucao.

O Next.js encaminha `/api/*` para `http://127.0.0.1:5000/api/*` (configuravel por `FLASK_URL`), por isso as rotas consumidas pelo frontend devem ficar sob `/api`. No macOS, use `127.0.0.1` e nao `localhost`: a porta 5000 tambem e usada pelo AirPlay Receiver.

## Colaboracao

Criar uma branch por tarefa e integrar alteracoes por pull request. Alteracoes apoiadas por IA devem indicar o ID do registro em `docs/ia/prompts/` e o commit correspondente.
