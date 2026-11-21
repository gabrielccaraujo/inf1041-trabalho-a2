from datetime import date

import pytest

from domain.erros import NaoEncontrado
from domain.meio import Meio
from tests.use_cases.fakes import (
    GrupoRepositoryEmMemoria,
    VaquinhaRepositoryEmMemoria,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_apoiadores import ConsultarApoiadores
from use_cases.contribuir import Contribuir
from use_cases.criar_grupo import CriarGrupo
from use_cases.criar_vaquinha import CriarVaquinha
from use_cases.encerrar_vaquinha import EncerrarVaquinha


@pytest.fixture
def grupos():
    return GrupoRepositoryEmMemoria()


@pytest.fixture
def vaquinhas():
    return VaquinhaRepositoryEmMemoria()


@pytest.fixture
def grupo(grupos):
    """Membros fora da ordem alfabetica: id nao coincide com o nome."""
    grupo = CriarGrupo(grupos).executar("Rep")
    for nome in ["Davi", "Carla", "Bruno", "Ana", "Eva"]:
        AdicionarMembro(grupos).executar(grupo.id, nome)
    return grupos.buscar(grupo.id)


@pytest.fixture
def membro(grupo):
    """Id do Membro pelo nome."""
    ids = {m.nome: m.id for m in grupo.membros}

    def membro(nome):
        return ids[nome]

    return membro


@pytest.fixture
def abrir(grupos, vaquinhas, grupo, membro):
    use_case = CriarVaquinha(grupos, vaquinhas)

    def abrir(beneficiario):
        return use_case.executar(
            grupo.id,
            titulo=f"Ajuda para {beneficiario}",
            descricao="",
            meta_centavos=10000,
            beneficiario_id=membro(beneficiario),
        ).id

    return abrir


@pytest.fixture
def contribuir(grupos, vaquinhas, grupo, membro):
    use_case = Contribuir(grupos, vaquinhas, relogio=lambda: date(2026, 1, 1))

    def contribuir(vaquinha_id, nome, valor_centavos):
        use_case.executar(
            grupo.id, vaquinha_id, membro(nome), valor_centavos, Meio.PIX
        )

    return contribuir


@pytest.fixture
def consultar(grupos, vaquinhas, grupo):
    use_case = ConsultarApoiadores(grupos, vaquinhas)
    return lambda: use_case.executar(grupo.id)


def ranking(apoiadores):
    return [
        (a.nome, a.total_contribuido.centavos, a.vaquinhas_apoiadas)
        for a in apoiadores
    ]


def test_ranking_por_total_depois_vaquinhas_apoiadas_depois_nome(
    abrir, contribuir, consultar
):
    da_ana, do_bruno, da_eva = abrir("Ana"), abrir("Bruno"), abrir("Eva")
    contribuir(da_ana, "Bruno", 3000)
    contribuir(da_ana, "Carla", 1000)
    contribuir(do_bruno, "Carla", 2000)
    contribuir(da_eva, "Davi", 1500)
    contribuir(da_eva, "Davi", 1500)
    contribuir(do_bruno, "Ana", 500)

    assert ranking(consultar()) == [
        ("Carla", 3000, 2),
        ("Bruno", 3000, 1),
        ("Davi", 3000, 1),
        ("Ana", 500, 1),
    ]


def test_membro_que_nunca_contribuiu_nao_aparece(abrir, contribuir, consultar):
    contribuir(abrir("Ana"), "Bruno", 1000)

    assert [a.nome for a in consultar()] == ["Bruno"]


def test_contribuicoes_em_vaquinha_encerrada_continuam_contando(
    grupos, vaquinhas, grupo, abrir, contribuir, consultar
):
    da_ana = abrir("Ana")
    contribuir(da_ana, "Bruno", 1000)
    EncerrarVaquinha(grupos, vaquinhas).executar(grupo.id, da_ana)

    assert ranking(consultar()) == [("Bruno", 1000, 1)]


def test_varias_contribuicoes_na_mesma_vaquinha_contam_uma_vez(
    abrir, contribuir, consultar
):
    da_ana = abrir("Ana")
    contribuir(da_ana, "Bruno", 1000)
    contribuir(da_ana, "Bruno", 2000)
    contribuir(abrir("Carla"), "Bruno", 500)

    assert ranking(consultar()) == [("Bruno", 3500, 2)]


def test_grupo_sem_contribuicoes_nao_tem_apoiadores(abrir, consultar):
    abrir("Ana")

    assert consultar() == []


def test_apoiadores_de_grupo_inexistente_nao_e_encontrado(grupos, vaquinhas):
    with pytest.raises(NaoEncontrado):
        ConsultarApoiadores(grupos, vaquinhas).executar(99)
