#!/usr/bin/env python3
"""Build self-contained AURIX preview + Blogger XML from a single source."""
from pathlib import Path
from base64 import b64encode
from html import escape
import re
import json
import shutil

root=Path(__file__).parent
src=root/'src'
out=root/'release'
(out/'preview').mkdir(parents=True,exist_ok=True)
(out/'preview'/'assets').mkdir(parents=True,exist_ok=True)
for asset in ('pdf.mjs','pdf.worker.mjs','pdfjs-LICENSE.txt'):
    shutil.copyfile(src/'assets'/asset,out/'preview'/'assets'/asset)
shutil.copyfile(src/'pdf-init.mjs',out/'preview'/'pdf-init.mjs')
# Public Google Search Console HTML-file verification. Keep it on Hosting across rebuilds.
shutil.copyfile(src/'verification'/'google16fac1570d0d10bd.html',out/'preview'/'google16fac1570d0d10bd.html')
css=(src/'styles.css').read_text()
js=(src/'app.js').read_text()
cloud_js=(src/'firebase-cloud.js').read_text()
config_file=root/'firebase.web.json'
config=json.loads(config_file.read_text()) if config_file.exists() else None
if config:
    assert all(config.get(k) for k in ('apiKey','authDomain','projectId','appId'))
    assert not any(str(v).startswith(('PUBLIC_', 'AURIX_')) for v in config.values())
    # Firebase web config is public by design; never use an Admin service-account key here.
    cfg_json=json.dumps(config,separators=(',',':')).replace('<','\\u003c')
    cloud_html='<script>window.AURIX_FIREBASE_CONFIG='+cfg_json+';</script><script type="module">'+cloud_js+'</script>'
    cloud_xml='<script type="text/javascript"><![CDATA[window.AURIX_FIREBASE_CONFIG='+cfg_json+';]]></script><script type="module"><![CDATA['+cloud_js+']]></script>'
else:
    cloud_html=cloud_xml=''

app=(src/'app.html').read_text()
icon='data:image/webp;base64,'+b64encode((src/'brand-icon.webp').read_bytes()).decode()
app=app.replace('data-brand="icon"',f'src="{icon}"')
# Blogger theme remains separate. The Firebase public URL is the canonical free AURIX domain.
site='https://skullaistudio.blogspot.com/'
public_url='https://aurix-ea09b.web.app'
blog_app=app
for name in ('about','contact','privacy','terms'):
    blog_app=blog_app.replace(f'href="#{name}"',f'href="{site}p/{name}.html"')
# XML special chars in ordinary content; CDATA for CSS/JS.
def xml_escape_content(text):
    # XML needs literal & in attributes and text escaped.
    return text.replace('&','&amp;')

preview_app=app
for name in ('about','contact','privacy','terms'):
    preview_app=preview_app.replace(f'href="#{name}"',f'href="/pages/{name}.html"')
