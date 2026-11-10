// Carrusel continuo: captura el #lienzo (N×1080 por 1440) y lo corta en N slides 3:4 (1080x1440).
// Uso: node render_panorama.cjs pagina.html N prefijo   ->  prefijo-01.jpg ... prefijo-NN.jpg + prefijo-vista.jpg
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [page, nStr, prefijo] = process.argv.slice(2); const n = +nStr;
  const opts = { args: ['--allow-file-access-from-files'] };
  if (fs.existsSync('/opt/pw-browsers/chromium')) opts.executablePath = '/opt/pw-browsers/chromium';
  const b = await chromium.launch(opts);
  const p = await b.newPage({ viewport: { width: n * 1080, height: 1440 } });
  await p.goto('file://' + path.resolve(page)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(500);
  for (let i = 0; i < n; i++)
    await p.screenshot({ path: `${prefijo}-${String(i + 1).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 93, clip: { x: i * 1080, y: 0, width: 1080, height: 1440 } });
  // vista previa: todo el panorama reducido, con una línea en cada corte
  await p.evaluate(n => { for (let i = 1; i < n; i++) { const d = document.createElement('div'); d.style.cssText = `position:absolute;top:0;bottom:0;left:${i * 1080 - 3}px;width:6px;background:#0b0614;z-index:999`; document.getElementById('lienzo').appendChild(d); } }, n);
  await p.setViewportSize({ width: n * 1080, height: 1440 });
  const buf = await p.screenshot({ type: 'jpeg', quality: 85 });
  fs.writeFileSync(`${prefijo}-vista.jpg`, buf);
  await b.close();
})().catch(e => { console.error(e); process.exit(1); });
