/* 익스플로러로 열리면 같은 주소를 엣지로 다시 열기 (익스플로러도 읽을 수 있는 옛 문법으로 작성)
   - 엣지로 넘길 때 주소에 ?from=ie 를 붙임 → 회사 설정(IE 모드 목록) 때문에 엣지에서도 다시 익스플로러 방식으로 열리면
     그 표시를 보고 더 넘기지 않고(무한 반복 방지) 크롬용 주소 복사 안내를 보여 줌
   - 정상 브라우저로 넘어오면 주소창의 ?from=ie 는 지움 */
(function () {
  var ua = navigator.userAgent || '';
  var isIE = !!document.documentMode || ua.indexOf('MSIE ') > -1 || ua.indexOf('Trident/') > -1;
  var href = location.href, hash = location.hash || '', base = hash ? href.substring(0, href.length - hash.length) : href;
  var flag = /[?&]from=ie(?=&|$)/, plain = base.replace(flag, '').replace(/^([^?]*)&/, '$1?');
  if (!isIE) { if (flag.test(base) && window.history && history.replaceState) { try { history.replaceState(null, '', plain + hash); } catch (e) {} } return; }
  var loop = flag.test(base);
  window.__IE_LOOP = loop;
  window.__PLAIN_URL = plain + hash;
  window.__EDGE_URL = 'microsoft-edge:' + plain + (plain.indexOf('?') > -1 ? '&' : '?') + 'from=ie' + hash;
  document.documentElement.className += ' is-ie' + (loop ? ' ie-loop' : '');
})();
/* 안내 상자(.ie-box)의 단추 연결 · 엣지로 넘기기 : 상자가 그려진 뒤에 실행 */
(function () {
  function wire() {
    if (!window.__EDGE_URL) return;
    var a = document.getElementById('ie-go'), u = document.getElementById('ie-url'), c = document.getElementById('ie-copy');
    if (a) a.href = window.__EDGE_URL;
    if (u) { u.value = window.__PLAIN_URL; u.onclick = function () { u.select(); }; }
    if (c) c.onclick = function () {
      var ok = false;
      try { if (window.clipboardData) ok = window.clipboardData.setData('Text', window.__PLAIN_URL); } catch (e) {}
      if (!ok && u) { u.select(); try { ok = document.execCommand('copy'); } catch (e2) {} }
      c.innerHTML = ok ? '복사했어요 · 크롬 주소창에 붙여 넣으세요' : '위 주소를 선택해 Ctrl+C 로 복사해 주세요';
    };
    /* 안내 화면을 먼저 그린 뒤 엣지로 넘김. 이미 엣지에서 넘어왔는데도 IE 방식이면(IE 모드) 넘기지 않음 */
    if (!window.__IE_LOOP) setTimeout(function () { try { window.location.href = window.__EDGE_URL; } catch (e) {} }, 400);
  }
  if (!window.__EDGE_URL) return;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', wire); else wire();
})();
