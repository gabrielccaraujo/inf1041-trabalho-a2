import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS grupos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS membros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_id INTEGER NOT NULL REFERENCES grupos (id),
    nome TEXT NOT NULL,
    chave_pix TEXT
);

CREATE TABLE IF NOT EXISTS despesas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grupo_id INTEGER NOT NULL REFERENCES grupos (id),
    descricao TEXT NOT NULL,
    valor_centavos INTEGER NOT NULL,
    pagador_id INTEGER NOT NULL REFERENCES membros (id),
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cotas (
    despesa_id INTEGER NOT NULL REFERENCES despesas (id),
    posicao INTEGER NOT NULL,
    membro_id INTEGER NOT NULL REFERENCES membros (id),
    valor_centavos INTEGER NOT NULL,
    PRIMARY KEY (despesa_id, posicao)
);
"""


class Database:
    """Conexao SQLite compartilhada e segura entre threads.

    O servidor Flask atende requisicoes em threads diferentes; uma mesma
    conexao sqlite3 usada ao mesmo tempo por duas threads corrompe os
    resultados. Todo acesso passa por `transaction()`, que serializa o uso
    com um lock e faz commit/rollback automaticamente.
    """

    def __init__(self, db_path: str | Path = DEFAULT_DB_PATH) -> None:
        self._connection = sqlite3.connect(db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.Lock()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            try:
                yield self._connection
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def init_schema(self) -> None:
        with self.transaction() as conn:
            conn.executescript(SCHEMA)

    def ping(self) -> bool:
        with self.transaction() as conn:
            return conn.execute("SELECT 1").fetchone()[0] == 1
