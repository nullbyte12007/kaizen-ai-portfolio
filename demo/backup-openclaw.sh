#!/usr/bin/env bash
#
# OpenClaw HOT backup — tidak menghentikan gateway.
#   - DB sqlite di-snapshot pakai `sqlite3 .backup` (konsisten walau sedang jalan)
#   - Sisanya di-tar gzip
#   - Retensi: simpan N backup terbaru (default 14)
#
# Pemakaian:
#   ./backup-openclaw.sh              # backup + rotasi
#   ./backup-openclaw.sh --list       # lihat daftar backup
#   KEEP=30 ./backup-openclaw.sh            # ubah retensi lokal
#   INCLUDE_MEDIA=1 ./backup-openclaw.sh    # ikutkan folder media (besar)
#   OFFSITE_REMOTE=KaizenAI:openclaw-backup ./backup-openclaw.sh   # enkripsi + upload ke Drive
#     (retensi remote: OFFSITE_KEEP_DAYS=30, passphrase: ~/.config/openclaw-backup/pass)
#
set -euo pipefail

HOME_DIR="$HOME"
SRC="$HOME_DIR"
BACKUP_ROOT="${BACKUP_ROOT:-$HOME_DIR/backups/openclaw}"
KEEP="${KEEP:-14}"
INCLUDE_MEDIA="${INCLUDE_MEDIA:-0}"
LOG="$BACKUP_ROOT/backup.log"
STAMP="$(date +%Y%m%d-%H%M%S)"
STAGE="$(mktemp -d)"
OUT="$BACKUP_ROOT/openclaw-$STAMP.tar.gz"
DEST="$STAGE/openclaw-$STAMP"

log() { printf '%s %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG"; }
die() { log "ERROR: $*"; exit 1; }

case "${1:-}" in
  --list) ls -lhtr "$BACKUP_ROOT"/openclaw-*.tar.gz 2>/dev/null || echo "(belum ada backup)"; exit 0 ;;
esac

command -v tar >/dev/null || die "tar tidak ada"
mkdir -p "$BACKUP_ROOT" "$DEST"
: >> "$LOG"

# cek ruang disk (butuh minimal 1.5GB bebas)
free_kb=$(df -Pk "$BACKUP_ROOT" | awk 'NR==2{print $4}')
if [ "$free_kb" -lt 1500000 ]; then
  log "PERINGATAN: sisa disk kurang dari 1.5GB ($((free_kb/1024))MB)"
fi

log "=== mulai backup $STAMP ==="
trap 'rm -rf "$STAGE"' EXIT

# --- 1. config utama ---
cp -a "$SRC/.openclaw/openclaw.json" "$DEST/" 2>/dev/null || log "  (openclaw.json tidak ada?)"
[ -f "$SRC/.openclaw/openclaw.json.last-good" ] && cp -a "$SRC/.openclaw/openclaw.json.last-good" "$DEST/"
log "  config: ok"

# --- 2. folder statis ---
STATIC=(.openclaw/credentials .openclaw/plugins .openclaw/extensions \
        .openclaw/plugin-skills .openclaw/chat-workspace .openclaw/openclaw \
        .openclaw/delivery-queue-media \
        .commandcode openclaw-cmd-cli my-openclaw-agent \
        .config/systemd/user/openclaw-gateway.service)
if [ "$INCLUDE_MEDIA" = "1" ]; then STATIC+=(.openclaw/media); fi
for rel in "${STATIC[@]}"; do
  src="$SRC/$rel"
  [ -e "$src" ] || continue
  mkdir -p "$DEST/$(dirname "$rel")"
  if [ "$rel" = "my-openclaw-agent" ]; then
    rsync -a --exclude 'venv' --exclude '__pycache__' "$src/" "$DEST/$rel/"
  else
    cp -a "$src" "$DEST/$rel" 2>/dev/null || rsync -a "$src" "$DEST/$(dirname "$rel")/"
  fi
