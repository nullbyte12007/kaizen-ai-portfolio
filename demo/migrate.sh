#!/usr/bin/env bash
#
# OpenClaw migration helper
#   Di mesin LAMA : ./migrate.sh pack
#   Di mesin BARU : ./migrate.sh install <bundle.tar.gz>
#                   ./migrate.sh verify
#
# Bundle berisi: ~/.openclaw, ~/.commandcode, ~/openclaw-cmd-cli,
#                ~/my-openclaw-agent, systemd user unit, dan script ini.
# Cache/log/node_modules/venv TIDAK ikut (bisa dibangun ulang).
#
set -euo pipefail

OLD_HOME="/home/parkee"          # home asli yang masih ke-hardcode di config
GATEWAY_UNIT="openclaw-gateway.service"
GATEWAY_EXEC_RE="openclaw/dist/index.js gateway"

ITEMS=(
  .openclaw
  .commandcode
  openclaw-cmd-cli
  my-openclaw-agent
  .config/systemd/user/openclaw-gateway.service
  migrate.sh
)

EXCLUDES=(
  --exclude='.openclaw/cache'
  --exclude='.openclaw/logs'
  --exclude='.openclaw/tmp'
  --exclude='.openclaw/npm'
  --exclude='.openclaw/state/*-wal'
  --exclude='.openclaw/state/*-shm'
  --exclude='.openclaw/agents/*/agent/*.sqlite-wal'
  --exclude='.openclaw/agents/*/agent/*.sqlite-shm'
  --exclude='my-openclaw-agent/venv'
  --exclude='*.pre-migrate-*'
)

log()  { printf '\033[1;36m[migrate]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[migrate:warn]\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m[migrate:error]\033[0m %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "butuh '$1' tapi belum ada di PATH"; }

cmd_pack() {
  need tar
  log "menghentikan gateway (supaya sqlite konsisten)..."
  systemctl --user stop "$GATEWAY_UNIT" 2>/dev/null || true
  sleep 2
  if pgrep -f "$GATEWAY_EXEC_RE" >/dev/null 2>&1; then
    warn "masih ada proses gateway terdeteksi; tunggu lalu ulangi kalau bundle terlihat aneh"
  fi

  local out="$HOME/openclaw-migrate-$(date +%Y%m%d-%H%M%S).tar.gz"
  log "membuat bundle: $out"
  # 'migrate.sh' mungkin belum ada di $HOME -> buat salinan dulu supaya ikut terbawa
  [ -f "$HOME/migrate.sh" ] || cp -f "$0" "$HOME/migrate.sh" 2>/dev/null || true
  ( cd "$HOME" && tar czf "$out" "${EXCLUDES[@]}" "${ITEMS[@]}" ) \
    || die "gagal membuat bundle"

  log "selesai — ukuran $(du -h "$out" | cut -f1)"
  log "pindahkan file itu ke mesin baru, lalu: ./migrate.sh install $(basename "$out")"
}

cmd_install() {
  local bundle="${1:-}"
  [ -n "$bundle" ] && [ -f "$bundle" ] || die "usage: migrate.sh install <bundle.tar.gz>"
  need tar
  command -v node >/dev/null 2>&1 || die "Node.js belum terpasang. Install dulu (mis. nvm install 24)."

  local home="$HOME"

  if [ -e "$home/.openclaw" ]; then
    local bak="$home/.openclaw.pre-migrate-$(date +%s)"
    log "konfigurasi lama dipindah ke: $bak"
    mv "$home/.openclaw" "$bak"
  fi

  log "extract bundle ke $home ..."
  tar xzf "$bundle" -C "$home" || die "extract gagal"

  if [ "$home" != "$OLD_HOME" ]; then
    log "menyesuaikan path $OLD_HOME -> $home"
    local f
    for f in "$home/.openclaw/openclaw.json" "$home/.config/systemd/user/$GATEWAY_UNIT"; do
      if [ -f "$f" ]; then
        sed -i.migrate-tmp "s|$OLD_HOME|$home|g" "$f" && rm -f "$f.migrate-tmp"
      fi
    done
  fi

  log "memastikan openclaw & command-code terpasang global..."
  npm i -g openclaw command-code >/dev/null 2>&1 \
    || warn "npm i -g gagal — jalankan manual: npm i -g openclaw command-code"

  local unit="$home/.config/systemd/user/$GATEWAY_UNIT"
  if [ -f "$unit" ]; then
    local nodepath distpath
    nodepath="$(command -v node)"
    distpath="$(npm root -g)/openclaw/dist/index.js"
    sed -i.migrate-tmp -E "s|^ExecStart=.*|ExecStart=$nodepath --max-old-space-size=7617 $distpath gateway --port 18789|" "$unit" \
      && rm -f "$unit.migrate-tmp"
    log "ExecStart diarahkan ke: $nodepath"
  else
    warn "service unit tidak ada di bundle; bikin dengan: openclaw daemon install"
  fi

  log "mengaktifkan service..."
  systemctl --user daemon-reload || true
  systemctl --user enable --now "$GATEWAY_UNIT" \
    || die "gagal start service — cek: systemctl --user status $GATEWAY_UNIT"
  command -v loginctl >/dev/null 2>&1 && { loginctl enable-linger "$USER" 2>/dev/null || true; }

  log "menunggu gateway naik..."
  sleep 6
  cmd_verify || true

  cat <<EOF

Langkah manual yang mungkin masih perlu:
  - WhatsApp: kalau minta pairing ulang, buka control UI gateway dan scan QR
  - Teleport : tsh login
  - X/Twitter: refresh twitter_cookies.json kalau sudah expired
  - Sheets   : pastikan Google Sheet tetap dibagikan ke service account
               bot-wa-sheets@banded-equinox-508811-d3.iam.gserviceaccount.com
EOF
}

cmd_verify() {
  log "=== status service ==="
  systemctl --user status "$GATEWAY_UNIT" --no-pager 2>/dev/null | head -n 12 || true
  log "=== openclaw health ==="
  openclaw health 2>&1 | head -n 20 || true
  log "=== login CLI Command Code ==="
  cmd status 2>&1 | head -n 6 || true
}

case "${1:-}" in
  pack)    shift; cmd_pack "$@" ;;
  install) shift; cmd_install "$@" ;;
  verify)  shift; cmd_verify "$@" ;;
  *)
    cat <<'USAGE'
OpenClaw migration helper

  pack                      # di mesin LAMA: stop gateway + bikin bundle
  install <bundle.tar.gz>   # di mesin BARU: extract + fix path + pasang service
  verify                    # cek service, health, dan login CLI
USAGE
    ;;
esac
