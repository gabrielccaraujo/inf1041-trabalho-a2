from domain.despesa import DespesaRepository
from domain.grupo import GrupoRepository
from domain.saldos import CalculadoraDeSaldos, SaldosDoGrupo
from use_cases.comum import obter_grupo_ou_falhar


class ConsultarSaldos:
    """Carrega o historico do Grupo e delega o calculo (ADR 0004)."""

    def __init__(
        self, grupos: GrupoRepository, despesas: DespesaRepository
    ) -> None:
        self._grupos = grupos
        self._despesas = despesas
        self._calculadora = CalculadoraDeSaldos()

    def executar(self, grupo_id: int) -> SaldosDoGrupo:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        return self._calculadora.calcular(
            membros=[m.id for m in grupo.membros],
            despesas=self._despesas.listar_por_grupo(grupo.id),
        )
