'use strict';
// Captures public bundled HTML only. This is NOT a Windows/MSIX capture.
// Setup: npm install --prefix .cache/store-media-tools playwright-core @sparticuz/chromium
const { chromium: playwright } = require('../.cache/store-media-tools/node_modules/playwright-core');
// Chromium is ESM-only; load its entry point below.
const fs = require('node:fs/promises');
const path = require('node:path');
(async () => {
  const { default: chromium } = await import('../.cache/store-media-tools/node_modules/@sparticuz/chromium/build/index.js');
  const out = path.resolve('store/submission/media/review-ui-not-windows');
  await fs.mkdir(out, { recursive: true });
  const browser = await playwright.launch({ executablePath: await chromium.executablePath(), args: chromium.args, headless: true });
  const context = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1, locale: 'en-US' });
  // External requests cannot work in the capture sandbox. Do not stub account,
  // credentials, provider responses, results, counts, or sign-in success.
  await context.route('**/*', route => {
    const url = new URL(route.request().url());
    return url.hostname === '127.0.0.1' ? route.continue() : route.abort();
  });
  const page = await context.newPage();
  const base = process.env.AURIX_CAPTURE_URL || 'http://127.0.0.1:4173';
  const records = [];
  for (const [name, route, language] of [
    ['01-welcome-en', '/#login', 'en'],
    ['02-welcome-fr', '/#login', 'fr'],
    ['03-welcome-ar', '/#login', 'ar'],
    ['04-windows-privacy-en', '/pages/windows-privacy.html', 'en']
  ]) {
    await page.goto(base + '/', { waitUntil: 'domcontentloaded' });
    await page.evaluate(language => localStorage.setItem('aurix_v1_lang', language), language);
    await page.goto(base + route, { waitUntil: 'domcontentloaded' });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(out, name + '.png'), animations: 'disabled' });
    records.push({ file: name + '.png', route, language, width: 1920, height: 1080, authenticated: false, runtime: 'headless Chromium, bundled web UI; not Windows/MSIX', externalNetwork: 'blocked; sign-in unavailable as actually rendered' });
  }
  await fs.writeFile(path.join(out, 'provenance.json'), JSON.stringify(records, null, 2) + '\n');
  await browser.close();
})().catch(error => { console.error(error); process.exitCode = 1; });
