/**
 * LgcAutocomplete — Componente autocomplete ES5 con glass-morphism.
 *
 * Uso:
 *   var ac = LgcAutocomplete(inputEl, {
 *     data:      [],            // [{label,value,extra}] o ["string"]
 *     onSelect:  function(item){},
 *     onClear:   function(){},
 *     minChars:  1,
 *     maxResults: 8,
 *     strict:    false,         // true = limpia si no coincide al blur
 *     displayFn: null           // function(item) → string para mostrar en lista
 *   });
 *
 *   ac.setData(newArray);       // actualizar datos (ej. ciudades al cambiar país)
 *   ac.setValue(value);         // setear valor programáticamente
 */
var LgcAutocomplete = (function () {
  "use strict";

  // ── Helpers ──

  /** Normaliza string: lowercase + sin acentos */
  function normalize(s) {
    if (!s) return "";
    return s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  }

  /** Convierte item a formato uniforme {label, value, extra} */
  function toItem(raw) {
    if (typeof raw === "string") {
      return { label: raw, value: raw, extra: null };
    }
    return raw;
  }

  // ── Constructor ──

  function Autocomplete(inputEl, opts) {
    if (!(this instanceof Autocomplete)) {
      return new Autocomplete(inputEl, opts);
    }

    var self = this;
    opts = opts || {};

    self.input = inputEl;
    self.onSelect = opts.onSelect || function () {};
    self.onClear = opts.onClear || function () {};
    self.minChars = opts.minChars != null ? opts.minChars : 1;
    self.maxResults = opts.maxResults || 8;
    self.strict = !!opts.strict;
    self.displayFn = opts.displayFn || null;
    self._data = [];
    self._filtered = [];
    self._activeIdx = -1;
    self._selected = null;    // item seleccionado actualmente
    self._open = false;
    self._mouseDown = false;  // evitar blur antes del click

    // Convertir data inicial
    self.setData(opts.data || []);

    // ── DOM: wrapper ──
    var wrap = document.createElement("div");
    wrap.className = "lgc-ac-wrap";
    inputEl.parentNode.insertBefore(wrap, inputEl);
    wrap.appendChild(inputEl);

    // ── DOM: lista ──
    var list = document.createElement("ul");
    list.className = "lgc-ac-list";
    list.style.display = "none";
    wrap.appendChild(list);
    self._list = list;

    // ── Atributos del input ──
    inputEl.setAttribute("autocomplete", "off");
    inputEl.setAttribute("role", "combobox");
    inputEl.setAttribute("aria-autocomplete", "list");
    inputEl.setAttribute("aria-expanded", "false");

    // ── Debounce timer ──
    var debounceTimer = null;

    // ── Events ──

    inputEl.addEventListener("input", function () {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function () {
        self._selected = null;
        self._filter();
        self._render();
        self._show();
      }, 80);
    });

    inputEl.addEventListener("focus", function () {
      if (self.input.value.length >= self.minChars) {
        self._filter();
        self._render();
        self._show();
      }
    });

    inputEl.addEventListener("blur", function () {
      // Si mouseDown en la lista, no cerrar (el click lo maneja)
      if (self._mouseDown) return;

      setTimeout(function () {
        self._hide();
        // strict mode: si no hay selección válida, limpiar
        if (self.strict && !self._selected) {
          var val = self.input.value.trim();
          if (val) {
            // intentar match exacto
            var match = self._findExact(val);
            if (match) {
              self._doSelect(match);
            } else {
              self.input.value = "";
              self.onClear();
            }
          } else {
            self.onClear();
          }
        }
      }, 120);
    });

    inputEl.addEventListener("keydown", function (e) {
      if (!self._open) {
        if (e.keyCode === 40) { // ArrowDown
          self._filter();
          self._render();
          self._show();
          e.preventDefault();
        }
        return;
      }

      switch (e.keyCode) {
        case 40: // ArrowDown
          e.preventDefault();
          self._move(1);
          break;
        case 38: // ArrowUp
          e.preventDefault();
          self._move(-1);
          break;
        case 13: // Enter
          e.preventDefault();
          if (self._activeIdx >= 0 && self._activeIdx < self._filtered.length) {
            self._doSelect(self._filtered[self._activeIdx]);
          }
          break;
        case 27: // Escape
          e.preventDefault();
          self._hide();
          break;
        case 9: // Tab
          self._hide();
          break;
      }
    });

    // Evitar que blur cierre antes del click en la lista
    list.addEventListener("mousedown", function (e) {
      e.preventDefault();
      self._mouseDown = true;
    });

    list.addEventListener("mouseup", function () {
      self._mouseDown = false;
    });

    // Cerrar al hacer click fuera
    document.addEventListener("click", function (e) {
      if (!wrap.contains(e.target)) {
        self._hide();
      }
    });
  }

  // ── Prototype ──

  Autocomplete.prototype.setData = function (data) {
    var self = this;
    self._data = [];
    for (var i = 0; i < (data || []).length; i++) {
      self._data.push(toItem(data[i]));
    }
    self._filtered = [];
    self._activeIdx = -1;
  };

  Autocomplete.prototype.setValue = function (value, label) {
    var self = this;
    if (!value) {
      self.input.value = "";
      self._selected = null;
      return;
    }
    // Buscar en data
    for (var i = 0; i < self._data.length; i++) {
      if (self._data[i].value === value) {
        self._selected = self._data[i];
        self.input.value = label || self._data[i].label;
        return;
      }
    }
    // Fallback
    self.input.value = label || value;
    self._selected = { label: label || value, value: value, extra: null };
  };

  Autocomplete.prototype._filter = function () {
    var self = this;
    var query = normalize(self.input.value);
    self._filtered = [];
    self._activeIdx = -1;

    if (query.length < self.minChars) return;

    // Separar matches: empieza con query vs contiene query
    var startsWith = [];
    var contains = [];

    for (var i = 0; i < self._data.length; i++) {
      var item = self._data[i];
      var norm = normalize(item.label);
      if (norm.indexOf(query) === 0) {
        startsWith.push(item);
      } else if (norm.indexOf(query) > 0) {
        contains.push(item);
      }
      if (startsWith.length + contains.length >= self.maxResults) break;
    }

    self._filtered = startsWith.concat(contains).slice(0, self.maxResults);
  };

  Autocomplete.prototype._findExact = function (text) {
    var norm = normalize(text);
    for (var i = 0; i < this._data.length; i++) {
      if (normalize(this._data[i].label) === norm) {
        return this._data[i];
      }
    }
    return null;
  };

  Autocomplete.prototype._render = function () {
    var self = this;
    var list = self._list;
    list.innerHTML = "";

    if (self._filtered.length === 0) {
      var empty = document.createElement("li");
      empty.className = "lgc-ac-empty";
      empty.textContent = self.input.value.length >= self.minChars
        ? "Sin resultados"
        : "";
      if (empty.textContent) list.appendChild(empty);
      return;
    }

    for (var i = 0; i < self._filtered.length; i++) {
      (function (idx) {
        var item = self._filtered[idx];
        var li = document.createElement("li");
        li.className = "lgc-ac-item";
        if (idx === self._activeIdx) li.className += " lgc-ac-active";

        // Texto a mostrar
        var text = self.displayFn ? self.displayFn(item) : item.label;
        li.textContent = text;

        li.addEventListener("click", function () {
          self._doSelect(item);
          self._mouseDown = false;
        });

        li.addEventListener("mouseenter", function () {
          // Quitar active del anterior
          var prev = list.querySelector(".lgc-ac-active");
          if (prev) prev.className = "lgc-ac-item";
          li.className = "lgc-ac-item lgc-ac-active";
          self._activeIdx = idx;
        });

        list.appendChild(li);
      })(i);
    }
  };

  Autocomplete.prototype._doSelect = function (item) {
    var self = this;
    self._selected = item;
    self.input.value = item.label;
    self._hide();
    self.onSelect(item);
  };

  Autocomplete.prototype._move = function (delta) {
    var self = this;
    var len = self._filtered.length;
    if (len === 0) return;

    self._activeIdx += delta;
    if (self._activeIdx < 0) self._activeIdx = len - 1;
    if (self._activeIdx >= len) self._activeIdx = 0;

    // Actualizar clases
    var items = self._list.querySelectorAll(".lgc-ac-item");
    for (var i = 0; i < items.length; i++) {
      items[i].className = "lgc-ac-item" + (i === self._activeIdx ? " lgc-ac-active" : "");
    }

    // Scroll into view
    if (items[self._activeIdx]) {
      items[self._activeIdx].scrollIntoView({ block: "nearest" });
    }
  };

  Autocomplete.prototype._show = function () {
    var self = this;
    if (self._filtered.length === 0 && self.input.value.length < self.minChars) {
      self._hide();
      return;
    }
    self._list.style.display = "";
    self._open = true;
    self.input.setAttribute("aria-expanded", "true");
  };

  Autocomplete.prototype._hide = function () {
    var self = this;
    self._list.style.display = "none";
    self._open = false;
    self._activeIdx = -1;
    self.input.setAttribute("aria-expanded", "false");
  };

  return Autocomplete;
})();
