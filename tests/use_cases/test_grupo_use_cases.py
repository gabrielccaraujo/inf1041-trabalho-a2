import pytest

from domain.erros import NaoEncontrado, RegraDeDominioViolada
from tests.use_cases.fakes import GrupoRepositoryEmMemoria
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_grupo import ConsultarGrupo
from use_cases.criar_grupo import CriarGrupo


@pytest.fixture
def grupos():
    return GrupoRepositoryEmMemoria()


def test_criar_grupo_com_nome(grupos):
    grupo = CriarGrupo(grupos).executar("  Republica Azul  ")

    assert grupo.id is not None
    assert grupo.nome == "Republica Azul"
    assert grupo.membros == []


@pytest.mark.parametrize("nome", ["", "   "])
def test_grupo_de_nome_vazio_e_rejeitado(grupos, nome):
    with pytest.raises(RegraDeDominioViolada):
        CriarGrupo(grupos).executar(nome)


@pytest.fixture
def grupo(grupos):
    return CriarGrupo(grupos).executar("Republica Azul")


def test_adicionar_membro_com_chave_pix(grupos, grupo):
    membro = AdicionarMembro(grupos).executar(
        grupo.id, "Ana", chave_pix="ana@email.com"
    )

    assert membro.id is not None
    assert membro.nome == "Ana"
    assert membro.chave_pix == "ana@email.com"


def test_adicionar_membro_sem_chave_pix(grupos, grupo):
    membro = AdicionarMembro(grupos).executar(grupo.id, "Bruno")

    assert membro.chave_pix is None


@pytest.mark.parametrize("repetido", ["Ana", "  ana  ", "ANA"])
def test_membro_com_nome_repetido_no_grupo_e_rejeitado(
    grupos, grupo, repetido
):
    AdicionarMembro(grupos).executar(grupo.id, "Ana")

    with pytest.raises(RegraDeDominioViolada):
        AdicionarMembro(grupos).executar(grupo.id, repetido)


def test_mesmo_nome_em_grupos_distintos_e_permitido(grupos, grupo):
    outro = CriarGrupo(grupos).executar("Viagem")
    AdicionarMembro(grupos).executar(grupo.id, "Ana")

    membro = AdicionarMembro(grupos).executar(outro.id, "Ana")

    assert membro.nome == "Ana"


@pytest.mark.parametrize("nome", ["", "   "])
def test_membro_de_nome_vazio_e_rejeitado(grupos, grupo, nome):
    with pytest.raises(RegraDeDominioViolada):
        AdicionarMembro(grupos).executar(grupo.id, nome)


def test_chave_pix_e_aparada(grupos, grupo):
    membro = AdicionarMembro(grupos).executar(
        grupo.id, "Ana", chave_pix="  ana@email.com  "
    )

    assert membro.chave_pix == "ana@email.com"


def test_chave_pix_em_branco_vira_ausente(grupos, grupo):
    membro = AdicionarMembro(grupos).executar(grupo.id, "Ana", chave_pix="  ")

    assert membro.chave_pix is None


def test_chave_pix_com_77_caracteres_e_aceita(grupos, grupo):
    membro = AdicionarMembro(grupos).executar(
        grupo.id, "Ana", chave_pix="a" * 77
    )

    assert len(membro.chave_pix) == 77


def test_chave_pix_acima_de_77_caracteres_e_rejeitada(grupos, grupo):
    with pytest.raises(RegraDeDominioViolada):
        AdicionarMembro(grupos).executar(grupo.id, "Ana", chave_pix="a" * 78)


def test_membro_rejeitado_nao_entra_no_grupo(grupos, grupo):
    AdicionarMembro(grupos).executar(grupo.id, "Ana")
    with pytest.raises(RegraDeDominioViolada):
        AdicionarMembro(grupos).executar(grupo.id, "Ana")

    assert [m.nome for m in grupos.buscar(grupo.id).membros] == ["Ana"]


def test_adicionar_membro_em_grupo_inexistente(grupos):
    with pytest.raises(NaoEncontrado):
        AdicionarMembro(grupos).executar(99, "Ana")


def test_consultar_grupo_traz_membros_e_chaves_pix(grupos, grupo):
    AdicionarMembro(grupos).executar(grupo.id, "Ana", chave_pix="ana@pix")
    AdicionarMembro(grupos).executar(grupo.id, "Bruno")

    consultado = ConsultarGrupo(grupos).executar(grupo.id)

    assert consultado.nome == "Republica Azul"
    assert [(m.nome, m.chave_pix) for m in consultado.membros] == [
        ("Ana", "ana@pix"),
        ("Bruno", None),
    ]


def test_consultar_grupo_inexistente(grupos):
    with pytest.raises(NaoEncontrado):
        ConsultarGrupo(grupos).executar(99)
