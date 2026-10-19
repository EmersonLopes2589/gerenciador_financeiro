"""Leitura e validacao do CSV de transacoes."""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, InvalidOperation

EXPECTED_HEADER = ["data", "descricao", "valor"]


@dataclass
class ParsedRow:
    """Linha valida ja convertida (valor em centavos)."""

    data: str
    descricao: str
    valor_centavos: int


@dataclass
class ImportResult:
    """Resultado da leitura: linhas validas e erros por linha."""

    rows: list[ParsedRow] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _to_centavos(raw: str) -> int:
    """Converte "5200.00" em 520000 (int); levanta ValueError."""
    try:
        return int((Decimal(raw.strip()) * 100).to_integral_value())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"valor invalido: {raw!r}") from exc


def parse_csv(content: bytes) -> ImportResult:
    """Le bytes do CSV (utf-8-sig) sem quebrar em linhas invalidas."""
    result = ImportResult()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return ImportResult(errors=["arquivo nao esta em UTF-8"])
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames != EXPECTED_HEADER:
        return ImportResult(errors=[f"cabecalho esperado: {','.join(EXPECTED_HEADER)}"])
    for lineno, row in enumerate(reader, start=2):
        try:
            data = (row["data"] or "").strip()
            descricao = (row["descricao"] or "").strip()
            valor_raw = (row["valor"] or "").strip()
            if not data or not descricao or not valor_raw:
                raise ValueError("coluna vazia")
            date.fromisoformat(data)  # valida YYYY-MM-DD
            result.rows.append(
                ParsedRow(
                    data=data,
                    descricao=descricao,
                    valor_centavos=_to_centavos(valor_raw),
                )
            )
        except ValueError as exc:
            result.errors.append(f"linha {lineno}: {exc}")
    return result
