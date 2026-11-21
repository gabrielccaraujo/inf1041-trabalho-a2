"""Leitura e validacao de formato do corpo JSON (erros viram 400)."""

from typing import Any, Optional

from flask import request

from app.routes.erros import RequisicaoInvalida


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
