# AURIX — AI Creative Studio for Blogger

> **الموقع الحي الوحيد:** https://aurix-ea09b.web.app (Firebase Hosting).
> هذا المستودع هو مصدر المشروع ونسخته الاحتياطية. لا توجد نسخة Vercel بعد اليوم.


**Preview:** `release/preview/index.html` · **Installable Blogger theme:** `release/aurix-blogger.xml`

## Windows 10 / 11 desktop (x64)

Electron desktop packaging now includes the current dashboard, images, code, writing, chat/PDF, projects and settings from the same `src/` files. Run `npm ci`, then `npm run desktop` to develop or `npm run dist:win -- --publish never` on Windows to build an NSIS installer and a portable EXE. A Windows GitHub Actions workflow is in `.github/workflows/windows.yml`.

**Build status:** real NSIS, Portable and MSIX candidates were built successfully on a GitHub-hosted Windows runner (run `45508613913`, source commit `9f69e21`). [Download candidates and read remaining gates](WINDOWS-DOWNLOADS-AR.md). Interactive Windows end-to-end testing and WACK have not been completed. Google login opens the system browser and requires deploying the included desktop auth bridge to the existing Firebase site first. AI services still require internet; unavailable features (including video) are not unlocked by packaging. See [Windows setup, prerequisites and acceptance checklist (Arabic)](WINDOWS-AR.md).

The prior dashboard-only release improvements have been reconciled into `src/` so the standard build preserves them.

### Microsoft Store (MSIX candidate)

The Store channel is separate from NSIS/Portable. The owner-supplied public identity is tracked in `store/identity.store.json` (`Ahmedbecetti.AURIXAI`, publisher `Ahmedbecetti`); PFN/SID and Store ID `9NLM756D1CZR` are in `store/product.json` and cross-checked. The existing display name AURIX remains provisional until confirmed against the reservation. An optional ignored `store/identity.json` can override the tracked profile. On Windows with the SDK installed, run `npm ci`, `npm run store:validate`, then `npm run dist:store`. The build stages the x64 runtime and uses MakeAppx with validation enabled; `.github/workflows/microsoft-store.yml` provides a manual Windows build with the same public inputs.

Package logos, listing drafts (English/Arabic/French), review notes and reporting procedures are in `store/`. A user-reviewed AI content report/email/copy control and a public Windows privacy page are included in the web build. Deploy the auth bridge and `/pages/windows-privacy.html` before distributing the candidate.

**Not submitted or certified:** the Windows MSIX candidate build has succeeded. The exact reserved display name, interactive Windows 10/11 tests, WACK, production service/safety checks and real screenshots are still required. An unsigned candidate is for Store submission after verification, not public sideload distribution. See [Microsoft Store preparation and release gates (Arabic)](STORE-AR.md).

A standalone, no-server, responsive guest-mode app for the owner's `skullaistudio.blogspot.com` site. Built from the project owner's reference artwork (cropped icon in `src/brand-icon.webp`). Frontend source: `src/app.html`, `src/styles.css`, `src/app.js`; rebuild with `python build.py`. The application is **published on Firebase Hosting staging** at https://aurix-ea09b.web.app with noindex. It has **not been published to the owner's Blogger account**; Blogger admin access is required to install the theme and create pages. See `DEPLOYED-AR.md`.

## Current feature matrix (tested 2026-10-24)

| Feature | Implementation | Real availability |
|---|---|---|
| Images | Pollinations Classic public image endpoint, one model; As written default or optional style modifier, 1:1 / 16:9 / 9:16, fast/detail size, explicit Arabic-to-English translation, safe filtering, cancel, download, local image-link history | Image prompts in Arabic can produce unrelated results; English translation improved subject relevance in a live test but still missed an exact object count. Free model is best effort and watermarked |
| Code | Pollinations Classic text endpoint via JSON POST; code generation/explanation/repair, copy, download and local save; optional sandboxed HTML preview | Test POST returned real text |
| Writing | Same text endpoint, 8 actions, copy/download/local save | Test POST returned real text |
| Video | Explicitly disabled | No provider configured |
| Accounts | Guest mode; folders, favorites, JSON export, local deletion | Firebase project aurix-ea09b connected; Google OAuth reaches Google; Firestore rules deployed and owner isolation tested; actual human Google sign-in not yet completed; email sign-in not built |
| Ad slots | Hidden | No ads until network review/approval |
| Internationalization | English default, French/Arabic navigation; Arabic RTL shell | **Main tool copy is currently English. Full French/Arabic localization is unfinished** |
| Legal pages | About, Contact, Privacy, Terms in `release/*-page.html` | Contact email added from owner’s instruction; owner should verify the inbox |

## Optional original tutorial pages

