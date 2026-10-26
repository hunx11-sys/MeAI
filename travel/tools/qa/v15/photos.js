const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'), fs = require('fs');
const [,, html, dir] = process.argv; const url = 'file://' + path.resolve(html);
const jpg = [0,1,2,3].map(n => fs.readFileSync(path.join(dir, `p${n}.jpg`)));
const KY = JSON.parse(fs.readFileSync('/home/user/MeAI/travel/data/guides/kyoto.json')).spots;
const ll = n => KY.find(s => s.name_ja === n);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const c = await b.newContext({ ...devices['iPhone 13'] }); const p = await c.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
  const log = [];
  const ii = (t, w, h, lic, n) => ({ title: t, index: 0, imageinfo: [{ mime: 'image/jpeg', width: w, height: h, thumburl: `https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/F${n}.jpg/960px-F${n}.jpg`, descriptionurl: 'https://commons.wikimedia.org/wiki/'+t, extmetadata: { LicenseShortName: { value: lic }, Artist: { value: 'Taro' } } }] });
  await p.route(/ja\.wikipedia\.org/, r => { const u = new URL(r.request().url()); const ts = u.searchParams.get('titles').split('|'); log.push('wiki:' + ts.join('|'));
    const pages = {}; let id = 1;
    for (const t of ts){
      const s = KY.find(x => x.name_ja.split('・')[0] === t || x.name_ja === t);
      if (t === '清水寺') pages[id++] = { title: t, pageprops: { page_image_free: 'Kiyomizu.jpg' }, coordinates: [{ lat: s.lat + 0.003, lon: s.lng }] };
      else if (t === '伏見稲荷大社') pages[id++] = { title: t, pageprops: { page_image_free: 'Fushimi_Inari.jpg' }, coordinates: [{ lat: s.lat, lon: s.lng }] };
      else if (t === '八坂神社') pages[id++] = { title: t, pageprops: { page_image_free: 'Far.jpg' }, coordinates: [{ lat: 35.0, lon: 139.0 }] };
      else if (t === '三十三間堂') pages[id++] = { title: t, pageprops: { page_image_free: 'Dis.jpg', disambiguation: '' }, coordinates: [{ lat: s.lat, lon: s.lng }] };
      else pages[-id] = { title: t, missing: '' }, id++;
    }
    r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ query: { pages } }) }); });
  await p.route(/commons\.wikimedia\.org\/w\/api\.php/, r => { const u = new URL(r.request().url()); const t = u.searchParams.get('titles');
    if (t){ log.push('file:' + t); return r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ query: { pages: { 1: ii(t, 1200, 1500, 'CC BY-SA 4.0', 1) } } }) }); }
    const co = u.searchParams.get('ggscoord'); const s = KY.find(x => Math.abs(x.lat - parseFloat(co)) < 1e-4); log.push('near:' + (s && s.name_ja));
    const pages = { 1: ii('File:Random street.jpg', 2000, 1200, 'CC BY-SA 4.0', 2) };
    if (s && s.name_ja === '八坂神社') pages[2] = Object.assign(ii('File:八坂神社 西楼門.jpg', 2000, 1200, 'CC BY 4.0', 3), { index: 1 });
    r.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ query: { pages } }) }); });
  await p.route(/upload\.wikimedia\.org/, r => { const h = +(r.request().url().match(/F(\d)\.jpg$/) || [0, 0])[1]; r.fulfill({ status: 200, contentType: 'image/jpeg', body: jpg[h] }); });
  await p.route(/cyberjapandata|openstreetmap|maps\.google|google\.com/, r => r.abort());
  await p.goto(url + '#kyoto/spot'); await p.waitForTimeout(500);
  for (let i = 0; i < 6; i++){ await p.evaluate(() => scrollBy(0, 500)); await p.waitForTimeout(500); }
  await p.waitForTimeout(1500);
  const R = await p.evaluate(() => [...document.querySelectorAll('.gcard')].slice(0, 14).map(c => (c.querySelector('.tx b') || {}).textContent + ':' + ((c.querySelector('.lpimg.on') || {}).src || '-').replace(/.*\/960px-/, '').replace(/.*\/(\d+)px-/, '')));
  console.log(R.join('\n')); console.log(log.slice(0, 30).join('\n')); console.log(errs); await b.close();
})();
