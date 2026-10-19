"""Testes do categorizador por palavras-chave."""

from app.categorizer import categorize


def test_transporte_inclui_uber_e_posto() -> None:
    assert categorize("Uber viagem centro") == "Transporte"
    assert categorize("Posto Shell combustível") == "Transporte"


def test_lazer() -> None:
    assert categorize("Cinema ingresso") == "Lazer"
    assert categorize("Livraria Cultura, livros") == "Lazer"


def test_contas() -> None:
    assert categorize("Conta de luz") == "Contas"
    assert categorize("Internet fibra") == "Contas"


def test_compras_amazon() -> None:
    assert categorize("Amazon compra fones") == "Compras"


def test_receitas_por_tipo() -> None:
    assert categorize("Salário empresa XYZ") == "Salário"
    assert categorize("Freelance site cliente") == "Freelance"
    assert categorize("Estorno compra online") == "Estorno"


def test_acentos_e_maiusculas() -> None:
    assert categorize("FARMÁCIA Saúde+") == "Saúde"
    assert categorize("SUPERMERCADO Bom Preço") == "Alimentação"


def test_fallback_outros_de_proposito() -> None:
    assert categorize("Compra loja XPTO") == "Outros"
    assert categorize("Pagamento transferência PIX") == "Outros"
