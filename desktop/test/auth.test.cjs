const { test } = require('node:test');
const assert = require('node:assert/strict');
const { startAuth } = require('../auth.cjs');

async function attempt(options) {
  let url;
  const auth = await startAuth(value => { url = new URL(value); }, options);
  const callback = new URL(url.searchParams.get('callback'));
  return { ...auth, url, callback, state: url.searchParams.get('state') };
}
async function post(a, data, origin = a.callback.origin) {
  return fetch(new URL('/complete', a.callback), { method: 'POST', headers: { 'Content-Type': 'application/json', Origin: origin }, body: JSON.stringify(data) });
}
test('login opens only the hosted bridge, receives credentials once via loopback POST', async () => {
  const a = await attempt();
  try {
    assert.equal(a.url.origin, 'https://aurix-ea09b.web.app');
    assert.equal(a.url.pathname, '/desktop-auth.html');
    assert.match(a.state, /^[a-f0-9]{64}$/);
    assert.equal(a.callback.hostname, '127.0.0.1');
    const page = await fetch(a.callback);
    assert.equal(page.status, 200);
    assert.equal(page.headers.get('cache-control'), 'no-store');
    assert.match(page.headers.get('content-security-policy'), /frame-ancestors 'none'/);
    const script = await (await fetch(new URL('/callback.js', a.callback))).text();
    assert.match(script, /history.replaceState/);
    const creds = { state: a.state, idToken: 'google-id-token-for-test-only', accessToken: 'access-for-test' };
    assert.equal((await post(a, creds, 'https://evil.test')).status, 403);
    assert.equal((await post(a, { ...creds, state: 'a'.repeat(64) })).status, 403);
    assert.equal((await post(a, { state: a.state, idToken: '' })).status, 400);
    assert.equal((await post(a, creds)).status, 200);
    assert.deepEqual(await a.result, { idToken: creds.idToken, accessToken: creds.accessToken });
    await assert.rejects(() => post(a, creds));
  } finally { a.cancel(); }
});
test('cancellation and browser startup failure reject without returning credentials', async () => {
  const a = await attempt();
  a.cancel();
  await assert.rejects(a.result, /cancelled/);
  const b = await startAuth(() => { throw Error('Browser failure'); });
  await assert.rejects(b.result, /open the system browser/);
});
test('abandoned login expires and closes its local callback server', async () => {
  const a = await attempt({ timeoutMs: 30 });
  await assert.rejects(a.result, /timed out/);
  await assert.rejects(() => fetch(a.callback));
});
test('callback rejects cross-host requests, invalid JSON, oversized data and unknown routes', async () => {
  const a = await attempt();
  try {
    assert.equal((await fetch(new URL('/other', a.callback))).status, 404);
    const hostStatus = await new Promise((resolve, reject) => {
      require('node:http').get(a.callback, { headers: { Host: 'evil.test' } }, response => {
        response.resume(); resolve(response.statusCode);
      }).on('error', reject);
    });
    assert.equal(hostStatus, 403);
    const invalid = await fetch(new URL('/complete', a.callback), { method: 'POST', headers: { Origin: a.callback.origin, 'Content-Type': 'application/json' }, body: 'not json' });
    assert.equal(invalid.status, 400);
    assert.equal((await post(a, { value: 'x'.repeat(25000) })).status, 413);
  } finally { a.cancel(); await assert.rejects(a.result, /cancelled/); }
});
