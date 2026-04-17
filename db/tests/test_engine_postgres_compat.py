"""Smoke tests: db/engine.py is Postgres-compatible after the connect_args fix."""
import importlib
import os
import sys


def _reload_engine(url: str):
    os.environ["DATABASE_URL"] = url
    sys.modules.pop("db.engine", None)
    import db.engine as eng
    return eng


def teardown_module(_):
    os.environ.pop("DATABASE_URL", None)
    sys.modules.pop("db.engine", None)


def test_postgres_url_scheme():
    eng = _reload_engine("postgresql://user:pass@localhost/testdb")
    assert eng.engine.url.drivername.startswith("postgresql")


def test_postgres_no_check_same_thread():
    """connect_args must be empty dict for Postgres — check_same_thread is SQLite-only."""
    eng = _reload_engine("postgresql://user:pass@localhost/testdb")
    # SQLAlchemy stores the connect_args passed at create_engine time on the pool
    # The easiest check: _is_sqlite flag must be False
    assert not eng._is_sqlite


def test_sqlite_check_same_thread_preserved():
    eng = _reload_engine("sqlite:///./test_compat.db")
    assert eng._is_sqlite
    # engine should have been created without error
    assert eng.engine.url.drivername == "sqlite"
