from domain.grupo import Grupo, GrupoRepository


class CriarGrupo:
    def __init__(self, grupos: GrupoRepository) -> None:
        self._grupos = grupos

    def executar(self, nome: str) -> Grupo:
        return self._grupos.adicionar(Grupo(nome=nome))
