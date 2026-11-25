# Real Windows screenshots required before submission

The media kit in `media/` now contains nine listing-artwork PNGs, a 30-second brand trailer, and four **reference-only bundled web UI captures** in `media/review-ui-not-windows/`. Those reference captures use headless Chromium with external networking blocked, without Google sign-in; they are **not Windows/MSIX product screenshots** and must not be used to imply successful authentication or AI generation. The final Windows screenshot gate remains open. See `media/UPLOAD-GUIDE-AR.md` and `scripts/capture-windows-store-screenshots.ps1` for the owner-assisted capture procedure. Do not upload HTML design mockups, empty test-account previews or AI-generated illustrations as screenshots of a working Windows product.

Capture the final MSIX candidate actually running on Windows (a properly signed local test copy or a Store flight). Recommended captures at 1920x1080, without added fake data or unsupported claims:

1. Dashboard with the current layout and real local activity (zero activity is fine; invented totals are not).
2. A real successful image generation, with its square output and honest provider labels.
3. A real writer/code result; never show credentials in a prompt.
4. Chat with a non-confidential text PDF, only if production chat is actually functional.
5. Projects/history or the content-report dialog.

Use a disposable account, remove personal emails/names and private prompts before capture, and ensure redaction does not misrepresent functionality. The Store description, package and screenshots must describe the same version. Do not include the unavailable video tool as an enabled feature.

The owner must check the current Partner Center screenshot dimensions, number, file-size and locale requirements when uploading. `artwork/ProductIcon300.png` is listing icon artwork only, not a substitute for screenshots. `store/assets/` contains manifest logos only.
