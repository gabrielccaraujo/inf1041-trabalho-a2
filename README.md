# RachAI - Trabalho A2 de Engenharia de Software

Backend em Python/Flask para grupos de amigos e republicas dividirem
despesas, acertarem saldos e organizarem vaquinhas. O frontend em
Next.js/React esta no repositorio
[RachAI-Frontend](https://github.com/Pedro-Consales/RachAI-Frontend).

## Funcionalidades implementadas

| Acao | Comportamento |
| --- | --- |
| Criar Grupo e adicionar Membros | Nome de Membro unico no Grupo e Chave Pix opcional |
| Lancar Despesa | Pagador, participantes, data e divisao igualitaria ou por valores |
| Consultar Saldos | Saldos derivados das Despesas e Pagamentos, com transferencias sugeridas |
| Registrar Pagamento | Acerto declarado entre dois Membros, por Pix, dinheiro ou outro meio |
| Gerenciar Vaquinha | Criar, contribuir, acompanhar total e encerrar |
| Consultar Apoiadores | Ranking derivado somente das Contribuicoes |

Os valores da API sao centavos inteiros. Uma despesa de R$ 100,00 dividida
entre tres Membros gera cotas de 3334, 3333 e 3333 centavos. A soma dos
Saldos e zero; Contribuicoes em Vaquinhas nao alteram os Saldos.

Nao ha cadastro global nem login: cada Membro pertence a um Grupo, e o
frontend guarda localmente a escolha de "quem sou eu" (ADR 0001).
Pix e declarativo: o sistema exibe a chave e registra o meio informado,
sem executar ou confirmar transferencias bancarias (ADR 0007).

## Arquitetura

As dependencias apontam para dentro:
`app -> use_cases -> domain`. A infraestrutura implementa as portas
definidas no dominio, e `app/main.py` faz a composicao das dependencias.

```text
app/
  main.py                  # create_app(): composicao e inicializacao
  routes/                  # Blueprints, JSON e traducao de erros HTTP
domain/
  grupo.py                 # Grupo, Membro e porta GrupoRepository
  despesa.py               # Despesa, Divisao, Cota e porta de repositorio
  pagamento.py             # Pagamento e porta de repositorio
  vaquinha.py               # Vaquinha, Contribuicao e porta de repositorio
  saldos.py                # CalculadoraDeSaldos, servico puro
  reconhecimento.py        # ReconhecimentoDeAjuda, servico puro
  valor.py                 # Valor em centavos inteiros
  meio.py                  # Pix, dinheiro ou outro
  erros.py                 # Excecoes de dominio
use_cases/                 # Uma classe por acao; repositorios e relogio injetados
infra/
  db/database.py           # Conexao, transacoes e schema SQLite
  repositories/            # Adaptadores SQLite das portas do dominio
tests/
  use_cases/               # Regras isoladas com repositorios em memoria
  app/                     # Contrato HTTP e integracao com SQLite
  infra/                   # Acesso concorrente ao banco
docs/
  adr/                     # Decisoes de arquitetura
  ia/prompts/              # Prompts, contexto, resultados e referencias
GLOSSARY.md                # Vocabulario do dominio
requirements.txt
```

O dominio e os casos de uso nao importam Flask nem SQLite. A divisao
usa estrategias por meio de `PedidoDeDivisao`; os repositorios e o
relogio sao injetados, permitindo testar as regras sem servidor ou banco.

### Concorrencia em Vaquinhas

Contribuir e encerrar sao operacoes atomicas do repositorio. Cada uma
reserva a escrita com `BEGIN IMMEDIATE`, carrega o estado atual,
revalida a operacao usando o dominio e grava na mesma transacao.

Cada Contribuicao e inserida individualmente. Nao se compara a posicao
de uma lista antiga com a quantidade de registros do banco. Uma
contribuicao que chegar depois do encerramento recebe erro 422; uma
requisicao antiga nao pode reabrir a Vaquinha. A mudanca preserva o
schema SQLite e os formatos HTTP existentes. Veja o ADR 0010.

## Preparar o ambiente e executar

Requer Python 3.11 ou mais novo. No Windows, dentro desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.main
```

No macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.main
```

A API inicia em `http://127.0.0.1:5000`. Consulte
`GET /api/health` para verificar API e banco. O SQLite e criado
automaticamente em `app.db` na raiz do backend e fica fora do Git.
Reiniciar a aplicacao preserva os dados. Para testes, a fabrica aceita
outro caminho: `create_app(":memory:")`.

O comando acima inicia o servidor de desenvolvimento do Flask com debug.
Para uma publicacao, configure um servidor WSGI e armazenamento persistente.

## Contrato HTTP

Prefixo: `/api`. Envie `Content-Type: application/json` nos corpos JSON.

| Metodo | Rota | Acao |
| --- | --- | --- |
| GET | `/health` | Saude da API e do banco |
| POST | `/grupos` | Criar Grupo |
| GET | `/grupos/<id>` | Consultar Grupo e Membros |
| POST | `/grupos/<id>/membros` | Adicionar Membro |
| POST / GET | `/grupos/<id>/despesas` | Lancar ou listar Despesas |
| POST / GET | `/grupos/<id>/pagamentos` | Registrar ou listar Pagamentos |
| GET | `/grupos/<id>/saldos` | Consultar Saldos e transferencias sugeridas |
| POST / GET | `/grupos/<id>/vaquinhas` | Criar ou listar Vaquinhas |
| POST | `/grupos/<id>/vaquinhas/<vid>/contribuicoes` | Contribuir |
| POST | `/grupos/<id>/vaquinhas/<vid>/encerrar` | Encerrar Vaquinha |
| GET | `/grupos/<id>/apoiadores` | Consultar ranking |

Exemplo de despesa igualitaria, usando IDs de Membros ja cadastrados:

```json
{
  "descricao": "Conta de luz",
  "valor_centavos": 10000,
  "pagador_id": 1,
  "data": "2026-11-25",
  "divisao": {
    "modo": "igualitaria",
    "membros": [1, 2, 3]
  }
}
```

O outro modo e `por_valores`, com
`"cotas": [{"membro_id": 1, "valor_centavos": 10000}]`.
As cotas precisam somar o valor da Despesa. O pagador e os participantes
devem pertencer ao Grupo. A data da Despesa e opcional; quando omitida,
o backend usa a data atual.

Erros seguem `{"erro": "mensagem"}`:

- **400:** JSON malformado, campo ausente, tipo incorreto ou modo desconhecido.
  O campo `divisao.modo` deve ser texto: `igualitaria` ou `por_valores`.
- **404:** Grupo ou recurso inexistente.
- **422:** regra de dominio violada, como valor nao positivo ou Vaquinha encerrada.

O contrato de referencia esta na issue #1 do repositorio e no ADR 0008.

## Integracao com o frontend

O Next.js encaminha `/api/*` para
`http://127.0.0.1:5000/api/*`, configuravel por `FLASK_URL` no frontend.
O navegador conversa com o Next, que faz o proxy para o Flask.

Execute o backend como descrito acima e o frontend em outro terminal.
Para instalar, iniciar e testar o frontend, siga o
[README do frontend](https://github.com/Pedro-Consales/RachAI-Frontend/blob/main/rachai-frontend/README.md).
A interface abre em `http://localhost:3000`, e a pagina `/health`
verifica a comunicacao com o backend.

## Testes

No Windows:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

No macOS/Linux:

```bash
.venv/bin/python -m pytest -q
```

Os testes de casos de uso usam repositorios falsos, sem Flask nem SQLite.
Os testes HTTP verificam JSON, status e persistencia, incluindo regressao
para contribuintes simultaneos, conexoes SQLite distintas e disputa entre
contribuir e encerrar. Os testes de API usam bancos em memoria ou
temporarios e nao alteram `app.db`.

## Colaboracao e uso de IA

Crie uma branch por tarefa e integre por pull request. Cada intervencao
apoiada por IA tem um registro em `docs/ia/prompts/`; preserve os registros
anteriores e acrescente um novo ID para correcoes.

Esta revisao esta documentada em
[docs/ia/prompts/P011-correcoes-concorrencia-validacao-readme.md](docs/ia/prompts/P011-correcoes-concorrencia-validacao-readme.md).
Como a entrada foi um ZIP sem historico Git, o registro identifica o
arquivo-base e nao inventa hashes de commits. Ao integrar a revisao,
acrescente o hash real do novo commit em um registro complementar.
