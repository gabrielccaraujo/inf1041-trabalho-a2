from datetime import date

from domain.meio import Meio
from domain.pagamento import Pagamento
from domain.valor import Valor
from infra.db.database import Database


class PagamentoRepositorySqlite:
    def __init__(self, database: Database) -> None:
        self.database = database

    def adicionar(self, pagamento: Pagamento) -> Pagamento:
        with self.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO pagamentos (grupo_id, de_membro_id, "
                "para_membro_id, valor_centavos, meio, data) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    pagamento.grupo_id,
                    pagamento.de_membro_id,
                    pagamento.para_membro_id,
                    pagamento.valor.centavos,
                    pagamento.meio.value,
                    pagamento.data.isoformat(),
                ),
            )
            pagamento.id = cursor.lastrowid
        return pagamento

    def listar_por_grupo(self, grupo_id: int) -> list[Pagamento]:
        with self.database.transaction() as conn:
            linhas = conn.execute(
                "SELECT * FROM pagamentos WHERE grupo_id = ? ORDER BY id",
                (grupo_id,),
            ).fetchall()
        return [
            Pagamento(
                id=linha["id"],
                grupo_id=linha["grupo_id"],
                de_membro_id=linha["de_membro_id"],
                para_membro_id=linha["para_membro_id"],
                valor=Valor(linha["valor_centavos"]),
                meio=Meio(linha["meio"]),
                data=date.fromisoformat(linha["data"]),
            )
            for linha in linhas
        ]
