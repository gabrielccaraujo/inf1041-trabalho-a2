from datetime import date

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
        for nome in ["Ana", "Bruno"]
    ]
    return grupo_id, ids


def pagar(client, grupo_id, de, para, valor, meio="pix"):
    return client.post(
        f"/api/grupos/{grupo_id}/pagamentos",
        json={
            "de_membro_id": de,
            "para_membro_id": para,
            "valor_centavos": valor,
            "meio": meio,
        },
    )


def saldos(client, grupo_id):
    corpo = client.get(f"/api/grupos/{grupo_id}/saldos").get_json()
    return [s["saldo_centavos"] for s in corpo["saldos"]], corpo[
        "transferencias"
    ]


def test_despesa_saldo_pagamento_saldo_zerado(client, grupo):
    grupo_id, (ana, bruno) = grupo
    client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json={
            "descricao": "Mercado",
            "valor_centavos": 8000,
            "pagador_id": ana,
            "divisao": {"modo": "igualitaria", "membros": [ana, bruno]},
        },
    )
    assert saldos(client, grupo_id) == (
        [4000, -4000],
        [
            {
                "de_membro_id": bruno,
                "para_membro_id": ana,
                "valor_centavos": 4000,
            }
        ],
    )

    resposta = pagar(client, grupo_id, bruno, ana, 4000)

    assert resposta.status_code == 201
    pagamento = resposta.get_json()
    assert isinstance(pagamento.pop("id"), int)
    esperado = {
        "de_membro_id": bruno,
        "para_membro_id": ana,
        "valor_centavos": 4000,
        "meio": "pix",
        "data": date.today().isoformat(),
    }
    assert pagamento == esperado
    assert saldos(client, grupo_id) == ([0, 0], [])
    listados = client.get(f"/api/grupos/{grupo_id}/pagamentos").get_json()
    assert [{k: v for k, v in p.items() if k != "id"} for p in listados] == [
        esperado
    ]


@pytest.mark.parametrize(
    "caso", ["mesmo-membro", "valor-zero", "valor-negativo", "de-fora"]
)
def test_regra_de_pagamento_violada_responde_422(client, grupo, caso):
    grupo_id, (ana, bruno) = grupo
    de, para, valor = {
        "mesmo-membro": (ana, ana, 100),
        "valor-zero": (bruno, ana, 0),
        "valor-negativo": (bruno, ana, -100),
        "de-fora": (999, ana, 100),
    }[caso]

    resposta = pagar(client, grupo_id, de, para, valor)

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "corpo",
    [
        {"de_membro_id": 2, "para_membro_id": 1, "valor_centavos": 100,
         "meio": "boleto"},
        {"de_membro_id": 2, "para_membro_id": 1, "valor_centavos": 100},
        {"de_membro_id": 2, "para_membro_id": 1, "valor_centavos": "100",
         "meio": "pix"},
        {"para_membro_id": 1, "valor_centavos": 100, "meio": "pix"},
    ],
)
def test_corpo_de_pagamento_malformado_responde_400(client, grupo, corpo):
    grupo_id, _ = grupo

    resposta = client.post(f"/api/grupos/{grupo_id}/pagamentos", json=corpo)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_pagamentos_de_grupo_inexistente_responde_404(client):
    assert client.get("/api/grupos/99/pagamentos").status_code == 404
    resposta = pagar(client, 99, 2, 1, 100)
    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()
