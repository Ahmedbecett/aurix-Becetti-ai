# AURIX — تنزيل مرشحات ويندوز وMicrosoft Store

**تاريخ البناء:** 24 نوفمبر 2026، الساعة 23:21 UTC تقريبًا.

نجح بناء الملفات على Windows عبر GitHub Actions. هذا إصدار **مرشّح للاختبار والمراجعة**؛ ليس تطبيقًا منشورًا أو معتمدًا في Microsoft Store، ولم يُجرَ اختبار تشغيل تفاعلي أو WACK في هذه الجلسة.

## 1. حزمة Microsoft Store (MSIX)

[تنزيل مخرجات MSIX من GitHub Actions](https://github.com/Ahmedbecett/aurix-Becetti-ai/actions/runs/45508613913/artifacts/14974542325)

قد يطلب GitHub تسجيل الدخول لتنزيل artifact. التنزيل أرشيف ZIP؛ بعد فكّه ستجد حزمة البناء:

```text
Ahmedbecetti.AURIXAI_1.0.0.0_x64.msix
```

وملفات `SHA256SUMS.txt` و`AppxManifest.xml` و`store-build.json` و`makeappx.log` ومسودات الإرسال. قارن بصمة MSIX بالقيمة الموجودة داخل `SHA256SUMS.txt`. البصمة ليست مجرد اسم الملف.

هذه حزمة **غير موقّعة مخصّصة لمسار المتجر** بعد استكمال اختبارات القبول. لا تشاركها كمُثبّت sideload عام ولا تطلب من المستخدمين تعطيل أمان Windows لتثبيتها. ارفع ملف **MSIX نفسه، وليس ZIP**، في Partner Center بعد مراجعة المتطلبات.

## 2. مُثبّت EXE ونسخة محمولة للاختبار

[تنزيل Setup وPortable من GitHub Actions](https://github.com/Ahmedbecett/aurix-Becetti-ai/actions/runs/45508613913/artifacts/14975266903)

بعد فك الأرشيف، تتضمن مخرجات البناء:

```text
AURIX-1.0.0-x64-Setup.exe
AURIX-1.0.0-x64-Portable.exe
SHA256SUMS.txt
```

هذه ليست حزمة الرفع لمسار MSIX في المتجر. لا توجد شهادة توقيع Windows تجارية مهيّأة لهذه القناة؛ قد تظهر تحذيرات أو تمنعها سياسة الجهاز. اختبر فقط في بيئة اختبار مناسبة، ولا تعطّل سياسات الحماية أو توصي مستخدمًا بتجاوز تحذير ملف مجهول.

## 3. بيانات البناء المؤكدة

- [صفحة البناء والتحقق](https://github.com/Ahmedbecett/aurix-Becetti-ai/actions/runs/45508613913).
- الفرع: `arena/1f56f634-aurix-becetti-ai`.
- commit المصدر الذي بُني: `9f69e21d50b5ec8402415ef116007abe0e5f869f`.
- نتيجة مهمة `MSIX candidate (public owner identity)`: **success**، بما في ذلك MakeAppx واختبارات npm.
- نتيجة مهمة `windows`: **success**، بما في ذلك بناء NSIS وPortable.
- اسم الحزمة: `Ahmedbecetti.AURIXAI`.
- الناشر: `CN=A5D5DC31-4A15-4059-8030-D96C51054596`.
- اسم الناشر الظاهر: `Ahmedbecetti`.
- PFN: `Ahmedbecetti.AURIXAI_y0zvy3a8v70hm`؛ تطابق مع حساب Publisher الذي أرسله المالك.
- Store ID: `9NLM756D1CZR`؛ لا يعني توفر صفحة منتج أو رابط تنزيل من Microsoft Store بعد.
- اسم العرض المستخدم: **AURIX**، ويحتاج تأكيدًا أنه الاسم المحجوز بالضبط قبل الإرسال النهائي.

روابط artifacts مؤقتة بحسب سياسة GitHub الحالية، وتنتهي هذه المخرجات في **24 ديسمبر 2026** ما لم تُحذف قبل ذلك. احتفظ بنسخة وبصمتها. ليست هذه روابط Microsoft Store عامة أو GitHub Releases منشورة.

بيانات سلامة أرشيفات artifacts كما أبلغت بها GitHub API (هذه بصمات أرشيف artifact، وليست بصمات ملفات EXE/MSIX الداخلية):

```text
AURIX-Microsoft-Store-x64-candidate
size: 164000241 bytes
sha256: fdabdb31206f29d371ff7afdbc708c13a589415a5002da3855bd063ef6aaf4bb

AURIX-Windows-x64
size: 233502039 bytes
sha256: c0ca3389a34b58990092c30fe865cc94db3d5443d30414d20fc4fe8943abeea1
```

نجاح البناء والتحقق أعلاه مؤكد من بيانات GitHub Actions. محاولة تنزيل الأرشيف داخل بيئة هذه الجلسة تعذرت بسبب قيود الاتصال بمضيف تخزين artifacts؛ لذلك لا ندّعي أننا فتحنا محتوى الأرشيف محليًا أو شغّلنا الملفات تفاعليًا. التنزيل من متصفح المستخدم عبر رابط GitHub منفصل عن قيود هذه البيئة.

## 4. ما الذي يجب إنهاؤه قبل الإرسال والنشر؟

1. **تأكيد اسم العرض المحجوز:** هل هو AURIX أم AURIX AI أم اسم آخر؟ اسم الهوية `Ahmedbecetti.AURIXAI` ليس دليلًا على اسم العرض.
2. نشر صفحة ربط Google وسياسة خصوصية ويندوز على Firebase الحالي، والتحقق منهما من المتصفح. لا يكفي بناء ملف MSIX لجعلهما منشورين؛ محاولة فحص الروابط من هذه الجلسة لم تنجح، ولا نثبت حالتهما الحية.
3. اختبار تثبيت وتشغيل حقيقي على Windows 10 22H2 وWindows 11، والدخول عبر Google والتوليد وPDF والحفظ والخروج والعزل والتحديث والإزالة.
4. تشغيل Windows App Certification Kit ومعالجة أي إخفاقات.
5. التقاط لقطات Windows فعلية لنفس الإصدار، والتحقق من حقوق المزوّدين وسلامة المحتوى وبريد البلاغات.
6. إكمال حقول Partner Center والإفصاح عن AI وIARC والخصوصية والصلاحيات وملاحظات المراجعين، ثم الإرسال بقرار المالك.

التفاصيل في [STORE-AR.md](STORE-AR.md). وجود ملفات تنزيل حقيقية لا يعني استكمال هذه الخطوات أو موافقة Microsoft.
