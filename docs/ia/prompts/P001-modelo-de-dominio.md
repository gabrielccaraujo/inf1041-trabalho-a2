# P001 - Modelo de dominio do RachAI (grill-with-docs)

- Data: 2026-11-20
- Responsavel: gugavalente05
- Ferramenta/modelo: Claude Code, Claude Opus 5.5 (skills `grilling` e `domain-modeling`)
- Commit anterior: 238732d
- Objetivo: definir o modelo de dominio do RachAI antes de escrever codigo, com a IA questionando o grupo uma decisao por vez e recomendando uma resposta.
- Arquivos e contexto fornecidos: estrutura do repositorio (placeholder `Task`), `README.md`, `docs/agents/domain.md`, `docs/ia/prompts/README.md` e o frontend irmao `../RachAI-Frontend` (Next.js com proxy `/api`).
- Criterios de aceitacao: entidades e value objects definidos; regra de saldo fechada para divisao nao igualitaria; 4 historias de usuario avaliaveis; `GLOSSARY.md` e ADRs escritos; nenhum codigo alterado.

## Prompt integral

```text
/grill-with-docs

Me questione sobre o modelo de domínio do RachAÍ antes de escrevermos qualquer código.
Ao final, atualize o GLOSSARY.md e registre as decisões como ADRs.

PRODUTO
RachAÍ, app de despesas e vaquinhas para grupos de amigos e repúblicas, que têm
dificuldade de dividir contas e pedir ajuda. Mostra quem deve a quem e cria vaquinhas.
Diferencial sobre planilhas e Splitwise: aceita Pix e reconhece quem ajuda.

STACK
- Back: Flask, API REST pura, sem template. SQLite via repositório.
- Front: React, em porta separada, consumindo a API por fetch.
- Testes: pytest, nos use cases, isolados da infraestrutura.
- Estrutura de pastas em Clean Architecture já criada
  (app/routes, domain, use_cases, infra/repositories, infra/db, tests).

RESTRIÇÕES DA DISCIPLINA (trabalho avaliado, 10 pontos)
- Mínimo 4 histórias de usuário e 2 entidades.
- Camadas separadas: entidades, use cases, interface adapters, frameworks & drivers.
- SOLID explícito no design das classes.
- Testes unitários dos use cases isolados da infra.
- PEP-8.
- Uso de IA vale bônus se justificado, então registre as decisões que tomarmos com IA como orienta o arquivo README na pasta prompts em ia.

ME GRELHE SOBRE
1. Entidades: quais são de fato entidades e quais são value objects. Candidatos óbvios
   são Grupo, Membro, Despesa, Divisão, Vaquinha, Contribuição e Pagamento. Qual o mínimo
   que sustenta o produto sem inflar o domínio.
2. O cálculo de "quem deve a quem": é entidade, serviço de domínio ou use case. Como
   fecha o saldo quando a divisão não é igualitária.
3. "Reconhecer quem ajuda": é dado derivado do histórico ou estado persistido.
4. Vaquinha e despesa: mesma abstração com um campo de tipo, ou coisas separadas.
5. Pix: até onde entra no domínio agora, dado que é um trabalho acadêmico sem integração real.
6. Fronteira Flask/React: o que a API expõe, e o que fica só no front.
7. Quais 4 histórias de usuário cobrem o produto e, ao mesmo tempo, exercitam
   as duas entidades e os use cases de forma avaliável.

Cada termo que fecharmos vai para o GLOSSARY.md com a definição acordada.
Uma pergunta por vez, com a sua recomendação. Não escreva código nesta sessão.
```

## Decisoes tomadas (pergunta da IA -> resposta do grupo)

| # | Pergunta | Decisao | ADR |
|---|----------|---------|-----|
| Q1 | Existe Usuario com login? | Nao. Grupo e raiz; Membro so existe dentro dele. | 0001 |
| Q2 | Divisao e entidade ou VO? | VO com Cotas; pagador unico; fabricas igualitaria e por valores. | 0003 |
| Q3 | Como representar dinheiro? | VO `Valor` em centavos inteiros. | 0002 |
| Q4 | Como registrar acerto? | Entidade `Pagamento` com `meio` (PIX, DINHEIRO, OUTRO). | 0007 |
| Q5 | Onde calcular quem deve a quem? | Servico de dominio puro `CalculadoraDeSaldos`; saldo derivado; soma zero; algoritmo guloso. | 0004 |
| Q6 | Vaquinha e Despesa juntas? | Separadas; Vaquinha fora do saldo; encerramento manual. | 0005 |
| Q7 | Contribuicao e entidade? | VO append-only; beneficiario nao contribui. | 0005 |
| Q8 | Reconhecimento persistido? | Derivado (`ReconhecimentoDeAjuda`), so de Contribuicoes. | 0006 |
| Q9 | Ate onde vai o Pix? | Chave opcional no Membro + `meio`; sem confirmacao; BR Code adiado. | 0007 |
| Q10 | Fronteira API/front? | Calculo todo no backend; Next.js como cliente via proxy; erros 400/404/422. | 0008 |
| Q11 | Quais historias? | H0 habilitadora + H1..H4 (abaixo). | - |
| Q12 | Limites de agregado? | Quatro agregados pequenos, uma porta por raiz. | 0009 |

Em todas as perguntas o grupo aceitou a recomendacao da IA. A justificativa de cada decisao esta no ADR correspondente.

## Historias de usuario acordadas

- **H0 (habilitadora):** como morador, quero criar um grupo e cadastrar os membros (com chave Pix opcional) para lancar contas entre nos. Use cases: `CriarGrupo`, `AdicionarMembro`.
- **H1:** como membro, quero registrar uma despesa que paguei, dividida igualmente ou por valores, para que cada um saiba sua parte. Use case: `LancarDespesa`.
- **H2:** como membro, quero ver meu saldo e as transferencias sugeridas e registrar um acerto via Pix, para zerar as dividas com o minimo de transferencias. Use cases: `ConsultarSaldos`, `RegistrarPagamento`.
- **H3:** como membro, quero abrir uma vaquinha com meta para pedir ajuda ao grupo, e os outros querem contribuir via Pix. Use cases: `CriarVaquinha`, `Contribuir`, `EncerrarVaquinha`.
- **H4:** como membro, quero ver quem mais apoiou as vaquinhas do grupo, para reconhecer quem ajuda. Use case: `ConsultarApoiadores`.

## Resultado

- Resumo da resposta: sessao de 12 perguntas, uma por vez, cada uma com recomendacao; modelo consolidado e confirmado pelo grupo antes da escrita dos documentos.
- Arquivos alterados: `GLOSSARY.md` (novo), `docs/adr/0001` a `0009` (novos), este registro.
- Testes e resultados: nao se aplica (nenhum codigo alterado).
- Commit resultante: (preencher apos o commit)
- Observacoes: o prompt dizia "Front: React"; a IA verificou que o front e Next.js (React) com proxy `/api`, o que dispensa CORS (ADR 0008). O placeholder `Task` permanece ate o primeiro recurso real ser implementado.
