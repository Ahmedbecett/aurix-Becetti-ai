#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 - <<'PY'
from pathlib import Path
p=Path('release/preview')
assert (p/'index.html').is_file() and (p/'sitemap.xml').is_file() and (p/'sitemap.txt').is_file()
assert (p/'google16fac1570d0d10bd.html').is_file()
assert (p/'ads.txt').read_text(encoding='utf-8') == 'google.com, pub-6858364141205978, DIRECT, f08c47fec0942fa0\n'
assert 'pagead2.googlesyndication.com' not in (p/'index.html').read_text()
print('Verified: public ads.txt belongs to the supplied AdSense ID; existing Hosting files present; no ad script enabled.')
PY
printf '\nTarget: Firebase Hosting project aurix-ea09b ONLY. No Worker, Firestore, or AI configuration changes.\n'
read -r -p 'Type yes to publish ads.txt verification file: ' answer
if [[ "$answer" != yes ]]; then echo 'Stopped without publishing.'; exit 1; fi
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nCheck https://aurix-ea09b.web.app/ads.txt before pressing Verify in AdSense.\n'
