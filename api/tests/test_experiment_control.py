from __future__ import annotations

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from control.experiment_control import ExperimentControl
from dao.model.experiment import metadata


class SQLiteConnectionManager:
    def __init__(self, engine) -> None:
        self._engine = engine

    @contextmanager
    def get_session(self):
        with Session(self._engine) as session:
            yield session


def test_experiment_lifecycle_transitions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    control = ExperimentControl(SQLiteConnectionManager(engine))

    created = control.create_experiment("cooling test", "description")
    running = control.start_experiment(created.id)
    completed = control.complete_experiment(created.id)
    reopened = control.reopen_experiment(created.id)
    completed_again = control.complete_experiment(created.id)
    archived = control.delete_experiment(created.id)

    assert created.status == "planned"
    assert running.status == "running"
    assert completed.status == "completed"
    assert reopened.status == "running"
    assert completed_again.status == "completed"
    assert archived.status == "archived"


def test_archived_experiment_is_hidden_from_list() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    metadata.create_all(engine)
    control = ExperimentControl(SQLiteConnectionManager(engine))

    created = control.create_experiment("cooling test", None)
    control.delete_experiment(created.id)

    assert control.list_experiments() == []
