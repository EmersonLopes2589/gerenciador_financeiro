"""Fixtures: banco temporario para os testes (nunca toca transacoes.db)."""

from __future__ import annotations

import os

import pytest

from app import db


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """Cria banco vazio em tmp_path e redireciona app.db para ele."""
    path = str(tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", path)
    os.environ["FINANCAS_DB"] = path
    db.init_db(path)
    return path
