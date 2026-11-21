from flask import Blueprint, jsonify

from app.routes.requisicao import (
    corpo_json,
    inteiro_obrigatorio,
    opcao_obrigatoria,
    texto_obrigatorio,
    texto_opcional,
)
from domain.meio import Meio
from domain.vaquinha import Vaquinha
from use_cases.contribuir import Contribuir
from use_cases.criar_vaquinha import CriarVaquinha
from use_cases.encerrar_vaquinha import EncerrarVaquinha
from use_cases.listar_vaquinhas import ListarVaquinhas


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
            {
                "membro_id": c.membro_id,
                "valor_centavos": c.valor.centavos,
                "meio": c.meio.value,
                "data": c.data.isoformat(),
            }
            for c in vaquinha.contribuicoes
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
            descricao=texto_opcional(dados, "descricao") or "",
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
        vaquinha = contribuir.executar(
            grupo_id,
            vaquinha_id,
            membro_id=inteiro_obrigatorio(dados, "membro_id"),
            valor_centavos=inteiro_obrigatorio(dados, "valor_centavos"),
            meio=opcao_obrigatoria(dados, "meio", Meio),
        )
        return jsonify(vaquinha_json(vaquinha)), 201

    @bp.post("/<int:vaquinha_id>/encerrar")
    def encerrar(grupo_id: int, vaquinha_id: int):
        vaquinha = encerrar_vaquinha.executar(grupo_id, vaquinha_id)
        return jsonify(vaquinha_json(vaquinha))

    return bp
