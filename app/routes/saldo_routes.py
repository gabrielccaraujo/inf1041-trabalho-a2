from flask import Blueprint, jsonify

from domain.saldos import SaldosDoGrupo
from use_cases.consultar_saldos import ConsultarSaldos


def saldos_json(resultado: SaldosDoGrupo) -> dict:
    return {
        "saldos": [
            {"membro_id": s.membro_id, "saldo_centavos": s.valor.centavos}
            for s in resultado.saldos
        ],
        "transferencias": [
            {
                "de_membro_id": t.de_membro_id,
                "para_membro_id": t.para_membro_id,
                "valor_centavos": t.valor.centavos,
            }
            for t in resultado.transferencias
        ],
    }


def create_saldo_blueprint(consultar_saldos: ConsultarSaldos) -> Blueprint:
    bp = Blueprint(
        "saldos", __name__, url_prefix="/api/grupos/<int:grupo_id>/saldos"
    )

    @bp.get("")
    def consultar(grupo_id: int):
        return jsonify(saldos_json(consultar_saldos.executar(grupo_id)))

    return bp
