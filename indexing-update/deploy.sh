#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
printf '\nAURIX PUBLIC INDEXING UPDATE for https://aurix-ea09b.web.app/\n'
printf 'This removes site-wide noindex/robots blocking and publishes public guides. Interactive tools still require Google sign-in. No ads or paid services are enabled.\n'
read -r -p 'Type yes to publish crawlable pages on the AURIX Firebase site: ' answer
if [[ "$answer" != yes ]]; then echo 'Stopped without deploying.'; exit 1; fi
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nDone. Check https://aurix-ea09b.web.app/robots.txt and https://aurix-ea09b.web.app/sitemap.xml\n'
