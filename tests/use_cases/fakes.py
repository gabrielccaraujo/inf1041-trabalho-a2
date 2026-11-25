"""Repositorios falsos em memoria: testam os use cases sem banco de dados."""

from copy import deepcopy
from typing import Optional

from domain.despesa import Despesa
from domain.erros import NaoEncontrado
from domain.grupo import Grupo
from domain.pagamento import Pagamento
from domain.vaquinha import Contribuicao, Vaquinha


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
    """Usa copias desacopladas, como o adaptador SQLite."""

    def __init__(self) -> None:
        self._vaquinhas: dict[int, Vaquinha] = {}

    def adicionar(self, vaquinha: Vaquinha) -> Vaquinha:
        vaquinha.id = len(self._vaquinhas) + 1
        self._vaquinhas[vaquinha.id] = deepcopy(vaquinha)
        return vaquinha

    def adicionar_contribuicao(
        self, vaquinha_id: int, contribuicao: Contribuicao
    ) -> Contribuicao:
        vaquinha = self._obter(vaquinha_id)
        nova = vaquinha.contribuir(
            contribuicao.membro_id,
            contribuicao.valor,
            contribuicao.meio,
            contribuicao.data,
        )
        self._vaquinhas[vaquinha_id] = vaquinha
        return nova

    def encerrar(self, vaquinha_id: int) -> Vaquinha:
        vaquinha = self._obter(vaquinha_id)
        vaquinha.encerrar()
        self._vaquinhas[vaquinha_id] = deepcopy(vaquinha)
        return vaquinha

    def buscar(self, vaquinha_id: int) -> Optional[Vaquinha]:
        return deepcopy(self._vaquinhas.get(vaquinha_id))

    def _obter(self, vaquinha_id: int) -> Vaquinha:
        vaquinha = self.buscar(vaquinha_id)
        if vaquinha is None:
            raise NaoEncontrado(f"Vaquinha {vaquinha_id} nao encontrada.")
        return vaquinha

    def listar_por_grupo(self, grupo_id: int) -> list[Vaquinha]:
        return deepcopy(
            [v for v in self._vaquinhas.values() if v.grupo_id == grupo_id]
        )


class PagamentoRepositoryEmMemoria:
    def __init__(self) -> None:
        self._pagamentos: list[Pagamento] = []

    def adicionar(self, pagamento: Pagamento) -> Pagamento:
        pagamento.id = len(self._pagamentos) + 1
        self._pagamentos.append(pagamento)
        return pagamento

    def listar_por_grupo(self, grupo_id: int) -> list[Pagamento]:
        return [p for p in self._pagamentos if p.grupo_id == grupo_id]
