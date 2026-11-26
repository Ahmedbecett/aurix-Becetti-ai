# AURIX — رابط MSIX مباشر بعد رفض الحزمة السابقة

## التنزيل الحالي: الإصدار 1.0.2.0

**[تنزيل ملف MSIX مباشرة](https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/download/aurix-store-candidate-1.0.2/Ahmedbecetti.AURIXAI_1.0.2.0_x64.msix)**

هذا ملف MSIX نفسه، وليس أرشيف artifact خارجيًا يحتاج تسجيل الدخول أو فك ZIP. نُشر كـGitHub prerelease للاختبار والتقديم، **وليس كتطبيق معتمد أو منشور في Microsoft Store**.

```text
File: Ahmedbecetti.AURIXAI_1.0.2.0_x64.msix
Exact bytes: 164079485
SHA-256: 99b7a1819463cb4839f09c7709699da50f699aedfe4fe91f60d51b2b4093ae95
```

[تحميل ملف البصمة](https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/download/aurix-store-candidate-1.0.2/SHA256SUMS.txt) · [تقرير سلامة الحزمة](https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/download/aurix-store-candidate-1.0.2/msix-integrity.json) · [صفحة الإصدار وتفاصيل التحقق](https://github.com/Ahmedbecett/aurix-Becetti-ai/releases/tag/aurix-store-candidate-1.0.2)

يبلغ الحجم نحو 164 MB بالقياس العشري، أو 156.5 MiB. لا ترفع ملفًا حجمه 52.2 MB بدلًا منه. الرقم الدقيق بالبايت هو المرجع لتجنب اختلاف طريقة عرض MB بين الأدوات.

## تصحيح اسم العرض في 1.0.2.0

أرسل المالك صفحة Packages للمنتج **AURIX AI**، وفيها رفض صريح لاسم `Package/Properties/DisplayName` القديم **AURIX** لأنه غير محجوز. صُحّح الاسمان داخل ملف MSIX النهائي إلى **AURIX AI**:

- `Package/Properties/DisplayName`
- `Application/uap:VisualElements/@DisplayName`

تقرير البناء قرأ الاسمين من الأرشيف النهائي وأدرجهما في بيانات الإصدار. بقيت هوية الحزمة والناشر وPFN وSID وApplication Id كما هي. يحظر فحص المنتج الآن إعادة استخدام AURIX وحده. هذا إصلاح للخطأ المبلّغ عنه، وليس ادعاء قبول جميع الحقول لدى Microsoft.

## ماذا تفعل الآن في Partner Center؟

1. احذف إدخالات الحزم المرفوضة `1.0.0.0` و`1.0.1.0` إن بقيت في الصفحة؛ بقاء حزمة مرفوضة يمنع اكتمال التقديم.
2. نزّل الملف المباشر أعلاه وانتظر اكتمال التنزيل. لا تعِد تسمية ZIP أو صفحة HTML إلى `.msix`.
3. قارن الحجم والبصمة، ثم ارفع `Ahmedbecetti.AURIXAI_1.0.2.0_x64.msix` نفسه في Packages.
4. انتظر نتيجة التحقق الجديدة. إذا استمر الخطأ، احتفظ بالملف الذي رُفع ونتيجة الحجم/البصمة وتفاصيل الخطأ للمقارنة؛ لا نستنتج قبول Microsoft من نجاح أدوات البناء فقط.

بعد قبول الحزمة، تأكد من تفعيل أجهزة الكمبيوتر ضمن **Device family availability** إذا لم تكن محددة، ثم احفظ. تحذير AArch32/Arm العام ليس سبب خطأ اسم العرض؛ الحزمة الحالية تستهدف Windows.Desktop x64، ولم تُحوّل إلى ARM.

التحقق على Windows من الملف الذي نزّلته:

```powershell
(Get-Item .\Ahmedbecetti.AURIXAI_1.0.2.0_x64.msix).Length
Get-FileHash .\Ahmedbecetti.AURIXAI_1.0.2.0_x64.msix -Algorithm SHA256
```

## نتيجة التحقيق في رفض 0x8051100F

أبلغ المالك أن Partner Center رفض ملف `1.0.0.0` بحجم ظاهر **52.2 MB**. أعاد Windows runner تنزيل مرشّح GitHub القديم الأصلي وفحصه دون تعديله:

```text
Old file: Ahmedbecetti.AURIXAI_1.0.0.0_x64.msix
Exact bytes: 164079480
SHA-256: 07dfbcc3b98d4428a3e470b6eccb32d24c94ee76c119d654a561040892c9ce16
ZIP CRC checks: passed
SHA-256 block-map checks: passed
```

اختلاف الحجم يرجّح أن الملف الذي وصل إلى المتجر مختلف أو ناقص مقارنةً بمرشّح البناء. **لم نتسلم بايتات ملف 52.2 MB، لذلك لم يُثبت السبب النهائي ولم نُعِد إنتاج رفض Partner Center نفسه.** لم نغيّر هوية الناشر أو نضف توقيعًا ذاتيًا عشوائيًا لمحاولة إخفاء الخطأ.

## فحوص الإصدار الجديد

[مهمة MSIX على Windows](https://github.com/Ahmedbecett/aurix-Becetti-ai/actions/runs/45523785067/job/138901949231) نجحت، ونشرت الملف المباشر فقط بعد:

- نجاح اختبارات الواجهة والخادم، و23 اختبار Node و6 اختبارات Python للتحقق من الحزم.
- MakeAppx pack مع التحقق الافتراضي، دون `/nv`.
- فتح ZIP النهائي والتحقق من ملفات MSIX المطلوبة وCRCs، لا الاكتفاء باسم الامتداد.
- مطابقة هوية manifest وإصداره مع المصدر المجهّز.
- التحقق من كل كتلة SHA-256 في `AppxBlockMap.xml`.
- مطابقة قائمة الملفات وبصمات بايتاتها مع شجرة staging.
- MakeAppx unpack للملف النهائي مع التحقق الافتراضي.
- تسجيل الحجم وبصمة SHA-256 ورفع ملف MSIX مباشرة إلى GitHub Releases.

مصدر البناء: `bc43d44996ea32255a387fcac98439af9aa2229c`، والفرع الوحيد المستخدم هو `arena/1f56f634-aurix-becetti-ai`.

## حدود ما تم إنجازه

- هذا مرشّح غير موقّع لمسار تقديم MSIX إلى المتجر؛ ليس مُثبّت sideload عامًا. لا تطلب من المستخدمين تعطيل أمان Windows لتثبيته خارج المتجر.
- لا ندّعي اجتياز WACK أو اختبارات التشغيل التفاعلية على Windows 10/11 أو قبول Partner Center أو نشر التطبيق.
- ما زال نشر/فحص صفحات Google auth والخصوصية، واختبارات الوظائف الحية وسلامة المحتوى ولقطات الشاشة متطلبات قبل الإرسال النهائي. راجع [STORE-AR.md](STORE-AR.md).
- لا تستخدم روابط artifact للإصدار 1.0.0.0 في المحادثات السابقة لإعادة التقديم. الرابط الحالي هو ملف MSIX المباشر أعلاه، ولا تنطبق عليه صلاحية artifact القديمة البالغة 30 يومًا.

### 2026-11-26 — حزمة تحمل نظام الإعلانات

- تشغيل بناء المتجر مرة أخرى على نفس الإصدار `1.0.2.0` (بدون رفع إلى Store).
- بعد نجاح `MSIX candidate (public owner identity)` تُنشر الحزمة في صفحة الإصدار `windows-ads-1.0.2.0`
  مع `SHA256SUMS.txt` و`AppxManifest.xml` و`store-build.json` و`msix-integrity.json`.
- ملف `AURIX-Windows-x64-ads` = نسخة Electron المحمولة/NSIS التي تُظهر البانر فعليًا في Chromium.
