package meai.sp;

/**
 * 파이썬 판의 긴 글자 상수(CSS · JS) — golden/gen_consts.py 가 파이썬 판에서 읽어 그대로 적은 파일이다.
 * 손으로 고치지 않는다(파이썬 판을 고친 뒤 스크립트를 다시 돌린다).
 */
public final class Txt {
    private Txt() {}

    /** ga_proposal.CSS */
    public static final String GP_CSS = "\n"
            + "@page{size:A4;margin:0} *{box-sizing:border-box} body{margin:0;font-family:\"Pretendard\",\"GANG\",\"Malgun Gothic\",sans-serif;color:#111;letter-spacing:-.2pt}\n"
            + ".page{width:210mm;height:297mm;padding:11mm 12mm 14mm 12mm;page-break-after:always;position:relative;overflow:hidden;background:#fff}\n"
            + "/* 쪽 머리 */\n"
            + ".ph{display:flex;align-items:center;gap:7pt;height:9mm;margin-bottom:5mm} .logo{display:inline-flex;align-items:baseline;gap:3pt;white-space:nowrap} .logo b{font-size:17pt;font-weight:800;color:#F23A2B;letter-spacing:-1.2pt;font-family:\"Pretendard\",Arial,sans-serif} .logo span{font-size:11.5pt;font-weight:700;color:#111}\n"
            + "img.logo{height:7.5mm} .ph .sp{font-size:15pt;font-weight:800;color:#F23A2B;margin-left:6pt;letter-spacing:-.6pt} .ph .bar{width:1px;height:14pt;background:#C9C9C9;margin:0 3pt}\n"
            + ".ph .ttl{font-size:15.5pt;font-weight:800;color:#111;letter-spacing:-.6pt} .ph .ttl small{font-size:9pt;font-weight:600;color:#777;margin-left:4pt}\n"
            + ".ph .warn{margin-left:auto;display:flex;gap:4pt;align-items:center;font-size:6.6pt;color:#666;line-height:1.3;text-align:left}\n"
            + ".ph .warn i,.cv-note i{display:inline-block;width:10pt;height:10pt;border-radius:50%;background:#F23A2B;color:#fff;font-style:normal;font-weight:900;font-size:7.5pt;text-align:center;line-height:10pt;flex:0 0 auto}\n"
            + "/* 정보표 */\n"
            + ".dno{text-align:right;font-size:7.5pt;color:#444;margin:0 0 2pt} .info{width:100%;border-collapse:collapse;border-top:1.5px solid #F23A2B;margin-bottom:4mm} .info th,.info td{height:9.5mm;border-bottom:1px solid #E6E6E6;padding:0 9pt;font-size:10.5pt;text-align:left;white-space:nowrap}\n"
            + ".info th{background:#F4F4F4;color:#555;font-weight:500;width:18%;letter-spacing:.3pt} .info td{font-weight:500} .info td b.prem{color:#F23A2B;font-size:14.5pt;font-weight:700} .info td b.prem i{font-style:normal;font-size:9pt;color:#111;font-weight:500;margin-left:1pt}\n"
            + ".info.p1 th,.info.p1 td{height:9mm;font-size:10pt} .info td.pn{white-space:normal;word-break:keep-all;line-height:1.2;font-size:9.6pt;padding-top:2pt;padding-bottom:2pt} .cover .info td.pn{font-size:10.5pt}\n"
            + "/* 제목 탭 */\n"
            + ".sec{border-bottom:2px solid #DADADA;margin:5.5mm 0 0;height:8.6mm;position:relative} .sec .tab{position:absolute;left:0;bottom:-2px;background:#F23A2B;color:#fff;border-radius:3.5pt 3.5pt 0 0;padding:0 11pt;height:8.6mm;line-height:8.6mm;font-size:12.5pt;font-weight:500;letter-spacing:-.4pt;white-space:nowrap}\n"
            + ".sec .tab b{font-weight:800} .sec .tab small{font-size:8.5pt;font-weight:500;margin-left:2pt} .roomy .sec{margin-top:7mm}\n"
            + "/* 표 공통 */\n"
            + "table{border-collapse:collapse;width:100%;table-layout:fixed} th,td{font-size:9.6pt;padding:0 6pt;height:8.3mm;border-bottom:1px solid #E6E6E6;white-space:nowrap;overflow:hidden}\n"
            + "th{background:#F4F4F4;font-weight:500;color:#444;text-align:center;height:8mm} td{text-align:center} .g th:first-child{background:#F4F4F4} .g th small{font-size:7pt;color:#777}\n"
            + ".lab{text-align:left;color:#333;white-space:nowrap;font-size:9.4pt;padding-left:12pt} tr.first .lab{color:#F23A2B} tr.first b.v{color:#F23A2B}\n"
            + ".g tbody b.v{color:#111} .g td small.pre{font-size:7.6pt;color:#555;margin-right:4pt;vertical-align:1pt}\n"
            + ".roomy th,.roomy td{height:9.6mm} .roomy .eight th{height:8.8mm} .roomy .eight td{height:9.6mm}\n"
            + ".kv th{height:8.6mm;font-size:10.5pt} .kv td{width:25%;text-align:left;border-right:1px solid #ECECEC;height:8.9mm;padding:0 7pt 0 9pt} .kv td:last-child{border-right:0} .kv td.e{border-right:0}\n"
            + ".kv td span{display:inline-block;max-width:58%;color:#222;font-size:9.6pt;white-space:normal;word-break:keep-all;line-height:1.1;vertical-align:middle;font-weight:500} .kv td span small{font-size:8.2pt;letter-spacing:-.5pt} .kv td b.v,.kv td .na,.kv td .txt{float:right;line-height:8.9mm}\n"
            + "b.v{font-weight:700;color:#F23A2B;font-size:12pt;white-space:nowrap;letter-spacing:-.4pt} b.v i{font-style:normal;font-weight:500;font-size:8.6pt;color:#111;margin-left:1pt;letter-spacing:0}\n"
            + "b.v.z{color:#9A9A9A} b.v.big{font-size:19pt} b.v.big i{font-size:10pt}\n"
            + "small{font-size:7.5pt;color:#777} .na{color:#C4C4C4;font-size:9.6pt;font-weight:500} .txt{font-weight:800;color:#F23A2B;font-size:10pt}\n"
            + ".two{display:flex;gap:5mm;align-items:flex-start} .two .l{flex:1} .two .r{width:40%} .r2 .sec{margin-top:5.5mm}\n"
            + "/* 주요수술 12칸 */\n"
            + ".dz td{text-align:center;vertical-align:top;border:1px solid #E6E6E6;width:25%;padding:7pt 3pt 6pt;height:auto;white-space:normal;background:#fff} .dz tr:nth-child(odd) td{background:#F7F7F7}\n"
            + ".dz td b{display:block;font-size:10.5pt;font-weight:600;color:#222} .dz td em{display:block;font-style:normal;color:#888;font-size:7.2pt;margin:1pt 0 7pt} .dz .val{height:8mm;line-height:8mm} .dz b.v{display:inline;color:#111;font-size:14pt} .dz small.side{font-size:6.8pt;color:#999;margin-right:3pt}\n"
            + "/* 간병인 */\n"
            + ".care th{text-align:left;background:#F4F4F4;height:8mm;font-size:9.6pt;color:#333;font-weight:500;padding-left:9pt} .care th span{color:#777;margin-left:1pt} .care td{text-align:left;height:7.6mm;font-size:9.4pt;padding-left:9pt;color:#222;font-weight:500} .care td:last-child{text-align:right;padding-right:6pt} .care td small{font-size:7.4pt;color:#888}\n"
            + ".care b.v{color:#111;font-size:10.5pt} .care small.dem{display:block;color:#F23A2B;font-weight:700;font-size:6.4pt;text-align:right;line-height:1}\n"
            + "/* 2·3쪽 */\n"
            + ".eight th{font-size:9pt;white-space:nowrap;height:8mm;padding:0 2pt;background:#F4F4F4} .eight th small{font-size:6pt;color:#777} .eight td{padding:0 2pt} .eight b.v{color:#111;font-size:11pt} .three th,.three td{width:33.3%}\n"
            + ".dxbig{display:flex;gap:4pt;margin-top:0} .dxbig div{flex:1;background:#FBF1F0;padding:7pt 11pt 6pt;min-height:19mm;position:relative}\n"
            + ".dxbig span{font-weight:600;font-size:13pt;color:#222} .dxbig em{font-style:normal;color:#666;font-size:7.6pt;display:block;margin-top:3pt} .dxbig b.v{position:absolute;right:11pt;top:6pt} .dxbig .na{position:absolute;right:11pt;top:8pt;font-size:11pt}\n"
            + ".g.one th{height:9.2mm} .g.sev th{font-size:9pt}\n"
            + ".ft{position:absolute;left:12mm;right:12mm;bottom:7mm;font-size:7pt;color:#555;border-top:1px solid #DADADA;padding-top:5pt;display:flex;justify-content:space-between;align-items:baseline}\n"
            + ".ft .fr span{margin-left:8pt;padding-left:8pt;border-left:1px solid #D0D0D0;font-weight:600;color:#333} .ft .fr span:first-child{border:0} .ft .fr em{font-style:normal;color:#BBB;font-size:5.5pt;margin-left:8pt}\n"
            + "/* 표지 */\n"
            + ".cover{padding:0} .cv-tag{position:absolute;left:12mm;top:35mm;font-size:19pt;font-weight:300;color:#222;letter-spacing:-.6pt} .cv-title{position:absolute;left:11mm;top:45mm;margin:0;font-size:50pt;font-weight:800;letter-spacing:-2.8pt;color:#111;white-space:nowrap} .cv-title span{color:#F23A2B}\n"
            + ".cover .info{position:absolute;left:12mm;top:74mm;width:186mm} .cover .info th,.cover .info td{height:12mm;font-size:11.5pt} .cover .info th{width:18%} .cover .info td b.prem{font-size:17pt}\n"
            + ".cv-note{position:absolute;left:12mm;top:115mm;display:flex;gap:6pt;align-items:flex-start;font-size:7.6pt;color:#555;line-height:1.45} .cv-note i{margin-top:2pt}\n"
            + ".cv-warn{position:absolute;left:12mm;top:132mm;color:#F23A2B;font-weight:700;font-size:8pt}\n"
            + ".cv-contact{position:absolute;left:12mm;bottom:17mm;display:grid;grid-template-columns:auto auto;gap:4pt 24pt;font-size:11pt} .cv-contact em{font-style:normal;color:#666;margin-right:10pt;letter-spacing:1pt;display:inline-block;min-width:38pt} .cv-contact b{font-weight:600;color:#111}\n"
            + ".logo.cv-logo{position:absolute;right:12mm;bottom:18mm} .logo.cv-logo b{font-size:27pt} .logo.cv-logo span{font-size:17pt;font-weight:700} img.logo.cv-logo{height:10mm}\n"
            + "/* 표지1 : 연한 붉은 도형(GA 가안을 CSS 로 옮긴 것) */\n"
            + ".art1{position:absolute;inset:0;overflow:hidden;z-index:0} .art1 .s{position:absolute;border-radius:16mm;background:linear-gradient(135deg,rgba(255,225,222,.55),rgba(255,150,140,.28));filter:blur(.3mm);mix-blend-mode:multiply}\n"
            + ".art1 .a{width:150mm;height:60mm;left:70mm;top:170mm;transform:rotate(-32deg)} .art1 .b{width:140mm;height:55mm;left:95mm;top:120mm;transform:rotate(-32deg);opacity:.8} .art1 .c{width:120mm;height:48mm;left:120mm;top:222mm;transform:rotate(-32deg);opacity:.7} .art1 .d{width:90mm;height:36mm;left:140mm;top:88mm;transform:rotate(-32deg);opacity:.55}\n"
            + ".cover>*:not(.art1):not(.art1img):not(.art2):not(.art2css){z-index:1} svg.art1{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0;overflow:visible} img.art1img{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0}\n"
            + "/* 표지2 : 방패·하트 일러스트 — 원본 그림(ga_assets/cover_art2.png)이 없으면 CSS 로 비슷하게 */\n"
            + "img.art2{position:absolute;left:55mm;top:130mm;width:140mm} .art2css{position:absolute;left:0;top:0;width:210mm;height:297mm;z-index:0}\n"
            + ".art2css .shield{position:absolute;left:100mm;top:150mm;width:72mm;height:84mm;background:linear-gradient(160deg,#fff,#EDEDED);border-radius:36mm 36mm 50% 50%/30mm 30mm 60% 60%;box-shadow:0 8mm 14mm rgba(0,0,0,.08),inset 0 -3mm 6mm rgba(0,0,0,.05);transform:rotate(-8deg)}\n"
            + ".art2css .heart{position:absolute;left:21mm;top:22mm;width:30mm;height:30mm;background:#F23A2B;transform:rotate(-45deg);border-radius:0 0 2mm 0;box-shadow:inset -3mm -3mm 6mm rgba(0,0,0,.12)} .art2css .heart:before,.art2css .heart:after{content:\"\";position:absolute;width:30mm;height:30mm;background:#F23A2B;border-radius:50%} .art2css .heart:before{left:-15mm;top:0} .art2css .heart:after{left:0;top:-15mm}\n"
            + ".art2css .cross{position:absolute;left:66mm;top:190mm;width:40mm;height:40mm;background:rgba(255,205,200,.6);border-radius:8mm;transform:rotate(-10deg)} .art2css .cross i{position:absolute;left:14mm;top:6mm;width:12mm;height:28mm;background:#F23A2B;border-radius:2mm} .art2css .cross i+i{transform:rotate(90deg)}\n"
            + ".art2css .doc{position:absolute;left:150mm;top:200mm;width:36mm;height:40mm;background:rgba(255,205,200,.6);border-radius:7mm;transform:rotate(8deg)} .art2css .doc i{position:absolute;left:8mm;width:20mm;height:3mm;background:#F8B8B2;border-radius:2mm} .art2css .doc i:nth-child(1){top:11mm} .art2css .doc i:nth-child(2){top:18mm} .art2css .doc i:nth-child(3){top:25mm;width:13mm}\n"
            + ".art2css .ball{position:absolute;border-radius:50%;box-shadow:inset -2mm -2mm 5mm rgba(0,0,0,.15),0 3mm 6mm rgba(0,0,0,.08)} .art2css .ball.r1{left:166mm;top:142mm;width:18mm;height:18mm;background:#F23A2B} .art2css .ball.r2{left:104mm;top:232mm;width:16mm;height:16mm;background:#F23A2B}\n"
            + ".art2css .ball.w1{left:80mm;top:176mm;width:10mm;height:10mm;background:#F3F3F3} .art2css .ball.w2{left:180mm;top:168mm;width:16mm;height:16mm;background:#F3F3F3} .art2css .ball.w3{left:138mm;top:240mm;width:14mm;height:14mm;background:#F3F3F3}\n"
            + "/* 세부내역 */\n"
            + ".calcpg .sec{margin-top:4.5mm;height:7.6mm} .calcpg .sec .tab{height:7.6mm;line-height:7.6mm;font-size:11.5pt;font-weight:800} .calcpg .sec .tab b{font-weight:800}\n"
            + ".calc th{font-size:8pt;height:7mm;padding:0 4pt;background:#F4F4F4;color:#444} .calc td{font-size:7.2pt;height:auto;padding:2.2pt 5pt;white-space:normal;vertical-align:middle;border-bottom:1px solid #E6E6E6;line-height:1.3}\n"
            + ".calc th:nth-child(1){width:20%} .calc th:nth-child(2){width:13.5%} .calc th:nth-child(3){width:44.5%} .calc th:nth-child(4){width:9%} .calc th:nth-child(5){width:13%}\n"
            + ".calc td.lab{text-align:left;font-size:8.4pt;font-weight:500;color:#222;padding-left:8pt;white-space:normal;word-break:keep-all;line-height:1.2} .calc td.sum{text-align:center;white-space:normal;word-break:keep-all;line-height:1.15;padding-left:2pt;padding-right:2pt} .calc .cn{font-weight:700;font-size:10pt;color:#111} .calc .cn i{font-style:normal;font-size:7pt;font-weight:500;margin-left:1pt} .calc .cna{color:#C4C4C4;font-size:8.6pt;font-weight:500}\n"
            + ".calc td.nm{text-align:left;color:#222} .calc td.nm b{font-weight:600} .calc td.nm em{font-style:normal;color:#999;font-size:6.8pt} .calc td.mn{text-align:right;color:#999;white-space:nowrap} .calc td.am{text-align:right;color:#222;font-weight:600;white-space:nowrap}\n";

