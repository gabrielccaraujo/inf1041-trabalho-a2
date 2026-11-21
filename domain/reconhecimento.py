"""Reconhecimento de ajuda, derivado so das Contribuicoes (ADR 0006)."""

from dataclasses import dataclass
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


class ReconhecimentoDeAjuda:
    """Servico de dominio puro: ranking dos Apoiadores de um Grupo.

    Despesas e Pagamentos nao entram: so Contribuicoes contam como ajuda,
    inclusive as de Vaquinhas encerradas.
    """

    def ranking(
        self, membros: Iterable[Membro], vaquinhas: Iterable[Vaquinha]
    ) -> list[Apoiador]:
        totais: dict[int, Valor] = {}
        apoiadas: dict[int, set[int]] = {}
        for vaquinha in vaquinhas:
            for contribuicao in vaquinha.contribuicoes:
                membro_id = contribuicao.membro_id
                totais[membro_id] = (
                    totais.get(membro_id, Valor(0)) + contribuicao.valor
                )
                apoiadas.setdefault(membro_id, set()).add(vaquinha.id)
        apoiadores = [
            Apoiador(m.id, m.nome, totais[m.id], len(apoiadas[m.id]))
            for m in membros
            if m.id in totais
        ]
        return sorted(
            apoiadores,
            key=lambda a: (
                -a.total_contribuido.centavos,
                -a.vaquinhas_apoiadas,
                a.nome.casefold(),
            ),
        )
