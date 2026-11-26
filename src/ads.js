/* AURIX — MG Ads (Miracle Games) banners, Windows desktop build only.
   * AdUnitIds are the public placement identifiers supplied by the owner and are
     the same values MG Ads publishes in its SDK documentation.
   * The App ID + Secret Key that authorize the SDK are NOT here: they stay in the
     Electron main process (desktop/ads.cjs, environment variables) so they are
     never shipped to renderer code, never written to Git and never logged.
   * In a normal browser this file does nothing: the mount gate requires the
     desktop preload bridge (window.AurixDesktop.ads.enabled), so the Firebase
     website neither loads the SDK nor renders an ad region. */
(function () {
  'use strict';
  const SLOTS = Object.freeze([
    Object.freeze({ key: 'banner-1', unitId: 'f97e5aa93a22438f8ef1d3e549d7a245' }),
    Object.freeze({ key: 'banner-2', unitId: 'fc1e2f0faa8343d889687c5fc9ba19a3' })
  ]);
  const SDK_URL = 'https://ad.mguwp.net/js/h5adsdk.js';
  const SDK_TIMEOUT_MS = 8000;
  const MIN_APP_WIDTH = 800;

  const copy = {
    en: {
      region: 'Sponsored messages', tag: 'Advertisement',
      waiting: 'Reserving banner slot…',
      connecting: 'Connecting to MG Ads…',
      credentials: 'This build has no MG Ads credentials installed, so no banner can be requested. The slot stays reserved.',
      requested: 'Banner requested from MG Ads.',
      noMaterial: 'MG Ads reported no banner material for this slot right now.',
      placementOff: 'This placement is switched off in the MG Ads dashboard.',
      closed: 'Banner closed.',
      failed: 'The banner could not be loaded.',
      sdkMissing: 'The MG Ads SDK did not load in this build.',
      clicked: 'Banner opened.',
      narrow: 'Banner hidden because the window is too narrow.'
    },
    fr: {
      region: 'Messages sponsorisés', tag: 'Publicité',
      waiting: 'Réservation de l’emplacement…',
      connecting: 'Connexion à MG Ads…',
      credentials: 'Cette version n’a aucune information d’accès MG Ads, donc aucune bannière ne peut être demandée. L’emplacement reste réservé.',
      requested: 'Bannière demandée à MG Ads.',
      noMaterial: 'MG Ads ne propose aucun visuel de bannière pour cet emplacement pour le moment.',
      placementOff: 'Cet emplacement est désactivé dans le tableau de bord MG Ads.',
      closed: 'Bannière fermée.',
      failed: 'La bannière n’a pas pu être chargée.',
      sdkMissing: 'Le SDK MG Ads ne s’est pas chargé dans cette version.',
      clicked: 'Bannière ouverte.',
      narrow: 'Bannière masquée : fenêtre trop étroite.'
    },
    ar: {
      region: 'رسائل دعائية', tag: 'إعلان',
      waiting: 'جارٍ حجز مساحة البانر…',
      connecting: 'جارٍ الاتصال بـMG Ads…',
      credentials: 'هذه النسخة لا تحتوي بيانات اعتماد MG Ads، لذلك لا يمكن طلب بانر. تبقى المساحة محجوزة.',
      requested: 'تم طلب البانر من MG Ads.',
      noMaterial: 'أبلغت MG Ads بعدم توفر مادة إعلانية لهذه المساحة الآن.',
      placementOff: 'هذه المساحة الإعلانية موقوفة من لوحة MG Ads.',
      closed: 'أُغلق البانر.',
      failed: 'تعذّر تحميل البانر.',
      sdkMissing: 'لم يُحمّل MG Ads SDK في هذه النسخة.',
      clicked: 'تم فتح البانر.',
      narrow: 'أُخفي البانر لأن عرض النافذة ضيّق.'
    }
  };
  const state = { mounted: false, region: null, sdk: 'idle', shown: new Set(), status: new Map() };
  const lang = () => String(document.documentElement.lang || 'en').slice(0, 2);
  const t = key => (copy[lang()] || copy.en)[key] || copy.en[key];
  const bridge = () => {
    const ads = window.AurixDesktop && window.AurixDesktop.ads;
    return ads && ads.enabled === true ? ads : null;
  };

  const CSS = [
    '.aurix-ads{margin:26px auto 0;padding:0 0 10px;max-width:1180px;display:flex;flex-wrap:wrap;gap:14px;justify-content:center}',
    '.aurix-ads[hidden]{display:none!important}',
    '.ad-slot{background:var(--surface,#141a2e);border:1px dashed var(--line2,#2d3757);border-radius:var(--radius,14px);padding:10px 12px 12px;min-width:0}',
    '.ad-slot-head{display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted2,#6b7492)}',
    '.ad-slot-head .ad-tag{border:1px solid var(--line2,#2d3757);border-radius:999px;padding:1px 8px;color:var(--muted,#9aa3bd)}',
    '.ad-frame{width:728px;max-width:100%;min-height:90px;display:flex;align-items:center;justify-content:center;text-align:center;background:var(--bg2,#0d1226);border:1px solid var(--line,#232c48);border-radius:10px;padding:10px 14px;color:var(--muted2,#6b7492);font-size:13px;line-height:1.5}',
    '.ad-frame[data-state="ready"]{border-style:solid}',
    '.ad-frame[data-state="error"]{border-color:var(--warn,#fbbf24);color:var(--warn,#fbbf24)}',
    '@media (max-width:900px){.ad-slot{flex:1 1 100%}}'
  ].join('');

  function ensureStyle() {
    if (document.getElementById('aurix-ads-style')) return;
    const style = document.createElement('style');
    style.id = 'aurix-ads-style';
    style.textContent = CSS;
    document.head.append(style);
  }

  // Messages are stored by key, so switching EN/FR/AR re-renders them locally.
  function setStatus(key, msgKey, kind) {
    state.status.set(key, { msgKey, kind: kind || 'waiting' });
    paint(key);
  }
  function paint(key) {
    const frame = document.getElementById('ad-frame-' + key);
    const slot = state.status.get(key);
    if (!frame || !slot) return;
    frame.dataset.state = slot.kind;
    frame.textContent = t(slot.msgKey);
  }

  function buildRegion() {
    const region = document.createElement('section');
    region.id = 'aurix-ads';
    region.className = 'aurix-ads';
    region.hidden = true;
    region.setAttribute('aria-label', t('region'));
    for (const slot of SLOTS) {
      const box = document.createElement('div');
      box.className = 'ad-slot';
      box.dataset.adSlot = slot.key;
      box.dataset.adUnit = slot.unitId;
      const head = document.createElement('div');
      head.className = 'ad-slot-head';
      const tag = document.createElement('span');
      tag.className = 'ad-tag';
      tag.textContent = t('tag');
      const name = document.createElement('span');
      name.textContent = slot.key === 'banner-1' ? 'Banner 1' : 'Banner 2';
      head.append(tag, name);
      const frame = document.createElement('div');
      frame.className = 'ad-frame';
      frame.id = 'ad-frame-' + slot.key;
      frame.dataset.state = 'waiting';
      frame.setAttribute('role', 'status');
      frame.setAttribute('aria-live', 'polite');
      frame.textContent = t('waiting');
      state.status.set(slot.key, { msgKey: 'waiting', kind: 'waiting' });
      box.append(head, frame);
      region.append(box);
    }
    const wrap = document.querySelector('.aurix-wrap');
    const footer = wrap && wrap.querySelector('.aurix-foot');
    if (wrap && footer) wrap.insertBefore(region, footer);
    else document.body.append(region);
    // The provider calls these globals after it renders or the user interacts.
    window.AdCloseEvent = function (param) {
      let detail = {};
      try { detail = JSON.parse(param) || {}; } catch { detail = {}; }
      const key = String(detail.unitId || '');
      const slot = SLOTS.find(s => s.unitId.toLowerCase() === key.toLowerCase());
      if (!slot) return;
      if (detail.advertStatus === 2) return setStatus(slot.key, 'placementOff', 'error');
      if (detail.advertStatus === 3) return setStatus(slot.key, 'noMaterial', 'error');
      setStatus(slot.key, 'closed', 'waiting');
    };
    window.AdClickEvent = function (param) {
      let detail = {};
      try { detail = JSON.parse(param) || {}; } catch { detail = {}; }
      const slot = SLOTS.find(s => s.unitId.toLowerCase() === String(detail.unitId || '').toLowerCase());
      if (slot) setStatus(slot.key, 'clicked', 'ready');
    };
    return region;
  }

  function sdkPresent() {
    // h5adsdk.js delivers ShowAd and needs the packaged WebView2 host object.
    return typeof window.ShowAd === 'function' &&
      !!(window.chrome && window.chrome.webview && window.chrome.webview.hostObjects);
  }

  function loadSdk(done) {
    if (state.sdk === 'ready') return done(true);
    if (state.sdk === 'loading') return;
    state.sdk = 'loading';
    const script = document.createElement('script');
    script.src = SDK_URL;
    script.async = true;
    script.onerror = () => { state.sdk = 'error'; done(false); };
    script.onload = () => { state.sdk = sdkPresent() ? 'ready' : 'error'; done(state.sdk === 'ready'); };
    document.head.append(script);
    setTimeout(() => {
      if (state.sdk === 'loading') { state.sdk = sdkPresent() ? 'ready' : 'error'; done(state.sdk === 'ready'); }
    }, SDK_TIMEOUT_MS);
  }

  function show(slot) {
    if (state.shown.has(slot.key)) return;
    state.shown.add(slot.key);
    setStatus(slot.key, 'requested', 'ready');
    try {
      window.ShowAd(JSON.stringify({ unitId: slot.unitId, adType: 3, media: 'image' }));
    } catch {
      state.shown.delete(slot.key);
      setStatus(slot.key, 'failed', 'error');
    }
  }

  function credentialsNote(bridgeApi) {
    // Only a boolean crosses the IPC boundary; the secret never reaches the page.
    if (typeof bridgeApi.credentialsInstalled !== 'function') return null;
    return Promise.resolve(bridgeApi.credentialsInstalled())
      .then(result => (result && result.installed === true ? null : 'credentials'))
      .catch(() => null);
  }

  function start(region) {
    const each = [...region.querySelectorAll('.ad-slot')];
    each.forEach(box => setStatus(box.dataset.adSlot, 'connecting', 'waiting'));
    loadSdk(ok => {
      if (!ok) {
        each.forEach(box => setStatus(box.dataset.adSlot, 'sdkMissing', 'error'));
        return;
      }
      credentialsNote(bridge()).then(note => {
        if (note) {
          each.forEach(box => setStatus(box.dataset.adSlot, note, 'error'));
          return;
        }
        SLOTS.forEach(show);
      });
    });
  }

  function retranslate() {
    const region = state.region;
    if (!region) return;
    region.setAttribute('aria-label', t('region'));
    region.querySelectorAll('.ad-slot').forEach(box => {
      const tag = box.querySelector('.ad-tag');
      if (tag) tag.textContent = t('tag');
      paint(box.dataset.adSlot);
    });
  }

  function sync() {
    const region = state.region;
    if (!region) return;
    retranslate();
    const signedOut = document.body.classList.contains('auth-mode');
    const tooNarrow = window.innerWidth < MIN_APP_WIDTH;
    const visible = !!bridge() && !signedOut && !tooNarrow;
    // A sign-in screen and a too-narrow window keep the region out of the layout
    // entirely, so no ad request is made and no empty box is left behind.
    if (visible === region.hidden) region.hidden = !visible;
    if (!visible) return;
    if (!region.dataset.started) {
      region.dataset.started = '1';
      start(region);
    }
  }

  function mount() {
    if (state.mounted) return state.region;
    if (!bridge()) return null; // normal browser: inert, no DOM, no network
    state.mounted = true;
    ensureStyle();
    state.region = buildRegion();
    window.addEventListener('hashchange', sync);
    window.addEventListener('resize', sync);
    if (window.MutationObserver) {
      new MutationObserver(sync).observe(document.body, { attributes: true, attributeFilter: ['class'] });
      new MutationObserver(retranslate).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
    }
    sync();
    return state.region;
  }

  // Minimal, dependency-free status surface for tests and for support reports.
  window.AurixAds = Object.freeze({
    slots: SLOTS,
    mount,
    sync,
    state: () => ({
      mounted: state.mounted,
      sdk: state.sdk,
      visible: !!(state.region && !state.region.hidden),
      shown: [...state.shown],
      status: Object.fromEntries([...state.status].map(([k, v]) => [k, v.kind + ':' + v.msgKey]))
    })
  });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();
})();
