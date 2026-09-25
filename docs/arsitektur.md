# Arsitektur

## Gambaran besar

```
WhatsApp / Telegram
        │
        ▼
┌────────────────────────┐
│   OpenClaw Gateway     │  systemd user service (port 18789)
│   routing, sesi, state │  state: ~/.openclaw/state/openclaw.sqlite
└───────────┬────────────┘
            │ spawn + stream
            ▼
┌────────────────────────┐
│   cmd-cli backend      │  plugin kustom (index.js)
│   (OpenClaw plugin)    │  memetakan model & parsing NDJSON
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│   Command Code CLI     │  cmd -p --output-format json
│   headless, resumable  │  model: deepseek/deepseek-v4-flash
└───────────┬────────────┘
            ▼
   tool: shell | files | web | vision
```

## Komponen

### 1. Channel

Pesan masuk dari WhatsApp (dan Telegram) diteruskan gateway ke agent. Gateway juga
menangani media (gambar, dokumen, video), sesi percakapan, dan antrean pengiriman.

### 2. Gateway

- Jalan sebagai **systemd user service** → hidup lagi otomatis setelah reboot
- `loginctl enable-linger` supaya tetap jalan walau tidak ada yang login GUI
- Config: `~/.openclaw/openclaw.json` (kebijakan model, izin tool, channel, plugin)

### 3. Backend CLI (`cmd-cli`)

Plugin kustom yang menjembatani OpenClaw dengan Command Code CLI:

- Menjalankan `cmd` headless dengan `--output-format json` (NDJSON)
- Mem-parsing event stream (`text_delta`, `tool_running`, `tool_completed`, `result`)
- Memetakan alias model (`default` → `deepseek/deepseek-v4-flash`, dst.)
- Mendukung resume sesi supaya konteks tidak hilang antar pesan

### 4. Permukaan tool

| Tool | Kegunaan |
|---|---|
| shell | menjalankan perintah, mengelola proses, systemd |
| filesystem | baca/tulis file, pencarian isi (grep/glob) |
| web | search + fetch halaman |
| vision | membaca gambar & screenshot |
| messaging | kirim balasan/media ke channel |

### 5. Otomasi

- **Backup harian** — systemd timer 03:30 + `OnBootSec=15min`
  - Snapshot sqlite konsisten pakai `sqlite3 .backup` (tanpa stop service)
  - Enkripsi AES-256 (gpg) → upload ke cloud (rclone)
  - Retensi lokal 14 hari, remote 30 hari
- **Catch-up** — kalau mesin mati saat jadwal, backup jalan otomatis setelah boot

## Kenapa DIDESAIN begini

| Keputusan | Alasan |
|---|---|
| CLI headless sebagai backend, bukan SDK | model gampang diganti, sesi terisolasi, jejak bisa diaudit |
| Backup tanpa stop service | snapshot sqlite konsisten, nol downtime |
| Enkripsi sebelum upload | isi backup mencakup sesi channel & token, tidak boleh mentah di cloud |
| Guardrail berlapis | prompt saja tidak cukup; batasan ditegakkan juga di config & aturan tertulis |
| Tool ditulis sendiri | tidak semua kebutuhan ada library-nya (mis. extractor media SPA) |
