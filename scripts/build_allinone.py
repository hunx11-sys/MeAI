#!/usr/bin/env python3
"""
올인원 HTML 만들기 — 사내 메일에 파일 하나만 붙여 보낼 때
- 저장소 루트에서 실행: python3 scripts/build_allinone.py
- 결과: dist/meritz_tools_allinone.html  (대문 + 도구 5종이 한 파일)

고치는 것은 지금처럼 원래 파일(index.html · tool.html …)에서 한다. 이 파일은 보낼 때마다 새로 만든다.

만드는 방법
  1) build_single.py 로 낱개 자립형 6개를 만든다(글꼴·용어사전을 안에 넣고, 통계 전송을 끈 판).
  2) 6개를 한 파일 안에 '보관'만 해 두고, 화면에는 한 번에 하나를 칸막이(iframe) 안에 띄운다.
     도구끼리 디자인·기능 이름이 겹쳐도 칸막이가 달라 서로 망가뜨리지 않는다.
  3) 대문 카드·🏠 버튼처럼 다른 파일로 가는 링크는 파일 안의 해당 도구로 바꿔 띄운다.
     보상시뮬레이터(특약검색기 안의 또 한 겹)의 🏠 버튼도 같게 맞춘다.
"""
import base64, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SINGLE = os.path.join(ROOT, 'dist', 'single')
OUT = os.path.join(ROOT, 'dist', 'meritz_tools_allinone.html')
PAGES = ['home', 'tool', 'care', 'products', 'prompts', 'nameplate']

# 링크를 가로채 바깥 틀에 "이 도구로 바꿔 달라"고 알린다
NAV = ("<script>/* 올인원 : 다른 도구로 가는 링크를 파일 안의 도구로 */(function(){"
       "var P={'home.html':1,'index.html':1,'tool.html':1,'care.html':1,'products.html':1,'prompts.html':1,'nameplate.html':1};"
       "document.addEventListener('click',function(e){var a=e.target&&e.target.closest&&e.target.closest('a[href]');if(!a)return;"
       "var m=(a.getAttribute('href')||'').match(/^(?:\\.\\/)?([a-z]+\\.html)(#.*)?$/);if(!m||!P[m[1]])return;"
       "e.preventDefault();e.stopPropagation();var n=m[1]==='index.html'?'home':m[1].replace('.html','');"
       "try{window.top.postMessage({meaiGo:n,hash:m[2]||''},'*');}catch(x){}},true);})();</script>")


def inject(html):
    """<head> 바로 뒤에 NAV 를 넣는다(없으면 맨 앞)"""
    m = re.search(r'<head[^>]*>', html, re.I)
    return html[:m.end()] + NAV + html[m.end():] if m else NAV + html


def fix_sim(tool):
    """특약검색기 안에 base64 로 들어 있는 보상시뮬레이터 원문에도 NAV 를 넣는다"""
    m = re.search(r'(<script id="SIMSRC"[^>]*>)(.*?)(</script>)', tool, re.S)
    if not m: sys.exit('tool.html 에 SIMSRC 가 없습니다')
    inner = base64.b64decode(m.group(2).strip()).decode('utf-8')
    inner = inject(inner)
    return tool[:m.start(2)] + base64.b64encode(inner.encode('utf-8')).decode('ascii') + tool[m.end(2):]


def stash(text):
    """<script type="text/plain"> 안에 넣어도 HTML 이 끊기지 않게 두 글자열만 바꿔 둔다(열 때 되돌림)"""
    for tok in ('@@MEAI_S@@', '@@MEAI_C@@'):
        if tok in text: sys.exit('보관 표시 글자가 원문에 이미 있습니다: ' + tok)
    return text.replace('</script', '<@@MEAI_S@@/script').replace('<!--', '<@@MEAI_C@@!--')


SHELL = """<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>메리츠 영업지원도구 (올인원)</title>
<style>html,body{margin:0;height:100%;background:#fff}
#v{position:fixed;inset:0;width:100%;height:100%;border:0;display:block}
#w{position:fixed;inset:0;display:flex;align-items:center;justify-content:center;font:15px/1.6 sans-serif;color:#666}</style>
</head><body>
<div id="w">여는 중입니다…</div>
<iframe id="v" title="영업지원도구"></iframe>
__PAGES__
<script>
(function(){
  var NAMES=__NAMES__, urls={}, cur=null, v=document.getElementById('v');
  function url(p){
    if(urls[p]) return urls[p];
    var t=document.getElementById('pg-'+p).textContent
      .split('<@@MEAI_S@@/script').join('</script').split('<@@MEAI_C@@!--').join('<!--');
    return (urls[p]=URL.createObjectURL(new Blob([t],{type:'text/html;charset=utf-8'})));
  }
  function show(p,hash,push){
    if(NAMES.indexOf(p)<0) p='home';
    // 틀을 새로 만들어 끼운다 — 기존 틀의 주소만 바꾸면 브라우저 '뒤로'가 틀 안에서 따로 쌓인다
    var n=document.createElement('iframe'); n.id='v'; n.title='영업지원도구'; n.src=url(p)+(hash||'');
    v.parentNode.replaceChild(n,v); v=n; cur=p;
    document.getElementById('w').style.display='none';
    if(push){ try{ history.pushState({p:p,h:hash||''},'','#'+p+(hash?hash.replace('#','-'):'')); }catch(e){} }
  }
  window.addEventListener('message',function(e){ var d=e.data; if(d&&d.meaiGo) show(d.meaiGo,d.hash,true); });
  window.addEventListener('popstate',function(e){ var s=e.state||{p:'home',h:''}; show(s.p,s.h,false); });
  var h=(location.hash||'').replace('#','').split('-');
  try{ history.replaceState({p:h[0]||'home',h:h[1]?'#'+h[1]:''},'',location.href); }catch(e){}
  show(h[0]||'home', h[1]?'#'+h[1]:'', false);
})();
</script>
</body></html>
"""


def main():
    subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build_single.py')], check=True,
                   stdout=subprocess.DEVNULL)
    blocks = []
    for p in PAGES:
        s = open(os.path.join(SINGLE, p + '.html'), encoding='utf-8').read()
        if p == 'tool': s = fix_sim(s)
        s = inject(s)
        blocks.append('<script type="text/plain" id="pg-%s">%s</script>' % (p, stash(s)))
        print('  %-10s %.1f MB' % (p, len(s.encode('utf-8')) / 1e6))
    out = SHELL.replace('__NAMES__', repr(PAGES).replace("'", '"')).replace('__PAGES__', '\n'.join(blocks))
    open(OUT, 'w', encoding='utf-8').write(out)
    print('\n%s · %.1f MB' % (os.path.relpath(OUT, ROOT), len(out.encode('utf-8')) / 1e6))


if __name__ == '__main__':
    main()
