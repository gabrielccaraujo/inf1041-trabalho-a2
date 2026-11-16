# RachAÍ — backend (INF1041 A2)

API Flask para dividir despesas em grupos. O frontend React está no repositório [RachAI-Frontend](https://github.com/Pedro-Consales/RachAI-Frontend). Os dois repositórios podem ficar em pastas adjacentes; o React chama esta API por HTTP.

## Escopo implementado

| História da A1 | Entrega nesta API |
| --- | --- |
| F01 Cadastro e login | Cadastro com nome, e-mail e senha; login com token Bearer |
| F02 Grupos e convites | Criar/listar grupo, obter membros e entrar pelo código de convite |
| F03 Registrar despesa | Registrar pagador, valor, categoria, data e participantes |
| F04 Dividir despesa | Divisão igual em centavos, sem perder centavos |
| F05 Saldos | Saldo por membro: total pago menos sua parte nas despesas |

O recorte da A2 cobre a primeira onda funcional do Lean Inception. CPF e tela de convite por link não fazem parte desta API inicial. Pix, vaquinha e ranking continuam no backlog da A1. Consulte [arquitetura](docs/arquitetura.md) para regras e decisões.

## Abrir no VS Code

Neste computador, use **Arquivo → Abrir Pasta** e escolha `C:\Users\Gabriel\Downloads\ArqsPuc\INF1041 - ENGENHARIA DE SOFTWARE\Trabalho A2`. Não precisa clonar novamente. Em outro computador, use **Clone Repository** com `https://github.com/gabrielccaraujo/inf1041-trabalho-a2`; como o repositório é privado, entre na conta GitHub com acesso.

Crie o ambiente virtual e instale as dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Selecione o interpretador `.venv\Scripts\python.exe` no VS Code. A configuração em `.vscode/settings.json` já aponta para ele. Para executar:

```powershell
.\.venv\Scripts\python.exe -m app.main
```

A API responde em `http://127.0.0.1:5000`; `GET /health` verifica se iniciou. O banco SQLite nasce automaticamente em `instance/rachai.sqlite3` e não entra no Git. Para testes:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Contrato para o React

Prefixo: `http://127.0.0.1:5000/api/v1`. Envie `Content-Type: application/json`. Após login, envie `Authorization: Bearer <token>` nas rotas protegidas. O CORS local permite `http://localhost:5173` e `http://127.0.0.1:5173`; ajuste `RACHAI_CORS_ORIGINS` para outras origens, separadas por vírgula.

| Método | Rota | Corpo principal | Resposta |
| --- | --- | --- | --- |
| POST | `/auth/register` | `name`, `email`, `password` | usuário, 201 |
| POST | `/auth/login` | `email`, `password` | `token`, `token_type`, `user` |
| GET | `/auth/me` | — | usuário |
| POST | `/groups` | `name`, `category` opcional | grupo, 201 |
| GET | `/groups` | — | `groups` |
| POST | `/groups/join` | `invite_code` | grupo |
| GET | `/groups/<id>` | — | grupo com `members` |
| POST | `/groups/<id>/expenses` | veja exemplo | despesa com `splits`, 201 |
| GET | `/groups/<id>/expenses` | — | `expenses` |
| GET | `/groups/<id>/balances` | — | `balances` |

Exemplo de despesa:

```json
{
  "description": "Mercado",
  "amount": "10.01",
  "paid_by": "ID_DO_USUARIO",
  "participant_ids": ["ID_DO_USUARIO", "ID_DE_OUTRO_MEMBRO"],
  "category": "Mercado",
  "occurred_on": "2026-11-16"
}
```

Valores monetários são **strings decimais** com ponto e até duas casas, por exemplo `"10.01"`; respostas seguem o mesmo formato. `occurred_on` é opcional e usa a data atual quando ausente. O código de convite vem no objeto do grupo. O pagador e todos os participantes precisam ser membros do grupo. A divisão é igual; eventual centavo restante vai aos participantes em ordem crescente de ID. Saldo positivo significa que o membro pagou mais do que sua parte; saldo negativo significa que deve ao grupo.

Erros de negócio retornam `{"error":{"code":"...","message":"..."}}` com HTTP 400, 401, 403, 404 ou 409. Token de sessão expira em sete dias. A API não processa transferências Pix.

## Estrutura

```text
app/                 Flask, rotas e composição
domain/              entidades e regras puras
use_cases/           serviços de aplicação e porta de repositório
infra/db/            esquema SQLite
infra/repositories/  adaptador SQLite
tests/               regras, casos de uso isolados e fluxo HTTP
docs/ia/prompts/     prompts desenvolvidos e commits associados
```

A documentação da arquitetura está em [docs/arquitetura.md](docs/arquitetura.md). Cada intervenção apoiada por IA tem um registro imutável em [docs/ia/prompts](docs/ia/prompts/README.md), ligado aos commits de código. Novas correções devem ganhar novo ID.

## Colaboração

Abra uma branch por tarefa e integre por pull request. Para desenvolver frontend e backend juntos, mantenha os dois diretórios adjacentes, inicie Flask na porta 5000 e Vite na 5173. Os projetos têm dependências e histórico Git separados.
