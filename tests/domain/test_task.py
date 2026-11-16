import pytest

from domain.task import InvalidTaskError, Task


def test_cria_tarefa_com_titulo_valido():
    task = Task(title="  Estudar Flask  ")
    assert task.title == "Estudar Flask"
    assert task.done is False


@pytest.mark.parametrize("title", ["", "   ", None])
def test_titulo_vazio_e_invalido(title):
    with pytest.raises(InvalidTaskError):
        Task(title=title)


def test_titulo_muito_longo_e_invalido():
    with pytest.raises(InvalidTaskError):
        Task(title="a" * 201)


def test_completar_e_reabrir():
    task = Task(title="Tarefa")
    task.complete()
    assert task.done is True
    task.reopen()
    assert task.done is False
