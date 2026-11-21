from flask import Blueprint, jsonify

from app.routes.erros import corpo_json, texto_obrigatorio, texto_opcional
from domain.grupo import Grupo, Membro
from use_cases.adicionar_membro import AdicionarMembro
from use_cases.consultar_grupo import ConsultarGrupo
from use_cases.criar_grupo import CriarGrupo


def membro_json(membro: Membro) -> dict:
    return {
        "id": membro.id,
        "nome": membro.nome,
        "chave_pix": membro.chave_pix,
    }


def grupo_json(grupo: Grupo) -> dict:
    return {
        "id": grupo.id,
        "nome": grupo.nome,
        "membros": [membro_json(m) for m in grupo.membros],
    }


def create_grupo_blueprint(
    criar_grupo: CriarGrupo,
    adicionar_membro: AdicionarMembro,
    consultar_grupo: ConsultarGrupo,
) -> Blueprint:
    bp = Blueprint("grupos", __name__, url_prefix="/api/grupos")

    @bp.post("")
    def criar():
        dados = corpo_json()
        grupo = criar_grupo.executar(texto_obrigatorio(dados, "nome"))
        return jsonify(grupo_json(grupo)), 201

    @bp.get("/<int:grupo_id>")
    def consultar(grupo_id: int):
        return jsonify(grupo_json(consultar_grupo.executar(grupo_id)))

    @bp.post("/<int:grupo_id>/membros")
    def adicionar(grupo_id: int):
        dados = corpo_json()
        membro = adicionar_membro.executar(
            grupo_id,
            texto_obrigatorio(dados, "nome"),
            chave_pix=texto_opcional(dados, "chave_pix"),
        )
        return jsonify(membro_json(membro)), 201

    return bp
