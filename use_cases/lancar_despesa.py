from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional, Protocol

from domain.despesa import Despesa, DespesaRepository, Divisao
from domain.erros import RegraDeDominioViolada
from domain.grupo import GrupoRepository
from domain.valor import Valor
from use_cases.comum import obter_grupo_ou_falhar


class PedidoDeDivisao(Protocol):
    """Modo de divisao escolhido pelo cliente; cada modo usa uma fabrica."""

    def dividir(self, valor: Valor) -> Divisao: ...


@dataclass(frozen=True)
class DivisaoIgualitaria:
    """Pedido de Divisao igualitaria entre os Membros informados."""

    membros: tuple[int, ...]

    def dividir(self, valor: Valor) -> Divisao:
        return Divisao.igualitaria(list(self.membros), valor)


@dataclass(frozen=True)
class DivisaoPorValores:
    """Pedido de Divisao com a Cota de cada Membro: (membro_id, centavos)."""

    cotas: tuple[tuple[int, int], ...]

    def dividir(self, valor: Valor) -> Divisao:
        return Divisao.por_valores(
            [(membro_id, Valor(c)) for membro_id, c in self.cotas], valor
        )


class LancarDespesa:
    def __init__(
        self,
        grupos: GrupoRepository,
        despesas: DespesaRepository,
        relogio: Callable[[], date],
    ) -> None:
        self._grupos = grupos
        self._despesas = despesas
        self._relogio = relogio

    def executar(
        self,
        grupo_id: int,
        descricao: str,
        valor_centavos: int,
        pagador_id: int,
        divisao: PedidoDeDivisao,
        data: Optional[date] = None,
    ) -> Despesa:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        valor = Valor(valor_centavos)
        divisao_da_despesa = divisao.dividir(valor)
        de_fora = [
            m
            for m in [pagador_id, *divisao_da_despesa.membros()]
            if not grupo.tem_membro(m)
        ]
        if de_fora:
            raise RegraDeDominioViolada(
                f"Membro {de_fora[0]} nao pertence ao Grupo {grupo.id}."
            )
        despesa = Despesa(
            grupo_id=grupo.id,
            descricao=descricao,
            valor=valor,
            pagador_id=pagador_id,
            data=data or self._relogio(),
            divisao=divisao_da_despesa,
        )
        return self._despesas.adicionar(despesa)
