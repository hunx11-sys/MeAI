package meai.sp;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserType;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.options.Media;
import com.microsoft.playwright.options.WaitUntilState;

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
 * 브라우저 하나를 띄워 두고 계속 쓴다 — Playwright 규칙대로 **한 스레드에서만** 부른다.
 * 프로그램을 끝낼 때는 close_browser() 를 부르거나 System.exit 로 끝낸다 — 브라우저를 띄운 채 main 에서 그냥 돌아오면
 * Playwright 의 일꾼 스레드가 남아 프로그램이 끝나지 않는다(System.exit 일 때는 종료 훅이 닫는다).
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
        try { return ((Browser) _PW.get("b")).isConnected() && !((Page) _PW.get("pg")).isClosed(); }
        catch (RuntimeException ex) { return false; }
    }

    /** 크로뮴 하나를 띄워 두고 계속 쓴다. 죽어 있으면 닫고 새로 띄운다 */
    public static Page _page() {
        if (_PW.containsKey("pg") && !_alive()) close_browser();
        if (!_PW.containsKey("pg")) {
            Map<String, String> env = new HashMap<>(System.getenv());
            env.put("PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD", "1");            // 브라우저를 내려받으려 하지 않는다(폐쇄망 · 깔린 것을 쓴다)
            Playwright pw = Playwright.create(new Playwright.CreateOptions().setEnv(env));
            Browser b; Page pg;
            try {
                String exe = System.getenv("GA_CHROMIUM");
                if (exe == null || exe.isEmpty()) {
                    File f = new File("/opt/pw-browsers/chromium");
                    exe = (f.exists() && !f.isDirectory()) ? f.getPath() : null;
                }
                try {
                    b = exe != null ? pw.chromium().launch(new BrowserType.LaunchOptions().setExecutablePath(Paths.get(exe))) : pw.chromium().launch();
                } catch (RuntimeException ex) {      // Playwright 크로뮴이 없는 PC(폐쇄망) — 깔려 있는 Edge · Chrome 으로(GA_CHROMIUM 을 안 넣었을 때)
                    List<String> cand = new ArrayList<>();
                    for (String x : CHROME_CAND) { String c = expandvars(x); if (new File(c).isFile()) cand.add(c); }
                    if (exe != null || cand.isEmpty()) throw ex;
                    b = pw.chromium().launch(new BrowserType.LaunchOptions().setExecutablePath(Paths.get(cand.get(0))));
                }
                pg = b.newPage(new Browser.NewPageOptions().setViewportSize(794, 1123));
                pg.setDefaultTimeout(120000);                          // 한 동작 2분 넘으면 오류(멈춘 채 붙잡지 않게)
            } catch (RuntimeException ex) {
                try { pw.close(); } catch (RuntimeException ignore) { }
                throw ex;
            }
            _PW.put("pw", pw); _PW.put("b", b); _PW.put("pg", pg);
            if (!Py.truthy(_PW.get("atexit"))) {
                Runtime.getRuntime().addShutdownHook(new Thread(Render::close_browser));
                _PW.put("atexit", true);
            }
        }
        return (Page) _PW.get("pg");
    }

    /** 띄워 둔 크로뮴을 닫는다. 실패해도 프로그램 종료를 막지 않는다 */
    public static void close_browser() {
        Playwright pw = (Playwright) _PW.remove("pw"); Browser b = (Browser) _PW.remove("b"); _PW.remove("pg");
        try {
            if (b != null) b.close();
            if (pw != null) pw.close();
        } catch (RuntimeException ignore) { }
    }

    public static Page _goto(String html, String name) {
        String hp = Paths.get(TMP, name + ".html").toString();
        Py.write(hp, html);
        Page pg = _page();
        pg.emulateMedia(new Page.EmulateMediaOptions().setMedia(Media.PRINT));
        String uri;
        try { uri = Paths.get(hp).toRealPath().toUri().toString(); } catch (IOException ex) { throw new RuntimeException(ex); }
        pg.navigate(uri, new Page.NavigateOptions().setWaitUntil(WaitUntilState.LOAD));
        pg.evaluate("document.fonts.ready");
        pg.waitForTimeout(120);
        return pg;
    }

    /** pg.pdf(path=…, prefer_css_page_size=True, print_background=True) — 쪽 크기는 HTML 의 @page 를 따른다 */
    public static void pdf_css(Page pg, String out_pdf) {
        pg.pdf(new Page.PdfOptions().setPath(Paths.get(out_pdf)).setPreferCSSPageSize(true).setPrintBackground(true));
    }

    /** 정해진 크기(pt)의 조각 한 장 */
    public static String render_snippet(String html, String out_pdf, double w_pt, double h_pt) {
        Page pg = _goto(html, "snip");
        pg.pdf(new Page.PdfOptions().setPath(Paths.get(out_pdf)).setWidth(Py.fmt("%spx", w_pt * 4 / 3)).setHeight(Py.fmt("%spx", h_pt * 4 / 3))
                .setPrintBackground(true).setPreferCSSPageSize(true));
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
        Page pg = _goto(html, name);
        List<Object> fit = Py.L(pyval(pg.evaluate(FIT_JS, 18)));
        List<Object> clip = Py.L(pyval(pg.evaluate(CLIP_JS)));       // 칸 밖으로 넘친 글자(수술 카드 줄 이름 · 칩 · 간병 표 칸)
        pg.pdf(new Page.PdfOptions().setPath(Paths.get(out_pdf)).setFormat("A4").setPrintBackground(true).setPreferCSSPageSize(true));
        List<Object> over = new ArrayList<>();
        for (Object o : fit) { List<Object> f = Py.L(o); if (Py.truthy(f.get(3)) && Py.num(f.get(2)) > Py.num(f.get(3)) + 1) over.add(f); }
        over.addAll(clip);
        return Py.list(fit, over);
    }
    public static List<Object> render_pages(String html, String out_pdf) { return render_pages(html, out_pdf, "pages"); }

    /** 세부내역 — HTML(스스로 쪽을 나누는 스크립트 포함)을 그려 595×708pt 쪽들로. 돌려주는 것 = 스크립트가 남긴 window.REPORT */
    public static Map<String, Object> render_detail_html(String html, String out_pdf) {
        Page pg = _goto(html, "detail");
        pg.waitForFunction("window.REPORT");
        Map<String, Object> rep = Py.M(pyval(pg.evaluate("window.REPORT")));
        pg.pdf(new Page.PdfOptions().setPath(Paths.get(out_pdf)).setWidth(Py.fmt("%spx", 595 * 4 / 3.0)).setHeight(Py.fmt("%spx", 708 * 4 / 3.0))
                .setPrintBackground(true).setPreferCSSPageSize(true));
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
