// 설계도(마크다운)를 보기 좋은 HTML · PDF 로 만든다. 흐름 그림(mermaid)은 그림(SVG)으로 바꿔 넣어 인터넷 없이 보인다.
// 준비 : npm pack marked@12.0.2 mermaid@10.9.1 → 압축을 풀어 두 폴더를 넘긴다 (node · playwright 필요)
// 쓰는 법 : node fortune/tools/render_doc.js <문서.md> <marked 폴더> <mermaid 폴더>
//          → 같은 자리에 <문서>.html · <문서>.pdf
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [, , MD, MARKED, MERMAID] = process.argv;
const FONT = path.join(__dirname, '..', 'assets', 'fonts', 'serif-ko.woff2');

const CSS = `
@font-face { font-family: "DocSerif"; src: url(data:font/woff2;base64,${fs.readFileSync(FONT).toString('base64')}) format("woff2"); font-weight: 400 900; }
:root { --ink: #1c1730; --sub: #4b4560; --line: #e2d8c3; --soft: #faf6ec; --gold: #b8913f; --night: #22165c; --pur5: #efeafb; }
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: var(--ink); font-family: "Pretendard", -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans CJK KR", sans-serif; font-size: 14px; line-height: 1.7; word-break: keep-all; overflow-wrap: anywhere; }
.page { max-width: 880px; margin: 0 auto; padding: 40px max(20px, env(safe-area-inset-left, 0px)) 64px; }
.cover { margin: 0 0 28px; padding: 30px 32px; border-radius: 18px; color: #fff; background: radial-gradient(120% 120% at 50% 0%, #3d2793, #22165c 55%, #120a35); }
.cover .k { font-size: 12px; font-weight: 700; letter-spacing: .2em; color: #e8c77a; }
.cover h1 { margin: 6px 0 4px; font-family: "DocSerif", serif; font-size: 30px; line-height: 1.3; border: 0; padding: 0; color: #fff; }
.cover p { margin: 0; color: #ddd5ff; font-size: 13.5px; }
h1 { font-family: "DocSerif", serif; font-size: 26px; }
h2 { margin: 36px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--line); font-family: "DocSerif", serif; font-size: 21px; color: var(--night); break-after: avoid; }
h3 { margin: 24px 0 8px; font-family: "DocSerif", serif; font-size: 16.5px; color: var(--ink); break-after: avoid; }
p, li { color: var(--ink); }
blockquote { margin: 12px 0; padding: 10px 16px; border-radius: 10px; background: var(--pur5); color: var(--sub); }
blockquote p { margin: 0; color: var(--sub); }
table { width: 100%; border-collapse: collapse; margin: 10px 0 16px; font-size: 13px; break-inside: auto; }
th { background: var(--soft); text-align: left; font-weight: 700; color: var(--sub); }
th, td { padding: 7px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr { break-inside: avoid; }
code { font-family: "D2Coding", "Consolas", "SF Mono", monospace; font-size: 12.5px; background: #f3efe5; padding: 1px 5px; border-radius: 5px; }
pre { background: #1d1546; color: #f1ebff; padding: 14px 16px; border-radius: 12px; overflow-x: auto; white-space: pre-wrap; font-size: 12px; line-height: 1.55; break-inside: avoid; }
pre code { background: none; padding: 0; color: inherit; }
.mermaid { margin: 14px 0 18px; padding: 14px; border: 1px solid var(--line); border-radius: 14px; background: #fffdf8; text-align: center; break-inside: avoid; }
.mermaid svg { max-width: 100%; height: auto; }
.foot { margin-top: 40px; font-size: 12px; color: var(--sub); text-align: center; }
@page { size: A4; margin: 14mm 12mm; }
@media print { .page { padding: 0; } .cover { -webkit-print-color-adjust: exact; print-color-adjust: exact; } pre, th, .mermaid { -webkit-print-color-adjust: exact; print-color-adjust: exact; } }
`;

(async () => {
  let md = fs.readFileSync(MD, 'utf8').replace(/^---\n[\s\S]*?\n---\n/, '');
  const m = md.match(/^# (.+)\n/m); const title = m ? m[1] : path.basename(MD);
  md = md.replace(/^# .+\n/m, '');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1200 } });
  await p.setContent(`<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title}</title><style>${CSS}</style></head>` +
    `<body><main class="page"><header class="cover"><div class="k">MeAI · 세일즈혁신TF</div><h1>${title}</h1><p>사내 웹서버 · 폐쇄망 탑재용 개발 설계도 · 2026-10-29</p></header><article id="doc"></article>` +
    `<p class="foot">오늘의 운세 v2 · 재미로 보는 콘텐츠이며 보험 권유 · 의사결정 근거로 쓰지 않습니다.</p></main></body></html>`);
  await p.addScriptTag({ path: path.join(MARKED, 'marked.min.js') });
  await p.addScriptTag({ path: path.join(MERMAID, 'dist', 'mermaid.min.js') });
  await p.evaluate(async (src) => {
    const r = new marked.Renderer(); const code = r.code.bind(r);
    r.code = function (c, lang) { const t = typeof c === 'object' ? c.text : c, l = typeof c === 'object' ? c.lang : lang;
      if (l === 'mermaid') { const d = document.createElement('div'); d.textContent = t; return '<div class="mermaid">' + d.innerHTML + '</div>'; } return code(c, lang); };
    document.getElementById('doc').innerHTML = marked.parse(src, { renderer: r, gfm: true });
    mermaid.initialize({ startOnLoad: false, theme: 'base', securityLevel: 'strict', flowchart: { htmlLabels: false, curve: 'basis' },
      themeVariables: { fontFamily: '"Pretendard", "Malgun Gothic", "Noto Sans CJK KR", sans-serif', fontSize: '14px', primaryColor: '#f3eefc', primaryBorderColor: '#4b2fb0', primaryTextColor: '#1c1730', lineColor: '#8a7a55', secondaryColor: '#fbf1d6', tertiaryColor: '#fffdf8' } });
    await mermaid.run({ querySelector: '.mermaid' });
    document.querySelectorAll('script').forEach(s => s.remove());
  }, md);
  const errs = await p.evaluate(() => [...document.querySelectorAll('.mermaid')].filter(d => !d.querySelector('svg') || /Syntax error/.test(d.textContent)).length);
  const html = '<!DOCTYPE html>\n' + await p.evaluate(() => document.documentElement.outerHTML);
  const base = MD.replace(/\.md$/, '');
  fs.writeFileSync(base + '.html', html);
  await p.emulateMedia({ media: 'print' });
  await p.pdf({ path: base + '.pdf', format: 'A4', printBackground: true, margin: { top: '14mm', bottom: '14mm', left: '12mm', right: '12mm' },
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:8px;color:#888;text-align:center">오늘의 운세 v2 설계도 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  console.log('그림', await p.evaluate(() => document.querySelectorAll('.mermaid svg').length), '개 · 그림 오류', errs, '·', path.basename(base) + '.html', (fs.statSync(base + '.html').size / 1024).toFixed(0) + 'KB ·', path.basename(base) + '.pdf', (fs.statSync(base + '.pdf').size / 1024).toFixed(0) + 'KB');
  await b.close();
  process.exit(errs ? 1 : 0);
})();
