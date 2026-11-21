# Pix é declarativo e mínimo, sem integração

Não há integração com o sistema bancário. O Pix aparece no domínio só como um valor de `Meio` (PIX | DINHEIRO | OUTRO) em Pagamento e Contribuição e como uma Chave Pix opcional no Membro (texto aparado, no máximo 77 caracteres, sem classificar o tipo de chave). O registro com `meio=PIX` é uma declaração do Membro: o sistema confia e nunca confirma. Copiar a chave ou gerar QR é responsabilidade do front.

## Consequences

Se um dia o backend gerar o BR Code (payload EMV copia-e-cola), isso entra como adapter de infra atrás de uma porta, sem tocar no domínio.
