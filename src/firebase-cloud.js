/* Optional Firebase adapter. Loaded only when the owner supplies a PUBLIC Firebase web config.
   No Admin SDK, service-account credentials, or provider secrets belong here. */
const cfg = window.AURIX_FIREBASE_CONFIG;
if (cfg && cfg.apiKey && cfg.authDomain && cfg.projectId && cfg.appId) {
  const version = '10.14.1';
  const base = `https://www.gstatic.com/firebasejs/${version}/`;
  try {
    const [{ initializeApp }, auth, fs] = await Promise.all([
      import(base + 'firebase-app.js'),
      import(base + 'firebase-auth.js'),
      import(base + 'firebase-firestore.js')
    ]);
    const app = initializeApp(cfg);
    const a = auth.getAuth(app);
    const db = fs.getFirestore(app);
    const provider = new auth.GoogleAuthProvider();
    provider.setCustomParameters({ prompt: 'select_account' });
    const path = () => {
      if (!a.currentUser) throw Error('Sign in to save projects to the cloud.');
      return fs.collection(db, 'users', a.currentUser.uid, 'items');
    };
    const cloud = {
      get user() { return a.currentUser; },
      async signIn() { return auth.signInWithPopup(a, provider); },
      async getIdToken() { if (!a.currentUser) throw Error('Sign in with Google first.'); return a.currentUser.getIdToken(); },
      async signOut() { return auth.signOut(a); },
      async list() { const snapshot = await fs.getDocs(path()); return snapshot.docs.map(d => ({ id: d.id, ...d.data() })); },
      async save(item) {
        if (!item || !item.id || !['image', 'code', 'writer'].includes(item.kind)) throw Error('Invalid project.');
        await fs.setDoc(fs.doc(path(), item.id), {
          kind: item.kind, prompt: String(item.prompt || '').slice(0, 3500),
          result: String(item.result || '').slice(0, 30000),
          at: String(item.at || ''), folder: String(item.folder || 'Unsorted').slice(0, 42),
          fav: !!item.fav
        });
      },
      async remove(id) { await fs.deleteDoc(fs.doc(path(), id)); },
      async deleteAccount() {
        if (!a.currentUser) throw Error('Not signed in.');
        // Reauthenticate first. If this fails, no saved projects are deleted.
        await auth.reauthenticateWithPopup(a.currentUser, provider);
        while (true) {
          const docs = await fs.getDocs(fs.query(path(), fs.limit(100)));
          if (docs.empty) break;
          const batch = fs.writeBatch(db);
          docs.forEach(d => batch.delete(d.ref));
          await batch.commit();
        }
        await auth.deleteUser(a.currentUser);
      }
    };
    window.AurixCloud = cloud;
    auth.onAuthStateChanged(a, () => window.dispatchEvent(new Event('aurix-cloud')));
    window.dispatchEvent(new Event('aurix-cloud'));
  } catch (err) {
    console.error('AURIX cloud initialization failed:', err);
    window.dispatchEvent(new CustomEvent('aurix-cloud-error', { detail: 'Account service is unavailable.' }));
  }
}