    /** ga_proposal.MOCK_CSS */
    public static final String GP_MOCK_CSS = ".mockpg{padding:0} .ov b.v{font-size:inherit;color:inherit;font-weight:inherit;letter-spacing:-.4pt} .ov b.v i{font-size:var(--u);color:var(--uc);font-weight:500;margin-left:1px}.ov .na{color:var(--na,#C4C4C4);font-weight:500;font-size:var(--naf,inherit)} .ov .txt{color:#F23A2B;font-weight:800;font-size:inherit} .ov b.v.z{color:#9A9A9A}.calcpg.mockpg .calcbody{position:absolute;left:12mm;top:25.76mm;width:186mm} .calcpg.mockpg .calcbody .sec:first-child{margin-top:0}";

    /** ga_v2.DETAIL_CSS */
    public static final String DETAIL_CSS = "\n"
            + "@page{size:595pt 708pt;margin:0}*{box-sizing:border-box}\n"
            + "html,body{margin:0;font-family:P;color:#222;-webkit-print-color-adjust:exact;print-color-adjust:exact;word-break:keep-all;overflow-wrap:anywhere}\n"
            + ".pg{width:595pt;height:708pt;overflow:hidden;position:relative;page-break-after:always}\n"
            + ".w{position:absolute;left:33.8pt;top:6pt;width:527.2pt}\n"
            + ".tab{display:inline-block;background:#EE3823;color:#fff;font-weight:800;font-size:12pt;line-height:1;padding:5.5pt 15pt 5pt;border-radius:6pt 6pt 0 0}\n"
            + ".tab:not(:first-child){margin-top:10pt}\n"
            + "table{width:100%;border-collapse:collapse;table-layout:fixed;border-top:1.5pt solid #DADADA}\n"
            + "th{background:#F4F4F4;white-space:nowrap;font-size:9.2pt;font-weight:500;color:#444;height:23pt;padding:0 6pt;border-bottom:.75pt solid #E6E6E6}th.r{text-align:right}\n"
            + "td{border-bottom:.75pt solid #E6E6E6;padding:2.3pt 6pt;vertical-align:middle}\n"
            + "td.k{font-size:9.6pt;line-height:1.25;padding-left:9pt;overflow-wrap:normal;word-break:keep-all}td.k small{display:block;font-size:7.6pt;color:#8B8B93;font-weight:500;margin-bottom:1pt}td.k b{font-weight:600}\n"
            + "td.m{text-align:right;padding-right:10pt;white-space:nowrap}td.m b{font-size:12.2pt;font-weight:800;color:#111;letter-spacing:-.2pt}td.m span{font-size:8.4pt;font-weight:500;margin-left:1.5pt}\n"
            + "td.m b.tx{font-size:10pt;font-weight:700}\n"
            + "td.m .x10{font-size:6.6pt;line-height:1.25;color:#666;font-weight:500;margin-top:2pt;white-space:nowrap}td.m .x10 b{font-size:8.4pt;font-weight:700;color:#333;letter-spacing:0}\n"
            + "td.m.na .pill{display:inline-block;font-size:8.6pt;color:#9A9AA2;border:.8pt dashed #C4C4C8;border-radius:9pt;padding:1.5pt 8pt}\n"
            + "td.n{font-size:8.7pt;font-weight:600;line-height:1.24;color:#222}td.n .sub{font-weight:500;color:#8B8B93}\n"
            + "td.n.none{color:#9A9AA2;font-weight:500;font-size:8.4pt}\n"
            + "td.ga{text-align:right;font-size:8.6pt;color:#9A9AA2;white-space:nowrap}\n"
            + "td.ea{text-align:right;font-size:8.9pt;font-weight:700;color:#222;white-space:nowrap;padding-right:7pt}\n"
            + "tbody.g tr:last-child td,tbody.g td.k,tbody.g td.m{border-bottom-color:#D2D2D6}\n";

