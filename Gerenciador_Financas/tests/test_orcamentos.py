"""Testes de orcamento mensal por categoria (alerta >= 80%)."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

EXAMPLE = Path(__file__).resolve().parent.parent / "transacoes_exemplo.csv"


def _client() -> TestClient:
    return TestClient(app)


def _importar(client: TestClient) -> None:
    resp = client.post(
        "/transacoes/importar",
        files={"file": ("transacoes.csv", EXAMPLE.read_bytes(), "text/csv")},
    )
    assert resp.status_code == 200


def test_alerta_acima_de_80(temp_db) -> None:
    client = _client()
    _importar(client)
    # Alimentacao em 2026-07: 342.15+18.50+62.40+289.45+87.60 = 800.10
    resp = client.post(
        "/orcamentos",
        json={"categoria": "Alimentação", "mes": "2026-07", "limite": 800.0},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["gasto"] == 800.10
    assert body["percentual"] == 100.0
    assert body["alerta"] is True


def test_sem_alerta_abaixo_de_80(temp_db) -> None:
    client = _client()
    _importar(client)
    resp = client.post(
        "/orcamentos",
        json={"categoria": "Alimentação", "mes": "2026-07", "limite": 2000.0},
    )
    body = resp.json()
    assert body["percentual"] == 40.0
    assert body["alerta"] is False
    lista = client.get("/orcamentos/2026-07").json()
    assert len(lista) == 1
    assert lista[0]["categoria"] == "Alimentação"


def test_limite_invalido_rejeitado(temp_db) -> None:
    client = _client()
    resp = client.post(
        "/orcamentos",
        json={"categoria": "Lazer", "mes": "2026-07", "limite": -50},
    )
    assert resp.status_code == 422
