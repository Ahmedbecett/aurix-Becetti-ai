'use strict';
const http = require('node:http');
const { randomBytes, timingSafeEqual } = require('node:crypto');
const { ORIGIN } = require('./policy.cjs');
const CALLBACK_SCRIPT = `
const fields = new URLSearchParams(location.hash.slice(1));
history.replaceState(null, '', '/callback');
fetch('/complete', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(Object.fromEntries(fields))})
.then(r=>{if(!r.ok)throw Error(); document.querySelector('p').textContent='Signed in. You can close this tab and return to AURIX.';})
.catch(()=>{document.querySelector('p').textContent='Sign-in failed or expired. Return to AURIX and try again.';});
`;
const CALLBACK_HTML = '<!doctype html><html lang="en"><meta charset="utf-8"><title>AURIX sign-in</title><h1>AURIX</h1><p>Completing sign-in…</p><script src="/callback.js"></script></html>';

// No OAuth client secret or Firebase ID token is stored in the desktop main process.
// A single-use random state binds the external browser result to one login attempt.
async function startAuth(openExternal, { timeoutMs = 180000 } = {}) {
  const state = randomBytes(32).toString('hex');
  let settle, fail, timer, completed = false;
  const result = new Promise((resolve, reject) => { settle = resolve; fail = reject; });
  // Attach immediately: a cancelled startup must not create an unhandled rejection.
  result.catch(() => {});
  const finish = (err, credentials) => {
    if (completed) return;
    completed = true;
    clearTimeout(timer);
    server.close();
    server.closeIdleConnections();
    if (err) fail(err); else settle(credentials);
  };
  const server = http.createServer(async (req, res) => {
    const expectedHost = `127.0.0.1:${server.address()?.port}`;
    const headers = {
      'Cache-Control': 'no-store',
      'Content-Security-Policy': "default-src 'none'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
      'Referrer-Policy': 'no-referrer', 'X-Content-Type-Options': 'nosniff'
    };
    const reply = (status, body, type = 'text/plain; charset=utf-8') => {
      res.writeHead(status, { ...headers, 'Content-Type': type }); res.end(body);
    };
    if (req.headers.host !== expectedHost) return reply(403, 'Invalid host');
    if (req.method === 'GET' && req.url === '/callback') return reply(200, CALLBACK_HTML, 'text/html; charset=utf-8');
    if (req.method === 'GET' && req.url === '/callback.js') return reply(200, CALLBACK_SCRIPT, 'text/javascript; charset=utf-8');
    if (req.method !== 'POST' || req.url !== '/complete') return reply(404, 'Not found');
    if (req.headers.origin !== `http://${expectedHost}` || !req.headers['content-type']?.startsWith('application/json')) return reply(403, 'Invalid origin');
    let size = 0, body = '';
    try {
      for await (const chunk of req) {
        size += chunk.length;
        if (size > 24000) { reply(413, 'Too large'); req.destroy(); return; }
        body += chunk;
      }
      const data = JSON.parse(body);
      if (typeof data.state !== 'string' || data.state.length !== state.length ||
          !timingSafeEqual(Buffer.from(data.state), Buffer.from(state))) return reply(403, 'Invalid state');
      if (completed) return reply(409, 'Already completed');
      if (data.error) {
        reply(400, 'Sign-in cancelled or failed');
        finish(Error('Google sign-in was cancelled or failed. Please try again.'));
        return;
      }
      if (typeof data.idToken !== 'string' || data.idToken.length < 20 || data.idToken.length > 12000 ||
          (data.accessToken !== undefined && (typeof data.accessToken !== 'string' || data.accessToken.length > 8000))) return reply(400, 'Invalid credentials');
      reply(200, 'OK');
      finish(null, { idToken: data.idToken, accessToken: data.accessToken || null });
    } catch { reply(400, 'Invalid request'); }
  });
  server.requestTimeout = 10000;
  server.headersTimeout = 10000;
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  server.on('error', () => finish(Error('Could not complete desktop sign-in.')));
  timer = setTimeout(() => finish(Error('Sign-in timed out. Please try again.')), timeoutMs);
  const callback = `http://127.0.0.1:${server.address().port}/callback`;
  const url = new URL('/desktop-auth.html', ORIGIN);
  url.search = new URLSearchParams({ callback, state }).toString();
  try { await openExternal(url.href); }
  catch { finish(Error('Could not open the system browser.')); }
  return { result, cancel: () => finish(Error('Sign-in cancelled.')) };
}
module.exports = { startAuth };
