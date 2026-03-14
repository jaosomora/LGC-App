/**
 * calendaria.js — Motor de cálculos y visualización Calendaria LGC.
 * Protocolo de comunicación entre la conciencia solar y la conciencia humana.
 */
(function () {
  "use strict";

  // ── Constantes del sistema ──
  var JDN_EPOCH = 1721424;
  var CARD_MAP  = ["SO","SO","SO","SO","NE","NE","NE","NE","NO","NO","NO","NO","SE","SE","SE","SE"];
  var PASOS     = ["Lógica","Inhumano","Humano","Contexto"];
  var MEMORIAS  = ["","RAM","REM","ROM","RUM"];
  var FASES     = ["","Asume","Asimila","Desafía","Decide"];
  var MESES     = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
  var ms        = 86400000;

  // ── Grilla: estructura de cuadrantes ──
  var QUADS = [
    { name: "SO", start: 1,  mems: ["RAM","REM","ROM","RUM"] },
    { name: "NE", start: 5,  mems: [null,null,null,null] },
    { name: "NO", start: 9,  mems: [null,null,null,null] },
    { name: "SE", start: 13, mems: [null,null,null,null] }
  ];

  // ── JDN (Número de Día Juliano) ──
  function jdnG(y,m,d) {
    var a = Math.floor((14-m)/12), Y = y+4800-a, M = m+12*a-3;
    return d + Math.floor((153*M+2)/5) + 365*Y + Math.floor(Y/4) - Math.floor(Y/100) + Math.floor(Y/400) - 32045;
  }
  function jdnJ(y,m,d) {
    var a = Math.floor((14-m)/12), Y = y+4800-a, M = m+12*a-3;
    return d + Math.floor((153*M+2)/5) + 365*Y + Math.floor(Y/4) - 32083;
  }
  function jdnCut(y,m,d) {
    if (y > 1582) return jdnG(y,m,d);
    if (y < 1582) return jdnJ(y,m,d);
    if (m > 10) return jdnG(y,m,d);
    if (m < 10) return jdnJ(y,m,d);
    return d >= 15 ? jdnG(y,m,d) : jdnJ(y,m,d);
  }

  // ── Helpers ──
  function diaSolar(y,m,d) { return jdnCut(y,m,d) - JDN_EPOCH + 1; }
  function isLeap(y) { return (y%4===0) && ((y%100)!==0 || y%400===0); }
  function dt(y,m,d) { var b = new Date(Date.UTC(2000, m-1, d)); b.setUTCFullYear(y); return b; }
  function dFrom(a,b) { return Math.floor((b-a)/ms); }
  function fmtSign(n) { return (n >= 0 ? "+" : "") + n; }
  function fmtDate(d,m,y) { return d + " " + MESES[m-1] + " " + y; }

  function toDateStr(date) {
    var y = date.getFullYear();
    var m = String(date.getMonth() + 1).padStart(2, "0");
    var d = String(date.getDate()).padStart(2, "0");
    return y + "-" + m + "-" + d;
  }

  // ── Barra de progreso ──
  function progressBar(value, max, label) {
    var pct = Math.round((value / max) * 100);
    return '<div class="mt-2">' +
      '<div class="flex items-center justify-between text-[10px] text-th-text/30 mb-0.5">' +
        '<span>' + label + '</span>' +
        '<span>' + value + '/' + max + '</span>' +
      '</div>' +
      '<div class="h-1.5 rounded-full overflow-hidden" style="background:var(--glass-border)">' +
        '<div class="h-full rounded-full transition-all duration-500" style="width:' + pct + '%;background:rgb(var(--c-accent))"></div>' +
      '</div>' +
    '</div>';
  }

  // ── Motor de cálculo ──
  function calcular(year, month, day, nacY, nacM, nacD) {
    var leap = isLeap(year), total = leap ? 366 : 365;
    var doy = dFrom(dt(year,1,1), dt(year,month,day)) + 1;

    // Aparato
    var apNum   = Math.floor((year-1)/4) + 1;
    var apStart = year - ((year-1)%4);
    var apos    = dFrom(dt(apStart,1,1), dt(year,month,day)) + 1;
    var aneg    = 1461 - apos;
    var fase    = Math.max(1, Math.min(4, year - apStart + 1));

    // Día Solar, Día Solar Nativo y Días de Vida
    var ds       = diaSolar(year, month, day);
    var dsNativo = (nacY != null) ? diaSolar(nacY, nacM, nacD) : null;
    var ddv      = (nacY != null) ? Math.max(0, jdnCut(year,month,day) - jdnCut(nacY,nacM,nacD)) : null;

    // Cuarentena Global (inicio: 14/10/2012)
    var Q  = dt(2012, 10, 14);
    var qd = dFrom(Q, dt(year,month,day));
    var qi       = qd > 0 ? Math.floor((qd-1)/39)+1 : 0;
    var qDpos    = qd > 0 ? (qd-1)%39+1 : 0;
    var brickIdx = qDpos > 0 ? Math.floor((qDpos-1)/3)+1 : 0;
    var brickDay = qDpos > 0 ? (qDpos-1)%3+1 : 0;

    // Frecuencias del año
    var frcPos = doy, frcNeg = total - doy, anuAño = frcPos - frcNeg;

    // Encaje anual
    var encajeAnual = null;
    if (frcNeg > 0) {
      var ed = new Date(dt(year,1,1).getTime() + (frcNeg - 1) * ms);
      encajeAnual = { d: ed.getUTCDate(), m: ed.getUTCMonth()+1, y: ed.getUTCFullYear() };
    }

    // Encaje del Aparato
    var encajeAp = null;
    if (aneg > 0) {
      var ea = new Date(dt(apStart,1,1).getTime() + (aneg - 1) * ms);
      encajeAp = { d: ea.getUTCDate(), m: ea.getUTCMonth()+1, y: ea.getUTCFullYear() };
    }

    var cuarentena = { qd:qd, qi:qi, qDpos:qDpos, brickIdx:brickIdx, brickDay:brickDay };

    var base = {
      doy:doy, total:total, ds:ds, dsNativo:dsNativo, ddv:ddv,
      apNum:apNum, apStart:apStart, fase:fase, faseName:FASES[fase],
      apos:apos, aneg:aneg, anuAp:apos-aneg,
      frcPos:frcPos, frcNeg:frcNeg, anuAño:anuAño,
      encajeAnual:encajeAnual, encajeAp:encajeAp,
      cuarentena:cuarentena, year:year
    };

    if (doy > 352) {
      base.esAnillo = true;
      base.diaAnillo = doy - 352;
      base.totalAnillo = leap ? 14 : 13;
      return base;
    }

    base.esAnillo = false;
    var pos  = (doy-1)%16+1;
    var cuad = CARD_MAP[pos-1];
    var step = (pos-1)%4+1;
    base.pos  = pos;
    base.cuad = cuad;
    base.paso = PASOS[step-1];
    base.mem  = cuad === "SO" ? MEMORIAS[step] : null;
    base.vAbs = Math.floor((doy-1)/16)+1;
    base.vRel = base.vAbs <= 11 ? base.vAbs : base.vAbs - 11;
    return base;
  }

  // ── Grilla visual 4×4 ──
  function renderGrid(data) {
    var html = '<div class="grid grid-cols-5 gap-1.5 mt-4">';

    // Header
    html += '<div></div>';
    html += '<div class="text-[10px] uppercase tracking-wider text-th-text/30 text-center pb-1">Lógica</div>';
    html += '<div class="text-[10px] uppercase tracking-wider text-th-text/30 text-center pb-1">Inhumano</div>';
    html += '<div class="text-[10px] uppercase tracking-wider text-th-text/30 text-center pb-1">Humano</div>';
    html += '<div class="text-[10px] uppercase tracking-wider text-th-text/30 text-center pb-1">Contexto</div>';

    // Rows
    for (var q = 0; q < 4; q++) {
      var quad = QUADS[q];
      var isActiveQuad = data.cuad === quad.name;
      var labelCls = isActiveQuad ? "text-th-accent font-bold" : "text-th-text/40 font-semibold";
      html += '<div class="flex items-center justify-center text-xs ' + labelCls + '">' + quad.name + '</div>';

      for (var i = 0; i < 4; i++) {
        var pos = quad.start + i;
        var isActive = data.pos === pos;
        var cellCls = isActive ? "cal-grid-active" : "cal-grid-cell";
        html += '<div class="' + cellCls + ' flex flex-col items-center justify-center py-2 rounded-lg">';
        html += '<span class="font-bold text-sm">' + pos + '</span>';
        if (quad.mems[i]) {
          html += '<span class="text-[9px] leading-tight mt-0.5 opacity-70">' + quad.mems[i] + '</span>';
        }
        html += '</div>';
      }
    }

    html += '</div>';
    return html;
  }

  // ── Renderizado principal ──
  function render(data) {
    var container = document.getElementById("calendaria-results");
    if (!container) return;

    var html = "";

    // ── 1. Día Solar + Nativo + Días de Vida ──
    html += '<div class="glass-card p-4">';
    if (data.dsNativo !== null) {
      // Con fecha de nacimiento: 3 filas
      html += '<div class="grid grid-cols-3 gap-4 text-center">';
      html += '<div>';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Día Solar</div>';
      html += '<div class="text-xl font-bold text-th-accent">' + data.ds + '</div>';
      html += '</div>';
      html += '<div>';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Solar Nativo</div>';
      html += '<div class="text-xl font-bold text-th-text/70">' + data.dsNativo + '</div>';
      html += '</div>';
      html += '<div>';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Días de Vida</div>';
      html += '<div class="text-xl font-bold text-th-accent">' + data.ddv + '</div>';
      html += '</div>';
      html += '</div>';
    } else {
      // Sin fecha de nacimiento: solo Día Solar
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Día Solar</div>';
      html += '<div class="text-2xl font-bold text-th-accent">' + data.ds + '</div>';
    }
    html += '</div>';

    // ── 2. Posición Calendaria + Grilla + Barra ──
    if (data.esAnillo) {
      html += '<div class="glass-card p-6 text-center">';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-2">Posición Calendaria</div>';
      html += '<div class="text-3xl sm:text-4xl font-bold text-th-accent">Anillo de Fuego</div>';
      html += '<div class="text-lg font-semibold text-th-text/70 mt-2">V23 · ' + data.diaAnillo + '/' + data.totalAnillo + '</div>';
      html += progressBar(data.diaAnillo, data.totalAnillo, "Anillo de Fuego");
      html += '</div>';
    } else {
      html += '<div class="glass-card p-5">';
      html += '<div class="text-center">';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Posición Calendaria</div>';
      var memStr = data.mem ? " · " + data.mem : "";
      html += '<div class="text-2xl sm:text-3xl font-bold text-th-accent">V' + data.vAbs + ' · ' + data.pos + '/16</div>';
      html += '<div class="text-sm text-th-text/50 mt-1">' + data.cuad + ' · ' + data.paso + memStr + '</div>';
      html += '<div class="text-xs text-th-text/40 mt-0.5">Vuelta ' + data.vRel + '</div>';
      html += '</div>';
      html += progressBar(data.pos, 16, "Posición en la vuelta");
      html += renderGrid(data);
      html += '</div>';
    }

    // ── 3. Métricas adicionales ──
    html += '<div class="grid grid-cols-2 gap-3">';

    // Día del Año / Frecuencias
    var encAnualStr = data.encajeAnual
      ? '<div class="text-xs text-th-text/30 mt-0.5">Encaje: ' + fmtDate(data.encajeAnual.d, data.encajeAnual.m, data.encajeAnual.y) + '</div>'
      : "";
    html += '<div class="glass-card p-4">';
    html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Día del Año</div>';
    html += '<div class="text-2xl font-bold">' + data.doy + '<span class="text-base text-th-text/40">/' + data.total + '</span></div>';
    html += '<div class="text-xs text-th-text/40 mt-1">+' + data.frcPos + ' −' + data.frcNeg + ' · Anu: ' + fmtSign(data.anuAño) + '</div>';
    html += encAnualStr;
    html += progressBar(data.doy, data.total, "Progreso anual");
    html += '</div>';

    // Aparato
    var encApStr = data.encajeAp
      ? '<div class="text-xs text-th-text/30 mt-0.5">Encaje: ' + fmtDate(data.encajeAp.d, data.encajeAp.m, data.encajeAp.y) + '</div>'
      : "";
    html += '<div class="glass-card p-4">';
    html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Aparato ' + data.apNum + '</div>';
    html += '<div class="text-lg font-bold">' + data.faseName + '</div>';
    html += '<div class="text-sm text-th-text/50">Día ' + data.apos + '/1461</div>';
    html += '<div class="text-xs text-th-text/40 mt-1">+' + data.apos + ' −' + data.aneg + ' · Anu: ' + fmtSign(data.anuAp) + '</div>';
    html += encApStr;
    html += progressBar(data.apos, 1461, "Progreso del Aparato");
    html += '</div>';

    // Cuarentena Global
    if (data.cuarentena.qd > 0) {
      html += '<div class="glass-card p-4 col-span-2">';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Cuarentena Global</div>';
      html += '<div class="flex items-center justify-between">';
      html += '<div>';
      html += '<div class="text-lg font-bold">#' + data.cuarentena.qi + '</div>';
      html += '<div class="text-sm text-th-text/50">Día ' + data.cuarentena.qDpos + '/39 · Ladrillo ' + data.cuarentena.brickIdx + '</div>';
      html += '</div>';
      html += '<div class="text-right">';
      html += '<div class="text-xs text-th-text/40">Día ' + data.cuarentena.brickDay + '/3 del ladrillo</div>';
      html += '</div>';
      html += '</div>';
      html += progressBar(data.cuarentena.qDpos, 39, "Progreso de la cuarentena");
      html += '</div>';
    }

    html += '</div>';

    container.innerHTML = html;
  }

  // ── Navegación de fecha ──
  function shiftDate(days) {
    var calDate = document.getElementById("cal-date");
    if (!calDate || !calDate.value) return;
    var current = new Date(calDate.value + "T12:00:00");
    current.setDate(current.getDate() + days);
    calDate.value = toDateStr(current);
    refresh();
  }

  // ── Inicialización ──
  function init() {
    var calDate  = document.getElementById("cal-date");
    var calBirth = document.getElementById("cal-birth");
    var btnPrev  = document.getElementById("cal-prev");
    var btnNext  = document.getElementById("cal-next");
    if (!calDate) return;

    // Default: hoy (zona horaria local del usuario)
    var today = new Date();
    calDate.value = toDateStr(today);

    // Cargar fecha de nacimiento guardada
    var savedBirth = localStorage.getItem("lgc_birth_date");
    if (savedBirth && calBirth) calBirth.value = savedBirth;

    // Event listeners
    calDate.addEventListener("input", refresh);
    if (calBirth) {
      calBirth.addEventListener("input", function () {
        if (calBirth.value) localStorage.setItem("lgc_birth_date", calBirth.value);
        else localStorage.removeItem("lgc_birth_date");
        refresh();
      });
    }
    if (btnPrev) btnPrev.addEventListener("click", function () { shiftDate(-1); });
    if (btnNext) btnNext.addEventListener("click", function () { shiftDate(1); });

    // Render inicial
    refresh();
  }

  function refresh() {
    var calDate = document.getElementById("cal-date");
    if (!calDate || !calDate.value) return;

    var parts = calDate.value.split("-").map(Number);
    var year = parts[0], month = parts[1], day = parts[2];
    if (!year || !month || !day) return;

    var nacY = null, nacM = null, nacD = null;
    var calBirth = document.getElementById("cal-birth");
    if (calBirth && calBirth.value) {
      var bp = calBirth.value.split("-").map(Number);
      nacY = bp[0]; nacM = bp[1]; nacD = bp[2];
    }

    var data = calcular(year, month, day, nacY, nacM, nacD);
    render(data);
  }

  document.addEventListener("DOMContentLoaded", init);
  window.LGCCalendaria = { refresh: refresh };

})();
