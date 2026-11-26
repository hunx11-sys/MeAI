package meai.sp;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * HTML → 브라우저(Chromium · Edge · Chrome) → PDF 조각. 파이썬 ga_v2.py 의 「글꼴 · 그리기」 부분
 * (_alive · _page · close_browser · _goto · render_snippet · FIT_JS · CLIP_JS · render_pages · render_detail 의 브라우저 부분)을 그대로 옮겼다.
 * 브라우저 하나를 띄워 두고 계속 쓴다. 조종은 Cdp(DevTools 프로토콜 직접 · 바깥 부품 없음)가 한다 —
 * 띄우는 스위치 · 쪽 설정 · PDF 인자를 파이썬 판이 쓰는 Playwright 와 같게 맞춰 같은 PDF 가 나온다.
 * 프로그램이 끝날 때 종료 훅이 브라우저를 닫고 임시 프로필을 지운다(close_browser() 를 직접 불러도 된다).
 */
public final class Render {
    private Render() {}

    /** 중간 파일(설계 내용이 든 HTML · PDF 조각)을 두는 곳 — 파이썬 TMP 와 같다(BASE/out/v2tmp · 환경변수 SP_TMP 로 바꿀 수 있음). 건마다 begin_job 이 그 안에 job_* 폴더를 만든다 */
    public static String TMP = tmpRoot();
    private static String tmpRoot() {
        String e = System.getenv("SP_TMP");
        return (e != null && !e.isEmpty()) ? Paths.get(e).toAbsolutePath().toString() : Py.path("out", "v2tmp");
    }

    // ── 브라우저 ─────────────────────────────────────────
    static final Map<String, Object> _PW = new HashMap<>();
    public static final String[] CHROME_CAND = {
        "%ProgramFiles(x86)%\\Microsoft\\Edge\\Application\\msedge.exe", "%ProgramFiles%\\Microsoft\\Edge\\Application\\msedge.exe",
        "%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe", "%LocalAppData%\\Google\\Chrome\\Application\\chrome.exe",
        "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"};

    /** os.path.expandvars 의 %이름% 꼴(윈도우 경로) */
    static String expandvars(String s) {
        return Py.sub("%([^%]+)%", m -> { String v = System.getenv(m.group(1)); return v != null ? v : m.group(0); }, s);
    }

    static boolean _alive() {
        try { Cdp pg = (Cdp) _PW.get("pg"); return pg != null && pg.alive(); }
        catch (RuntimeException ex) { return false; }
    }

    /** 쓸 브라우저 실행 파일 : GA_CHROMIUM → /opt/pw-browsers/chromium(파일이면) → 깔려 있는 Edge · Chrome · Chromium(CHROME_CAND) → PATH */
    static String find_browser() {
        String exe = Py.env("GA_CHROMIUM");
        if (exe != null && !exe.isEmpty()) return exe;
        File f = new File("/opt/pw-browsers/chromium");
        if (f.exists() && !f.isDirectory()) return f.getPath();
        for (String x : CHROME_CAND) { String c = expandvars(x); if (new File(c).isFile()) return c; }
        String path = System.getenv("PATH");
        if (path != null) {
            boolean win = System.getProperty("os.name", "").toLowerCase().contains("win");
            for (String nm : PATH_NAMES) for (String d : path.split(File.pathSeparator)) {
                if (d.isEmpty()) continue;
                File c = new File(d, win ? nm + ".exe" : nm);
                if (c.isFile() && c.canExecute()) return c.getPath();
            }
        }
        throw new RuntimeException("PDF 를 그릴 브라우저(Edge · Chrome · Chromium)를 찾지 못했습니다 — 환경변수 GA_CHROMIUM 에 실행 파일 경로를 넣어 주세요");
    }
    public static final String[] PATH_NAMES = {"chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome", "microsoft-edge", "msedge"};

