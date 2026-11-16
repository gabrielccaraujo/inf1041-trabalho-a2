# INF1041 - Trabalho A2

Aplicacao web da disciplina de Engenharia de Software. O backend sera desenvolvido em Python/Flask; o frontend, em React. O tema, as historias de usuario e o contrato da API serao definidos pelo grupo antes da implementacao.

## Estrutura

- `backend/`: dominio, casos de uso, adaptadores e API Flask.
- `frontend/`: aplicacao React.
- `docs/ia/prompts/`: prompts usados no desenvolvimento, com vinculo aos commits.
- `requirements.txt`: dependencias Python do ambiente local.

## Ambiente Python

Abra esta pasta no VS Code. O interpretador configurado e `.venv/Scripts/python.exe`. Para recriar o ambiente em outro computador:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

A pasta `.venv` fica fora do Git. O frontend devera registrar suas dependencias no proprio diretorio `frontend/`.

## Colaboracao

Criar uma branch por tarefa e integrar alteracoes por pull request. Alteracoes apoiadas por IA devem indicar o ID do registro em `docs/ia/prompts/` e o commit correspondente. Antes de conectar frontend e backend, registrar o contrato HTTP e os formatos de dados acordados pelo grupo.
