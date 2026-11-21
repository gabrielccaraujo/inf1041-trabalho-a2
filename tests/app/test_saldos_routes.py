import pytest

from app.main import create_app


@pytest.fixture
def client():
    return create_app(":memory:").test_client()


def test_saldos_e_transferencias_de_despesas_lancadas_pela_api(client):
    resposta = client.post("/api/grupos", json={"nome": "Rep"})
    grupo_id = resposta.get_json()["id"]
    ana, bruno, carla = [
        client.post(
            f"/api/grupos/{grupo_id}/membros", json={"nome": nome}
        ).get_json()["id"]
        for nome in ["Ana", "Bruno", "Carla"]
    ]
    client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json={
            "descricao": "Conta de luz",
            "valor_centavos": 10000,
            "pagador_id": ana,
            "divisao": {"modo": "igualitaria", "membros": [ana, bruno]},
        },
    )

    resposta = client.get(f"/api/grupos/{grupo_id}/saldos")

    assert resposta.status_code == 200
    assert resposta.get_json() == {
        "saldos": [
            {"membro_id": ana, "saldo_centavos": 5000},
            {"membro_id": bruno, "saldo_centavos": -5000},
            {"membro_id": carla, "saldo_centavos": 0},
        ],
        "transferencias": [
            {
                "de_membro_id": bruno,
                "para_membro_id": ana,
                "valor_centavos": 5000,
            }
        ],
    }


def test_saldos_de_grupo_inexistente_responde_404(client):
    resposta = client.get("/api/grupos/99/saldos")

    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()
