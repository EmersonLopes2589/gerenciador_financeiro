"""Testes do importer (utf-8-sig, validacao, centavos)."""

from pathlib import Path

from app.importer import parse_csv

EXAMPLE = Path(__file__).resolve().parent.parent / "transacoes_exemplo.csv"


def test_exemplo_todo_valido() -> None:
    result = parse_csv(EXAMPLE.read_bytes())
    assert result.errors == []
    assert len(result.rows) == 49
    first = result.rows[0]
    assert (first.data, first.descricao, first.valor_centavos) == (
        "2026-07-01",
        "Salário empresa XYZ",
        520000,
    )


def test_descricao_com_virgula_entre_aspas() -> None:
    content = 'data,descricao,valor\n2026-07-20,"Livraria Cultura, livros",-135.80\n'.encode()
    result = parse_csv(content)
    assert result.errors == []
    assert result.rows[0].descricao == "Livraria Cultura, livros"
    assert result.rows[0].valor_centavos == -13580


def test_bom_do_excel() -> None:
    content = "data,descricao,valor\n2026-07-01,Salário,5200.00\n".encode("utf-8-sig")
    result = parse_csv(content)
    assert result.errors == []
    assert len(result.rows) == 1


def test_linhas_invalidas_nao_quebram() -> None:
    content = (
        "data,descricao,valor\n"
        "2026-07-01,Salário,5200.00\n"
        "data-invalida,Quebrado,-10.00\n"
        "2026-07-02,Sem valor,\n"
        "2026-07-03,Válido,-342.15\n"
    ).encode()
    result = parse_csv(content)
    assert len(result.rows) == 2
    assert len(result.errors) == 2
    assert result.errors[0].startswith("linha 3:")
