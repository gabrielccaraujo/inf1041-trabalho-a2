from flask import Flask

from app.routes.erros import registrar_tratadores_de_erro
from app.routes.grupo_routes import create_grupo_blueprint
from app.routes.health_routes import create_health_blueprint
from infra.db.database import DEFAULT_DB_PATH, Database
from infra.repositories.grupo_repository_sqlite import GrupoRepositorySqlite
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_grupo import ConsultarGrupo
from use_cases.criar_grupo import CriarGrupo


def create_app(db_path=DEFAULT_DB_PATH) -> Flask:
    """Composicao: liga infra -> casos de uso -> rotas."""
    app = Flask(__name__)
    registrar_tratadores_de_erro(app)

    database = Database(db_path)
    database.init_schema()

    grupos = GrupoRepositorySqlite(database)
    app.register_blueprint(
        create_grupo_blueprint(
            CriarGrupo(grupos),
            AdicionarMembro(grupos),
            ConsultarGrupo(grupos),
        )
    )
    app.register_blueprint(create_health_blueprint(database.ping))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
