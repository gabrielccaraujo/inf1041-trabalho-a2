from domain.grupo import GrupoRepository
from domain.valor import Valor
from domain.vaquinha import Vaquinha, VaquinhaRepository
from use_cases.comum import garantir_membros_do_grupo, obter_grupo_ou_falhar


class CriarVaquinha:
    def __init__(
        self, grupos: GrupoRepository, vaquinhas: VaquinhaRepository
    ) -> None:
        self._grupos = grupos
        self._vaquinhas = vaquinhas

    def executar(
        self,
        grupo_id: int,
        titulo: str,
        descricao: str,
        meta_centavos: int,
        beneficiario_id: int,
    ) -> Vaquinha:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        garantir_membros_do_grupo(grupo, [beneficiario_id])
        vaquinha = Vaquinha(
            grupo_id=grupo.id,
            titulo=titulo,
            descricao=descricao,
            meta=Valor(meta_centavos),
            beneficiario_id=beneficiario_id,
        )
        return self._vaquinhas.adicionar(vaquinha)
