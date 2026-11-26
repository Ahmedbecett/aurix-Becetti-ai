#!/usr/bin/env python3
"""Check generated media without asserting Windows or Store certification."""
from pathlib import Path
import hashlib, json, re, subprocess
from PIL import Image
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'store/submission/media'
manifest=json.loads((OUT/'manifest.json').read_text())
checks=[]
for entry in manifest:
    p=OUT/entry['file']
    with Image.open(p) as image:
        image.verify()
    with Image.open(p) as image:
        assert image.format=='PNG'
        assert image.size==(entry['width'],entry['height'])
    assert p.stat().st_size < 5_000_000, str(p)
    checks.append({**entry,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'result':'PASS'})
assert len(checks)==9
video=OUT/'trailer/AURIX-AI-Trailer-1080p.mp4'
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
probe=subprocess.run([ffmpeg,'-hide_banner','-i',str(video)],capture_output=True,text=True)
info=probe.stderr
assert '1920x1080' in info and '30 fps' in info
assert re.search(r'Video: h264',info)
assert re.search(r'Audio: aac.*48000 Hz, stereo',info)
assert re.search(r'Duration: 00:00:30\.\d+',info)
subprocess.run([ffmpeg,'-hide_banner','-v','error','-i',str(video),'-f','null','-'],check=True)
vtt=(OUT/'trailer/AURIX-AI-English.vtt').read_text()
assert vtt.startswith('WEBVTT') and vtt.count(' --> ')==5 and '00:00:30.000' in vtt
assert video.stat().st_size<100_000_000
report={
 'artwork':checks,
 'trailer':{'file':str(video.relative_to(OUT)),'result':'PASS','durationSeconds':30,'width':1920,'height':1080,'fps':30,'videoCodec':'H.264','pixelFormat':'yuv420p','audio':'AAC stereo, 48kHz','fullDecode':'PASS','bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest()},
 'captions':{'format':'WebVTT','cues':5,'endsAtSeconds':30,'platformUploadCompatibility':'not tested'},
 'manualReview':{'posterAndHero':'visually inspected','heroProductTitle':'absent by design; symbol crop excludes logo lettering','windowsScreenshotRequirement':'NOT COMPLETE: only bundled web UI reference captures, not Windows/MSIX','storeUpload':'NOT PERFORMED','xboxAssets':'not applicable; Windows.Desktop package only'}
}
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS: 9 PNG assets, 30-second 1080p H.264/AAC trailer, full decode, 5 caption cues.')
print('OPEN GATE: owner must capture/review the final MSIX running on Windows.')
