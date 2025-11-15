// DOM helpers and basic sanitization
export function $(selector, scope = document) {
  return scope.querySelector(selector);
}
export function $all(selector, scope = document) {
  return Array.from(scope.querySelectorAll(selector));
}

export function setMessage(msg, type = "info") {
  const box = $("#global-message");
  box.textContent = msg || "";
  box.className = `message ${type}`;
  if (msg) {
    clearTimeout(box._clearTimeout);
    box._clearTimeout = setTimeout(() => {
      box.textContent = "";
      box.className = "message";
    }, 20000); // 20 seconds
  }
}

// Sanitize plain text (removes potential tags)
export function sanitizeText(value) {
  if (value == null) return "";
  return String(value).replace(/[\n\r]+/g, " ").replace(/</g, "&lt;").replace(/>/g, "&gt;").trim();
}

export function activateView(id) {
  $all(".view").forEach(v => v.classList.remove("active"));
  const el = $("#" + id);
  if (el) el.classList.add("active");
}

export function renderTable(container, columns, rows) {
  const div = typeof container === "string" ? $(container) : container;
  if (!div) return;
  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const trh = document.createElement("tr");
  columns.forEach(c => {
    const th = document.createElement("th");
    th.textContent = c;
    trh.appendChild(th);
  });
  thead.appendChild(trh);
  table.appendChild(thead);
  const tbody = document.createElement("tbody");
  rows.forEach(r => {
    const tr = document.createElement("tr");
    columns.forEach(c => {
      const td = document.createElement("td");
      td.textContent = r[c] != null ? String(r[c]) : "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  div.innerHTML = "";
  div.appendChild(table);
}
