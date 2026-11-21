"""Apoio compartilhado pelos use cases (nao e um use case)."""

from domain.erros import NaoEncontrado
from domain.grupo import Grupo, GrupoRepository


def obter_grupo_ou_falhar(grupos: GrupoRepository, grupo_id: int) -> Grupo:
    """Carrega o Grupo ou falha com NaoEncontrado."""
    grupo = grupos.buscar(grupo_id)
    if grupo is None:
        raise NaoEncontrado(f"Grupo {grupo_id} nao encontrado.")
    return grupo
