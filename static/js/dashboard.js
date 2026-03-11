/**
 * dashboard.js — Interfaz LGC Dashboard
 * Sidebar toggle + theme toggle (standalone, no depende de app.js).
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

  /* ── Init ───────────────────────────────────────────────────────── */
  document.addEventListener("DOMContentLoaded", function () {
    initTheme();
    initSidebar();
    initUserMenu();
  });
})();
