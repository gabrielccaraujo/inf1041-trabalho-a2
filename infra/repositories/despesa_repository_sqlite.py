import sqlite3
from datetime import date

from domain.despesa import Cota, Despesa, Divisao
from domain.valor import Valor
from infra.db.database import Database


class DespesaRepositorySqlite:
    def __init__(self, database: Database) -> None:
        self.database = database

    def adicionar(self, despesa: Despesa) -> Despesa:
        with self.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO despesas "
                "(grupo_id, descricao, valor_centavos, pagador_id, data) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    despesa.grupo_id,
                    despesa.descricao,
                    despesa.valor.centavos,
                    despesa.pagador_id,
                    despesa.data.isoformat(),
                ),
            )
            despesa.id = cursor.lastrowid
            conn.executemany(
                "INSERT INTO cotas "
                "(despesa_id, posicao, membro_id, valor_centavos) "
                "VALUES (?, ?, ?, ?)",
                [
                    (despesa.id, posicao, c.membro_id, c.valor.centavos)
                    for posicao, c in enumerate(despesa.cotas)
                ],
            )
        return despesa

    def listar_por_grupo(self, grupo_id: int) -> list[Despesa]:
        with self.database.transaction() as conn:
            linhas = conn.execute(
                "SELECT * FROM despesas WHERE grupo_id = ? ORDER BY id",
                (grupo_id,),
            ).fetchall()
            return [self._para_despesa(conn, linha) for linha in linhas]

    @staticmethod
    def _para_despesa(conn: sqlite3.Connection, linha: sqlite3.Row) -> Despesa:
        cotas = conn.execute(
            "SELECT membro_id, valor_centavos FROM cotas "
            "WHERE despesa_id = ? ORDER BY posicao",
            (linha["id"],),
        ).fetchall()
        valor = Valor(linha["valor_centavos"])
        return Despesa(
            id=linha["id"],
            grupo_id=linha["grupo_id"],
            descricao=linha["descricao"],
            valor=valor,
            pagador_id=linha["pagador_id"],
            data=date.fromisoformat(linha["data"]),
            divisao=Divisao(
                valor,
                tuple(
                    Cota(c["membro_id"], Valor(c["valor_centavos"]))
                    for c in cotas
                )
            ),
        )
