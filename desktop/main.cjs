'use strict';
const { app, BrowserWindow, Menu, ipcMain, session, shell, net, dialog } = require('electron');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { stat } = require('node:fs/promises');
const { ORIGIN, PARTITION, isAppURL, externalURL, assetPath } = require('./policy.cjs');
const { startAuth } = require('./auth.cjs');
let mainWindow, pendingAuth;
const singleInstance = app.requestSingleInstanceLock();
if (!singleInstance) app.quit();
else {
  app.on('second-instance', () => { if (mainWindow) { if (mainWindow.isMinimized()) mainWindow.restore(); mainWindow.show(); mainWindow.focus(); } });
  app.whenReady().then(createWindow).catch(err => {
    dialog.showErrorBox('AURIX could not start', err.message); app.quit();
  });
}
app.on('window-all-closed', () => { pendingAuth?.cancel(); app.quit(); });

async function createWindow() {
  const ses = session.fromPartition(PARTITION);
  const root = path.join(app.getAppPath(), 'release', 'preview');
  // A stable HTTPS origin keeps existing Firebase authorized domains, Worker CORS,
  // IndexedDB and secure-context APIs. Only bundled files are served to this session.
  await ses.protocol.handle('https', async req => {
    if (!isAppURL(req.url)) return ses.fetch(req, { bypassCustomProtocolHandlers: true });
    const target = assetPath(req.url, root);
    if (!target || req.method !== 'GET') return new Response('Not found', { status: 404 });
    try {
      if (!(await stat(target)).isFile()) return new Response('Not found', { status: 404 });
      const file = await net.fetch(pathToFileURL(target).href);
      const headers = new Headers(file.headers);
      headers.set('X-Content-Type-Options', 'nosniff');
      headers.set('Referrer-Policy', 'no-referrer');
      // Inline styles/scripts belong to the existing generated application. Node
      // remains inaccessible even to script in the renderer or generated previews.
      headers.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.gstatic.com https://apis.google.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob: https:; font-src 'self' data:; connect-src 'self' https://*.googleapis.com https://*.firebaseio.com wss://*.firebaseio.com https://aurix-api-ea09b.ahmedbecetti41.workers.dev; frame-src 'self' https://aurix-ea09b.firebaseapp.com; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; form-action 'none'");
      return new Response(file.body, { status: file.status, headers });
    } catch { return new Response('Bundled page not found', { status: 404 }); }
  });
  ses.setPermissionRequestHandler((wc, permission, callback, details) => {
    callback(wc === mainWindow?.webContents && isAppURL(details.requestingUrl) && permission === 'clipboard-sanitized-write');
  });
  ses.setPermissionCheckHandler((wc, permission, origin) => wc === mainWindow?.webContents && isAppURL(origin) && permission === 'clipboard-sanitized-write');
  mainWindow = new BrowserWindow({
    width: 1380, height: 900, minWidth: 800, minHeight: 600,
    backgroundColor: '#0b1020', title: 'AURIX', show: false,
    icon: path.join(__dirname, 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'), partition: PARTITION,
      contextIsolation: true, nodeIntegration: false, sandbox: true,
      webSecurity: true, allowRunningInsecureContent: false, webviewTag: false,
      navigateOnDragDrop: false
    }
  });
  mainWindow.once('ready-to-show', () => mainWindow.show());
  mainWindow.on('closed', () => { mainWindow = null; });
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (externalURL(url)) shell.openExternal(url).catch(() => {});
    return { action: 'deny' };
  });
  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (isAppURL(url)) return;
    event.preventDefault();
    if (externalURL(url)) shell.openExternal(url).catch(() => {});
  });
  mainWindow.webContents.on('will-attach-webview', event => event.preventDefault());
  // Keep standard Save As dialogs for images, generated text and JSON exports.
  ses.on('will-download', (_event, item, wc) => {
    if (wc !== mainWindow?.webContents) { item.cancel(); return; }
    item.setSaveDialogOptions({ title: 'Save AURIX file' });
  });
  ipcMain.handle('aurix:google-sign-in', async event => {
    if (event.sender !== mainWindow?.webContents || event.senderFrame !== mainWindow.webContents.mainFrame || !isAppURL(event.senderFrame.url)) throw Error('Untrusted caller');
    if (pendingAuth) throw Error('A Google sign-in is already in progress. Complete it in your browser.');
    // Reserve before awaiting server startup, so concurrent requests cannot race.
    pendingAuth = { cancel() {} };
    try {
      pendingAuth = await startAuth(url => shell.openExternal(url));
      return await pendingAuth.result;
    } finally { pendingAuth = null; }
  });
  Menu.setApplicationMenu(Menu.buildFromTemplate([
    { label: 'AURIX', submenu: [
      { label: 'Home', click: () => mainWindow?.loadURL(ORIGIN + '/#home') },
      { type: 'separator' }, { role: 'quit' }
    ] },
    { label: 'Edit', submenu: [{ role: 'undo' }, { role: 'redo' }, { type: 'separator' }, { role: 'cut' }, { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' }] },
    { label: 'View', submenu: [{ role: 'reload' }, { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' }, { role: 'togglefullscreen' }] },
    { label: 'Help', submenu: [
      { label: 'About AURIX', click: () => dialog.showMessageBox(mainWindow, { type: 'info', title: 'AURIX', message: `AURIX ${app.getVersion()}`, detail: 'Windows 10 / 11 (64-bit)\nAI generation and Google sign-in require internet access. Video generation is not configured.\nLocal app data is separate from your browser.' }) },
      { label: 'Open website', click: () => shell.openExternal(ORIGIN) }
    ] }
  ]));
  await mainWindow.loadURL(ORIGIN + '/');
}
