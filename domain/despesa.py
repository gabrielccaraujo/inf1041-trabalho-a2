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
    """VO de Cotas que reparte um Valor (ADR 0003).

    Garante na construcao: ao menos uma Cota, uma Cota por Membro e soma
    das Cotas igual ao Valor repartido. Os modos de divisao sao fabricas.
    """

    valor: Valor
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
        total = sum((cota.valor for cota in self.cotas), Valor(0))
        if total != self.valor:
            raise RegraDeDominioViolada(
                "A soma das Cotas deve ser igual ao Valor da Despesa."
            )

    @classmethod
    def igualitaria(cls, membros: list[int], valor: Valor) -> "Divisao":
        """A sobra de centavos vai para os primeiros Membros da lista."""
        if not membros:
            return cls(valor, ())
        valores_das_cotas = valor.dividir_em(len(membros))
        return cls(
            valor,
            tuple(Cota(m, v) for m, v in zip(membros, valores_das_cotas)),
        )

    def membros(self) -> list[int]:
        return [cota.membro_id for cota in self.cotas]


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
        if self.divisao.valor != self.valor:
            raise RegraDeDominioViolada(
                "A Divisao deve repartir o Valor da Despesa."
            )

    @property
    def cotas(self) -> tuple[Cota, ...]:
        return self.divisao.cotas


class DespesaRepository(Protocol):
    """Porta de persistencia da Despesa, implementada na infra."""

    def adicionar(self, despesa: Despesa) -> Despesa: ...

    def listar_por_grupo(self, grupo_id: int) -> list[Despesa]: ...
