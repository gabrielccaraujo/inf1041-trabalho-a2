# RachAÍ

App para grupos de amigos e repúblicas dividirem despesas, acertarem quem deve a quem e pedirem ajuda por vaquinhas, reconhecendo quem ajuda.

## Grupo e participantes

**Grupo**:
Conjunto de pessoas que dividem contas entre si, como uma república ou uma turma de viagem. Tudo no RachAÍ acontece dentro de um Grupo.
_Avoid_: república, turma, sala

**Membro**:
Pessoa participante de um Grupo. A mesma pessoa em dois Grupos é dois Membros distintos.
_Avoid_: usuário, participante, conta

**Chave Pix**:
Identificador opcional que um Membro informa para receber Pix. É exibida, nunca validada contra o sistema bancário.
_Avoid_: conta bancária, dados de pagamento

## Despesas e acertos

**Valor**:
Quantia em reais, exata até o centavo. Pode ser negativa apenas quando expressa um Saldo.
_Avoid_: preço, montante, quantia

**Despesa**:
Gasto já feito por um Membro (o Pagador) em nome do Grupo, que gera dívida para quem participou dele.
_Avoid_: conta, gasto, lançamento, transação

**Pagador**:
O único Membro que desembolsou o dinheiro de uma Despesa. Pode ou não fazer parte da Divisão.
_Avoid_: credor, dono da despesa

**Divisão**:
Repartição do Valor de uma Despesa em Cotas, cuja soma é sempre igual ao Valor da Despesa. Pode ser igualitária ou por valores.
_Avoid_: rateio, split, partilha

**Cota**:
Parte da Divisão que cabe a um Membro específico.
_Avoid_: parcela, parte, fatia

**Pagamento**:
Transferência declarada de um Membro para outro com o fim de acertar contas. Abate o Saldo de ambos.
_Avoid_: acerto, quitação, reembolso, transferência

**Meio**:
Forma pela qual um Pagamento ou uma Contribuição foi feito: Pix, dinheiro ou outro. É declarado pelo Membro, nunca confirmado.
_Avoid_: forma de pagamento, método

**Saldo**:
Posição líquida de um Membro no Grupo: positivo se tem a receber, negativo se deve. É sempre derivado das Despesas e dos Pagamentos, e a soma dos Saldos de um Grupo é zero.
_Avoid_: dívida, débito, crédito, conta corrente

**Transferência sugerida**:
Pagamento recomendado pelo RachAÍ (de quem deve para quem tem a receber) que, junto das demais sugestões, zera os Saldos do Grupo.
_Avoid_: dívida, cobrança

## Vaquinhas e reconhecimento

**Vaquinha**:
Pedido de ajuda ao Grupo com uma Meta, em favor de um Beneficiário. Contribuir é voluntário: quem não contribui não fica devendo nada.
_Avoid_: arrecadação, campanha, fundo, despesa

**Meta**:
Valor que uma Vaquinha pretende arrecadar. Atingi-la não encerra a Vaquinha.
_Avoid_: objetivo, alvo

**Beneficiário**:
Membro em favor de quem a Vaquinha é aberta. Não contribui na própria Vaquinha.
_Avoid_: dono, criador, destinatário

**Contribuição**:
Valor que um Membro dá para uma Vaquinha aberta. Não gera dívida e não pode ser desfeita.
_Avoid_: doação, aporte, pagamento

**Vaquinha encerrada**:
Vaquinha que não aceita mais Contribuições. Uma Vaquinha só é encerrada por decisão explícita.
_Avoid_: vaquinha finalizada, vaquinha concluída

**Apoiador**:
Membro que fez ao menos uma Contribuição. Os Apoiadores são ordenados pelo total contribuído, depois pelo número de Vaquinhas apoiadas.
_Avoid_: doador, colaborador, ajudante

**Reconhecimento de ajuda**:
Ranking dos Apoiadores de um Grupo, sempre derivado das Contribuições. Pagar Despesas ou fazer Pagamentos não conta como ajuda.
_Avoid_: pontuação, selos, gamificação

## Relações

- Um **Grupo** tem vários **Membros**; **Despesas**, **Pagamentos** e **Vaquinhas** pertencem a um Grupo e só envolvem Membros dele.
- Uma **Despesa** tem um **Pagador** e uma **Divisão**; a Divisão tem uma **Cota** por Membro participante.
- O **Saldo** vem de Despesas e Pagamentos; **Vaquinhas** não afetam o Saldo.
- Uma **Vaquinha** tem um **Beneficiário**, uma **Meta** e várias **Contribuições**; o **Reconhecimento de ajuda** vem só das Contribuições.

## Exemplo de diálogo

> **Dev:** "O João pagou a conta de luz de R$ 100 e dividiu entre os 3 da república. Isso muda o Saldo de quem?"
> **Especialista:** "O João é o Pagador da Despesa. A Divisão igualitária gera Cotas de R$ 33,34, R$ 33,33 e R$ 33,33. O Saldo do João sobe R$ 66,66 e o dos outros dois cai."
> **Dev:** "E se a Ana contribuir R$ 50 na Vaquinha da geladeira?"
> **Especialista:** "O Saldo dela não muda: Contribuição não é Despesa. Mas ela passa a aparecer como Apoiadora no Reconhecimento de ajuda."

## Ambiguidades resolvidas

- "Pagamento" no sentido de "pagar a conta do mercado" é uma **Despesa** (com Pagador). "Pagamento" no RachAÍ é sempre um acerto entre dois Membros.
- "Ajudar" pagando uma Despesa pelos outros **não** é ajuda: gera Saldo a receber. Ajuda é só **Contribuição**.
