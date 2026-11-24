# نشر AURIX على Vercel — خطوات دقيقة

## 1) إنشاء المستودع على GitHub
ارفع محتويات هذا المجلد إلى مستودع جديد (مثلاً `Ahmedbecett/aurix`).

## 2) ربط Vercel
- في Vercel: **Add New → Project → Import** مستودع `aurix`.
- Framework Preset: **Other**.
- Build Command: اتركه فارغاً.
- Output Directory: `release/preview`.
- Root Directory: `.` (جذر المستودع).
- Deploy.

## 3) خطوتان إلزاميتان حتى يعمل التطبيق بالكامل على نطاق Vercel
1. **Firebase Authentication → Settings → Authorized domains**: أضف النطاقات:
   - `aurix-gules.vercel.app`
   - `aurix-ahmed-d33b.vercel.app`
   - `aurix-git-main-ahmed-d33b.vercel.app`

   بدون ذلك يفشل Google Sign-In بالخطأ `auth/unauthorized-domain`.
2. **Cloudflare Worker `aurix-api-ea09b`**: ملف `backend/src/index.mjs` في هذا المستودع
   مُحدَّث ليشمل نطاقات Vercel في `ORIGINS` (ومنطق `aurix-*.vercel.app`). أعد نشر الـWorker:
   ```sh
   cd backend && npx wrangler deploy
   ```
   بدون ذلك سترفض المتصفحات طلبات `/api/image` و`/api/chat` و`/api/text` بسبب CORS.

## 3.1) النطاقات الحالية بعد النشر
- الإنتاج: https://aurix-gules.vercel.app
- Alias: https://aurix-ahmed-d33b.vercel.app (محمي بـSSO)
- Git branch: https://aurix-git-main-ahmed-d33b.vercel.app

## 4) ملاحظات
- `release/preview` هو الإصدار المنشور حالياً على `aurix-ea09b.web.app`
  (نسخة لوحة التحكم `dashboard-real-20261024`).
- `src/` هو مصدر التطبيق الأصلي، و`updates/dashboard-2026-10-24/` هو حزمة
  تحديث اللوحة.
- لا تضع أي مفاتيح Admin أو Cloudflare في المستودع. إعدادات Firebase العامة
  فقط (وهي عامة بطبيعتها).
