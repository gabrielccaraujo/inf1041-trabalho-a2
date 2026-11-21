# Vaquinha é separada da Despesa e não entra no Saldo

Despesa gera dívida; Vaquinha é um pedido de ajuda voluntário. Por isso são entidades distintas, e a Vaquinha não participa da `CalculadoraDeSaldos`. A Vaquinha tem Meta, Beneficiário e um ciclo de vida aberta → encerrada, controlado por `encerrar()` explícito. Atingir a Meta não encerra, e contribuir acima da Meta é permitido. A Contribuição é um value object append-only dentro da Vaquinha, sem edição nem remoção. Só Membros do Grupo contribuem, e o Beneficiário não contribui na própria Vaquinha.

## Considered Options

- Uma abstração `Lancamento` com campo `tipo`: os campos e as invariantes não coincidem, o que levaria a condicionais por tipo e violaria OCP e LSP.
- Contribuição como entidade removível: nenhuma história pede isso, e tornaria o Reconhecimento de ajuda instável.
