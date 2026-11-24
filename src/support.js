/* AURIX: user-controlled content reports. Nothing is sent automatically. */
(function () {
  'use strict';
  const copy = {
    en: { open: 'Report AI content', title: 'Report inappropriate AI content', note: 'Nothing is sent automatically. Describe the concern without passwords, account tokens or confidential PDF text. You choose what to include. We prepare an email for you to review and send.', label: 'What happened?', prepare: 'Prepare email', send: 'Open email app to review and send', copy: 'Copy report', close: 'Close', ready: 'Email draft prepared, not sent. If no email app is configured, copy the report and email it to ahmedbecetti41@gmail.com.', copied: 'Report copied. Send it to ahmedbecetti41@gmail.com.', failed: 'Clipboard unavailable. Select and copy your report manually.', privacy: 'Windows privacy policy' },
    ar: { open: 'الإبلاغ عن محتوى الذكاء الاصطناعي', title: 'الإبلاغ عن محتوى غير مناسب', note: 'لن يُرسل شيء تلقائيًا. صف المشكلة دون كلمات مرور أو رموز دخول أو نص PDF سري. أنت تختار ما تشاركه؛ نجهّز رسالة بريد لتراجعها وترسلها بنفسك.', label: 'ما المشكلة؟', prepare: 'تجهيز رسالة البريد', send: 'فتح تطبيق البريد للمراجعة والإرسال', copy: 'نسخ البلاغ', close: 'إغلاق', ready: 'جُهّزت الرسالة ولم تُرسل. إن لم يكن لديك تطبيق بريد، انسخ البلاغ وأرسله إلى ahmedbecetti41@gmail.com.', copied: 'نُسخ البلاغ. أرسله إلى ahmedbecetti41@gmail.com.', failed: 'تعذّر النسخ. حدّد نص البلاغ وانسخه يدويًا.', privacy: 'خصوصية نسخة ويندوز' },
    fr: { open: 'Signaler un contenu IA', title: 'Signaler un contenu IA inapproprié', note: 'Aucun envoi automatique. Décrivez le problème sans mot de passe, jeton de connexion ni texte PDF confidentiel. Vous choisissez les informations à partager et envoyez vous-même le courriel préparé.', label: 'Quel est le problème ?', prepare: 'Préparer le courriel', send: 'Ouvrir la messagerie pour vérifier et envoyer', copy: 'Copier le signalement', close: 'Fermer', ready: 'Brouillon préparé, non envoyé. Sans messagerie configurée, copiez le signalement et envoyez-le à ahmedbecetti41@gmail.com.', copied: 'Signalement copié. Envoyez-le à ahmedbecetti41@gmail.com.', failed: 'Presse-papiers indisponible. Sélectionnez et copiez le texte manuellement.', privacy: 'Confidentialité Windows' }
  };
  const root = document.createElement('div');
  root.className = 'aurix-support';
  const open = document.createElement('button');
  open.id = 'report-content'; open.type = 'button'; open.className = 'btn sm ghost';
  const policy = document.createElement('a');
  policy.href = '/pages/windows-privacy.html'; policy.id = 'windows-privacy-link'; policy.hidden = !window.AurixDesktop;
  root.append(open, policy); document.body.append(root);
  const dialog = document.createElement('dialog');
  dialog.id = 'content-report'; dialog.className = 'content-report';
  dialog.setAttribute('aria-labelledby', 'report-title');
  dialog.innerHTML = '<h2 id="report-title"></h2><p id="report-note"></p><form id="report-form"><label for="report-details" id="report-label"></label><textarea id="report-details" class="ta" required="required" minlength="5" maxlength="1600"></textarea><button class="btn" id="report-prepare" type="submit"></button></form><p id="report-status" role="status"></p><a class="btn sm ghost" id="report-email" hidden="hidden"></a><button class="btn sm ghost" id="report-copy" type="button" hidden="hidden"></button><button class="btn sm ghost" id="report-close" type="button"></button>';
  document.body.append(dialog);
  const get = id => dialog.querySelector('#' + id);
  const labels = () => copy[document.documentElement.lang] || copy.en;
  const update = () => { open.textContent = labels().open; policy.textContent = labels().privacy; };
  update();
  new MutationObserver(update).observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
  let report = '';
  open.addEventListener('click', () => {
    const c = labels();
    for (const [id, key] of Object.entries({ 'report-title': 'title', 'report-note': 'note', 'report-label': 'label', 'report-prepare': 'prepare', 'report-email': 'send', 'report-copy': 'copy', 'report-close': 'close' })) get(id).textContent = c[key];
    get('report-form').reset(); get('report-status').textContent = ''; report = '';
    get('report-email').hidden = true; get('report-email').removeAttribute('href'); get('report-copy').hidden = true;
    dialog.showModal(); get('report-details').focus();
  });
  get('report-form').addEventListener('submit', event => {
    event.preventDefault();
    const details = get('report-details').value.trim();
    if (details.length < 5 || details.length > 1600) return;
    // Deliberately exclude prompts, outputs, account IDs, PDF contents and tokens.
    const requestedRoute = location.hash.slice(1).split('?')[0];
    const route = ['home', 'image', 'code', 'writer', 'chat', 'projects', 'history', 'favorites', 'settings', 'login', 'video', 'billing'].includes(requestedRoute) ? requestedRoute : 'home';
    report = `AURIX AI content report\nArea: ${route}\nDate: ${new Date().toISOString()}\n\n${details}`;
    get('report-email').href = 'mailto:ahmedbecetti41@gmail.com?subject=' + encodeURIComponent('AURIX AI content report') + '&body=' + encodeURIComponent(report);
    get('report-email').hidden = false; get('report-copy').hidden = false;
    get('report-status').textContent = labels().ready;
  });
  get('report-copy').addEventListener('click', async () => {
    if (!report) return;
    try { await navigator.clipboard.writeText(report); get('report-status').textContent = labels().copied; }
    catch { get('report-status').textContent = labels().failed; }
  });
  get('report-close').addEventListener('click', () => dialog.close());
})();
