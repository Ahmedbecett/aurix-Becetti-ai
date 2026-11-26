# AURIX for Windows — Privacy Policy

Last updated: November 24, 2026. This policy describes the Windows application prepared for distribution as MSIX and as a separate desktop installer. It does not claim that the application has been published or certified by Microsoft.

The application operator is the AURIX project owner, contactable at [ahmedbecetti41@gmail.com](mailto:ahmedbecetti41@gmail.com). Contact the operator with privacy, deletion or safety questions. The publisher must keep this contact current.

## Account information and Google sign-in

A Google account is required for interactive tools. Google and Firebase Authentication process your sign-in, account identifier, email address and available profile information. AURIX uses this identity to isolate projects and authorize AI requests. Sign-in opens your default browser on the existing Firebase-hosted AURIX domain. After your approval, Google credentials are returned to the application using a random temporary loopback address on your own computer, protected by a single-use state value. They are exchanged with Firebase for the application session. The callback listener closes on success, cancellation or timeout. AURIX does not ask for your Google password or access to Gmail, Drive or other account content.

## AI requests and providers

- Cloudflare receives authenticated requests through the AURIX Worker and uses Workers AI / Black Forest Labs FLUX.1 Schnell for images.

- Writing and code prompts are forwarded through the Worker to Pollinations.ai.

- Chat messages and any selected PDF text excerpt are forwarded to Google Gemini when the operator has configured chat. Free-tier provider data may be used for provider improvement under its terms.

- These services receive the text needed for the requested generation. Providers, hosting services and authentication services may process technical information, such as IP addresses and request logs, according to their own policies. AURIX does not control their retention periods.

Do not submit passwords, keys, confidential work, health information or other sensitive personal data. Generated material may be incorrect, unsafe or infringing; review it before use. Video generation is not configured.

## PDF files

PDF.js extracts selectable text on your device. The original PDF file is not uploaded by this feature. Only the extracted text excerpt included with your question is sent to the chat service. Scanned PDFs without selectable text need OCR, which is not provided. The current limits are 5 MB and 20 pages, with at most 12,000 characters included as document context.

## Local storage and optional cloud projects

The application stores your language preference, prompts, recent chat messages, history, generated text, favorites and folders locally using Chromium storage. New image bytes are stored in IndexedDB under the signed-in account. Google/Firebase session state is retained locally so that you can remain signed in. This desktop profile is separate from your usual web browser profile. Older image entries may contain third-party image URLs.

Text and code projects that you explicitly save to cloud are stored in Firestore under your account. New image bytes are not automatically synced to Firestore. There is no automatic cross-device sync of all local data. JSON export does not include stored image bytes. Download important images separately.

Unpackaged desktop editions ordinarily use the Windows app-data location. MSIX editions may have Windows-managed, redirected per-package storage; uninstalling or resetting the Store app can remove local data. Do not rely on uninstall or reset to delete cloud/provider copies.

## Content reports and support

The in-app “Report AI content” control prepares an email draft or copies a report. It includes the tool area, date and only the explanation you type. Prompts, results, PDF contents and account identifiers are not attached automatically. No report is transmitted until you send the email yourself. You may choose to add an excerpt or attachment after checking it for sensitive information. Email providers process messages according to their own policies. Reports are reviewed through the operator's support inbox; contact the operator for report retention or deletion requests.

## Ads, analytics and permissions

Two banner placements from MG Ads (Miracle Games) are integrated. Banners are requested only on the signed-in application screen (never on the sign-in screen or public pages) and are served from ad.mguwp.net; MG Ads and its partners receive the public AdUnitId and standard ad-request data under their own policy. Prompts, chats, PDF text and account identity are not sent to the ad provider. The app checks the MG Ads consent (CMP) requirement before requesting banners.

This version has no independent analytics system, payment collection or paid subscription. The Windows desktop package declares runFullTrust to run the Electron desktop application and its local callback, file picker/download and clipboard features. It does not request microphone, camera, location, contacts, broad file-system access capabilities or an always-running background service. It uses normal Windows file dialogs for user-selected files and downloads. Microsoft Store distribution and diagnostics are governed by Microsoft's own services and settings.

## Deletion, retention and your choices

- Settings lets you clear the current account's local history, chat, folders, favorites and stored image bytes. Language preference and a signed-in session can remain; use Sign out for the session.

- Delete explicitly saved cloud projects in Projects. Settings also provides account deletion, with Google reauthentication, to delete the Firebase account and cloud project copies. This does not automatically erase local projects; clear them separately.

- Local and cloud copies remain until you remove them or relevant storage is cleared. Keep backups you want to retain. The operator cannot restore cleared local data.

- Deleting application data does not delete provider logs, Google account data or support emails. Contact the relevant provider or the operator for their own records and applicable privacy rights.

## Provider policies and changes

[Google Privacy Policy](https://policies.google.com/privacy) · [Cloudflare Privacy Policy](https://www.cloudflare.com/privacypolicy/) · [Pollinations privacy information](https://pollinations.ai/privacy). Review their current terms before using the service. This policy will be updated if practices change; the published date identifies this version.

[Privacy and support contact](mailto:ahmedbecetti41@gmail.com) · [Terms](https://aurix-ea09b.web.app/pages/terms.html)