    /** ga_v2.DETAIL_COLS */
    public static final String DETAIL_COLS = "<colgroup><col style=\"width:102pt\"><col style=\"width:86pt\"><col><col style=\"width:50pt\"><col style=\"width:66pt\"></colgroup>";

    /** ga_v2.DETAIL_HEAD */
    public static final String DETAIL_HEAD = "<thead><tr><th>구분</th><th class=\"r\" style=\"padding-right:10pt\">보장금액</th><th>특약명</th><th class=\"r\">가입금액</th><th class=\"r\" style=\"padding-right:7pt\">특약별 보장금액</th></tr></thead>";

    /** ga_v2.DETAIL_JS */
    public static final String DETAIL_JS = "\n"
            + "const PX = 4/3, HPX = 708*PX, root = document.getElementById('root');\n"
            + "let page = null, wrap = null, table = null, tab = null, report = {pages:0, groups:0, over:[]};\n"
            + "function newPage(){ page = document.createElement('div'); page.className = 'pg'; wrap = document.createElement('div'); wrap.className = 'w'; page.appendChild(wrap); root.appendChild(page); table = null; }\n"
            + "function startTable(title, cont){ tab = document.createElement('div'); tab.className = 'tab'; tab.textContent = title + (cont ? ' (이어서)' : ''); wrap.appendChild(tab);\n"
            + "  table = document.createElement('table'); table.dataset.sec = title; table.innerHTML = COLS + HEAD; wrap.appendChild(table); }\n"
            + "function over(){ return wrap.offsetTop + wrap.getBoundingClientRect().height > HPX - 2; }\n"
            + "newPage();\n"
            + "for (const sec of SECTIONS){ let placed = false;\n"
            + "  for (const g of sec.groups){ let made = false;\n"
            + "    if (!table || table.dataset.sec !== sec.title){ startTable(sec.title, placed); made = true; }\n"
            + "    table.insertAdjacentHTML('beforeend', g); let tb = table.lastElementChild;\n"
            + "    const orphan = made && !placed && wrap.children.length > 2 && (HPX - (wrap.offsetTop + wrap.getBoundingClientRect().height)) < 60*PX;\n"
            + "    if (over() || orphan){ tb.remove(); if (made){ table.remove(); tab.remove(); }\n"
            + "      newPage(); startTable(sec.title, placed); table.insertAdjacentHTML('beforeend', g); tb = table.lastElementChild;\n"
            + "      if (over()) report.over.push(sec.title); }\n"
            + "    placed = true; report.groups++; } }\n"
            + "report.pages = document.querySelectorAll('.pg').length;\n"
            + "window.REPORT = report;\n";

