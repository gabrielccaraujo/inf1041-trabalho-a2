# Operacoes atomicas de contribuicao e encerramento

## Contexto

O antigo salvar sincronizava uma lista de Contribuicoes usando a quantidade
ja persistida. Duas requisicoes podiam carregar o mesmo estado, acrescentar
uma entrada na mesma posicao e retornar sucesso, embora uma entrada fosse
ignorada. Uma copia antiga tambem podia sobrescrever o status encerrada.

## Decisao

A porta VaquinhaRepository expoe adicionar_contribuicao e encerrar.
Ambas as operacoes carregam e validam o estado atual na mesma transacao
que grava o resultado. As regras continuam em Vaquinha.contribuir e
Vaquinha.encerrar, sem dependencias de Flask ou SQLite no dominio.

O SQLite usa BEGIN IMMEDIATE antes da leitura nessas duas operacoes.
Assim a reserva de escrita tambem serializa conexoes diferentes sobre
o mesmo arquivo. O lock de Database protege o uso da conexao entre threads.
Uma Contribuicao e inserida como um novo registro; nao se infere o que
falta com base na lista recebida de uma requisicao anterior.

Os casos de uso mantem a validacao de Grupo e Membros. A validacao inicial
de dominio nao substitui a revalidacao no momento da escrita. O fake de
Vaquinha usa copias desacopladas, como o SQLite, para nao alterar dados
persistidos apenas por modificar um objeto retornado por buscar.

## Consequencias

- Duas Contribuicoes validas simultaneas sao ambas gravadas.
- Se o encerramento vencer, a Contribuicao em voo recebe erro 422.
- Se a Contribuicao vencer, ela integra o estado devolvido ao encerrar.
- Dois encerramentos simultaneos produzem um sucesso e uma regra violada.
- A contribuicao nao escreve o status da Vaquinha e nao pode reabri-la.
- Nao ha alteracao de schema nem do contrato HTTP.
- SQLite continua com um escritor por vez e o timeout padrao do driver.
