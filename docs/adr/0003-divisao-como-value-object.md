# Divisão é value object da Despesa, criada por fábricas

A Despesa tem um único Pagador e uma Divisão imutável formada por Cotas (`membro_id`, `Valor`). A Divisão garante na construção que a soma das Cotas é igual ao Valor da Despesa. Os modos de divisão são fábricas que produzem a mesma Divisão (`igualitaria`, `por_valores`), e não subclasses de Despesa: um modo novo é uma fábrica nova (OCP). Na divisão igualitária, a sobra de centavos vai para os primeiros Membros da lista, de forma determinística.

## Considered Options

- Divisão ou Cota como entidade com estado "quitada": descartada porque o acerto acontece por Pagamento sobre o saldo líquido, não cota a cota.
- Só divisão igualitária: descartada porque o produto precisa de divisão não igualitária.
- Vários Pagadores por Despesa e divisão percentual: fora do MVP.