preview='''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="aurix-release" content="seo-ready-20261024"/><meta name="description" content="AURIX is an independent creative workspace for AI images, writing, code and text-based PDF questions. Read public guides or sign in with Google for interactive tools."/><link rel="canonical" href="https://aurix-ea09b.web.app/"/><meta name="robots" content="index,follow"/><meta name="theme-color" content="#0b1020"/><title>AURIX — Imagine. Create. Build.</title><style>'''+css+'''</style></head><body>'''+preview_app+'<script>'+js+'</script>'+cloud_html+'<script type="module" src="/pdf-init.mjs"></script></body></html>'
(out/'preview'/'index.html').write_text(preview)
# Blogger requires one b:skin and at least one b:section. The widget displays
# original indexable pages/posts. Interactive app is shown on homepage only.
head='''<meta charset="utf-8"/>
<meta content="width=device-width,initial-scale=1" name="viewport"/>
<meta content="#0b1020" name="theme-color"/>
<meta content="AURIX is an AI creative studio for real image generation, coding assistance and writing. Imagine. Create. Build." name="description"/>
<link expr:href="data:blog.canonicalUrl" rel="canonical"/>
<meta content="website" property="og:type"/>
<meta content="AURIX — Imagine. Create. Build." property="og:title"/>
<meta content="Real AI tools for images, code, and writing. No fake results." property="og:description"/>
<meta expr:content="data:blog.canonicalUrl" property="og:url"/>
<title><data:blog.pageTitle/></title>'''
# CDATA blocks cannot include their own closing token.
assert ']]>' not in css and ']]>' not in js
blog=blog_app.replace('href="#home"',f'href="{site}#home"').replace('href="#image"',f'href="{site}#image"').replace('href="#code"',f'href="{site}#code"').replace('href="#writer"',f'href="{site}#writer"').replace('href="#video"',f'href="{site}#video"').replace('href="#projects"',f'href="{site}#projects"').replace('href="#history"',f'href="{site}#history"').replace('href="#favorites"',f'href="{site}#favorites"').replace('href="#settings"',f'href="{site}#settings"')
# Hash links inside JS templates point to the homepage, because in the published
# theme the app is never mounted on non-home pages.
extra_css='''\n.blogger-content{max-width:850px;margin:36px auto;padding:0 20px 70px}.blogger-content .post-outer{background:var(--surface);border:1px solid var(--line);padding:26px;border-radius:var(--radius)}.blogger-content .post-body{color:var(--muted);line-height:1.75}.blogger-content .post-body h2{color:var(--text);margin:20px 0 8px}.blogger-content .post-title{font-size:28px}.blogger-content .post-header,.blogger-content .post-footer{color:var(--muted2)}.blogger-back{display:inline-flex;margin-bottom:16px}'''
xml=f'''<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:b="http://www.google.com/2005/gml/b" xmlns:data="http://www.google.com/2005/gml/data" xmlns:expr="http://www.google.com/2005/gml/expr" b:css="false" b:defaultwidgetversion="2" b:layoutsVersion="3" lang="en">
<head>
{head}
<b:skin><![CDATA[{css}{extra_css}]]></b:skin>
</head>
<body>
<b:if cond="data:view.isHomepage">
{blog}
<script type="text/javascript"><![CDATA[{js}]]></script>
{cloud_xml}
<b:else/>
<div class="blogger-content"><a class="btn ghost blogger-back" href="{site}">← Back to AURIX</a><b:section id="main" class="main" showaddelement="yes"><b:widget id="Blog1" locked="true" title="Blog Posts" type="Blog" version="2"/></b:section></div>
</b:if>
</body>
</html>
'''
(out/'aurix-blogger.xml').write_text(xml)
# Standalone Blogger pages: use as HTML-mode page bodies.
pages={
'about':('About AURIX', '''<p><strong>AURIX — Imagine. Create. Build.</strong> is an independent AI creative workspace on Firebase Hosting (with a separate Blogger theme). Image generation uses Cloudflare Workers AI with FLUX.1 Schnell through our authenticated Worker. Coding and writing use a separate text provider. Video generation is not enabled. Google sign-in is required to open the interactive studio. There are no ads at launch.</p><h2>Our approach</h2><p>Every successful result is produced by a real provider, not a hardcoded example. Locally saved projects are scoped to your Google account on this browser and are not automatically synced across devices. Provider availability can change without notice.</p><h2>Brand and ownership</h2><p>The AURIX skull identity is based on artwork supplied by the site owner. We are not affiliated with Pollinations.ai.</p>'''),
'contact':('Contact', '''<p>For questions, feedback or privacy requests, email <a href="mailto:ahmedbecetti41@gmail.com">ahmedbecetti41@gmail.com</a>. This link opens your email program; this site does not collect form submissions.</p><p>Please do not send passwords, API keys or sensitive personal data in email.</p>'''),
'privacy':('Privacy Policy', '''<p><strong>Last updated: October 24, 2026.</strong> AURIX requires Google sign-in for its interactive studio on Firebase Hosting; its static informational pages remain public. This policy describes the current implementation only.</p><h2>Generations</h2><p>Your signed-in browser sends generation requests to the AURIX Cloudflare Worker. Image prompts are processed by Cloudflare Workers AI using FLUX.1 Schnell (Black Forest Labs); text and code prompts go to Pollinations.ai Classic endpoints. For chat, only messages and locally extracted text from a user-selected PDF are forwarded by the Worker to Google Gemini when a verified free-tier Gemini key is configured. The original PDF file stays on the device. Free-tier Gemini data may be used to improve Google products; these providers may log requests. Do not enter confidential information or credentials. Its own privacy policy governs its processing.</p><h2>Local storage</h2><p>Prompts, recent chat messages, generated text, legacy image links, favorites, folders and language preference are stored in your browser. Newly generated image bytes are saved locally in IndexedDB under the signed-in account and are not included in JSON export or cloud Firestore. Clear or export the data from the application's Settings. Local projects are scoped to your Google account on this browser and are not automatically synced to other devices.</p><h2>Hosting and other services</h2><p>Firebase Hosting (Google) hosts this staging site and may use cookies or collect technical data under its own terms. Cloudflare processes signed-in API requests and image generation through Workers AI; Google Gemini processes chat messages and extracted PDF text when chat is configured. This version does not enable an independent ad network or analytics service. Google sign-in uses Firebase Authentication and text and code projects you explicitly save to cloud are stored in Firestore under your user ID; new image bytes are local only. Refer to <a href="https://policies.google.com/privacy">Google Privacy Policy</a> and <a href="https://pollinations.ai/privacy">Pollinations.ai privacy information</a> for provider practices.</p><h2>Data requests</h2><p>Google sign-in is processed by Firebase Authentication. Explicit cloud project copies are stored in Cloud Firestore; delete your account and cloud items in Settings. Clearing the browser's local data removes locally saved projects here; it does not remove provider logs. Contact the provider about its own data retention and deletion. Contact the site owner at <a href="mailto:ahmedbecetti41@gmail.com">ahmedbecetti41@gmail.com</a>.</p>'''),
'terms':('Terms of Service', '''<p><strong>Last updated: October 24, 2026.</strong> AURIX is provided as available. There is no guarantee of uptime, free access or a specific usage quota. Third-party provider terms also apply.</p><h2>Use responsibly</h2><p>Do not submit confidential data, secrets, illegal content or unauthorized third-party material. Do not abuse or bypass provider limits.</p><h2>Review outputs</h2><p>Generated content may be inaccurate, insecure or unsuitable. Test generated code before deployment. AURIX does not guarantee originality, ownership or commercial-use rights of outputs. You are responsible for checking provider and model licenses for your use case.</p><h2>Local project data</h2><p>Local projects and new image bytes are stored in this browser and may be lost when it is cleared. Export important work regularly. Video is unavailable. Google sign-in is required for the interactive studio.</p><p>See our <a href="https://skullaistudio.blogspot.com/p/privacy.html">Privacy Policy</a>.</p>''')
}
for slug,(title,body) in pages.items():
    (out/f'{slug}-page.html').write_text(f'<!-- Blogger: Pages → New Page → HTML view → paste this content; title: {title} -->\n'+body+'\n')
