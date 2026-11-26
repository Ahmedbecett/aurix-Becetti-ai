# Real Windows screenshots required before submission

The current media kit is `release/media/`, built by `scripts/make-listing-media.py`:

| File | Kind | Use |
|---|---|---|
| `aurix-hero-1920x1080.png` | Generated brand artwork | Website / repository hero image |
| `aurix-hero-1080x1080.png` | Generated brand artwork | Square social/listing slot |
| `aurix-walkthrough.mp4` + `.vtt` | Generated brand artwork, 28 s, silent | Feature walkthrough video |

None of these is a screenshot: they are brand artwork built from the project logo and the verified
feature list, with no simulated app interface. They may be used as illustration, but **not** in a
Store slot that requires a product screenshot. Do not upload HTML design mockups, empty
test-account previews or AI-generated illustrations as screenshots of a working Windows product.

An earlier nine-image artwork set and four reference-only web captures are no longer produced by
any script in this repository; only `release/media/` is generated and committed now. The Windows
screenshot gate is still open — see `scripts/capture-windows-store-screenshots.ps1` for the
owner-assisted capture procedure.

Capture the final MSIX candidate actually running on Windows (a properly signed local test copy or a Store flight). Recommended captures at 1920x1080, without added fake data or unsupported claims:

1. Dashboard with the current layout and real local activity (zero activity is fine; invented totals are not).
2. A real successful image generation, with its square output and honest provider labels.
3. A real writer/code result; never show credentials in a prompt.
4. Chat with a non-confidential text PDF, only if production chat is actually functional.
5. Projects/history or the content-report dialog.

Use a disposable account, remove personal emails/names and private prompts before capture, and ensure redaction does not misrepresent functionality. The Store description, package and screenshots must describe the same version. Do not include the unavailable video tool as an enabled feature.

The owner must check the current Partner Center screenshot dimensions, number, file-size and locale requirements when uploading. `artwork/ProductIcon300.png` is listing icon artwork only, not a substitute for screenshots. `store/assets/` contains manifest logos only.
