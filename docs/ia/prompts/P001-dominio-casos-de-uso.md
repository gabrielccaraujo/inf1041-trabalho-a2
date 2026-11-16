# P001 — Domínio e casos de uso RachAÍ

- Data: 2026-11-16
- Responsável: Gabriel com apoio do Codex nesta conversa
- Ferramenta/modelo: Codex, modelo da conversa
- Commit anterior: `c2efdb6eee8a425f434fdf3bd4780d7134e9b671`
- Commit de código resultante: `b0e125f70d9bf4acdf57ca2fd4bb7ad569903c67`
- Objetivo: definir entidades, regras e casos de uso independentes de Flask/SQLite
- Fontes consultadas: `Trabalho A2 - Arquiteutra e Projetos de Software.pdf`; `Lean Inception RachAÍ.pdf` (sequenciador e PBB Canvas, páginas 31 e 44); código no commit anterior

## Pedido integral do usuário

```text
Pode fazer los entao, seguindo os padroes de uso de IA. Tente implementar a estrutura "Sugestão de Estrutura de Pastas - Clean Architecture em Flask" Como eu abro o projeto no vs code? "CLone repository"?
```

Contexto anterior do usuário: “Para o uso de IA, o professor pediu uso de prompts desenvolvidos, guardados como artefatos, para podermos voltar exatamente onde oque foi implementando. Se tivermos problema em uma parte do codigo, conseguimos voltar no exato prompt que efetuou essa etapa.”

## Especificação operacional da etapa

```text
No backend RachAÍ, implemente uma primeira fatia coerente com o Lean Inception:
F01 cadastro/login, F02 grupos/convites, F03 registrar despesa, F04 dividir
despesa igualmente e F05 mostrar saldos. Use a estrutura Clean Architecture
sugerida pelo PDF da A2. Nesta etapa, trabalhe só nas camadas domain/ e
use_cases/, sem dependências de Flask e SQLite.

Modele User, Group, Expense e Split. Faça a divisão com centavos inteiros,
sem arredondamento que altere o total, e defina comportamento determinístico
para centavos restantes. Valide dados de entrada e participação no grupo.
Defina uma porta de repositório para injeção de dependência. Faça testes
Pytest dos casos de uso com repositório falso e de regras puras. Não inclua
Pix, vaquinha ou ranking nesta fatia. Preserve a rastreabilidade entre este
registro, o commit anterior e o commit produzido.
```

Esta especificação detalha o pedido recebido e registra as decisões usadas na intervenção; não representa uma chamada separada ao modelo.

## Resultado

- Arquivos: `domain/`, `use_cases/`, `tests/test_domain.py`, `tests/test_use_cases.py`.
- Regras: valor positivo com até duas casas; participantes distintos; divisão igual em centavos; acesso restrito aos membros; autenticação com senha derivada e sessão.
- Verificação final da branch: `python -m pytest -q` → 12 testes passaram (inclui P002).
- Para reproduzir o estado apenas desta etapa: `git checkout b0e125f70d9bf4acdf57ca2fd4bb7ad569903c67`.
