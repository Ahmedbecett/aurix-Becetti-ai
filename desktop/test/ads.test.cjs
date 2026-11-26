const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const ads = require('../../desktop/ads.cjs');

const SRC = read('../../src/ads.js');
const PRELOAD = read('../../desktop/preload.cjs');
const INDEX = read('../../release/preview/index.html');
const BANNER_1 = 'f97e5aa93a22438f8ef1d3e549d7a245';
const BANNER_2 = 'fc1e2f0faa8343d889687c5fc9ba19a3';

function read(rel) {
  return fs.readFileSync(path.join(__dirname, rel), 'utf8');
}

// --- A tiny DOM: enough for this module, and it fails loudly on anything else.
class Node2 {
  constructor(tag) {
    this.tagName = String(tag).toUpperCase();
    this.children = [];
    this.dataset = {};
    this.attributes = {};
    this.listeners = {};
    this.textContent = '';
    this.hidden = false;
    this.id = '';
    this.className = '';
    this.parent = null;
    const self = this;
    const list = () => String(self.className).split(/\s+/).filter(Boolean);
    this.classList = {
      contains: name => list().includes(name),
      add: name => { if (!list().includes(name)) self.className = [...list(), name].join(' '); },
      remove: name => { self.className = list().filter(n => n !== name).join(' '); },
      toggle: (name, force) => {
        const on = force === undefined ? !list().includes(name) : !!force;
        if (on) self.classList.add(name); else self.classList.remove(name);
        return on;
      }
    };
  }
  append(...nodes) { for (const n of nodes) { n.parent = this; this.children.push(n); } }
  insertBefore(node, ref) {
    node.parent = this;
    const i = this.children.indexOf(ref);
    if (i < 0) this.children.push(node); else this.children.splice(i, 0, node);
  }
  setAttribute(k, v) { this.attributes[k] = String(v); }
  getAttribute(k) { return this.attributes[k]; }
  addEventListener(name, fn) { (this.listeners[name] = this.listeners[name] || []).push(fn); }
  dispatch(name, event = {}) { (this.listeners[name] || []).forEach(fn => fn(event)); }
  matches() { return false; }
  querySelectorAll(selector) {
    const byClass = selector.startsWith('.') ? selector.slice(1) : null;
    const out = [];
    const walk = node => node.children.forEach(child => {
      const hit = byClass && String(child.className).split(/\s+/).includes(byClass);
      const hitById = selector.startsWith('#') && child.id === selector.slice(1);
      if (hit || hitById) out.push(child);
      walk(child);
    });
    walk(this);
    return out;
  }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
}

function environment({ desktop = true, width = 1400, credentials = true, sdk = 'host' } = {}) {
  const document = new Node2('html');
  const head = new Node2('head');
  const body = new Node2('body');
  body.className = '';
  document.append(head, body);
  document.head = head;
  document.body = body;
  document.documentElement = document;
  document.readyState = 'complete';
  document.getElementById = id => document.querySelector('#' + id) || null;
  document.createElement = tag => new Node2(tag);

  const wrap = new Node2('div'); wrap.className = 'aurix-wrap';
  const footer = new Node2('footer'); footer.className = 'aurix-foot';
  wrap.append(footer); body.append(wrap);

  const windowListeners = {};
  const window = {
    innerWidth: width,
    document,
    listeners: windowListeners,
    addEventListener: (name, fn) => { (windowListeners[name] = windowListeners[name] || []).push(fn); },
    dispatch: name => (windowListeners[name] || []).forEach(fn => fn({})),
    setTimeout: (fn, ms) => setTimeout(fn, ms),
    clearTimeout
  };
  window.window = window;
  if (desktop) {
    window.AurixDesktop = {
      signIn: async () => ({}),
      ads: {
        enabled: true,
        credentialsInstalled: () => ({ installed: credentials }),
        listSlots: () => ads.SLOTS.map(s => ({ key: s.key, unitId: s.unitId }))
      }
    };
  }
  if (sdk === 'host') {
    window.chrome = { webview: { hostObjects: { MGADSDK: { mgExchange() {} } } } };
  }
  const requests = [];
  window.fetch = async () => { throw Error('ads.js must not use fetch'); };
  return { window, document, body, head, wrap, footer, requests };
}

function run(env) {
  const ctx = vm.createContext({
    window: env.window,
    document: env.document,
    MutationObserver: undefined,
    console,
    setTimeout,
    clearTimeout,
    URL,
    JSON,
    Object,
    String,
    Promise,
    Error
  });
  env.window.window = env.window;
  vm.runInContext(SRC, ctx);
  return env;
}

function sdkScript(env) {
  return env.head.children.find(n => n.tagName === 'SCRIPT' && /h5adsdk\.js$/.test(n.src));
}

