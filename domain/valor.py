from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Valor:
    """Quantia em centavos inteiros (ADR 0002). Aceita sinal para Saldo."""

    centavos: int

    def __add__(self, outro: "Valor") -> "Valor":
        return Valor(self.centavos + outro.centavos)

    def __sub__(self, outro: "Valor") -> "Valor":
        return Valor(self.centavos - outro.centavos)

    def __neg__(self) -> "Valor":
        return Valor(-self.centavos)

    def dividir_em(self, partes: int) -> list["Valor"]:
        """Divide em partes que somam o total; a sobra vai para as primeiras.

        Ex.: 10000 em 3 partes da 3334, 3333 e 3333.
        """
        base, sobra = divmod(self.centavos, partes)
        return [Valor(base + (1 if i < sobra else 0)) for i in range(partes)]
