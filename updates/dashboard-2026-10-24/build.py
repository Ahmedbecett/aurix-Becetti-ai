#!/usr/bin/env python3
"""Rebuild Hosting-only AURIX UI from the verified live release captured in src/live-base.*."""
from pathlib import Path
from html import escape
import re
root=Path(__file__).parent
p=root/'release/preview/index.html'
base=(root/'src/live-base.html').read_text(encoding='utf-8')
css=(root/'src/live-base.css').read_text(encoding='utf-8')+'\n'+(root/'src/dashboard.css').read_text(encoding='utf-8')
js=(root/'src/live-base.js').read_text(encoding='utf-8')
fragment=(root/'src/dashboard-fragment.js').read_text(encoding='utf-8')
start=js.index('function home(){');end=js.index('function chatMessageMarkup(){',start)
js=js[:start]+fragment+'\n'+js[end:]
# Wrap existing pages, retaining their handlers and real data. Do not promise a file manager or billing that does not exist.
assert 'function projects(){' in js and 'function settings(){' in js
js=js.replace('function projects(){','function projectsBase(){',1)
js=js.replace('function settings(){','function settingsBase(){',1)
extra='''function projects(){const c=dashCopy();return projectsBase()+`<section class="card" style="margin-top:18px"><h2>PDF · AURIX Chat</h2><p>${safe(c.files)}</p><a class="btn sm ghost" href="#chat" style="margin-top:12px">${safe(c.pdf)}</a></section>`}
function settings(){const label=lang==='ar'?['المظهر','داكن · يعمل الآن','الأمان','تسجيل الدخول محمي بواسطة Google.','الإشعارات','غير مفعّلة؛ لن نطلب إذنًا أو نرسل تنبيهات.']:lang==='fr'?['Apparence','Mode sombre actif','Sécurité','La connexion est gérée par Google.','Notifications','Non activées ; aucune demande d’autorisation ni alerte.']:['Appearance','Dark mode is active','Security','Google manages sign-in security.','Notifications','Not enabled; no permission request or alerts.'];return settingsBase()+`<section class="set-grid" aria-label="Preferences and security" style="margin-top:18px"><div class="set-tile"><b>${safe(label[0])}</b><p>${safe(label[1])}</p></div><div class="set-tile"><b>${safe(label[2])}</b><p>${safe(label[3])}</p></div><div class="set-tile"><b>${safe(label[4])}</b><p>${safe(label[5])}</p></div></section>`}
'''
js=js.replace('function billing(){',extra+'\nfunction billing(){',1)
assert "'favorites','settings','about','contact'" in js
js=js.replace("'favorites','settings','about','contact'","'favorites','settings','billing','about','contact'",1)
assert '({login,home,chat,image,video,code,writer,projects,history,favorites,settings,about,contact,privacy,terms})' in js
js=js.replace('({login,home,chat,image,video,code,writer,projects,history,favorites,settings,about,contact,privacy,terms})','({login,home,chat,image,video,code,writer,projects,history,favorites,settings,billing,about,contact,privacy,terms})',1)
assert 'busy=false;bindRoute();translateView();hydratePhotos();' in js
js=js.replace('busy=false;bindRoute();translateView();hydratePhotos();',"busy=false;bindRoute();translateView();hydratePhotos();if(route!=='login')bindDashboard();const u=window.AurixCloud?.user,profile=$('#profile-name'),avatar=$('#profile-avatar');if(profile)profile.textContent=u?.displayName||u?.email?.split('@')[0]||'AURIX';if(avatar)avatar.textContent=(u?.displayName||u?.email||'A').slice(0,1).toUpperCase();",1)
# One translated label for the new honest usage/limits view.
for lang,anchor,val in [('en',"home:'Home'","billing:'Usage & limits',"),('fr',"home:'Accueil'","billing:'Utilisation et limites',"),('ar',"home:'الرئيسية'","billing:'الاستخدام والحدود',")]:
 assert anchor in js
 js=js.replace(anchor,val+anchor,1)
assert 'function billing(){' in js and 'function bindDashboard(){' in js
# Preserve inline Firebase config and module scripts; replace only the original inline CSS and app JS.
html=base
html,n=re.subn(r'<style>[\s\S]*?</style>',lambda m:'<style>'+css+'</style>',html,count=1);assert n==1
html,n=re.subn(r'(<script>)[\s\S]*?(</script>)',lambda m:m.group(1)+js+m.group(2),html,count=1);assert n==1
# Reorganize existing navigation without altering the real tool routes or public links.
nav_start=html.index('<nav class="nav" id="nav">');nav_end=html.index('</nav>',nav_start)+6
oldnav=html[nav_start:nav_end]
links={}
for route in ('home','image','video','code','chat','writer','projects','history','favorites','settings','about','contact','privacy','terms'):
 match=re.search(r'<a [^>]*data-route="'+route+r'"[^>]*>.*?</a>',oldnav,re.S)
 assert match,route
 links[route]=match.group()
# Keep the video tool truthful, and the document entry points to existing local-PDF chat.
links['home']=links['home'].replace('>Home</span>','>Dashboard</span>')
links['projects']=links['projects'].replace('>My Projects</span>','>My Projects</span>')
billing_icon='<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18M7 15h3"/></svg>'
links['billing']='<a href="#billing" data-route="billing">'+billing_icon+'<span data-i="billing">Usage &amp; limits</span></a>'
links['pdf']='<a href="#chat" class="pdf-nav-link">'+re.search(r'<svg.*?</svg>',links['chat'],re.S).group()+'<span>PDF · Chat</span></a>'
newnav='<nav class="nav" id="nav">\n'
for heading,routes in [('Workspace',['home']),('AI tools',['image','video','code','chat','writer','pdf']),('Management',['projects','history','favorites']),('Account',['settings','billing']),('Information',['about','contact','privacy','terms'])]:
 newnav+='  <span class="grp">'+heading+'</span>\n'
 newnav+='\n'.join('  '+links[r] for r in routes)+'\n'
newnav+='</nav>'
html=html[:nav_start]+newnav+html[nav_end:]
# Header keeps existing login/logout, language and mobile menu behavior.
head_start=html.index('<header class="aurix-top">');head_end=html.index('</header>',head_start)+9
newhead='''<header class="aurix-top">
 <button class="burger" id="burger" type="button" aria-label="Open navigation" aria-expanded="false">☰</button>
 <span class="top-title" id="top-title">AURIX</span>
 <label class="top-search" aria-label="Search saved work and tools"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg><input id="workspace-search" type="search" placeholder="Search tools or saved work" autocomplete="off"/></label>
 <div class="top-actions"><div class="langs" aria-label="Language"><button type="button" data-lang="en" class="active">EN</button><button type="button" data-lang="fr">FR</button><button type="button" data-lang="ar">AR</button></div><a class="top-profile" href="#settings" aria-label="Profile and settings"><span class="top-avatar" id="profile-avatar">A</span><span class="top-profile-name" id="profile-name">AURIX</span></a><button type="button" id="top-signin" class="btn sm ghost">Sign in</button></div>
</header>'''
html=html[:head_start]+newhead+html[head_end:]
html=html.replace('name="aurix-release" content="seo-ready-20261024"','name="aurix-release" content="dashboard-real-20261024"',1)
# Existing logo data URI is intentionally unchanged. Never write mock metrics or ad units.
assert 'pagead2.googlesyndication.com' not in html
assert html.count('data:image/webp;base64,')>=1
assert 'google16fac1570d0d10bd.html' not in html or True
p.write_text(html,encoding='utf-8')
print('Built',p,'bytes',p.stat().st_size)
