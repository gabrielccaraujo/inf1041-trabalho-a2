from flask import Blueprint, jsonify

from app.routes.requisicao import (
    corpo_json,
    inteiro_obrigatorio,
    opcao_obrigatoria,
    texto_obrigatorio,
)
from domain.meio import Meio
from domain.vaquinha import Contribuicao, Vaquinha
from use_cases.contribuir import Contribuir
from use_cases.criar_vaquinha import CriarVaquinha
from use_cases.encerrar_vaquinha import EncerrarVaquinha
from use_cases.listar_vaquinhas import ListarVaquinhas


def contribuicao_json(contribuicao: Contribuicao) -> dict:
    return {
        "membro_id": contribuicao.membro_id,
        "valor_centavos": contribuicao.valor.centavos,
        "meio": contribuicao.meio.value,
        "data": contribuicao.data.isoformat(),
    }


def vaquinha_json(vaquinha: Vaquinha) -> dict:
    return {
        "id": vaquinha.id,
        "titulo": vaquinha.titulo,
        "descricao": vaquinha.descricao,
        "meta_centavos": vaquinha.meta.centavos,
        "beneficiario_id": vaquinha.beneficiario_id,
        "status": "encerrada" if vaquinha.encerrada else "aberta",
        "total_arrecadado_centavos": vaquinha.total_arrecadado().centavos,
        "contribuicoes": [
            contribuicao_json(c) for c in vaquinha.contribuicoes
        ],
    }


def create_vaquinha_blueprint(
    criar_vaquinha: CriarVaquinha,
    contribuir: Contribuir,
    encerrar_vaquinha: EncerrarVaquinha,
    listar_vaquinhas: ListarVaquinhas,
) -> Blueprint:
    bp = Blueprint(
        "vaquinhas",
        __name__,
        url_prefix="/api/grupos/<int:grupo_id>/vaquinhas",
    )

    @bp.post("")
    def criar(grupo_id: int):
        dados = corpo_json()
        vaquinha = criar_vaquinha.executar(
            grupo_id,
            titulo=texto_obrigatorio(dados, "titulo"),
            descricao=texto_obrigatorio(dados, "descricao"),
            meta_centavos=inteiro_obrigatorio(dados, "meta_centavos"),
            beneficiario_id=inteiro_obrigatorio(dados, "beneficiario_id"),
        )
        return jsonify(vaquinha_json(vaquinha)), 201

    @bp.get("")
    def listar(grupo_id: int):
        return jsonify(
            [vaquinha_json(v) for v in listar_vaquinhas.executar(grupo_id)]
        )

    @bp.post("/<int:vaquinha_id>/contribuicoes")
    def contribuir_na_vaquinha(grupo_id: int, vaquinha_id: int):
        dados = corpo_json()
        contribuicao = contribuir.executar(
            grupo_id,
            vaquinha_id,
            membro_id=inteiro_obrigatorio(dados, "membro_id"),
            valor_centavos=inteiro_obrigatorio(dados, "valor_centavos"),
            meio=opcao_obrigatoria(dados, "meio", Meio),
        )
        return jsonify(contribuicao_json(contribuicao)), 201

    @bp.post("/<int:vaquinha_id>/encerrar")
    def encerrar(grupo_id: int, vaquinha_id: int):
        vaquinha = encerrar_vaquinha.executar(grupo_id, vaquinha_id)
        return jsonify(vaquinha_json(vaquinha))

    return bp
