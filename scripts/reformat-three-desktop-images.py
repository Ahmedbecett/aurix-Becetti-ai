#!/usr/bin/env python3
"""Create 3 desktop-layout reference images, not Windows/MSIX screenshots.
The existing combined edit supplies the shared dashboard/navigation pixels.
Settings labels are restored from src/app.js, not inferred account data.
Run with Pillow installed: python scripts/reformat-three-desktop-images.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, zipfile

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'store/submission/media'
BASE = MEDIA / 'reformatted-from-mobile/AURIX-AI-Desktop-1920x1080.png'
OUT = MEDIA / 'three-desktop-edits'
OUT.mkdir(parents=True, exist_ok=True)
regular = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
base = Image.open(BASE).convert('RGB')
assert base.size == (1920, 1080)

# Source 1: lower navigation with Profile & Settings selected.
im = base.copy()
d = ImageDraw.Draw(im)
def text(x, y, content, size=18, color='#b6c2da', heavy=False):
    d.text((x, y), content, font=ImageFont.truetype(bold if heavy else regular, size), fill=color)
def box(bounds, fill='#111d33', outline='#344562', radius=22):
    d.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=1)
def paragraph(x, y, content, width, size=18, color='#b6c2da', line=29):
    font = ImageFont.truetype(regular, size)
    current = ''
    for word in content.split():
        trial = (current + ' ' + word).strip()
        if d.textlength(trial, font=font) > width and current:
            text(x, y, current, size, color); y += line; current = word
        else:
            current = trial
    if current:
        text(x, y, current, size, color); y += line
    return y
def button(x, y, label, danger=False):
    font = ImageFont.truetype(bold, 16)
    width = round(d.textlength(label, font=font)) + 36
    box((x, y, x+width, y+46), '#2a1c34' if danger else '#1b2850', '#765276' if danger else '#526496', 12)
    text(x+18, y+12, label, 16, '#f0eaff', True)

# Remove the Home highlight and preserve its icon from the original source edit.
home_icon = base.crop((27, 150, 54, 178))
d.rectangle((14, 142, 288, 183), fill='#0a1225')
im.paste(home_icon, (27, 150))
# Match the crop's background locally so the menu has only one selected row.
d.rectangle((25, 148, 57, 180), fill='#0a1225')
text(32, 150, '⌂', 24, '#aebbd4')
text(66, 153, 'Home', 15, '#b5c1d9', True)
# Coordinates match the shared edited sidebar's Settings row.
settings_y = 679
# Derive exact y from the original editing layout: 113 + group spacings + rows.
settings_y = 113 + 29 + 45 + 29 + 6*45 + 29 + 3*45 + 29
box((14, settings_y, 288, settings_y+40), '#242d78', '#34387f', 10)
text(29, settings_y+5, '⚙', 23, '#e4eaff')
text(66, settings_y+10, 'Profile & Settings', 15, '#edf1ff', True)
# Reflow settings content using the real application's labels, without email.
d.rectangle((304, 0, 1440, 82), fill='#080f21')
text(342, 26, 'Profile & Settings', 24, '#edf1ff', True)
d.rectangle((304, 84, 1919, 1079), fill='#080f22')
text(350, 126, 'Profile & Settings', 36, '#edf1ff', True)
text(352, 185, 'Your AURIX account is active. Cloud saving remains your choice.', 20)
box((350, 248, 1887, 680))
text(383, 280, 'Privacy & local data', 26, '#edf1ff', True)
card_y = 344
for left, title, content, label in [
    (383, 'Export your work', 'Save prompts, text outputs and metadata as JSON. Locally stored images are NOT embedded in this export; download them separately.', 'Download JSON'),
    (884, 'Delete local data', 'Remove this account’s local history, favorites, projects and folders from this browser. This cannot be undone.', 'Clear AURIX data'),
    (1385, 'Accounts', 'Only items explicitly saved to cloud are synced.', 'Sign out'),
]:
    box((left, card_y, left+468, 641), '#0d172a', '#2d3d5a', 18)
    text(left+24, card_y+25, title, 22, '#edf1ff', True)
    paragraph(left+24, card_y+77, content, 417, 18)
    button(left+24, 556, label)
    if title == 'Accounts':
        button(left+24, 494, 'Delete account and cloud items', True)
box((350, 711, 1887, 808), '#261e2d', '#785640', 18)
paragraph(378, 730, "AURIX cannot remove data sent to the external provider on your behalf. Consult the provider's privacy policy for its retention and deletion process.", 1470, 18, '#dfc8b1')
for left, title, subtitle in [
    (350, 'Appearance', 'Dark mode is active'),
    (873, 'Security', 'Google manages sign-in security.'),
    (1396, 'Notifications', 'Not enabled; no permission request or alerts.'),
]:
    box((left, 839, left+491, 967))
    text(left+24, 859, title, 21, '#edf1ff', True)
    paragraph(left+24, 902, subtitle, 443, 17)
text(350, 1015, 'Reformatted reference from mobile captures and app labels · Not a native Windows screenshot', 15, '#93a0ba')
im.save(OUT/'01-Settings-Desktop-1920x1080.png', optimize=True)

# Source 2: the Home navigation was open. Expand the desktop sidebar while
# retaining the existing actual dashboard content, rather than inventing data.
im = Image.new('RGB', (1920, 1080), '#080f22')
im.paste(base.crop((0, 0, 303, 1080)).resize((360, 1080), Image.Resampling.LANCZOS), (0, 0))
im.paste(base.crop((303, 0, 1920, 1080)).resize((1560, 1080), Image.Resampling.LANCZOS), (360, 0))
ImageDraw.Draw(im).line((359, 0, 359, 1079), fill='#35435d', width=1)
im.save(OUT/'02-Navigation-Desktop-1920x1080.png', optimize=True)

# Source 3: the dashboard with the mobile menu closed, already reflowed earlier.
base.save(OUT/'03-Home-Desktop-1920x1080.png', optimize=True)

records = [
    {'source': 'Screenshot_20261125-152746.png', 'output': '01-Settings-Desktop-1920x1080.png', 'scene': 'Settings selected; content reconstructed using real app labels, no private account identity'},
    {'source': 'Screenshot_20261125-152657.png', 'output': '02-Navigation-Desktop-1920x1080.png', 'scene': 'Home with expanded navigation and the supplied dashboard content'},
    {'source': 'Screenshot_20261125-152647.png', 'output': '03-Home-Desktop-1920x1080.png', 'scene': 'Home dashboard with compact desktop navigation'},
]
(OUT/'provenance.json').write_text(json.dumps({'type': 'three separate desktop-layout reconstructions; NOT native Windows/MSIX captures', 'dimensions': [1920, 1080], 'images': records}, indent=2)+'\n')
(OUT/'READ-ME-AR.txt').write_text('ثلاث صور منفصلة بدقة 1920×1080، تقابل الصور الثلاث المرسلة بالترتيب.\n01: الإعدادات. 02: القائمة الرئيسية. 03: الصفحة الرئيسية.\nأُزيلت أشرطة الهاتف والمتصفح وأعيد ترتيب المحتوى لتخطيط سطح المكتب.\nهذه صور معدّلة وليست لقطات أصلية من Windows/MSIX. أُكملت نصوص صفحة الإعدادات من ملفات التطبيق الحالية، دون إضافة بيانات حساب شخصية.\n')
archive = MEDIA/'AURIX-AI-Three-Desktop-Images.zip'
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for path in sorted(OUT.iterdir()):
        if path.is_file():
            if path.suffix == '.png':
                with Image.open(path) as image:
                    assert image.size == (1920, 1080)
                    image.verify()
            z.write(path, Path('AURIX-AI-Three-Desktop-Images')/path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert len([p for p in z.namelist() if p.endswith('.png')]) == 3
print('Created and verified three 1920x1080 PNGs:', archive)
