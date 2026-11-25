import sqlite3
from datetime import date
from typing import Optional

from domain.erros import NaoEncontrado
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
            for posicao, contribuicao in enumerate(vaquinha.contribuicoes):
                self._inserir_contribuicao(
                    conn, vaquinha.id, posicao, contribuicao
                )
        return vaquinha

    def adicionar_contribuicao(
        self, vaquinha_id: int, contribuicao: Contribuicao
    ) -> Contribuicao:
        """Valida o estado atual e grava apenas a nova Contribuicao."""
        with self.database.transaction(escrita=True) as conn:
            vaquinha = self._obter_na_transacao(conn, vaquinha_id)
            nova = vaquinha.contribuir(
                contribuicao.membro_id,
                contribuicao.valor,
                contribuicao.meio,
                contribuicao.data,
            )
            self._inserir_contribuicao(
                conn, vaquinha_id, len(vaquinha.contribuicoes) - 1, nova
            )
        return nova

    def encerrar(self, vaquinha_id: int) -> Vaquinha:
        """Encerra o estado atual sem sobrescrever Contribuicoes."""
        with self.database.transaction(escrita=True) as conn:
            vaquinha = self._obter_na_transacao(conn, vaquinha_id)
            vaquinha.encerrar()
            conn.execute(
                "UPDATE vaquinhas SET encerrada = 1 WHERE id = ?",
                (vaquinha_id,),
            )
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

    def _obter_na_transacao(
        self, conn: sqlite3.Connection, vaquinha_id: int
    ) -> Vaquinha:
        linha = conn.execute(
            "SELECT * FROM vaquinhas WHERE id = ?", (vaquinha_id,)
        ).fetchone()
        if linha is None:
            raise NaoEncontrado(f"Vaquinha {vaquinha_id} nao encontrada.")
        return self._para_vaquinha(conn, linha)

    @staticmethod
    def _inserir_contribuicao(
        conn: sqlite3.Connection,
        vaquinha_id: int,
        posicao: int,
        contribuicao: Contribuicao,
    ) -> None:
        conn.execute(
            "INSERT INTO contribuicoes (vaquinha_id, posicao, membro_id, "
            "valor_centavos, meio, data) VALUES (?, ?, ?, ?, ?, ?)",
            (
                vaquinha_id,
                posicao,
                contribuicao.membro_id,
                contribuicao.valor.centavos,
                contribuicao.meio.value,
                contribuicao.data.isoformat(),
            ),
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