test('banner placements are exactly the two owner-supplied AdUnitIds', () => {
  assert.deepEqual(ads.SLOTS.map(s => s.unitId), [BANNER_1, BANNER_2]);
  assert.deepEqual(ads.SLOTS.map(s => s.key), ['banner-1', 'banner-2']);
  assert.match(SRC, new RegExp(BANNER_1));
  assert.match(SRC, new RegExp(BANNER_2));
  // No third placement, and no invented identifier, may sneak in.
  assert.equal((SRC.match(/unitId: '[a-f0-9]{32}'/g) || []).length, 2);
});

test('the module is inert in a packaged-less browser: no region, no SDK, no network', () => {
  const env = run(environment({ desktop: false }));
  assert.equal(env.document.querySelector('#aurix-ads') || null, null);
  assert.equal(sdkScript(env) || null, null);
  assert.equal(env.window.AurixAds.state().mounted, false);
});

test('desktop build mounts both slots, loads the MG Ads H5 SDK once and requests banner type 3', async () => {
  const env = run(environment());
  const region = env.document.querySelector('#aurix-ads');
  assert.ok(region, 'ad region mounted');
  assert.equal(env.document.querySelectorAll('.ad-slot').length, 2);
  assert.equal(region.parent, env.wrap);
  assert.equal(env.wrap.children.indexOf(region) + 1, env.wrap.children.indexOf(env.footer));
  const script = sdkScript(env);
  assert.ok(script, 'SDK script injected');
  assert.equal(script.src, 'https://ad.mguwp.net/js/h5adsdk.js');

  const shown = [];
  env.window.ShowAd = param => shown.push(JSON.parse(param));
  script.onload();
  await new Promise(r => setTimeout(r, 0));
  assert.deepEqual(shown, [
    { unitId: BANNER_1, adType: 3, media: 'image' },
    { unitId: BANNER_2, adType: 3, media: 'image' }
  ]);
  assert.equal(env.document.querySelector('#ad-frame-banner-1').dataset.state, 'ready');
  assert.equal(env.head.children.filter(n => n.tagName === 'SCRIPT').length, 1);
  env.window.AurixAds.sync();
  assert.equal(shown.length, 2, 're-render must not request the same banner twice');
});

test('missing credentials stop the request, keep the reserved slot and never print a secret', async () => {
  const env = run(environment({ credentials: false }));
  const shown = [];
  env.window.ShowAd = param => shown.push(param);
  sdkScript(env).onload();
  await new Promise(r => setTimeout(r, 0));
  assert.deepEqual(shown, []);
  const frame = env.document.querySelector('#ad-frame-banner-1');
  assert.equal(frame.dataset.state, 'error');
  assert.match(frame.textContent, /no MG Ads credentials/i);
  assert.equal(env.document.querySelector('#ad-frame-banner-2').dataset.state, 'error');
  assert.doesNotMatch(INDEX, /MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg/);
});

test('an SDK that cannot load reports it instead of leaving a silent empty box', async () => {
  const env = run(environment({ sdk: 'missing' }));
  const script = sdkScript(env);
  script.onload(); // loads, but no WebView2 host object exists
  await new Promise(r => setTimeout(r, 0));
  assert.equal(env.document.querySelector('#ad-frame-banner-1').dataset.state, 'error');
  assert.match(env.document.querySelector('#ad-frame-banner-1').textContent, /SDK did not load/i);
});

test('provider close/click callbacks are mapped by AdUnitId, unknown ids ignored', () => {
  const env = run(environment());
  env.window.AdCloseEvent(JSON.stringify({ unitId: BANNER_2, advertStatus: 3 }));
  assert.equal(env.document.querySelector('#ad-frame-banner-2').dataset.state, 'error');
  assert.match(env.document.querySelector('#ad-frame-banner-2').textContent, /no banner material/i);
  env.window.AdCloseEvent(JSON.stringify({ unitId: BANNER_2, advertStatus: 2 }));
  assert.match(env.document.querySelector('#ad-frame-banner-2').textContent, /switched off/i);
  env.window.AdClickEvent(JSON.stringify({ unitId: BANNER_1 }));
  assert.match(env.document.querySelector('#ad-frame-banner-1').textContent, /opened/i);
  env.window.AdCloseEvent('not json');
  env.window.AdCloseEvent(JSON.stringify({ unitId: 'ffffffffffffffffffffffffffffffff', advertStatus: 3 }));
  assert.equal(env.document.querySelector('#ad-frame-banner-1').dataset.state, 'ready');
});

