# Sem autenticação: Membro existe só dentro de um Grupo

Não há Usuário global nem login. O Grupo é a raiz, e o Membro é uma entidade que só existe dentro dele: a mesma pessoa em dois Grupos é dois Membros sem vínculo. O front escolhe "quem sou eu" numa lista de Membros e guarda essa escolha localmente. Decidimos assim porque senha, sessão e token não são avaliados na disciplina e inflariam o domínio e os testes. Por consequência, o Reconhecimento de ajuda é sempre por Grupo.

## Considered Options

- Usuário global com login, com Membro como vínculo Usuário↔Grupo: mais realista, mas custa autenticação sem ganho de nota.
- Usuário global sem senha: não resolve nada a mais que a opção escolhida e cria a pergunta sobre a identidade dele.
