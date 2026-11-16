# INF1041 - Trabalho A2 (backend)

Este repositorio contem o backend em Python/Flask do Trabalho A2 de Engenharia de Software. O frontend React esta em um repositorio separado: [RachAI-Frontend](https://github.com/Pedro-Consales/RachAI-Frontend).

O tema, as historias de usuario e o contrato da API serao definidos pelo grupo antes da implementacao. As regras de negocio devem ficar isoladas do Flask e da persistencia, conforme a Clean Architecture.

## Estrutura

- `backend/`: dominio, casos de uso, adaptadores e API Flask.
- `docs/ia/prompts/`: prompts usados no desenvolvimento, vinculados aos commits.
- `requirements.txt`: dependencias Python do ambiente local.

## Ambiente Python

Abra esta pasta no VS Code. O interpretador configurado e `.venv/Scripts/python.exe`. Para recriar o ambiente em outro computador:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

A pasta `.venv` fica fora do Git.

## Integracao com o frontend

Antes de conectar os repositorios, o grupo deve registrar os endpoints HTTP, os formatos de requisicao e resposta e o tratamento de erros. O frontend consome a API deste backend; cada repositorio mantem suas proprias dependencias e instrucoes de execucao.

## Colaboracao

Criar uma branch por tarefa e integrar alteracoes por pull request. Alteracoes apoiadas por IA devem indicar o ID do registro em `docs/ia/prompts/` e o commit correspondente.
