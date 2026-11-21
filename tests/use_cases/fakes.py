"""Repositorios falsos em memoria: testam os use cases sem banco de dados."""

from typing import Optional

from domain.despesa import Despesa
from domain.grupo import Grupo
from domain.vaquinha import Vaquinha


class GrupoRepositoryEmMemoria:
    def __init__(self) -> None:
        self._grupos: dict[int, Grupo] = {}
        self._proximo_grupo_id = 1
        self._proximo_membro_id = 1

    def adicionar(self, grupo: Grupo) -> Grupo:
        grupo.id = self._proximo_grupo_id
        self._proximo_grupo_id += 1
        self._grupos[grupo.id] = grupo
        return self.salvar(grupo)

    def salvar(self, grupo: Grupo) -> Grupo:
        for membro in grupo.membros:
            if membro.id is None:
                membro.id = self._proximo_membro_id
                self._proximo_membro_id += 1
        self._grupos[grupo.id] = grupo
        return grupo

    def buscar(self, grupo_id: int) -> Optional[Grupo]:
        return self._grupos.get(grupo_id)


class DespesaRepositoryEmMemoria:
    def __init__(self) -> None:
        self._despesas: list[Despesa] = []

    def adicionar(self, despesa: Despesa) -> Despesa:
        despesa.id = len(self._despesas) + 1
        self._despesas.append(despesa)
        return despesa

    def listar_por_grupo(self, grupo_id: int) -> list[Despesa]:
        return [d for d in self._despesas if d.grupo_id == grupo_id]


class VaquinhaRepositoryEmMemoria:
    def __init__(self) -> None:
        self._vaquinhas: dict[int, Vaquinha] = {}

    def adicionar(self, vaquinha: Vaquinha) -> Vaquinha:
        vaquinha.id = len(self._vaquinhas) + 1
        self._vaquinhas[vaquinha.id] = vaquinha
        return vaquinha

    def salvar(self, vaquinha: Vaquinha) -> Vaquinha:
        self._vaquinhas[vaquinha.id] = vaquinha
        return vaquinha

    def buscar(self, vaquinha_id: int) -> Optional[Vaquinha]:
        return self._vaquinhas.get(vaquinha_id)

    def listar_por_grupo(self, grupo_id: int) -> list[Vaquinha]:
        return [
            v for v in self._vaquinhas.values() if v.grupo_id == grupo_id
        ]