    /** ga_v2.FW_JS */
    public static final String FW_JS = "<script>document.fonts.ready.then(()=>document.querySelectorAll('.fw').forEach(e=>{const w=e.getBoundingClientRect().width*.75,m=+e.dataset.mw;if(w>m)e.style.transform='scale('+(m/w).toFixed(4)+')'}))</script>";

    /** ga_v2.FIT_JS */
    public static final String FIT_JS = "(gap)=>{const P=[...document.querySelectorAll('.page')].map((pg,i)=>{\n"
            + "  const c=pg.querySelector('.cnt'), ft=pg.querySelector('.ft'); if(!c||!ft) return {i,z:1};\n"
            + "  const W=pg.clientWidth-parseFloat(getComputedStyle(pg).paddingLeft)-parseFloat(getComputedStyle(pg).paddingRight);\n"
            + "  const top=c.getBoundingClientRect().top, avail=ft.getBoundingClientRect().top-top-(pg.dataset.gap?parseFloat(pg.dataset.gap)*4/3:gap);\n"
            + "  const set=z=>{c.style.zoom=z;c.style.width=(W/z)+'px'};\n"
            + "  const fits=z=>{set(z);let wide=false;c.querySelectorAll('table,.cards2,.cv-need,.cv-steps,.cv-two').forEach(t=>{if(t.scrollWidth>t.clientWidth+1||t.getBoundingClientRect().right>c.getBoundingClientRect().right+1)wide=true});return !wide&&c.getBoundingClientRect().height<=avail};\n"
            + "  const zmax=parseFloat(pg.dataset.zmax||'1.6');\n"
            + "  let lo=1,hi=zmax; if(!fits(1)){lo=0.7;hi=1} for(let k=0;k<14&&hi>lo;k++){const m=(lo+hi)/2; if(fits(m))lo=m; else hi=m}\n"
            + "  set(lo); return {i,z:lo,c,avail,set,g:pg.dataset.zg||''}});\n"
            + "  const G={}; P.forEach(p=>{if(p.g)(G[p.g]=G[p.g]||[]).push(p)});\n"
            + "  Object.values(G).forEach(a=>{const z=Math.min(...a.map(p=>p.z)); a.forEach(p=>{p.z=z;p.set(z)})});\n"
            + "  P.forEach(p=>{const pg=document.querySelectorAll('.page')[p.i]; if(!p.c||!pg.classList.contains('sfill'))return;      // 주요수술 : 남는 높이를 카드 줄에 고르게 나눠 쪽을 채운다(시안 ② 쪽처럼)\n"
            + "    const cd=p.c.querySelector('.cards2'), extra=p.avail-p.c.getBoundingClientRect().height; if(cd&&extra>2) cd.style.minHeight=((cd.getBoundingClientRect().height+extra-1)/p.z)+'px'});\n"
            + "  return P.map(p=>[p.i+1,+p.z.toFixed(3),p.c?Math.round(p.c.getBoundingClientRect().height):0,p.c?Math.round(p.avail):0])}";

    /** ga_v2.CLIP_JS */
    public static final String CLIP_JS = "()=>{const o=[];document.querySelectorAll('.sc-r>span:first-child,.sc-k,.sc-n,.cv-t td,.cv-two .x,.cv-steps>div').forEach(e=>{\n"
            + "  if(e.scrollWidth>e.clientWidth+1.5) o.push('글자 넘침 : '+(e.innerText||'').replace(/\\s+/g,' ').slice(0,30))});return o}";
}
