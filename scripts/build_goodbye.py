# -*- coding: utf-8 -*-
"""영업지원도구 인터넷판(깃허브 주소) 종료 인사 화면 — goodbye.html 조립

2026-11-25 회사 리스크진단파트 의견(외부 깃허브 주소가 피싱 사이트로 오인될 수 있음)으로
인터넷 주소(hunx11-sys.github.io/MeAI)에서는 영업지원도구를 보여 주지 않는다.
각 화면 맨 앞의 공통 스크립트(scripts/apply_ui.py BOOT)가 github.io 에서 열리면 이 화면으로 넘긴다.
사내 노트북 파일 · 사내망 · 올인원 배포판에서는 그대로 동작한다(개발은 계속 · MeAI 홈 이식 예정).

  python3 scripts/build_goodbye.py      → goodbye.html (걱정인형 그림은 파일 안에 넣음 · 글꼴은 저장소 assets/ · 바깥 주소 없음)

입력 · 누르는 칸 · 다른 화면으로 가는 링크를 두지 않는다(오인 방지 — 안내만 한다).
"""
import base64, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M = os.path.join(ROOT, 'ui', 'mascots')
OUT = os.path.join(ROOT, 'goodbye.html')

def b64(name):
    return 'data:image/webp;base64,' + base64.b64encode(open(os.path.join(M, name), 'rb').read()).decode()

# 걱정인형 여섯 — 도구마다 한 명(DESIGN-MeAI 12장 · 한 자리에 그림 하나 · 비율 그대로)
DOLLS = [('merry_ok.webp', '메리', '#C73D1C'), ('eco_point.webp', '에코', '#23874C'), ('rara_present.webp', '라라', '#F2B705'),
         ('indi_idea.webp', '인디', '#A23A91'), ('tata_ok.webp', '타타', '#2563C9'), ('ziziri_cheer.webp', '찌지리', '#6D5BD6')]

dolls = ''.join(
    '<figure class="doll" style="--i:%d;--c:%s"><img src="%s" alt="%s" draggable="false"><figcaption>%s</figcaption></figure>'
    % (i, c, b64(f), n, n) for i, (f, n, c) in enumerate(DOLLS))

# 떠오르는 하트 · 별 — 위치 · 크기 · 속도는 고정 값(매번 같은 화면)
FLOAT = [(6, 14, 11, 0, 'h', '#F5C2CA'), (14, 10, 14, 3.2, 's', '#F3DD94'), (22, 18, 12.5, 6.1, 'h', '#D3CCF5'), (31, 12, 15, 1.4, 's', '#BFE3CC'),
         (40, 16, 13, 8.3, 'h', '#F6CBBD'), (49, 10, 16, 4.6, 's', '#C3D6F4'), (58, 20, 12, 2.2, 'h', '#E8C3DF'), (67, 12, 14.5, 7.4, 's', '#F3DD94'),
         (75, 16, 11.5, 5.3, 'h', '#F5C2CA'), (83, 11, 15.5, 0.8, 's', '#D3CCF5'), (91, 18, 13.5, 9.1, 'h', '#BFE3CC'), (96, 10, 16.5, 3.9, 's', '#F6CBBD')]
HEART = '<svg viewBox="0 0 24 24"><path d="M12 21s-7.5-4.6-9.6-9.2C.9 8.4 3 4.5 6.7 4.5c2.1 0 3.6 1.2 5.3 3.1 1.7-1.9 3.2-3.1 5.3-3.1 3.7 0 5.8 3.9 4.3 7.3C19.5 16.4 12 21 12 21z"/></svg>'
STAR = '<svg viewBox="0 0 24 24"><path d="M12 2.5l2.6 6.2 6.7.5-5.1 4.4 1.6 6.6L12 16.6l-5.8 3.6 1.6-6.6-5.1-4.4 6.7-.5z"/></svg>'
floats = ''.join('<i class="fl" style="left:%s%%;width:%dpx;--d:%ss;--w:%ss;color:%s">%s</i>' % (x, sz, dur, dl, col, HEART if k == 'h' else STAR)
                 for x, sz, dur, dl, k, col in FLOAT)

# 글꼴은 저장소의 같은 파일을 주소로 부른다(파일 안에 넣으면 1.3MB — 휴대폰 첫 화면이 느려진다). 못 받으면 기기 글꼴.
FONTFACE = '@font-face{font-family:"Pretendard Variable";font-weight:45 930;font-display:swap;src:url(assets/pretendard-subset.woff2) format("woff2-variations"),url(assets/pretendard-subset.woff2) format("woff2")}'

