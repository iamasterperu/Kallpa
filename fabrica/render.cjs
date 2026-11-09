// Renderiza la página HTML animada cuadro por cuadro y la convierte en video (sin audio) + portada.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
(async () => {
  const [page, dur, out, portada, tPortada] = process.argv.slice(2);
  const fps = 30, dir = out + '_frames';
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const opts = { args: ['--allow-file-access-from-files'] };
  if (fs.existsSync('/opt/pw-browsers/chromium') && !process.env.PW_DEFAULT) opts.executablePath = '/opt/pw-browsers/chromium';
  let b; try { b = await chromium.launch(opts); } catch (e) { delete opts.executablePath; b = await chromium.launch(opts); }
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.resolve(page)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  const n = Math.round(+dur * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => setT(t), i / fps);
    await p.screenshot({ path: `${dir}/f${String(i).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 86 });
  }
  await p.evaluate(t => setT(t), +tPortada);
  await p.screenshot({ path: portada, type: 'jpeg', quality: 90 });
  await b.close();
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', String(fps), '-i', `${dir}/f%05d.jpg`, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '22', '-preset', 'medium', '-r', String(fps), '-movflags', '+faststart', out]);
  fs.rmSync(dir, { recursive: true, force: true });
})().catch(e => { console.error(e); process.exit(1); });
