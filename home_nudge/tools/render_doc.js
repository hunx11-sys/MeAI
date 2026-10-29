// 설계도(마크다운)를 보기 좋은 HTML · PDF 로 만든다. 흐름 그림(mermaid)은 그림(SVG)으로 바꿔 넣어 인터넷 없이 보인다.
// 준비 : npm pack marked@12.0.2 mermaid@10.9.1 → 압축을 풀어 두 폴더를 넘긴다 (node · playwright 필요)
// 쓰는 법 : node home_nudge/tools/render_doc.js <문서.md> <marked 폴더> <mermaid 폴더>
//          → 같은 자리에 <문서>.html · <문서>.pdf   (fortune/tools/render_doc.js 를 MeAI 홈 색으로 바꾼 것)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const [, , MD, MARKED, MERMAID] = process.argv;
const FONT = path.join(__dirname, '..', '..', 'assets', 'pretendard-subset.woff2');
const fontFace = fs.existsSync(FONT) ? `@font-face { font-family: "Pretendard"; src: url(data:font/woff2;base64,${fs.readFileSync(FONT).toString('base64')}) format("woff2"); font-weight: 100 900; }` : '';

const CSS = `
${fontFace}
:root { --ink: #191b1f; --sub: #4a4c50; --line: #e7e9ed; --soft: #f8f9fa; --red: #e0282f; --red5: #fceaea; --night: #1e1f21; --gold: #f5b301; }
* { box-sizing: border-box; }
body { margin: 0; background: #fff; color: var(--ink); font-family: "Pretendard", -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans CJK KR", sans-serif; font-size: 13.5px; line-height: 1.7; word-break: keep-all; overflow-wrap: anywhere; }
.page { max-width: 920px; margin: 0 auto; padding: 40px max(20px, env(safe-area-inset-left, 0px)) 64px; }
.cover { margin: 0 0 28px; padding: 30px 32px; border-radius: 18px; color: #fff; background: var(--night); position: relative; overflow: hidden; }
.cover::after { content: ""; position: absolute; right: -40px; top: -40px; width: 180px; height: 180px; border-radius: 50%; border: 18px solid rgba(224, 40, 47, .55); }
.cover .k { font-size: 12px; font-weight: 700; letter-spacing: .16em; color: #f5b8bb; }
.cover h1 { margin: 6px 0 4px; font-size: 28px; line-height: 1.3; border: 0; padding: 0; color: #fff; letter-spacing: -0.02em; }
.cover p { margin: 0; color: #d5d8dd; font-size: 13px; }
h2 { margin: 36px 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--line); font-size: 20px; color: var(--ink); break-after: avoid; letter-spacing: -0.02em; }
h2::before { content: ""; display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--red); margin: 0 8px 3px 0; }
h3 { margin: 24px 0 8px; font-size: 15.5px; color: var(--ink); break-after: avoid; }
p, li { color: var(--ink); }
blockquote { margin: 12px 0; padding: 10px 16px; border-radius: 10px; background: var(--soft); color: var(--sub); }
blockquote p { margin: 0; color: var(--sub); }
table { width: 100%; border-collapse: collapse; margin: 10px 0 16px; font-size: 12.3px; break-inside: auto; }
th { background: var(--soft); text-align: left; font-weight: 700; color: var(--sub); }
th, td { padding: 6px 9px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr { break-inside: avoid; }
code { font-family: "D2Coding", "Consolas", "SF Mono", monospace; font-size: 11.8px; background: #f2f3f5; padding: 1px 5px; border-radius: 5px; }
pre { background: var(--night); color: #f2f3f5; padding: 14px 16px; border-radius: 12px; overflow-x: auto; white-space: pre; font-size: 11px; line-height: 1.5; break-inside: avoid; }
pre code { background: none; padding: 0; color: inherit; }
.mermaid { margin: 14px 0 18px; padding: 14px; border: 1px solid var(--line); border-radius: 14px; background: #fff; text-align: center; break-inside: avoid; }
.mermaid svg { max-width: 100%; height: auto; }
.foot { margin-top: 40px; font-size: 12px; color: var(--sub); text-align: center; }
img { max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 10px; display: block; margin: 10px auto; break-inside: avoid; }
.shots { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 12px 0; }
.shots figure { margin: 0; break-inside: avoid; }
.shots figure.wide { grid-column: 1 / -1; }
.shots img { margin: 0 auto; max-height: 520px; width: auto; }
.shots figcaption { text-align: center; font-size: 11.5px; color: var(--sub); margin-top: 4px; }
@page { size: A4; margin: 14mm 12mm; }
@media print { .page { padding: 0; } .cover, pre, th, .mermaid { -webkit-print-color-adjust: exact; print-color-adjust: exact; } pre { white-space: pre-wrap; } }
`;

