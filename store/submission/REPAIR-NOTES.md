# AURIX 1.0.1 — Store package validation candidate

Replaces the 1.0.0.0 candidate reported as rejected by Partner Center with HRESULT 0x8051100F. The exact submitted bytes were not available to us, so this is not a claim that the reported upload's root cause has been conclusively reproduced.

The new package must pass all of the following before these assets are published:
- Windows SDK MakeAppx pack validation, without /nv.
- ZIP central-directory/CRC checks, required root MSIX footprints and manifest identity checks.
- Independent SHA-256 verification of every block in AppxBlockMap.xml.
- Byte hashes/file-list comparison against the staged payload.
- Windows SDK MakeAppx unpack round-trip, without /nv.

Download the .msix asset directly. Do not rename an artifact ZIP to .msix and do not upload an incomplete download. Match the exact byte count and SHA-256 below before uploading to Partner Center. Upload the .msix, not the checksum, report or ZIP.

This is an unsigned package for the Microsoft Store submission path, NOT a public sideload installer. Store acceptance, WACK, interactive Windows tests, deployed Google auth/privacy pages, content safety and the reserved display name still require verification. No Microsoft certification or publication is claimed.
