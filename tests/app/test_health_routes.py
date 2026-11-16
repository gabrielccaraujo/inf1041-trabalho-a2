from flask import Flask

from app.main import create_app
from app.routes.health_routes import create_health_blueprint


def test_health_ok():
    response = create_app(":memory:").test_client().get("/api/health")
    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert "timestamp" in body


def test_health_com_banco_fora():
    def banco_quebrado():
        raise RuntimeError("sem conexao")

    app = Flask(__name__)
    app.register_blueprint(create_health_blueprint(banco_quebrado))
    response = app.test_client().get("/api/health")
    assert response.status_code == 503
    assert response.get_json()["status"] == "degraded"
