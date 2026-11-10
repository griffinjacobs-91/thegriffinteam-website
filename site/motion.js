/* The Griffin Team · motion layer. See motion.css for what each piece does and why.
   One-shot reveals (IntersectionObserver), pointer effects on a single rAF, no scroll listeners. */
(function () {
  if (!window.matchMedia || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;
  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---- split headline words into masked spans, keeping <em>, <br> and the like ---- */
  function split(el, cls, mask) {
    var i = 0;
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (n) {
        if (n.nodeType === 1) { if (n.tagName !== "BR") walk(n); return; }
        if (n.nodeType !== 3 || !n.nodeValue.trim()) return;
        var frag = document.createDocumentFragment();
        n.nodeValue.split(/(\s+)/).forEach(function (t) {
          if (!t) return;
          if (/^\s+$/.test(t)) { frag.appendChild(document.createTextNode(t)); return; }
          var inner = document.createElement("span");
          inner.className = cls; inner.textContent = t; inner.style.setProperty("--i", i++);
          if (mask) { var m = document.createElement("span"); m.className = "mo-w"; m.appendChild(inner); frag.appendChild(m); }
          else frag.appendChild(inner);
        });
        n.parentNode.replaceChild(frag, n);
      });
    })(el);
    el.classList.add("mo-split");
  }

  var heads = $$("main h1.sc-display, main h2.sc-display");
  /* screen readers get the heading as one phrase, not word by word */
  heads.forEach(function (h) { h.setAttribute("aria-label", h.textContent.replace(/\s+/g, " ").trim()); split(h, "mo-wi", true); });
  var quotes = $$(".quote--big p");
  quotes.forEach(function (q) { split(q, "mo-rw", false); });

  /* ---- photo frames: curtain reveal; framed photos also settle and drift ---- */
  var pics = $$(".places__pic, .meet__pic-a, .meet__pic-b, .help__pic, .sale__pic, .page-hero__pic, .dane__pic, main figure:not(.hero__card)");
  pics = pics.filter(function (p, i) { return pics.indexOf(p) === i && p.querySelector("img"); });
  pics.forEach(function (p) {
    p.classList.add("mo-pic");
    if (getComputedStyle(p).overflow === "hidden") p.classList.add("mo-zoom");
  });

  /* ---- reveal once on entry ---- */
  var targets = heads.concat(quotes, pics);
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      if (e.isIntersecting || e.boundingClientRect.bottom < 0) { e.target.classList.add("mo-in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.1 });
  targets.forEach(function (t) { io.observe(t); });
  /* nothing stays hidden: anything above the fold on load, or skipped by a fast jump, is shown */
  window.addEventListener("load", function () {
    setTimeout(function () { targets.forEach(function (t) { if (t.getBoundingClientRect().top < innerHeight) t.classList.add("mo-in"); }); }, 1800);
  });
  window.addEventListener("hashchange", function () { targets.forEach(function (t) { t.classList.add("mo-in"); }); });

  /* ---- "10+" counts up when it arrives ---- */
  $$(".ledger__n").forEach(function (n) {
    var t = n.firstChild; if (!t || t.nodeType !== 3) return;
    var end = parseInt(t.nodeValue, 10); if (!(end > 1 && end < 100)) return;
    var cio = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return; cio.disconnect();
      var t0 = performance.now();
      (function tick(now) {
        var k = Math.min(1, (now - t0) / 1400), e = 1 - Math.pow(1 - k, 3);
        t.nodeValue = String(Math.round(end * e));
        if (k < 1) requestAnimationFrame(tick);
      })(t0);
    }, { threshold: 0.6 });
    t.nodeValue = "0"; cio.observe(n);
  });

  if (!fine) return;

  /* ---- cards lean toward the cursor (3 degrees at most) with a soft light ---- */
  $$(".help, .sale, .card, .pcard, .placecard, .tcard, .quote--small, .nbnav").forEach(function (el) {
    el.classList.add("mo-tilt");
    var sheen = document.createElement("span"); sheen.className = "mo-sheen"; sheen.setAttribute("aria-hidden", "true");
    el.appendChild(sheen);
    if (el.parentElement) el.parentElement.style.perspective = "1100px";
    var raf = 0, px = 0, py = 0;
    el.addEventListener("pointermove", function (e) {
      var r = el.getBoundingClientRect();
      px = (e.clientX - r.left) / r.width; py = (e.clientY - r.top) / r.height;
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var max = Math.min(3, 900 / Math.max(r.width, 1));
        var ax = -(py - 0.5), ay = (px - 0.5), mag = Math.sqrt(ax * ax + ay * ay) * 2;
        el.classList.add("is-tilting");
        el.style.rotate = mag ? ax.toFixed(3) + " " + ay.toFixed(3) + " 0 " + (mag * max).toFixed(2) + "deg" : "";
        el.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
        el.style.setProperty("--my", (py * 100).toFixed(1) + "%");
      });
    });
    el.addEventListener("pointerleave", function () { el.classList.remove("is-tilting"); el.style.rotate = ""; });
  });

  /* ---- buttons lean toward the cursor ---- */
  $$(".cta").forEach(function (b) {
    b.addEventListener("pointermove", function (e) {
      var r = b.getBoundingClientRect();
      var dx = (e.clientX - r.left - r.width / 2) / (r.width / 2), dy = (e.clientY - r.top - r.height / 2) / (r.height / 2);
      b.classList.add("is-magnet");
      b.style.setProperty("--tx", (dx * 6).toFixed(1) + "px");
      b.style.setProperty("--ty", (dy * 4).toFixed(1) + "px");
    });
    b.addEventListener("pointerleave", function () { b.classList.remove("is-magnet"); b.style.setProperty("--tx", "0px"); b.style.setProperty("--ty", "0px"); });
  });

  /* ---- home hero: the headshot card and the valley shift a touch with the cursor (depth) ---- */
  var hero = document.querySelector(".calm-hero");
  if (hero) {
    var card = hero.querySelector(".calm-hero__card"), media = $$(".calm-hero__media", hero), hr = 0;
    hero.addEventListener("pointermove", function (e) {
      if (hr) return;
      hr = requestAnimationFrame(function () {
        hr = 0;
        var x = e.clientX / innerWidth - 0.5, y = e.clientY / innerHeight - 0.5;
        if (card) card.style.translate = (x * -14).toFixed(1) + "px " + (y * -10).toFixed(1) + "px";
        media.forEach(function (m) { m.style.transform = "scale(1.05) translate(" + (x * 10).toFixed(1) + "px," + (y * 7).toFixed(1) + "px)"; });
      });
    });
    media.forEach(function (m) { m.style.transition = "transform 1200ms cubic-bezier(0.16,1,0.3,1)"; m.style.transform = "scale(1.05)"; });
    if (card) card.style.transition = "translate 1200ms cubic-bezier(0.16,1,0.3,1)";
  }
})();
