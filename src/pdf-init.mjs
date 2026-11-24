/* Mozilla PDF.js 5.4.624 (Apache 2.0): parse text locally, never upload PDF bytes. */
import * as pdf from './assets/pdf.mjs';
pdf.GlobalWorkerOptions.workerSrc = new URL('./assets/pdf.worker.mjs', import.meta.url).href;
window.AurixPdf = {
  async extract(file) {
    if (!file || (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf'))) throw Error('Choose a PDF file.');
    if (file.size > 5_000_000) throw Error('PDF is too large. Maximum 5 MB.');
    const task = pdf.getDocument({ data: new Uint8Array(await file.arrayBuffer()), isEvalSupported: false });
    let doc;
    try {
      doc = await task.promise;
      if (doc.numPages > 20) throw Error('PDF has too many pages. Maximum 20.');
      let text = '';
      for (let n = 1; n <= doc.numPages; n++) {
        const page = await doc.getPage(n);
        const content = await page.getTextContent();
        text += `\n[Page ${n}]\n` + content.items.map(item => typeof item.str === 'string' ? item.str : '').join(' ') + '\n';
        page.cleanup();
      }
      text = text.trim();
      if (!text || text.length < 20) throw Error('No selectable text found. Scanned image PDFs need OCR, which is not available here.');
      return { text: text.slice(0, 12_000), pages: doc.numPages, truncated: text.length > 12_000 };
    } finally { await task.destroy().catch(() => {}); }
  }
};
window.dispatchEvent(new Event('aurix-pdf-ready'));
