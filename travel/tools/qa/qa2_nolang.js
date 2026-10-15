// 상호작용 점검 : 칩 누를 때 스크롤 유지, 뒤로가기, 일차 전환, 체크 키, 언어 메뉴, 오류 0
const { chromium, devices } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path');
const [,, html, dest] = process.argv;
(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
  const ctx = await browser.newContext({ ...devices['iPhone 13'], locale: 'ko-KR' });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await page.waitForTimeout(600);
  const R = {};
  // 1. 테마 칩 누르면 스크롤 유지
  await page.evaluate(() => document.querySelector('.filters').scrollIntoView());
  const y0 = await page.evaluate(() => window.scrollY);
  await page.click('.filters .chip:nth-child(2)'); await page.waitForTimeout(200);
  R.scrollKeptOnTag = Math.abs((await page.evaluate(() => window.scrollY)) - y0) < 5;
  await page.click('.filters .chip:nth-child(1)'); await page.waitForTimeout(200);
  // 2. 카드 열기 → 뒤로 → 홈
  await page.click(`#card-${dest}`); await page.waitForTimeout(600);
  R.openedDest = await page.evaluate(() => !!document.querySelector('.dhero'));
  R.hashAfterOpen = await page.evaluate(() => location.hash);
  // 3. 박 수 버튼 누르면 스크롤 유지
  await page.evaluate(() => document.querySelector('.pick').scrollIntoView());
  const y1 = await page.evaluate(() => window.scrollY);
  const nbtn = await page.$$('.nseg button'); if (nbtn[1]) { await nbtn[1].click(); await page.waitForTimeout(300); }
  R.scrollKeptOnNights = Math.abs((await page.evaluate(() => window.scrollY)) - y1) < 40;
  // 4. 일차 타일 → dayhead 가 상단바 밑에 가리지 않는지
  const tiles = await page.$$('.tile'); if (tiles[1]) { await tiles[1].click(); await page.waitForTimeout(900); }
  R.dayheadVisible = await page.evaluate(() => { const t = document.querySelector('.topbar').getBoundingClientRect().bottom; const d = document.querySelector('.dayhead h2').getBoundingClientRect().top; return d >= t - 2; });
  // 5. 체크 → 박 수 바꾸면 다른 줄로 옮겨가지 않음
  await page.evaluate(() => { const d = document.getElementById('acc-check'); d.open = true; });
  const li = await page.$('.checks li'); const txt = li ? await li.textContent() : '';
  if (li) await li.click();
  const nbtn2 = await page.$$('.nseg button'); if (nbtn2[0]) { await nbtn2[0].click(); await page.waitForTimeout(300); }
  await page.evaluate(() => { const d = document.getElementById('acc-check'); if (d) d.open = true; });
  R.checkStays = await page.evaluate(t => { const done = [...document.querySelectorAll('.checks li.done')].map(x => x.textContent); return done.length === 0 || done.includes(t); }, txt);
  // 6. 언어 메뉴
  R.langBtnHidden = !(await page.$("[data-act=lang]"));
  
  
  // 7. 뒤로 → 홈, 한 번 더 뒤로 → 페이지 밖으로 나가지 않음(해시 home)
  await page.click('[data-act=back]'); await page.waitForTimeout(500);
  R.backToHome = await page.evaluate(() => !!document.querySelector('.hero'));
  R.hashAfterBack = await page.evaluate(() => location.hash);
  // 8. 해시로 바로 열고 뒤로 → 홈(밖으로 안 나감)
  await page.goto('file://' + path.resolve(html) + '#' + dest, { waitUntil: 'load' }); await page.waitForTimeout(500);
  await page.click('[data-act=back]'); await page.waitForTimeout(400);
  R.directBackHome = await page.evaluate(() => !!document.querySelector('.hero') && location.href.includes(document.title ? '' : ''));
  // 9. 이상한 해시
  await page.goto('file://' + path.resolve(html) + '#constructor', { waitUntil: 'load' }); await page.waitForTimeout(300);
  R.protoHashSafe = await page.evaluate(() => !!document.querySelector('.hero'));
  // 10. 금액 표기
  await page.goto('file://' + path.resolve(html) + '#' + dest, { waitUntil: 'load' }); await page.waitForTimeout(500);
  R.bottomAmount = await page.evaluate(() => document.querySelector('.bottombar .v').innerText.replace(/\n/g, ' / '));
  R.hScroll = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  R.errors = errors;
  console.log(JSON.stringify(R, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
