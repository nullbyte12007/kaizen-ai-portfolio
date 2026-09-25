#!/usr/bin/env python3
"""
spa-media-dl — download video dari situs yang URL medianya di-resolve oleh JavaScript.

Cara kerja:
  1. buka halaman pakai headless Chromium (Playwright)
  2. pantau request jaringan, cari URL media (.mp4 / .m3u8 / .mpd / .webm)
  3. ambil cookie + header yang dibutuhkan dari browser
  4. unduh pakai curl (streaming) atau ffmpeg kalau HLS/DASH

Pemakaian:
  spa-dl <url> [-o DIR] [--timeout 45] [--show] [--name namafile] [--url-only]

Contoh:
  spa-dl "https://contoh.tld/e/ABC123"
  spa-dl "https://contoh.tld/e/ABC123" -o ~/Downloads --name video-saya
  spa-dl "https://contoh.tld/e/ABC123" --url-only      # cuma tampilkan URL media
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

MEDIA_RE = re.compile(r"\.(mp4|m3u8|mpd|webm|mkv|mov|ts)(\?|$)", re.I)
SKIP_RE = re.compile(
    r"(\.gif|\.jpg|\.jpeg|\.png|\.webp|\.svg|\.css|\.js|\.woff|doubleclick"
    r"|googletagmanager|google-analytics|adservice|adsystem)",
    re.I,
)


def log(msg: str) -> None:
    print(f"[spa-dl] {msg}", file=sys.stderr)


def pick_media(url: str) -> bool:
    return bool(MEDIA_RE.search(url)) and not SKIP_RE.search(url)


def capture(url: str, timeout: int, show: bool) -> tuple[str | None, list[dict], str]:
    """Kembalikan (media_url, cookies, user_agent)."""
    from playwright.sync_api import sync_playwright

    found: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=not show, args=["--autoplay-policy=no-user-gesture-required"]
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        def on_request(req):
            u = req.url
            if pick_media(u) and u not in found:
                found.append(u)
                log(f"kandidat media: {u[:120]}")

        context.on("request", on_request)
        page = context.new_page()
        page.on("popup", lambda pop: pop.close())  # popup iklan jangan ganggu

        log(f"membuka {url}")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        except Exception as exc:
            log(f"peringatan saat load: {type(exc).__name__}")

        deadline = time.time() + timeout
        while time.time() < deadline and not found:
            # beberapa situs butuh klik play dulu
            for sel in ("video", "button[aria-label*=play i]", ".play", "button"):
                try:
                    el = page.query_selector(sel)
                    if el:
                        el.click(timeout=800)
                        break
                except Exception:
                    continue
            # atau sudah ada <video src>
            try:
                src = page.evaluate(
                    "() => {const v = document.querySelector('video'); "
                    "return v && (v.currentSrc || v.src) || null;}"
                )
                if src and pick_media(src) and src not in found:
                    found.append(src)
            except Exception:
                pass
            if not found:
                page.wait_for_timeout(1500)

        cookies = context.cookies()
        ua = page.evaluate("() => navigator.userAgent")
        browser.close()

    if not found:
        return None, [], ua
    found.sort(
        key=lambda u: (
            0 if re.search(r"\.(m3u8|mpd)$", urlparse(u).path, re.I) else 1,
            -len(u),
        )
    )
    return found[0], cookies, ua


def cookie_header(cookies: list[dict]) -> str:
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)


def download(
    media_url: str, cookies: list[dict], ua: str, referer: str, outdir: Path, name: str | None
) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    is_hls = bool(re.search(r"\.(m3u8|mpd)$", urlparse(media_url).path, re.I))
    ext = ".mkv" if is_hls else (os.path.splitext(urlparse(media_url).path)[1] or ".mp4")
    stem = name or (Path(urlparse(referer).path).name or f"media-{int(time.time())}")
    target = outdir / f"{stem}{ext}"

    headers = [
        "-H", f"User-Agent: {ua}",
        "-H", f"Referer: {referer}",
        "-H", "Accept: */*",
    ]
    ck = cookie_header(cookies)
    if ck:
        headers += ["-H", f"Cookie: {ck}"]

    if is_hls:
        if not shutil.which("ffmpeg"):
            raise SystemExit("butuh ffmpeg untuk stream HLS/DASH")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-y",
               *headers, "-i", media_url, "-c", "copy", str(target)]
    else:
        cmd = ["curl", "-L", "--fail", "--progress-bar", *headers, media_url, "-o", str(target)]

    log(f"mengunduh -> {target}")
    rc = subprocess.call(cmd)
    if rc != 0 or not target.exists() or target.stat().st_size == 0:
        raise SystemExit(f"gagal mengunduh (exit {rc})")
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description="Download video dari situs SPA (media di-resolve JS)")
    ap.add_argument("url")
    ap.add_argument("-o", "--outdir", default=str(Path.home() / "Downloads"))
    ap.add_argument("--timeout", type=int, default=45, help="detik menunggu media muncul (default 45)")
    ap.add_argument("--show", action="store_true", help="tampilkan browser (butuh display)")
    ap.add_argument("--name", help="nama file output (tanpa ekstensi)")
    ap.add_argument("--url-only", action="store_true", help="cuma cetak URL media, tidak mengunduh")
    args = ap.parse_args()

    media_url, cookies, ua = capture(args.url, args.timeout, args.show)
    if not media_url:
        print(
            "Tidak menemukan URL media. Coba --timeout lebih besar atau --show untuk lihat browser.",
            file=sys.stderr,
        )
        return 1

    print(media_url)
    if args.url_only:
        return 0

    target = download(media_url, cookies, ua, args.url, Path(args.outdir), args.name)
    print(f"OK -> {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
