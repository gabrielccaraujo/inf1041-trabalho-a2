from domain.grupo import GrupoRepository
from domain.vaquinha import Vaquinha, VaquinhaRepository
from use_cases.comum import obter_grupo_ou_falhar


class ListarVaquinhas:
    def __init__(
        self, grupos: GrupoRepository, vaquinhas: VaquinhaRepository
    ) -> None:
        self._grupos = grupos
        self._vaquinhas = vaquinhas

    def executar(self, grupo_id: int) -> list[Vaquinha]:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        return self._vaquinhas.listar_por_grupo(grupo.id)
