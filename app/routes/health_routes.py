from datetime import datetime, timezone
from typing import Callable

from flask import Blueprint, jsonify


def create_health_blueprint(check_database: Callable[[], bool]) -> Blueprint:
    """GET /api/health: informa se a API e o banco estao respondendo."""
    bp = Blueprint("health", __name__, url_prefix="/api")

    @bp.get("/health")
    def health():
        try:
            database_ok = check_database()
        except Exception:
            database_ok = False

        body = {
            "status": "ok" if database_ok else "degraded",
            "database": "ok" if database_ok else "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return jsonify(body), 200 if database_ok else 503

    return bp
