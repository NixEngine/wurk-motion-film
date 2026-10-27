"""Render an original, source-reproducible WURK motion film. No network access.

Usage: python render.py --preview | python render.py --render
Runtime: Pillow and imageio-ffmpeg. Fonts and task-supplied logo are local assets.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import pathlib
import struct
import subprocess
import sys
import wave

HERE = pathlib.Path(__file__).resolve().parent
if (HERE / "render_deps").is_dir():
    sys.path.insert(0, str(HERE / "render_deps"))
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

W, H, FPS, DURATION = 1920, 1080, 24, 34
BG, INK, MUTED, LINE = "#F4F1EA", "#161616", "#746E66", "#DFDBD3"
ORANGE, GREEN, WHITE = "#F35B36", "#12674F", "#FFFFFF"
ASSETS = HERE / "assets"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
LOGO = Image.open(ASSETS / "wurk-logo.jpg").convert("RGB")


@functools.lru_cache(maxsize=50)
def font(size: int, weight: int = 500):
    item = ImageFont.truetype(str(ASSETS / "Manrope.ttf"), size)
    item.set_variation_by_axes([weight])
    return item


def clamp(x):
    return max(0.0, min(1.0, x))


def ease(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def pill(draw, box, text, fill=WHITE, color=INK, size=25):
    draw.rounded_rectangle(box, radius=22, fill=fill)
    x1, y1, x2, y2 = box
    bb = draw.textbbox((0, 0), text, font=font(size, 650))
    draw.text(((x1 + x2 - bb[2]) / 2, (y1 + y2 - bb[3]) / 2 - 4), text, font=font(size, 650), fill=color)


def text(draw, xy, value, size=32, fill=INK, weight=500):
    draw.text(xy, value, font=font(size, weight), fill=fill, spacing=6)


def logo(im, xy, size):
    im.paste(LOGO.resize((size, size), Image.Resampling.LANCZOS), xy)


def base(t):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(-140, W + 140, 140):
        xx = x + int(t * 9) % 140
        d.line((xx, 0, xx, H), fill="#EAE6DE", width=1)
    for y in range(0, H, 140):
        d.line((0, y, W, y), fill="#EAE6DE", width=1)
    logo(im, (100, 62), 56)
    text(d, (175, 63), "WURK", 34, weight=800)
    text(d, (1420, 76), "HUMANS + AGENTS", 23, MUTED, 650)
    d.line((100, 970, 1820, 970), fill=LINE, width=2)
    d.line((100, 970, 100 + int(1720 * t / DURATION), 970), fill=ORANGE, width=5)
    text(d, (100, 993), "WORK, BETTER TOGETHER.", 20, MUTED, 650)
    text(d, (1670, 993), "wurk.fun", 22, INK, 700)
    return im, d


def title(d, lines, x, y, size=92):
    for j, line in enumerate(lines):
        text(d, (x, y + j * int(size * 1.20)), line, size, INK, 800)


def card(d, x, y, width, height, label, sub, accent=ORANGE):
    d.rounded_rectangle((x + 5, y + 10, x + width + 5, y + height + 10), radius=28, fill="#E2DDD4")
    d.rounded_rectangle((x, y, x + width, y + height), radius=28, fill=WHITE, outline=LINE, width=2)
    d.rounded_rectangle((x + 28, y + 30, x + 40, y + height - 30), radius=6, fill=accent)
    text(d, (x + 68, y + 28), label, 34, INK, 750)
    text(d, (x + 68, y + 85), sub, 25, MUTED, 500)


def frame(t):
    im, d = base(t)
    if t < 4.5:
        u = ease(t / 0.85)
        title(d, ["A good idea", "needs a teammate."], 100, int(275 + 55 * (1 - u)), 108)
        text(d, (107, 610), "Human ideas. Agent capabilities. One place to connect.", 30, MUTED)
        bob = int(14 * math.sin(t * 2))
        card(d, 1260, 270 + bob, 500, 165, "HUMAN", "Judgment + creativity", ORANGE)
        card(d, 1260, 550 - bob, 500, 165, "AGENT", "Tools + execution", GREEN)
        d.line((1510, 451 + bob, 1510, 535 - bob), fill=INK, width=3)
        d.ellipse((1498, 480, 1522, 504), fill=ORANGE)
    elif t < 10:
        local = t - 4.5
        title(d, ["Start with", "a clear brief."], 100, 265, 102)
        text(d, (107, 565), "Define the task. Show what good looks like.", 30, MUTED)
        x, y = 1070, int(225 + 50 * (1 - ease(local / 0.7)))
        d.rounded_rectangle((x, y, 1790, y + 600), radius=34, fill=WHITE, outline=LINE, width=2)
        pill(d, (1110, y + 35, 1350, y + 90), "NEW JOB", ORANGE, WHITE, 23)
        text(d, (1110, y + 135), "Help review a dataset", 43, weight=750)
        fields = [("SCOPE", "Find missing fields"), ("DELIVERABLE", "A clear QA report"), ("ACCEPTANCE", "Reproducible findings")]
        for j, (label, value) in enumerate(fields):
            yy = y + 235 + j * 108
            text(d, (1110, yy), label, 19, MUTED, 700)
            text(d, (1110, yy + 31), value, 29, INK, 650)
            d.line((1110, yy + 90, 1745, yy + 90), fill=LINE, width=1)
        text(d, (1110, y + 555), "Illustrative task", 18, MUTED)
    elif t < 16.5:
        local = t - 10
        title(d, ["Find the right", "kind of help."], 100, 220, 100)
        text(d, (105, 500), "Post jobs. Discover people and agents.", 30, MUTED)
        cards = [(1010, 230, "RESEARCH", "A source-backed brief", ORANGE),
                 (1190, 455, "CODE", "A useful working tool", GREEN),
                 (1010, 680, "CREATIVE", "A fresh perspective", ORANGE)]
        for j, (x, y, lab, sub, c) in enumerate(cards):
            x += int(90 * (1 - ease((local - j * .24) / .7)))
            card(d, x, y, 600, 160, lab, sub, c)
        pill(d, (105, 660, 545, 730), "HUMANS + AGENTS", INK, WHITE, 28)
    elif t < 23:
        local = t - 16.5
        title(d, ["Deliver useful work.", "Earn rewards."], 100, 235, 96)
        text(d, (105, 540), "Submit. Review. Move forward.", 31, MUTED)
        x, y = 1130, 235
        d.rounded_rectangle((x, y, 1790, 835), radius=34, fill=WHITE, outline=LINE, width=2)
        pill(d, (1170, 280, 1450, 338), "DELIVERY", GREEN, WHITE, 24)
        for j, lab in enumerate(["Artifact delivered", "Ready for review", "Reward on approval"]):
            yy = 405 + j * 113
            on = local > 0.8 + j * 1.15
            d.ellipse((1170, yy, 1212, yy + 42), fill=GREEN if on else LINE)
            if on:
                d.line((1181, yy + 21, 1189, yy + 29, 1202, yy + 13), fill=WHITE, width=4)
            text(d, (1240, yy - 2), lab, 32, INK if on else MUTED, 650)
        text(d, (1170, 770), "Rewards follow each job's rules.", 22, MUTED)
    elif t < 28:
        local = t - 23
        title(d, ["Your skills.", "A clear offer."], 100, 220, 106)
        text(d, (105, 540), "Offer services in the WURK Store.", 32, MUTED)
        for j, (label, sub, c) in enumerate([("CODE", "Automation + tools", GREEN), ("RESEARCH", "Answers + insight", ORANGE), ("DESIGN", "Ideas made visual", GREEN)]):
            xx = 960 + j * 282
            yy = int(310 + (j % 2) * 65 + 50 * (1 - ease((local - j * .18) / .65)))
            d.rounded_rectangle((xx, yy, xx + 250, yy + 400), radius=30, fill=WHITE, outline=LINE, width=2)
            d.rounded_rectangle((xx + 28, yy + 30, xx + 222, yy + 215), radius=20, fill=c)
            # Original geometric icon, drawn from primitives.
            if j == 0:
                for a, b in [((xx + 87, yy + 85), (xx + 58, yy + 120)), ((xx + 58, yy + 120), (xx + 87, yy + 155)), ((xx + 162, yy + 85), (xx + 192, yy + 120)), ((xx + 192, yy + 120), (xx + 162, yy + 155))]:
                    d.line((*a, *b), fill=WHITE, width=10)
            elif j == 1:
                for k in range(4):
                    d.line((xx + 65, yy + 75 + k * 30, xx + 185 - k * 8, yy + 75 + k * 30), fill=WHITE, width=8)
            else:
                d.ellipse((xx + 75, yy + 78, xx + 177, yy + 180), outline=WHITE, width=9)
                d.line((xx + 125, yy + 62, xx + 125, yy + 194), fill=WHITE, width=5)
            text(d, (xx + 27, yy + 250), label, 30, weight=800)
            # Two lines fit the narrow card.
            first, _, second = sub.partition(" + ")
            text(d, (xx + 27, yy + 305), first, 23, MUTED)
            text(d, (xx + 27, yy + 339), "+ " + second, 23, MUTED)
    else:
        local = t - 28
        logo(im, (132, 255), 285)
        text(d, (450, 265), "WURK", 170, weight=800)
        text(d, (144, 585), "Great work takes a team.", 66, weight=750)
        pill(d, (135, 745, 775, 852), "Explore wurk.fun", INK, WHITE, 42)
        # Two arcs become one loop: the two kinds of worker share the outcome.
        pulse = 10 * math.sin(local * 2.5)
        d.ellipse((1190 - pulse, 300, 1570 - pulse, 680), outline=ORANGE, width=26)
        d.ellipse((1380 + pulse, 300, 1760 + pulse, 680), outline=GREEN, width=26)
        d.ellipse((1456, 466, 1494, 504), fill=INK)
    return im


def soundtrack():
    """An original restrained chord bed plus soft transition pips; no samples."""
    dest = BUILD / "original-score.wav"
    rate = 44100
    notes = [130.8128, 164.8138, 195.9977, 261.6256]
    transitions = [0.3, 4.5, 10, 16.5, 23, 28]
    with wave.open(str(dest), "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(rate)
        for second in range(DURATION):
            samples = bytearray()
            for i in range(rate):
                t = second + i / rate
                fade = min(clamp(t / 1.2), clamp((DURATION - t) / 1.8))
                chord = sum(math.sin(2 * math.pi * n * t) * .032 for n in notes)
                tick = 0.0
                for start in transitions:
                    dt = t - start
                    if 0 < dt < .22:
                        tick += math.sin(2 * math.pi * 880 * dt) * math.exp(-dt * 26) * .075
                s = int(32767 * fade * (chord + tick) * (.85 + .15 * math.sin(2 * math.pi * .25 * t)))
                samples.extend(struct.pack("<hh", s, s))
            out.writeframesraw(samples)
    return dest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    if args.preview:
        sheet = Image.new("RGB", (1280, 1080), WHITE)
        for j, t in enumerate([2, 7, 13, 20, 25, 31]):
            shot = frame(t)
            shot.save(BUILD / f"frame-{j + 1}.png")
            sheet.paste(shot.resize((640, 360), Image.Resampling.LANCZOS), ((j % 2) * 640, (j // 2) * 360))
        sheet.save(BUILD / "storyboard.jpg", quality=92)
        print(json.dumps({"storyboard": str(BUILD / "storyboard.jpg"), "frames": 6}), flush=True)
    if args.render:
        audio = soundtrack()
        target = BUILD / "wurk-great-work-takes-a-team.mp4"
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        command = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-vcodec", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0", "-i", str(audio), "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-threads", "2", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", str(DURATION), str(target)]
        with (BUILD / "ffmpeg.log").open("wb") as error:
            proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=error)
            try:
                for n in range(FPS * DURATION):
                    proc.stdin.write(frame(n / FPS).tobytes())
                    if n % (FPS * 5) == 0:
                        print(json.dumps({"renderedSeconds": n / FPS, "duration": DURATION}), flush=True)
                proc.stdin.close()
                if proc.wait() != 0:
                    raise RuntimeError("FFMPEG_RENDER_FAILED_SEE_LOCAL_LOG")
            except BaseException:
                proc.kill()
                proc.wait()
                raise
        result = {"video": target.name, "width": W, "height": H, "fps": FPS, "durationSeconds": DURATION, "frames": FPS * DURATION, "size": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "encoder": imageio_ffmpeg.get_ffmpeg_version(), "logoSha256": hashlib.sha256((ASSETS / "wurk-logo.jpg").read_bytes()).hexdigest(), "networkRequestsDuringRender": 0, "score": "Original procedural synthesis; no third-party samples", "productClaims": "No guaranteed income, award or instant-payment claim"}
        (BUILD / "render-manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
