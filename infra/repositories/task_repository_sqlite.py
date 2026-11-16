import sqlite3
from typing import Optional

from domain.task import Task
from infra.db.database import Database


class TaskRepositorySqlite:
    def __init__(self, database: Database) -> None:
        self.database = database

    @staticmethod
    def _to_task(row: sqlite3.Row) -> Task:
        return Task(id=row["id"], title=row["title"], done=bool(row["done"]))

    def add(self, task: Task) -> Task:
        with self.database.transaction() as conn:
            cursor = conn.execute(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, int(task.done))
            )
            task.id = cursor.lastrowid
        return task

    def get(self, task_id: int) -> Optional[Task]:
        with self.database.transaction() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return self._to_task(row) if row else None

    def list(self) -> list[Task]:
        with self.database.transaction() as conn:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [self._to_task(row) for row in rows]

    def update(self, task: Task) -> Task:
        with self.database.transaction() as conn:
            conn.execute(
                "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                (task.title, int(task.done), task.id),
            )
        return task

    def delete(self, task_id: int) -> bool:
        with self.database.transaction() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0
