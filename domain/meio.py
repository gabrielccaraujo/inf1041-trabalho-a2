from enum import Enum


class Meio(Enum):
    """Forma declarada de um Pagamento ou Contribuicao (ADR 0007)."""

    PIX = "pix"
    DINHEIRO = "dinheiro"
    OUTRO = "outro"
