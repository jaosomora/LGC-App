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
  var PASOS_S   = ["Lóg","Inh","Hum","Ctx"];
  var MEMORIAS  = ["","RAM","REM","ROM","RUM"];
  var FASES     = ["","Asume","Asimila","Desafía","Decide"];
  var MESES     = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
  var MESES_FULL = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
  var DIAS      = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"];
  var DIAS_FULL = ["Domingo","Lunes","Martes","Miércoles","Jueves","Viernes","Sábado"];
  var QUAD_INFO = {
    "NO": { full: "Noroeste",  concepto: "Conciencia" },
    "NE": { full: "Noreste",   concepto: "Mente" },
    "SO": { full: "Suroeste",  concepto: "Soma" },
    "SE": { full: "Sureste",   concepto: "Entorno" }
  };
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

  // ── Timezone label ──
  function getTimezoneLabel() {
    try {
      var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      var offset = new Date().getTimezoneOffset();
      var sign = offset <= 0 ? "+" : "\u2212";
      var h = Math.floor(Math.abs(offset) / 60);
      var m = Math.abs(offset) % 60;
      var utc = "UTC" + sign + h + (m ? ":" + String(m).padStart(2, "0") : "");
      var city = tz.split("/").pop().replace(/_/g, " ");
      return city + " \u00b7 " + utc;
    } catch (e) { return ""; }
  }

  // ── Birth date: 3 estados (empty / editing / set) ──

  // ISO "1990-03-15" → display "15/03/1990"
  function isoToDmy(iso) {
    var p = iso.split("-");
    return p[2] + "/" + p[1] + "/" + p[0];
  }
  // "15/03/1990" → ISO "1990-03-15"
  function dmyToIso(dmy) {
    var p = dmy.split("/");
    return p[2] + "-" + p[1] + "-" + p[0];
  }
  // Valida "DD/MM/AAAA" como fecha real con año >= 1900
  function isValidDmy(dmy) {
    var p = dmy.split("/");
    if (p.length !== 3 || p[2].length !== 4) return false;
    var d = parseInt(p[0], 10), m = parseInt(p[1], 10), y = parseInt(p[2], 10);
    if (y < 1900 || m < 1 || m > 12 || d < 1 || d > 31) return false;
    var date = new Date(y, m - 1, d);
    return date.getFullYear() === y && date.getMonth() === m - 1 && date.getDate() === d;
  }

  function fmtBirthDisplay(iso) {
    var p = iso.split("-").map(Number);
    return p[2] + " " + MESES[p[1] - 1] + " " + p[0];
  }

  function showBirthState(state) {
    var el = {
      empty:   document.getElementById("cal-birth-empty"),
      editing: document.getElementById("cal-birth-editing"),
      set:     document.getElementById("cal-birth-set")
    };
    for (var k in el) if (el[k]) el[k].classList.toggle("hidden", k !== state);
  }

  function updateBirthDisplay() {
    var birthText = document.getElementById("cal-birth-text");
    var saved = localStorage.getItem("lgc_birth_date");
    if (saved) {
      if (birthText) birthText.textContent = fmtBirthDisplay(saved);
      showBirthState("set");
    } else {
      showBirthState("empty");
    }
  }

  // ── Toast de navegación ──
  function showNavToast(msg) {
    var existing = document.getElementById("cal-nav-toast");
    if (existing) existing.remove();

    var toast = document.createElement("div");
    toast.id = "cal-nav-toast";
    toast.className = "fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full text-sm font-medium shadow-lg pointer-events-none";
    toast.style.cssText = "background:rgb(var(--c-accent));color:#fff;opacity:0;transform:translateX(-50%) translateY(10px);transition:opacity 0.3s,transform 0.3s";
    toast.textContent = "✦ " + msg;
    document.body.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(function () {
      toast.style.opacity = "1";
      toast.style.transform = "translateX(-50%) translateY(0)";
    });

    setTimeout(function () {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(-50%) translateY(-10px)";
      setTimeout(function () { toast.remove(); }, 300);
    }, 1800);
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
      cuarentena:cuarentena, year:year, month:month, day:day
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

  // ── Grilla visual 4×4 (plano cartesiano) ──
  // Orden visual: NO(arriba-izq), NE(arriba-der), SO(abajo-izq), SE(abajo-der)
  var GRID_DISPLAY = [
    { name: "NO", start: 9,  mems: [null,null,null,null] },
    { name: "NE", start: 5,  mems: [null,null,null,null] },
    { name: "SO", start: 1,  mems: ["RAM","REM","ROM","RUM"] },
    { name: "SE", start: 13, mems: [null,null,null,null] }
  ];

  function renderGrid(data) {
    var html = '<div class="grid grid-cols-2 mt-4 rounded-xl overflow-hidden" style="border:1px solid var(--glass-border)">';

    for (var q = 0; q < 4; q++) {
      var quad = GRID_DISPLAY[q];
      var isActiveQuad = data.cuad === quad.name;

      // Bordes internos: cruz cartesiana
      var borders = [];
      if (q === 0 || q === 2) borders.push("border-right:1px solid var(--glass-border)");
      if (q === 0 || q === 1) borders.push("border-bottom:1px solid var(--glass-border)");
      if (isActiveQuad) borders.push("background:rgb(var(--c-accent)/0.05)");

      html += '<div class="p-2.5" style="' + borders.join(";") + '">';

      // Label del cuadrante
      var lblCls = isActiveQuad ? "text-th-accent font-bold" : "text-th-text/25";
      html += '<div class="text-[10px] uppercase tracking-wider ' + lblCls + ' mb-1.5 text-center">' + quad.name + '</div>';

      // 4 celdas de posición
      html += '<div class="grid grid-cols-4 gap-1">';
      for (var i = 0; i < 4; i++) {
        var pos = quad.start + i;
        var isActive = data.pos === pos;
        var cls = isActive ? "cal-grid-active" : "cal-grid-cell";
        html += '<div class="' + cls + ' flex flex-col items-center justify-center py-2 rounded-lg cursor-pointer" data-calpos="' + pos + '">';
        html += '<span class="font-bold text-sm">' + pos + '</span>';
        if (quad.mems[i]) {
          html += '<span class="text-[8px] leading-tight mt-0.5 opacity-60">' + quad.mems[i] + '</span>';
        }
        html += '</div>';
      }
      html += '</div>';

      // Etiquetas de paso debajo de las celdas
      html += '<div class="grid grid-cols-4 gap-0 mt-0.5">';
      for (var j = 0; j < 4; j++) {
        html += '<div class="text-[6px] sm:text-[7px] uppercase text-th-text/20 text-center leading-tight">' +
          '<span class="hidden sm:inline">' + PASOS[j] + '</span>' +
          '<span class="sm:hidden">' + PASOS_S[j] + '</span>' +
          '</div>';
      }
      html += '</div>';

      html += '</div>';
    }

    html += '</div>';
    return html;
  }

  // ── Vista Cardinalidad: cuadrante activo con info enriquecida ──
  function renderFocusView(data) {
    // Encontrar el cuadrante activo
    var activeQuad = null;
    for (var q = 0; q < GRID_DISPLAY.length; q++) {
      if (GRID_DISPLAY[q].name === data.cuad) { activeQuad = GRID_DISPLAY[q]; break; }
    }
    if (!activeQuad) return "";

    var qi = QUAD_INFO[activeQuad.name];
    var hasMems = activeQuad.name === "SO";

    // Fecha de consulta como referencia
    var refDate = new Date(data.year, data.month - 1, data.day, 12, 0, 0);

    // Pre-calcular datos de cada posición
    var rows = [];
    for (var i = 0; i < 4; i++) {
      var pos = activeQuad.start + i;
      var offset = pos - data.pos;
      var posDate = new Date(refDate.getTime() + offset * ms);
      var posDoy = data.doy + offset;
      var posDs = data.ds + offset;
      rows.push({
        pos: pos,
        isActive: data.pos === pos,
        paso: PASOS[i],
        mem: activeQuad.mems[i],
        date: posDate,
        dayShort: DIAS[posDate.getDay()],
        dayFull: DIAS_FULL[posDate.getDay()],
        dateDay: posDate.getDate(),
        dateMes: MESES[posDate.getMonth()],
        dateMesFull: MESES_FULL[posDate.getMonth()],
        dateYear: posDate.getFullYear(),
        ds: posDs,
        doy: posDoy,
        total: data.total
      });
    }

    var html = '<div class="mt-4 rounded-xl overflow-hidden" style="border:1px solid var(--glass-border)">';

    // Header: flechas + nombre completo + concepto
    // Calcular posiciones destino para prev/next cuadrante (misma posición relativa)
    var stepInQuad = (data.pos - 1) % 4;
    var qIdx = Math.floor((data.pos - 1) / 4);
    var prevPos = ((qIdx + 3) % 4) * 4 + 1 + stepInQuad;
    var nextPos = ((qIdx + 1) % 4) * 4 + 1 + stepInQuad;
    var prevQuad = CARD_MAP[prevPos - 1];
    var nextQuad = CARD_MAP[nextPos - 1];
    var prevQI = QUAD_INFO[prevQuad];
    var nextQI = QUAD_INFO[nextQuad];

    html += '<div class="flex items-center justify-between px-3 py-2" style="background:rgb(var(--c-accent)/0.05);border-bottom:1px solid var(--glass-border)">';
    // Flecha prev
    html += '<button data-calquad-nav="prev" class="flex items-center gap-1 text-th-text/25 hover:text-th-accent transition-colors cursor-pointer" title="' + prevQuad + ' · ' + prevQI.concepto + '">';
    html += '<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>';
    html += '<span class="text-[10px] font-semibold hidden sm:inline">' + prevQuad + '</span>';
    html += '</button>';
    // Centro
    html += '<div class="text-center">';
    html += '<span class="text-sm font-bold text-th-accent">' + activeQuad.name + '</span>';
    html += '<span class="text-[10px] text-th-text/20 mx-2">·</span>';
    html += '<span class="text-xs text-th-text/50">' + qi.concepto + '</span>';
    html += '<span class="text-[10px] text-th-text/20 mx-2">·</span>';
    html += '<span class="text-xs text-th-text/30 italic">' + qi.full + '</span>';
    html += '</div>';
    // Flecha next
    html += '<button data-calquad-nav="next" class="flex items-center gap-1 text-th-text/25 hover:text-th-accent transition-colors cursor-pointer" title="' + nextQuad + ' · ' + nextQI.concepto + '">';
    html += '<span class="text-[10px] font-semibold hidden sm:inline">' + nextQuad + '</span>';
    html += '<svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>';
    html += '</button>';
    html += '</div>';

    // ── Desktop: tabla con columnas y separadores (hidden en mobile) ──
    var colBorder = "border-left:1px solid var(--glass-divider)";
    var gridCols = "grid-template-columns:1fr" + (hasMems ? " auto" : "") + " 100px 50px 1fr";
    html += '<div class="hidden sm:block">';

    // Header de columnas
    html += '<div class="grid text-[10px] uppercase tracking-wider text-th-text/25" style="border-bottom:1px solid var(--glass-border);background:rgb(255 255 255/0.02);' + gridCols + '">';
    html += '<span class="px-3 py-1.5">Posición</span>';
    if (hasMems) html += '<span class="px-3 py-1.5 text-center" style="' + colBorder + '">Mem</span>';
    html += '<span class="px-3 py-1.5 text-right" style="' + colBorder + '">Día Solar</span>';
    html += '<span class="px-3 py-1.5 text-right" style="' + colBorder + '">Día</span>';
    html += '<span class="px-3 py-1.5 text-right" style="' + colBorder + '">Fecha</span>';
    html += '</div>';

    // Filas desktop
    for (var d = 0; d < 4; d++) {
      var r = rows[d];
      var rowBg = r.isActive ? "background:rgb(var(--c-accent)/0.08)" : "";
      var borderB = d < 3 ? "border-bottom:1px solid var(--glass-border);" : "";

      html += '<div class="grid items-stretch cursor-pointer" data-calpos="' + r.pos + '" style="' + borderB + rowBg + ';' + gridCols + '">';

      // Posición + nombre
      var numCls = r.isActive ? "text-th-accent font-bold" : "text-th-text/50 font-semibold";
      var pasoCls = r.isActive ? "font-semibold" : "text-th-text/60";
      html += '<span class="text-sm flex items-center gap-1.5 px-3 py-2.5">';
      if (r.isActive) {
        html += '<span class="inline-block w-1.5 h-1.5 rounded-full flex-shrink-0" style="background:rgb(var(--c-accent))"></span>';
      } else {
        html += '<span class="inline-block w-1.5 flex-shrink-0"></span>';
      }
      html += '<span class="text-base ' + numCls + '">' + r.pos + '</span>';
      html += '<span class="' + pasoCls + '">' + r.paso + '</span>';
      html += '</span>';

      // Memoria (solo SO)
      if (hasMems) {
        var memCls = r.isActive ? "text-th-accent/70" : "text-th-text/30";
        html += '<span class="text-[10px] uppercase font-semibold flex items-center justify-center px-2" style="' + colBorder + '">' + (r.mem || '') + '</span>';
      }

      // Día Solar
      var dsCls = r.isActive ? "text-th-accent/80 font-semibold" : "text-th-text/35";
      html += '<span class="text-xs tabular-nums flex items-center justify-end px-3 ' + dsCls + '" style="' + colBorder + '">' + r.ds + '</span>';

      // Día del Año (solo número)
      var doyCls = r.isActive ? "text-th-accent/80 font-semibold" : "text-th-text/35";
      html += '<span class="text-xs tabular-nums flex items-center justify-end px-3 ' + doyCls + '" style="' + colBorder + '">' + r.doy + '</span>';

      // Fecha completa (Domingo 15 marzo 2026)
      var dateCls = r.isActive ? "text-th-accent/80" : "text-th-text/30";
      html += '<span class="text-xs tabular-nums flex items-center justify-end px-3 ' + dateCls + ' whitespace-nowrap" style="' + colBorder + '">' +
        r.dayFull + ' ' + r.dateDay + ' ' + r.dateMesFull + ' ' + r.dateYear + '</span>';

      html += '</div>';
    }

    html += '</div>';

    // ── Mobile: 2 líneas por fila (hidden en desktop) ──
    html += '<div class="sm:hidden">';

    for (var m = 0; m < 4; m++) {
      var r = rows[m];
      var rowBg = r.isActive ? "background:rgb(var(--c-accent)/0.08)" : "";
      var borderB = m < 3 ? "border-bottom:1px solid var(--glass-border);" : "";

      html += '<div class="px-3 py-2 cursor-pointer" data-calpos="' + r.pos + '" style="' + borderB + rowBg + '">';

      // Línea 1: indicador + posición + nombre + [mem] + fecha
      html += '<div class="flex items-center gap-2">';
      if (r.isActive) {
        html += '<div class="w-1.5 h-1.5 rounded-full flex-shrink-0" style="background:rgb(var(--c-accent))"></div>';
      } else {
        html += '<div class="w-1.5 flex-shrink-0"></div>';
      }
      var numCls = r.isActive ? "text-th-accent font-bold" : "text-th-text/50 font-semibold";
      html += '<span class="text-sm ' + numCls + ' w-5 text-right">' + r.pos + '</span>';
      var pasoCls = r.isActive ? "font-semibold" : "text-th-text/60";
      html += '<span class="text-sm ' + pasoCls + ' flex-1">' + r.paso;
      if (r.mem) {
        var memCls = r.isActive ? "text-th-accent/70" : "text-th-text/30";
        html += ' <span class="text-[10px] uppercase font-semibold ' + memCls + '">· ' + r.mem + '</span>';
      }
      html += '</span>';
      var dateCls = r.isActive ? "text-th-accent/80" : "text-th-text/30";
      html += '<span class="text-xs tabular-nums ' + dateCls + ' whitespace-nowrap">' +
        r.dayShort + ' ' + r.dateDay + ' ' + r.dateMes + '</span>';
      html += '</div>';

      // Línea 2: DS + Día del Año
      var subCls = r.isActive ? "text-th-accent/40" : "text-th-text/20";
      html += '<div class="text-[10px] tabular-nums ' + subCls + ' ml-7 mt-0.5">';
      html += 'DS ' + r.ds + ' · Día ' + r.doy + '/' + r.total;
      html += '</div>';

      html += '</div>';
    }

    html += '</div>';

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
      var calView = localStorage.getItem("lgc_cal_view") || "cuadrantes";

      html += '<div class="glass-card p-5">';
      html += '<div class="text-center">';
      html += '<div class="text-xs uppercase tracking-wider text-th-text/40 mb-1">Posición Calendaria</div>';
      var memStr = data.mem ? " · " + data.mem : "";
      html += '<div class="text-2xl sm:text-3xl font-bold text-th-accent">V' + data.vAbs + ' · ' + data.pos + '/16</div>';
      html += '<div class="text-sm text-th-text/50 mt-1">' + data.cuad + ' · ' + data.paso + memStr + '</div>';
      html += '<div class="text-xs text-th-text/40 mt-0.5">Vuelta ' + data.vRel + '</div>';
      html += '</div>';
      html += progressBar(data.pos, 16, "Posición en la vuelta");

      // Toggle Cuadrantes / Cardinalidad
      var cuadActive = calView === "cuadrantes";
      var cardActive = calView === "cardinalidad";
      html += '<div class="flex justify-center gap-1.5 mt-3 mb-1">';
      html += '<button data-calview="cuadrantes" class="px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider transition-all ' +
        (cuadActive ? 'text-th-accent' : 'text-th-text/30 hover:text-th-text/50') + '"' +
        (cuadActive ? ' style="background:rgb(var(--c-accent)/0.12)"' : '') +
        '>Cuadrantes</button>';
      html += '<button data-calview="cardinalidad" class="px-3 py-1 rounded-full text-[11px] font-semibold uppercase tracking-wider transition-all ' +
        (cardActive ? 'text-th-accent' : 'text-th-text/30 hover:text-th-text/50') + '"' +
        (cardActive ? ' style="background:rgb(var(--c-accent)/0.12)"' : '') +
        '>Cardinalidad</button>';
      html += '</div>';

      // Renderizar según vista seleccionada
      if (calView === "cardinalidad") {
        html += renderFocusView(data);
      } else {
        html += renderGrid(data);
      }

      html += '</div>';
    }

    // ── 3. Métricas adicionales ──
    html += '<div class="grid grid-cols-2 gap-3">';

    // Aparato (contenedor mayor: 1461 días / 4 años)
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
    var btnToday = document.getElementById("cal-today");
    if (!calDate) return;

    // Default: hoy (zona horaria local del usuario)
    var today = new Date();
    calDate.value = toDateStr(today);

    // Event listeners
    calDate.addEventListener("input", refresh);

    // Birth date: input de texto con auto-formato DD/MM/AAAA
    if (calBirth) {
      calBirth.addEventListener("input", function () {
        // Solo dígitos, formatear con /
        var raw = calBirth.value.replace(/\D/g, "");
        var fmt = "";
        if (raw.length > 0) fmt += raw.substring(0, 2);
        if (raw.length > 2) fmt += "/" + raw.substring(2, 4);
        if (raw.length > 4) fmt += "/" + raw.substring(4, 8);
        calBirth.value = fmt;
        // Cuando tiene 10 chars (DD/MM/AAAA) y es válida → guardar y mostrar badge
        if (fmt.length === 10 && isValidDmy(fmt)) {
          localStorage.setItem("lgc_birth_date", dmyToIso(fmt));
          updateBirthDisplay();
          refresh();
        }
      });
    }
    if (btnPrev) btnPrev.addEventListener("click", function () { shiftDate(-1); });
    if (btnNext) btnNext.addEventListener("click", function () { shiftDate(1); });
    if (btnToday) btnToday.addEventListener("click", function () {
      calDate.value = toDateStr(new Date());
      refresh();
    });

    // Birth date: handlers de estado
    var birthAdd    = document.getElementById("cal-birth-add");
    var birthEdit   = document.getElementById("cal-birth-edit");
    var birthCancel = document.getElementById("cal-birth-cancel");
    var birthClear  = document.getElementById("cal-birth-clear");

    if (birthAdd) birthAdd.addEventListener("click", function () {
      if (calBirth) calBirth.value = "";
      showBirthState("editing");
      if (calBirth) calBirth.focus();
    });
    if (birthEdit) birthEdit.addEventListener("click", function () {
      var saved = localStorage.getItem("lgc_birth_date");
      if (calBirth) calBirth.value = saved ? isoToDmy(saved) : "";
      showBirthState("editing");
      if (calBirth) calBirth.focus();
    });
    if (birthCancel) birthCancel.addEventListener("click", function () {
      var prev = localStorage.getItem("lgc_birth_date");
      if (prev) updateBirthDisplay();
      else showBirthState("empty");
    });
    if (birthClear) birthClear.addEventListener("click", function () {
      if (calBirth) calBirth.value = "";
      localStorage.removeItem("lgc_birth_date");
      showBirthState("empty");
      refresh();
    });

    // Timezone indicator
    var tzEl = document.getElementById("cal-tz");
    if (tzEl) {
      var label = getTimezoneLabel();
      if (label) tzEl.querySelector("span").textContent = label;
      else tzEl.classList.add("hidden");
    }

    // Estado inicial birth date
    updateBirthDisplay();

    // Toggle Cuadrantes/Cardinalidad (event delegation)
    document.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-calview]");
      if (!btn) return;
      var view = btn.getAttribute("data-calview");
      localStorage.setItem("lgc_cal_view", view);
      refresh();
    });

    // Navegación entre cardinalidades (flechas prev/next)
    document.addEventListener("click", function (e) {
      var nav = e.target.closest("[data-calquad-nav]");
      if (!nav) return;
      var dir = nav.getAttribute("data-calquad-nav");
      var calDate = document.getElementById("cal-date");
      if (!calDate || !calDate.value) return;
      var p = calDate.value.split("-").map(Number);
      var currentDoy = dFrom(dt(p[0],1,1), dt(p[0],p[1],p[2])) + 1;
      if (currentDoy > 352) return;
      var currentPos = (currentDoy - 1) % 16 + 1;
      var stepInQ = (currentPos - 1) % 4;
      var qI = Math.floor((currentPos - 1) / 4);
      var newQI = dir === "next" ? (qI + 1) % 4 : (qI + 3) % 4;
      var targetPos = newQI * 4 + 1 + stepInQ;
      var offset = targetPos - currentPos;
      if (offset === 0) return;

      var targetQuad = CARD_MAP[targetPos - 1];
      var tqi = QUAD_INFO[targetQuad];
      var toastMsg = targetQuad + " · " + tqi.concepto;

      shiftDate(offset);
      showNavToast(toastMsg);
    });

    // Navegación por click en posición (event delegation)
    document.addEventListener("click", function (e) {
      var cell = e.target.closest("[data-calpos]");
      if (!cell) return;
      if (cell.hasAttribute("data-calview")) return;
      var targetPos = parseInt(cell.getAttribute("data-calpos"), 10);
      if (isNaN(targetPos)) return;
      var calDate = document.getElementById("cal-date");
      if (!calDate || !calDate.value) return;
      var p = calDate.value.split("-").map(Number);
      var currentDoy = dFrom(dt(p[0],1,1), dt(p[0],p[1],p[2])) + 1;
      if (currentDoy > 352) return;
      var currentPos = (currentDoy - 1) % 16 + 1;
      var offset = targetPos - currentPos;
      if (offset === 0) return;

      // Calcular info de la posición destino para el toast
      var targetDate = new Date(p[0], p[1] - 1, p[2], 12, 0, 0);
      targetDate.setDate(targetDate.getDate() + offset);
      var step = (targetPos - 1) % 4;
      var toastMsg = "Posición " + targetPos + " · " + PASOS[step] + " · " +
        DIAS[targetDate.getDay()] + " " + targetDate.getDate() + " " + MESES[targetDate.getMonth()];

      shiftDate(offset);
      showNavToast(toastMsg);
    });

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
    var savedBirth = localStorage.getItem("lgc_birth_date");
    if (savedBirth) {
      var bp = savedBirth.split("-").map(Number);
      nacY = bp[0]; nacM = bp[1]; nacD = bp[2];
    }

    var data = calcular(year, month, day, nacY, nacM, nacD);
    render(data);
  }

  document.addEventListener("DOMContentLoaded", init);
  window.LGCCalendaria = { refresh: refresh };

})();
