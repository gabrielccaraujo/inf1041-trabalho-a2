import pytest

from app.main import create_app


@pytest.fixture
def client():
    return create_app(":memory:").test_client()


def criar_grupo(client, nome="Republica Azul"):
    return client.post("/api/grupos", json={"nome": nome})


def test_criar_grupo_responde_201(client):
    resposta = criar_grupo(client)

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert corpo["nome"] == "Republica Azul"
    assert corpo["membros"] == []
    assert isinstance(corpo["id"], int)


def test_grupo_de_nome_vazio_responde_422(client):
    resposta = criar_grupo(client, nome="  ")

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


def test_grupo_e_membros_persistem_ida_e_volta(client):
    grupo_id = criar_grupo(client).get_json()["id"]
    resposta = client.post(
        f"/api/grupos/{grupo_id}/membros",
        json={"nome": "Ana", "chave_pix": "  ana@pix  "},
    )
    client.post(f"/api/grupos/{grupo_id}/membros", json={"nome": "Bruno"})

    assert resposta.status_code == 201
    ana = resposta.get_json()
    assert ana["nome"] == "Ana"
    assert ana["chave_pix"] == "ana@pix"

    grupo = client.get(f"/api/grupos/{grupo_id}").get_json()
    assert grupo["nome"] == "Republica Azul"
    assert grupo["membros"] == [
        {"id": ana["id"], "nome": "Ana", "chave_pix": "ana@pix"},
        {"id": grupo["membros"][1]["id"], "nome": "Bruno", "chave_pix": None},
    ]


def test_membro_com_nome_repetido_responde_422(client):
    grupo_id = criar_grupo(client).get_json()["id"]
    client.post(f"/api/grupos/{grupo_id}/membros", json={"nome": "Ana"})

    resposta = client.post(
        f"/api/grupos/{grupo_id}/membros", json={"nome": "Ana"}
    )

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


def test_chave_pix_longa_demais_responde_422(client):
    grupo_id = criar_grupo(client).get_json()["id"]

    resposta = client.post(
        f"/api/grupos/{grupo_id}/membros",
        json={"nome": "Ana", "chave_pix": "a" * 78},
    )

    assert resposta.status_code == 422


def test_consultar_grupo_inexistente_responde_404(client):
    resposta = client.get("/api/grupos/99")

    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()


def test_adicionar_membro_em_grupo_inexistente_responde_404(client):
    resposta = client.post("/api/grupos/99/membros", json={"nome": "Ana"})

    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "corpo",
    [None, {}, {"nome": 123}, ["Republica"], "texto"],
)
def test_criar_grupo_com_corpo_malformado_responde_400(client, corpo):
    resposta = client.post("/api/grupos", json=corpo)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_criar_grupo_com_json_invalido_responde_400(client):
    resposta = client.post(
        "/api/grupos", data="{nome", content_type="application/json"
    )

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "corpo",
    [{}, {"nome": None}, {"nome": "Ana", "chave_pix": 42}],
)
def test_adicionar_membro_com_corpo_malformado_responde_400(client, corpo):
    grupo_id = criar_grupo(client).get_json()["id"]

    resposta = client.post(f"/api/grupos/{grupo_id}/membros", json=corpo)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()
