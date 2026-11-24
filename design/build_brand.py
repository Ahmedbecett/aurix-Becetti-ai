from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
source=Image.open(root/'design/brand-icon-original.webp').convert('RGB')
S=600
im=Image.new('RGB',(S,S)); pix=im.load()
for y in range(S):
 for x in range(S):
  a=x/S;b=y/S
  purple=max(0,1-((x-85)**2+(y-100)**2)**.5/550)
  orange=max(0,1-((x-510)**2+(y-460)**2)**.5/560)
  pix[x,y]=(int(10+14*purple+12*orange),int(11+3*purple+2*orange),int(29+21*purple+12*orange))
# Retain the supplied skull artwork while removing its original type and softening crop edges.
skull=source.crop((48,38,274,233)).resize((430,371),Image.Resampling.LANCZOS)
mask=Image.new('L',skull.size);mp=mask.load();w,h=skull.size
for y in range(h):
 for x in range(w):
  fade=min(x,y,w-1-x,h-1-y)
  mp[x,y]=int(255*min(1,fade/44))
im.paste(skull,(85,141),mask)
# Subtle luminous frame.
frame=Image.new('RGBA',(S,S));d=ImageDraw.Draw(frame)
for i in range(3):
 d.rounded_rectangle((8+i,8+i,S-9-i,S-9-i),radius=105,outline=(115,58,195,115-25*i),width=2)
im=Image.alpha_composite(im.convert('RGBA'),frame)
d=ImageDraw.Draw(im)
font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
for text,sz,y,color in [('AURIX',73,38,(248,246,253,255)),('AI',65,495,(255,169,100,255))]:
 ft=ImageFont.truetype(font,sz)
 box=d.textbbox((0,0),text,font=ft,stroke_width=0)
 tw=box[2]-box[0]
 d.text(((S-tw)//2,y),text,font=ft,fill=color,stroke_width=0)
im.convert('RGB').resize((400,400),Image.Resampling.LANCZOS).save(root/'src/brand-icon.webp','WEBP',quality=94,method=6)
print(root/'src/brand-icon.webp')
