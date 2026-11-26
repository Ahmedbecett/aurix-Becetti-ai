const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

async function adapter(desktop) {
  const calls = [];
  const user = { uid: 'test-user' };
  const auth = {
    getAuth: () => ({ currentUser: user }),
    GoogleAuthProvider: class { setCustomParameters() {} static credential(...args) { return args; } },
    signInWithPopup: async () => calls.push('popup'),
    signInWithCredential: async (_a, credential) => calls.push(['credential', credential]),
    reauthenticateWithPopup: async () => calls.push('reauth-popup'),
    reauthenticateWithCredential: async (_u, credential) => calls.push(['reauth-credential', credential]),
    onAuthStateChanged: () => {},
    deleteUser: async () => calls.push('delete')
  };
  const fs = { getFirestore() {}, collection() {}, query() {}, limit() {}, getDocs: async () => ({ empty: true }) };
  const window = {
    AURIX_FIREBASE_CONFIG: { apiKey: 'public', authDomain: 'example.test', projectId: 'test', appId: 'test' },
    dispatchEvent() {},
    ...(desktop ? { AurixDesktop: { signIn: async () => ({ idToken: 'google-id', accessToken: 'google-access' }) } } : {})
  };
  const source = readFileSync(path.join(__dirname, '../../src/firebase-cloud.js'), 'utf8');
  // Substitute only the remote module import; exercise the real adapter logic.
  const rewritten = source.replaceAll("import(base + 'firebase-app.js')", 'Promise.resolve({initializeApp(){}})')
    .replaceAll("import(base + 'firebase-auth.js')", 'Promise.resolve(mockAuth)')
    .replaceAll("import(base + 'firebase-firestore.js')", 'Promise.resolve(mockFs)');
  const ctx = vm.createContext({ window, mockAuth: auth, mockFs: fs, console, Event: class {}, CustomEvent: class {} });
  await vm.runInContext('(async()=>{' + rewritten + '})()', ctx);
  await window.AurixCloud.signIn();
  await window.AurixCloud.deleteAccount();
  return JSON.parse(JSON.stringify(calls));
}
test('desktop sign-in and reauthentication use browser-returned Google credentials', async () => {
  assert.deepEqual(await adapter(true), [['credential', ['google-id', 'google-access']], ['reauth-credential', ['google-id', 'google-access']], 'delete']);
});
test('ordinary web sign-in and account deletion preserve existing popup behavior', async () => {
  assert.deepEqual(await adapter(false), ['popup', 'reauth-popup', 'delete']);
});
