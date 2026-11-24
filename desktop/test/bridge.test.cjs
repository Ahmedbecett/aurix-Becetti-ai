const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = readFileSync(path.join(__dirname, '../../src/desktop-auth.mjs'), 'utf8');

async function bridge(callback, state = 'a'.repeat(64)) {
  let handler, replaced, cleared = false;
  const button = { disabled: true, addEventListener: (_name, fn) => { handler = fn; } };
  const status = { textContent: '' };
  const location = { search: '?' + new URLSearchParams({ callback, state }), replace: url => { replaced = new URL(url); } };
  const auth = {
    getAuth() {}, setPersistence: async () => {}, inMemoryPersistence: {},
    signInWithPopup: async () => ({}), signOut: async () => {},
    GoogleAuthProvider: class {
      setCustomParameters() {}
      static credentialFromResult() { return { idToken: 'google-id', accessToken: 'google-access' }; }
    }
  };
  const rewritten = source
    .replace("import('https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js')", 'Promise.resolve({ initializeApp(){} })')
    .replace("import('https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js')", 'Promise.resolve(mockAuth)');
  const ctx = vm.createContext({
    URL, URLSearchParams, location, mockAuth: auth,
    history: { replaceState: () => { cleared = true; } },
    document: { querySelector: selector => selector === '#signin' ? button : status },
    fetch: async () => ({ ok: true, json: async () => ({}) })
  });
  await vm.runInContext('(async()=>{' + rewritten + '})()', ctx);
  if (handler) await handler();
  return { button, status, replaced, cleared };
}
test('browser bridge rejects arbitrary/non-loopback destinations and invalid state', async () => {
  for (const callback of ['https://evil.test/callback', 'http://localhost:3000/callback', 'http://127.0.0.1:80/callback', 'http://127.0.0.1:3000/other', 'http://user@127.0.0.1:3000/callback', 'http://127.0.0.1:3000/callback?steal=1']) {
    const r = await bridge(callback);
    assert.equal(r.button.disabled, true, callback);
    assert.equal(r.replaced, undefined, callback);
  }
  assert.equal((await bridge('http://127.0.0.1:3000/callback', 'bad')).replaced, undefined);
});
test('browser bridge clears original link and returns credentials in fragment, never query', async () => {
  const r = await bridge('http://127.0.0.1:50000/callback');
  assert.equal(r.cleared, true);
  assert.equal(r.replaced.origin, 'http://127.0.0.1:50000');
  assert.equal(r.replaced.search, '');
  const fields = new URLSearchParams(r.replaced.hash.slice(1));
  assert.equal(fields.get('state'), 'a'.repeat(64));
  assert.equal(fields.get('idToken'), 'google-id');
});
test('standard web build retains dashboard and bundled PDF files', () => {
  const preview = readFileSync(path.join(__dirname, '../../release/preview/index.html'), 'utf8');
  const app = readFileSync(path.join(__dirname, '../../src/app.js'), 'utf8');
  assert.ok(preview.includes('<script>' + app + '</script>'));
  assert.match(app, /function bindDashboard/);
  assert.match(preview, /workspace-search/);
  assert.match(preview, /src="\/pdf-init.mjs"/);
  for (const name of ['assets/pdf.mjs', 'assets/pdf.worker.mjs', 'assets/pdfjs-LICENSE.txt', 'desktop-auth.html', 'desktop-auth.mjs', 'desktop-firebase.json']) {
    assert.ok(readFileSync(path.join(__dirname, '../../release/preview', name)).length > 0, name);
  }
});