# Public informational pages for the Firebase web.app free domain. Interactive tools remain Google-only.
static_pages=out/'preview'/'pages'
static_pages.mkdir(parents=True,exist_ok=True)
for slug,(title,body) in pages.items():
    saved=(out/f'{slug}-page.html').read_text()
    content=saved.split('\n',1)[1].replace('https://skullaistudio.blogspot.com/p/privacy.html','/pages/privacy.html')
    plain=re.sub(r'<[^>]*>',' ',content)
    desc=escape(' '.join(plain.split())[:160],quote=True)
    nav=' | '.join(f'<a href="/pages/{item}.html">{label}</a>' for item,label in [('image-guide','Images'),('code-guide','Code'),('writer-guide','Writing'),('about','About'),('contact','Contact'),('privacy','Privacy'),('terms','Terms')])
    canonical=f'{public_url}/pages/{slug}.html'
    heading='' if re.search(r'<h1\b', content, re.I) else f'<h1>{escape(title)}</h1>'
    html_page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="description" content="{desc}"/><link rel="canonical" href="{canonical}"/><meta name="robots" content="index,follow"/><meta name="theme-color" content="#0b1020"/><title>{escape(title)} — AURIX</title><style>{css}{extra_css}</style></head><body><main class="blogger-content"><nav aria-label="AURIX public pages" class="public-page-nav"><a href="/">AURIX Studio</a> | {nav}</nav><article class="card aurix-page">{heading}<div class="content">{content}</div></article><footer class="public-page-footer">© 2026 AURIX · Interactive AI tools require Google sign-in. Video generation is not available. <a href="/pages/contact.html">Contact</a></footer></main></body></html>'''
    (static_pages/f'{slug}.html').write_text(html_page)
for slug,title in [('image-guide','How to Write Better AI Image Prompts'),('code-guide','A Practical Checklist for AI-Generated Website Code'),('writer-guide','How to Use an AI Writer Without Publishing Generic Content')]:
    content=(out/f'{slug}-page.html').read_text().split('\n',1)[1]
    desc=escape(' '.join(re.sub(r'<[^>]*>',' ',content).split())[:160],quote=True)
    nav=' | '.join(f'<a href="/pages/{item}.html">{label}</a>' for item,label in [('image-guide','Images'),('code-guide','Code'),('writer-guide','Writing'),('about','About'),('contact','Contact'),('privacy','Privacy'),('terms','Terms')])
    canonical=f'{public_url}/pages/{slug}.html'
    heading='' if re.search(r'<h1\b', content, re.I) else f'<h1>{escape(title)}</h1>'
    html_page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="description" content="{desc}"/><link rel="canonical" href="{canonical}"/><meta name="robots" content="index,follow"/><meta name="theme-color" content="#0b1020"/><title>{escape(title)} — AURIX</title><style>{css}{extra_css}</style></head><body><main class="blogger-content"><nav aria-label="AURIX public pages" class="public-page-nav"><a href="/">AURIX Studio</a> | {nav}</nav><article class="card aurix-page">{heading}<div class="content">{content}</div></article><footer class="public-page-footer">© 2026 AURIX · Interactive AI tools require Google sign-in. Video generation is not available. <a href="/pages/contact.html">Contact</a></footer></main></body></html>'''
    (static_pages/f'{slug}.html').write_text(html_page)
# Crawlable public documents only; do not place account-specific or chat URLs in the sitemap.
(out/'preview'/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {public_url}/sitemap.xml\n')
paths=['/']+[f'/pages/{slug}.html' for slug in ('about','contact','privacy','terms','image-guide','code-guide','writer-guide')]
(out/'preview'/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{public_url}{path}</loc></url>\n' for path in paths)+'</urlset>\n')
# Independent plain-text sitemap for diagnosing Search Console's XML sitemap reading.
# Each line is one absolute public URL; keep the existing XML and robots.txt unchanged.
(out/'preview'/'sitemap.txt').write_text(''.join(f'{public_url}{path}\n' for path in paths), encoding='utf-8')
# The owner-supplied PUBLIC AdSense publisher ID, used only to verify site ownership.
# Do not activate ad scripts on the Google sign-in screen or insert ad units here.
print('Built:', *(str(x.relative_to(root)) for x in sorted(out.iterdir())),sep='\n - ')
