from domain.grupo import Grupo, GrupoRepository
from use_cases.buscar_grupo import buscar_grupo


class ConsultarGrupo:
    def __init__(self, grupos: GrupoRepository) -> None:
        self._grupos = grupos

    def executar(self, grupo_id: int) -> Grupo:
        return buscar_grupo(self._grupos, grupo_id)
