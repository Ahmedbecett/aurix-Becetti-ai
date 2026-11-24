#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
p=Path('release/preview')
assert (p/'index.html').exists() and (p/'sitemap.xml').exists() and (p/'robots.txt').exists()
x=[e.text for e in ET.parse(p/'sitemap.xml').findall('.//{*}loc')]
t=(p/'sitemap.txt').read_text(encoding='utf-8').splitlines()
assert x==t and len(t)==8 and len(set(t))==8
assert all(u.startswith('https://aurix-ea09b.web.app/') for u in t)
print('Verified: 8 public URLs; XML and text sitemaps match. Existing site files included.')
PY
printf '\nTarget: Firebase Hosting project aurix-ea09b ONLY.\nThis adds /sitemap.txt. No Worker, Firestore, ads or paid service changes.\n'
read -r -p 'Type yes to publish: ' answer
if [[ "$answer" != yes ]]; then echo 'Stopped without publishing.'; exit 1; fi
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nPublished. Open https://aurix-ea09b.web.app/sitemap.txt and verify all eight lines before submitting to Search Console.\n'
