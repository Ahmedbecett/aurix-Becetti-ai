# نشر إصلاح AURIX من الهاتف عبر Firebase Cloud Shell

**قبل البدء:** الحزمة [`aurix-quality-update.zip`](aurix-quality-update.zip) تحتوي ملفات الواجهة العامة فقط، بلا مفتاح Firebase الإداري. الإصلاح **لم يُنشر بعد** على https://aurix-ea09b.web.app؛ ينبغي تنفيذ هذه الخطوات بحسابك صاحب مشروع `aurix-ea09b`.

1. نزّل ملف **`aurix-quality-update.zip`** من مساحة العمل إلى هاتفك (اضغط اسم الملف في المحادثة/عارض الملفات ثم تنزيل).
2. افتح [لوحة مشروع AURIX في Firebase](https://console.firebase.google.com/project/aurix-ea09b/hosting) من المتصفح بحسابك. اضغط رمز **Cloud Shell** الذي يشبه `>_` أعلى الصفحة. إن كان مخفيًا في الجوال، افتح قائمة المتصفح `⋮` وفعّل **عرض الموقع المخصص للكمبيوتر** (Desktop site)، ثم أعد فتح الصفحة. انتظر حتى يظهر مربع أوامر في أسفل الشاشة.
3. في شريط Cloud Shell اضغط **More / المزيد `⋮` → Upload / رفع**، واختر `aurix-quality-update.zip` من تنزيلات هاتفك. يُرفع إلى مجلدك الرئيسي في Cloud Shell. قد يختلف موضع زر `⋮` باختلاف عرض الهاتف.
4. انسخ هذا السطر والصقه في مربع الأوامر ثم اضغط Enter:
   ```sh
   unzip -o aurix-quality-update.zip && cd aurix-quality-update && firebase deploy --only hosting --project aurix-ea09b
   ```
5. انتظر ظهور **Deploy complete!** ورابط `https://aurix-ea09b.web.app`. لا ترسل أي رمز دخول أو مفتاح إليّ. Cloud Shell في لوحة Firebase يكون عادةً موثّقًا بحسابك بالفعل؛ إن طلب الدخول نفّذ `firebase login --no-localhost` واتبع التعليمات داخل Cloud Shell فقط.
6. افتح [استوديو الصور](https://aurix-ea09b.web.app/#image) في نافذة خاصة (أو حدّث الصفحة بقوة). إذا ظهر **As written** و**Translate prompt to English** و**Fast preview · 512px** فقد وصلت النسخة الجديدة. جرّب وصفًا عربيًا؛ يجب أن يطلب منك الترجمة بدل إنتاج صورة عشوائية.

**إن ظهر خطأ:** أرسل صورة لنص الخطأ فقط بعد إخفاء أي رمز تسجيل دخول. لا ترسل ملف Firebase Admin أو كلمة مرور.

**ملاحظة:** النطاق المرحلي باقٍ على `noindex` عن قصد، ولا يُقدّم إلى AdSense قبل نطاقك النهائي ومراجعة المحتوى.

المراجع الرسمية: https://firebase.google.com/docs/cloud-shell وhttps://cloud.google.com/shell/docs/uploading-and-downloading-files
