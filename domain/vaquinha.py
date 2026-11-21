from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Protocol

from domain.erros import RegraDeDominioViolada
from domain.meio import Meio
from domain.valor import Valor


@dataclass(frozen=True)
class Contribuicao:
    """Valor dado a uma Vaquinha; nao gera divida e nao se desfaz."""

    membro_id: int
    valor: Valor
    meio: Meio
    data: date

    def __post_init__(self) -> None:
        if self.valor <= Valor(0):
            raise RegraDeDominioViolada(
                "O Valor da Contribuicao deve ser positivo."
            )


@dataclass
class Vaquinha:
    """Raiz de agregado separada da Despesa: nao entra no Saldo.

    Ver ADR 0005.
    """

    grupo_id: int
    titulo: str
    descricao: str
    meta: Valor
    beneficiario_id: int
    encerrada: bool = False
    contribuicoes: list[Contribuicao] = field(default_factory=list)
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.titulo = (self.titulo or "").strip()
        if not self.titulo:
            raise RegraDeDominioViolada(
                "O titulo da Vaquinha nao pode ser vazio."
            )
        self.descricao = (self.descricao or "").strip()
        if self.meta <= Valor(0):
            raise RegraDeDominioViolada(
                "A Meta da Vaquinha deve ser positiva."
            )

    def contribuir(
        self, membro_id: int, valor: Valor, meio: Meio, data: date
    ) -> Contribuicao:
        if self.encerrada:
            raise RegraDeDominioViolada(
                "A Vaquinha encerrada nao aceita Contribuicoes."
            )
        if membro_id == self.beneficiario_id:
            raise RegraDeDominioViolada(
                "O Beneficiario nao contribui na propria Vaquinha."
            )
        contribuicao = Contribuicao(membro_id, valor, meio, data)
        self.contribuicoes.append(contribuicao)
        return contribuicao

    def encerrar(self) -> None:
        if self.encerrada:
            raise RegraDeDominioViolada("A Vaquinha ja esta encerrada.")
        self.encerrada = True

    def total_arrecadado(self) -> Valor:
        return sum((c.valor for c in self.contribuicoes), Valor(0))


class VaquinhaRepository(Protocol):
    """Porta de persistencia da Vaquinha, implementada na infra.

    `salvar` grava o status e as Contribuicoes novas.
    """

    def adicionar(self, vaquinha: Vaquinha) -> Vaquinha: ...

    def salvar(self, vaquinha: Vaquinha) -> Vaquinha: ...

    def buscar(self, vaquinha_id: int) -> Optional[Vaquinha]: ...

    def listar_por_grupo(self, grupo_id: int) -> list[Vaquinha]: ...
