// 사용 : node render.js <그림.json> <출력.png> [표시폭px=240]
// 그림.json = { "key": "<svg ...>", ... } 를 표시폭과 그 절반 크기로 함께 그려 견본 시트를 만든다(viewBox 비율 유지).
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
(async () => {
  const [src, out, wStr] = process.argv.slice(2);
  const W = Number(wStr || 240);
  const icons = JSON.parse(fs.readFileSync(src, 'utf8'));
  const cells = Object.entries(icons).map(([k, svg]) => `<div class="c"><div class="big" style="width:${W}px">${svg}</div><div class="sm" style="width:${Math.round(W / 2)}px">${svg}</div><b>${k}</b><i>${Buffer.byteLength(svg)}B</i></div>`).join('');
  const html = `<!doctype html><meta charset="utf-8"><style>body{margin:0;padding:16px;background:#FFFCFA;font:12px sans-serif;display:flex;flex-wrap:wrap;gap:14px;align-items:flex-start}
  .c{border:1px solid #EFE3DD;border-radius:14px;padding:10px;background:#fff;display:flex;flex-direction:column;gap:6px}
  .big,.sm{border-radius:16px;overflow:hidden;background:#F8F1ED;line-height:0}.big svg,.sm svg{width:100%;height:auto;display:block}
  i{color:#999;font-style:normal}</style>${cells}`;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: Math.max(700, W * 3 + 120), height: 400 }, deviceScaleFactor: 2 });
  await p.setContent(html); await p.screenshot({ path: out, fullPage: true }); await b.close();
  console.log('saved', out);
})();
