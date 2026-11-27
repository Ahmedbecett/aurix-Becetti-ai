# AURIX AI 1.0.3 — unique package full name

**Why this version exists.** Partner Center rejected the ads build with:

> You have provided two packages with the full name Ahmedbecetti.AURIXAI_1.0.2.0_X64_ which have different contents.

1.0.2.0 is already published for `Ahmedbecetti.AURIXAI`, so a different payload cannot be uploaded
under that full name. A Microsoft Store package full name is `<IdentityName>_<Version>_<Arch>`: the
version is the only part that changes the identity, therefore every new payload needs a higher
version. This build is **1.0.3.0**.

Nothing else changed: the identity, publisher, PFN `Ahmedbecetti.AURIXAI_y0zvy3a8v70hm`, package SID,
application ID and the reserved display name **AURIX AI** are untouched.

**History**

| Version | Status | Contents |
|---|---|---|
| 1.0.1.0 | rejected (unreserved display name) | — |
| 1.0.2.0 | published in the Store | pre-ads build |
| 1.0.3.0 | this candidate | same app + MG Ads banners on signed-in screens |

**Guard.** `scripts/store.cjs` now refuses to stage or validate a version whose full name is listed in
`store/product.json → publishedFullNames`, and refuses any version that is not higher than
`liveVersion`. The failure message names the next version to use. `npm test` covers both cases, and
the release steps in `.github/workflows/windows.yml` derive their tags from `package.json`, so a
reused version can no longer be published as a second download with different bytes.

**Before upload, the emitted file must still pass:** MakeAppx pack validation without `/nv`, ZIP
CRC/central-directory checks, independent SHA-256 verification of every block in `AppxBlockMap.xml`,
byte/file-list comparison against staging, and the MakeAppx unpack round-trip. `scripts/build-store.ps1`
runs all of these and writes `dist/store/msix-integrity.json`.

**Submission steps**

1. In Partner Center → Packages, remove the failed `1.0.2.0` upload **only if it is not the published
   package**; never delete the currently published flight entry.
2. Upload `Ahmedbecetti.AURIXAI_1.0.3.0_x64.msix` — unsigned by the CI build, so sign or let the Store
   do it as usual for your account.
3. Keep the listing text in [`LISTING-EN.md`](../../LISTING-EN.md) aligned with 1.0.3.0; the current
   Store page still describes 1.0.2.0.

This is an unsigned submission candidate, not a public sideload installer. Store-side validation,
WACK, interactive Windows 10/11 tests and real screenshots still require verification, and no
certification is claimed here.
