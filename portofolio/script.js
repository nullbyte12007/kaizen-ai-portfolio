(function () {
  "use strict";

  var root = document.documentElement;
  var nav = document.getElementById("nav");
  var navToggle = document.getElementById("navToggle");
  var navMenu = document.getElementById("navMenu");
  var themeToggle = document.getElementById("themeToggle");
  var form = document.getElementById("contactForm");
  var formStatus = document.getElementById("formStatus");
  var year = document.getElementById("year");

  /* Tahun otomatis di footer */
  if (year) year.textContent = String(new Date().getFullYear());

  /* Tema: simpan pilihan di localStorage, hormati preferensi sistem */
  var stored = localStorage.getItem("theme");
  var prefersLight = window.matchMedia("(prefers-color-scheme: light)").matches;
  root.setAttribute("data-theme", stored || (prefersLight ? "light" : "dark"));

  if (themeToggle) {
    themeToggle.addEventListener("click", function () {
      var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      localStorage.setItem("theme", next);
    });
  }

  /* Menu mobile */
  function closeMenu() {
    if (!navMenu || !navToggle) return;
    navMenu.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Buka menu");
  }

  if (navToggle && navMenu) {
    navToggle.addEventListener("click", function () {
      var open = navMenu.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Tutup menu" : "Buka menu");
    });

    navMenu.addEventListener("click", function (event) {
      if (event.target.tagName === "A") closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
  }

  /* Shadow di navbar saat halaman discroll */
  function onScroll() {
    if (nav) nav.classList.toggle("is-scrolled", window.scrollY > 8);
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Animasi reveal saat masuk viewport */
  var revealables = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15, rootMargin: "0px 0px -40px 0px" });

    revealables.forEach(function (el) { observer.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Form kontak: demo validasi client-side.
     Ganti isi handler ini dengan fetch() ke backend / layanan form lu. */
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.checkValidity()) {
        formStatus.textContent = "Lengkapi dulu semua field ya.";
        formStatus.classList.add("is-error");
        return;
      }

      var data = Object.fromEntries(new FormData(form).entries());
      formStatus.classList.remove("is-error");
      formStatus.textContent = "Makasih " + data.name + "! Pesan lu udah kesimpen (demo).";

      /* Contoh kirim ke backend:
      fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      */

      form.reset();
    });
  }
})();
