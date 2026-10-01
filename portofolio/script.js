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

  /* ===== Form kontak: pengiriman sungguhan =====
     Situs ini statis (GitHub Pages) sehingga tidak bisa punya backend sendiri,
     jadi memakai layanan relay formulir:

       - Web3Forms : isi `web3formsKey` (gratis, https://web3forms.com). Email
                     tujuan TIDAK terlihat di kode.
       - FormSubmit: cukup isi `email` (https://formsubmit.co). Tanpa API key,
                     tetapi alamat email terlihat di kode dan butuh SATU kali
                     klik konfirmasi dari inbox saat submission pertama.

     Kalau `web3formsKey` diisi, dia yang dipakai. Kalau kosong tapi `email`
     diisi, otomatis pakai FormSubmit. Kalau dua-duanya kosong -> mode demo. */
  var CONTACT = {
    web3formsKey: "",
    email: "workyusuf0301@gmail.com",
    subject: "Pesan baru dari portofolio"
  };

  function contactTarget(payload) {
    if (CONTACT.web3formsKey) {
      return {
        url: "https://api.web3forms.com/submit",
        body: Object.assign({
          access_key: CONTACT.web3formsKey,
          subject: CONTACT.subject,
          from_name: "Portofolio"
        }, payload)
      };
    }
    if (CONTACT.email) {
      return {
        url: "https://formsubmit.co/ajax/" + encodeURIComponent(CONTACT.email),
        body: Object.assign({
          _subject: CONTACT.subject,
          _template: "table",
          _captcha: "false"
        }, payload)
      };
    }
    return null;
  }

  function setFormStatus(text, isError) {
    formStatus.textContent = text;
    formStatus.classList.toggle("is-error", !!isError);
  }

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      if (!form.checkValidity()) {
        setFormStatus(window.portoText("form.fillAll"), true);
        return;
      }

      var data = Object.fromEntries(new FormData(form).entries());
      var target = contactTarget(data);
      var button = form.querySelector('button[type="submit"]');
      var original = button ? button.textContent : "";

      if (!target) {
        setFormStatus(window.portoText("form.thanks") + data.name + window.portoText("form.demo"), true);
        return;
      }

      setFormStatus(window.portoText("form.sending"), false);
      if (button) { button.disabled = true; button.textContent = window.portoText("form.sending"); }

      fetch(target.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(target.body)
      })
        .then(function (res) {
          if (!res.ok) { throw new Error("HTTP " + res.status); }
          return res;
        })
        .then(function () {
          setFormStatus(window.portoText("form.thanks") + data.name + window.portoText("form.saved"), false);
          form.reset();
        })
        .catch(function () {
          setFormStatus(window.portoText("form.error"), true);
        })
        .then(function () {
          if (button) { button.disabled = false; button.textContent = original; }
        });
    });
  }
})();
