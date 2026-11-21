"""Traducao de erros para respostas {"erro": "mensagem"} (ADR 0008).

400: corpo malformado ou campo ausente ou de tipo errado (validado na rota).
404: recurso inexistente. 422: regra de dominio violada. Os erros HTTP do
proprio Flask (rota inexistente, metodo nao permitido) seguem o mesmo formato.
"""

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from domain.erros import NaoEncontrado, RegraDeDominioViolada


class RequisicaoInvalida(Exception):
    """O corpo da requisicao nao tem o formato esperado."""


def registrar_tratadores_de_erro(app: Flask) -> None:
    @app.errorhandler(RequisicaoInvalida)
    def requisicao_invalida(erro):
        return jsonify({"erro": str(erro)}), 400

    @app.errorhandler(NaoEncontrado)
    def nao_encontrado(erro):
        return jsonify({"erro": str(erro)}), 404

    @app.errorhandler(RegraDeDominioViolada)
    def regra_violada(erro):
        return jsonify({"erro": str(erro)}), 422

    @app.errorhandler(HTTPException)
    def erro_http(erro):
        return jsonify({"erro": erro.description}), erro.code
