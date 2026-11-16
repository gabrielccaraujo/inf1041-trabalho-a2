import threading

from domain.task import Task
from infra.db.database import Database
from infra.repositories.task_repository_sqlite import TaskRepositorySqlite


def test_acesso_concorrente_nao_corrompe_resultados():
    database = Database(":memory:")
    database.init_schema()
    repository = TaskRepositorySqlite(database)
    erros = []

    def trabalho():
        for i in range(100):
            try:
                assert database.ping()
                repository.add(Task(title=f"tarefa {i}"))
                repository.list()
            except Exception as e:  # pragma: no cover - so ocorre se houver regressao
                erros.append(e)

    threads = [threading.Thread(target=trabalho) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert erros == []
    assert len(repository.list()) == 800
