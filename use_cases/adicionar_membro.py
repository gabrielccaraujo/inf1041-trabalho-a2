from typing import Optional

from domain.grupo import GrupoRepository, Membro
from use_cases.comum import obter_grupo_ou_falhar


class AdicionarMembro:
    def __init__(self, grupos: GrupoRepository) -> None:
        self._grupos = grupos

    def executar(
        self, grupo_id: int, nome: str, chave_pix: Optional[str] = None
    ) -> Membro:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        membro = grupo.adicionar_membro(nome, chave_pix)
        self._grupos.salvar(grupo)
        return membro
