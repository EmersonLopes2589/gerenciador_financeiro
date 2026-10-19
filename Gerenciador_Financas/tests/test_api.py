"""Testes da API (importar + resumos, sem duplicar)."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

EXAMPLE = Path(__file__).resolve().parent.parent / "transacoes_exemplo.csv"


def _client() -> TestClient:
    return TestClient(app)


def test_importar_e_resumos(temp_db) -> None:
    client = _client()
    resp = client.post(
        "/transacoes/importar",
        files={"file": ("transacoes.csv", EXAMPLE.read_bytes(), "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["importadas"] == 49
    assert body["duplicadas"] == 0
    assert body["erros"] == []

    # Reimportar nao duplica.
    resp2 = client.post(
        "/transacoes/importar",
        files={"file": ("transacoes.csv", EXAMPLE.read_bytes(), "text/csv")},
    )
    assert resp2.json()["importadas"] == 0
    assert resp2.json()["duplicadas"] == 49

    cats = {c["categoria"]: c for c in client.get("/resumo/categorias").json()}
    assert cats["Outros"]["despesas"] == pytest.approx(-429.0)
    assert cats["Salário"]["receitas"] == pytest.approx(15600.0)
    assert cats["Estorno"]["receitas"] == pytest.approx(45.0)

    meses = {m["mes"]: m for m in client.get("/resumo/meses").json()}
    assert set(meses) == {"2026-07", "2026-08", "2026-09"}
    assert meses["2026-07"]["receitas"] == pytest.approx(6095.0)
    assert meses["2026-07"]["despesas"] == pytest.approx(-3608.62)


def test_csv_invalido_rejeitado(temp_db) -> None:
    client = _client()
    resp = client.post(
        "/transacoes/importar",
        files={"file": ("ruim.csv", b"coluna1,coluna2\n1,2\n", "text/csv")},
    )
    assert resp.status_code == 400
