"""Categorizacao de transacoes por palavras-chave."""

from __future__ import annotations

import unicodedata

#: Categoria de fallback quando nada casa.
OUTROS = "Outros"

#: Palavra-chave (sem acento, minuscula) -> categoria.
KEYWORDS: dict[str, str] = {
    "aluguel": "Moradia",
    "luz": "Contas",
    "internet": "Contas",
    "supermercado": "Alimentação",
    "padaria": "Alimentação",
    "ifood": "Alimentação",
    "restaurante": "Alimentação",
    "uber": "Transporte",
    "posto": "Transporte",
    "combustivel": "Transporte",
    "farmacia": "Saúde",
    "academia": "Saúde",
    "consulta": "Saúde",
    "netflix": "Assinaturas",
    "spotify": "Assinaturas",
    "cinema": "Lazer",
    "livraria": "Lazer",
    "amazon": "Compras",
    "salario": "Salário",
    "freelance": "Freelance",
    "estorno": "Estorno",
}


def normalize(text: str) -> str:
    """Minusculas sem acentos para comparar palavras-chave."""
    folded = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in folded if not unicodedata.combining(c))


def categorize(descricao: str) -> str:
    """Retorna a categoria da descricao ou "Outros"."""
    desc = normalize(descricao)
    for keyword, categoria in KEYWORDS.items():
        if keyword in desc:
            return categoria
    return OUTROS
