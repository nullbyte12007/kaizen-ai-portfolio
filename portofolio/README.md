# Template Portofolio

Template portofolio satu halaman, tanpa dependency. Tinggal edit teks, buka `index.html` di browser.

## Struktur

```
template-portofolio/
├── index.html        # markup + semua konten
├── style.css         # tema (dark/light) & layout responsive
├── script.js         # menu mobile, toggle tema, animasi, validasi form
└── assets/
    └── avatar.svg    # ganti dengan foto lu (jpg/png/svg)
```

## Cara pakai

1. Buka `index.html` langsung di browser, atau jalankan server lokal:
   ```bash
   python3 -m http.server 8000
   ```
   lalu buka http://localhost:8000
2. Ganti data placeholder:
   - `Nama Lu`, `NL` (inisial), role, dan deskripsi di `<section id="hero">`
   - Statistik di `<dl class="stats">`
   - Skill di `<section id="skills">`
   - Proyek di `<section id="projects">` (duplikat `<article class="project">` kalau perlu nambah)
   - Email/telepon/lokasi di `<section id="contact">`
3. Foto: taruh file di `assets/`, lalu update `src` di `<img>` avatar.
4. Link sosial: ganti semua `href="#"` di `.socials` dan `.project-links`.

## Kustomisasi cepat

- **Warna:** ubah `--accent` dan `--accent-2` di bagian `:root` pada `style.css`.
- **Tema default:** ubah `data-theme="dark"` di `<html>` jadi `"light"`.
- **Form kontak:** `script.js` cuma demo validasi. Sambungkan ke backend/layanan form
  (mis. Formspree, Resend, API sendiri) — lihat komentar `fetch("/api/contact", ...)`.

## Fitur

- Responsive (mobile menu + layout grid adaptif)
- Dark/light toggle, tersimpan di `localStorage`
- Animasi reveal pakai IntersectionObserver
- Aksesibel: skip link, `aria-*`, hormati `prefers-reduced-motion`
- Zero dependency, zero build step
