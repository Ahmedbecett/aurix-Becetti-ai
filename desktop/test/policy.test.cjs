const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { ORIGIN, isAppURL, externalURL, assetPath } = require('../policy.cjs');

test('only the exact application HTTPS origin is trusted', () => {
  assert.equal(isAppURL(ORIGIN + '/#image'), true);
  for (const url of ['http://aurix-ea09b.web.app/', ORIGIN + '.evil.test/', 'file:///tmp/x', 'https://evil.test/', 'not a URL', 'https://user@aurix-ea09b.web.app/']) assert.equal(isAppURL(url), false, url);
});
test('external navigation accepts HTTPS/mail only, not scripts, files or local services', () => {
  assert.equal(externalURL('https://policies.google.com/privacy'), true);
  assert.equal(externalURL('mailto:ahmedbecetti41@gmail.com'), true);
  for (const url of ['javascript:alert(1)', 'data:text/html,x', 'file:///C:/Windows', 'http://example.com', 'https://127.0.0.1/x', 'https://10.0.0.1/', 'https://[::1]/', 'https://localhost/', 'https://user:pass@example.com']) assert.equal(externalURL(url), false, url);
});
test('bundled resources cannot escape the package directory', () => {
  const root = path.resolve('release/preview');
  assert.equal(assetPath(ORIGIN + '/', root), path.join(root, 'index.html'));
  assert.equal(assetPath(ORIGIN + '/assets/pdf.mjs', root), path.join(root, 'assets/pdf.mjs'));
  for (const url of [ORIGIN + '/..%2f..%2fsecret', ORIGIN + '/%5c..%5csecret', ORIGIN + '/%00', ORIGIN + '/%E0%A4%A', 'https://evil.test/index.html']) assert.equal(assetPath(url, root), null, url);
});
