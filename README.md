# INF1041 - Trabalho A2 (backend)

Este repositorio contem o backend em Python/Flask do Trabalho A2 de Engenharia de Software. O frontend React esta em um repositorio separado: [RachAI-Frontend](https://github.com/Pedro-Consales/RachAI-Frontend).

O tema, as historias de usuario e o contrato da API serao definidos pelo grupo antes da implementacao. As regras de negocio devem ficar isoladas do Flask e da persistencia, conforme a Clean Architecture.

## Estrutura

Arquitetura em camadas: as dependencias apontam para dentro (`app` -> `use_cases` -> `domain`; `infra` implementa as portas do dominio).

```
app/
  routes/grupo_routes.py             # rotas HTTP de Grupo e Membros (Flask Blueprint)
  routes/despesa_routes.py           # rotas HTTP de Despesas
  routes/saldo_routes.py             # GET de Saldos e Transferencias sugeridas
  routes/health_routes.py            # GET /api/health
  routes/erros.py                    # traducao de erros para {"erro": ...} (400/404/422)
  routes/requisicao.py               # leitura e validacao de formato do corpo JSON
  main.py                            # create_app(): monta infra -> casos de uso -> rotas
domain/
  grupo.py                           # raiz Grupo, entidade Membro e porta GrupoRepository
  despesa.py                         # raiz Despesa, VOs Divisao e Cota, porta DespesaRepository
  saldos.py                          # servico CalculadoraDeSaldos (ADR 0004)
  valor.py                           # VO Valor em centavos inteiros (ADR 0002)
  erros.py                           # excecoes de dominio (regra violada, nao encontrado)
use_cases/                           # um caso de uso por acao (CriarGrupo, AdicionarMembro, ...)
infra/
  repositories/grupo_repository_sqlite.py  # implementacao SQLite do GrupoRepository
  repositories/despesa_repository_sqlite.py  # implementacao SQLite do DespesaRepository
  db/database.py                     # conexao SQLite (segura entre threads) e schema
tests/                               # testes por seam (use_cases com repositorio em memoria, app via API)
docs/ia/prompts/                     # prompts usados no desenvolvimento, vinculados aos commits
requirements.txt
```

## Executar

```bash
python -m app.main      # sobe a API em http://127.0.0.1:5000
python -m pytest        # roda os testes
```

Endpoints: `GET /api/health` (200 se API e banco ok, 503 se o banco falhar), `POST /api/grupos` (`{"nome": "..."}`), `GET /api/grupos/<id>` (Grupo com Membros), `POST /api/grupos/<id>/membros` (`{"nome": "...", "chave_pix": "..."}`, Chave Pix opcional), `POST /api/grupos/<id>/despesas` (`{"descricao", "valor_centavos", "pagador_id", "data"?, "divisao": {"modo": "igualitaria", "membros": [...]} | {"modo": "por_valores", "cotas": [{"membro_id", "valor_centavos"}]}}`), `GET /api/grupos/<id>/despesas`, `GET /api/grupos/<id>/saldos` (`{"saldos": [{"membro_id", "saldo_centavos"}], "transferencias": [{"de_membro_id", "para_membro_id", "valor_centavos"}]}`). Erros vem como `{"erro": "mensagem"}`: 400 corpo malformado, 404 recurso inexistente, 422 regra de dominio violada. O contrato completo esta na issue #1 e no ADR 0008.

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
