from dataclasses import dataclass
from typing import Optional, Protocol


class InvalidTaskError(ValueError):
    """Erro de regra de negocio da entidade Task."""


@dataclass
class Task:
    title: str
    done: bool = False
    id: Optional[int] = None

    def __post_init__(self) -> None:
        self.title = (self.title or "").strip()
        if not self.title:
            raise InvalidTaskError("O titulo da tarefa nao pode ser vazio.")
        if len(self.title) > 200:
            raise InvalidTaskError("O titulo da tarefa deve ter no maximo 200 caracteres.")

    def complete(self) -> None:
        self.done = True

    def reopen(self) -> None:
        self.done = False

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "done": self.done}


class TaskRepository(Protocol):
    """Porta de persistencia: implementada na camada infra."""

    def add(self, task: Task) -> Task: ...

    def get(self, task_id: int) -> Optional[Task]: ...

    def list(self) -> list[Task]: ...

    def update(self, task: Task) -> Task: ...

    def delete(self, task_id: int) -> bool: ...
