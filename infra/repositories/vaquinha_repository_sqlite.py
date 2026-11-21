import sqlite3
from datetime import date
from typing import Optional

from domain.meio import Meio
from domain.valor import Valor
from domain.vaquinha import Contribuicao, Vaquinha
from infra.db.database import Database


class VaquinhaRepositorySqlite:
    def __init__(self, database: Database) -> None:
        self.database = database

    def adicionar(self, vaquinha: Vaquinha) -> Vaquinha:
        with self.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO vaquinhas (grupo_id, titulo, descricao, "
                "meta_centavos, beneficiario_id, encerrada) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    vaquinha.grupo_id,
                    vaquinha.titulo,
                    vaquinha.descricao,
                    vaquinha.meta.centavos,
                    vaquinha.beneficiario_id,
                    int(vaquinha.encerrada),
                ),
            )
            vaquinha.id = cursor.lastrowid
            self._inserir_contribuicoes_novas(conn, vaquinha)
        return vaquinha

    def salvar(self, vaquinha: Vaquinha) -> Vaquinha:
        with self.database.transaction() as conn:
            conn.execute(
                "UPDATE vaquinhas SET encerrada = ? WHERE id = ?",
                (int(vaquinha.encerrada), vaquinha.id),
            )
            self._inserir_contribuicoes_novas(conn, vaquinha)
        return vaquinha

    def buscar(self, vaquinha_id: int) -> Optional[Vaquinha]:
        with self.database.transaction() as conn:
            linha = conn.execute(
                "SELECT * FROM vaquinhas WHERE id = ?", (vaquinha_id,)
            ).fetchone()
            return self._para_vaquinha(conn, linha) if linha else None

    def listar_por_grupo(self, grupo_id: int) -> list[Vaquinha]:
        with self.database.transaction() as conn:
            linhas = conn.execute(
                "SELECT * FROM vaquinhas WHERE grupo_id = ? ORDER BY id",
                (grupo_id,),
            ).fetchall()
            return [self._para_vaquinha(conn, linha) for linha in linhas]

    @staticmethod
    def _inserir_contribuicoes_novas(
        conn: sqlite3.Connection, vaquinha: Vaquinha
    ) -> None:
        """Contribuicoes sao append-only: grava so as que faltam no banco."""
        gravadas = conn.execute(
            "SELECT COUNT(*) FROM contribuicoes WHERE vaquinha_id = ?",
            (vaquinha.id,),
        ).fetchone()[0]
        conn.executemany(
            "INSERT INTO contribuicoes (vaquinha_id, posicao, membro_id, "
            "valor_centavos, meio, data) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    vaquinha.id,
                    posicao,
                    c.membro_id,
                    c.valor.centavos,
                    c.meio.value,
                    c.data.isoformat(),
                )
                for posicao, c in enumerate(vaquinha.contribuicoes)
                if posicao >= gravadas
            ],
        )

    @staticmethod
    def _para_vaquinha(
        conn: sqlite3.Connection, linha: sqlite3.Row
    ) -> Vaquinha:
        contribuicoes = conn.execute(
            "SELECT * FROM contribuicoes WHERE vaquinha_id = ? "
            "ORDER BY posicao",
            (linha["id"],),
        ).fetchall()
        return Vaquinha(
            id=linha["id"],
            grupo_id=linha["grupo_id"],
            titulo=linha["titulo"],
            descricao=linha["descricao"],
            meta=Valor(linha["meta_centavos"]),
            beneficiario_id=linha["beneficiario_id"],
            encerrada=bool(linha["encerrada"]),
            contribuicoes=[
                Contribuicao(
                    membro_id=c["membro_id"],
                    valor=Valor(c["valor_centavos"]),
                    meio=Meio(c["meio"]),
                    data=date.fromisoformat(c["data"]),
                )
                for c in contribuicoes
            ],
        )
