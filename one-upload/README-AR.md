# ملف واحد لرفع تحديث AURIX

ارفع `AURIX-upload-once-chat-pdf.zip` إلى Cloud Shell ثم نفّذ:

```sh
cd ~
unzip -o AURIX-upload-once-chat-pdf.zip
cd AURIX-upload-once-chat-pdf
bash deploy.sh
```

سيسألك عن تحققك من أن مشروع Gemini خاص بـAURIX وعلى الفئة المجانية **دون فوترة**، ثم توكن نشر Cloudflare، ثم مفتاح Gemini عند طلب Wrangler. اكتب `yes` في طلب الـsecret الثاني `GEMINI_FREE_TIER_CONFIRMED`. لا تحفظ أي مفتاح في هذه الحزمة أو في المحادثة. السكربت ينشر Worker أولًا ثم Firebase؛ لا يفعّل OpenAI أو صورًا مدفوعة. تأكد أن حساب Firebase المسجل في Cloud Shell يملك مشروع `aurix-ea09b`.

**مهم:** المفاتيح التي أُرسلت في المحادثة تعتبر مكشوفة؛ أنشئ بديلًا آمنًا قبل استخدامها. إرسال مفتاح جديد إلى المحادثة ليس جزءًا من هذه العملية.
