from dataclasses import dataclass
from datetime import date
from typing import Optional, Protocol

from domain.erros import RegraDeDominioViolada
from domain.meio import Meio
from domain.valor import Valor


@dataclass
class Pagamento:
    """Raiz de agregado: Pagamento declarado entre dois Membros.

    E declarativo: o RachAI confia e nunca confirma (ADR 0007).
    """

    grupo_id: int
    de_membro_id: int
    para_membro_id: int
    valor: Valor
    meio: Meio
    data: date
    id: Optional[int] = None

    def __post_init__(self) -> None:
        if self.de_membro_id == self.para_membro_id:
            raise RegraDeDominioViolada(
                "Um Membro nao faz Pagamento para ele mesmo."
            )
        if self.valor <= Valor(0):
            raise RegraDeDominioViolada(
                "O Valor do Pagamento deve ser positivo."
            )


class PagamentoRepository(Protocol):
    """Porta de persistencia do Pagamento, implementada na infra."""

    def adicionar(self, pagamento: Pagamento) -> Pagamento: ...

    def listar_por_grupo(self, grupo_id: int) -> list[Pagamento]: ...
