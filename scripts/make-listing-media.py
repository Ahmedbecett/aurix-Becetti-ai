#!/usr/bin/env python3
"""Build the AURIX AI listing hero image and walkthrough video.

These are ORIGINAL illustrations (brand gradient, the AURIX symbol, the real
web address, the real Microsoft Store link). They are deliberately NOT fake
screenshots: if a frame needs to show something found only inside a running
app, this script draws a headline card instead of inventing an interface.

Outputs
  release/media/aurix-hero-1920x1080.png   - listing / README hero
  release/media/aurix-hero-1080x1080.png   - square social crop
  release/media/aurix-walkthrough.mp4      - ~26 s, 1280x720, no audio
  release/media/aurix-walkthrough.vtt      - captions for the video
"""
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'release' / 'media'
OUT.mkdir(parents=True, exist_ok=True)
SYMBOL = Image.open(ROOT / 'src' / 'brand-icon.webp').convert('RGB')

W, H = 1920, 1080
BG = (11, 16, 32)
BG2 = (13, 18, 38)
TEXT = (232, 234, 242)
MUTED = (154, 163, 189)
MUTED2 = (107, 116, 146)
ORANGE = (255, 122, 26)
VIOLET = (139, 92, 246)
VIOLET2 = (167, 139, 250)
OK = (52, 211, 153)
WARN = (251, 191, 36)

