# AURIX — التحقق من الموقع لدى AdSense عبر ads.txt

هذه الحزمة تضيف **ملف تحقق `ads.txt` فقط** إلى ملفات Firebase Hosting العامة. استخدمت سطر AdSense الذي أعطاه مالك الموقع؛ لم أضف سكربت `adsbygoogle.js` إلى شاشة الدخول، ولم أفعل وحدات إعلان أو Auto ads. لا تعني هذه الخطوة الموافقة على الموقع أو بدء عرض الإعلانات. ملف `ads.txt` ومُعرّف الناشر بيانات عامة بطبيعتها.

من الهاتف ارفع `AURIX-adsense-verification.zip` إلى Google Cloud Shell، ثم نفّذ:

```sh
cd ~ && unzip -o AURIX-adsense-verification.zip && cd AURIX-adsense-verification && bash deploy.sh
```

اكتب `yes` لتأكيد نشر **Hosting فقط** في مشروع `aurix-ea09b`. بعد النجاح، تأكد أن الرابط التالي يعرض السطر الذي أعطاه لك AdSense:

`https://aurix-ea09b.web.app/ads.txt`

في AdSense اختر طريقة التحقق **Ads.txt snippet** (وليس Code snippet) ثم اضغط Verify وبعد نجاح التحقق Request review. إن أصرّ AdSense على وضع سكربت الإعلانات أو واجهت رسالة خطأ، أرسل النص أو صورة لها قبل أي تغيير آخر. لا ترسل كلمات المرور أو معلومات الدفع.
