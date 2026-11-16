# Arquitetura do backend RachAÍ

## Origem e recorte

O Lean Inception da A1 define o MVP F01–F10. Esta implementação da A2 cobre F01–F05: cadastro/login, grupos/convites, registro de despesa, divisão igual e saldos. O PDF da A2 pede Python, Flask, Pytest, persistência, Clean Architecture, pelo menos duas entidades e quatro histórias implementadas. F06–F10 ficam para incrementos futuros.

## Camadas e dependências

```text
HTTP/Flask (app) → casos de uso (use_cases) → domínio (domain)
             ↘ adaptador SQLite (infra) → porta Repository (use_cases)
```

`domain` contém entidades imutáveis e funções de dinheiro/divisão sem Flask ou SQLite. `RachaiService` coordena regras e usa apenas a porta `Repository`. `SqliteRepository` implementa a porta e `app.main` liga as peças. Os testes de caso de uso injetam um repositório falso, sem banco nem servidor.

Entidades principais: `User`, `Group`, `Expense` e `Split`. No banco, `group_members` representa associação e `sessions` armazena o hash dos tokens. A criação de grupo com o criador como membro e a criação de despesa com suas partes ocorrem em transações SQLite.

## Regras

- E-mail é único, normalizado em minúsculas. Senhas têm pelo menos oito caracteres e um número, e são armazenadas com PBKDF2-SHA256 e salt aleatório.
- Login emite token aleatório; só o hash SHA-256 fica no SQLite. A sessão expira após sete dias.
- Um membro cria um grupo e compartilha o código de convite. Outro usuário autenticado entra pelo código. A entrada repetida é idempotente.
- Apenas membros consultam grupo, despesas e saldos ou criam despesas nele.
- Valor é string decimal positiva com até duas casas. O domínio converte para centavos inteiros.
- Pagador e participantes pertencem ao grupo; participantes são distintos e a lista não pode estar vazia.
- A divisão é igual. O resto de centavos é distribuído pela ordem crescente de ID, garantindo que a soma das partes seja o valor integral.
- O saldo por membro é soma das despesas que pagou menos soma das partes atribuídas a ele. A soma dos saldos do grupo é zero.

## Persistência e operação

SQLite mantém os dados em `instance/rachai.sqlite3` por padrão, configurável por `RACHAI_DATABASE`. O esquema é criado na inicialização. O banco é local para desenvolvimento; cada colega mantém o próprio arquivo. Para compartilhar dados entre máquinas será necessário hospedar a API e o banco. A aplicação não possui migrações versionadas ainda: alterações futuras de esquema exigirão uma migração explícita. Em produção, configure HTTPS e um servidor WSGI.

## Testes

`tests/test_domain.py` verifica centavos, divisão e entradas inválidas. `tests/test_use_cases.py` isola registro e criação de despesa com fake repository. `tests/test_api.py` percorre cadastro, login, grupo, convite, despesa, consulta e saldo com SQLite temporário, além de autenticação e erros.
