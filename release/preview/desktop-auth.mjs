// This page runs ONLY in the user's ordinary system browser, never an embedded
// OAuth window. Google credentials travel in a loopback URL fragment, then a
// same-origin POST; fragments are not sent to Firebase Hosting or HTTP logs.
const button = document.querySelector('#signin');
const status = document.querySelector('#status');
let callback, state;
try {
  const params = new URLSearchParams(location.search);
  callback = new URL(params.get('callback'));
  state = params.get('state');
  if (callback.protocol !== 'http:' || callback.hostname !== '127.0.0.1' ||
      !callback.port || Number(callback.port) < 1024 || callback.pathname !== '/callback' ||
      callback.search || callback.hash || callback.username || callback.password || !/^[a-f0-9]{64}$/.test(state || '')) throw Error('Invalid callback');
  history.replaceState(null, '', '/desktop-auth.html');
  const [cfg, { initializeApp }, auth] = await Promise.all([
    fetch('/desktop-firebase.json', { cache: 'no-store' }).then(r => { if (!r.ok) throw Error('Configuration unavailable'); return r.json(); }),
    import('https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js'),
    import('https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js')
  ]);
  const app = initializeApp(cfg, 'aurix-desktop-browser');
  const a = auth.getAuth(app);
  await auth.setPersistence(a, auth.inMemoryPersistence);
  const provider = new auth.GoogleAuthProvider();
  provider.setCustomParameters({ prompt: 'select_account' });
  button.disabled = false;
  status.textContent = 'اضغط للمتابعة. سيتم فتح نافذة Google في متصفحك.';
  button.addEventListener('click', async () => {
    button.disabled = true;
    try {
      const result = await auth.signInWithPopup(a, provider);
      const credential = auth.GoogleAuthProvider.credentialFromResult(result);
      if (!credential?.idToken) throw Error('Google did not return a credential');
      callback.hash = new URLSearchParams({ state, idToken: credential.idToken, ...(credential.accessToken ? { accessToken: credential.accessToken } : {}) }).toString();
      await auth.signOut(a);
      status.textContent = 'جارٍ العودة إلى التطبيق…';
      location.replace(callback.href);
    } catch {
      status.textContent = 'لم يكتمل تسجيل الدخول. تحقق من الاتصال والسماح بالنوافذ المنبثقة، ثم حاول مجددًا.';
      button.disabled = false;
    }
  });
} catch {
  status.textContent = 'الرابط غير صالح أو خدمة الدخول غير متاحة. ابدأ تسجيل الدخول من تطبيق AURIX مجددًا.';
}
