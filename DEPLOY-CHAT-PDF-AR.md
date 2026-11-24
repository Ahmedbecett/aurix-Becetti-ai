# المرحلة التالية: محادثة AURIX وقراءة PDF محليًا

**حالة النشر:** الملفات جاهزة واختُبرت محليًا؛ لم تُنشر إضافة الدردشة إلى Worker أو Firebase بعد. الصورة المجانية ما زالت قد تفشل بـ502؛ تظهر رسالة تعطل صريحة، ولا نفعّل صورة مدفوعة أو OpenAI أو فيديو. لا تنشر واجهة الدردشة قبل نشر Worker وتجهيز مفتاح Gemini من مشروع مجاني مستقل لـAURIX.

## 1) مفتاح Gemini مجاني خاص بـAURIX

افتح Google AI Studio، وأنشئ مفتاح Gemini API في **مشروع مخصص لـAURIX وعلى Free tier دون ربط فوترة**. تحقق بنفسك من حالة الحساب والحصص قبل المتابعة؛ مفتاح Gemini القادم من مشروع مدفوع قد يسبب رسومًا. لا ترسل المفتاح إليّ أو إلى المحادثة أو Google Drive. لا حاجة لمفتاح OpenAI؛ صور OpenAI API ليست مجانية.

**تنبيه خصوصية:** النص المستخرج من PDF عند سؤالك والرسائل يذهبان إلى Gemini عبر Worker. النص فقط، لا بايتات PDF. بيانات Free tier قد تُستخدم لتحسين منتجات المزوّد؛ لا ترفع PDF حساسًا.

## 2) تحديث Worker من Cloud Shell بهاتفك

نزّل `aurix-chat-backend-update.zip` وارفعه إلى Google Cloud Shell. استعمل حساب Cloudflare صاحب Worker الموجود `aurix-api-ea09b`، وتوكن API محدود Editor لهذا Worker؛ لا تنشر التوكن. إن كان التوكن الذي ظهر سابقًا في المحادثة ما زال فعّالًا فألغِه وأنشئ بديلًا.

في Cloud Shell اكتب **كل سطر على حدة**. عند سطر `read` ألصق توكن نشر Cloudflare في الطلب المخفي:

```sh
read -rsp 'Cloudflare deploy token: ' CLOUDFLARE_API_TOKEN; echo; export CLOUDFLARE_API_TOKEN
cd ~ && unzip -o aurix-chat-backend-update.zip && cd aurix-worker
npx --yes wrangler@4.152.0 secret put GEMINI_API_KEY
```

عند سؤال `GEMINI_API_KEY` ألصق **مفتاح Gemini** داخل Cloud Shell فقط. إذا *وتحققت بنفسك* أن مشروع المفتاح على Free tier **غير مربوط بفاتورة**، أكمل وأدخل `yes` عند الطلب:

```sh
npx --yes wrangler@4.152.0 secret put GEMINI_FREE_TIER_CONFIRMED
npx --yes wrangler@4.152.0 deploy
unset CLOUDFLARE_API_TOKEN
```

إذا كان المشروع مدفوعًا أو لا تعرف حالة الفوترة، **لا تدخل `yes` ولا تفعّل مفتاح الدردشة**؛ سيرفض Worker طلبات الدردشة برمز 503 عمدًا. لا تجرّب طلبًا مدفوعًا للتأكد. رابط Worker العام يبقى نفسه. لا تشارك المفاتيح أو رسائل سجل تعرض قيمًا حساسة.

## 3) تحديث موقع Firebase

بعد نجاح Worker، نزّل `aurix-chat-pdf-update.zip` وارفعه إلى Cloud Shell. لا تحتاج توكن Cloudflare لنشر Firebase:

```sh
cd ~ && unzip -o aurix-chat-pdf-update.zip && cd aurix-chat-pdf-update && firebase deploy --only hosting --project aurix-ea09b
```

افتح https://aurix-ea09b.web.app/?v=chat-pdf-20261024 بنافذة خاصة، سجّل دخول Google، افتح **AI Chat**، واسأل سؤالًا بسيطًا. جرّب ملف PDF صغيرًا يحتوي نصًا قابلًا للتحديد؛ حد 5MB و20 صفحة، ويُرسل أول 12 ألف حرف فقط إلى النموذج عند السؤال. PDF المصوّر يحتاج OCR، وهو غير متوفر الآن. الملف الأصلي لا يُخزّن في Firestore ولا Cloudflare؛ الرسائل الأخيرة تُحفظ محليًا لهذا الحساب في هذا المتصفح.

إذا فشل إرسال السؤال، أرسل صورة للخطأ بعد إخفاء الأسرار. لا تدّعِ أن ميزة الدردشة تعمل قبل اختبار سؤال حقيقي بمفتاحك. ملفات PDF.js مضمّنة محليًا في الحزمة بترخيص Apache 2.0؛ لا تعتمد على CDN.

المراجع الرسمية: https://ai.google.dev/gemini-api/docs/pricing ، https://ai.google.dev/gemini-api/docs/rate-limits ، https://developers.cloudflare.com/workers/wrangler/commands/#secret-put