(async () => {
  let md = fs.readFileSync(MD, 'utf8').replace(/^---\n[\s\S]*?\n---\n/, '');
  const m = md.match(/^# (.+)\n/m); const title = m ? m[1] : path.basename(MD);
  md = md.replace(/^# .+\n/m, '');
  // 문서 옆 img/ 그림을 파일 안에 넣는다 (HTML 한 파일 · PDF 에서 그대로 보이게)
  const dir = path.dirname(MD), uri = (f) => 'data:image/' + (f.endsWith('.png') ? 'png' : 'jpeg') + ';base64,' + fs.readFileSync(path.join(dir, f)).toString('base64');
  md = md.replace(/\]\((img\/[^)]+)\)/g, (m, f) => '](' + uri(f) + ')').replace(/src="(img\/[^"]+)"/g, (m, f) => 'src="' + uri(f) + '"');
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1000, height: 1200 } });
  await p.setContent(`<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${title}</title><style>${CSS}</style></head>` +
    `<body><main class="page"><header class="cover"><div class="k">MeAI 홈 · 세일즈혁신TF</div><h1>${title}</h1><p>사내 개발 설계도 · 2026-10-29 · 내부 검토용 · 화면 · 수치는 확정 전 예시</p></header><article id="doc"></article>` +
    `<p class="foot">MeAI 홈 넛지 플레이 v5 · 보상 · 경품 · 명칭은 준법 · 재무 확인 전 예시입니다.</p></main></body></html>`);
  await p.addScriptTag({ path: path.join(MARKED, 'marked.min.js') });
  await p.addScriptTag({ path: path.join(MERMAID, 'dist', 'mermaid.min.js') });
  await p.evaluate(async (src) => {
    const r = new marked.Renderer(); const code = r.code.bind(r);
    r.code = function (c, lang) { const t = typeof c === 'object' ? c.text : c, l = typeof c === 'object' ? c.lang : lang;
      if (l === 'mermaid') { const d = document.createElement('div'); d.textContent = t; return '<div class="mermaid">' + d.innerHTML + '</div>'; } return code(c, lang); };
    document.getElementById('doc').innerHTML = marked.parse(src, { renderer: r, gfm: true });
    mermaid.initialize({ startOnLoad: false, theme: 'base', securityLevel: 'strict', flowchart: { htmlLabels: false, curve: 'basis' },
      themeVariables: { fontFamily: '"Pretendard", "Malgun Gothic", "Noto Sans CJK KR", sans-serif', fontSize: '13px', primaryColor: '#fceaea', primaryBorderColor: '#e0282f', primaryTextColor: '#191b1f', lineColor: '#61646b', secondaryColor: '#f2f3f5', tertiaryColor: '#ffffff' } });
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
    footerTemplate: '<div style="width:100%;font-size:8px;color:#888;text-align:center">MeAI 홈 넛지 플레이 v5 설계도 · <span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  console.log('그림', await p.evaluate(() => document.querySelectorAll('.mermaid svg').length), '개 · 그림 오류', errs, '·', path.basename(base) + '.html', (fs.statSync(base + '.html').size / 1024).toFixed(0) + 'KB ·', path.basename(base) + '.pdf', (fs.statSync(base + '.pdf').size / 1024).toFixed(0) + 'KB');
  await b.close();
  process.exit(errs ? 1 : 0);
})();
