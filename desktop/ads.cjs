'use strict';
/* MG Ads (Miracle Games) client credentials for the packaged Windows build.

   The owner cannot generate separate keys: MG Ads issues one client key per
   application and that key is embedded in the app itself (the same pattern MG
   publishes in its own SDK samples). This module therefore carries the shipped
   client credential, ships inside app.asar, and keeps two rules:

     1. It is only ever handed to the MG Ads runtime — never to the renderer
        page, never to the website, never to a log or a support report. The page
        can only ask whether the credential is installed (true/false).
     2. A build-time environment override still wins, so a rotated key can be
        supplied without editing source.

   Treat this as a client credential, not a server secret: anyone who installs
   the MSIX can read it, exactly as in MG's own samples. Never use it for an API
   that authorizes payouts, uploads or account administration. */

// Default, build-time values (client credentials shipped in the package).
const BUILD_CREDENTIALS = Object.freeze({
  appId: '692e5d6a207c9dd383ba56f7',
  secretKey: 'MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQggSW3Y6T33c7eJPZD+mFRkeJwP4XiaKJthgWbj8YwnMagCgYIKoZIzj0DAQehRANCAARz2TWOHafmtTGEP3kDAJet8vtwBqnj0ZRtNy7W75JT1LPsiif7RdediRUg1A9rSr+FqQHUC6F7fFjMQAgMkjjg'
});

// Optional runtime override: AURIX_MGADS_APP_ID / AURIX_MGADS_SECRET_KEY.
const APP_ID_KEYS = ['AURIX_MGADS_APP_ID'];
const SECRET_KEYS = ['AURIX_MGADS_SECRET_KEY'];
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

function valid(appId, secretKey) {
  return typeof appId === 'string' && typeof secretKey === 'string' &&
    APP_ID_SHAPE.test(appId) && SECRET_SHAPE.test(secretKey);
}

// Resolution order: a complete, well-formed environment override, then the
// client credential shipped in the package. A partial override is ignored.
function readCredentials(env = process.env) {
  const appId = firstEnv(env, APP_ID_KEYS);
  const secretKey = firstEnv(env, SECRET_KEYS);
  if (appId && secretKey && valid(appId, secretKey)) {
    return Object.freeze({ appId, secretKey, source: 'environment' });
  }
  if (valid(BUILD_CREDENTIALS.appId, BUILD_CREDENTIALS.secretKey)) {
    return Object.freeze({
      appId: BUILD_CREDENTIALS.appId,
      secretKey: BUILD_CREDENTIALS.secretKey,
      source: 'package'
    });
  }
  return null;
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
