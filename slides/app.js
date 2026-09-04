(function () {
  var slides = [].slice.call(document.querySelectorAll(".slide"));
  var i = 0;
  var bar = document.getElementById("bar");
  var count = document.getElementById("count");
  var fa = "۰۱۲۳۴۵۶۷۸۹";

  function faNum(n) {
    return String(n).replace(/[0-9]/g, function (d) { return fa[d]; });
  }

  function toFaDigits(s) {
    s = String(s);
    var prev = "";
    while (s !== prev) {
      prev = s;
      s = s.replace(/([0-9۰-۹])\.([0-9۰-۹])/g, "$1٫$2");
    }
    return s.replace(/[0-9]/g, function (d) { return fa[d]; });
  }

  function persianize(root) {
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    while (w.nextNode()) nodes.push(w.currentNode);
    nodes.forEach(function (n) {
      if (!n.parentElement) return;
      if (n.parentElement.closest(".katex, .katex-mathml, script, style")) return;
      if (!n.nodeValue || !/[0-9]/.test(n.nodeValue)) return;
      n.nodeValue = toFaDigits(n.nodeValue);
    });
  }

  function go(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, k) { s.classList.toggle("on", k === i); });
    bar.style.width = ((i + 1) / slides.length * 100) + "%";
    count.textContent = faNum(i + 1) + " / " + faNum(slides.length);
    history.replaceState(null, "", "#s" + (i + 1));
  }

  function parseHash() {
    var m = location.hash.match(/s(\d+)/);
    return m ? parseInt(m[1], 10) - 1 : 0;
  }

  document.addEventListener("keydown", function (e) {
    if (["INPUT", "TEXTAREA"].indexOf(e.target.tagName) >= 0) return;
    if (e.key === "ArrowLeft" || e.key === "ArrowDown" || e.key === " " || e.key === "PageDown") {
      e.preventDefault(); go(i + 1);
    } else if (e.key === "ArrowRight" || e.key === "ArrowUp" || e.key === "PageUp" || e.key === "Backspace") {
      e.preventDefault(); go(i - 1);
    } else if (e.key === "Home") go(0);
    else if (e.key === "End") go(slides.length - 1);
    else if (e.key === "n" || e.key === "N") document.body.classList.toggle("show-notes");
    else if (e.key === "f" || e.key === "F") {
      if (!document.fullscreenElement) document.documentElement.requestFullscreen();
      else document.exitFullscreen();
    } else if (e.key === "?" || e.key === "h" || e.key === "H") {
      document.body.classList.toggle("help-on");
    } else if (e.key === "Escape") document.body.classList.remove("help-on");
  });

  document.getElementById("deck").addEventListener("click", function (e) {
    if (e.target.closest("a")) return;
    var x = e.clientX / window.innerWidth;
    if (x < 0.28) go(i + 1);
    else if (x > 0.72) go(i - 1);
  });

  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: "\\[", right: "\\]", display: true },
        { left: "\\(", right: "\\)", display: false }
      ],
      throwOnError: false
    });
  }
  persianize(document.getElementById("deck"));

  go(parseHash());
  window.addEventListener("hashchange", function () { go(parseHash()); });
})();
