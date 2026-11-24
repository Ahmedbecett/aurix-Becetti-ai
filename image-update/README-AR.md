# تحديث الصور المجانية لـAURIX — Workers AI

**حالة النشر:** هذا التحديث جُهّز واختُبر محليًا باستخدام نموذج مُحاكى؛ لم يُنشر أو يُختبر توليد صورة حقيقية بعد. اخترتَ أن حساب Cloudflare الخاص بـAURIX على خطة **Workers Free**. لا تشغّل الحزمة إذا انتقل الحساب إلى Workers Paid؛ الفئة المجانية تمنح 10,000 Neurons يوميًا وتتوقف بعد استنفادها على خطة Free، بينما يمكن تحصيل رسوم بعد ذلك على Paid.

## من الهاتف في Google Cloud Shell

ارفع `AURIX-free-images-update.zip` ثم نفذ:

```sh
cd ~ && unzip -o AURIX-free-images-update.zip
cd AURIX-free-images-update
bash deploy.sh
```

اكتب `yes` فقط إذا ما زال الحساب المحدد على **Workers Free**، ثم الصق **توكن نشر Cloudflare** عند الطلب المخفي. ليس مطلوبًا إدخال مفاتيح Gemini أو OpenAI أو FreeTheAI مرة أخرى. ينشر السكربت Worker أولًا، ثم Firebase Hosting. عند انقطاع Cloud Shell، افتح جلسة جديدة ونفذ `cd ~/AURIX-free-images-update && bash deploy.sh`؛ سيسألك عن التوكن مجددًا.

## ما تغيّر

- صور مربعة فقط بتوليد Cloudflare Workers AI `@cf/black-forest-labs/flux-1-schnell`، أربع خطوات سريعة أو ثماني خطوات تفصيلية. يرفض طلب نسبة أخرى بدل إظهار صورة بنسب خاطئة.
- حُذف اعتماد مسار الصور على مزوّد Pollinations ذي الحد المشترك على عنوان IP؛ النص/الشيفرة القديمة ما زالت تستخدم Pollinations، والدردشة/PDF تستخدم Gemini كما هي.
- المصادقة Google JWT والحد لكل مستخدم والمسار الآمن لم تتغير. الصور تُحفظ في متصفح المستخدم فقط.
- الفيديو غير مفعّل، وFTA/OpenAI مخزّنان فقط إن أضفتهما أنت؛ **لا تُجرى بهما طلبات** ولا ينشر هذا الإصدار أي مفتاح.
- عند نفاد حصة Workers AI أو غياب الـAI binding تفشل الصور برسالة واضحة ولا تحفظ صورة وهمية.

بعد النجاح افتح https://aurix-ea09b.web.app/?v=image-workers-ai-20261024 وجرّب صورة مربعة واحدة بوصف واضح باللغة الإنجليزية. راقب لوحة Workers AI لحصة الحساب. لا تدّعِ أن الصور تعمل حيًا قبل اختبارها. ملفات PDF الأصلية تبقى على الجهاز، ويُرسل النص المستخرج فقط عند سؤال الدردشة.

المراجع الرسمية: https://developers.cloudflare.com/workers-ai/platform/pricing/ ، https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/ ، https://developers.cloudflare.com/workers-ai/get-started/workers-wrangler/
