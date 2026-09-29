// 공용 캡처 도우미. 사용: import { open, shot, hideOverlays, SRC } from './cap.mjs'
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import fs from 'fs';
import path from 'path';
export const SRC = process.env.CAP_SRC || ("file://" + new URL('../prototype/index_260929_v2.html', import.meta.url).pathname);
export const ROUTES = {
  gate010:'#/mg-gate-010', gate020:'#/mg-gate-020', find010:'#/mg-find-010', board010:'#/mg-board-010',
  tags:'#/mg-tag-legend', term_pc:'#/term-glossary-pc', term_mo:'#/term-glossary-m', mode_pc:'#/analysis-mode-pc', mode_mo:'#/analysis-mode-m',
};
const HIDE_CSS = `#root > a.fixed, #root > div.fixed { display:none !important; }`;
export async function hideOverlays(page){ await page.addStyleTag({content: HIDE_CSS}); }
// route: '#/mg-gate-010' 등. 반환 {browser, page}. 프로토타입 전용 컨트롤(← 목록, 폰트 확대)은 자동으로 숨김.
export async function open(route, {width=1440, height=900, dsf=2, mobile=false, settle=1500}={}){
  const browser = await chromium.launch();
  const ctx = await browser.newContext({viewport:{width,height}, deviceScaleFactor:dsf, isMobile:mobile, hasTouch:mobile, locale:'ko-KR'});
  const page = await ctx.newPage();
  await page.goto(SRC + route, {waitUntil:'load'});
  await page.waitForTimeout(settle);
  await hideOverlays(page);
  await page.waitForTimeout(200);
  return {browser, page};
}
// 캡처. opts: {fullPage:true} | {clip:{x,y,width,height}} | {selector:'css', pad:8}
export async function shot(page, file, opts={}){
  fs.mkdirSync(path.dirname(file), {recursive:true});
  if (opts.selector){
    const el = page.locator(opts.selector).first();
    await el.scrollIntoViewIfNeeded();
    const box = await el.boundingBox();
    if (!box) throw new Error('no box for '+opts.selector);
    const pad = opts.pad ?? 8;
    const vp = page.viewportSize();
    const clip = {x:Math.max(0,box.x-pad), y:Math.max(0,box.y-pad), width:Math.min(vp.width, box.width+pad*2), height:box.height+pad*2};
    await page.screenshot({path:file, clip, fullPage: opts.fullPage ?? false});
  } else {
    await page.screenshot({path:file, fullPage: !!opts.fullPage, clip: opts.clip});
  }
  return file;
}
// 요소를 텍스트로 찾을 때: page.getByText('정확한 문구', {exact:true}).first()
