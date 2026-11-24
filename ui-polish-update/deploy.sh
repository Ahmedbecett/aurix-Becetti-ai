#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
from pathlib import Path
from xml.etree import ElementTree as ET
p=Path('release/preview')
assert (p/'index.html').is_file() and all((p/'pages'/f'{n}.html').is_file() for n in ('about','contact','privacy','terms','image-guide','code-guide','writer-guide'))
assert len(ET.parse(p/'sitemap.xml').findall('.//{*}loc'))==8
assert len((p/'sitemap.txt').read_text().splitlines())==8
assert (p/'ads.txt').read_text().strip()=='google.com, pub-6858364141205978, DIRECT, f08c47fec0942fa0'
assert (p/'google16fac1570d0d10bd.html').is_file()
s=(p/'index.html').read_text()
assert 'hero-eyebrow' in s and 'nav-icon' in s and 'pagead2.googlesyndication.com' not in s
print('Verified: 17 Hosting files; SEO, ads.txt verification, Google file preserved. No ad script.')
PY
printf '\nTarget: AURIX Firebase Hosting project aurix-ea09b. UI update only; no Worker/Firestore changes.\n'
read -r -p 'Type yes to publish the AURIX visual update: ' answer
if [[ "$answer" != yes ]]; then echo 'Stopped without publishing.'; exit 1; fi
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nPublished. Open https://aurix-ea09b.web.app/ and sign in with Google to see the internal design.\n'