    /** 크로뮴 하나를 띄워 두고 계속 쓴다. 죽어 있으면 닫고 새로 띄운다 */
    public static Cdp _page() {
        if (_PW.containsKey("pg") && !_alive()) close_browser();
        if (!_PW.containsKey("pg")) {
            if (!Py.truthy(_PW.get("atexit"))) {                      // 띄우다 실패해도 · 프로그램이 그냥 끝나도 브라우저 · 임시 프로필이 남지 않게
                Runtime.getRuntime().addShutdownHook(new Thread(Render::close_browser));
                _PW.put("atexit", true);
            }
            Cdp pg = Cdp.launch(find_browser(), 794, 1123);          // 한 동작 2분 넘으면 오류(Cdp.TIMEOUT_MS)
            _PW.put("pg", pg);
        }
        return (Cdp) _PW.get("pg");
    }

    /** 띄워 둔 크로뮴을 닫는다. 실패해도 프로그램 종료를 막지 않는다 */
    public static void close_browser() {
        Cdp pg = (Cdp) _PW.remove("pg");
        try { if (pg != null) pg.close(); } catch (RuntimeException ignore) { }
    }

    public static Cdp _goto(String html, String name) {
        String hp = Paths.get(TMP, name + ".html").toString();
        Py.write(hp, html);
        Cdp pg = _page();
        pg.emulate_media("print");
        String uri;
        try { uri = Paths.get(hp).toRealPath().toUri().toString(); } catch (IOException ex) { throw new RuntimeException(ex); }
        pg.navigate(uri);
        pg.evaluate("document.fonts.ready.then(()=>1)");
        try { Thread.sleep(120); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); throw new RuntimeException("중단됨", ex); }
        return pg;
    }

    /** Playwright 의 종이 크기 변환(px 글자 → 인치) : 픽셀 / 96 */
    static double px_in(double px) { return px / 96; }

    /** pg.pdf(path=…, prefer_css_page_size=True, print_background=True) — 쪽 크기는 HTML 의 @page 를 따른다 */
    public static void pdf_css(Cdp pg, String out_pdf) {
        pg.pdf(out_pdf, null, null, true, true);
    }

    /** 정해진 크기(pt)의 조각 한 장 */
    public static String render_snippet(String html, String out_pdf, double w_pt, double h_pt) {
        Cdp pg = _goto(html, "snip");
        pg.pdf(out_pdf, px_in(w_pt * 4 / 3), px_in(h_pt * 4 / 3), true, true);
        if (PdfKit.page_count(out_pdf) != 1) throw new AssertionError("조각이 두 쪽으로 넘어감 : " + out_pdf);
        return out_pdf;
    }

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
    public static final String CLIP_JS = "()=>{const o=[];document.querySelectorAll('.sc-r>span:first-child,.sc-k,.sc-n,.cv-t td,.cv-two .x,.cv-steps>div').forEach(e=>{\n"
        + "  if(e.scrollWidth>e.clientWidth+1.5) o.push('글자 넘침 : '+(e.innerText||'').replace(/\\s+/g,' ').slice(0,30))});return o}";

    /** 브라우저가 돌려준 값을 파이썬 꼴로(정수 → Long · 소수 → Double · 목록 → ArrayList · 객체 → LinkedHashMap) */
    @SuppressWarnings("unchecked")
    public static Object pyval(Object o) {
        if (o instanceof Integer || o instanceof Short || o instanceof Byte) return ((Number) o).longValue();
        if (o instanceof Float) return ((Float) o).doubleValue();
        if (o instanceof List) { List<Object> a = new ArrayList<>(); for (Object x : (List<Object>) o) a.add(pyval(x)); return a; }
        if (o instanceof Map) { Map<String, Object> m = new LinkedHashMap<>(); for (Map.Entry<String, Object> e : ((Map<String, Object>) o).entrySet()) m.put(e.getKey(), pyval(e.getValue())); return m; }
        return o;
    }

    /**
     * A4 쪽들(.page) — 쪽마다 본문(.cnt)을 머리 아래 ~ 바닥글 위 빈 곳에 맞춘다.
     * 돌려주는 것 : [fit, over] — fit = [[쪽, 배율, 본문 높이, 쓸 수 있는 높이] …] · over = 넘친 쪽의 fit 줄 + 「글자 넘침 : …」 글자
     */
    public static List<Object> render_pages(String html, String out_pdf, String name) {
        Cdp pg = _goto(html, name);
        List<Object> fit = Py.L(pyval(pg.call(FIT_JS, 18L)));
        List<Object> clip = Py.L(pyval(pg.call(CLIP_JS)));           // 칸 밖으로 넘친 글자(수술 카드 줄 이름 · 칩 · 간병 표 칸)
        pg.pdf(out_pdf, 8.27, 11.7, true, true);                     // format='A4' — Playwright 의 A4 = 8.27 × 11.7 인치
        List<Object> over = new ArrayList<>();
        for (Object o : fit) { List<Object> f = Py.L(o); if (Py.truthy(f.get(3)) && Py.num(f.get(2)) > Py.num(f.get(3)) + 1) over.add(f); }
        over.addAll(clip);
        return Py.list(fit, over);
    }
    public static List<Object> render_pages(String html, String out_pdf) { return render_pages(html, out_pdf, "pages"); }

    /** 세부내역 — HTML(스스로 쪽을 나누는 스크립트 포함)을 그려 595×708pt 쪽들로. 돌려주는 것 = 스크립트가 남긴 window.REPORT */
    public static Map<String, Object> render_detail_html(String html, String out_pdf) {
        Cdp pg = _goto(html, "detail");
        pg.wait_for("window.REPORT");
        Map<String, Object> rep = Py.M(pyval(pg.evaluate("window.REPORT")));
        pg.pdf(out_pdf, px_in(595 * 4 / 3.0), px_in(708 * 4 / 3.0), true, true);
        if (Py.truthy(rep.get("over"))) throw new RuntimeException(Py.fmt("세부내역 한 묶음이 한 쪽을 넘음 : %s", rep.get("over")));
        return rep;
    }

    // ── 건마다 임시 폴더(파이썬 build 의 TMP 다루기) ─────
    /** 한 건을 시작한다 — TMP 아래 job_* 폴더를 만들고 TMP 를 그리로 돌린다. 돌려주는 것 = 원래 TMP(end_job 에 넘긴다) */
    public static String begin_job() {
        String root = TMP;
        try {
            Files.createDirectories(Paths.get(root));
            TMP = Files.createTempDirectory(Paths.get(root), Py.fmt("job_%d_", ProcessHandle.current().pid())).toString();
        } catch (IOException ex) { throw new RuntimeException("임시 폴더를 만들지 못함 : " + root, ex); }
        return root;
    }

    /** 한 건을 끝낸다 — TMP 를 되돌리고 그 건의 폴더를 지운다(GA_V2_KEEP=1 이면 남긴다 — 지면 점검용) */
    public static void end_job(String root) {
        String work = TMP; TMP = root;
        if (!"1".equals(System.getenv("GA_V2_KEEP"))) rmtree(Paths.get(work));
    }

    static void rmtree(Path p) {
        try {
            if (!Files.exists(p)) return;
            try (java.util.stream.Stream<Path> w = Files.walk(p)) {
                w.sorted(java.util.Comparator.reverseOrder()).forEach(q -> { try { Files.delete(q); } catch (IOException ignore) { } });
            }
        } catch (IOException ignore) { }
    }

    /** 서버가 처리 중에 꺼져 남은 중간 파일(job_*)을 치운다 — 만든 지 max_age 초 넘은 것만 */
    public static int sweep_tmp(long max_age) {
        int n = 0;
        File[] ds = new File(TMP).listFiles((d, nm) -> nm.startsWith("job_"));
        if (ds == null) return 0;
        for (File d : ds) {
            if ((System.currentTimeMillis() - d.lastModified()) / 1000.0 > max_age) { rmtree(d.toPath()); n++; }
        }
        return n;
    }
    public static int sweep_tmp() { return sweep_tmp(3600); }
}
