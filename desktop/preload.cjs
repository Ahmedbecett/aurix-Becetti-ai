'use strict';
const { contextBridge, ipcRenderer } = require('electron');
// Only the top-level bundled page can request this one narrow capability.
if (process.isMainFrame && location.origin === 'https://aurix-ea09b.web.app') {
  contextBridge.exposeInMainWorld('AurixDesktop', Object.freeze({
    signIn: () => ipcRenderer.invoke('aurix:google-sign-in')
  }));
}
