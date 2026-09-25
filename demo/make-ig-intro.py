#!/usr/bin/env python3
"""
Generator video perkenalan Kaizen (9:16, 1080x1920, 10s).
Frame di-render dengan Pillow lalu di-pipe sebagai raw RGB ke ffmpeg.

Contoh:
  python3 make-ig-intro.py | ffmpeg -hide_banner -loglevel error \
      -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 24 -i - \
      -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
      -movflags +faststart ~/Downloads/kaizen-intro-9x16.mp4
"""
import math
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 24
DUR = 10.0
N = int(FPS * DUR)

DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

NAVY_TOP = (9, 12, 32)
NAVY_BOT = (24, 16, 58)
ACCENT = (0, 229, 168)
VIOLET = (124, 92, 255)
WHITE = (255, 255, 255)
MUTED = (168, 176, 205)

SKILLS = [
    "Analisis log & error",
    "Otomasi server & backup",
    "Integrasi API & Sheets",
    "Bikin script & tools",
    "Rekap data & laporan",
    "Standby 24/7 tanpa rehat",
]
CREATOR = "M Yusuf Saleh"

PAD = 110                 # margin kiri/kanan kartu
SKILL_X = 250             # posisi teks skill (setelah nomor)
SKILL_TOP = int(H * 0.300)
SKILL_STEP = 148
SKILL_H = 120
CREDIT_TOP = 1546
CREDIT_BOT = 1770


def ease_out(t):
    return 1 - (1 - t) ** 3


def clamp01(t):
    return 0.0 if t < 0 else (1.0 if t > 1 else t)


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def fit_font(draw, text, max_width, start=56, floor=34):
    """Perkecil ukuran font sampai teks muat dalam max_width."""
    size = start
    while size > floor:
        f = font(DEJAVU, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(DEJAVU, floor)


def build_base():
    small = Image.new("RGB", (8, 8))
    p = small.load()
    for y in range(8):
        for x in range(8):
            f = (x * 0.35 + y * 0.65) / 7
            p[x, y] = tuple(int(NAVY_TOP[i] + (NAVY_BOT[i] - NAVY_TOP[i]) * f) for i in range(3))
    base = small.resize((W, H), Image.BICUBIC)
    d = ImageDraw.Draw(base, "RGBA")
    for y in range(0, H, 120):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 8), width=1)
    for x in range(0, W, 120):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 8), width=1)
    return base


def build_glow(color, size=900, blur=70):
    small = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(small)
    steps = 72
    for i in range(steps, 0, -1):
        r = 128 * i / steps
        a = int(52 * (1 - i / steps) ** 1.6) + 3
        d.ellipse((128 - r, 128 - r, 128 + r, 128 + r), fill=color + (a,))
    return small.resize((size, size), Image.BICUBIC).filter(ImageFilter.GaussianBlur(blur))


def paste_emoji(img, ch, cx, cy, size, alpha=255):
    try:
        f = ImageFont.truetype(EMOJI, 109)
    except Exception:
        return
    tmp = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((10, 10), ch, font=f, embedded_color=True)
    box = tmp.getbbox()
    if not box:
        return
    glyph = tmp.crop(box)
    scale = size / max(glyph.width, glyph.height)
    glyph = glyph.resize((max(1, int(glyph.width * scale)), max(1, int(glyph.height * scale))),
                         Image.LANCZOS)
    if alpha < 255:
        glyph.putalpha(glyph.getchannel("A").point(lambda v: int(v * alpha / 255)))
    img.alpha_composite(glyph, (int(cx - glyph.width / 2), int(cy - glyph.height / 2)))


