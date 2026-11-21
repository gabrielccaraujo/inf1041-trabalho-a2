from datetime import date
from typing import Callable

from domain.grupo import GrupoRepository
from domain.meio import Meio
from domain.valor import Valor
from domain.vaquinha import Vaquinha, VaquinhaRepository
from use_cases.comum import (
    garantir_membros_do_grupo,
    obter_grupo_ou_falhar,
    obter_vaquinha_ou_falhar,
)


class Contribuir:
    def __init__(
        self,
        grupos: GrupoRepository,
        vaquinhas: VaquinhaRepository,
        relogio: Callable[[], date],
    ) -> None:
        self._grupos = grupos
        self._vaquinhas = vaquinhas
        self._relogio = relogio

    def executar(
        self,
        grupo_id: int,
        vaquinha_id: int,
        membro_id: int,
        valor_centavos: int,
        meio: Meio,
    ) -> Vaquinha:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        vaquinha = obter_vaquinha_ou_falhar(
            self._vaquinhas, grupo, vaquinha_id
        )
        garantir_membros_do_grupo(grupo, [membro_id])
        vaquinha.contribuir(
            membro_id, Valor(valor_centavos), meio, self._relogio()
        )
        return self._vaquinhas.salvar(vaquinha)
