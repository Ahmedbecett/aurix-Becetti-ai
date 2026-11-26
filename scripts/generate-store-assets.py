#!/usr/bin/env python3
"""Generate package/store logos from the existing owner-supplied AURIX icon.
Not screenshots. Build-time utility only: Python + Pillow 13.0.0.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
source = Image.open(ROOT / 'desktop/icon.png').convert('RGBA')
assets = ROOT / 'store/assets'
assets.mkdir(parents=True, exist_ok=True)
for name, size in {
    'StoreLogo.png': (50, 50),
    'Square44x44Logo.png': (44, 44),
    'Square150x150Logo.png': (150, 150),
    'Square310x310Logo.png': (310, 310),
    'Wide310x150Logo.png': (310, 150),
}.items():
    canvas = Image.new('RGBA', size, '#0b1020')
    side = round(min(size) * 0.8)
    icon = source.resize((side, side), Image.Resampling.LANCZOS)
    canvas.alpha_composite(icon, ((size[0] - side) // 2, (size[1] - side) // 2))
    canvas.save(assets / name)
listing = ROOT / 'store/submission/artwork'
listing.mkdir(parents=True, exist_ok=True)
canvas = Image.new('RGBA', (300, 300), '#0b1020')
canvas.alpha_composite(source.resize((240, 240), Image.Resampling.LANCZOS), (30, 30))
canvas.save(listing / 'ProductIcon300.png')
print('Generated package logos and listing icon, not product screenshots.')
