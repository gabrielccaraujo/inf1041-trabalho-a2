from domain.despesa import Despesa, DespesaRepository
from domain.grupo import GrupoRepository
from use_cases.comum import obter_grupo_ou_falhar


class ListarDespesas:
    def __init__(
        self, grupos: GrupoRepository, despesas: DespesaRepository
    ) -> None:
        self._grupos = grupos
        self._despesas = despesas

    def executar(self, grupo_id: int) -> list[Despesa]:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        return self._despesas.listar_por_grupo(grupo.id)
