# Quatro agregados pequenos, uma porta de repositório por raiz

As raízes são Grupo (com Membros), Despesa (com Divisão), Pagamento e Vaquinha (com Contribuições). As três últimas referenciam Grupo e Membros por id. Cada raiz tem sua porta (`GrupoRepository`, `DespesaRepository`, `PagamentoRepository`, `VaquinhaRepository`), definida no domínio como `Protocol`, e cada use case recebe só as portas de que precisa (ISP e DIP). Nos testes, as portas são substituídas por repositórios em memória. A pertinência de um Membro ao Grupo é verificada pelo use case, que consulta o Grupo antes de criar Despesa, Pagamento ou Contribuição. Um agregado Grupo único com tudo dentro foi descartado: viraria uma classe "deus" e cada operação regravaria o grupo inteiro.

## Consequences

Não há remoção de Membro nem de Grupo no MVP, para evitar referências órfãs.
