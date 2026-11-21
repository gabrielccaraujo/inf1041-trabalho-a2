from datetime import date

import pytest

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from tests.use_cases.fakes import (
    DespesaRepositoryEmMemoria,
    GrupoRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.criar_grupo import CriarGrupo
from use_cases.lancar_despesa import (
    DivisaoIgualitaria,
    DivisaoPorValores,
    LancarDespesa,
)
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


def lancar_padrao(lancar, grupo_id, pagador_id, membros, **mudancas):
    dados = dict(
        descricao="Conta de luz",
        valor_centavos=10000,
        pagador_id=pagador_id,
        divisao=DivisaoIgualitaria(membros=tuple(membros)),
    )
    dados.update(mudancas)
    return lancar.executar(grupo_id, **dados)


def test_divisao_igualitaria_entrega_sobra_de_centavos_aos_primeiros(
    lancar, grupo, ana, bruno, carla
):
    despesa = lancar_padrao(lancar, grupo.id, ana, [bruno, ana, carla])

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
    despesa = lancar_padrao(
        lancar, grupo.id, ana, [bruno, carla], valor_centavos=5000
    )

    assert cotas_em_centavos(despesa) == [(bruno, 2500), (carla, 2500)]


def test_sem_data_a_despesa_usa_a_data_do_relogio(lancar, grupo, ana):
    despesa = lancar_padrao(lancar, grupo.id, ana, [ana])

    assert despesa.data == HOJE


def test_data_informada_e_mantida(lancar, grupo, ana):
    despesa = lancar_padrao(
        lancar, grupo.id, ana, [ana], data=date(2026, 10, 1)
    )

    assert despesa.data == date(2026, 10, 1)


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


def test_membro_da_divisao_de_fora_do_grupo_e_rejeitado(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, 999])


def test_membro_de_outro_grupo_e_rejeitado(grupos, lancar, grupo, ana):
    outro = CriarGrupo(grupos).executar("Viagem")
    intruso = AdicionarMembro(grupos).executar(outro.id, "Eva")

    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [ana, intruso.id])


def test_divisao_sem_membros_e_rejeitada(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_padrao(lancar, grupo.id, ana, [])


def test_membro_repetido_na_divisao_e_rejeitado(
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


def lancar_por_valores(lancar, grupo_id, pagador_id, cotas, **mudancas):
    return lancar_padrao(
        lancar,
        grupo_id,
        pagador_id,
        [],
        divisao=DivisaoPorValores(cotas=tuple(cotas)),
        **mudancas,
    )


def test_divisao_por_valores_usa_as_cotas_informadas(
    despesas, lancar, grupo, ana, bruno, carla
):
    despesa = lancar_por_valores(
        lancar, grupo.id, ana, [(bruno, 6000), (carla, 2500), (ana, 1500)]
    )

    assert cotas_em_centavos(despesa) == [
        (bruno, 6000),
        (carla, 2500),
        (ana, 1500),
    ]
    assert despesas.listar_por_grupo(grupo.id) == [despesa]


@pytest.mark.parametrize(
    "valores", [(6000, 2500, 1499), (6000, 2500, 1501)]
)
def test_cotas_que_nao_somam_o_valor_da_despesa_sao_rejeitadas(
    lancar, grupo, ana, bruno, carla, valores
):
    cotas = list(zip([bruno, carla, ana], valores))

    with pytest.raises(RegraDeDominioViolada):
        lancar_por_valores(lancar, grupo.id, ana, cotas)


@pytest.mark.parametrize("cota_de_carla", [0, -500])
def test_cota_zero_ou_negativa_e_rejeitada(
    lancar, grupo, ana, bruno, carla, cota_de_carla
):
    cotas = [(bruno, 10000 - cota_de_carla), (carla, cota_de_carla)]

    with pytest.raises(RegraDeDominioViolada):
        lancar_por_valores(lancar, grupo.id, ana, cotas)


def test_membro_repetido_nas_cotas_e_rejeitado(lancar, grupo, ana, bruno):
    with pytest.raises(RegraDeDominioViolada):
        lancar_por_valores(
            lancar, grupo.id, ana, [(bruno, 5000), (bruno, 5000)]
        )


def test_membro_das_cotas_de_fora_do_grupo_e_rejeitado(
    lancar, grupo, ana, bruno
):
    with pytest.raises(RegraDeDominioViolada):
        lancar_por_valores(lancar, grupo.id, ana, [(bruno, 5000), (999, 5000)])


def test_divisao_por_valores_sem_cotas_e_rejeitada(lancar, grupo, ana):
    with pytest.raises(RegraDeDominioViolada):
        lancar_por_valores(lancar, grupo.id, ana, [])
