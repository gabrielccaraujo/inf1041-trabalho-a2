from dataclasses import dataclass
from datetime import date
from typing import Optional, Protocol

from domain.erros import RegraDeDominioViolada
from domain.valor import Valor


@dataclass(frozen=True)
class Cota:
    """Parte da Divisao que cabe a um Membro."""

    membro_id: int
    valor: Valor


@dataclass(frozen=True)
class Divisao:
    """VO de Cotas cuja soma e o Valor da Despesa (ADR 0003)."""

    cotas: tuple[Cota, ...]

    def __post_init__(self) -> None:
        if not self.cotas:
            raise RegraDeDominioViolada(
                "A Divisao precisa de ao menos um Membro."
            )
        membros = self.membros()
        if len(set(membros)) != len(membros):
            raise RegraDeDominioViolada(
                "Um Membro nao pode ter duas Cotas na mesma Divisao."
            )

    @classmethod
    def igualitaria(cls, membros: list[int], valor: Valor) -> "Divisao":
        if not membros:
            return cls(())
        partes = valor.dividir_em(len(membros))
        return cls(tuple(Cota(m, v) for m, v in zip(membros, partes)))

    def membros(self) -> list[int]:
        return [cota.membro_id for cota in self.cotas]

    def total(self) -> Valor:
        return sum((cota.valor for cota in self.cotas), Valor(0))


@dataclass
class Despesa:
    """Raiz de agregado: gasto de um Pagador repartido numa Divisao."""

    grupo_id: int
    descricao: str
    valor: Valor
    pagador_id: int
    data: date
    divisao: Divisao
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.descricao = (self.descricao or "").strip()
        if not self.descricao:
            raise RegraDeDominioViolada(
                "A descricao da Despesa nao pode ser vazia."
            )
        if self.valor <= Valor(0):
            raise RegraDeDominioViolada(
                "O Valor da Despesa deve ser positivo."
            )
        if self.divisao.total() != self.valor:
            raise RegraDeDominioViolada(
                "A soma das Cotas deve ser igual ao Valor da Despesa."
            )

    @property
    def cotas(self) -> tuple[Cota, ...]:
        return self.divisao.cotas


class DespesaRepository(Protocol):
    """Porta de persistencia da Despesa, implementada na infra."""

    def adicionar(self, despesa: Despesa) -> Despesa: ...

    def listar_por_grupo(self, grupo_id: int) -> list[Despesa]: ...
