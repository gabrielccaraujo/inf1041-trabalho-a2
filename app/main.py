import os
from pathlib import Path

from flask import Flask, jsonify, request

from app.routes.api import api
from domain.rules import BusinessError
from infra.db.sqlite import SqliteDatabase
from infra.repositories.sqlite_repository import SqliteRepository
from use_cases.service import RachaiService


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        DATABASE_PATH=os.environ.get(
            "RACHAI_DATABASE",
            str(Path(__file__).resolve().parents[1] / "instance" / "rachai.sqlite3")),
        CORS_ORIGINS=os.environ.get(
            "RACHAI_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173").split(","),
    )
    if config:
        app.config.update(config)
    repository = SqliteRepository(SqliteDatabase(app.config["DATABASE_PATH"]))
    app.extensions["rachai_service"] = RachaiService(repository)
    app.register_blueprint(api)

    @app.errorhandler(BusinessError)
    def business_error(error):
        return jsonify({"error": {"code": error.code, "message": str(error)}}), error.status

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.after_request
    def cors(response):
        origin = request.headers.get("Origin")
        if origin in app.config["CORS_ORIGINS"]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        return response

    return app


if __name__ == "__main__":
    create_app().run(debug=False, port=5000)
