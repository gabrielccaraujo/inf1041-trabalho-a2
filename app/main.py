from datetime import date

from flask import Flask

from app.routes.despesa_routes import create_despesa_blueprint
from app.routes.erros import registrar_tratadores_de_erro
from app.routes.grupo_routes import create_grupo_blueprint
from app.routes.health_routes import create_health_blueprint
from app.routes.pagamento_routes import create_pagamento_blueprint
from app.routes.saldo_routes import create_saldo_blueprint
from app.routes.vaquinha_routes import create_vaquinha_blueprint
from infra.db.database import DEFAULT_DB_PATH, Database
from infra.repositories.despesa_repository_sqlite import (
    DespesaRepositorySqlite,
)
from infra.repositories.grupo_repository_sqlite import GrupoRepositorySqlite
from infra.repositories.pagamento_repository_sqlite import (
    PagamentoRepositorySqlite,
)
from infra.repositories.vaquinha_repository_sqlite import (
    VaquinhaRepositorySqlite,
)
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_grupo import ConsultarGrupo
from use_cases.consultar_saldos import ConsultarSaldos
from use_cases.contribuir import Contribuir
from use_cases.criar_grupo import CriarGrupo
from use_cases.criar_vaquinha import CriarVaquinha
from use_cases.encerrar_vaquinha import EncerrarVaquinha
from use_cases.lancar_despesa import LancarDespesa
from use_cases.listar_despesas import ListarDespesas
from use_cases.listar_pagamentos import ListarPagamentos
from use_cases.listar_vaquinhas import ListarVaquinhas
from use_cases.registrar_pagamento import RegistrarPagamento


def create_app(db_path=DEFAULT_DB_PATH) -> Flask:
    """Composicao: liga infra -> casos de uso -> rotas."""
    app = Flask(__name__)
    registrar_tratadores_de_erro(app)

    database = Database(db_path)
    database.init_schema()

    grupos = GrupoRepositorySqlite(database)
    despesas = DespesaRepositorySqlite(database)
    pagamentos = PagamentoRepositorySqlite(database)
    vaquinhas = VaquinhaRepositorySqlite(database)
    app.register_blueprint(
        create_grupo_blueprint(
            CriarGrupo(grupos),
            AdicionarMembro(grupos),
            ConsultarGrupo(grupos),
        )
    )
    app.register_blueprint(
        create_despesa_blueprint(
            LancarDespesa(grupos, despesas, relogio=date.today),
            ListarDespesas(grupos, despesas),
        )
    )
    app.register_blueprint(
        create_pagamento_blueprint(
            RegistrarPagamento(grupos, pagamentos, relogio=date.today),
            ListarPagamentos(grupos, pagamentos),
        )
    )
    app.register_blueprint(
        create_saldo_blueprint(ConsultarSaldos(grupos, despesas, pagamentos))
    )
    app.register_blueprint(
        create_vaquinha_blueprint(
            CriarVaquinha(grupos, vaquinhas),
            Contribuir(grupos, vaquinhas, relogio=date.today),
            EncerrarVaquinha(grupos, vaquinhas),
            ListarVaquinhas(grupos, vaquinhas),
        )
    )
    app.register_blueprint(create_health_blueprint(database.ping))

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
