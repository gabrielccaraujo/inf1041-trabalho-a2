"""Excecoes de dominio. As rotas as traduzem para HTTP (ADR 0008)."""


class RegraDeDominioViolada(Exception):
    """Uma regra de negocio do RachAI foi violada."""


class NaoEncontrado(Exception):
    """O recurso pedido nao existe."""
