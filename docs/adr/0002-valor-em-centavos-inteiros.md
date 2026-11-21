# Dinheiro como VO Valor em centavos inteiros

Toda quantia é um value object `Valor` que guarda centavos como `int`. Ele é persistido como `INTEGER` e trafega na API como inteiro em campos `*_centavos`. O único lugar onde mora a regra de dividir um Valor em N partes sem perder centavo é esse VO. `float` está descartado por imprecisão, e `Decimal` solto espalharia a regra de arredondamento. `Valor` aceita sinal para representar Saldo; Despesa, Pagamento, Meta e Contribuição exigem valor positivo. Só existe BRL.
