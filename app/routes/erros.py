"""Traducao de erros para respostas {"erro": "mensagem"} (ADR 0008).

400: corpo malformado ou campo ausente ou de tipo errado (validado na rota).
404: recurso inexistente. 422: regra de dominio violada.
"""

from typing import Any, Optional

from flask import Flask, jsonify, request

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


def corpo_json() -> dict[str, Any]:
    """Le o corpo como objeto JSON ou falha com RequisicaoInvalida."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise RequisicaoInvalida("O corpo deve ser um objeto JSON.")
    return dados


def texto_obrigatorio(dados: dict[str, Any], campo: str) -> str:
    valor = dados.get(campo)
    if not isinstance(valor, str):
        raise RequisicaoInvalida(f"O campo '{campo}' e obrigatorio e textual.")
    return valor


def texto_opcional(dados: dict[str, Any], campo: str) -> Optional[str]:
    valor = dados.get(campo)
    if valor is not None and not isinstance(valor, str):
        raise RequisicaoInvalida(f"O campo '{campo}' deve ser textual.")
    return valor
