/**
 * Year dropdown: 1970 … current year, plus "Kaikki vuodet" (empty value).
 *
 *   <div data-year-select data-selected-year="2020" data-min-year="1970">
 *     <label for="y">Vuosi</label>
 *     <select id="y" name="year"></select>
 *   </div>
 *
 * Optional: data-max-year (defaults to calendar year in the browser).
 */
(function () {
  var DEFAULT_MIN = 1970;

  function init(root) {
    var sel = root.querySelector("select[name='year']");
    if (!sel) return;

    var maxY = parseInt(root.getAttribute("data-max-year"), 10);
    if (isNaN(maxY)) maxY = new Date().getFullYear();

    var minY = parseInt(root.getAttribute("data-min-year"), 10);
    if (isNaN(minY)) minY = DEFAULT_MIN;
    if (minY > maxY) minY = maxY;

    var selected = (root.getAttribute("data-selected-year") || "").trim();

    sel.innerHTML = "";
    var all = document.createElement("option");
    all.value = "";
    all.textContent = "Kaikki vuodet";
    sel.appendChild(all);

    for (var y = maxY; y >= minY; y--) {
      var opt = document.createElement("option");
      opt.value = String(y);
      opt.textContent = String(y);
      sel.appendChild(opt);
    }

    if (selected && sel.querySelector('option[value="' + selected + '"]')) {
      sel.value = selected;
    } else {
      sel.value = "";
    }
  }

  document.querySelectorAll("[data-year-select]").forEach(init);
})();
