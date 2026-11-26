# AURIX Worker

**مصدر Worker الحالي:** يغطي `/api/chat` (Google Gemini free tier) و`/api/text` (Pollinations) و`/api/image` (Cloudflare Workers AI · FLUX.1 Schnell) كما يستخدمها تطبيق Windows 1.0.2.0 المنشور على Microsoft Store. حالة النشر الحقيقية لكل مسار تُتحقق بالاختبار المباشر ولا يفترضها هذا الملف. حزم التحديث المؤقتة القديمة (`image-update/`, `one-upload/` وغيرها) أُزيلت من المستودع لأنها كانت نسخًا مكرّرة غير مستخدمة.

المسارات `/api/chat` (Google Gemini Free tier) و`/api/text` (Pollinations) و`/api/image` (Cloudflare Workers AI FLUX.1 Schnell في الإصدار الجديد) كلها تتطلب Firebase Google ID token صحيحًا، وتستخدم محدد معدل لكل مستخدم. الملف الأصلي PDF محلي ولا يُرفع. الصور تُحفظ محليًا في متصفح المستخدم. الفيديو متوقف.

**شرط عدم الرسوم:** المستخدم أكّد أن حساب Cloudflare الخاص بـAURIX على Workers Free. يعطي Workers AI 10,000 Neurons مجانية يوميًا ويتوقف عند نفادها على Free؛ إذا تحول الحساب إلى Workers Paid فلا تنشر هذا التحديث دون موافقة جديدة وحماية موثوقة للإنفاق. لا يستخدم هذا التحديث أسرار OPENAI_API_KEY أو FTA_API_KEY حتى إن كانت موجودة في Worker.

للاختبار المحلي دون اتصالات مدفوعة: `node test.mjs`. اختبارات الـAI تستخدم محاكاة، وليست إثباتًا لتوليد صورة حيّة. لا تضع مفاتيح API أو توكنات النشر في الملفات أو المحادثة.
