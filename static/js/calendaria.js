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
  function fmt(n) { return n.toLocaleString("es"); }
  function fmtSign(n) { return (n >= 0 ? "+" : "") + fmt(n); }
  function fmtDate(d,m,y) { return d + " " + MESES[m-1] + " " + y; }

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

    // Día Solar y Días de Vida
    var ds  = diaSolar(year, month, day);
    var ddv = (nacY != null) ? Math.max(0, jdnCut(year,month,day) - jdnCut(nacY,nacM,nacD)) : null;

    // Cuarentena Global (inicio: 14/10/2012)
    var Q  = dt(2012, 10, 14);
    var qd = dFrom(Q, dt(year,month,day));
    var qi      = qd > 0 ? Math.floor((qd-1)/39)+1 : 0;
    var qDpos   = qd > 0 ? (qd-1)%39+1 : 0;
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
      doy:doy, total:total, ds:ds, ddv:ddv,
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
    base.vTipo = base.vAbs <= 11 ? "con uno mismo" : "con el otro";
    return base;
  }

  // ── Renderizado ──
  function render(data) {
    var posEl = document.getElementById("cal-position");
    var metricsEl = document.getElementById("cal-metrics");
    if (!posEl || !metricsEl) return;

    // ── Position Hero ──
    if (data.esAnillo) {
      posEl.innerHTML =
        '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-2">Posición Calendaria</div>' +
        '<div class="text-3xl sm:text-4xl font-bold text-th-accent">Anillo de Fuego</div>' +
        '<div class="text-lg font-semibold text-th-text/70 mt-2">V23 · ' + data.diaAnillo + '/' + data.totalAnillo + '</div>' +
        '<div class="text-sm text-th-text/40 mt-1">Días fuera del cuerpo calendárico</div>';
    } else {
      var memStr = data.mem ? " · " + data.mem : "";
      posEl.innerHTML =
        '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-2">Posición Calendaria</div>' +
        '<div class="text-3xl sm:text-4xl font-bold text-th-accent">V' + data.vAbs + ' · ' + data.pos + '/16</div>' +
        '<div class="text-lg font-semibold text-th-text/70 mt-2">' + data.cuad + ' · ' + data.paso + memStr + '</div>' +
        '<div class="text-sm text-th-text/40 mt-1">Vuelta ' + data.vRel + ' (' + data.vTipo + ')</div>';
    }

    // ── Metrics Grid ──
    var html = "";

    // Día Solar
    html += '<div class="glass-card p-4">' +
      '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Día Solar</div>' +
      '<div class="text-2xl font-bold text-th-accent">' + fmt(data.ds) + '</div>' +
      '</div>';

    // Frecuencias del Año
    var encAnualStr = data.encajeAnual
      ? '<div class="text-xs text-th-text/30 mt-0.5">Encaje: ' + fmtDate(data.encajeAnual.d, data.encajeAnual.m, data.encajeAnual.y) + '</div>'
      : "";
    html += '<div class="glass-card p-4">' +
      '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Día del Año</div>' +
      '<div class="text-2xl font-bold">' + data.doy + '<span class="text-base text-th-text/40">/' + data.total + '</span></div>' +
      '<div class="text-xs text-th-text/40 mt-1">+' + data.frcPos + ' −' + data.frcNeg + ' · Anu: ' + fmtSign(data.anuAño) + '</div>' +
      encAnualStr +
      '</div>';

    // Aparato
    var encApStr = data.encajeAp
      ? '<div class="text-xs text-th-text/30 mt-0.5">Encaje: ' + fmtDate(data.encajeAp.d, data.encajeAp.m, data.encajeAp.y) + '</div>'
      : "";
    html += '<div class="glass-card p-4">' +
      '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Aparato ' + data.apNum + '</div>' +
      '<div class="text-lg font-bold">' + data.faseName + '</div>' +
      '<div class="text-sm text-th-text/50">Día ' + fmt(data.apos) + '/1461</div>' +
      '<div class="text-xs text-th-text/40 mt-1">+' + fmt(data.apos) + ' −' + fmt(data.aneg) + ' · Anu: ' + fmtSign(data.anuAp) + '</div>' +
      encApStr +
      '</div>';

    // Cuarentena Global
    if (data.cuarentena.qd > 0) {
      html += '<div class="glass-card p-4">' +
        '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Cuarentena Global</div>' +
        '<div class="text-lg font-bold">#' + fmt(data.cuarentena.qi) + '</div>' +
        '<div class="text-sm text-th-text/50">Día ' + data.cuarentena.qDpos + '/39 · Ladrillo ' + data.cuarentena.brickIdx + '</div>' +
        '<div class="text-xs text-th-text/40 mt-1">Día ' + data.cuarentena.brickDay + '/3 del ladrillo</div>' +
        '</div>';
    }

    // Días de Vida
    if (data.ddv !== null) {
      html += '<div class="glass-card p-4 col-span-2">' +
        '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Días de Vida</div>' +
        '<div class="text-2xl font-bold text-th-accent">' + fmt(data.ddv) + '</div>' +
        '</div>';
    }

    metricsEl.innerHTML = html;
  }

  // ── Inicialización ──
  function init() {
    var calDate  = document.getElementById("cal-date");
    var calBirth = document.getElementById("cal-birth");
    if (!calDate) return;

    // Default: hoy
    var today = new Date();
    var yyyy = today.getFullYear();
    var mm = String(today.getMonth() + 1).padStart(2, "0");
    var dd = String(today.getDate()).padStart(2, "0");
    calDate.value = yyyy + "-" + mm + "-" + dd;

    // Cargar fecha de nacimiento guardada
    var savedBirth = localStorage.getItem("lgc_birth_date");
    if (savedBirth && calBirth) calBirth.value = savedBirth;

    calDate.addEventListener("input", refresh);
    if (calBirth) {
      calBirth.addEventListener("input", function () {
        if (calBirth.value) localStorage.setItem("lgc_birth_date", calBirth.value);
        else localStorage.removeItem("lgc_birth_date");
        refresh();
      });
    }

    // Render inicial (oculto hasta que se active el modo)
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
