from flask import Blueprint, jsonify

from app.routes.requisicao import (
    corpo_json,
    inteiro_obrigatorio,
    opcao_obrigatoria,
)
from domain.meio import Meio
from domain.pagamento import Pagamento
from use_cases.listar_pagamentos import ListarPagamentos
from use_cases.registrar_pagamento import RegistrarPagamento


def pagamento_json(pagamento: Pagamento) -> dict:
    return {
        "id": pagamento.id,
        "de_membro_id": pagamento.de_membro_id,
        "para_membro_id": pagamento.para_membro_id,
        "valor_centavos": pagamento.valor.centavos,
        "meio": pagamento.meio.value,
        "data": pagamento.data.isoformat(),
    }


def create_pagamento_blueprint(
    registrar_pagamento: RegistrarPagamento,
    listar_pagamentos: ListarPagamentos,
) -> Blueprint:
    bp = Blueprint(
        "pagamentos",
        __name__,
        url_prefix="/api/grupos/<int:grupo_id>/pagamentos",
    )

    @bp.post("")
    def registrar(grupo_id: int):
        dados = corpo_json()
        pagamento = registrar_pagamento.executar(
            grupo_id,
            de_membro_id=inteiro_obrigatorio(dados, "de_membro_id"),
            para_membro_id=inteiro_obrigatorio(dados, "para_membro_id"),
            valor_centavos=inteiro_obrigatorio(dados, "valor_centavos"),
            meio=opcao_obrigatoria(dados, "meio", Meio),
        )
        return jsonify(pagamento_json(pagamento)), 201

    @bp.get("")
    def listar(grupo_id: int):
        return jsonify(
            [pagamento_json(p) for p in listar_pagamentos.executar(grupo_id)]
        )

    return bp
