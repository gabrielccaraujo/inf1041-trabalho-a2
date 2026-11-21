from datetime import date
from typing import Callable

from domain.grupo import GrupoRepository
from domain.meio import Meio
from domain.pagamento import Pagamento, PagamentoRepository
from domain.valor import Valor
from use_cases.comum import garantir_membros_do_grupo, obter_grupo_ou_falhar


class RegistrarPagamento:
    def __init__(
        self,
        grupos: GrupoRepository,
        pagamentos: PagamentoRepository,
        relogio: Callable[[], date],
    ) -> None:
        self._grupos = grupos
        self._pagamentos = pagamentos
        self._relogio = relogio

    def executar(
        self,
        grupo_id: int,
        de_membro_id: int,
        para_membro_id: int,
        valor_centavos: int,
        meio: Meio,
    ) -> Pagamento:
        grupo = obter_grupo_ou_falhar(self._grupos, grupo_id)
        garantir_membros_do_grupo(grupo, [de_membro_id, para_membro_id])
        pagamento = Pagamento(
            grupo_id=grupo.id,
            de_membro_id=de_membro_id,
            para_membro_id=para_membro_id,
            valor=Valor(valor_centavos),
            meio=meio,
            data=self._relogio(),
        )
        return self._pagamentos.adicionar(pagamento)
