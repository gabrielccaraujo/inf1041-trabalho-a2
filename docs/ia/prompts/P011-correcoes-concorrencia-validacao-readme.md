# P011 - Correcoes de concorrencia, validacao e README

- Data: 2026-11-25
- Ferramenta: Codex; identificador exato do modelo nao registrado.
- Entrada: inf1041-trabalho-a2-main.zip fornecido pelo usuario.
- SHA-256 do ZIP de entrada: `fbdca995942cb65be88a2d515e78a53fe74dd13381c8d9016f2aa28fe0f4d753`.
- Commit anterior: indisponivel; o ZIP nao contem .git.
- Commit resultante: nao criado; esta entrega e uma copia corrigida local.
- Objetivo: corrigir os dois defeitos reproduzidos na revisao e atualizar
  a documentacao para o escopo ja implementado.

## Prompt integral

```text
Como que voce implementaria a mudanca nova? Mude a parte do readme tambem. O .2 tambem
```

Contexto do pedido: a revisao anterior reproduziu perda de Contribuicoes
simultaneas, resposta 500 para divisao.modo igual a lista ou objeto e
trechos do README que ainda tratavam tema e contrato como pendentes.

## Implementacao

- Porta VaquinhaRepository com adicionar_contribuicao e encerrar,
  substituindo a sincronizacao por salvar.
- Adaptador SQLite aplica as regras do dominio ao estado atual dentro
  de uma transacao BEGIN IMMEDIATE e grava somente a nova Contribuicao
  ou a mudanca de status. Nao ha alteracao de schema.
- Casos de uso preservam a validacao do Grupo, dos Membros e do dominio;
  o adaptador revalida o estado que efetivamente sera alterado.
- Fake de Vaquinha usa copias desacopladas e implementa a nova porta.
- divisao.modo passa por texto_obrigatorio antes da consulta ao mapa
  de estrategias, retornando 400 para formato invalido.
- README atualizado com funcionalidades, escopo sem login/Pix bancario,
  arquitetura, preparacao do ambiente, integracao, contrato e testes.
- Decisao transacional registrada no ADR 0010.

## Verificacao

Antes da correcao, os novos testes produziram 6 falhas e 4 sucessos:
perda de Contribuicao na mesma conexao e entre conexoes separadas,
Contribuicao em voo reabrindo uma Vaquinha, dois encerramentos aceitos
e modo de divisao como lista ou objeto causando 500.

Depois da correcao, a suite completa passou com 184 testes, incluindo os
174 originais e 10 novos cenarios parametrizados/de concorrencia.
pycodestyle 2.15.0 verificou app, domain, infra, use_cases e tests,
sem apontamentos. A ferramenta de estilo foi instalada separadamente,
sem mudar requirements.txt.

Os testes foram executados com o ambiente Python 3.12 ja existente neste
computador, em uma copia separada do ZIP. O frontend nao foi alterado.
Build e Playwright do frontend nao foram executados nesta intervencao.

## Integracao

Nenhum push ou alteracao no GitHub foi realizado. Ao integrar esta copia
ao repositorio, registrar o hash real do commit em um registro complementar.
Os registros P001-P010 foram preservados.
