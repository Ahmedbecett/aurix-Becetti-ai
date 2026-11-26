# AURIX AI 1.0.2 — reserved display-name correction

The owner supplied the current Partner Center Packages page for product **AURIX AI**. It rejected 1.0.1.0 because Package/Properties/DisplayName was the unreserved name **AURIX**.

This candidate changes both Package/Properties/DisplayName and Application/uap:VisualElements/@DisplayName to **AURIX AI**. Package identity, publisher, PFN, SID and application ID remain unchanged. A regression guard now rejects an identity override that replaces the confirmed reserved display name with AURIX again.

The package version is 1.0.2.0. This is a manifest/display-name correction, not a claim that the application has passed Store certification.

Before these assets are published, the actual emitted file must pass:
- Windows SDK MakeAppx pack validation, without /nv.
- ZIP central-directory/CRC checks and required root MSIX footprints.
- Independent SHA-256 checks for every block in AppxBlockMap.xml.
- Packaged identity and byte/file-list comparison with staging.
- Windows SDK MakeAppx unpack round-trip, without /nv.

The release metadata below records the display names read from inside the emitted MSIX, its exact bytes and SHA-256. Download the .msix directly, delete the rejected 1.0.1.0 entry in Partner Center, and upload the new file. Do not upload a ZIP or rename a different file.

This is an unsigned Microsoft Store submission candidate, not a public sideload installer. Store-side validation, WACK, interactive Windows tests, deployed Google auth/privacy pages and content-safety review still require verification. No Microsoft certification or Store publication is claimed.