test('sign-in screen and narrow windows are excluded, and the region returns', async () => {
  const env = run(environment());
  assert.equal(env.document.querySelector('#aurix-ads').hidden, false);
  env.body.className = 'auth-mode';
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('#aurix-ads').hidden, true);
  env.body.className = '';
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('#aurix-ads').hidden, false);
  env.window.innerWidth = 640;
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('#aurix-ads').hidden, true);
  env.window.innerWidth = 1400;
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('#aurix-ads').hidden, false);
});

test('localized labels follow the document language', () => {
  const env = run(environment());
  env.document.documentElement.lang = 'ar';
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('.ad-tag').textContent, 'إعلان');
  assert.equal(env.document.querySelector('#aurix-ads').getAttribute('aria-label'), 'رسائل دعائية');
  env.document.documentElement.lang = 'fr';
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('.ad-tag').textContent, 'Publicité');
  env.document.documentElement.lang = 'en';
  env.window.AurixAds.sync();
  assert.equal(env.document.querySelector('.ad-tag').textContent, 'Advertisement');
});

test('credentials are read only from the environment, validated, and never exposed to the page', () => {
  // Throw-away key generated for this test only; never a real MG Ads credential.
  const secret = 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgud/tAUtU6eq4u69lakVeqq/yH9Dz2ZdOQFTdpfFVOiyhRANCAATp0N0vPiiB4l+GXHxpbpIRQaZiamuVaDO3ZlJqk1BmE8Aljo0kSCAYSbuN89/Dv7QZ0vBzJCRsX6nVWMeuOVrj';
  assert.equal(ads.readCredentials({}), null);
  assert.equal(ads.credentialsInstalled({ AURIX_MGADS_APP_ID: '692e5d6a207c9dd383ba56f7' }), false, 'partial pair');
  assert.equal(ads.credentialsInstalled({ AURIX_MGADS_APP_ID: 'not-an-id', AURIX_MGADS_SECRET_KEY: secret }), false, 'bad app id');
  assert.equal(ads.credentialsInstalled({ AURIX_MGADS_APP_ID: '692e5d6a207c9dd383ba56f7', AURIX_MGADS_SECRET_KEY: 'short' }), false, 'bad key shape');
  const env = { MGADS_APP_ID: '692e5d6a207c9dd383ba56f7', MGADS_SECRET_KEY: secret };
  const found = ads.readCredentials(env);
  assert.equal(found.appId, '692e5d6a207c9dd383ba56f7');
  assert.equal(found.secretKey, secret);
  assert.equal(Object.isFrozen(found), true);
  // Nothing in the shipped renderer or preload can carry the secret.
  assert.doesNotMatch(SRC, /secretKey|appId|MIGT[0-9A-Za-z+/=]{60,}/);
  assert.doesNotMatch(PRELOAD, /secretKey|appId|mgExchange/i);
  assert.match(PRELOAD, /credentialsInstalled: \(\) => ipcRenderer\.sendSync\('aurix:ads-credentials'\)/);
  assert.doesNotMatch(INDEX, /MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg/);
});

test('ads are suppressed on the sign-in screen and below the banner width', () => {
  assert.equal(ads.shouldRequestAds({ width: 1400, authMode: false }), true);
  assert.equal(ads.shouldRequestAds({ width: 1400, authMode: true }), false);
  assert.equal(ads.shouldRequestAds({ width: 799, authMode: false }), false);
  assert.equal(ads.shouldRequestAds({ width: 800, authMode: false }), true);
});

test('the Electron shell allows the SDK host but keeps every other guard', () => {
  const main = read('../../desktop/main.cjs');
  assert.match(main, /script-src[^"]*https:\/\/ad\.mguwp\.net/);
  assert.match(main, /frame-src[^"]*\*\.mguwp\.net/);
  assert.match(main, /contextIsolation: true, nodeIntegration: false, sandbox: true/);
  assert.match(main, /object-src 'none'/);
  assert.match(main, /form-action 'none'/);
  // The capability flags are synchronous, read-only reads of process env.
  assert.match(main, /ipcMain\.on\('aurix:ads-credentials'/);
  assert.doesNotMatch(main, /aurix:ads-secret|secretKey:\s*'/);
  const preload = read('../../desktop/preload.cjs');
  assert.match(preload, /process\.isMainFrame && location\.origin === APP_ORIGIN/);
  assert.match(preload, /enabled: true/);
});

test('the built page ships the ad module and keeps the app untouched', () => {
  assert.match(INDEX, /<script>\/\* AURIX — MG Ads/);
  assert.ok(INDEX.indexOf('/\* AURIX — MG Ads') > INDEX.indexOf('AURIX: user-controlled content reports'));
  assert.match(INDEX, /workspace-search/);
  assert.match(INDEX, /data-route="billing"/);
});
