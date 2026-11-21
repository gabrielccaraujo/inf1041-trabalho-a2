import threading

from domain.grupo import Grupo
from infra.db.database import Database
from infra.repositories.grupo_repository_sqlite import GrupoRepositorySqlite


def test_acesso_concorrente_nao_corrompe_resultados():
    database = Database(":memory:")
    database.init_schema()
    repository = GrupoRepositorySqlite(database)
    criados = []
    erros = []

    def trabalho():
        for i in range(100):
            try:
                assert database.ping()
                grupo = repository.adicionar(Grupo(nome=f"grupo {i}"))
                criados.append(grupo.id)
                assert repository.buscar(grupo.id).nome == f"grupo {i}"
            except Exception as e:  # pragma: no cover - so ocorre em regressao
                erros.append(e)

    threads = [threading.Thread(target=trabalho) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert erros == []
    assert len(set(criados)) == 800
