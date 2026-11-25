from typing import Callable

from flask import Blueprint, jsonify

from app.routes.erros import RequisicaoInvalida
from app.routes.requisicao import (
    corpo_json,
    data_opcional,
    inteiro_obrigatorio,
    lista_de_inteiros,
    lista_de_objetos,
    objeto_obrigatorio,
    texto_obrigatorio,
)
from domain.despesa import Despesa
from use_cases.lancar_despesa import (
    DivisaoIgualitaria,
    DivisaoPorValores,
    LancarDespesa,
    PedidoDeDivisao,
)
from use_cases.listar_despesas import ListarDespesas


def despesa_json(despesa: Despesa) -> dict:
    return {
        "id": despesa.id,
        "descricao": despesa.descricao,
        "valor_centavos": despesa.valor.centavos,
        "pagador_id": despesa.pagador_id,
        "data": despesa.data.isoformat(),
        "cotas": [
            {"membro_id": c.membro_id, "valor_centavos": c.valor.centavos}
            for c in despesa.cotas
        ],
    }


def ler_divisao_igualitaria(divisao: dict) -> DivisaoIgualitaria:
    return DivisaoIgualitaria(
        membros=tuple(lista_de_inteiros(divisao, "membros"))
    )


def ler_divisao_por_valores(divisao: dict) -> DivisaoPorValores:
    return DivisaoPorValores(
        cotas=tuple(
            (
                inteiro_obrigatorio(cota, "membro_id"),
                inteiro_obrigatorio(cota, "valor_centavos"),
            )
            for cota in lista_de_objetos(divisao, "cotas")
        )
    )


LEITORES_DE_DIVISAO: dict[str, Callable[[dict], PedidoDeDivisao]] = {
    "igualitaria": ler_divisao_igualitaria,
    "por_valores": ler_divisao_por_valores,
}


def ler_divisao(dados: dict) -> PedidoDeDivisao:
    divisao = objeto_obrigatorio(dados, "divisao")
    modo = texto_obrigatorio(divisao, "modo")
    leitor = LEITORES_DE_DIVISAO.get(modo)
    if leitor is None:
        raise RequisicaoInvalida(
            "O modo da Divisao deve ser um de: "
            + ", ".join(LEITORES_DE_DIVISAO)
            + "."
        )
    return leitor(divisao)


def create_despesa_blueprint(
    lancar_despesa: LancarDespesa, listar_despesas: ListarDespesas
) -> Blueprint:
    bp = Blueprint(
        "despesas", __name__, url_prefix="/api/grupos/<int:grupo_id>/despesas"
    )

    @bp.post("")
    def lancar(grupo_id: int):
        dados = corpo_json()
        despesa = lancar_despesa.executar(
            grupo_id,
            descricao=texto_obrigatorio(dados, "descricao"),
            valor_centavos=inteiro_obrigatorio(dados, "valor_centavos"),
            pagador_id=inteiro_obrigatorio(dados, "pagador_id"),
            divisao=ler_divisao(dados),
            data=data_opcional(dados, "data"),
        )
        return jsonify(despesa_json(despesa)), 201

    @bp.get("")
    def listar(grupo_id: int):
        return jsonify(
            [despesa_json(d) for d in listar_despesas.executar(grupo_id)]
        )

    return bp
