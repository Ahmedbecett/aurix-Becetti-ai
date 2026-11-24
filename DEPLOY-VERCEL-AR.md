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
1. **Firebase Authentication → Settings → Authorized domains**: أضف نطاق Vercel
   (مثلاً `aurix.vercel.app` و`aurix-<team>.vercel.app`). بدون ذلك يفشل
   Google Sign-In بالخطأ `auth/unauthorized-domain`.
2. **Cloudflare Worker `aurix-api-ea09b`**: عدّل `backend/src/index.mjs` وأضف
   نطاق Vercel إلى مجموعة `ORIGINS`، ثم أعد نشر الـWorker. بدون ذلك سترفض
   المتصفحات طلبات `/api/image` و`/api/chat` و`/api/text` بسبب CORS.

## 4) ملاحظات
- `release/preview` هو الإصدار المنشور حالياً على `aurix-ea09b.web.app`
  (نسخة لوحة التحكم `dashboard-real-20261024`).
- `src/` هو مصدر التطبيق الأصلي، و`updates/dashboard-2026-10-24/` هو حزمة
  تحديث اللوحة.
- لا تضع أي مفاتيح Admin أو Cloudflare في المستودع. إعدادات Firebase العامة
  فقط (وهي عامة بطبيعتها).
