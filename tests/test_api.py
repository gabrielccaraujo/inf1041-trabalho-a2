import pytest

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE_PATH": str(tmp_path / "test.sqlite3")})
    return app.test_client()


def register_and_login(client, name, email):
    response = client.post("/api/v1/auth/register", json={
        "name": name, "email": email, "password": "senhaforte1"})
    assert response.status_code == 201
    user = response.get_json()
    response = client.post("/api/v1/auth/login", json={
        "email": email, "password": "senhaforte1"})
    assert response.status_code == 200
    return user, {"Authorization": "Bearer " + response.get_json()["token"]}


def test_complete_group_expense_and_balance_flow(client):
    ana, ana_headers = register_and_login(client, "Ana", "ana@example.com")
    bruno, bruno_headers = register_and_login(client, "Bruno", "bruno@example.com")

    response = client.post("/api/v1/groups", headers=ana_headers,
                           json={"name": "Republica", "category": "Casa"})
    assert response.status_code == 201
    group = response.get_json()
    path = f"/api/v1/groups/{group['id']}"

    assert client.get(path, headers=bruno_headers).status_code == 403
    assert client.post("/api/v1/groups/join", headers=bruno_headers,
                       json={"invite_code": group["invite_code"]}).status_code == 200
    assert len(client.get(path, headers=bruno_headers).get_json()["members"]) == 2

    response = client.post(path + "/expenses", headers=ana_headers, json={
        "description": "Mercado", "amount": "10.01", "paid_by": ana["id"],
        "participant_ids": [ana["id"], bruno["id"]], "category": "Mercado",
        "occurred_on": "2026-11-16"})
    assert response.status_code == 201
    expense = response.get_json()
    assert expense["amount"] == "10.01"
    assert sum(int(s["amount"].replace(".", "")) for s in expense["splits"]) == 1001
    assert len(client.get(path + "/expenses", headers=bruno_headers)
               .get_json()["expenses"]) == 1

    balances = client.get(path + "/balances", headers=bruno_headers).get_json()["balances"]
    shares = {item["user_id"]: int(item["amount"].replace(".", ""))
              for item in expense["splits"]}
    assert {item["user_id"]: int(item["balance"].replace(".", ""))
            for item in balances} == {
        ana["id"]: 1001 - shares[ana["id"]],
        bruno["id"]: -shares[bruno["id"]]}


def test_authentication_and_bad_input(client):
    assert client.get("/api/v1/groups").status_code == 401
    user, headers = register_and_login(client, "Ana", "ana@example.com")
    assert client.post("/api/v1/auth/login", json={
        "email": user["email"], "password": "errada"}).status_code == 401
    assert client.post("/api/v1/groups", headers=headers,
                       json={"name": ""}).status_code == 400
    assert client.post("/api/v1/auth/register", json={
        "name": "Outra", "email": user["email"], "password": "senhaforte1"
    }).status_code == 409
