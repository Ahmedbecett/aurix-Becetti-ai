#!/usr/bin/env bash
# Deploy the ad-free AURIX build to Firebase Hosting (project aurix-ea09b).
# Usage: FIREBASE_TOKEN="$(firebase login:ci)" bash deploy/firebase-clean.sh
set -euo pipefail
cd "$(dirname "$0")/.."
: "${FIREBASE_TOKEN:?Set FIREBASE_TOKEN first (run: firebase login:ci)}"
npx --yes firebase-tools deploy --only hosting --project aurix-ea09b --non-interactive
echo "Deployed ad-free build to https://aurix-ea09b.web.app/"
