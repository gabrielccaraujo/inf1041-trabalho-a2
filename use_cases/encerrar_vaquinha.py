from domain.grupo import GrupoRepository
from domain.vaquinha import Vaquinha, VaquinhaRepository
from use_cases.comum import obter_grupo_ou_falhar, obter_vaquinha_ou_falhar


class EncerrarVaquinha:
    def __init__(
        self, grupos: GrupoRepository, vaquinhas: VaquinhaRepository
    ) -> None:
        self._grupos = grupos
        self._vaquinhas = vaquinhas

    def executar(self, grupo_id: int, vaquinha_id: int) -> Vaquinha:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        vaquinha = obter_vaquinha_ou_falhar(
            self._vaquinhas, grupo, vaquinha_id
        )
        vaquinha.encerrar()
        return self._vaquinhas.salvar(vaquinha)
