"""Saldos e Transferencias sugeridas, derivados e nunca persistidos.

Ver ADR 0004.
"""

from dataclasses import dataclass
from typing import Iterable, Protocol

from domain.despesa import Despesa
from domain.valor import Valor

ZERO = Valor(0)


@dataclass(frozen=True)
class SaldoDoMembro:
    """Positivo: tem a receber. Negativo: deve."""

    membro_id: int
    valor: Valor


@dataclass(frozen=True)
class TransferenciaSugerida:
    de_membro_id: int
    para_membro_id: int
    valor: Valor


@dataclass(frozen=True)
class SaldosDoGrupo:
    saldos: list[SaldoDoMembro]
    transferencias: list[TransferenciaSugerida]


class PagamentoDeclarado(Protocol):
    """O que a calculadora precisa de um Pagamento entre dois Membros."""

    de_membro_id: int
    para_membro_id: int
    valor: Valor


class CalculadoraDeSaldos:
    """Servico de dominio puro: sem I/O, mesmo historico, mesma resposta."""

    def calcular(
        self,
        membros: list[int],
        despesas: Iterable[Despesa],
        pagamentos: Iterable[PagamentoDeclarado] = (),
    ) -> SaldosDoGrupo:
        saldos = {membro_id: ZERO for membro_id in membros}
        for despesa in despesas:
            saldos[despesa.pagador_id] += despesa.valor
            for cota in despesa.cotas:
                saldos[cota.membro_id] -= cota.valor
        for pagamento in pagamentos:
            saldos[pagamento.de_membro_id] += pagamento.valor
            saldos[pagamento.para_membro_id] -= pagamento.valor
        return SaldosDoGrupo(
            saldos=[SaldoDoMembro(m, saldos[m]) for m in membros],
            transferencias=self._sugerir_transferencias(membros, saldos),
        )

    @staticmethod
    def _sugerir_transferencias(
        membros: list[int], saldos: dict[int, Valor]
    ) -> list[TransferenciaSugerida]:
        """Guloso: o maior devedor paga ao maior credor ate zerar.

        Empates sao resolvidos pela ordem dos Membros no Grupo, o que torna
        o resultado deterministico. Cada passo zera ao menos um Saldo, entao
        sao no maximo N-1 transferencias.
        """
        ordem = {membro_id: i for i, membro_id in enumerate(membros)}
        restantes = dict(saldos)
        transferencias = []
        while True:
            devedores = [m for m in membros if restantes[m] < ZERO]
            credores = [m for m in membros if restantes[m] > ZERO]
            if not devedores or not credores:
                return transferencias
            devedor = min(devedores, key=lambda m: (restantes[m], ordem[m]))
            credor = min(credores, key=lambda m: (-restantes[m], ordem[m]))
            valor = min(-restantes[devedor], restantes[credor])
            transferencias.append(
                TransferenciaSugerida(devedor, credor, valor)
            )
            restantes[devedor] += valor
            restantes[credor] -= valor
