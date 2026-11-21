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
        for nome in ["Ana", "Bruno", "Carla"]
    ]
    return grupo_id, ids


def criar_vaquinha(client, grupo_id, beneficiario, /, **mudancas):
    corpo = {
        "titulo": "Geladeira",
        "descricao": "A antiga quebrou",
        "meta_centavos": 10000,
        "beneficiario_id": beneficiario,
    }
    corpo.update(mudancas)
    return client.post(f"/api/grupos/{grupo_id}/vaquinhas", json=corpo)


def contribuir(client, grupo_id, vaquinha_id, membro_id, valor, meio="pix"):
    return client.post(
        f"/api/grupos/{grupo_id}/vaquinhas/{vaquinha_id}/contribuicoes",
        json={"membro_id": membro_id, "valor_centavos": valor, "meio": meio},
    )


def test_ciclo_da_vaquinha_persiste_ida_e_volta(client, grupo):
    grupo_id, (ana, bruno, carla) = grupo

    criada = criar_vaquinha(client, grupo_id, ana)
    assert criada.status_code == 201
    vaquinha = criada.get_json()
    assert vaquinha["status"] == "aberta"
    assert vaquinha["total_arrecadado_centavos"] == 0

    resposta = contribuir(client, grupo_id, vaquinha["id"], bruno, 7000)
    assert resposta.status_code == 201
    assert resposta.get_json() == {
        "membro_id": bruno,
        "valor_centavos": 7000,
        "meio": "pix",
        "data": date.today().isoformat(),
    }
    contribuir(client, grupo_id, vaquinha["id"], carla, 5000, "dinheiro")

    encerrada = client.post(
        f"/api/grupos/{grupo_id}/vaquinhas/{vaquinha['id']}/encerrar"
    )
    assert encerrada.status_code == 200
    assert encerrada.get_json()["status"] == "encerrada"

    listadas = client.get(f"/api/grupos/{grupo_id}/vaquinhas").get_json()
    hoje = date.today().isoformat()
    assert listadas == [
        {
            "id": vaquinha["id"],
            "titulo": "Geladeira",
            "descricao": "A antiga quebrou",
            "meta_centavos": 10000,
            "beneficiario_id": ana,
            "status": "encerrada",
            "total_arrecadado_centavos": 12000,
            "contribuicoes": [
                {
                    "membro_id": bruno,
                    "valor_centavos": 7000,
                    "meio": "pix",
                    "data": hoje,
                },
                {
                    "membro_id": carla,
                    "valor_centavos": 5000,
                    "meio": "dinheiro",
                    "data": hoje,
                },
            ],
        }
    ]


def test_contribuicoes_nao_alteram_os_saldos(client, grupo):
    grupo_id, (ana, bruno, carla) = grupo
    client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json={
            "descricao": "Luz",
            "valor_centavos": 9000,
            "pagador_id": ana,
            "divisao": {"modo": "igualitaria", "membros": [ana, bruno, carla]},
        },
    )
    antes = client.get(f"/api/grupos/{grupo_id}/saldos").get_json()
    vaquinha_id = criar_vaquinha(client, grupo_id, ana).get_json()["id"]

    contribuir(client, grupo_id, vaquinha_id, bruno, 5000)
    contribuir(client, grupo_id, vaquinha_id, carla, 2500)

    depois = client.get(f"/api/grupos/{grupo_id}/saldos").get_json()
    assert depois == antes
    assert [s["saldo_centavos"] for s in antes["saldos"]] == [
        6000,
        -3000,
        -3000,
    ]


@pytest.mark.parametrize(
    "mudancas",
    [{"meta_centavos": 0}, {"titulo": " "}, {"beneficiario_id": 999}],
)
def test_regra_de_vaquinha_violada_responde_422(client, grupo, mudancas):
    grupo_id, (ana, _, _) = grupo

    resposta = criar_vaquinha(client, grupo_id, ana, **mudancas)

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


def test_regras_de_contribuicao_e_encerramento_respondem_422(client, grupo):
    grupo_id, (ana, bruno, _) = grupo
    vaquinha_id = criar_vaquinha(client, grupo_id, ana).get_json()["id"]
    encerrar = f"/api/grupos/{grupo_id}/vaquinhas/{vaquinha_id}/encerrar"

    assert contribuir(client, grupo_id, vaquinha_id, ana, 100).status_code == (
        422
    )
    assert contribuir(client, grupo_id, vaquinha_id, bruno, 0).status_code == (
        422
    )
    assert client.post(encerrar).status_code == 200
    assert contribuir(
        client, grupo_id, vaquinha_id, bruno, 100
    ).status_code == 422
    assert client.post(encerrar).status_code == 422


@pytest.mark.parametrize(
    "corpo",
    [
        {"titulo": "G", "descricao": "", "meta_centavos": "10",
         "beneficiario_id": 1},
        {"titulo": "G", "descricao": "", "meta_centavos": 10},
        {"descricao": "", "meta_centavos": 10, "beneficiario_id": 1},
        {"titulo": "G", "meta_centavos": 10, "beneficiario_id": 1},
        {"titulo": "G", "descricao": 5, "meta_centavos": 10,
         "beneficiario_id": 1},
    ],
)
def test_corpo_de_vaquinha_malformado_responde_400(client, grupo, corpo):
    grupo_id, _ = grupo

    resposta = client.post(f"/api/grupos/{grupo_id}/vaquinhas", json=corpo)

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "corpo",
    [
        {"membro_id": 2, "valor_centavos": 100},
        {"membro_id": 2, "valor_centavos": 100, "meio": "cheque"},
        {"membro_id": 2, "valor_centavos": "100", "meio": "pix"},
        {"valor_centavos": 100, "meio": "pix"},
    ],
)
def test_corpo_de_contribuicao_malformado_responde_400(client, grupo, corpo):
    grupo_id, (ana, _, _) = grupo
    vaquinha_id = criar_vaquinha(client, grupo_id, ana).get_json()["id"]

    resposta = client.post(
        f"/api/grupos/{grupo_id}/vaquinhas/{vaquinha_id}/contribuicoes",
        json=corpo,
    )

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_vaquinha_ou_grupo_inexistente_responde_404(client, grupo):
    grupo_id, (ana, bruno, _) = grupo

    assert contribuir(client, grupo_id, 99, bruno, 100).status_code == 404
    assert client.post(
        f"/api/grupos/{grupo_id}/vaquinhas/99/encerrar"
    ).status_code == 404
    assert client.get("/api/grupos/99/vaquinhas").status_code == 404
    resposta = criar_vaquinha(client, 99, ana)
    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()
