from domain.grupo import Grupo, GrupoRepository
from use_cases.comum import obter_grupo_ou_falhar


class ConsultarGrupo:
    def __init__(self, grupos: GrupoRepository) -> None:
        self._grupos = grupos

    def executar(self, grupo_id: int) -> Grupo:
        return obter_grupo_ou_falhar(self._grupos, grupo_id)
