(function () {
  "use strict";

  function compareNatural(a, b) {
    return String(a || "").localeCompare(String(b || ""), undefined, {
      numeric: true,
      sensitivity: "base",
    });
  }

  function parseYearValue(raw) {
    if (raw === null || raw === undefined) return null;
    var s = String(raw).trim();
    if (!s) return null;
    if (/^[+-]?\d+$/.test(s)) return parseInt(s, 10);
    var primary = s.split("/")[0].trim();
    var isBce = /\b(?:bce|bc)\b/i.test(primary);
    var m = primary.match(/[+-]?\d+/);
    if (!m) return null;
    var num = parseInt(m[0], 10);
    if (isNaN(num)) return null;
    return isBce && num > 0 ? -num : num;
  }

  function compareYears(rawA, rawB, desc, titleA, titleB) {
    var ya = parseYearValue(rawA);
    var yb = parseYearValue(rawB);
    if (ya === null && yb === null) return compareNatural(titleA, titleB);
    if (ya === null) return 1;
    if (yb === null) return -1;
    var diff = desc ? yb - ya : ya - yb;
    return diff || compareNatural(titleA, titleB);
  }

  function initCollectionDirectory(section) {
    var controls = section.querySelector(".collection-directory-controls");
    var grid = section.querySelector(".collection-directory-grid");
    if (!controls || !grid) return;

    var cards = Array.prototype.slice.call(grid.querySelectorAll(".collection-directory-card"));
    if (!cards.length) return;

    var hasDeath = cards.some(function (c) { return parseYearValue(c.getAttribute("data-death-year")) !== null; });
    var hasYear = cards.some(function (c) { return parseYearValue(c.getAttribute("data-year")) !== null; });
    var hasPub = cards.some(function (c) { return c.getAttribute("data-published-at") !== ""; });

    var langCounts = {};
    var eraCounts = {};
    cards.forEach(function (c) {
      var rawLangs = c.getAttribute("data-languages") || "";
      rawLangs.split("|").filter(Boolean).forEach(function (l) {
        langCounts[l] = (langCounts[l] || 0) + 1;
      });
      var era = c.getAttribute("data-era") || "";
      if (era) eraCounts[era] = (eraCounts[era] || 0) + 1;
    });

    var sortSel = controls.querySelector(".collection-directory-sort");
    var sortOptions = [];
    if (hasDeath) {
      sortOptions.push(["death_asc", "Sort: Date (Ancient → Modern)"]);
      sortOptions.push(["death_desc", "Sort: Date (Modern → Ancient)"]);
    }
    if (hasPub) {
      sortOptions.push(["pub_desc", "Sort: Publish Date (Newest First)"]);
      sortOptions.push(["pub_asc", "Sort: Publish Date (Oldest First)"]);
    }
    if (hasYear) {
      sortOptions.push(["year_asc", "Sort: Year (Earliest → Latest)"]);
      sortOptions.push(["year_desc", "Sort: Year (Latest → Earliest)"]);
    }
    sortOptions.push(["title_asc", "Sort: Title (A → Z)"]);
    sortOptions.push(["title_desc", "Sort: Title (Z → A)"]);

    sortSel.innerHTML = sortOptions
      .map(function (opt) { return '<option value="' + opt[0] + '">' + opt[1] + "</option>"; })
      .join("");

    var params = new URLSearchParams(window.location.search);
    var defaultSort = hasDeath ? "death_asc" : (hasPub ? "pub_desc" : (hasYear ? "year_asc" : "title_asc"));
    var state = {
      q: params.get("q") || "",
      lang: params.get("lang") || "All",
      era: params.get("era") || "All",
      sort: params.get("sort") || defaultSort,
    };
    sortSel.value = state.sort;

    var searchInp = controls.querySelector(".collection-directory-search");
    searchInp.value = state.q;

    var filtersWrap = controls.querySelector(".collection-directory-filters");
    var filterHtml = "";
    var langs = Object.keys(langCounts).sort();
    if (langs.length > 1) {
      filterHtml += '<div class="collection-directory-pills"><span class="collection-directory-label">Language:</span>';
      ["All"].concat(langs).forEach(function (l) {
        var active = state.lang === l ? " is-active" : "";
        filterHtml += '<button type="button" class="collection-directory-pill' + active + '" data-filter="lang" data-val="' + l + '">' + l + "</button>";
      });
      filterHtml += "</div>";
    }
    var eras = Object.keys(eraCounts);
    if (eras.length > 1) {
      filterHtml += '<div class="collection-directory-pills"><span class="collection-directory-label">Group:</span>';
      ["All"].concat(eras).forEach(function (e) {
        var active = state.era === e ? " is-active" : "";
        filterHtml += '<button type="button" class="collection-directory-pill' + active + '" data-filter="era" data-val="' + e + '">' + e + "</button>";
      });
      filterHtml += "</div>";
    }
    filtersWrap.innerHTML = filterHtml;
    controls.hidden = false;

    function syncUrl() {
      var p = new URLSearchParams();
      if (state.q) p.set("q", state.q);
      if (state.lang !== "All") p.set("lang", state.lang);
      if (state.era !== "All") p.set("era", state.era);
      if (state.sort !== defaultSort) p.set("sort", state.sort);
      var qs = p.toString();
      window.history.replaceState(null, "", window.location.pathname + (qs ? "?" + qs : ""));
    }

    function apply() {
      var qLow = state.q.trim().toLowerCase();
      var visibleCount = 0;

      cards.sort(function (a, b) {
        var ta = a.getAttribute("data-title") || "";
        var tb = b.getAttribute("data-title") || "";
        if (state.sort === "title_asc") return compareNatural(ta, tb);
        if (state.sort === "title_desc") return compareNatural(tb, ta);
        if (state.sort === "death_asc" || state.sort === "death_desc") {
          return compareYears(
            a.getAttribute("data-death-year"),
            b.getAttribute("data-death-year"),
            state.sort === "death_desc",
            ta,
            tb
          );
        }
        if (state.sort === "year_asc" || state.sort === "year_desc") {
          return compareYears(
            a.getAttribute("data-year"),
            b.getAttribute("data-year"),
            state.sort === "year_desc",
            ta,
            tb
          );
        }
        if (state.sort === "pub_desc" || state.sort === "pub_asc") {
          var pa = a.getAttribute("data-published-at") || "";
          var pb = b.getAttribute("data-published-at") || "";
          return state.sort === "pub_desc" ? pb.localeCompare(pa) : pa.localeCompare(pb);
        }
        return 0;
      });

      cards.forEach(function (card) {
        var cLangs = (card.getAttribute("data-languages") || "").split("|").filter(Boolean);
        var cEra = card.getAttribute("data-era") || "";
        var cHay = (card.getAttribute("data-search") || "").toLowerCase();
        var show = true;
        if (state.lang !== "All" && cLangs.indexOf(state.lang) === -1) show = false;
        if (state.era !== "All" && cEra !== state.era) show = false;
        if (qLow && cHay.indexOf(qLow) === -1) show = false;
        card.style.display = show ? "" : "none";
        if (show) visibleCount++;
        grid.appendChild(card);
      });

      var countEl = controls.querySelector(".collection-directory-count");
      if (countEl) countEl.textContent = visibleCount + " of " + cards.length + " records";
    }

    sortSel.addEventListener("change", function () {
      state.sort = sortSel.value;
      syncUrl();
      apply();
    });
    searchInp.addEventListener("input", function () {
      state.q = searchInp.value;
      syncUrl();
      apply();
    });
    filtersWrap.querySelectorAll(".collection-directory-pill").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var fk = btn.getAttribute("data-filter");
        var fv = btn.getAttribute("data-val");
        if (fv && fv !== "All" && state[fk] === fv) {
          fv = "All";
        }
        state[fk] = fv;
        filtersWrap.querySelectorAll('.collection-directory-pill[data-filter="' + fk + '"]').forEach(function (b) {
          b.classList.toggle("is-active", b.getAttribute("data-val") === fv);
        });
        syncUrl();
        apply();
      });
    });

    apply();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".collection-directory").forEach(initCollectionDirectory);
  });
})();
