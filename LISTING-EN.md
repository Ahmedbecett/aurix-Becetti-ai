# AURIX AI — English listing copy

This file is the single source of truth for the public English description of AURIX AI,
both for the Microsoft Store product page and for the web page. Every claim below was
checked against the code in this repository. Nothing here describes a feature that the
shipped build does not have.

- **App name:** AURIX AI
- **Microsoft Store:** <https://apps.microsoft.com/detail/9nlm756d1czr?ocid=webpdpshare>
- **Store product ID:** 9NLM756D1CZR
- **Version:** **1.0.4.0** is the canonical build for the next Store submission (MG Ads banners
  included). The published Store build is 1.0.2.0. Windows 10 22H2 or Windows 11, x64.
- **Web app:** <https://aurix-ea09b.web.app>
- **Developer:** Ahmedbecetti (independent project)
- **Support:** <ahmedbecetti41@gmail.com>
- **Privacy policy:** <https://aurix-ea09b.web.app/pages/windows-privacy.html>

---

## Short description (Store field, one sentence)

An AI creative studio for Windows: generate images, write and translate text, write and fix
code, and ask questions about a PDF you own — with your work saved on your own device.

## Full description

AURIX AI brings the four things people usually open four different websites for into one
desktop app for Windows 10 and 11.

**Images.** Describe what you want and the app sends the prompt to Cloudflare Workers AI,
which runs FLUX.1 Schnell. Pick a visual direction and a generation size, cancel a request
that is taking too long, then download the images you want to keep. Images are square; the
model is fast rather than precise, so exact details and counts are not guaranteed.

**Writing.** Draft an article or website copy, shorten a long text, fix grammar, rewrite for
clarity, summarise, or translate between English, French and Arabic. Every result can be
copied, downloaded, or saved to your library.

**Code.** Generate a snippet, ask for an explanation of code you paste in, or ask for a fix.
Results can be copied or downloaded as a file.

**PDF chat.** Attach a text-based PDF (up to 5 MB / 20 pages) and ask questions about it. The
file is read on your device: AURIX extracts the text locally and never uploads or stores the
original PDF. Only the extracted excerpt that you actually ask about is sent to the chat
service. Scanned-image PDFs need OCR, which is not included.

**Library.** Projects, folders, favourites and history are stored on your device, per signed-in
account, so recent work is one click away. You can export your data as JSON or delete it from
Settings at any time. Your work is not turned into demo numbers — the dashboard only ever
shows activity that actually happened.

**Sign-in.** A Google account is required, because every AI request is authorised per user
against the app's own backend. Sign-in opens in your browser and returns to the app.

**Honest limits, stated in the app itself:**

- Video generation is **not** available. The app says so instead of showing a dead button.
- AI generation needs an internet connection. This is not an on-device model.
- Image generation currently produces square images only.
- The app runs on free-tier AI capacity, so a provider can be slow, rate-limited, or briefly
  unavailable. Free capacity is best effort, not a guaranteed service level.
- AI output can be wrong, unsafe, or unsuitable. Review every result before you rely on it.
- English is the primary interface language; French and Arabic controls are partially
  translated.
- There is no paid AURIX subscription and no payment form in this version.
- In the Windows build, two banner placements supplied by MG Ads (Miracle Games) appear on
  signed-in screens only. The website and the sign-in screen show no advertising.
- The app can prepare a content report for you to review and send; reports are never sent
  automatically.

AURIX AI does not claim to be a general-purpose assistant, a trained model of its own, or a
replacement for human review. It is a focused creative tool built around providers that
already exist.

## Feature list (for the Store "features" bullets)

1. AI image generation through Cloudflare Workers AI (FLUX.1 Schnell), with style direction,
   fast/detail sizing, cancel, and download.
2. AI writing with eight actions: article copy, social caption, product description, rewrite,
   summarise, grammar, translate (English/French/Arabic), creative prompt.
3. AI code studio: generate, explain and repair code, with copy and file download.
4. PDF chat: local text extraction from a text-based PDF, with the original file never uploaded.
5. Local library: projects, folders, favourites and history, with JSON export and deletion.
6. Optional cloud copies of supported text and code projects under your own account.
7. Google sign-in gate on every AI action, with per-user rate limiting on the backend.
8. Dark, responsive workspace with English, French and Arabic interface controls and RTL.
9. User-reviewed content reporting built into the app.
10. Native Windows desktop build (x64) from the Microsoft Store, plus the same studio in the browser.

**Not included:** video generation, offline generation, OCR for scanned PDFs, a paid plan, or
any claim of unlimited free use.

## Web page copy

> **AURIX AI — imagine, create, build.**
> An AI creative studio for images, writing, code and PDF questions.
> Available for Windows 10 and 11 on the Microsoft Store, and in the browser at aurix-ea09b.web.app.
> Google sign-in required. Free-tier AI capacity is best effort. Video generation is not available.
> [Get it on the Microsoft Store](https://apps.microsoft.com/detail/9nlm756d1czr?ocid=webpdpshare) ·
> [Open the web app](https://aurix-ea09b.web.app)

## Media

| Asset | File | What it shows |
|---|---|---|
| Hero image (16:9) | [`release/media/aurix-hero-1920x1080.png`](release/media/aurix-hero-1920x1080.png) | Brand, headline, the five capabilities, Store/web links, version |
| Hero image (1:1) | [`release/media/aurix-hero-1080x1080.png`](release/media/aurix-hero-1080x1080.png) | Square crop for social/Store square slots |
| Walkthrough video | [`release/media/aurix-walkthrough.mp4`](release/media/aurix-walkthrough.mp4) | 28 s, 1280×720, silent, six cards: what the app is, images, writing+code, PDF chat and library, how to get it, honest limits |
| Video captions | [`release/media/aurix-walkthrough.vtt`](release/media/aurix-walkthrough.vtt) | English WebVTT track for the video |

Both images and the video are **generated brand artwork**, not screenshots of the running
Windows app. They were built from the project's own logo and the verified feature list by
[`scripts/make-listing-media.py`](scripts/make-listing-media.py); no interface is drawn that
the app does not have, and no screenshot is simulated. Real Windows screenshots still have to
be captured on a Windows machine before they can be uploaded to the Store — see
[`store/submission/SCREENSHOTS.md`](store/submission/SCREENSHOTS.md).

## Direct download (unsigned builds)

Microsoft Store is the recommended way to install. Exactly one file may be uploaded to Partner
Center: **1.0.4.0** — `Ahmedbecetti.AURIXAI_1.0.4.0_x64.msix`, 164,085,022 bytes,
SHA-256 `137535100e289e1c970595aa5323f9bccfd7d26f458cdbc43e6460e09c0b4275`, published on
<https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/tag/windows-ads-1.0.4.0>.
The earlier 1.0.2.0 (published in the Store) and 1.0.3.0 (rejected with error 5001) downloads are
history only — their package full names are taken, so uploading either one fails.
(see [`WINDOWS-DOWNLOADS-AR.md`](WINDOWS-DOWNLOADS-AR.md)). Those builds are unsigned and need
Developer Mode or a trusted certificate; that page is not a substitute for the Store listing.
