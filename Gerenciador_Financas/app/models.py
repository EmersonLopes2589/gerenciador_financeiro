"""Schemas Pydantic da API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ImportSummary(BaseModel):
    """Resumo de uma importacao de CSV."""

    importadas: int
    duplicadas: int
    erros: list[str] = Field(default_factory=list)


class Totais(BaseModel):
    """Receitas, despesas e liquido em reais."""

    receitas: float
    despesas: float
    liquido: float


class CategoriaTotal(Totais):
    """Totais de uma categoria."""

    categoria: str


class MesTotal(Totais):
    """Totais de um mes (YYYY-MM)."""

    mes: str


class OrcamentoIn(BaseModel):
    """Orcamento mensal de uma categoria (limite em reais)."""

    categoria: str
    mes: str = Field(pattern=r"^\d{4}-\d{2}$")
    limite: float = Field(gt=0)


class OrcamentoStatus(BaseModel):
    """Gasto x limite com flag de alerta (>= 80%)."""

    categoria: str
    mes: str
    limite: float
    gasto: float
    percentual: float
    alerta: bool
