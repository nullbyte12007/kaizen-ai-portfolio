/* i18n.js — kamus dua bahasa + pengalih bahasa (ID / ENG) */
(function () {
  "use strict";

  window.PORTO_I18N = {
    "meta.title": {
      id: "Muhammad Yusuf — Portofolio",
      en: "Muhammad Yusuf — Portfolio"
    },

    "a11y.skip": { id: "Lewati ke konten", en: "Skip to content" },

    /* navigasi */
    "nav.about":      { id: "Tentang",     en: "About" },
    "nav.skills":     { id: "Skill",       en: "Skills" },
    "nav.projects":   { id: "Proyek",      en: "Projects" },
    "nav.certs":      { id: "Sertifikasi", en: "Certifications" },
    "nav.contact":    { id: "Kontak",      en: "Contact" },

    /* hero */
    "hero.eyebrow":    { id: "Halo, saya", en: "Hello, I am" },
    "hero.role":       { id: "IT Administrator & Infrastructure Operations",
                         en: "IT Administrator & Infrastructure Operations" },
    "hero.lead": {
      id: "Mengelola dan menjaga keandalan infrastruktur IT multi-site — server, jaringan, perangkat akses, hingga CCTV. Fokus pada monitoring, penanganan gangguan, dan otomasi pekerjaan berulang agar operasional tidak bergantung pada proses manual.",
      en: "Managing and maintaining the reliability of multi-site IT infrastructure — servers, networks, access devices, and CCTV. Focused on monitoring, incident handling, and automating repetitive work so operations do not depend on manual processes."
    },
    "hero.cta.projects": { id: "Lihat Proyek",  en: "View Projects" },
    "hero.cta.contact":  { id: "Hubungi Saya",  en: "Contact Me" },
    "hero.link.ai":      { id: "Proyek AI Agent", en: "AI Agent Project" },

    /* label keahlian (marquee & tag) */
    "tag.serverMonitoring": { id: "Monitoring Server", en: "Server Monitoring" },
    "tag.automation":       { id: "Otomasi",           en: "Automation" },
    "tag.logAnalysis":      { id: "Analisis Log",      en: "Log Analysis" },

    /* tentang */
    "about.eyebrow": { id: "01 — Tentang", en: "01 — About" },
    "about.h2":      { id: "Sedikit cerita", en: "A short story" },
    "about.p1": {
      id: "Saya IT Administrator dengan pengalaman menangani infrastruktur multi-site: server, jaringan, perangkat akses (reader & RFID), CCTV, hingga perangkat pengguna. Terbiasa menangani gangguan layanan sejak pendeteksian sampai pulih.",
      en: "I am an IT Administrator experienced in handling multi-site infrastructure: servers, networks, access devices (readers & RFID), CCTV, and end-user devices. Accustomed to handling service disruptions from detection through recovery."
    },
    "about.p2": {
      id: "Keseharian bekerja di lingkungan Linux: menganalisis log dan menyusun skrip untuk menghemat waktu tim, mulai dari backup otomatis hingga rekapitulasi data. Terbiasa menyusun dokumentasi agar penanganan insiden tetap konsisten.",
      en: "Day-to-day work happens in a Linux environment: analysing logs and writing scripts that save the team time, from automated backups to data recaps. Accustomed to writing documentation so incident handling stays consistent."
    },
    "stats.experience":      { id: "Pengalaman",         en: "Experience" },
    "stats.experienceValue": { id: "3+ tahun",           en: "3+ years" },
    "stats.users":           { id: "Pengguna didukung",  en: "Users supported" },
    "stats.pc":              { id: "PC dirakit",         en: "PCs assembled" },

    /* keahlian */
    "skills.eyebrow": { id: "02 — Skill", en: "02 — Skills" },
    "skills.h2":      { id: "Keahlian",   en: "Skills" },
    "skills.c1":      { id: "Server & Infrastruktur", en: "Server & Infrastructure" },
    "skills.c2":      { id: "Jaringan & Keamanan",    en: "Networking & Security" },
    "skills.c3":      { id: "Otomasi & Tooling",      en: "Automation & Tooling" },

    /* proyek */
    "projects.eyebrow": { id: "03 — Proyek", en: "03 — Projects" },
    "projects.h2":      { id: "Karya pilihan", en: "Selected work" },
    "proj1.desc": {
      id: "Asisten AI yang jalan 24/7 di mesin sendiri: analisis log, monitoring server, backup terenkripsi otomatis, dan otomasi pelaporan. Dioperasikan lewat chat.",
      en: "An AI assistant running 24/7 on its own machine: log analysis, server monitoring, automated encrypted backups, and reporting automation. Operated through chat."
    },
    "proj2.title": { id: "Hardening Aplikasi Web Internal", en: "Internal Web App Hardening" },
    "proj2.desc": {
      id: "Audit & perbaikan keamanan aplikasi toko internal (Flask + SQLite): proteksi CSRF, captcha, throttle login, alur reset password berbasis token, dan hardening header/CSP.",
      en: "Security audit and remediation of an internal store app (Flask + SQLite): CSRF protection, captcha, login throttling, token-based password reset, and header/CSP hardening."
    },
    "proj3.title": { id: "Toolkit Operasional", en: "Operations Toolkit" },
    "proj3.desc": {
      id: "Kumpulan tool buatan sendiri: port & host scanner, pengunduh media untuk situs SPA, orkestrator backup terenkripsi, dan helper migrasi server.",
      en: "A set of self-built tools: a port and host scanner, a media downloader for SPA sites, an encrypted backup orchestrator, and a server migration helper."
    },
    "link.demo":   { id: "Demo",   en: "Demo" },
    "link.source": { id: "Source", en: "Source" },

    /* sertifikasi */
    "certs.eyebrow": { id: "04 — Sertifikasi", en: "04 — Certifications" },
    "certs.h2":      { id: "Sertifikasi",      en: "Certifications" },
    "cert3.title":   { id: "Pemrograman Dasar", en: "Programming Fundamentals" },

    /* kontak */
    "contact.eyebrow":  { id: "05 — Kontak", en: "05 — Contact" },
    "contact.h2":       { id: "Mari Berdiskusi", en: "Let's Talk" },
    "contact.lead": {
      id: "Terbuka untuk peluang kerja sama, proyek freelance, maupun diskusi seputar infrastruktur, monitoring, dan otomasi.",
      en: "Open to collaboration, freelance projects, and discussions about infrastructure, monitoring, and automation."
    },
    "contact.location": { id: "Lokasi", en: "Location" },

    /* formulir */
    "form.name":       { id: "Nama",  en: "Name" },
    "form.namePh":     { id: "Nama Anda", en: "Your name" },
    "form.message":    { id: "Pesan", en: "Message" },
    "form.messagePh":  { id: "Ceritakan kebutuhan Anda...", en: "Tell me about your needs..." },
    "form.send":       { id: "Kirim Pesan", en: "Send Message" },
    "form.fillAll":    { id: "Mohon lengkapi seluruh kolom.", en: "Please complete all fields." },
    "form.thanks":     { id: "Terima kasih, ", en: "Thank you, " },
    "form.saved":      { id: ". Pesan Anda telah tersimpan (demo).", en: ". Your message has been saved (demo)." },

    /* footer */
    "footer.repos": { id: "Semua repositori ↑", en: "All repositories ↑" }
  };

  var STORAGE_KEY = "porto-lang";
  var DEFAULT_LANG = "id";

  function currentLang() {
    return document.documentElement.getAttribute("data-lang") || DEFAULT_LANG;
  }

  /* dipakai juga oleh script.js untuk pesan formulir */
  window.portoText = function (key) {
    var entry = window.PORTO_I18N[key];
    if (!entry) return key;
    return entry[currentLang()] || entry[DEFAULT_LANG] || key;
  };

  function applyLang(lang) {
    if (lang !== "id" && lang !== "en") lang = DEFAULT_LANG;

    document.documentElement.setAttribute("data-lang", lang);
    document.documentElement.setAttribute("lang", lang);

    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var text = window.portoText(el.getAttribute("data-i18n"));
      if (text && text !== el.getAttribute("data-i18n")) el.textContent = text;
    });

    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
      var text = window.portoText(el.getAttribute("data-i18n-ph"));
      if (text) el.setAttribute("placeholder", text);
    });

    var desc = document.querySelector('meta[name="description"]');
    if (desc) {
      desc.setAttribute("content", lang === "en"
        ? "Personal portfolio — projects, skills, and contact."
        : "Portofolio pribadi — proyek, skill, dan kontak.");
    }

    document.querySelectorAll("[data-set-lang]").forEach(function (btn) {
      btn.classList.toggle("is-active", btn.getAttribute("data-set-lang") === lang);
    });

    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* diabaikan */ }
  }

  function init() {
    document.querySelectorAll("[data-set-lang]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyLang(btn.getAttribute("data-set-lang"));
      });
    });

    var saved = DEFAULT_LANG;
    try { saved = localStorage.getItem(STORAGE_KEY) || DEFAULT_LANG; } catch (e) { /* diabaikan */ }
    applyLang(saved);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
