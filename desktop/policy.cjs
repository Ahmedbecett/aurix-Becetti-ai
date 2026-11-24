'use strict';
const path = require('node:path');
const ORIGIN = 'https://aurix-ea09b.web.app';
const PARTITION = 'persist:aurix-studio';

function isAppURL(value) {
  try { const u = new URL(value); return u.origin === ORIGIN && !u.username && !u.password; }
  catch { return false; }
}
function externalURL(value) {
  try {
    const u = new URL(value);
    if (u.username || u.password) return false;
    if (u.protocol === 'mailto:') return true;
    if (u.protocol !== 'https:') return false;
    // Never hand local/private hosts to the system browser from renderer input.
    return !/^(localhost|.*\.localhost|127\..*|0\..*|10\..*|192\.168\..*|172\.(1[6-9]|2\d|3[01])\..*|\[.*\])$/i.test(u.hostname);
  } catch { return false; }
}
function assetPath(url, root) {
  if (!isAppURL(url)) return null;
  let name;
  try { name = decodeURIComponent(new URL(url).pathname); } catch { return null; }
  if (name === '/') name = '/index.html';
  if (name.includes('\\') || name.includes('\0')) return null;
  const target = path.resolve(root, '.' + name);
  return target.startsWith(path.resolve(root) + path.sep) ? target : null;
}
module.exports = { ORIGIN, PARTITION, isAppURL, externalURL, assetPath };
