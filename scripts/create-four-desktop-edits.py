#!/usr/bin/env python3
"""Package the three owner-requested desktop edits plus a matching login edit.
Illustrative reformatting only: these are not Windows/MSIX runtime captures.
Requires Pillow. Existing three-desktop-edits are kept unchanged.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, shutil, zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'store/submission/media'
OUT = MEDIA / 'four-desktop-edits'
OUT.mkdir(parents=True, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
WHITE = '#edf1ff'
MUTED = '#aebcd6'
im = Image.new('RGB', (1920, 1080), '#080f22')
d = ImageDraw.Draw(im)

def text(x, y, content, size=18, color=WHITE, heavy=False):
    d.text((x, y), content, font=ImageFont.truetype(BOLD if heavy else FONT, size), fill=color)

def paragraph(x, y, content, width, size=18, color=MUTED, line=29):
    font = ImageFont.truetype(FONT, size)
    current = ''
    for word in content.split():
        trial = (current + ' ' + word).strip()
        if current and d.textlength(trial, font=font) > width:
            text(x, y, current, size, color); y += line; current = word
        else:
            current = trial
    if current:
        text(x, y, current, size, color); y += line
    return y

def box(bounds, fill='#111d33', outline='#344562', radius=22):
    d.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=1)

def logo(x, y, size):
    image = Image.open(ROOT/'src/brand-icon.webp').convert('RGB').resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size-1, size-1), radius=round(size*.2), fill=255)
    im.paste(image, (x, y), mask)

# Same dark desktop palette, header height, card treatment and typography as
# the first edit, with no fake OS title bar, taskbar or signed-in identity.
d.rectangle((0, 0, 1919, 83), fill='#0a1225')
d.line((0, 83, 1919, 83), fill='#2b3854')
logo(43, 17, 48)
text(111, 23, 'AURIX', 28, '#c5a5ff', True)
text(267, 33, 'AI CREATIVE STUDIO', 13, '#aebbd5')
box((1637, 20, 1876, 64), '#111a30', '#344562', 12)
box((1643, 25, 1711, 59), '#34347b', '#53549a', 9)
text(1661, 31, 'EN', 18, WHITE, True)
text(1738, 31, 'FR', 18, '#aebbd5', True)
text(1811, 31, 'AR', 18, '#aebbd5', True)

# Wide desktop welcome panel, based on the actual login wording.
box((126, 147, 893, 939), '#111b3d', '#494c8e', 28)
logo(388, 219, 242)
text(201, 510, 'Welcome to AURIX', 43, WHITE, True)
paragraph(202, 590, 'Turn your ideas into images, code and words. Sign in with Google to use the AURIX studio and save selected projects.', 597, 24, '#c9d4eb', 38)
d.line((204, 766, 813, 766), fill='#38476e')
text(204, 803, 'A Google account is required to enter.', 20, '#becbea')
text(204, 845, 'Cloud saving is optional.', 20, '#becbea')

# Signed-out login panel. No account data, success state or model output added.
box((963, 147, 1793, 939), '#111d33', '#344562', 28)
text(1005, 183, 'Sign in', 34, WHITE, True)
box((1004, 253, 1750, 397), '#0d172a', '#2d3d5a', 18)
text(1030, 276, 'AI results need review', 23, WHITE, True)
paragraph(1030, 323, 'Images may miss details in your prompt. Check writing and code before relying on them.', 689, 19, MUTED, 30)
box((1004, 421, 1750, 602), '#0d172a', '#2d3d5a', 18)
text(1030, 444, 'Your privacy, your choice', 23, WHITE, True)
paragraph(1030, 489, 'Prompts go to an external AI provider when you generate. Work saved locally stays on this device unless you choose to save it to your account.', 689, 19, MUTED, 30)
paragraph(1007, 636, 'By continuing, you agree to the Terms of Service and have read the Privacy Policy.', 737, 18, '#c2cce1', 30)
box((1004, 737, 1750, 810), '#34347b', '#7a71cc', 16)
text(1165, 759, 'Continue with Google', 25, WHITE, True)
text(1124, 759, 'G', 25, '#e1e6ff', True)
text(1006, 849, 'Terms of Service', 17, '#c4b5fa')
text(1224, 849, 'Privacy Policy', 17, '#c4b5fa')
text(1407, 849, 'Contact', 17, '#c4b5fa')
text(127, 1014, 'Reformatted desktop reference · Not a native Windows screenshot', 15, '#93a0ba')
im.save(OUT/'01-Login-Desktop-1920x1080.png', optimize=True)

mapping = [
    ('01-Settings-Desktop-1920x1080.png', '02-Settings-Desktop-1920x1080.png'),
    ('02-Navigation-Desktop-1920x1080.png', '03-Navigation-Desktop-1920x1080.png'),
    ('03-Home-Desktop-1920x1080.png', '04-Home-Desktop-1920x1080.png'),
]
for source, dest in mapping:
    shutil.copyfile(MEDIA/'three-desktop-edits'/source, OUT/dest)

(OUT/'READ-ME-AR.txt').write_text('الملف يحتوي على أربع صور منفصلة، كلها 1920×1080 وبنمط سطح مكتب داكن متوافق مع الصورة الأولى المعدلة.\n01: تسجيل الدخول.\n02: الإعدادات، استنادًا إلى صورة Screenshot_20261125-152746.png.\n03: القائمة الرئيسية، استنادًا إلى صورة Screenshot_20261125-152657.png.\n04: الصفحة الرئيسية، استنادًا إلى صورة Screenshot_20261125-152647.png.\n\nهذه إعادة تنسيق توضيحية وليست لقطات أصلية من تطبيق Windows/MSIX.\nتسجيل الدخول أُعيد تصميمه بالألوان المطلوبة اعتمادًا على نصوص الواجهة الفعلية في src/app.js؛ لا يمثل اختبار تسجيل الدخول.\nالنصوص غير الظاهرة في صفحة الإعدادات استُكملت من ملفات التطبيق، دون بيانات حساب شخصية.\n')
(OUT/'provenance.json').write_text(json.dumps({
    'type': 'edited desktop-layout illustrations; not Windows/MSIX runtime screenshots',
    'dimensions': [1920, 1080],
    'login': 'matching dark desktop styling using actual login wording from src/app.js; not a successful sign-in capture',
    'otherImages': 'the three separate existing desktop reformats of the owner-supplied mobile captures',
    'privateAccountDataAdded': False,
}, indent=2)+'\n')
archive = MEDIA/'AURIX-AI-Login-And-Three-Desktop-Images.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in sorted(OUT.iterdir()):
        if path.is_file():
            if path.suffix == '.png':
                with Image.open(path) as image:
                    assert image.size == (1920, 1080)
                    image.verify()
            z.write(path, Path('AURIX-AI-Desktop-Images')/path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len([p for p in z.namelist() if p.endswith('.png')]) == 4
print('Verified ZIP with four separate 1920x1080 PNGs:', archive)
