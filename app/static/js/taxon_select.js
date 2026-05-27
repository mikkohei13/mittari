/**
 * Reusable taxon name autocomplete (FinBIF /autocomplete/taxa via same-origin proxy).
 *
 * Markup (inside a form):
 *   <div data-taxon-select data-autocomplete-url="...">
 *     <input type="text" class="taxon-select__query" autocomplete="off" />
 *     <input type="hidden" name="taxon_id" value="" />
 *     <ul class="taxon-select__suggestions" hidden></ul>
 *   </div>
 *
 * On pick, hidden input name="taxon_id" is set to result.id (MX-code).
 */
(function () {
  var DEBOUNCE_MS = 220;

  function labelFor(item) {
    var sci = item.scientificName || item.value || item.matchingName || "";
    var vern = item.vernacularName;
    if (vern && sci && vern.toLowerCase() !== sci.toLowerCase()) {
      return sci + " (" + vern + ")";
    }
    return sci || item.matchingName || item.value || item.id;
  }

  function closeList(ul) {
    ul.hidden = true;
    ul.innerHTML = "";
  }

  function init(root) {
    var endpoint =
      root.getAttribute("data-autocomplete-url") || "/api/finbif/autocomplete/taxa";
    var queryInput = root.querySelector(".taxon-select__query");
    var idInput = root.querySelector('input[name="taxon_id"]');
    var ul = root.querySelector(".taxon-select__suggestions");
    if (!queryInput || !idInput || !ul) return;

    var timer = null;
    var lastController = null;

    function scheduleFetch() {
      if (timer) clearTimeout(timer);
      timer = setTimeout(runFetch, DEBOUNCE_MS);
    }

    function runFetch() {
      timer = null;
      var q = queryInput.value.trim();
      if (lastController) lastController.abort();
      if (!q) {
        closeList(ul);
        return;
      }

      lastController = new AbortController();
      var params = new URLSearchParams({ query: q });
      fetch(endpoint + "?" + params.toString(), {
        signal: lastController.signal,
        headers: { Accept: "application/json" },
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          var results = data.results;
          if (!Array.isArray(results) || results.length === 0) {
            closeList(ul);
            return;
          }
          ul.innerHTML = "";
          results.forEach(function (item) {
            var id = item.id;
            if (!id) return;
            var li = document.createElement("li");
            li.className = "taxon-select__suggestion";
            var btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = labelFor(item);
            btn.addEventListener("click", function () {
              idInput.value = id;
              queryInput.value = labelFor(item);
              closeList(ul);
            });
            li.appendChild(btn);
            ul.appendChild(li);
          });
          ul.hidden = ul.childElementCount === 0;
        })
        .catch(function (err) {
          if (err.name === "AbortError") return;
          closeList(ul);
        });
    }

    queryInput.addEventListener("input", function () {
      scheduleFetch();
    });

    queryInput.addEventListener("focus", function () {
      if (ul.childElementCount) ul.hidden = false;
    });

    document.addEventListener("click", function (ev) {
      if (!root.contains(ev.target)) closeList(ul);
    });
  }

  document.querySelectorAll("[data-taxon-select]").forEach(init);
})();
