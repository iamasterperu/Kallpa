// Captura cada <section class="slide"> de la página como JPG de 1080x1350 (4:5).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [page, prefijo] = process.argv.slice(2);
  const opts = { args: ['--allow-file-access-from-files'] };
  if (fs.existsSync('/opt/pw-browsers/chromium') && !process.env.PW_DEFAULT) opts.executablePath = '/opt/pw-browsers/chromium';
  let b; try { b = await chromium.launch(opts); } catch (e) { delete opts.executablePath; b = await chromium.launch(opts); }
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 } });
  await p.goto('file://' + path.resolve(page)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const slides = await p.$$('section.slide');
  for (let i = 0; i < slides.length; i++) await slides[i].screenshot({ path: `${prefijo}-${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 92 });
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
