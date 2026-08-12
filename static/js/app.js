// ============================================================
// NetSec frontend — talks to the existing FastAPI endpoints:
//   GET  /train    -> triggers training pipeline
//   POST /predict  -> multipart file upload, returns JSON rows
//   GET  /health   -> optional, used for the status dot (see app.py notes)
// ============================================================

const $ = (sel) => document.querySelector(sel);

/* ---------- typewriter hero title ---------- */
(function typeHero() {
  const target = $("#typeTarget");
  const text = "Phishing Detection Engine";
  let i = 0;
  const tick = () => {
    if (i <= text.length) {
      target.textContent = text.slice(0, i);
      i++;
      setTimeout(tick, 28);
    }
  };
  tick();
})();

/* ---------- API status check ---------- */
async function checkStatus() {
  const dot = document.querySelector("#apiStatus .dot");
  const label = document.querySelector("#apiStatus .status__label");
  try {
    // Falls back to "/" if you haven't added a /health route (see app.py notes)
    const res = await fetch("/health").catch(() => fetch("/"));
    if (res.ok) {
      dot.className = "dot dot--up";
      label.textContent = "engine online";
    } else {
      throw new Error("bad status");
    }
  } catch {
    dot.className = "dot dot--down";
    label.textContent = "engine unreachable";
  }
}
checkStatus();

/* ---------- dropzone ---------- */
const dropzone = $("#dropzone");
const fileInput = $("#fileInput");
const dropLabel = $("#dropLabel");
const scanBtn = $("#scanBtn");
let selectedFile = null;

function setFile(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".csv")) {
    logTo("#scanLog", "rejected: file must be .csv", "err");
    return;
  }
  selectedFile = file;
  dropLabel.textContent = file.name;
  dropzone.classList.add("has-file");
  scanBtn.disabled = false;
}

fileInput.addEventListener("change", (e) => setFile(e.target.files[0]));

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("is-drag");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("is-drag");
  })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  setFile(file);
});

/* ---------- logging helper ---------- */
function logTo(sel, msg, kind) {
  const el = $(sel);
  el.textContent = msg;
  el.className = "log" + (kind ? ` log--${kind}` : "");
}

/* ---------- train ---------- */
$("#trainBtn").addEventListener("click", async () => {
  const btn = $("#trainBtn");
  btn.disabled = true;
  logTo("#trainLog", "> training pipeline started…");
  try {
    const res = await fetch("/train");
    if (!res.ok) throw new Error(`server responded ${res.status}`);
    logTo("#trainLog", "> training complete. model artifact updated.", "ok");
  } catch (err) {
    logTo("#trainLog", `> training failed: ${err.message}`, "err");
  } finally {
    btn.disabled = false;
  }
});

/* ---------- predict ---------- */
$("#predictForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!selectedFile) return;

  scanBtn.disabled = true;
  logTo("#scanLog", "> uploading and scanning…");

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const res = await fetch("/predict", { method: "POST", body: formData });
    if (!res.ok) throw new Error(`server responded ${res.status}`);

    const contentType = res.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
      const data = await res.json();
      renderResults(Array.isArray(data) ? data : data.rows || []);
    } else {
      // Backend returns rendered HTML (Jinja2 table) — parse the table out of it
      const html = await res.text();
      const rows = parseHtmlTable(html);
      renderResults(rows);
    }

    logTo("#scanLog", "> scan complete.", "ok");
  } catch (err) {
    logTo("#scanLog", `> scan failed: ${err.message}`, "err");
  } finally {
    scanBtn.disabled = false;
  }
});

/* ---------- parse a returned HTML table into row objects (fallback path) ---------- */
function parseHtmlTable(html) {
  const doc = new DOMParser().parseFromString(html, "text/html");
  const table = doc.querySelector("table");
  if (!table) return [];
  const headers = [...table.querySelectorAll("thead th, tr:first-child th, tr:first-child td")]
    .map((th) => th.textContent.trim());
  const bodyRows = [...table.querySelectorAll("tbody tr")].length
    ? [...table.querySelectorAll("tbody tr")]
    : [...table.querySelectorAll("tr")].slice(1);

  return bodyRows.map((tr) => {
    const cells = [...tr.querySelectorAll("td")].map((td) => td.textContent.trim());
    const obj = {};
    headers.forEach((h, i) => (obj[h || `col_${i}`] = cells[i]));
    return obj;
  });
}

/* ---------- render results table ---------- */
function renderResults(rows) {
  const panel = $("#resultsPanel");
  const head = $("#resultsHead");
  const body = $("#resultsBody");
  const summary = $("#resultsSummary");

  head.innerHTML = "";
  body.innerHTML = "";

  if (!rows.length) {
    panel.hidden = false;
    summary.textContent = "no rows returned";
    return;
  }

  const columns = Object.keys(rows[0]);
  const verdictCol =
    columns.find((c) => /predicted_column|predicted|result/i.test(c)) ||
    columns[columns.length - 1];

  columns.forEach((c) => {
    const th = document.createElement("th");
    th.textContent = c;
    head.appendChild(th);
  });

  let legitCount = 0;
  let phishCount = 0;

  rows.forEach((row) => {
    const tr = document.createElement("tr");
    const verdictRaw = String(row[verdictCol]).trim();
    const isLegit = verdictRaw === "1";
    isLegit ? legitCount++ : phishCount++;
    tr.className = isLegit ? "row--legit" : "row--phish";

    columns.forEach((c) => {
      const td = document.createElement("td");
      if (c === verdictCol) {
        td.className = `cell--verdict ${isLegit ? "good" : "bad"}`;
        td.textContent = isLegit ? "LEGITIMATE" : "PHISHING";
      } else {
        td.textContent = row[c];
      }
      tr.appendChild(td);
    });
    body.appendChild(tr);
  });

  summary.textContent = `${rows.length} rows — ${legitCount} legitimate / ${phishCount} phishing`;
  panel.hidden = false;
  panel.scrollIntoView({ behavior: "smooth", block: "start" });
}