Three original, substantial tutorial bodies are included in `release/image-guide-page.html`, `release/code-guide-page.html`, and `release/writer-guide-page.html`. Create them as Blogger pages or posts in HTML view after reviewing/editing them for the owner’s voice. They are **not** automatically published, linked, indexed or proof of AdSense eligibility. Add accurate page titles and individual search descriptions in Blogger.

## Free-tier and usage constraints

Pollinations' [Classic API docs](https://github.com/pollinations/pollinations/blob/master/APIDOCS.md) as of 2026-10-24: **images one at a time and at least 45 seconds apart per IP; text one at a time and at least 30 seconds apart per IP**. App applies local cooldowns for each type. It cannot securely enforce a global limit or block a user clearing local data. Provider may independently respond 402, refuse prompts, watermark images or stop service. There are no displayed invented credit balances. Image limit is at most 768×768 in area (1024×576 and 576×1024 have that same area). Images use `safe=true`. Browser-side requests expose visitor IP and prompts to provider; image URLs can be shared, and cached URLs return the same result to anyone with the URL. Do not submit sensitive data. Text requests are POST rather than URL paths.

**Commercial-use caveat:** Pollinations [Terms](https://pollinations.ai/terms) do not grant blanket commercial rights for every model and output. **Do not assume monetization or commercial reuse is authorized** without checking current model/endpoint conditions with the provider. Anonymous Classic endpoints are best-effort, not a sustainable SLA. An app-specific key must never be embedded in Blogger HTML; authenticated/provider upgrades require a server-side proxy or a provider-supported client authorization flow. A zero-dollar, dependable production API cannot be guaranteed. Blogger hosting itself is free; ads/AdSense are neither enabled nor guaranteed approval.

See [`DEPLOYED-AR.md`](DEPLOYED-AR.md) for live status and remaining owner actions; [`NEXT-STEPS-AR.md`](NEXT-STEPS-AR.md) is an earlier setup plan and may describe steps already completed.

## Install on Blogger (site owner only)

1. Go to [Blogger](https://www.blogger.com) and select `skullaistudio.blogspot.com`. Back up the existing theme: **Theme → ▼ → Backup**.
2. **Theme → ▼ → Restore → Upload** `release/aurix-blogger.xml` (UI wording varies by locale). **Do not paste API keys** into the theme.
3. Under **Pages**, create pages named **About**, **Contact**, **Privacy Policy**, **Terms of Service**. Open HTML mode and paste each matching `release/*-page.html` body. Set URLs to `about`, `contact`, `privacy`, `terms` as shown in the theme links; Blogger may assign different URLs, so confirm the four links after publishing and update theme links if needed.
4. Verify that the Contact page’s email address works before the public launch. Review/adjust policy for actual practices and local law. **Do not claim it is published until it is**.
5. Test all studio features on your Blogger domain and on a phone. Send a screenshot of Blogger theme upload results if validation fails; Blogger's editor can enforce extra constraints not testable offline.
6. Add the blog to Google Search Console (URL-prefix property). Submit Blogger's own `/sitemap.xml`; Blogger's `robots.txt` is managed by Blogger. There is no separate XML sitemap file to upload. Verify indexing; it is not automatic or guaranteed.
7. Only after meaningful original content, policy/contact verification, and network approval, enable compliant ads through Blogger Earnings or your approved network. No ads appear in this theme by default. Do not assume `blogspot.com` or any platform guarantees AdSense approval.

### What cannot be finished on Blogger alone

A Blogger theme has no safe server-side secret store and no robust server-side rate limiting. An optional Firebase Auth + Firestore integration for cross-device accounts and private cloud projects is prepared with per-user rules, but is not active or live-tested without owner configuration. Per-user Firestore rules are not a server-side generation or abuse quota; add App Check and monitor quotas before opening registration widely. Provider keys and paid/limited API quotas still need a secure backend. Video has no sustainable verified free provider. Current app is a functional guest-mode first phase, **not the complete five-phase production platform**.

## 2026-10-24 quality correction

See [`QUALITY-FIX-AR.md`](QUALITY-FIX-AR.md) for the reproduced Arabic-prompt failure, rate-limit JPEG card, bounded wait/cancel UX, tests, and the **unpublished-update** notice. Deployment ZIP: `aurix-quality-update.zip`; guide: [`DEPLOY-UPDATE-AR.md`](DEPLOY-UPDATE-AR.md). The live Firebase site remains on the prior version until the owner deploys the update using their Firebase login.

## Quality checks

`npm ci && npm test` rebuilds the web output and runs UI checks with repository-local `happy-dom` / `fake-indexeddb`, backend checks, and desktop authentication/policy tests. Node.js 22+ and Python 3.10+ are required. The historical XML validation used `lxml`; it is not required by this npm test command. Real external GET image and POST text requests were made successfully on 2026-10-24. Live Playwright checks on the Firebase staging site passed desktop/mobile, OAuth redirect to Google, actual image/text generation and static legal page; real Google user login and Blogger theme installation remain pending.
