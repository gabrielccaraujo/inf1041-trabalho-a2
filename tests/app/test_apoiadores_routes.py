import pytest

from app.main import create_app


@pytest.fixture
def client():
    return create_app(":memory:").test_client()


@pytest.fixture
def grupo(client):
    resposta = client.post("/api/grupos", json={"nome": "Rep"})
    grupo_id = resposta.get_json()["id"]
    ids = [
        client.post(
            f"/api/grupos/{grupo_id}/membros", json={"nome": nome}
        ).get_json()["id"]
        for nome in ["Ana", "Bruno", "Carla"]
    ]
    return grupo_id, ids


def test_ranking_conta_so_contribuicoes(client, grupo):
    grupo_id, (ana, bruno, carla) = grupo
    client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json={
            "descricao": "Mercado",
            "valor_centavos": 90000,
            "pagador_id": carla,
            "divisao": {"modo": "igualitaria", "membros": [ana, bruno]},
        },
    )
    client.post(
        f"/api/grupos/{grupo_id}/pagamentos",
        json={
            "de_membro_id": carla,
            "para_membro_id": ana,
            "valor_centavos": 50000,
            "meio": "pix",
        },
    )
    vaquinha_id = client.post(
        f"/api/grupos/{grupo_id}/vaquinhas",
        json={
            "titulo": "Geladeira",
            "descricao": "",
            "meta_centavos": 10000,
            "beneficiario_id": ana,
        },
    ).get_json()["id"]
    client.post(
        f"/api/grupos/{grupo_id}/vaquinhas/{vaquinha_id}/contribuicoes",
        json={"membro_id": bruno, "valor_centavos": 1500, "meio": "pix"},
    )

    resposta = client.get(f"/api/grupos/{grupo_id}/apoiadores")

    assert resposta.status_code == 200
    assert resposta.get_json() == [
        {
            "membro_id": bruno,
            "nome": "Bruno",
            "total_contribuido_centavos": 1500,
            "vaquinhas_apoiadas": 1,
        }
    ]


def test_grupo_sem_contribuicoes_devolve_lista_vazia(client, grupo):
    grupo_id, _ = grupo

    resposta = client.get(f"/api/grupos/{grupo_id}/apoiadores")

    assert resposta.status_code == 200
    assert resposta.get_json() == []


def test_apoiadores_de_grupo_inexistente_responde_404(client):
    resposta = client.get("/api/grupos/99/apoiadores")

    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()
