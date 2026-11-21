from datetime import date

import pytest

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from tests.use_cases.fakes import (
    DespesaRepositoryEmMemoria,
    GrupoRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.criar_grupo import CriarGrupo
from use_cases.lancar_despesa import DivisaoIgualitaria, LancarDespesa
from use_cases.listar_despesas import ListarDespesas

HOJE = date(2026, 11, 20)


@pytest.fixture
def grupos():
    return GrupoRepositoryEmMemoria()


@pytest.fixture
def despesas():
    return DespesaRepositoryEmMemoria()


@pytest.fixture
def grupo(grupos):
    grupo = CriarGrupo(grupos).executar("Republica Azul")
    for nome in ["Ana", "Bruno", "Carla", "Davi"]:
        AdicionarMembro(grupos).executar(grupo.id, nome)
    return grupos.buscar(grupo.id)


@pytest.fixture
def ana(grupo):
    return grupo.membros[0].id


@pytest.fixture
def bruno(grupo):
    return grupo.membros[1].id


@pytest.fixture
def carla(grupo):
    return grupo.membros[2].id


@pytest.fixture
def davi(grupo):
    return grupo.membros[3].id


@pytest.fixture
def lancar(grupos, despesas):
    return LancarDespesa(grupos, despesas, relogio=lambda: HOJE)


def cotas_em_centavos(despesa):
    return [(c.membro_id, c.valor.centavos) for c in despesa.cotas]


def test_divisao_igualitaria_entrega_sobra_de_centavos_aos_primeiros(
    lancar, grupo, ana, bruno, carla
):
    despesa = lancar.executar(
        grupo.id,
        descricao="Conta de luz",
        valor_centavos=10000,
        pagador_id=ana,
        divisao=DivisaoIgualitaria(membros=[bruno, ana, carla]),
    )

    assert despesa.id is not None
    assert despesa.descricao == "Conta de luz"
    assert despesa.valor.centavos == 10000
    assert despesa.pagador_id == ana
    assert cotas_em_centavos(despesa) == [
        (bruno, 3334),
        (ana, 3333),
        (carla, 3333),
    ]


def test_pagador_pode_ficar_fora_da_divisao(lancar, grupo, ana, bruno, carla):
    despesa = lancar.executar(
        grupo.id,
        descricao="Mercado",
        valor_centavos=5000,
        pagador_id=ana,
        divisao=DivisaoIgualitaria(membros=[bruno, carla]),
    )

    assert cotas_em_centavos(despesa) == [(bruno, 2500), (carla, 2500)]


def test_sem_data_a_despesa_usa_a_data_do_relogio(lancar, grupo, ana):
    despesa = lancar.executar(
        grupo.id,
        descricao="Gas",
        valor_centavos=9000,
        pagador_id=ana,
        divisao=DivisaoIgualitaria(membros=[ana]),
    )

    assert despesa.data == HOJE


def test_data_informada_e_mantida(lancar, grupo, ana):
    despesa = lancar.executar(
        grupo.id,
        descricao="Gas",
        valor_centavos=9000,
        pagador_id=ana,
        divisao=DivisaoIgualitaria(membros=[ana]),
        data=date(2026, 10, 1),
    )

    assert despesa.data == date(2026, 10, 1)


def lancar_padrao(lancar, grupo_id, pagador_id, membros, **mudancas):
    dados = dict(
        descricao="Conta de luz",
        valor_centavos=10000,
        pagador_id=pagador_id,
        divisao=DivisaoIgualitaria(membros=membros),
    )
    dados.update(mudancas)
    return lancar.executar(grupo_id, **dados)


@pytest.mark.parametrize("valor_centavos", [0, -100])
def test_despesa_com_valor_zero_ou_negativo_e_rejeitada(
    lancar, grupo, ana, bruno, valor_centavos
):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(
            lancar, grupo.id, ana, [ana, bruno], valor_centavos=valor_centavos
        )


@pytest.mark.parametrize("descricao", ["", "   "])
def test_despesa_sem_descricao_e_rejeitada(
    lancar, grupo, ana, bruno, descricao
):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, bruno], descricao=descricao)


def test_descricao_e_aparada(lancar, grupo, ana):
    despesa = lancar_padrao(lancar, grupo.id, ana, [ana], descricao=" Luz ")

    assert despesa.descricao == "Luz"


def test_pagador_de_fora_do_grupo_e_rejeitado(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, 999, [ana])


def test_participante_de_fora_do_grupo_e_rejeitado(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, 999])


def test_membro_de_outro_grupo_e_rejeitado(grupos, lancar, grupo, ana):
    outro = CriarGrupo(grupos).executar("Viagem")
    intruso = AdicionarMembro(grupos).executar(outro.id, "Eva")

    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, intruso.id])


def test_divisao_sem_participantes_e_rejeitada(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [])


def test_participante_repetido_na_divisao_e_rejeitado(
    lancar, grupo, ana, bruno
):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, bruno, ana])


def test_despesa_rejeitada_nao_e_lancada(despesas, lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, 999])

    assert despesas.listar_por_grupo(grupo.id) == []


def test_lancar_despesa_em_grupo_inexistente(lancar, ana):
    with pytest.raises(NaoEncontrado):
        lancar_padrao(lancar, 99, ana, [ana])


def test_listar_despesas_do_grupo_com_pagador_e_cotas(
    grupos, despesas, lancar, grupo, ana, bruno, carla
):
    lancar_padrao(lancar, grupo.id, ana, [ana, bruno], descricao="Luz")
    lancar_padrao(
        lancar, grupo.id, bruno, [carla], descricao="Pizza",
        valor_centavos=4500,
    )
    outro = CriarGrupo(grupos).executar("Viagem")
    eva = AdicionarMembro(grupos).executar(outro.id, "Eva")
    lancar_padrao(lancar, outro.id, eva.id, [eva.id], descricao="Hotel")

    listadas = ListarDespesas(grupos, despesas).executar(grupo.id)

    assert [
        (d.descricao, d.pagador_id, d.valor.centavos, cotas_em_centavos(d))
        for d in listadas
    ] == [
        ("Luz", ana, 10000, [(ana, 5000), (bruno, 5000)]),
        ("Pizza", bruno, 4500, [(carla, 4500)]),
    ]


def test_listar_despesas_de_grupo_inexistente(grupos, despesas):
    with pytest.raises(NaoEncontrado):
        ListarDespesas(grupos, despesas).executar(99)
