#!/usr/bin/env bash
# AURIX deployment helper. No API keys are stored in this file or archive.
set -euo pipefail
cd "$(dirname "$0")"
trap 'unset CLOUDFLARE_API_TOKEN 2>/dev/null || true' EXIT
printf '\nAURIX: Worker + Firebase Hosting update.\n'
printf 'This package contains NO API keys. Do not paste keys into chat or scripts.\n'
printf 'OpenAI is NOT used. Gemini must be a key from an unbilled Free-tier AURIX project.\n\n'
read -r -p 'If you checked the Gemini project has NO billing attached, type yes: ' ok
if [[ "$ok" != yes ]]; then echo 'Stopped. No changes made.'; exit 1; fi
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  read -r -s -p 'Cloudflare deployment token (hidden input): ' CLOUDFLARE_API_TOKEN
  printf '\n'
  export CLOUDFLARE_API_TOKEN
fi
if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then echo 'Missing Cloudflare deployment token.'; exit 1; fi
cd aurix-worker
printf '\nEnter your GEMINI API key ONLY when Wrangler prompts you (hidden input).\n'
npx --yes wrangler@4.152.0 secret put GEMINI_API_KEY
printf '\nAt the next Wrangler prompt enter yes (not your API key).\n'
npx --yes wrangler@4.152.0 secret put GEMINI_FREE_TIER_CONFIRMED
npx --yes wrangler@4.152.0 deploy
cd ../aurix-chat-pdf-update
if command -v firebase >/dev/null 2>&1; then
  firebase deploy --only hosting --project aurix-ea09b
else
  npx --yes firebase-tools deploy --only hosting --project aurix-ea09b
fi
printf '\nDone: verify a real signed-in chat question at https://aurix-ea09b.web.app/?v=chat-pdf-20261024\n'
printf 'If it fails, share ONLY a screenshot with all tokens and keys hidden.\n'
