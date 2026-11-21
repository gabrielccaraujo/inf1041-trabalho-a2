import sqlite3
from typing import Optional

from domain.grupo import Grupo, Membro
from infra.db.database import Database


class GrupoRepositorySqlite:
    def __init__(self, database: Database) -> None:
        self.database = database

    def adicionar(self, grupo: Grupo) -> Grupo:
        with self.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO grupos (nome) VALUES (?)", (grupo.nome,)
            )
            grupo.id = cursor.lastrowid
            self._inserir_membros_novos(conn, grupo)
        return grupo

    def salvar(self, grupo: Grupo) -> Grupo:
        with self.database.transaction() as conn:
            self._inserir_membros_novos(conn, grupo)
        return grupo

    @staticmethod
    def _inserir_membros_novos(conn: sqlite3.Connection, grupo: Grupo) -> None:
        for membro in grupo.membros:
            if membro.id is None:
                cursor = conn.execute(
                    "INSERT INTO membros (grupo_id, nome, chave_pix) "
                    "VALUES (?, ?, ?)",
                    (grupo.id, membro.nome, membro.chave_pix),
                )
                membro.id = cursor.lastrowid

    def buscar(self, grupo_id: int) -> Optional[Grupo]:
        with self.database.transaction() as conn:
            linha = conn.execute(
                "SELECT id, nome FROM grupos WHERE id = ?", (grupo_id,)
            ).fetchone()
            if linha is None:
                return None
            membros = conn.execute(
                "SELECT id, nome, chave_pix FROM membros "
                "WHERE grupo_id = ? ORDER BY id",
                (grupo_id,),
            ).fetchall()
        return Grupo(
            id=linha["id"],
            nome=linha["nome"],
            membros=[
                Membro(id=m["id"], nome=m["nome"], chave_pix=m["chave_pix"])
                for m in membros
            ],
        )
