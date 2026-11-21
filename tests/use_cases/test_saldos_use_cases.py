from datetime import date

import pytest

from domain.erros import NaoEncontrado
from tests.use_cases.fakes import (
    DespesaRepositoryEmMemoria,
    GrupoRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_saldos import ConsultarSaldos
from use_cases.criar_grupo import CriarGrupo
from use_cases.lancar_despesa import (
    DivisaoIgualitaria,
    DivisaoPorValores,
    LancarDespesa,
)


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
def membros(grupo):
    return [m.id for m in grupo.membros]


@pytest.fixture
def lancar(grupos, despesas, grupo):
    use_case = LancarDespesa(
        grupos, despesas, relogio=lambda: date(2026, 1, 1)
    )

    def lancar(pagador_id, valor_centavos, divisao):
        use_case.executar(
            grupo.id,
            descricao="Despesa",
            valor_centavos=valor_centavos,
            pagador_id=pagador_id,
            divisao=divisao,
        )

    return lancar


@pytest.fixture
def consultar(grupos, despesas, grupo):
    return lambda: ConsultarSaldos(grupos, despesas).executar(grupo.id)


def saldos_em_centavos(resultado):
    return [(s.membro_id, s.valor.centavos) for s in resultado.saldos]


def transferencias_em_centavos(resultado):
    return [
        (t.de_membro_id, t.para_membro_id, t.valor.centavos)
        for t in resultado.transferencias
    ]


def saldos_apos_transferencias(resultado):
    """Aplica as Transferencias sugeridas como se fossem pagas."""
    saldos = dict(saldos_em_centavos(resultado))
    for de, para, centavos in transferencias_em_centavos(resultado):
        saldos[de] += centavos
        saldos[para] -= centavos
    return saldos


def test_grupo_sem_despesas_tem_saldos_zero_e_nenhuma_transferencia(
    consultar, membros
):
    resultado = consultar()

    assert saldos_em_centavos(resultado) == [(m, 0) for m in membros]
    assert resultado.transferencias == []


def test_saldo_e_o_que_pagou_menos_as_cotas_com_sobra_de_centavos(
    lancar, consultar, membros
):
    ana, bruno, carla, davi = membros
    lancar(ana, 10000, DivisaoIgualitaria(membros=(ana, bruno, carla)))

    resultado = consultar()

    assert saldos_em_centavos(resultado) == [
        (ana, 6666),
        (bruno, -3333),
        (carla, -3333),
        (davi, 0),
    ]
    assert transferencias_em_centavos(resultado) == [
        (bruno, ana, 3333),
        (carla, ana, 3333),
    ]


@pytest.fixture
def historico_misto(lancar, membros):
    """Igualitaria com sobra, por valores e Pagador fora da Divisao."""
    ana, bruno, carla, davi = membros
    lancar(ana, 10000, DivisaoIgualitaria(membros=(ana, bruno, carla)))
    lancar(bruno, 9000, DivisaoPorValores(cotas=((carla, 5000), (davi, 4000))))
    lancar(davi, 101, DivisaoIgualitaria(membros=(ana, bruno, carla, davi)))


def test_saldos_refletem_as_cotas_da_divisao_por_valores(
    historico_misto, consultar, membros
):
    ana, bruno, carla, davi = membros

    resultado = consultar()

    assert saldos_em_centavos(resultado) == [
        (ana, 6640),
        (bruno, 5642),
        (carla, -8358),
        (davi, -3924),
    ]
    assert sum(centavos for _, centavos in saldos_em_centavos(resultado)) == 0


def test_transferencias_sugeridas_pelo_maior_devedor_e_maior_credor(
    historico_misto, consultar, membros
):
    ana, bruno, carla, davi = membros

    resultado = consultar()

    assert transferencias_em_centavos(resultado) == [
        (carla, ana, 6640),
        (davi, bruno, 3924),
        (carla, bruno, 1718),
    ]


def test_transferencias_sugeridas_zeram_os_saldos_em_no_maximo_n_menos_1(
    historico_misto, consultar, membros
):
    resultado = consultar()

    assert set(saldos_apos_transferencias(resultado).values()) == {0}
    assert len(resultado.transferencias) <= len(membros) - 1


def test_mesmo_historico_gera_as_mesmas_transferencias(
    historico_misto, consultar
):
    assert consultar() == consultar()


def test_empate_entre_devedores_segue_a_ordem_dos_membros(
    lancar, consultar, membros
):
    ana, bruno, carla, davi = membros
    lancar(davi, 300, DivisaoIgualitaria(membros=(carla, bruno, ana)))

    resultado = consultar()

    assert transferencias_em_centavos(resultado) == [
        (ana, davi, 100),
        (bruno, davi, 100),
        (carla, davi, 100),
    ]


def test_consultar_saldos_de_grupo_inexistente(grupos, despesas):
    with pytest.raises(NaoEncontrado):
        ConsultarSaldos(grupos, despesas).executar(99)
