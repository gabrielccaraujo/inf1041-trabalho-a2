from domain.erros import NaoEncontrado
from domain.grupo import Grupo, GrupoRepository


def buscar_grupo(grupos: GrupoRepository, grupo_id: int) -> Grupo:
    """Carrega o Grupo ou falha com NaoEncontrado (reusado pelos use cases)."""
    grupo = grupos.buscar(grupo_id)
    if grupo is None:
        raise NaoEncontrado(f"Grupo {grupo_id} nao encontrado.")
    return grupo