HTML = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#FFFFFF">
<title>MeAI 영업지원도구 안내</title>
<style>
%(fontface)s
:root{--ink:#191F28;--sub:#4E5968;--muted:#6B7684;--line:#E5E8EB;--surface:#FFFFFF;--bg:#F7F8FA;--accent:#C8102E;--accent-weak:#FDECEE;--accent-line:#F5C2CA;
  --spring:cubic-bezier(.16,1,.3,1);--font:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
*{box-sizing:border-box}
html,body{margin:0;min-height:100%%;background:var(--bg);color:var(--ink);font-family:var(--font);-webkit-font-smoothing:antialiased;word-break:keep-all;overflow-wrap:anywhere}
body{min-height:100svh;display:flex;align-items:center;justify-content:center;padding:32px 16px calc(32px + env(safe-area-inset-bottom));overflow-x:hidden;position:relative}
/* 바탕 빛 — 정지 */
.glow{position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(40%% 32%% at 18%% 12%%,rgba(200,16,46,.07),transparent 70%%),radial-gradient(36%% 30%% at 84%% 18%%,rgba(109,91,214,.08),transparent 70%%),
             radial-gradient(44%% 36%% at 50%% 100%%,rgba(242,183,5,.08),transparent 70%%)}
/* 떠오르는 하트 · 별 */
.sky{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden}
.fl{position:absolute;bottom:-40px;display:block;opacity:0;animation:rise var(--d) linear var(--w) infinite}
.fl svg{display:block;width:100%%;height:auto;fill:currentColor}
@keyframes rise{0%%{transform:translate3d(0,0,0) rotate(0);opacity:0}10%%{opacity:.9}50%%{transform:translate3d(14px,-55vh,0) rotate(12deg)}90%%{opacity:.7}100%%{transform:translate3d(-10px,-112vh,0) rotate(-8deg);opacity:0}}
/* 카드 */
.card{position:relative;z-index:1;width:100%%;max-width:720px;background:var(--surface);border:1px solid var(--line);border-radius:32px;
  padding:40px 40px 0;text-align:center;box-shadow:0 12px 40px rgba(15,23,42,.06),0 2px 6px rgba(15,23,42,.04);overflow:hidden;
  opacity:0;transform:translateY(16px) scale(.985);animation:in .9s var(--spring) .1s forwards}
@keyframes in{to{opacity:1;transform:none}}
.chip{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 14px;border-radius:999px;background:var(--accent-weak);color:#A50D26;font-size:13px;font-weight:600}
.chip b{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:6px;background:var(--accent);color:#fff;font-size:12px;font-weight:700}
h1{margin:20px 0 0;font-size:clamp(26px,6.4vw,38px);line-height:1.32;letter-spacing:-.03em;font-weight:700}
h1 .ln{display:block;opacity:0;transform:translateY(12px);animation:in .8s var(--spring) forwards}
h1 .ln:nth-child(1){animation-delay:.35s}h1 .ln:nth-child(2){animation-delay:.5s}
h1 em{font-style:normal;color:var(--accent)}
.msg{margin:20px auto 0;max-width:520px;font-size:17px;line-height:1.75;color:var(--sub)}
.msg p{margin:0;opacity:0;transform:translateY(10px);animation:in .8s var(--spring) forwards}
.msg p:nth-child(1){animation-delay:.75s}.msg p:nth-child(2){animation-delay:.9s}
.msg b{color:var(--ink);font-weight:600}
.sign{margin:24px 0 0;font-size:15px;color:var(--muted);font-weight:500;opacity:0;animation:in .8s var(--spring) 1.1s forwards}
/* 걱정인형 줄 */
.dolls{display:flex;justify-content:center;align-items:flex-end;gap:4px;margin:32px -24px 0;padding:0 8px}
.doll{margin:0;flex:1 1 0;min-width:0;display:flex;flex-direction:column;align-items:center;opacity:0;transform:translateY(40px);
  animation:pop .9s var(--spring) calc(1.25s + var(--i) * .12s) forwards}
.doll img{display:block;height:112px;width:auto;max-width:100%%;object-fit:contain;transform-origin:50%% 100%%;
  animation:bob 4.6s cubic-bezier(.45,0,.55,1) calc(2.4s + var(--i) * .37s) infinite;user-select:none;-webkit-user-drag:none;cursor:pointer}
.doll:nth-child(6) img{height:88px}   /* 찌지리는 몸집이 커 보여 작게(소유자 2026-11-25) */
.doll figcaption{margin:6px 0 0;padding:0 10px;height:24px;line-height:24px;border-radius:999px;font-size:12px;font-weight:600;color:#fff;background:var(--c)}
.doll:nth-child(3) figcaption{color:#3D2C00}
.doll.hop img{animation:hop .6s var(--spring)}
@keyframes pop{to{opacity:1;transform:none}}
@keyframes bob{0%%,100%%{transform:translateY(0) rotate(0)}30%%{transform:translateY(-5px) rotate(-2deg)}70%%{transform:translateY(-3px) rotate(2deg)}}
@keyframes hop{0%%{transform:none}40%%{transform:translateY(-16px) rotate(-4deg)}100%%{transform:none}}
.heart{position:absolute;pointer-events:none;width:22px;height:22px;color:var(--c,#C8102E);animation:pf 1.1s var(--spring) forwards;z-index:3}
.heart svg{width:100%%;height:100%%;fill:currentColor}
@keyframes pf{0%%{opacity:0;transform:translate(-50%%,0) scale(.4)}20%%{opacity:1}100%%{opacity:0;transform:translate(-50%%,-70px) scale(1.15)}}
.foot{margin:0 -40px;padding:16px 24px;border-top:1px solid var(--line);background:#FBFBFC;font-size:13px;color:var(--muted)}
@media(max-width:560px){
  .card{padding:32px 20px 0;border-radius:24px}
  .msg{font-size:15.5px}
  .dolls{flex-wrap:wrap;gap:12px 0;margin:28px -8px 0}
  .doll{flex:0 0 33.333%%}
  .doll img{height:96px}
  .doll:nth-child(6) img{height:76px}
  .foot{margin:0 -20px}
}
@media (prefers-reduced-motion:reduce){
  .card,h1 .ln,.msg p,.sign,.doll{animation:none;opacity:1;transform:none}
  .doll img{animation:none}.sky{display:none}
}
</style>
</head>
<body>
<div class="glow" aria-hidden="true"></div>
<div class="sky" aria-hidden="true">%(floats)s</div>
<main class="card" role="main">
  <span class="chip"><b>M</b>MeAI 영업지원도구</span>
  <h1><span class="ln">그동안 영업지원도구를</span><span class="ln"><em>사랑해주셔서</em> 감사합니다.</span></h1>
  <div class="msg">
    <p>영업지원도구는 <b>MeAI홈</b>에 이식하여<br>사내 정식 서비스로 찾아뵐 예정입니다.</p>
    <p>영업활동에 많은 도움이 되도록 노력하겠습니다.</p>
  </div>
  <p class="sign">-세일즈혁신TF 이헌수 배상-</p>
  <div class="dolls">%(dolls)s</div>
  <div class="foot">이 주소의 영업지원도구 서비스는 종료되었습니다.</div>
</main>
<script>
/* 걱정인형을 누르면 폴짝 뛰며 하트가 떠오른다(장식 · 움직임 줄이기면 하트만) */
(function(){
  var heart=%(heart)s, still=false;
  try{still=window.matchMedia('(prefers-reduced-motion: reduce)').matches}catch(e){}
  Array.prototype.forEach.call(document.querySelectorAll('.doll'),function(d){
    d.addEventListener('click',function(e){
      if(!still){d.classList.remove('hop');void d.offsetWidth;d.classList.add('hop');}
      var r=d.getBoundingClientRect(),h=document.createElement('i');
      h.className='heart';h.innerHTML=heart;h.style.setProperty('--c',getComputedStyle(d).getPropertyValue('--c'));
      h.style.left=(r.left+r.width/2+window.scrollX)+'px';h.style.top=(r.top+window.scrollY+8)+'px';h.style.position='absolute';
      document.body.appendChild(h);setTimeout(function(){h.remove()},1200);
    });
  });
})();
</script>
</body>
</html>
''' % {'fontface': FONTFACE, 'floats': floats, 'dolls': dolls, 'heart': repr(HEART).replace("'", '"') if False else '\'' + HEART + '\''}

open(OUT, 'w', encoding='utf-8').write(HTML)
print('goodbye.html  %.0f KB' % (len(HTML.encode('utf-8')) / 1024))
