# Draft certification notes — replace pending items with verified results

Do not submit this as a claim that tests have passed. The publisher must complete the release gates in STORE-AR.md and attach real results first.

## Product and dependencies

AURIX is a bundled Electron desktop creative workspace, not a generic web browser. Its HTML/CSS/JavaScript, branding and PDF.js are packaged in app.asar. Google/Firebase SDK modules are loaded from Google's CDN as part of the disclosed account service. AI generation requires internet, Google sign-in, Firebase Authentication, the AURIX Cloudflare Worker and its configured providers. No local AI model is included. Video is disabled and there are no payments, paid upgrade or separate analytics system. Two banner placements supplied by MG Ads (Miracle Games) are integrated: banners are requested from ad.mguwp.net only on the signed-in app screen, never on the sign-in screen or public pages. The ad SDK is inert in this website build. MG Ads issues one client credential per application; it is embedded in the package (desktop/ads.cjs inside app.asar), as in MG's own samples, and is never present in the public site, the page, or the renderer bridge — only a boolean capability flag crosses that bridge. It is a client credential for ad requests only, not a server secret, and it authorizes no account, payment or upload operation.

## Reviewer steps

1. Install the Store-provided or appropriately test-signed candidate on an x64 Windows 10 22H2/11 PC, with a default browser and internet.
2. Launch AURIX. Public legal information and content reporting are available without authentication.
3. Select Continue with Google. A page on the developer's existing Firebase domain opens in the default browser. Click the Google button, allow its popup, and complete Google sign-in. A short-lived local callback on 127.0.0.1 returns the Google credential to the application. It is validated by Firebase; no Google password is handled by AURIX.
4. Verify the app enters the dashboard. Generate an image with a simple English prompt, use the writer and code tool, then ask a chat question if the production chat service is configured. Retry later if providers throttle; do not mark an unavailable required service as passing.
5. Select a non-confidential text-based PDF under 5 MB and 20 pages. Ask a question; the app sends only a bounded extracted text excerpt with the question, not PDF bytes.
6. Test a text/code save, local project, favorite, download and optional cloud copy. JSON export excludes image bytes by design.
7. Open Report AI content. Enter a brief explanation, prepare an email and verify the reviewed email/copy path; no data is sent automatically.
8. Verify sign-out and account isolation. Use a disposable account only for destructive account-deletion tests.

## Test access

- There is no payment, invitation code, subscription or region gate implemented by AURIX.
- Google sign-in is required for interactive tools, and external providers may impose regional restrictions.
- Publisher must confirm that the production Firebase OAuth audience allows reviewers to sign in, not merely test users in a restricted project.
- No test credentials are stored in the repository. If Microsoft requests dedicated review access, arrange it privately through Partner Center; never place passwords, OAuth tokens or recovery codes in this file, GitHub or chat.
- The publisher must verify review-time service capacity and answer any access requests in Partner Center. Do not bypass authentication or show mock responses for reviewers.

## Restricted capability justification: runFullTrust

This is a standard-user Electron Win32 desktop application. Full trust is needed to run Electron/Chromium processes, access its own writable per-user app storage, open user-selected PDFs through standard file selection, save user-requested downloads, copy text on user action and run a temporary loopback HTTP listener for system-browser Google authentication. It does not require elevation, install services/drivers, modify system settings, start at login, or request microphone, camera, location or broadFileSystemAccess. Renderer Node integration is disabled, context isolation and sandbox are enabled, navigation is restricted and generated HTML previews are sandboxed. A restricted capability approval decision remains with Microsoft.

## Live generative AI declaration

This product creates images, writing, code and chat responses dynamically from user prompts. Mark live generative AI in the current Partner Center submission flow and disclose it in the listing. Model output is untrusted and must be reviewed. The publisher must verify applicable Store content policies and provider safety controls using real test results; a report button is not a guarantee of compliant generation or a substitute for moderation.

The in-app report control opens a user-reviewed email draft or allows copying to the support inbox. The publisher must verify delivery, monitor the inbox, investigate reports, and take appropriate action with providers or disable an unsafe feature. See REPORT-OPERATIONS.md. Do not claim an automated review queue or 24/7 moderation exists.

## Updates and data

There is no self-updater. Microsoft Store updates the MSIX channel. The separate NSIS/portable builds are not the Store submission. User data must remain in writable per-user storage, never the read-only install directory. Uninstall/reset may remove local data; optional cloud copies and provider logs are separate. The public Windows privacy notice is available without login after deployment.

## Required evidence before replacing this draft

- Candidate file name, SHA-256, real Partner Center identity and package version.
- Windows 10/11 installation, sign-in, generation, PDF, account isolation, logout, update and uninstall test results.
- Windows App Certification Kit report and any resolved failures.
- Real Windows screenshots of the same version, with personal data redacted.
- Confirmation of live auth bridge/privacy page, monitored inbox, provider rights and content-safety testing.
