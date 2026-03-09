/**
 * app.js — Interfaz LGC: SPA con calculos en tiempo real.
 */
(function () {
  "use strict";

  // ── Mapa de valores (duplicado del backend para calculos instantaneos) ──
  const VALORES = {
    A:1,B:2,C:3,D:4,E:5,F:6,G:7,H:8,I:9,J:10,K:11,L:12,M:13,
    N:14,"Ñ":15,O:16,P:17,Q:18,R:19,S:20,T:21,U:22,V:23,W:24,X:25,Y:26,Z:27
  };

  const LETRAS_ORDEN = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ".split("");

  // ── Normalizacion (replica del backend) ──
  function normalizar(texto) {
    let t = texto.trim().replace(/\s+/g, " ").toLowerCase();
    t = t.replace(/ñ/g, "__Ñ__");
    t = t.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    return t.replace(/__Ñ__/g, "ñ");
  }

  function calcularPotencial(texto) {
    return normalizar(texto).toUpperCase().split("").reduce(
      (sum, c) => sum + (VALORES[c] || 0), 0
    );
  }

  function calcularLupa(pot) { return Math.round(pot * 121) / 100; }

  function invertirNumero(n) { return parseInt(String(Math.abs(n)).split("").reverse().join(""), 10) || 0; }

  function desglosePorPalabra(frase) {
    return frase.trim().split(/\s+/).filter(Boolean).map(palabra => {
      const norm = normalizar(palabra).toUpperCase();
      const letras = [];
      for (const c of norm) {
        if (VALORES[c] !== undefined) letras.push({ letra: c, valor: VALORES[c] });
      }
      return { palabra, letras, suma: letras.reduce((s, l) => s + l.valor, 0) };
    });
  }

  function contarLetras(texto) {
    return normalizar(texto).split("").filter(c => /[a-zñ]/i.test(c)).length;
  }

  // ── Estado ──
  let currentMode = "conversor";
  let debounceTimer = null;
  let autoSaveTimer = null;
  let lastPotencial = null;
  let lastInput = "";
  let saved = false;

  // ── DOM refs ──
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  // ── Inicializacion ──
  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initModeSelector();
    initInputListeners();
    initLetterMap();
    initCalcGrid();
    initShare();
    initCookies();
    initHistory();
    loadRanking();
  });

  // ── Tema oscuro/claro ──
  function initTheme() {
    const toggle = document.getElementById("theme-toggle");
    toggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("lgc_theme", next);
    });
    // Escuchar cambios de preferencia del sistema
    matchMedia("(prefers-color-scheme: light)").addEventListener("change", e => {
      if (!localStorage.getItem("lgc_theme")) {
        document.documentElement.setAttribute("data-theme", e.matches ? "light" : "dark");
      }
    });
  }

  // ── Selector de modo ──
  function initModeSelector() {
    $$("[data-mode]").forEach(btn => {
      btn.addEventListener("click", () => {
        currentMode = btn.dataset.mode;
        $$("[data-mode]").forEach(b => {
          b.classList.toggle("active", b === btn);
          b.setAttribute("aria-pressed", b === btn);
        });
        $$(".mode-input").forEach(el => el.classList.add("hidden"));
        $(`#input-${currentMode}`).classList.remove("hidden");
        clearResults();
        focusCurrentInput();
      });
    });
  }

  function focusCurrentInput() {
    if (currentMode === "conversor") $("#word-input").focus();
    else if (currentMode === "buscador") $("#number-input").focus();
    else $("#word1-input").focus();
  }

  // ── Listeners de input ──
  function initInputListeners() {
    $("#word-input").addEventListener("input", () => onInputChange(getConversorValue(), "conversor"));
    $("#number-input").addEventListener("input", (e) => {
      e.target.value = e.target.value.replace(/[^\d]/g, "");
      onInputChange(e.target.value, "buscador");
    });
    $("#word1-input").addEventListener("input", () => onCalcInput());
    $("#word2-input").addEventListener("input", () => onCalcInput());
    $("#btn-limpiar").addEventListener("click", clearAll);
    $("#btn-guardar").addEventListener("click", saveManual);
  }

  function getConversorValue() { return $("#word-input").value; }

  function onInputChange(value, mode) {
    const trimmed = value.trim();
    if (!trimmed) { clearResults(); return; }

    saved = false;
    lastInput = trimmed;

    if (mode === "conversor") {
      const pot = calcularPotencial(trimmed);
      lastPotencial = pot;
      renderConversorResults(trimmed, pot);
      debouncedSearch(pot, normalizar(trimmed));
      scheduleAutoSave(trimmed);
    } else if (mode === "buscador") {
      const num = parseInt(trimmed, 10);
      if (isNaN(num) || num <= 0) { clearResults(); return; }
      lastPotencial = num;
      renderBuscadorResults(num);
      debouncedSearch(num, "");
      scheduleAutoSave(String(num));
    }
  }

  function onCalcInput() {
    const w1 = $("#word1-input").value.trim();
    const w2 = $("#word2-input").value.trim();
    if (!w1 || !w2) { clearResults(); return; }

    saved = false;
    lastInput = `${w1} | ${w2}`;

    const pot1 = calcularPotencial(w1);
    const pot2 = calcularPotencial(w2);
    const suma = pot1 + pot2;
    const resta = Math.abs(pot1 - pot2);
    lastPotencial = suma;

    renderCalcResults(w1, w2, pot1, pot2, suma, resta);
    debouncedSearchCalc(suma, resta, normalizar(w1), normalizar(w2));
    scheduleAutoSave(w1);
    scheduleAutoSave(w2);
  }

  // ── Render: Conversor ──
  function renderConversorResults(texto, pot) {
    const desglose = desglosePorPalabra(texto);
    const lupa = calcularLupa(pot);
    const nLetras = contarLetras(texto);
    const nPalabras = desglose.length;

    showQuickMetrics(nLetras, nPalabras, pot, lupa);
    renderBreakdownTable(desglose, pot, lupa);
    renderCalcGrid(pot);
    renderLetterMap(texto);
    showResults();
    hideComparison();
  }

  // ── Render: Buscador ──
  function renderBuscadorResults(num) {
    const lupa = calcularLupa(num);
    showQuickMetrics(0, 0, num, lupa);
    $("#breakdown-card").classList.add("hidden");
    renderCalcGrid(num);
    renderLetterMap("");
    showResults();
    hideComparison();
  }

  // ── Render: Calculadora ──
  function renderCalcResults(w1, w2, pot1, pot2, suma, resta) {
    const lupa1 = calcularLupa(pot1);
    const lupa2 = calcularLupa(pot2);
    const lupaSuma = calcularLupa(suma);
    const lupaResta = calcularLupa(resta);

    const d1 = desglosePorPalabra(w1);
    const d2 = desglosePorPalabra(w2);

    showQuickMetricsCalc(pot1, pot2, suma, resta, lupaSuma);

    $("#breakdown-card").classList.add("hidden");
    $("#comparison-results").classList.remove("hidden");

    $("#comparison-word1").innerHTML = buildWordCard("Palabra 1", w1, d1, pot1, lupa1);
    $("#comparison-word2").innerHTML = buildWordCard("Palabra 2", w2, d2, pot2, lupa2);
    $("#comparison-operations").innerHTML = `
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-th-text/50 text-sm">Suma</span>
          <div class="text-right">
            <span class="text-2xl font-bold text-th-accent">${suma}</span>
            <span class="text-th-text/40 text-sm ml-2">Lupa: ${lupaSuma}</span>
          </div>
        </div>
        <div id="calc-suma-words" class="text-sm text-th-text/60"></div>
        <hr class="border-th">
        <div class="flex items-center justify-between">
          <span class="text-th-text/50 text-sm">Resta</span>
          <div class="text-right">
            <span class="text-2xl font-bold text-th-muted">${resta}</span>
            <span class="text-th-text/40 text-sm ml-2">Lupa: ${lupaResta}</span>
          </div>
        </div>
        <div id="calc-resta-words" class="text-sm text-th-text/60"></div>
      </div>
    `;

    renderCalcGrid(suma);
    renderLetterMap(`${w1} ${w2}`);
    showResults();
  }

  function buildWordCard(label, word, desglose, pot, lupa) {
    let rows = desglose.map((d, i) => `
      <tr class="border-b border-th-div">
        <td class="py-1.5 pr-3 text-th-text/40">${i + 1}</td>
        <td class="py-1.5 pr-3 font-medium">${escapeHtml(d.palabra)}</td>
        <td class="py-1.5 pr-3 text-th-text/60 text-xs">${d.letras.map(l => `${l.letra}(${l.valor})`).join(" + ")}</td>
        <td class="py-1.5 text-right font-semibold">${d.suma}</td>
      </tr>
    `).join("");
    return `
      <h4 class="text-xs font-semibold text-th-text/40 uppercase tracking-wider mb-3">${label}</h4>
      <table class="w-full text-sm">
        <thead><tr class="text-th-text/30 text-left text-xs">
          <th class="pb-1.5">#</th><th class="pb-1.5">Palabra</th><th class="pb-1.5">Letras</th><th class="pb-1.5 text-right">Total</th>
        </tr></thead>
        <tbody>${rows}</tbody>
      </table>
      <div class="mt-3 flex justify-end gap-4 text-sm">
        <span>Potencial: <strong class="text-th-accent font-semibold">${pot}</strong></span>
        <span>Lupa: <strong class="text-th-muted">${lupa}</strong></span>
      </div>
    `;
  }

  // ── Tabla de desglose ──
  function renderBreakdownTable(desglose, pot, lupa) {
    $("#breakdown-card").classList.remove("hidden");
    const tbody = $("#breakdown-body");
    const tfoot = $("#breakdown-footer");

    tbody.innerHTML = desglose.map((d, i) => `
      <tr class="border-b border-th-div">
        <td class="py-2 pr-4 text-th-text/40">${i + 1}</td>
        <td class="py-2 pr-4 font-medium">${escapeHtml(d.palabra)}</td>
        <td class="py-2 pr-4 text-th-text/60 text-xs">${d.letras.map(l => `${l.letra}(${l.valor})`).join(" + ")}</td>
        <td class="py-2 text-right font-semibold">${d.suma}</td>
      </tr>
    `).join("");

    tfoot.innerHTML = `
      <tr>
        <td colspan="3" class="py-2 text-right font-semibold text-th-text/50">Frecuencia resultante</td>
        <td class="py-2 text-right font-bold text-th-accent text-lg">${pot}</td>
      </tr>
      <tr>
        <td colspan="3" class="py-1 text-right font-semibold text-th-text/50">Lupa</td>
        <td class="py-1 text-right font-bold text-th-muted">${lupa}</td>
      </tr>
    `;
  }

  // ── Metricas rapidas ──
  function showQuickMetrics(letras, palabras, pot, lupa) {
    const el = $("#quick-metrics");
    el.classList.remove("hidden");
    if (currentMode === "buscador") {
      el.innerHTML = `
        <span class="glass-badge">Numero: <strong class="text-th-accent font-semibold">${pot}</strong></span>
        <span class="glass-badge">Lupa: <strong class="text-th-muted">${lupa}</strong></span>
        <button id="btn-limpiar" class="ml-auto text-th-text/40 hover:text-th-text transition-colors text-xs">Limpiar</button>
      `;
      el.querySelector("#btn-limpiar").addEventListener("click", clearAll);
    } else {
      $("#metric-letras").textContent = letras;
      $("#metric-palabras").textContent = palabras;
      $("#metric-potencial").textContent = pot;
      $("#metric-lupa").textContent = lupa;
    }
  }

  function showQuickMetricsCalc(pot1, pot2, suma, resta, lupaSuma) {
    const el = $("#quick-metrics");
    el.classList.remove("hidden");
    el.innerHTML = `
      <span class="glass-badge">P1: <strong class="text-th-accent font-semibold">${pot1}</strong></span>
      <span class="glass-badge">P2: <strong class="text-th-accent font-semibold">${pot2}</strong></span>
      <span class="glass-badge">Suma: <strong class="text-th-accent font-semibold">${suma}</strong></span>
      <span class="glass-badge">Resta: <strong class="text-th-muted">${resta}</strong></span>
      <button id="btn-limpiar" class="ml-auto text-th-text/40 hover:text-th-text transition-colors text-xs">Limpiar</button>
    `;
    el.querySelector("#btn-limpiar").addEventListener("click", clearAll);
  }

  // ── Calculadora visual (grid 0-9) ──
  function initCalcGrid() {
    const grid = $("#calc-grid");
    const order = [7,8,9,4,5,6,1,2,3,0];
    grid.innerHTML = order.map(n => `
      <div class="calc-cell" data-digit="${n}">
        <span class="text-lg font-bold">${n}</span>
      </div>
    `).join("");
  }

  function renderCalcGrid(num) {
    const digits = new Set(String(Math.abs(num)).split("").map(Number));
    $$(".calc-cell").forEach(cell => {
      const d = parseInt(cell.dataset.digit, 10);
      cell.classList.toggle("calc-cell-active", digits.has(d));
    });
  }

  // ── Mapa de letras ──
  function initLetterMap() {
    const map = $("#letter-map");
    map.innerHTML = LETRAS_ORDEN.map(l => `
      <div class="glass-letter-cell" data-letter="${l}">
        <span class="font-bold text-sm">${l}</span>
        <span class="text-[10px] text-th-text/40">${VALORES[l]}</span>
      </div>
    `).join("");
  }

  function renderLetterMap(texto) {
    const activeLetters = new Set();
    if (texto) {
      const norm = normalizar(texto).toUpperCase();
      for (const c of norm) {
        if (VALORES[c] !== undefined) activeLetters.add(c);
      }
    }
    $$(".glass-letter-cell").forEach(cell => {
      const letter = cell.dataset.letter;
      cell.classList.toggle("glass-letter-cell-active", activeLetters.has(letter));
    });
  }

  // ── API: Busqueda debounced ──
  function debouncedSearch(potencial, excluir) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchSearch(potencial, excluir), 300);
  }

  function debouncedSearchCalc(suma, resta, excl1, excl2) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(async () => {
      const [resSuma, resResta] = await Promise.all([
        fetchSearchRaw(suma, `${excl1},${excl2}`),
        fetchSearchRaw(resta, `${excl1},${excl2}`),
      ]);
      if (resSuma) {
        $("#calc-suma-words").innerHTML = renderWordList(resSuma.palabras_relacionadas, "Palabras relacionadas con la suma");
      }
      if (resResta) {
        $("#calc-resta-words").innerHTML = renderWordList(resResta.palabras_relacionadas, "Palabras relacionadas con la resta");
      }
    }, 300);
  }

  async function fetchSearchRaw(potencial, excluir) {
    try {
      const params = new URLSearchParams({ potencial });
      if (excluir) params.set("excluir", excluir);
      const res = await fetch(`/api/buscar?${params}`);
      if (!res.ok) return null;
      return await res.json();
    } catch { return null; }
  }

  async function fetchSearch(potencial, excluir) {
    const data = await fetchSearchRaw(potencial, excluir);
    if (!data) return;

    // Palabras relacionadas
    const rc = $("#related-content");
    rc.innerHTML = renderWordList(data.palabras_relacionadas, "Palabras con el mismo potencial");
    $("#related-count").textContent = data.palabras_relacionadas.length ? `(${data.palabras_relacionadas.length})` : "";

    // Invertido
    $("#inverted-value").textContent = `→ ${data.total_invertido}`;
    const ic = $("#inverted-content");
    ic.innerHTML = renderWordList(data.palabras_invertidas, `Palabras con potencial ${data.total_invertido}`);
  }

  function renderWordList(words, title) {
    if (!words || !words.length) return `<p class="text-th-text/30 text-sm">Sin coincidencias</p>`;
    return `
      <div class="flex flex-wrap gap-1.5">
        ${words.map(w => `<span class="glass-badge cursor-pointer hover:bg-th-surface/10" onclick="window.lgcClickWord('${escapeHtml(w)}')">${escapeHtml(w)}</span>`).join("")}
      </div>
    `;
  }

  // Permitir clic en palabras relacionadas para buscarlas
  window.lgcClickWord = function(word) {
    if (currentMode !== "conversor") {
      $$("[data-mode]").forEach(b => {
        b.classList.toggle("active", b.dataset.mode === "conversor");
        b.setAttribute("aria-pressed", b.dataset.mode === "conversor");
      });
      $$(".mode-input").forEach(el => el.classList.add("hidden"));
      $("#input-conversor").classList.remove("hidden");
      currentMode = "conversor";
    }
    $("#word-input").value = word;
    onInputChange(word, "conversor");
  };

  // ── Auto-guardado (5 segundos) ──
  function scheduleAutoSave(texto) {
    clearTimeout(autoSaveTimer);
    autoSaveTimer = setTimeout(() => {
      if (!saved && texto.trim()) saveWord(texto);
    }, 5000);
  }

  function saveManual() {
    if (saved || !lastInput.trim()) return;
    if (currentMode === "calculadora") {
      const w1 = $("#word1-input").value.trim();
      const w2 = $("#word2-input").value.trim();
      if (w1) saveWord(w1);
      if (w2) saveWord(w2);
    } else {
      saveWord(lastInput);
    }
    saved = true;
    showToast("Busqueda guardada");
  }

  async function saveWord(texto) {
    try {
      await fetch("/api/guardar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ palabra: texto }),
      });
      addToHistory(texto, currentMode);
      saved = true;
    } catch { /* silencioso */ }
  }

  // ── Historial (localStorage) ──
  function getHistory() {
    try { return JSON.parse(localStorage.getItem("lgc_historial") || "[]"); }
    catch { return []; }
  }

  function addToHistory(texto, modo) {
    const hist = getHistory();
    const entry = { texto, modo, fecha: new Date().toISOString() };
    if (hist.length && hist[0].texto === texto && hist[0].modo === modo) return;
    hist.unshift(entry);
    if (hist.length > 50) hist.length = 50;
    localStorage.setItem("lgc_historial", JSON.stringify(hist));
    renderHistory();
  }

  function initHistory() { renderHistory(); }

  function renderHistory() {
    const hist = getHistory();
    const el = $("#history-list");
    if (!hist.length) {
      el.innerHTML = `<p class="text-th-text/30 text-sm">Aun no has realizado busquedas</p>`;
      return;
    }
    el.innerHTML = hist.slice(0, 20).map(h => `
      <div class="flex items-center justify-between py-1.5 border-b border-th-div text-sm cursor-pointer hover:bg-th-surface/5 rounded px-2 -mx-2"
           onclick="window.lgcClickWord('${escapeHtml(h.texto)}')">
        <span class="truncate">${escapeHtml(h.texto)}</span>
        <span class="text-th-text/30 text-xs shrink-0 ml-2">${h.modo}</span>
      </div>
    `).join("");
  }

  // ── Ranking ──
  async function loadRanking() {
    try {
      const res = await fetch("/api/ranking?limit=15");
      if (!res.ok) return;
      const data = await res.json();
      const el = $("#ranking-list");
      if (!data.ranking.length) {
        el.innerHTML = `<p class="text-th-text/30 text-sm">Sin datos aun</p>`;
        return;
      }
      el.innerHTML = data.ranking.map(r => `
        <div class="flex items-center justify-between py-1.5 border-b border-th-div text-sm cursor-pointer hover:bg-th-surface/5 rounded px-2 -mx-2"
             onclick="window.lgcClickWord('${escapeHtml(r.palabra)}')">
          <span class="truncate">${escapeHtml(r.palabra)}</span>
          <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-th-accent/15 border border-th-accent/30 text-th-accent">${r.puntuacion} busquedas</span>
        </div>
      `).join("");
    } catch { /* silencioso */ }
  }

  // ── Compartir ──
  function initShare() {
    const modal = $("#share-modal");
    const open = () => { modal.classList.remove("hidden"); modal.classList.add("flex"); };
    const close = () => { modal.classList.add("hidden"); modal.classList.remove("flex"); $("#share-msg").classList.add("hidden"); };

    $("#btn-compartir").addEventListener("click", open);
    $("#share-cancel").addEventListener("click", close);
    modal.addEventListener("click", (e) => { if (e.target === modal) close(); });

    $("#share-whatsapp").addEventListener("click", () => {
      const text = buildShareText();
      window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, "_blank");
      close();
    });

    $("#share-copy").addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(buildShareText());
        $("#share-msg").classList.remove("hidden");
        setTimeout(() => $("#share-msg").classList.add("hidden"), 2000);
      } catch { /* fallback */ }
    });
  }

  function buildShareText() {
    const pot = lastPotencial || 0;
    const lupa = calcularLupa(pot);
    if (currentMode === "buscador") {
      return `Interfaz LGC\nNumero: ${pot}\nLupa: ${lupa}\n\nhttps://www.julianosoriom.com`;
    }
    return `Interfaz LGC\n"${lastInput}" → Potencial: ${pot} | Lupa: ${lupa}\n\nhttps://www.julianosoriom.com`;
  }

  // ── Cookies ──
  function initCookies() {
    if (localStorage.getItem("lgc_cookies")) return;
    const banner = $("#cookie-banner");
    banner.classList.remove("hidden");
    $("#cookie-accept").addEventListener("click", () => {
      localStorage.setItem("lgc_cookies", "accepted");
      banner.classList.add("hidden");
    });
    $("#cookie-reject").addEventListener("click", () => {
      localStorage.setItem("lgc_cookies", "rejected");
      banner.classList.add("hidden");
    });
  }

  // ── Helpers UI ──
  function showResults() { $("#results-area").classList.remove("hidden"); }
  function hideComparison() { $("#comparison-results").classList.add("hidden"); }

  function clearResults() {
    $("#results-area").classList.add("hidden");
    $("#quick-metrics").classList.add("hidden");
    renderLetterMap("");
    lastPotencial = null;
    lastInput = "";
    saved = false;
  }

  function clearAll() {
    $("#word-input").value = "";
    $("#number-input").value = "";
    $("#word1-input").value = "";
    $("#word2-input").value = "";
    clearResults();
    clearTimeout(debounceTimer);
    clearTimeout(autoSaveTimer);
    focusCurrentInput();
  }

  function showToast(msg) {
    const toast = document.createElement("div");
    toast.className = "fixed bottom-20 right-4 glass-card px-4 py-2 text-sm text-th-text z-50 animate-fade-in";
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => { toast.classList.add("opacity-0", "transition-opacity"); setTimeout(() => toast.remove(), 300); }, 2000);
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

})();
