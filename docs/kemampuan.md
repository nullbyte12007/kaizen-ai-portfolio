# Kemampuan

Semua contoh di bawah **pernah dijalankan sungguhan**, bukan ilustrasi.

## 1. Analisis log & troubleshooting

**Studi kasus:** tiket parkir `DE5414AF` tidak bisa keluar.

Yang dilakukan:
- Buka log agent (182 MB, terkompresi) + log server (52 MB) tanpa membuka semuanya
  ke memori — pakai pencarian terarah
- Telusuri alur: kartu e-money gagal (saldo Rp3.000 < tarif Rp13.000)
  → sistem otomatis bikin QRIS → QRIS dibayar 15 detik kemudian
  → **tapi pintu baru buka 80 detik setelahnya**
- Ketemu penyebabnya: consumer Kafka di sisi agent terputus, jadi notifikasi
  pembayaran tidak sampai real-time
- Bonus temuan: NPE di jalur payment notification server (tiket lain), dilaporkan terpisah

Output: ringkasan akar masalah + rekomendasi perbaikan.

## 2. Server & infrastruktur

- Cek status service, port, konfigurasi, versi
- Inventaris lokasi: tarik 531 lokasi + uniq code, filter per environment
- Audit endpoint aplikasi: header keamanan, endpoint terbuka, konfigurasi debug
- Cari node di infrastruktur berdasarkan label (nama lokasi, kota, jenis aset)

## 3. Data & laporan

- Rekap Google Sheets: hitung per PIC, breakdown per bulan, filter per platform
  (contoh: 8.791 baris registrasi → 1.002 milik PIC tertentu → 962 di antaranya
  platform X, dipecah per bulan)
- Korelasi antar sumber: chat export ↔ helpdesk ↔ sistem tiket eksternal
- Export ke JSON/CSV untuk dipakai lanjut

## 4. Integrasi API

| Sistem | Pemanfaatan |
|---|---|
| Helpdesk (Chatwoot) | baca percakapan, telusuri asal tiket, status assignment — read-only |
| Google Sheets | baca data operasional, service account, scope terbatas |
| Helpdesk publik | ambil status tiket dari halaman publik |

## 5. Membuat tool

Kalau kebutuhan tidak ada di library, tool-nya ditulis sendiri:

- **Port scanner** — discovery + port scan + banner grab, concurrency, ekspor JSON/CSV,
  guard supaya target publik wajib konfirmasi
- **Media extractor** — untuk situs yang URL medianya di-decrypt JavaScript:
  headless browser menangkap request jaringan, lalu unduh via curl/ffmpeg dengan
  cookie & referer dari sesi browser
- **Backup orchestrator** — snapshot database tanpa downtime, enkripsi, upload, retensi
- **Migration helper** — pindah seluruh instalasi ke mesin baru: pack → install →
  auto-perbaiki path → verifikasi
- **Video generator** — render frame-by-frame (Pillow) → pipe ke ffmpeg, termasuk
  emoji berwarna, teks auto-fit, animasi easing

## 6. Konten & aset

- Card & banner (feed 1:1, story 9:16, banner repo)
- Video pendek dengan animasi (fade, slide, zoom, progress bar)
- Diagram arsitektur
- Semua dihasilkan dari kode — bisa diulang & diubah parameter

## 7. Kualitas & verifikasi diri

Bagian yang sering dilewatkan: **memeriksa hasil sendiri**.

- Setelah render video, frame diekstrak lalu diperiksa visual — ketemu teks
  terpotong & elemen bertumpuk, lalu diperbaiki sebelum diserahkan
- Setelah ubah kode, dijalankan test client: kasus sukses, kasus gagal, dan
  kasus tepi (captcha kosong, honeypot terisi, submit instan, token dipakai ulang)
- Setelah ubah konfigurasi: validasi + restart + cek ulang status

## 8. Batasan yang diakui

- Berjalan **saat diminta** — tidak punya inisiatif di antara pesan (kecuali timer)
- **Butuh kredensial** untuk apa pun yang privat; tidak bisa menembus batas akses
- **Tidak bisa** hal fisik (kamera, perangkat), dan tidak mengontrol browser desktop
- **Jeda panjang tanpa output** bisa memicu watchdog — kerjaan panjang dipecah
  atau dijalankan di background
