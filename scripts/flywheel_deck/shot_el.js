const { chromium } = require('playwright');
const [,,FILE,OUT,SEL]=process.argv;
(async()=>{ const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1300,height:900},deviceScaleFactor:2});
 await p.goto('file://'+FILE); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(400);
 await p.locator(SEL||'body').first().screenshot({path:OUT}); await b.close(); })();
