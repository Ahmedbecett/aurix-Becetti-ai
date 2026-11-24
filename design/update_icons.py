from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/'src/app.html'
s=p.read_text()
paths={
'home':'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
'chat':'<path d="M20 11.5a7.5 7.5 0 0 1-7.5 7.5H6l-3 2v-6.5A7.5 7.5 0 1 1 20 11.5Z"/><path d="M8 11h8M8 14h5"/>',
'image':'<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="m4 17 5-5 3 3 3-4 5 6"/>',
'video':'<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m10 9 5 3-5 3z"/>',
'code':'<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m9 9-3 3 3 3m6-6 3 3-3 3"/>',
'writer':'<path d="M4 20h16M6 16l10.5-10.5a2.12 2.12 0 0 1 3 3L9 19H6z"/>',
'projects':'<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
'history':'<path d="M3 12a9 9 0 1 0 2.7-6.4L3 8"/><path d="M3 3v5h5M12 7v5l3 2"/>',
'favorites':'<path d="M20.8 8.6c0 4.2-8.8 10.4-8.8 10.4S3.2 12.8 3.2 8.6a4.6 4.6 0 0 1 8.8-1.8 4.6 4.6 0 0 1 8.8 1.8z"/>',
'settings':'<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1A7 7 0 0 0 15 6l-.4-2.5h-4.2L10 6a7 7 0 0 0-1.5 1.1l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.4-1A7 7 0 0 0 10 18l.4 2.5h4.2L15 18a7 7 0 0 0 1.5-1.1l2.4 1 2-3.4-2-1.5a7 7 0 0 0 .1-1z"/>',
'about':'<circle cx="12" cy="12" r="9"/><path d="M12 11v5m0-8h.01"/>',
'contact':'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
'privacy':'<path d="M12 3 4 6v5c0 5 3.4 8.2 8 10 4.6-1.8 8-5 8-10V6z"/><path d="m9 12 2 2 4-4"/>',
'terms':'<path d="M7 3h8l4 4v14H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2zm8 0v5h4M9 12h6M9 16h6"/>'}
def icon(route):return '<svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+paths[route]+'</svg>'
for route in paths:
 pattern=r'(<a href="#'+route+r'" data-route="'+route+r'">)<span>[^<]*</span>'
 s,n=re.subn(pattern,lambda m:m.group(1)+icon(route),s)
 assert n==1,(route,n)
p.write_text(s)
print('Updated',len(paths),'navigation icons')
