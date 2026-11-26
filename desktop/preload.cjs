'use strict';
const { contextBridge, ipcRenderer } = require('electron');
// The packaged app page is the only origin allowed to call this bridge.
const APP_ORIGIN = 'https://aurix-ea09b.web.app';
if (process.isMainFrame && location.origin === APP_ORIGIN) {
  const ads = Object.freeze({
    // Read-only capability flags. The App ID / Secret Key stay in the main
    // process and are only ever written into the native MG Ads runtime.
    enabled: true,
    credentialsInstalled: () => ipcRenderer.sendSync('aurix:ads-credentials'),
    listSlots: () => ipcRenderer.sendSync('aurix:ads-slots')
  });
  contextBridge.exposeInMainWorld('AurixDesktop', Object.freeze({
    signIn: () => ipcRenderer.invoke('aurix:google-sign-in'),
    ads
  }));
}
