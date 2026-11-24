#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
trap 'unset CLOUDFLARE_API_TOKEN 2>/dev/null || true' EXIT
printf '\nAURIX IMAGE UPDATE: Cloudflare Workers AI, square images only. Video stays disabled.\n'
printf 'No OpenAI or FreeTheAI key is used. No image generation runs during deployment.\n'
read -r -p 'Confirm this AURIX Cloudflare account is still on Workers FREE plan (type yes): ' free
if [[ "$free" != yes ]]; then echo 'Stopped. No changes made.'; exit 1; fi
export CLOUDFLARE_ACCOUNT_ID=753729d9d7658095cabb9ea8820184c9
read -r -s -p 'Cloudflare deployment token (hidden): ' CLOUDFLARE_API_TOKEN; echo
if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then echo 'No token entered. Nothing deployed.'; exit 1; fi
export CLOUDFLARE_API_TOKEN
cd aurix-worker
npx --yes wrangler@4.152.0 deploy
unset CLOUDFLARE_API_TOKEN
cd ../aurix-image-update
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nDeployment finished. Test ONE square image at https://aurix-ea09b.web.app/?v=image-workers-ai-20261024\n'