done
log "  folder statis: ok"

# --- 3. workspace (media opsional) ---
ws_excl=(--exclude './media' --exclude './.dreams/session-corpus')
if [ "$INCLUDE_MEDIA" = "1" ]; then ws_excl=(); fi
mkdir -p "$DEST/.openclaw/workspace"
tar -C "$SRC/.openclaw/workspace" "${ws_excl[@]}" -cf - . 2>/dev/null \
  | tar -C "$DEST/.openclaw/workspace" -xf -
log "  workspace: ok (include_media=$INCLUDE_MEDIA)"

# --- 4. agents/ + state/ : snapshot sqlite konsisten ---
for d in .openclaw/state .openclaw/agents; do
  [ -d "$SRC/$d" ] || continue
  mkdir -p "$DEST/$d"
  # file non-sqlite dulu
  rsync -a --exclude '*.sqlite' --exclude '*.sqlite-wal' --exclude '*.sqlite-shm' \
        "$SRC/$d/" "$DEST/$d/" 2>/dev/null || true
  while IFS= read -r -d '' db; do
    relpath="${db#$SRC/}"
    mkdir -p "$DEST/$(dirname "$relpath")"
    if sqlite3 "$db" ".backup '$DEST/$relpath'" 2>/dev/null; then
      :
    else
      cp -a "$db" "$DEST/$relpath"
      log "  (fallback copy: $relpath)"
    fi
  done < <(find "$SRC/$d" -name '*.sqlite' -print0 2>/dev/null)
done
log "  sqlite snapshot: ok"

# --- 5. bungkus ---
tar -C "$STAGE" -czf "$OUT" "openclaw-$STAMP"
size=$(du -h "$OUT" | cut -f1)
log "  bundle: $OUT ($size)"

# --- 6. rotasi ---
mapfile -t old < <(ls -1t "$BACKUP_ROOT"/openclaw-*.tar.gz 2>/dev/null | tail -n "+$((KEEP+1))")
for f in "${old[@]:-}"; do
  [ -n "$f" ] && rm -f "$f" && log "  hapus lama: $(basename "$f")"
done

count=$(ls -1 "$BACKUP_ROOT"/openclaw-*.tar.gz 2>/dev/null | wc -l)
log "=== lokal selesai: $count backup tersimpan (retensi $KEEP) ==="

# --- 7. offsite: enkripsi (gpg AES256) lalu upload via rclone ---
#   set OFFSITE_REMOTE="KaizenAI:openclaw-backup" untuk mengaktifkan
if [ -n "${OFFSITE_REMOTE:-}" ]; then
  passfile="${PASSFILE:-$HOME/.config/openclaw-backup/pass}"
  if [ ! -f "$passfile" ]; then
    log "  offsite: DILEWATI (passphrase '$passfile' tidak ada)"
  elif ! command -v rclone >/dev/null 2>&1; then
    log "  offsite: DILEWATI (rclone tidak terpasang)"
  else
    enc="$OUT.gpg"
    if gpg --batch --yes --quiet --passphrase-file "$passfile" --symmetric \
           --cipher-algo AES256 -o "$enc" "$OUT"; then
      if rclone copy "$enc" "$OFFSITE_REMOTE" --no-traverse --quiet; then
        log "  offsite: terkirim ke $OFFSITE_REMOTE ($(du -h "$enc" | cut -f1))"
        rclone delete "$OFFSITE_REMOTE" --min-age "${OFFSITE_KEEP_DAYS:-30}d" --quiet 2>/dev/null \
          && log "  offsite: retensi ${OFFSITE_KEEP_DAYS:-30} hari diterapkan"
      else
        log "  offsite: GAGAL upload ke $OFFSITE_REMOTE"
      fi
    else
      log "  offsite: GAGAL enkripsi"
    fi
    rm -f "$enc"
  fi
fi
