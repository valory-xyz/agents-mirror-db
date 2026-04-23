import importlib
import sys

import pytest

from app.db.database import get_engine


def test_db_module_imports_without_env(monkeypatch):
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URL", raising=False)
    for mod in ["app.db", "app.db.database"]:
        sys.modules.pop(mod, None)
    importlib.import_module("app.db.database")
    importlib.import_module("app.db")


def test_get_engine_raises_without_env(monkeypatch):
    get_engine.cache_clear()
    monkeypatch.delenv("SQLALCHEMY_DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError, match="SQLALCHEMY_DATABASE_URL"):
        get_engine()
    get_engine.cache_clear()
