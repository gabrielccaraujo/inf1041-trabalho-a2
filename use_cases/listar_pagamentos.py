from domain.grupo import GrupoRepository
from domain.pagamento import Pagamento, PagamentoRepository
from use_cases.comum import obter_grupo_ou_falhar


class ListarPagamentos:
    def __init__(
        self, grupos: GrupoRepository, pagamentos: PagamentoRepository
    ) -> None:
        self._grupos = grupos
        self._pagamentos = pagamentos

    def executar(self, grupo_id: int) -> list[Pagamento]:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        return self._pagamentos.listar_por_grupo(grupo.id)
