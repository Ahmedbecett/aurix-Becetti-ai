#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
p=Path('release/preview')
assert all((p/f).is_file() for f in ('index.html','robots.txt','sitemap.xml','sitemap.txt','ads.txt','google16fac1570d0d10bd.html'))
assert len(ET.parse(p/'sitemap.xml').findall('.//{*}loc'))==8
assert len((p/'sitemap.txt').read_text().splitlines())==8
assert (p/'ads.txt').read_text().strip()=='google.com, pub-6858364141205978, DIRECT, f08c47fec0942fa0'
s=(p/'index.html').read_text()
assert 'dashboard-real-20261024' in s and 'function billing()' in s and 'dash-brand-motion' in s
assert 'pagead2.googlesyndication.com' not in s
print('Verified AURIX dashboard update; public pages, sitemaps, ads.txt and verification preserved.')
PY
printf 'Firebase Hosting project: aurix-ea09b. UI only; no Worker/AI/Firestore paid changes.\n'
read -r -p 'Type yes to publish: ' answer
if [[ "$answer" != yes ]]; then echo 'Stopped without publishing.'; exit 1; fi
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nOpen https://aurix-ea09b.web.app/ and sign in with Google to view the dashboard.\n'
