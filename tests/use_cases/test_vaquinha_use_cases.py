from datetime import date

import pytest

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from domain.meio import Meio
from tests.use_cases.fakes import (
    DespesaRepositoryEmMemoria,
    GrupoRepositoryEmMemoria,
    VaquinhaRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.criar_grupo import CriarGrupo
from use_cases.consultar_saldos import ConsultarSaldos
from use_cases.contribuir import Contribuir
from use_cases.criar_vaquinha import CriarVaquinha
from use_cases.encerrar_vaquinha import EncerrarVaquinha
from use_cases.lancar_despesa import DivisaoIgualitaria, LancarDespesa
from use_cases.listar_vaquinhas import ListarVaquinhas


HOJE = date(2026, 11, 21)


@pytest.fixture
def grupos():
    return GrupoRepositoryEmMemoria()


@pytest.fixture
def vaquinhas():
    return VaquinhaRepositoryEmMemoria()


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
def criar(grupos, vaquinhas, grupo, membros):
    use_case = CriarVaquinha(grupos, vaquinhas)

    def criar(**mudancas):
        dados = dict(
            titulo="Geladeira nova",
            descricao="A antiga quebrou",
            meta_centavos=150000,
            beneficiario_id=membros[0],
        )
        dados.update(mudancas)
        return use_case.executar(grupo.id, **dados)

    return criar


def test_criar_vaquinha_aberta_com_meta_e_beneficiario(criar, membros):
    vaquinha = criar()

    assert vaquinha.id is not None
    assert vaquinha.titulo == "Geladeira nova"
    assert vaquinha.descricao == "A antiga quebrou"
    assert vaquinha.meta.centavos == 150000
    assert vaquinha.beneficiario_id == membros[0]
    assert vaquinha.encerrada is False
    assert vaquinha.total_arrecadado().centavos == 0
    assert vaquinha.contribuicoes == ()


@pytest.mark.parametrize("meta_centavos", [0, -1])
def test_vaquinha_com_meta_zero_ou_negativa_e_rejeitada(
    criar, meta_centavos
):
    with pytest.raises(RegraDeDominioViolada):
        criar(meta_centavos=meta_centavos)


@pytest.mark.parametrize("titulo", ["", "  "])
def test_vaquinha_sem_titulo_e_rejeitada(criar, titulo):
    with pytest.raises(RegraDeDominioViolada):
        criar(titulo=titulo)


def test_beneficiario_de_fora_do_grupo_e_rejeitado(criar):
    with pytest.raises(RegraDeDominioViolada):
        criar(beneficiario_id=999)


def test_criar_vaquinha_em_grupo_inexistente_nao_e_encontrado(
    grupos, vaquinhas, membros
):
    with pytest.raises(NaoEncontrado):
        CriarVaquinha(grupos, vaquinhas).executar(
            99,
            titulo="Geladeira",
            descricao="",
            meta_centavos=100,
            beneficiario_id=membros[0],
        )


@pytest.fixture
def vaquinha(criar):
    return criar(meta_centavos=10000)


@pytest.fixture
def contribuir(grupos, vaquinhas, grupo):
    use_case = Contribuir(grupos, vaquinhas, relogio=lambda: HOJE)

    def contribuir(vaquinha_id, membro_id, valor_centavos, meio=Meio.PIX):
        return use_case.executar(
            grupo.id, vaquinha_id, membro_id, valor_centavos, meio
        )

    return contribuir


def contribuicoes_resumidas(vaquinha):
    return [
        (c.membro_id, c.valor.centavos, c.meio, c.data)
        for c in vaquinha.contribuicoes
    ]


def test_contribuir_aumenta_o_total_arrecadado(
    contribuir, vaquinhas, vaquinha, membros
):
    _, bruno, carla = membros

    contribuir(vaquinha.id, bruno, 3000, Meio.PIX)
    contribuicao = contribuir(vaquinha.id, carla, 2000, Meio.DINHEIRO)

    assert (contribuicao.membro_id, contribuicao.valor.centavos) == (
        carla,
        2000,
    )
    atualizada = vaquinhas.buscar(vaquinha.id)

    assert atualizada.total_arrecadado().centavos == 5000
    assert contribuicoes_resumidas(atualizada) == [
        (bruno, 3000, Meio.PIX, HOJE),
        (carla, 2000, Meio.DINHEIRO, HOJE),
    ]


def test_contribuir_acima_da_meta_e_permitido_e_nao_encerra(
    contribuir, vaquinhas, vaquinha, membros
):
    _, bruno, carla = membros

    contribuir(vaquinha.id, bruno, 10000)
    contribuir(vaquinha.id, carla, 500)
    atualizada = vaquinhas.buscar(vaquinha.id)

    assert atualizada.total_arrecadado().centavos == 10500
    assert atualizada.encerrada is False


def test_beneficiario_nao_contribui_na_propria_vaquinha(
    contribuir, vaquinha, membros
):
    with pytest.raises(RegraDeDominioViolada):
        contribuir(vaquinha.id, membros[0], 1000)


def test_contribuicao_de_membro_de_fora_do_grupo_e_rejeitada(
    contribuir, vaquinha
):
    with pytest.raises(RegraDeDominioViolada):
        contribuir(vaquinha.id, 999, 1000)


@pytest.mark.parametrize("valor_centavos", [0, -100])
def test_contribuicao_com_valor_zero_ou_negativo_e_rejeitada(
    contribuir, vaquinha, membros, valor_centavos
):
    with pytest.raises(RegraDeDominioViolada):
        contribuir(vaquinha.id, membros[1], valor_centavos)


def test_contribuicao_rejeitada_nao_entra_na_vaquinha(
    contribuir, vaquinhas, vaquinha, membros
):
    with pytest.raises(RegraDeDominioViolada):
        contribuir(vaquinha.id, membros[0], 1000)

    assert vaquinhas.buscar(vaquinha.id).contribuicoes == ()


def test_contribuir_em_vaquinha_inexistente_nao_e_encontrada(
    contribuir, membros
):
    with pytest.raises(NaoEncontrado):
        contribuir(99, membros[1], 1000)


def test_vaquinha_de_outro_grupo_nao_e_encontrada(
    grupos, vaquinhas, contribuir, membros
):
    outro = CriarGrupo(grupos).executar("Viagem")
    eva = AdicionarMembro(grupos).executar(outro.id, "Eva")
    alheia = CriarVaquinha(grupos, vaquinhas).executar(
        outro.id,
        titulo="Passagem",
        descricao="",
        meta_centavos=100,
        beneficiario_id=eva.id,
    )

    with pytest.raises(NaoEncontrado):
        contribuir(alheia.id, membros[1], 1000)


@pytest.fixture
def encerrar(grupos, vaquinhas, grupo):
    use_case = EncerrarVaquinha(grupos, vaquinhas)
    return lambda vaquinha_id: use_case.executar(grupo.id, vaquinha_id)


def test_encerrar_vaquinha_muda_o_status_para_encerrada(
    encerrar, vaquinhas, vaquinha
):
    encerrada = encerrar(vaquinha.id)

    assert encerrada.encerrada is True
    assert vaquinhas.buscar(vaquinha.id).encerrada is True


def test_contribuir_em_vaquinha_encerrada_e_rejeitado(
    encerrar, contribuir, vaquinha, membros
):
    encerrar(vaquinha.id)

    with pytest.raises(RegraDeDominioViolada):
        contribuir(vaquinha.id, membros[1], 1000)


def test_encerrar_vaquinha_ja_encerrada_e_rejeitado(encerrar, vaquinha):
    encerrar(vaquinha.id)

    with pytest.raises(RegraDeDominioViolada):
        encerrar(vaquinha.id)


def test_encerrar_vaquinha_inexistente_nao_e_encontrada(encerrar):
    with pytest.raises(NaoEncontrado):
        encerrar(99)


def test_listar_vaquinhas_do_grupo_com_total_status_e_contribuicoes(
    grupos, vaquinhas, criar, contribuir, encerrar, membros
):
    _, bruno, carla = membros
    geladeira = criar(titulo="Geladeira", meta_centavos=10000)
    criar(titulo="Sofa", meta_centavos=50000, beneficiario_id=bruno)
    contribuir(geladeira.id, bruno, 4000)
    contribuir(geladeira.id, carla, 1000)
    encerrar(geladeira.id)

    listadas = ListarVaquinhas(grupos, vaquinhas).executar(geladeira.grupo_id)

    assert [
        (
            v.titulo,
            v.meta.centavos,
            v.total_arrecadado().centavos,
            v.encerrada,
            [(c.membro_id, c.valor.centavos) for c in v.contribuicoes],
        )
        for v in listadas
    ] == [
        ("Geladeira", 10000, 5000, True, [(bruno, 4000), (carla, 1000)]),
        ("Sofa", 50000, 0, False, []),
    ]


def test_listar_vaquinhas_de_grupo_inexistente_nao_e_encontrado(
    grupos, vaquinhas
):
    with pytest.raises(NaoEncontrado):
        ListarVaquinhas(grupos, vaquinhas).executar(99)


def test_contribuicoes_nao_alteram_os_saldos(
    grupos, grupo, contribuir, vaquinha, membros
):
    ana, bruno, carla = membros
    despesas = DespesaRepositoryEmMemoria()
    LancarDespesa(grupos, despesas, relogio=lambda: HOJE).executar(
        grupo.id,
        descricao="Luz",
        valor_centavos=9000,
        pagador_id=ana,
        divisao=DivisaoIgualitaria(membros=(ana, bruno, carla)),
    )
    consultar = ConsultarSaldos(grupos, despesas)
    antes = consultar.executar(grupo.id)

    contribuir(vaquinha.id, bruno, 5000)
    contribuir(vaquinha.id, carla, 2500)

    assert consultar.executar(grupo.id) == antes
    assert [s.valor.centavos for s in antes.saldos] == [6000, -3000, -3000]
