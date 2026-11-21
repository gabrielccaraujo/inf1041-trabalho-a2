from dataclasses import dataclass, field
from typing import Optional, Protocol

from domain.erros import RegraDeDominioViolada

TAMANHO_MAXIMO_CHAVE_PIX = 77


@dataclass
class Membro:
    """Entidade interna do Grupo (ADR 0001).

    A Chave Pix e so exibida, nunca validada contra o banco (ADR 0007);
    o limite de tamanho apenas barra erro grosseiro de digitacao.
    """

    nome: str
    chave_pix: Optional[str] = None
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.nome = _nome_obrigatorio(self.nome, "Membro")
        self.chave_pix = (self.chave_pix or "").strip() or None
        if self.chave_pix and len(self.chave_pix) > TAMANHO_MAXIMO_CHAVE_PIX:
            raise RegraDeDominioViolada(
                "A Chave Pix deve ter no maximo "
                f"{TAMANHO_MAXIMO_CHAVE_PIX} caracteres."
            )


@dataclass
class Grupo:
    """Raiz de agregado: garante nome nao vazio e nome de Membro unico.

    Ver ADR 0009.
    """

    nome: str
    membros: list[Membro] = field(default_factory=list)
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.nome = _nome_obrigatorio(self.nome, "Grupo")
        vistos: list[Membro] = []
        for membro in self.membros:
            self._garantir_nome_livre(membro.nome, vistos)
            vistos.append(membro)

    def adicionar_membro(
        self, nome: str, chave_pix: Optional[str] = None
    ) -> Membro:
        membro = Membro(nome=nome, chave_pix=chave_pix)
        self._garantir_nome_livre(membro.nome, self.membros)
        self.membros.append(membro)
        return membro

    @staticmethod
    def _garantir_nome_livre(nome: str, membros: list[Membro]) -> None:
        if any(m.nome.casefold() == nome.casefold() for m in membros):
            raise RegraDeDominioViolada(
                f"Ja existe um Membro chamado {nome} no Grupo."
            )


def _nome_obrigatorio(nome: Optional[str], entidade: str) -> str:
    nome = (nome or "").strip()
    if not nome:
        raise RegraDeDominioViolada(
            f"O nome do {entidade} nao pode ser vazio."
        )
    return nome


class GrupoRepository(Protocol):
    """Porta de persistencia do Grupo, implementada na infra.

    `salvar` grava os Membros novos (sem id) e lhes atribui id.
    """

    def adicionar(self, grupo: Grupo) -> Grupo: ...

    def salvar(self, grupo: Grupo) -> Grupo: ...

    def buscar(self, grupo_id: int) -> Optional[Grupo]: ...
