from flask import Blueprint, jsonify

from domain.reconhecimento import Apoiador
from use_cases.consultar_apoiadores import ConsultarApoiadores


def apoiador_json(apoiador: Apoiador) -> dict:
    return {
        "membro_id": apoiador.membro_id,
        "nome": apoiador.nome,
        "total_contribuido_centavos": apoiador.total_contribuido.centavos,
        "vaquinhas_apoiadas": apoiador.vaquinhas_apoiadas,
    }


def create_apoiador_blueprint(
    consultar_apoiadores: ConsultarApoiadores,
) -> Blueprint:
    bp = Blueprint(
        "apoiadores",
        __name__,
        url_prefix="/api/grupos/<int:grupo_id>/apoiadores",
    )

    @bp.get("")
    def consultar(grupo_id: int):
        return jsonify(
            [apoiador_json(a) for a in consultar_apoiadores.executar(grupo_id)]
        )

    return bp