FONT_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def font(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def gradient(width, height, top=(16, 22, 45), bottom=BG):
    base = Image.new('RGB', (width, height), top)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        t = y / max(height - 1, 1)
        draw.line(
            [(0, y), (width, y)],
            fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return base


def glow(canvas, center, radius, color, strength=90):
    """Additive light without visible seams: draw on a full-size layer, then add."""
    from PIL import ImageChops
    layer = Image.new('RGB', canvas.size, (0, 0, 0))
    d = ImageDraw.Draw(layer)
    steps = 48
    for i in range(steps, 0, -1):
        r = int(radius * i / steps)
        a = strength * (1 - i / steps) ** 2
        d.ellipse((center[0] - r, center[1] - r, center[0] + r, center[1] + r),
                  fill=tuple(int(c * a / 255) for c in color))
    layer = layer.filter(ImageFilter.GaussianBlur(radius / 6))
    canvas.paste(ImageChops.add(canvas, layer))


def symbol(size):
    """Circular crop of the project's own mark, no invented artwork."""
    im = SYMBOL.copy()
    side = min(im.size)
    im = im.crop((0, 0, side, side)).resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2))
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def wrap(draw, text, fnt, max_width):
    words, lines, line = text.split(), [], ''
    for word in words:
        trial = (line + ' ' + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def card(draw, box, radius=26, fill=(20, 26, 46), outline=(35, 44, 72), width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def hero():
    img = gradient(W, H)
    glow(img, (240, 120), 520, VIOLET, 130)
    glow(img, (1760, 980), 560, ORANGE, 110)
    glow(img, (1180, 120), 380, (60, 70, 140), 90)
    d = ImageDraw.Draw(img)

    LEFT = 96
    COL = 830            # left column width
    PANEL_X = 1000
    PANEL_W = W - PANEL_X - 96

    mark = symbol(190)
    img.paste(mark, (LEFT, 84), mark)
    d.text((LEFT + 214, 92), 'AURIX', font=font(82), fill=TEXT)
    d.text((LEFT + 218, 182), 'AI', font=font(82), fill=VIOLET2)
    d.text((LEFT, 318), 'IMAGINE. CREATE. BUILD.', font=font(27), fill=ORANGE)

    h1 = font(56)
    head_lines = wrap(d, 'AI creative studio for Windows 10 and 11', h1, COL)
    for i, line in enumerate(head_lines):
        d.text((LEFT, 380 + i * 66), line, font=h1, fill=TEXT)
    body_top = 380 + len(head_lines) * 66 + 26

    body = font(26, bold=False)
    body_lines = wrap(d, 'Images, writing and code from real AI providers, plus questions about a '
                         'text-based PDF you pick - in one desktop app. Google sign-in is required, '
                         'and AI results always need review.', body, COL)
    for i, line in enumerate(body_lines):
        d.text((LEFT, body_top + i * 40), line, font=body, fill=MUTED)

    y = body_top + len(body_lines) * 40 + 26
    chips = [('Images', 'FLUX.1 Schnell'), ('Writing', 'AI writer'), ('Code', 'AI code studio'),
             ('PDF chat', 'text PDFs')]
    x = LEFT
    for title, sub in chips:
        cw = int(d.textlength(title, font=font(23)) + d.textlength('  ' + sub, font=font(23, bold=False))) + 52
        if x + cw > LEFT + COL:
            x = LEFT
            y += 74
        card(d, (x, y, x + cw, y + 62), radius=31, fill=(23, 29, 52))
        d.text((x + 26, y + 17), title, font=font(23), fill=TEXT)
        d.text((x + 26 + d.textlength(title, font=font(23)), y + 17), '  ' + sub,
               font=font(23, bold=False), fill=MUTED)
        x += cw + 14

    card_top = max(y + 84, 806)
    card(d, (LEFT, card_top, LEFT + COL, card_top + 132), radius=26, fill=(16, 22, 40))
    d.text((LEFT + 30, card_top + 20), 'AURIX AI', font=font(36), fill=TEXT)
    d.text((LEFT + 30, card_top + 68), 'Microsoft Store: apps.microsoft.com/detail/9nlm756d1czr',
           font=font(21, bold=False), fill=MUTED)
    d.text((LEFT + 30, card_top + 98), 'Version 1.0.2.0  ·  Windows 10 22H2 / 11  ·  x64',
           font=font(20, bold=False), fill=MUTED2)

    d.text((LEFT, 1006), 'aurix-ea09b.web.app  ·  Independent project. Free providers are best effort; results need review.',
           font=font(20, bold=False), fill=MUTED2)

    # ---- right panel: capabilities only, no invented interface ----
    rows = [
        ('Image studio', 'Prompts become images with Cloudflare Workers AI (FLUX.1 Schnell).'),
        ('Writing', 'Draft, refine, shorten and translate text with an AI writer.'),
        ('Code', 'Generate, explain and repair code, then copy or download it.'),
        ('PDF chat', 'Ask about the text of a PDF you choose; the file stays on your device.'),
        ('Library', 'Projects, folders, favourites and history saved on this device.'),
    ]
    sub_f = font(21, bold=False)
    title_f = font(25)
    measured = []
    for title, sub in rows:
        lines = wrap(d, sub, sub_f, PANEL_W - 150)
        measured.append((title, lines, 40 + len(lines) * 28 + 30))
    warning = 'Video generation is not available.'
    panel_h = 110 + sum(m[2] for m in measured) + 76
    panel_top = max(96, (H - panel_h) // 2 - 40)
    card(d, (PANEL_X, panel_top, PANEL_X + PANEL_W, panel_top + panel_h), radius=30, fill=(15, 21, 39))
    d.text((PANEL_X + 40, panel_top + 34), 'What AURIX AI does', font=font(34), fill=TEXT)
    ry = panel_top + 100
    for title, lines, height in measured:
        d.ellipse((PANEL_X + 40, ry + 10, PANEL_X + 58, ry + 28), fill=VIOLET)
        d.text((PANEL_X + 76, ry), title, font=title_f, fill=TEXT)
        for i, line in enumerate(lines):
            d.text((PANEL_X + 76, ry + 36 + i * 28), line, font=sub_f, fill=MUTED)
        ry += height
    card(d, (PANEL_X + 32, ry + 2, PANEL_X + PANEL_W - 32, ry + 58), radius=14, fill=(38, 30, 22))
    d.text((PANEL_X + 56, ry + 16), warning, font=font(21), fill=WARN)

    img.save(OUT / 'aurix-hero-1920x1080.png')
    img.crop((200, 60, 1720, 1080)).resize((1080, 1080), Image.LANCZOS).save(OUT / 'aurix-hero-1080x1080.png')
    print('wrote', OUT / 'aurix-hero-1920x1080.png')


def slide(title, subtitle, bullets=(), footer='aurix-ea09b.web.app'):
    img = gradient(1280, 720, top=(15, 20, 42))
    glow(img, (140, 120), 300, VIOLET, 110)
    glow(img, (1160, 660), 320, ORANGE, 100)
    d = ImageDraw.Draw(img)
    mark = symbol(96)
    img.paste(mark, (64, 56), mark)
    d.text((176, 62), 'AURIX', font=font(46), fill=TEXT)
    d.text((306, 62), 'AI', font=font(46), fill=VIOLET2)
    d.text((64, 208), title, font=font(58), fill=TEXT)
    y = 300
    if subtitle:
        for i, line in enumerate(wrap(d, subtitle, font(28, bold=False), 1100)):
            d.text((64, y + i * 42), line, font=font(28, bold=False), fill=MUTED)
        y += len(wrap(d, subtitle, font(28, bold=False), 1100)) * 42 + 40
    y = max(y, 400)
    for bullet in bullets:
        d.ellipse((66, y + 10, 82, y + 26), fill=ORANGE)
        for i, line in enumerate(wrap(d, bullet, font(27, bold=False), 1100)):
            d.text((100, y + i * 38), line, font=font(27, bold=False), fill=MUTED if i else TEXT)
        y += 78 if len(bullet) < 90 else 110
    d.text((64, 664), footer, font=font(22, bold=False), fill=MUTED2)
    return img


def video():
    ffmpeg = None
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        print('ffmpeg not available; skipping the video', file=sys.stderr)
        return

    scenes = [
        (slide('AURIX AI', 'An AI creative studio for Windows 10 and 11: images, writing, code and PDF questions.',
               ['One desktop app instead of four browser tabs.', 'Google sign-in keeps your projects separate.']), 5.0),
        (slide('Image studio', 'Describe a picture and get a real generation - not a canned example.',
               ['Prompts go to Cloudflare Workers AI (FLUX.1 Schnell).', 'Square, wide and tall formats; download what you keep.']), 5.0),
        (slide('Writing and code', 'Draft text, refine it, or generate and repair code.',
               ['Copy or download the result, or save it to your library.', 'AI output can be wrong - review it before use.']), 5.0),
        (slide('PDF chat and your library', 'Ask about a text-based PDF you choose. The file stays on your device.',
               ['Projects, folders, favourites and history live on this device.', 'Cloud copies only when you choose to save them.']), 5.0),
        (slide('Get AURIX AI', 'One download, one sign-in, three studios and PDF chat.',
               ['Microsoft Store: apps.microsoft.com/detail/9nlm756d1czr',
                'Website: aurix-ea09b.web.app',
                'Version 1.0.2.0  ·  x64  ·  Windows 10 22H2 / 11']), 4.5),
        (slide('What AURIX AI does not do', 'Honest limits, stated up front.',
               ['No video generation.', 'Free AI providers can be slow, rate-limited or unavailable.',
                'Banners come from MG Ads on the signed-in Windows screen.'], footer='aurix-ea09b.web.app'), 4.0),
    ]
    frames = OUT / 'frames'
    if frames.exists():
        shutil.rmtree(frames)
    frames.mkdir()
    index = 0
    for img, seconds in scenes:
        for _ in range(int(seconds * 30)):
            img.save(frames / f'f{index:05d}.png')
            index += 1
    target = OUT / 'aurix-walkthrough.mp4'
    subprocess.run([
        ffmpeg, '-y', '-loglevel', 'error', '-framerate', '30',
        '-i', str(frames / 'f%05d.png'),
        '-vf', 'fade=t=in:st=0:d=0.5,format=yuv420p',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-movflags', '+faststart',
        str(target),
    ], check=True)
    shutil.rmtree(frames)

    offset = 0.0
    lines = ['WEBVTT', '']
    captions = [
        'AURIX AI - an AI creative studio for Windows 10 and 11.',
        'Image studio: describe a picture, get a real generation from Cloudflare Workers AI.',
        'Writing and code studio: draft, refine, generate and repair, then copy or save.',
        'Ask about a text-based PDF you choose. The file stays on your device.',
        'Get AURIX AI: Microsoft Store apps.microsoft.com/detail/9nlm756d1czr, version 1.0.2.0, x64.',
        'Honest limits: no video generation, free providers are best effort, banners from MG Ads.',
    ]
    for caption, seconds in zip(captions, [5, 5, 5, 5, 4.5, 4]):
        start = f'{int(offset // 60):02d}:{offset % 60:06.3f}'
        offset += seconds
        end = f'{int(offset // 60):02d}:{offset % 60:06.3f}'
        lines += [f'{start} --> {end}', caption, '']
    (OUT / 'aurix-walkthrough.vtt').write_text('\n'.join(lines), encoding='utf-8')
    print('wrote', target)


if __name__ == '__main__':
    hero()
    video()
