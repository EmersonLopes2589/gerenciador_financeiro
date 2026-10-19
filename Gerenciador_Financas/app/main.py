"""Rotas FastAPI: importar CSV e resumos por categoria e por mes."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles

from app import db
from app.categorizer import categorize
from app.importer import parse_csv
from app.models import (
    CategoriaTotal,
    ImportSummary,
    MesTotal,
    OrcamentoIn,
    OrcamentoStatus,
)

#: Limite de upload: ~5 MB.
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas na inicializacao."""
    db.init_db()
    yield


app = FastAPI(title="Gerenciador de Finanças", lifespan=lifespan)


def _totais(rows: list[tuple[int]]) -> tuple[float, float, float]:
    """Soma centavos separando receita/despesa; retorna reais."""
    receitas = sum(v for (v,) in rows if v > 0) / 100
    despesas = sum(v for (v,) in rows if v < 0) / 100
    return receitas, despesas, receitas + despesas


@app.post("/transacoes/importar", response_model=ImportSummary)
async def importar(file: UploadFile = File(...)) -> ImportSummary:
    """Importa CSV; ignora duplicadas e reporta linhas invalidas."""
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="arquivo maior que 5 MB")
    parsed = parse_csv(content)
    if parsed.errors and not parsed.rows:
        raise HTTPException(status_code=400, detail="; ".join(parsed.errors))
    importadas = duplicadas = 0
    for row in parsed.rows:
        ok = db.insert_transaction(
            row.data, row.descricao, row.valor_centavos, categorize(row.descricao)
        )
        if ok:
            importadas += 1
        else:
            duplicadas += 1
    return ImportSummary(
        importadas=importadas, duplicadas=duplicadas, erros=parsed.errors
    )


@app.get("/resumo/categorias", response_model=list[CategoriaTotal])
def resumo_categorias() -> list[CategoriaTotal]:
    """Totais (receita/despesa) agrupados por categoria."""
    conn = db.get_connection()
    try:
        cats = [r[0] for r in conn.execute("SELECT DISTINCT categoria FROM transacoes")]
        out = []
        for cat in sorted(cats):
            rows = conn.execute(
                "SELECT valor_centavos FROM transacoes WHERE categoria = ?", (cat,)
            ).fetchall()
            rec, des, liq = _totais(rows)
            out.append(CategoriaTotal(categoria=cat, receitas=rec, despesas=des, liquido=liq))
        return out
    finally:
        conn.close()


@app.get("/resumo/meses", response_model=list[MesTotal])
def resumo_meses() -> list[MesTotal]:
    """Totais (receita/despesa) agrupados por mes YYYY-MM."""
    conn = db.get_connection()
    try:
        meses = [
            r[0]
            for r in conn.execute(
                "SELECT DISTINCT substr(data, 1, 7) FROM transacoes ORDER BY 1"
            )
        ]
        out = []
        for mes in meses:
            rows = conn.execute(
                "SELECT valor_centavos FROM transacoes WHERE substr(data, 1, 7) = ?",
                (mes,),
            ).fetchall()
            rec, des, liq = _totais(rows)
            out.append(MesTotal(mes=mes, receitas=rec, despesas=des, liquido=liq))
        return out
    finally:
        conn.close()


@app.post("/orcamentos", response_model=OrcamentoStatus, status_code=201)
def definir_orcamento(body: OrcamentoIn) -> OrcamentoStatus:
    """Define o limite mensal de uma categoria e retorna o status atual."""
    db.set_orcamento(body.categoria, body.mes, round(body.limite * 100))
    return status_orcamento(body.categoria, body.mes)


def status_orcamento(categoria: str, mes: str) -> OrcamentoStatus:
    """Monta o status gasto x limite de uma categoria+mes."""
    rows = db.get_orcamentos(mes)
    limite_row = next((r for r in rows if r["categoria"] == categoria), None)
    if limite_row is None:
        raise HTTPException(status_code=404, detail="orcamento nao definido")
    limite = int(limite_row["limite_centavos"])
    gasto = db.gasto_categoria_mes(categoria, mes)
    percentual = (gasto / limite * 100) if limite else 0.0
    return OrcamentoStatus(
        categoria=categoria,
        mes=mes,
        limite=limite / 100,
        gasto=gasto / 100,
        percentual=round(percentual, 1),
        alerta=percentual >= 80,
    )


@app.get("/orcamentos/{mes}", response_model=list[OrcamentoStatus])
def listar_orcamentos(mes: str) -> list[OrcamentoStatus]:
    """Status de todos os orcamentos de um mes (YYYY-MM)."""
    return [status_orcamento(r["categoria"], mes) for r in db.get_orcamentos(mes)]


app.mount("/", StaticFiles(directory="static", html=True), name="static")
