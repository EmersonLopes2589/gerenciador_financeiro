"""Conexao SQLite e criacao das tabelas (valores em centavos)."""

from __future__ import annotations

import os
import sqlite3

DB_PATH = os.environ.get("FINANCAS_DB", "transacoes.db")


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Abre conexao SQLite com Row como factory."""
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    """Cria a tabela transacoes se ela nao existir."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                descricao TEXT NOT NULL,
                valor_centavos INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                UNIQUE (data, descricao, valor_centavos)
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT NOT NULL,
                mes TEXT NOT NULL,
                limite_centavos INTEGER NOT NULL CHECK (limite_centavos > 0),
                UNIQUE (categoria, mes)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def insert_transaction(
    data: str,
    descricao: str,
    valor_centavos: int,
    categoria: str,
    db_path: str | None = None,
) -> bool:
    """Insere uma transacao; retorna False se for duplicada."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO transacoes (data, descricao, valor_centavos, categoria)"
            " VALUES (?, ?, ?, ?)",
            (data, descricao, valor_centavos, categoria),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def set_orcamento(
    categoria: str, mes: str, limite_centavos: int, db_path: str | None = None
) -> None:
    """Define (ou substitui) o orcamento mensal de uma categoria."""
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO orcamentos (categoria, mes, limite_centavos)"
            " VALUES (?, ?, ?)"
            " ON CONFLICT (categoria, mes)"
            " DO UPDATE SET limite_centavos = excluded.limite_centavos",
            (categoria, mes, limite_centavos),
        )
        conn.commit()
    finally:
        conn.close()


def get_orcamentos(mes: str, db_path: str | None = None) -> list[sqlite3.Row]:
    """Lista os orcamentos de um mes (YYYY-MM)."""
    conn = get_connection(db_path)
    try:
        return conn.execute(
            "SELECT categoria, mes, limite_centavos FROM orcamentos WHERE mes = ?"
            " ORDER BY categoria",
            (mes,),
        ).fetchall()
    finally:
        conn.close()


def gasto_categoria_mes(
    categoria: str, mes: str, db_path: str | None = None
) -> int:
    """Soma as despesas (centavos, valor absoluto) de categoria+mes."""
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT COALESCE(SUM(-valor_centavos), 0) FROM transacoes"
            " WHERE categoria = ? AND substr(data, 1, 7) = ?"
            " AND valor_centavos < 0",
            (categoria, mes),
        ).fetchone()
        return int(row[0])
    finally:
        conn.close()
