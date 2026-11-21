"""Apoio compartilhado pelos use cases (nao e um use case)."""

from typing import Iterable

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from domain.grupo import Grupo, GrupoRepository
from domain.vaquinha import Vaquinha, VaquinhaRepository


def obter_grupo_ou_falhar(grupos: GrupoRepository, grupo_id: int) -> Grupo:
    """Carrega o Grupo ou falha com NaoEncontrado."""
    grupo = grupos.buscar(grupo_id)
    if grupo is None:
        raise NaoEncontrado(f"Grupo {grupo_id} nao encontrado.")
    return grupo


def garantir_membros_do_grupo(grupo: Grupo, membro_ids: Iterable[int]) -> None:
    """Falha se algum dos Membros nao for do Grupo (ADR 0009)."""
    for membro_id in membro_ids:
        if not grupo.tem_membro(membro_id):
            raise RegraDeDominioViolada(
                f"Membro {membro_id} nao pertence ao Grupo {grupo.id}."
            )


def obter_vaquinha_ou_falhar(
    vaquinhas: VaquinhaRepository, grupo: Grupo, vaquinha_id: int
) -> Vaquinha:
    """Carrega a Vaquinha do Grupo; a de outro Grupo conta como inexistente."""
    vaquinha = vaquinhas.buscar(vaquinha_id)
    if vaquinha is None or vaquinha.grupo_id != grupo.id:
        raise NaoEncontrado(f"Vaquinha {vaquinha_id} nao encontrada.")
    return vaquinha
