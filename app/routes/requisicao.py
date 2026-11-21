"""Leitura e validacao de formato do corpo JSON (erros viram 400)."""

from datetime import date
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


def inteiro_obrigatorio(dados: dict[str, Any], campo: str) -> int:
    valor = dados.get(campo)
    if not _e_inteiro(valor):
        raise RequisicaoInvalida(f"O campo '{campo}' e obrigatorio e inteiro.")
    return valor


def lista_de_inteiros(dados: dict[str, Any], campo: str) -> list[int]:
    valor = dados.get(campo)
    if not isinstance(valor, list) or not all(map(_e_inteiro, valor)):
        raise RequisicaoInvalida(
            f"O campo '{campo}' deve ser uma lista de inteiros."
        )
    return valor


def objeto_obrigatorio(dados: dict[str, Any], campo: str) -> dict[str, Any]:
    valor = dados.get(campo)
    if not isinstance(valor, dict):
        raise RequisicaoInvalida(f"O campo '{campo}' deve ser um objeto.")
    return valor


def data_opcional(dados: dict[str, Any], campo: str) -> Optional[date]:
    valor = texto_opcional(dados, campo)
    if valor is None:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise RequisicaoInvalida(
            f"O campo '{campo}' deve ser uma data AAAA-MM-DD."
        ) from None


def _e_inteiro(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)
