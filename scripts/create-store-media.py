#!/usr/bin/env python3
"""Build original listing artwork from the existing AURIX logo; no simulated app UI.
Setup: python -m pip install --target .cache/store-media-python pillow imageio-ffmpeg
Run: PYTHONPATH=.cache/store-media-python python scripts/create-store-media.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, math, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'store/submission/media'
ART = OUT / 'upload-artwork'
SCENES = ROOT / '.cache/store-media-scenes'
for p in [ART, SCENES, OUT / 'trailer']:
    p.mkdir(parents=True, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
WHITE = '#F5F0FF'
MUTED = '#B0A8C5'
VIOLET = '#AC76FF'
ORANGE = '#FFAA68'
original = Image.open(ROOT / 'src/brand-icon.webp').convert('RGB')
# Isolate only the symbol: neither AURIX nor AI lettering is included.
symbol = original.crop((65, 96, 332, 335)).convert('RGBA')
mask = Image.new('L', symbol.size)
md = ImageDraw.Draw(mask)
md.ellipse((0, 0, symbol.width-1, symbol.height-1), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(5))
symbol.putalpha(mask)
manifest = []

class Canvas:
    def __init__(self, w, h, base=1080):
        self.w, self.h, self.s = w, h, w/base
        # Low-resolution analytic gradient, then smooth upscale.
        mini = Image.new('RGB', (max(1,w//6), max(1,h//6)))
        pix = mini.load()
        for y in range(mini.height):
            for x in range(mini.width):
                u,v=x/mini.width,y/mini.height
                purple=math.exp(-((u-.80)**2*5+(v-.25)**2*5))
                amber=math.exp(-((u-.1)**2*8+(v-.85)**2*9))
                pix[x,y]=(int(9+29*purple+15*amber),int(9+10*purple+5*amber),int(19+48*purple+2*amber))
        self.im=mini.resize((w,h),Image.Resampling.BICUBIC)
        self.d=ImageDraw.Draw(self.im)
    def xy(self, box): return tuple(round(v*self.s) for v in box)
    def text(self,x,y,text,size=24,color=WHITE,bold=False):
        f=ImageFont.truetype(BOLD if bold else FONT,round(size*self.s))
        self.d.text((round(x*self.s),round(y*self.s)),text,font=f,fill=color,stroke_width=0)
    def line(self,box,color='#443259',width=1):self.d.line(self.xy(box),fill=color,width=max(1,round(width*self.s)))
    def ellipse(self,box,color='#443259',width=1):self.d.ellipse(self.xy(box),outline=color,width=max(1,round(width*self.s)))
    def rect(self,box,fill,outline=None,radius=20):self.d.rounded_rectangle(self.xy(box),radius=round(radius*self.s),fill=fill,outline=outline,width=max(1,round(self.s)))
    def emblem(self,x,y,size):
        n=round(size*self.s)
        im=symbol.resize((n,round(n*symbol.height/symbol.width)),Image.Resampling.LANCZOS)
        self.im.paste(im,(round(x*self.s),round(y*self.s)),im)
    def rings(self,cx,cy,r):
        for k in range(5):
            a=r+k*30
            self.ellipse((cx-a,cy-a,cx+a,cy+a),['#634087','#4B315F','#382940','#2C2335','#231D2A'][k])
        for a in [0.3,2.4,4.5]:
            x=cx+math.cos(a)*r;y=cy+math.sin(a)*r
            self.d.ellipse(self.xy((x-5,y-5,x+5,y+5)),fill=ORANGE)
    def save(self,path):self.im.save(path,optimize=True)

def save(c,name,role):
    path=ART/name;c.save(path)
    manifest.append({'file':'upload-artwork/'+name,'width':c.w,'height':c.h,'role':role,'bytes':path.stat().st_size})

# Poster sizes follow the actual pixel dimensions pasted from Partner Center,
# although that UI labels its 720x1080 slot "9:16".
for w,h in [(720,1080),(1440,2160)]:
    c=Canvas(w,h,720)
    c.text(56,48,'AURIX AI',23,bold=True)
    c.text(56,95,'AI CREATIVE WORKSPACE',12,VIOLET)
    c.rings(360,374,163);c.emblem(220,246,280)
    c.line((56,624,664,624))
    c.text(56,668,'IMAGINE.',64,bold=True)
    c.text(56,746,'CREATE.',64,bold=True)
    c.text(56,824,'BUILD.',64,ORANGE,bold=True)
    c.text(58,954,'Images / Writing / Code',22)
    c.text(58,995,'Windows 10 & 11 · Internet + Google account',13,MUTED)
    save(c,f'poster-{w}x{h}.png','Poster art (use one resolution)')

for w in [1080,2160]:
    c=Canvas(w,w)
    c.text(72,66,'AURIX AI',30,bold=True)
    c.text(72,116,'YOUR AI CREATIVE WORKSPACE',16,VIOLET)
    c.rings(780,405,190);c.emblem(610,252,340)
    c.text(72,395,'Imagine.',78,bold=True)
    c.text(72,490,'Create.',78,bold=True)
    c.text(72,585,'Build.',78,ORANGE,bold=True)
    c.line((72,790,1008,790))
    c.text(72,836,'Images · Writing · Code',34)
    c.text(72,911,'Windows 10 & 11',23,MUTED)
    c.text(72,955,'Internet and Google account required',20,MUTED)
    save(c,f'box-art-{w}x{w}.png','1:1 Box art (use one resolution)')

# Title-free promotional hero, including no lettering from the source icon.
for w,h in [(1920,1080),(3840,2160)]:
    c=Canvas(w,h,1920)
    c.rings(960,540,335)
    c.emblem(710,316,500)
    for x,y,sign in [(270,310,'</>'),(1510,310,'✦'),(270,710,'Aa'),(1510,710,'?')]:
        c.rect((x-70,y-65,x+110,y+100),'#181224','#48335C',28)
        c.text(x-36,y-23,sign,56,VIOLET,True)
        c.line((x+110 if x<960 else x-70,y+20,580 if x<960 else 1340,540),'#493359',2)
    save(c,f'super-hero-no-title-{w}x{h}.png','16:9 Super hero art, no product title')

for size in [300,150,71]:
    path=ART/f'app-tile-{size}x{size}.png'
    original.resize((size,size),Image.Resampling.LANCZOS).save(path,optimize=True)
    manifest.append({'file':'upload-artwork/'+path.name,'width':size,'height':size,'role':'Store display app tile','bytes':path.stat().st_size})

# Xbox slots deliberately omitted: this package targets Windows.Desktop only.
# Never suggest that making Xbox promotional art enables Xbox compatibility.

# Trailer: deliberately typography/brand-only, no fabricated product demo.
scenes=[
    ('AURIX AI','Imagine. Create. Build.','An AI creative workspace for Windows.'),
    ('START WITH AN IDEA','Images. Writing. Code.','AI-assisted creation, powered by external providers.'),
    ('KEEP WORK ORGANIZED','Projects. Folders. Favorites.','Local history and optional text/code cloud saves.'),
    ('STAY IN CONTROL','Review every result.','AI can make mistakes. Provider limits apply.'),
    ('AURIX AI','Make room for your next idea.','Windows 10 & 11 · Internet and Google account required')
]
for i,(kicker,title,sub) in enumerate(scenes):
    c=Canvas(1920,1080,1920)
    c.rings(1530,470,215);c.emblem(1360,318,340)
    c.text(100,100,'AURIX AI',27,bold=True)
    c.text(100,220,kicker,23,VIOLET,True)
    # Deliberate line breaks sized to avoid the brand illustration.
    titles={0:['Imagine.','Create. Build.'],1:['Images.','Writing. Code.'],2:['Projects. Folders.','Favorites.'],3:['Review','every result.'],4:['Make room for','your next idea.']}
    for j,line in enumerate(titles[i]):c.text(92,320+j*120,line,92,ORANGE if j else WHITE,True)
    c.line((100,675,1220,675))
    if i==4:
        c.text(100,734,'Windows 10 & 11',32)
        c.text(100,794,'Internet and Google account required',28,MUTED)
    else:c.text(100,734,sub,28,MUTED)
    c.text(100,950,'AI services require internet · Google sign-in required',21,MUTED)
    c.text(100,987,'Video generation is not available in the app.',19,MUTED)
    for n in range(5):c.rect((1630+n*36,970,1654+n*36,974),ORANGE if n==i else '#483553',radius=2)
    c.save(SCENES/f'{i:02}.png')

vtt='WEBVTT\n\n'
def ts(n):return f'00:{n//60:02}:{n%60:02}.000'
for i,(k,t,s) in enumerate(scenes):
    vtt+=f'{i+1}\n{ts(i*6)} --> {ts((i+1)*6)}\n{k}. {t}\n{s}\n\n'
(OUT/'trailer/AURIX-AI-English.vtt').write_text(vtt)
(OUT/'trailer/TRANSCRIPT.txt').write_text('\n\n'.join(' / '.join(s) for s in scenes)+'\n\nOn-screen throughout: Internet and Google sign-in required. Video generation is not available in the app.\nAudio: original synthesized ambient tones only, no narration.\nVisuals: brand symbol, abstract orbital graphics and animated text cards, not app footage.\n')
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if '--render-video' in sys.argv:
    import imageio_ffmpeg
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    encoded=[]
    for i in range(5):
        target=SCENES/f'{i:02}.mp4'
        subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-loop','1','-i',str(SCENES/f'{i:02}.png'),'-vf',"zoompan=z='1+0.018*on/180':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=180:s=1920x1080:fps=30,fade=t=in:st=0:d=0.45,fade=t=out:st=5.55:d=0.45,format=yuv420p",'-t','6','-c:v','libx264','-preset','veryfast','-crf','20','-threads','2','-an',str(target)],check=True)
        encoded.append(target)
    listing=SCENES/'concat.txt';listing.write_text(''.join(f"file '{p.as_posix()}'\n" for p in encoded))
    # Original quiet ambient chord; no third-party soundtrack or voice.
    audio='aevalsrc=0.025*(sin(2*PI*130.8128*t)+0.6*sin(2*PI*195.9977*t)+0.4*sin(2*PI*261.6256*t))*(0.7+0.3*sin(2*PI*0.15*t)):s=48000:d=30'
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listing),'-f','lavfi','-i',audio,'-af','afade=t=in:st=0:d=2,afade=t=out:st=27:d=3','-c:v','copy','-c:a','aac','-b:a','192k','-ac','2','-t','30','-movflags','+faststart',str(OUT/'trailer/AURIX-AI-Trailer-1080p.mp4')],check=True)
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-i',str(OUT/'trailer/AURIX-AI-Trailer-1080p.mp4'),'-f','null','-'],check=True)
print('Created listing artwork and trailer sources in',OUT)
