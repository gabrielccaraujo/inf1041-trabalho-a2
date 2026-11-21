from datetime import date

import pytest

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from domain.meio import Meio
from tests.use_cases.fakes import (
    GrupoRepositoryEmMemoria,
    PagamentoRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.criar_grupo import CriarGrupo
from use_cases.listar_pagamentos import ListarPagamentos
from use_cases.registrar_pagamento import RegistrarPagamento

HOJE = date(2026, 11, 21)


@pytest.fixture
def grupos():
    return GrupoRepositoryEmMemoria()


@pytest.fixture
def pagamentos():
    return PagamentoRepositoryEmMemoria()


@pytest.fixture
def grupo(grupos):
    grupo = CriarGrupo(grupos).executar("Rep")
    for nome in ["Ana", "Bruno", "Carla"]:
        AdicionarMembro(grupos).executar(grupo.id, nome)
    return grupos.buscar(grupo.id)


@pytest.fixture
def membros(grupo):
    return [m.id for m in grupo.membros]


@pytest.fixture
def registrar(grupos, pagamentos, grupo):
    use_case = RegistrarPagamento(grupos, pagamentos, relogio=lambda: HOJE)

    def registrar(de, para, valor_centavos, meio=Meio.PIX, grupo_id=None):
        return use_case.executar(
            grupo_id or grupo.id,
            de_membro_id=de,
            para_membro_id=para,
            valor_centavos=valor_centavos,
            meio=meio,
        )

    return registrar


def test_registrar_pagamento_e_listar_com_meio_e_data(
    grupos, pagamentos, registrar, grupo, membros
):
    ana, bruno, carla = membros

    pagamento = registrar(bruno, ana, 3333, Meio.PIX)
    registrar(carla, ana, 1000, Meio.DINHEIRO)

    assert pagamento.id is not None
    listados = ListarPagamentos(grupos, pagamentos).executar(grupo.id)
    assert [
        (p.de_membro_id, p.para_membro_id, p.valor.centavos, p.meio, p.data)
        for p in listados
    ] == [
        (bruno, ana, 3333, Meio.PIX, HOJE),
        (carla, ana, 1000, Meio.DINHEIRO, HOJE),
    ]


def test_pagamento_de_um_membro_para_ele_mesmo_e_rejeitado(registrar, membros):
    with pytest.raises(RegraDeDominioViolada):
        registrar(membros[0], membros[0], 1000)


@pytest.mark.parametrize("valor_centavos", [0, -100])
def test_pagamento_com_valor_zero_ou_negativo_e_rejeitado(
    registrar, membros, valor_centavos
):
    with pytest.raises(RegraDeDominioViolada):
        registrar(membros[1], membros[0], valor_centavos)


@pytest.mark.parametrize("de_fora", ["de", "para"])
def test_pagamento_com_membro_de_fora_do_grupo_e_rejeitado(
    registrar, membros, de_fora
):
    de, para = (999, membros[0]) if de_fora == "de" else (membros[0], 999)

    with pytest.raises(RegraDeDominioViolada):
        registrar(de, para, 1000)


def test_pagamento_rejeitado_nao_e_registrado(
    grupos, pagamentos, registrar, grupo, membros
):
    with pytest.raises(RegraDeDominioViolada):
        registrar(membros[0], membros[0], 1000)

    assert ListarPagamentos(grupos, pagamentos).executar(grupo.id) == []


def test_registrar_pagamento_em_grupo_inexistente_nao_e_encontrado(
    registrar, membros
):
    with pytest.raises(NaoEncontrado):
        registrar(membros[1], membros[0], 1000, grupo_id=99)


def test_listar_pagamentos_de_grupo_inexistente_nao_e_encontrado(
    grupos, pagamentos
):
    with pytest.raises(NaoEncontrado):
        ListarPagamentos(grupos, pagamentos).executar(99)
