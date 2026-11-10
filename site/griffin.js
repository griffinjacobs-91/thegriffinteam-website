/* The Griffin Team · bespoke layer. Reads --sc-p and page scroll; never edits the engine. */
(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---- top bar: light on light grounds, dark on the photographic stages ---- */
  var bar = document.querySelector(".bar");
  var darks = Array.prototype.slice.call(document.querySelectorAll("[data-ground='dark']"));
  function tintBar() {
    if (!bar) return;
    var probeY = 56; // just under the bar
    var onDark = darks.some(function (el) {
      var r = el.getBoundingClientRect();
      return r.top <= probeY && r.bottom >= probeY;
    });
    bar.classList.toggle("is-dark", onDark);
    bar.classList.toggle("is-light", !onDark);
  }

  /* ---- the Valley line: a fixed elevation profile of the Grand Valley, west to east.
     Page scroll is the playhead; passing a place during the tour stamps it, and a
     stamped place is a link back to that moment. ---- */
  var valley = document.querySelector(".valley");
  var drawn = valley && valley.querySelector(".valley__drawn");
  var head = valley && valley.querySelector(".valley__head");
  var sun = valley && valley.querySelector(".valley__sun");
  var stops = valley ? Array.prototype.slice.call(valley.querySelectorAll(".valley__stop")) : [];
  var tour = document.querySelector("[data-tour]");
  var profileLen = 0;
  if (drawn && drawn.getTotalLength) { profileLen = drawn.getTotalLength(); drawn.style.strokeDasharray = profileLen + " " + profileLen; }

  function pointAt(frac) {
    if (!drawn || !profileLen) return null;
    return drawn.getPointAtLength(Math.max(0, Math.min(1, frac)) * profileLen);
  }
  /* a place on the line lights up once its card in "Six places" has been seen; clicking it goes back there */
  var seen = {};
  function stampSeen() {
    stops.forEach(function (s) { s.classList.toggle("is-stamped", reduce || !!seen[s.getAttribute("data-slug")]); });
  }
  if (stops.length && "IntersectionObserver" in window) {
    var placeIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { seen[e.target.id.replace("place-", "")] = true; placeIO.unobserve(e.target); } });
      stampSeen();
    }, { threshold: 0.5 });
    Array.prototype.forEach.call(document.querySelectorAll(".placecard[id]"), function (c) { placeIO.observe(c); });
  } else { stops.forEach(function (s) { seen[s.getAttribute("data-slug")] = true; }); stampSeen(); }

  function drawValley() {
    if (!valley) return;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var docFrac = max > 0 ? window.scrollY / max : 0;
    if (drawn && profileLen) drawn.style.strokeDashoffset = String(profileLen * (1 - docFrac));
    var pt = pointAt(docFrac);
    if (head && pt) { head.setAttribute("cx", pt.x); head.setAttribute("cy", pt.y); }
    if (sun && pt) { sun.setAttribute("cx", pt.x); sun.setAttribute("cy", pt.y); }
  }
  function sizeValleyTargets() {
    if (!valley) return;
    var svg = valley.querySelector('svg'), r = svg.getBoundingClientRect();
    if (!r.width || !r.height) return;
    stops.forEach(function (s) {
      var hit = s.querySelector('.valley__hit');
      if (!hit) { hit = document.createElementNS('http://www.w3.org/2000/svg', 'rect'); hit.setAttribute('class', 'valley__hit'); s.insertBefore(hit, s.firstChild); }
      var width = 44 * 1000 / r.width, height = 44 * 40 / r.height;
      var x = Number(s.querySelector('circle').getAttribute('cx'));
      hit.setAttribute('x', x - width / 2); hit.setAttribute('y', 40 - height);
      hit.setAttribute('width', width); hit.setAttribute('height', height);
    });
  }
  sizeValleyTargets(); window.addEventListener('resize', sizeValleyTargets);
  stops.forEach(function (s) {
    s.addEventListener("click", function () {
      var card = document.getElementById("place-" + s.getAttribute("data-slug"));
      if (card) card.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" });
    });
    s.addEventListener("keydown", function (e) { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); s.click(); } });
  });

  /* ---- hero film: a quiet loop, loaded after the page; skipped for reduced motion and data saver ---- */
  var film = document.querySelector(".calm-hero__video");
  var saveData = navigator.connection && navigator.connection.saveData;
  if (film && !reduce && !saveData) {
    var small = window.matchMedia("(max-width: 860px) and (orientation: portrait)").matches;
    var startFilm = function () {
      film.src = film.getAttribute(small ? "data-src-mobile" : "data-src");
      film.addEventListener("playing", function () { film.classList.add("is-playing"); }, { once: true });
      var pr = film.play(); if (pr && pr.catch) pr.catch(function () {});
    };
    if (document.readyState === "complete") startFilm(); else window.addEventListener("load", startFilm);
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { es.forEach(function (e) { if (!film.src) return; if (e.isIntersecting) { var p = film.play(); if (p && p.catch) p.catch(function () {}); } else film.pause(); }); }).observe(film);
    }
  }

  var ticking = false;
  function onScroll() {
    if (ticking) return; ticking = true;
    requestAnimationFrame(function () { tintBar(); drawValley(); ticking = false; });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  tintBar(); drawValley();
  window.addEventListener("load", onScroll);
  setTimeout(onScroll, 60); setTimeout(onScroll, 600);

  /* ---- reveal failsafe: anything that has reached the screen is shown, even after a fast flick ---- */
  var pending = Array.prototype.slice.call(document.querySelectorAll("[data-sc-in]"));
  var deepest = 0;
  function showReached() {
    deepest = Math.max(deepest, window.scrollY + window.innerHeight * 1.1);
    pending = pending.filter(function (el) {
      if (el.getBoundingClientRect().top + window.scrollY < deepest) {
        el.classList.add("sc-in");
        Array.prototype.forEach.call(el.querySelectorAll(":scope > *"), function (k) { if (el.hasAttribute("data-sc-stagger")) k.classList.add("sc-in"); });
        return false;
      }
      return true;
    });
  }
  var revTick = false;
  window.addEventListener("scroll", function () { if (revTick) return; revTick = true; requestAnimationFrame(function () { showReached(); revTick = false; }); }, { passive: true });
  window.addEventListener("load", showReached); showReached();

  /* ---- current page in the bar ---- */
  function norm(p) { p = p.replace(/\.html$/, "").replace(/\/index$/, "").replace(/\/+$/, ""); return p || "/"; }
  var here = norm(location.pathname), section = here.indexOf("/blog/") === 0 ? "/blog" : here;
  Array.prototype.forEach.call(document.querySelectorAll(".bar__links a, .mobile-nav a, .foot__nav a"), function (a) {
    var h = norm(a.getAttribute("href") || "");
    if (h === here) a.setAttribute("aria-current", "page");
    else if (h === section) a.setAttribute("aria-current", "true");
  });

  /* Native details works without scripts; Escape/outside click adds familiar dismissal. */
  var menu = document.querySelector('.mobile-nav');
  if (menu) {
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && menu.open) { menu.open = false; menu.querySelector('summary').focus(); }
    });
    document.addEventListener('click', function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    window.matchMedia('(min-width: 1040px)').addEventListener('change', function (e) { if (e.matches) menu.open = false; });
  }

  /* ---- contact form: posts to FormSubmit, which emails Kelley. Without JS the plain POST still works. ---- */
  Array.prototype.forEach.call(document.querySelectorAll("form.form[data-send]"), function (f) {
    var btn = f.querySelector('button[type="submit"]');
    var status = f.querySelector('.form__done');
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.checkValidity()) { f.reportValidity(); return; }
      btn.disabled = true;
      var data = {}; new FormData(f).forEach(function (v, k) { data[k] = v; });
      fetch(f.getAttribute("data-send"), { method: "POST", headers: { "Content-Type": "application/json", "Accept": "application/json" }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok || String(j.success) !== "true") throw new Error(j.message || r.status); }); })
        .then(function () { window.location.href = "/thank-you"; })
        .catch(function () {
          btn.disabled = false;
          status.textContent = "That didn’t go through. Please try again, or call Kelley at (970) 589-6555.";
          f.classList.add("is-sent"); status.focus();
        });
    });
    f.addEventListener('input', function () { f.classList.remove("is-sent"); status.textContent = ''; });
  });

  /* ---- counters outside acts tick once on entry via the engine; nothing else here ---- */
})();
