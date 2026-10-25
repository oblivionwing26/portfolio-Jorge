// Uso: node shoot.mjs <salida-prefijo> [w h] [acciones JSON]
import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const out = process.argv[2] || 'shot';
const W = +(process.argv[3] || 1440), Hh = +(process.argv[4] || 900);
const arg5 = process.argv[5] || '[["wait",2500],["shot","default"]]';
const actions = JSON.parse(arg5.startsWith('@') ? fs.readFileSync(arg5.slice(1), 'utf8') : arg5);
const mobile = W < 600;

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || undefined,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--enable-webgl']
});
const ctx = await browser.newContext({ viewport: { width: W, height: Hh }, deviceScaleFactor: mobile ? 2 : 1, isMobile: mobile, hasTouch: mobile });
const page = await ctx.newPage();
const logs = [];
page.on('console', m => logs.push(`[${m.type()}] ${m.text()}`));
page.on('pageerror', e => logs.push(`[pageerror] ${e.message}`));
await page.route('https://cdn.jsdelivr.net/npm/three@0.165.0/**', async (route) => {
  const u = new URL(route.request().url());
  const rel = u.pathname.replace('/npm/three@0.165.0/', '');
  const f = path.join('node_modules/three', rel);
  if (fs.existsSync(f)) await route.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(f), headers: { 'access-control-allow-origin': '*' } });
  else await route.fulfill({ status: 404, body: 'nf' });
});
await page.route('https://fonts.googleapis.com/**', r => r.fulfill({ status: 200, contentType: 'text/css', body: '' }));
await page.route('https://fonts.gstatic.com/**', r => r.fulfill({ status: 404, body: '' }));

const html = fs.readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const doc = html;
await page.route('http://local.test/', r => r.fulfill({ status: 200, contentType: 'text/html', body: doc }));
const t0 = Date.now();
await page.goto('http://local.test/');
try {
  await page.waitForFunction(() => window.__valle || !document.getElementById('fatal').hidden, null, { timeout: 240000 });
} catch (e) { logs.push('TIMEOUT waiting for scene'); }
logs.push(`ready in ${Date.now() - t0} ms`);
const fatalVisible = await page.evaluate(() => !document.getElementById('fatal').hidden);
if (fatalVisible) logs.push('FATAL: ' + await page.evaluate(() => document.getElementById('fatalTitle').textContent + ' | ' + document.getElementById('fatalCode').textContent));
for (const a of actions) {
  if (a[0] === 'wait') await page.waitForTimeout(a[1]);
  else if (a[0] === 'eval') { try { const r = await page.evaluate(a[1]); if (r !== undefined) logs.push('eval: ' + JSON.stringify(r)); } catch (e) { logs.push('eval error ' + e.message); } }
  else if (a[0] === 'click') await page.click(a[1]);
  else if (a[0] === 'shot') { await page.screenshot({ path: `shots/${out}-${a[1]}.png`, timeout: 300000, animations: 'allow', caret: 'initial' }); logs.push('shot ' + a[1]); }
}
console.log(logs.join('\n'));
await browser.close();
