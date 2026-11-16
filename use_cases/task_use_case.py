from typing import Optional

from domain.task import Task, TaskRepository


class TaskNotFoundError(LookupError):
    """Tarefa inexistente."""


class TaskUseCase:
    def __init__(self, repository: TaskRepository) -> None:
        self.repository = repository

    def create(self, title: str) -> Task:
        return self.repository.add(Task(title=title))

    def list(self) -> list[Task]:
        return self.repository.list()

    def get(self, task_id: int) -> Task:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Tarefa {task_id} nao encontrada.")
        return task

    def update(self, task_id: int, title: Optional[str] = None, done: Optional[bool] = None) -> Task:
        task = self.get(task_id)
        if title is not None:
            task = Task(title=title, done=task.done, id=task.id)
        if done is True:
            task.complete()
        elif done is False:
            task.reopen()
        return self.repository.update(task)

    def delete(self, task_id: int) -> None:
        if not self.repository.delete(task_id):
            raise TaskNotFoundError(f"Tarefa {task_id} nao encontrada.")
