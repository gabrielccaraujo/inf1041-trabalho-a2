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


def corpo_despesa(pagador, membros=(), /, **mudancas):
    corpo = {
        "descricao": "Conta de luz",
        "valor_centavos": 10000,
        "pagador_id": pagador,
        "data": "2026-11-01",
        "divisao": {"modo": "igualitaria", "membros": list(membros)},
    }
    corpo.update(mudancas)
    return corpo


def test_lancar_despesa_responde_201_e_persiste_cotas(client, grupo):
    grupo_id, (ana, bruno, carla) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(ana, [ana, bruno, carla]),
    )

    assert resposta.status_code == 201
    esperado = {
        "descricao": "Conta de luz",
        "valor_centavos": 10000,
        "pagador_id": ana,
        "data": "2026-11-01",
        "cotas": [
            {"membro_id": ana, "valor_centavos": 3334},
            {"membro_id": bruno, "valor_centavos": 3333},
            {"membro_id": carla, "valor_centavos": 3333},
        ],
    }
    criada = resposta.get_json()
    assert isinstance(criada.pop("id"), int)
    assert criada == esperado

    listadas = client.get(f"/api/grupos/{grupo_id}/despesas").get_json()
    assert [{k: v for k, v in d.items() if k != "id"} for d in listadas] == [
        esperado
    ]


def test_sem_data_a_despesa_fica_com_a_data_de_hoje(client, grupo):
    grupo_id, (ana, bruno, _) = grupo
    corpo = corpo_despesa(ana, [ana, bruno])
    del corpo["data"]

    resposta = client.post(f"/api/grupos/{grupo_id}/despesas", json=corpo)

    assert resposta.status_code == 201
    assert resposta.get_json()["data"] == date.today().isoformat()


@pytest.mark.parametrize(
    "mudancas",
    [
        {"valor_centavos": 0},
        {"descricao": "  "},
        {"pagador_id": 999},
        {"divisao": {"modo": "igualitaria", "membros": []}},
    ],
)
def test_regra_de_despesa_violada_responde_422(client, grupo, mudancas):
    grupo_id, (ana, bruno, _) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(ana, [ana, bruno], **mudancas),
    )

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "mudancas",
    [
        {"valor_centavos": "100"},
        {"valor_centavos": 10.5},
        {"valor_centavos": True},
        {"pagador_id": None},
        {"descricao": None},
        {"data": "01/11/2026"},
        {"divisao": None},
        {"divisao": {"modo": "percentual", "membros": [1]}},
        {"divisao": {"modo": "igualitaria", "membros": "todos"}},
        {"divisao": {"modo": "igualitaria", "membros": ["1"]}},
    ],
)
def test_corpo_de_despesa_malformado_responde_400(client, grupo, mudancas):
    grupo_id, (ana, bruno, _) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(ana, [ana, bruno], **mudancas),
    )

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_despesas_de_grupo_inexistente_responde_404(client):
    assert client.get("/api/grupos/99/despesas").status_code == 404
    resposta = client.post(
        "/api/grupos/99/despesas", json=corpo_despesa(1, [1])
    )
    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()


def por_valores(*cotas):
    return {
        "modo": "por_valores",
        "cotas": [
            {"membro_id": membro_id, "valor_centavos": valor}
            for membro_id, valor in cotas
        ],
    }


def test_divisao_por_valores_responde_201_e_aparece_na_listagem(
    client, grupo
):
    grupo_id, (ana, bruno, carla) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(
            ana, divisao=por_valores((bruno, 7000), (carla, 3000))
        ),
    )

    assert resposta.status_code == 201
    cotas = [
        {"membro_id": bruno, "valor_centavos": 7000},
        {"membro_id": carla, "valor_centavos": 3000},
    ]
    assert resposta.get_json()["cotas"] == cotas
    listadas = client.get(f"/api/grupos/{grupo_id}/despesas").get_json()
    assert [d["cotas"] for d in listadas] == [cotas]


def test_cotas_que_nao_somam_o_valor_respondem_422(client, grupo):
    grupo_id, (ana, bruno, carla) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(
            ana, divisao=por_valores((bruno, 7000), (carla, 2000))
        ),
    )

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "cotas",
    [
        [(1, 10000), (2, 0)],
        [(1, 5000), (1, 5000)],
        [(1, 5000), (999, 5000)],
    ],
    ids=["cota-zero", "membro-repetido", "membro-de-fora"],
)
def test_regra_de_cotas_violada_responde_422(client, grupo, cotas):
    grupo_id, membros = grupo
    ids = {1: membros[1], 2: membros[2], 999: 999}
    cotas = [(ids[membro], valor) for membro, valor in cotas]

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(membros[0], divisao=por_valores(*cotas)),
    )

    assert resposta.status_code == 422
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize(
    "divisao",
    [
        {"modo": "por_valores"},
        {"modo": "por_valores", "cotas": "todas"},
        {"modo": "por_valores", "cotas": [7000]},
        {"modo": "por_valores", "cotas": [{"valor_centavos": 7000}]},
        {"modo": "por_valores", "cotas": [{"membro_id": 1}]},
        {
            "modo": "por_valores",
            "cotas": [{"membro_id": 1, "valor_centavos": "70"}],
        },
    ],
)
def test_cotas_malformadas_respondem_400(client, grupo, divisao):
    grupo_id, (ana, _, _) = grupo

    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(ana, divisao=divisao),
    )

    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


@pytest.mark.parametrize("modo", [[], {}, None, True, 1, "desconhecido"])
def test_modo_de_divisao_invalido_responde_400(client, grupo, modo):
    grupo_id, (ana, bruno, _) = grupo
    resposta = client.post(
        f"/api/grupos/{grupo_id}/despesas",
        json=corpo_despesa(
            ana,
            divisao={"modo": modo, "membros": [ana, bruno]},
        ),
    )
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()
    assert client.get(
        f"/api/grupos/{grupo_id}/despesas"
    ).get_json() == []
