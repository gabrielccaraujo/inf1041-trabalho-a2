from flask import Flask

from app.routes.health_routes import create_health_blueprint
from app.routes.task_routes import create_task_blueprint
from infra.db.database import DEFAULT_DB_PATH, Database
from infra.repositories.task_repository_sqlite import TaskRepositorySqlite
from use_cases.task_use_case import TaskUseCase


def create_app(db_path=DEFAULT_DB_PATH) -> Flask:
    """Composicao: liga infra -> casos de uso -> rotas."""
    app = Flask(__name__)

    database = Database(db_path)
    database.init_schema()

    repository = TaskRepositorySqlite(database)
    use_case = TaskUseCase(repository)
    app.register_blueprint(create_task_blueprint(use_case))
    app.register_blueprint(create_health_blueprint(database.ping))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
