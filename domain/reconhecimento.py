"""Reconhecimento de ajuda, derivado so das Contribuicoes (ADR 0006)."""

from dataclasses import dataclass, field
from typing import Iterable

from domain.grupo import Membro
from domain.valor import Valor
from domain.vaquinha import Vaquinha


@dataclass(frozen=True)
class Apoiador:
    """Membro que fez ao menos uma Contribuicao."""

    membro_id: int
    nome: str
    total_contribuido: Valor
    vaquinhas_apoiadas: int


@dataclass
class _AjudaDoMembro:
    """Acumula o que um Membro contribuiu e em quais Vaquinhas."""

    total: Valor = Valor(0)
    vaquinhas: set[int] = field(default_factory=set)

    def registrar(self, vaquinha_id: int, valor: Valor) -> None:
        self.total += valor
        self.vaquinhas.add(vaquinha_id)


class ReconhecimentoDeAjuda:
    """Servico de dominio puro: ranking dos Apoiadores de um Grupo.

    Despesas e Pagamentos nao entram: so Contribuicoes contam como ajuda,
    inclusive as de Vaquinhas encerradas.
    """

    def ranking(
        self, membros: Iterable[Membro], vaquinhas: Iterable[Vaquinha]
    ) -> list[Apoiador]:
        ajuda: dict[int, _AjudaDoMembro] = {}
        for vaquinha in vaquinhas:
            for contribuicao in vaquinha.contribuicoes:
                ajuda.setdefault(
                    contribuicao.membro_id, _AjudaDoMembro()
                ).registrar(vaquinha.id, contribuicao.valor)
        apoiadores = [
            Apoiador(
                m.id,
                m.nome,
                ajuda[m.id].total,
                len(ajuda[m.id].vaquinhas),
            )
            for m in membros
            if m.id in ajuda
        ]
        return sorted(
            apoiadores,
            key=lambda a: (
                -a.total_contribuido.centavos,
                -a.vaquinhas_apoiadas,
                a.nome.casefold(),  # o Grupo garante nome unico
            ),
        )
