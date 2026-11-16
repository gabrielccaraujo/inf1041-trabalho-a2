from typing import Optional

import pytest

from domain.task import InvalidTaskError, Task
from use_cases.task_use_case import TaskNotFoundError, TaskUseCase


class FakeTaskRepository:
    """Repositorio em memoria: testa o caso de uso sem banco de dados."""

    def __init__(self) -> None:
        self.tasks: dict[int, Task] = {}
        self.next_id = 1

    def add(self, task: Task) -> Task:
        task.id = self.next_id
        self.tasks[task.id] = task
        self.next_id += 1
        return task

    def get(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)

    def list(self) -> list[Task]:
        return list(self.tasks.values())

    def update(self, task: Task) -> Task:
        self.tasks[task.id] = task
        return task

    def delete(self, task_id: int) -> bool:
        return self.tasks.pop(task_id, None) is not None


@pytest.fixture
def use_case():
    return TaskUseCase(FakeTaskRepository())


def test_criar_e_listar(use_case):
    use_case.create("Primeira")
    use_case.create("Segunda")
    assert [t.title for t in use_case.list()] == ["Primeira", "Segunda"]


def test_criar_com_titulo_invalido(use_case):
    with pytest.raises(InvalidTaskError):
        use_case.create("")


def test_atualizar_titulo_e_status(use_case):
    task = use_case.create("Antiga")
    updated = use_case.update(task.id, title="Nova", done=True)
    assert updated.title == "Nova"
    assert updated.done is True


def test_buscar_inexistente(use_case):
    with pytest.raises(TaskNotFoundError):
        use_case.get(99)


def test_remover(use_case):
    task = use_case.create("Remover")
    use_case.delete(task.id)
    assert use_case.list() == []
    with pytest.raises(TaskNotFoundError):
        use_case.delete(task.id)
