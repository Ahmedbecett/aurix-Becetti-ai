'use strict';
/* MG Ads (Miracle Games) credentials for the packaged Windows build.
   The App ID and the Secret Key are read from the process environment and are
   never written to Git, never sent to the renderer and never logged. They are
   passed only to the native MG Ads runtime inside the packaged app.
   Where credentials may be read from, in order:
     1. AURIX_MGADS_APP_ID / AURIX_MGADS_SECRET_KEY
     2. MGADS_APP_ID / MGADS_SECRET_KEY
   Both values must be present together; a partial pair is treated as absent. */
const APP_ID_KEYS = ['AURIX_MGADS_APP_ID', 'MGADS_APP_ID'];
const SECRET_KEYS = ['AURIX_MGADS_SECRET_KEY', 'MGADS_SECRET_KEY'];
const APP_ID_SHAPE = /^[a-f0-9]{16,64}$/i;
// Base64-encoded DER (PKCS#8) P-256 key, as issued by the MG Ads dashboard.
const SECRET_SHAPE = /^[A-Za-z0-9+/]{64,}={0,2}$/;

function firstEnv(env, keys) {
  for (const key of keys) {
    const value = env && typeof env[key] === 'string' ? env[key].trim() : '';
    if (value) return value;
  }
  return '';
}

function readCredentials(env = process.env) {
  const appId = firstEnv(env, APP_ID_KEYS);
  const secretKey = firstEnv(env, SECRET_KEYS);
  if (!appId || !secretKey) return null;
  if (!APP_ID_SHAPE.test(appId) || !SECRET_SHAPE.test(secretKey)) return null;
  return Object.freeze({ appId, secretKey });
}

function credentialsInstalled(env = process.env) {
  return readCredentials(env) !== null;
}

// Third-party ads must never sit on the account sign-in screen, and the banner
// needs the full 728x90 width without breaking the layout.
const MIN_AD_WINDOW_WIDTH = 800;
function shouldRequestAds({ width, authMode }) {
  return !authMode && Number(width) >= MIN_AD_WINDOW_WIDTH;
}

// Public placement identifiers supplied by the owner; they are not secrets.
const SLOTS = Object.freeze([
  Object.freeze({ key: 'banner-1', unitId: 'f97e5aa93a22438f8ef1d3e549d7a245' }),
  Object.freeze({ key: 'banner-2', unitId: 'fc1e2f0faa8343d889687c5fc9ba19a3' })
]);

module.exports = { readCredentials, credentialsInstalled, shouldRequestAds, SLOTS, MIN_AD_WINDOW_WIDTH };