def main():
    base = build_base()
    glow_violet = build_glow(VIOLET)
    glow_teal = build_glow(ACCENT, size=700, blur=60)

    f_hero = font(DEJAVU, 190)
    f_tag = font(DEJAVU_R, 52)
    f_small = font(DEJAVU_R, 40)
    f_tiny = font(DEJAVU_R, 34)

    out = sys.stdout.buffer
    for n in range(N):
        t = n / (N - 1)
        frame = base.copy().convert("RGBA")

        gx = int(W * 0.5 + math.sin(t * math.pi * 2) * 260 - 450)
        gy = int(H * 0.28 + math.cos(t * math.pi * 2) * 120 - 450)
        frame.alpha_composite(glow_violet, (gx, gy))
        g2 = int(W * 0.5 + math.sin(t * math.pi * 2 + 2.2) * 300 - 350)
        g2y = int(H * 0.72 + math.cos(t * math.pi * 2 + 1.1) * 140 - 350)
        frame.alpha_composite(glow_teal, (g2, g2y))

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)

        # --- HERO: 0.00-0.34 ---
        if t < 0.34:
            k = ease_out(clamp01(t / 0.14))
            fade = clamp01(t / 0.09)
            paste_emoji(layer, "\u26e9", W // 2, int(H * 0.300), 104, int(255 * fade))
            scale = 0.86 + 0.14 * k
            hero = Image.new("RGBA", (W, 300), (0, 0, 0, 0))
            ImageDraw.Draw(hero).text((W // 2, 150), "Kaizen", font=f_hero,
                                      fill=WHITE + (int(255 * fade),), anchor="mm")
            hero = hero.resize((int(W * scale), int(300 * scale)), Image.LANCZOS)
            layer.alpha_composite(hero, (int((W - hero.width) / 2),
                                         int(H * 0.390 - hero.height / 2)))
            a = clamp01((t - 0.08) / 0.08)
            if a > 0:
                d.line([(W * 0.32, H * 0.487), (W * 0.68, H * 0.487)],
                       fill=ACCENT + (int(255 * a),), width=6)
                d.text((W // 2, H * 0.532), "AI Assistant  ·  Standby 24/7", font=f_tag,
                       fill=MUTED + (int(255 * a),), anchor="mm")

        # --- JUDUL SKILL ---
        if t >= 0.28:
            a = ease_out(clamp01((t - 0.28) / 0.08))
            d.text((W // 2, H * 0.250), "SKILL", font=font(DEJAVU, 44),
                   fill=ACCENT + (int(240 * a),), anchor="mm")
            d.line([(W // 2 - int(70 * a), H * 0.272), (W // 2 + int(70 * a), H * 0.272)],
                   fill=ACCENT + (int(110 * a),), width=3)

        # --- DAFTAR SKILL ---
        if t >= 0.33:
            avail = W - PAD - SKILL_X - 30
            for i, sk in enumerate(SKILLS):
                start = 0.33 + i * 0.055
                if t < start:
                    continue
                a = ease_out(clamp01((t - start) / 0.055))
                slide = (1 - a) * 90
                y = SKILL_TOP + i * SKILL_STEP
                d.rounded_rectangle(
                    [PAD - slide, y, W - PAD - slide, y + SKILL_H], radius=26,
                    fill=(255, 255, 255, int(14 * a)), outline=ACCENT + (int(90 * a),), width=2)
                d.rounded_rectangle(
                    [PAD - slide + 14, y + 20, PAD - slide + 20, y + SKILL_H - 20], radius=3,
                    fill=ACCENT + (int(210 * a),))
                d.text((176 - slide, y + SKILL_H // 2), f"{i+1:02d}", font=f_tiny,
                       fill=ACCENT + (int(230 * a),), anchor="lm")
                fs = fit_font(d, sk, avail)
                d.text((SKILL_X - slide, y + SKILL_H // 2), sk, font=fs,
                       fill=WHITE + (int(255 * a),), anchor="lm")

        # --- CREDIT ---
        if t >= 0.80:
            a = ease_out(clamp01((t - 0.80) / 0.06))
            fadeout = 1.0 if t < 0.965 else clamp01((1.0 - t) / 0.035)
            aa = int(255 * a * fadeout)
            paste_emoji(layer, "\u26e9", W // 2, 1492, 64, int(255 * a * fadeout))
            d.rounded_rectangle([PAD, CREDIT_TOP, W - PAD, CREDIT_BOT], radius=30,
                                fill=(255, 255, 255, int(16 * a * fadeout)),
                                outline=VIOLET + (int(140 * a * fadeout),), width=3)
            d.text((W // 2, CREDIT_TOP + 52), "DIBUAT OLEH", font=f_tiny,
                   fill=MUTED + (aa,), anchor="mm")
            d.text((W // 2, CREDIT_TOP + 148), CREATOR, font=font(DEJAVU, 64),
                   fill=WHITE + (aa,), anchor="mm")

        # --- progress bar ---
        bw = W - 2 * PAD
        d.rounded_rectangle([PAD, H - 118, PAD + bw, H - 110], radius=4, fill=(255, 255, 255, 26))
        d.rounded_rectangle([PAD, H - 118, PAD + int(bw * t), H - 110], radius=4,
                            fill=ACCENT + (235,))

        frame.alpha_composite(layer)
        out.write(frame.convert("RGB").tobytes())

    out.flush()


if __name__ == "__main__":
    main()
