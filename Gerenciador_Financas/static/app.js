// Frontend puro: upload de CSV e resumos por categoria e por mes.

async function carregarResumos() {
  const [cats, meses] = await Promise.all([
    fetch("/resumo/categorias").then((r) => r.json()),
    fetch("/resumo/meses").then((r) => r.json()),
  ]);
  preenche("#cats tbody", cats, (c) => c.categoria);
  preenche("#meses tbody", meses, (m) => m.mes);
}

function preenche(seletor, linhas, rotulo) {
  const tbody = document.querySelector(seletor);
  tbody.innerHTML = "";
  for (const l of linhas) {
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td>${rotulo(l)}</td><td>${fmt(l.receitas)}</td>` +
      `<td>${fmt(l.despesas)}</td><td>${fmt(l.liquido)}</td>`;
    tbody.appendChild(tr);
  }
}

function fmt(v) {
  return v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

document.querySelector("#enviar").addEventListener("click", async () => {
  const input = document.querySelector("#csv");
  const msg = document.querySelector("#msg");
  if (!input.files.length) {
    msg.textContent = "Escolha um arquivo CSV.";
    return;
  }
  const form = new FormData();
  form.append("file", input.files[0]);
  const resp = await fetch("/transacoes/importar", { method: "POST", body: form });
  const body = await resp.json();
  if (!resp.ok) {
    msg.textContent = "Erro: " + (body.detail || resp.status);
    return;
  }
  msg.textContent =
    `Importadas: ${body.importadas}, duplicadas: ${body.duplicadas}` +
    (body.erros.length ? `, erros: ${body.erros.join("; ")}` : "");
  carregarResumos();
  carregarOrcamentos();
});

async function carregarOrcamentos() {
  const mes = document.querySelector("#orc-mes").value || "2026-07";
  const lista = await fetch(`/orcamentos/${mes}`).then((r) => r.json());
  const tbody = document.querySelector("#orcs tbody");
  tbody.innerHTML = "";
  for (const o of lista) {
    const tr = document.createElement("tr");
    if (o.alerta) tr.style.background = "#ffe0e0";
    tr.innerHTML =
      `<td>${o.categoria}</td><td>${fmt(o.gasto)}</td>` +
      `<td>${fmt(o.limite)}</td><td>${o.percentual}%</td>` +
      `<td>${o.alerta ? "⚠️ acima de 80%" : "ok"}</td>`;
    tbody.appendChild(tr);
  }
}

document.querySelector("#orc-salvar").addEventListener("click", async () => {
  const payload = {
    categoria: document.querySelector("#orc-cat").value,
    mes: document.querySelector("#orc-mes").value,
    limite: parseFloat(document.querySelector("#orc-limite").value),
  };
  const resp = await fetch("/orcamentos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const body = await resp.json();
    document.querySelector("#msg").textContent = "Erro: " + JSON.stringify(body.detail || body);
    return;
  }
  carregarOrcamentos();
});

carregarResumos();
carregarOrcamentos();
