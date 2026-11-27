# AURIX AI 1.0.4 — the canonical package for submission

**Read this before uploading anything.** Three package full names now exist for this product, and
Partner Center accepts exactly one of them:

| Version | Full name | State | Upload? |
|---|---|---|---|
| 1.0.2.0 | `Ahmedbecetti.AURIXAI_1.0.2.0_x64` | published in the Store | ❌ never again |
| 1.0.3.0 | `Ahmedbecetti.AURIXAI_1.0.3.0_x64` | submitted, failed certification with **error 5001** | ❌ never again |
| **1.0.4.0** | **`Ahmedbecetti.AURIXAI_1.0.4.0_x64`** | **built and published, then frozen (commit 547c288)** | ✅ **this file only** |

Verified artifact: `Ahmedbecetti.AURIXAI_1.0.4.0_x64.msix`, **164,085,025 bytes**,
SHA-256 `c4697223fc668e500911dfe9401ddebc3ea52259531867d89fef0838e99a37b8`,
release <https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/tag/windows-ads-1.0.4.0>.
Any other hash means a different (or damaged) file - do not upload it.

## Why a new version instead of re-uploading 1.0.3.0

A Store package full name is `<IdentityName>_<Version>_<Arch>`. Two packages with the same full name
but different contents are rejected (that was the first rejection). A version that has already been
submitted also stays recorded on the product even when certification fails —
[Microsoft's own answer](https://learn.microsoft.com/en-us/answers/questions/1497272/we-are-experiencing-difficulties-with-uploading-pa)
is that once a submission is in, "you can only upload 1.0.2 or larger number". Re-uploading 1.0.3.0
would therefore either be refused or, worse, repeat the 5001 failure against the same recorded name.

So the fix is not to repair 1.0.3.0's bytes in place. It is to produce **one clean package under a
full name Partner Center has never seen**, and make it impossible for the old links to be confused
with it.

## What guards this in the repository

1. `store/product.json` records `publishedFullNames: [1.0.2.0]` and
   `rejectedFullNames: [1.0.3.0]`. `scripts/store.cjs` refuses both during validation **and**
   staging, and refuses any version that is not higher than `liveVersion`.
2. `scripts/store-preflight.cjs` asks Partner Center's REST API for every package the product holds
   (`/applications/{storeId}/submissions/{n}/packages`) and fails if the current version's full name
   appears — including names that only Partner Center knows about. It runs as a gate at the end of
   `scripts/build-store.ps1`; the result (`partner-center-confirmed` / `local-lists-only`) is written
   into `dist/store/store-build.json` and into the GitHub release notes.
3. The release for 1.0.4.0 names the canonical file at the top of its notes: **UPLOAD THIS FILE ONLY**.
4. `scripts/diagnose-msix.py <file>.msix` audits the file itself (identity, version against the
   published/rejected records, targeting, entry point, x64 PE header, logo sizes, every BlockMap hash)
   before anything is uploaded.

## Submission steps

1. Download `Ahmedbecetti.AURIXAI_1.0.4.0_x64.msix` from the release `windows-ads-1.0.4.0` and confirm
   its SHA-256 against the release notes.
2. `python scripts/diagnose-msix.py .\Ahmedbecetti.AURIXAI_1.0.4.0_x64.msix` → must end with `0 FAIL`.
3. Partner Center → Packages: remove every package that is not 1.0.4.0 (the rejected 1.0.3.0 entry in
   particular). Do not touch the published 1.0.2.0 flight.
4. Upload the one file, complete every required section (including the `runFullTrust` justification),
   and submit.

Identity, Publisher, PFN `Ahmedbecetti.AURIXAI_y0zvy3a8v70hm` and the reserved display name
**AURIX AI** are unchanged in this build.

This is an unsigned submission candidate, not a public sideload installer. WACK, interactive Windows
10/11 testing and real screenshots are still owner-side checks, and no certification is claimed here.
