from typing import Optional

from domain.grupo import GrupoRepository, Membro
from use_cases.buscar_grupo import buscar_grupo


class AdicionarMembro:
    def __init__(self, grupos: GrupoRepository) -> None:
        self._grupos = grupos

    def executar(
        self, grupo_id: int, nome: str, chave_pix: Optional[str] = None
    ) -> Membro:
        grupo = buscar_grupo(self._grupos, grupo_id)
        membro = grupo.adicionar_membro(nome, chave_pix)
        self._grupos.salvar(grupo)
        return membro
