from domain.grupo import GrupoRepository
from domain.reconhecimento import Apoiador, ReconhecimentoDeAjuda
from domain.vaquinha import VaquinhaRepository
from use_cases.comum import obter_grupo_ou_falhar


class ConsultarApoiadores:
    """Carrega as Vaquinhas do Grupo e delega o ranking (ADR 0006)."""

    def __init__(
        self, grupos: GrupoRepository, vaquinhas: VaquinhaRepository
    ) -> None:
        self._grupos = grupos
        self._vaquinhas = vaquinhas
        self._reconhecimento = ReconhecimentoDeAjuda()

    def executar(self, grupo_id: int) -> list[Apoiador]:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        return self._reconhecimento.ranking(
            grupo.membros, self._vaquinhas.listar_por_grupo(grupo.id)
        )
