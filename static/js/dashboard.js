/**
 * dashboard.js — Interfaz LGC Dashboard
 * Sidebar toggle + theme toggle + Centro de Control.
 */
(function () {
  "use strict";

  /* ── Theme ─────────────────────────────────────────────────────── */
  function initTheme() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", function () {
      var html = document.documentElement;
      var current = html.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      localStorage.setItem("lgc_theme", next);
    });
  }

  /* ── Sidebar ───────────────────────────────────────────────────── */
  function initSidebar() {
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebar-overlay");
    var toggle = document.getElementById("sidebar-toggle");
    if (!sidebar || !overlay || !toggle) return;

    function open() {
      sidebar.classList.remove("-translate-x-full");
      sidebar.classList.add("translate-x-0");
      overlay.classList.remove("hidden");
    }

    function close() {
      sidebar.classList.add("-translate-x-full");
      sidebar.classList.remove("translate-x-0");
      overlay.classList.add("hidden");
    }

    toggle.addEventListener("click", function () {
      var isOpen = !sidebar.classList.contains("-translate-x-full");
      isOpen ? close() : open();
    });

    overlay.addEventListener("click", close);
  }

  /* ── User Menu ──────────────────────────────────────────────────── */
  function initUserMenu() {
    var btn = document.getElementById("user-menu-btn");
    var dropdown = document.getElementById("user-menu-dropdown");
    if (!btn || !dropdown) return;

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      dropdown.classList.toggle("hidden");
    });

    document.addEventListener("click", function () {
      dropdown.classList.add("hidden");
    });
  }

  /* ── Helpers ────────────────────────────────────────────────────── */
  function escapeHtml(str) {
    var div = document.createElement("div");
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function formatNumber(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + "M";
    if (n >= 1000) return (n / 1000).toFixed(1) + "K";
    return String(n);
  }

  /* ── Centro de Control ──────────────────────────────────────────── */
  function initControlPanel() {
    var kpiUsers = document.getElementById("kpi-users");
    if (!kpiUsers) return;

    fetch("/api/stats", { credentials: "same-origin" })
      .then(function (res) {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then(function (data) {
        renderKPIs(data);
        renderTopPalabras(data.top_10 || []);
        renderRecentUsers(data.recent_users || []);
        renderSystemStatus(true);
      })
      .catch(function () {
        renderSystemStatus(false);
      });
  }

  function renderKPIs(data) {
    var el;
    el = document.getElementById("kpi-users");
    if (el) el.textContent = formatNumber(data.users || 0);

    el = document.getElementById("kpi-users-detail");
    if (el) {
      var free = data.users || 0;
      el.textContent = free + " free";
    }

    el = document.getElementById("kpi-searches");
    if (el) el.textContent = formatNumber(data.total_searches || 0);

    el = document.getElementById("kpi-palabras");
    if (el) el.textContent = formatNumber(data.palabras || 0);

    el = document.getElementById("kpi-rankings");
    if (el) el.textContent = formatNumber(data.rankings || 0);
  }

  function renderTopPalabras(items) {
    var body = document.getElementById("top-palabras-body");
    var empty = document.getElementById("top-palabras-empty");
    var table = document.getElementById("top-palabras-table");
    if (!body) return;

    if (!items.length) {
      if (empty) empty.classList.remove("hidden");
      if (table) table.classList.add("hidden");
      return;
    }

    var max = items[0].puntuacion || 1;
    body.innerHTML = items
      .map(function (item, i) {
        var pct = Math.round((item.puntuacion / max) * 100);
        return (
          '<tr class="border-b border-th-div last:border-0">' +
          '<td class="py-2.5 pr-3 text-th-text/30 text-sm w-6">' + (i + 1) + "</td>" +
          '<td class="py-2.5 pr-3 text-sm font-medium whitespace-nowrap">' + escapeHtml(item.palabra) + "</td>" +
          '<td class="py-2.5 pr-3 w-full">' +
          '<div class="h-1.5 rounded-full bg-th-accent/10 overflow-hidden">' +
          '<div class="h-full rounded-full bg-th-accent/60 transition-all" style="width:' + pct + '%"></div>' +
          "</div></td>" +
          '<td class="py-2.5 text-right text-sm font-semibold text-th-accent tabular-nums">' + item.puntuacion + "</td>" +
          "</tr>"
        );
      })
      .join("");
  }

  function renderRecentUsers(users) {
    var list = document.getElementById("recent-users-list");
    var empty = document.getElementById("recent-users-empty");
    if (!list) return;

    if (!users.length) {
      if (empty) empty.classList.remove("hidden");
      return;
    }

    list.innerHTML = users
      .map(function (u) {
        var initials = (u.nombre || u.email || "?").charAt(0).toUpperCase();
        var date = u.created_at ? new Date(u.created_at).toLocaleDateString("es-CO", { day: "2-digit", month: "short" }) : "-";
        return (
          '<div class="flex items-center gap-3">' +
          '<div class="w-8 h-8 rounded-full bg-th-accent/20 flex items-center justify-center flex-shrink-0">' +
          '<span class="text-th-accent text-xs font-semibold">' + escapeHtml(initials) + "</span></div>" +
          '<div class="flex-1 min-w-0">' +
          '<p class="text-sm font-medium truncate">' + escapeHtml(u.nombre || u.email) + "</p>" +
          '<p class="text-[11px] text-th-text/40 truncate">' + escapeHtml(u.email) + "</p></div>" +
          '<span class="inline-block px-2 py-0.5 text-[10px] font-semibold uppercase rounded-full bg-th-text/5 text-th-text/40">' +
          escapeHtml(u.plan || "free") + "</span>" +
          '<span class="text-[11px] text-th-text/30 whitespace-nowrap">' + date + "</span>" +
          "</div>"
        );
      })
      .join("");
  }

  function renderSystemStatus(ok) {
    var dot = document.getElementById("status-dot");
    var text = document.getElementById("status-db");
    if (!dot || !text) return;

    if (ok) {
      dot.className = "w-2.5 h-2.5 rounded-full bg-green-500";
      text.textContent = "Conectada";
      text.className = "font-medium text-green-500";
    } else {
      dot.className = "w-2.5 h-2.5 rounded-full bg-red-500";
      text.textContent = "Error";
      text.className = "font-medium text-red-500";
    }
  }

  /* ── Init ───────────────────────────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initSidebar();
    initUserMenu();
    initControlPanel();
  });
})();
