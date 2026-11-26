package meai.sp;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * 크로뮴 · Edge · Chrome 을 직접 띄워 DevTools 프로토콜(CDP)로 조종한다 — 바깥 부품 없이(JDK 의 java.net.http.WebSocket + 우리 Json).
 * 하는 일은 지면을 PDF 로 뜨는 데 필요한 것뿐이다 : 쪽 하나 열기 · 인쇄 매체 흉내 · 파일 주소로 가기 · JS 평가 · PDF 로 인쇄.
 * 띄우는 스위치 · 쪽 설정 · PDF 인자는 Playwright 1.49(Apache-2.0)가 크로뮴에 주는 것과 같게 맞췄다(chromiumSwitches · crPage · crPdf) —
 * 파이썬 판(Playwright 로 그린다)과 같은 PDF 가 나오게 하려는 것이다. 고치면 golden/cmp_pdf.py 로 픽셀 차이 0 을 다시 본다.
 */
public final class Cdp {
    /** 한 동작(명령 하나 · 쪽 열림 기다리기) 제한 — 파이썬 판 pg.set_default_timeout(120000) */
    public static final long TIMEOUT_MS = 120000;
    /** 브라우저가 떠서 조종 주소를 알려 줄 때까지 기다리는 시간 */
    public static final long LAUNCH_MS = 60000;

    /** Playwright chromiumSwitches(1.49) + headless 일 때 붙는 것 + --no-sandbox */
    public static final String[] SWITCHES = {
        "--disable-field-trial-config",
        "--disable-background-networking", "--disable-background-timer-throttling", "--disable-backgrounding-occluded-windows", "--disable-back-forward-cache",
        "--disable-breakpad", "--disable-client-side-phishing-detection", "--disable-component-extensions-with-background-pages", "--disable-component-update",
        "--no-default-browser-check", "--disable-default-apps", "--disable-dev-shm-usage", "--disable-extensions",
        "--disable-features=ImprovedCookieControls,LazyFrameLoading,GlobalMediaControls,DestroyProfileOnBrowserClose,MediaRouter,DialMediaRouteProvider,AcceptCHFrame,AutoExpandDetailsElement,CertificateTransparencyComponentUpdater,AvoidUnnecessaryBeforeUnloadCheckSync,Translate,HttpsUpgrades,PaintHolding,ThirdPartyStoragePartitioning,LensOverlay,PlzDedicatedWorker",
        "--allow-pre-commit-input", "--disable-hang-monitor", "--disable-ipc-flooding-protection", "--disable-popup-blocking", "--disable-prompt-on-repost", "--disable-renderer-backgrounding",
        "--force-color-profile=srgb", "--metrics-recording-only", "--no-first-run", "--enable-automation", "--password-store=basic", "--use-mock-keychain",
        "--no-service-autorun", "--export-tagged-pdf",
        "--disable-search-engine-choice-screen",
        "--unsafely-disable-devtools-self-xss-warnings",
        "--headless",
        "--hide-scrollbars", "--mute-audio", "--blink-settings=primaryHoverType=2,availableHoverTypes=2,primaryPointerType=4,availablePointerTypes=4",
        "--no-sandbox"};

    /** headless 일 때 Playwright 가 넣는 기본 글꼴 가족(defaultFontFamilies) — 글꼴을 따로 정하지 않은 글자의 대체 글꼴이 같아지게 */
    static final String FONTS_LINUX = "{\"fontFamilies\":{\"standard\":\"Times New Roman\",\"fixed\":\"Monospace\",\"serif\":\"Times New Roman\",\"sansSerif\":\"Arial\",\"cursive\":\"Comic Sans MS\",\"fantasy\":\"Impact\"}}";
    static final String FONTS_MAC = "{\"fontFamilies\":{\"standard\":\"Times\",\"fixed\":\"Courier\",\"serif\":\"Times\",\"sansSerif\":\"Helvetica\",\"cursive\":\"Apple Chancery\",\"fantasy\":\"Papyrus\"},\"forScripts\":["
        + "{\"script\":\"jpan\",\"fontFamilies\":{\"standard\":\"Hiragino Kaku Gothic ProN\",\"fixed\":\"Osaka-Mono\",\"serif\":\"Hiragino Mincho ProN\",\"sansSerif\":\"Hiragino Kaku Gothic ProN\"}},"
        + "{\"script\":\"hang\",\"fontFamilies\":{\"standard\":\"Apple SD Gothic Neo\",\"serif\":\"AppleMyungjo\",\"sansSerif\":\"Apple SD Gothic Neo\"}},"
        + "{\"script\":\"hans\",\"fontFamilies\":{\"standard\":\",PingFang SC,STHeiti\",\"serif\":\"Songti SC\",\"sansSerif\":\",PingFang SC,STHeiti\",\"cursive\":\"Kaiti SC\"}},"
        + "{\"script\":\"hant\",\"fontFamilies\":{\"standard\":\",PingFang TC,Heiti TC\",\"serif\":\"Songti TC\",\"sansSerif\":\",PingFang TC,Heiti TC\",\"cursive\":\"Kaiti TC\"}}]}";
    static final String FONTS_WIN = "{\"fontFamilies\":{\"standard\":\"Times New Roman\",\"fixed\":\"Consolas\",\"serif\":\"Times New Roman\",\"sansSerif\":\"Arial\",\"cursive\":\"Comic Sans MS\",\"fantasy\":\"Impact\"},\"forScripts\":["
        + "{\"script\":\"cyrl\",\"fontFamilies\":{\"standard\":\"Times New Roman\",\"fixed\":\"Courier New\",\"serif\":\"Times New Roman\",\"sansSerif\":\"Arial\"}},"
        + "{\"script\":\"arab\",\"fontFamilies\":{\"fixed\":\"Courier New\",\"sansSerif\":\"Segoe UI\"}},"
        + "{\"script\":\"grek\",\"fontFamilies\":{\"standard\":\"Times New Roman\",\"fixed\":\"Courier New\",\"serif\":\"Times New Roman\",\"sansSerif\":\"Arial\"}},"
        + "{\"script\":\"jpan\",\"fontFamilies\":{\"standard\":\",Meiryo,Yu Gothic\",\"fixed\":\"MS Gothic\",\"serif\":\",Yu Mincho,MS PMincho\",\"sansSerif\":\",Meiryo,Yu Gothic\"}},"
        + "{\"script\":\"hang\",\"fontFamilies\":{\"standard\":\"Malgun Gothic\",\"fixed\":\"Gulimche\",\"serif\":\"Batang\",\"sansSerif\":\"Malgun Gothic\",\"cursive\":\"Gungsuh\"}},"
        + "{\"script\":\"hans\",\"fontFamilies\":{\"standard\":\"Microsoft YaHei\",\"fixed\":\"NSimsun\",\"serif\":\"Simsun\",\"sansSerif\":\"Microsoft YaHei\",\"cursive\":\"KaiTi\"}},"
        + "{\"script\":\"hant\",\"fontFamilies\":{\"standard\":\"Microsoft JhengHei\",\"fixed\":\"MingLiU\",\"serif\":\"PMingLiU\",\"sansSerif\":\"Microsoft JhengHei\",\"cursive\":\"DFKai-SB\"}}]}";

    private Process proc;
    private Path profile;
    private File errlog;
    private WebSocket ws;
    private String session;                         // 쪽(target)에 붙은 세션 — null 이면 브라우저에 보낸다
    private final AtomicInteger seq = new AtomicInteger();
    private final ConcurrentHashMap<Integer, CompletableFuture<Map<String, Object>>> pending = new ConcurrentHashMap<>();
    private final AtomicLong loads = new AtomicLong();      // Page.loadEventFired 를 받은 횟수
    private final Object loadLock = new Object();
    private volatile boolean dead;
    private volatile String deadWhy = "";

    private Cdp() {}

    // ── 띄우기 ───────────────────────────────────────────
    /** 브라우저를 띄우고 쪽 하나(뷰포트 width × height)를 열어 돌려준다. 실패하면 띄운 프로세스 · 임시 프로필을 치우고 예외 */
    public static Cdp launch(String exe, int width, int height) {
        Cdp c = new Cdp();
        try {
            c.start(exe);
            c.open_page(width, height);
            return c;
        } catch (RuntimeException ex) {
            c.close();
            throw ex;
        }
    }

    private void start(String exe) {
        try {
            profile = Files.createTempDirectory(Py.fmt("sp_chrome_profile_%d_", ProcessHandle.current().pid()));
            errlog = new File(profile.toFile(), "sp_browser_stderr.log");
            List<String> cmd = new ArrayList<>();
            cmd.add(exe);
            for (String s : SWITCHES) cmd.add(s);
            cmd.add("--user-data-dir=" + profile);
            cmd.add("--remote-debugging-port=0");
            cmd.add("--no-startup-window");
            ProcessBuilder pb = new ProcessBuilder(cmd);
            pb.redirectOutput(ProcessBuilder.Redirect.DISCARD);
            pb.redirectError(errlog);
            proc = pb.start();
        } catch (IOException ex) { throw new RuntimeException("브라우저를 띄우지 못함 : " + exe + " — " + ex.getMessage(), ex); }
        String url = wait_endpoint(exe);
        try {
            HttpClient http = HttpClient.newBuilder().proxy(HttpClient.Builder.NO_PROXY).connectTimeout(Duration.ofSeconds(30)).build();
            ws = http.newWebSocketBuilder().connectTimeout(Duration.ofSeconds(30)).buildAsync(URI.create(url), new Listener()).get(60, TimeUnit.SECONDS);
        } catch (InterruptedException | ExecutionException | TimeoutException ex) {
            throw new RuntimeException("브라우저 조종 주소에 연결하지 못함 : " + url + " — " + ex, ex);
        }
    }

    /** 브라우저가 프로필 폴더에 적는 DevToolsActivePort(첫 줄 = 포트 · 둘째 줄 = 경로)를 기다린다. 없으면 표준 오류의 「DevTools listening on ws://…」 */
    private String wait_endpoint(String exe) {
        Path f = profile.resolve("DevToolsActivePort");
        long end = System.currentTimeMillis() + LAUNCH_MS;
        while (System.currentTimeMillis() < end) {
            try {
                if (Files.exists(f)) {
                    List<String> ls = Files.readAllLines(f);
                    if (ls.size() >= 2 && !ls.get(0).trim().isEmpty() && ls.get(1).trim().startsWith("/")) return "ws://127.0.0.1:" + ls.get(0).trim() + ls.get(1).trim();
                }
                java.util.regex.Matcher m = Py.search("DevTools listening on (ws://\\S+)", err_tail(20000));
                if (m != null) return m.group(1);
            } catch (IOException ignore) { }
            if (!proc.isAlive()) throw new RuntimeException("브라우저가 뜨자마자 끝남(종료코드 " + proc.exitValue() + ") : " + exe + " — " + err_tail(600));
            try { Thread.sleep(25); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); throw new RuntimeException("브라우저 띄우기가 중단됨", ex); }
        }
        throw new RuntimeException("브라우저가 " + (LAUNCH_MS / 1000) + "초 안에 뜨지 않음 : " + exe + " — " + err_tail(600));
    }

    private String err_tail(int n) {
        try {
            if (errlog == null || !errlog.exists()) return "";
            String s = new String(Files.readAllBytes(errlog.toPath()), java.nio.charset.StandardCharsets.UTF_8);
            return s.length() > n ? s.substring(s.length() - n) : s;
        } catch (IOException ex) { return ""; }
    }

    /** 새 브라우저 컨텍스트 · 쪽을 만들고 Playwright 가 headless 쪽에 하는 설정(초점 흉내 · 뷰포트 · 기본 글꼴 · 매체 기본값 · 창 크기)을 한다 */
    private void open_page(int width, int height) {
        String ua = Py.gs0(send("Browser.getVersion", Py.dict()), "userAgent");
        String ctx = Py.gs(send("Target.createBrowserContext", Py.dict("disposeOnDetach", true)), "browserContextId");
        String target = Py.gs(send("Target.createTarget", Py.dict("url", "about:blank", "browserContextId", ctx)), "targetId");
        String sid = Py.gs(send("Target.attachToTarget", Py.dict("targetId", target, "flatten", true)), "sessionId");
        Object win = null;
        try { win = send("Browser.getWindowForTarget", Py.dict("targetId", target)).get("windowId"); } catch (RuntimeException ignore) { }
        session = sid;
        send("Page.enable", Py.dict());
        send("Emulation.setFocusEmulationEnabled", Py.dict("enabled", true));
        send("Emulation.setDeviceMetricsOverride", Py.dict("mobile", false, "width", (long) width, "height", (long) height, "screenWidth", (long) width, "screenHeight", (long) height,
                "deviceScaleFactor", 1L, "screenOrientation", Py.dict("angle", 0L, "type", "landscapePrimary"), "dontSetVisibleSize", false));
        if (win != null) {
            session = null;
            try { send("Browser.setWindowBounds", Py.dict("windowId", win, "bounds", Py.dict("width", (long) width, "height", (long) height))); } catch (RuntimeException ignore) { }
            session = sid;
        }
        String fam = ua.contains("Windows") ? FONTS_WIN : (ua.contains("Macintosh") ? FONTS_MAC : FONTS_LINUX);
        send("Page.setFontFamilies", Py.M(Json.parse(fam)));
        emulate_media("");
    }

    // ── 명령 ─────────────────────────────────────────────
    private final class Listener implements WebSocket.Listener {
        private final StringBuilder buf = new StringBuilder();
        @Override public CompletionStage<?> onText(WebSocket w, CharSequence data, boolean last) {
            buf.append(data);
            if (last) {
                String s = buf.toString(); buf.setLength(0);
                try { on_message(s); } catch (RuntimeException ignore) { }
            }
            w.request(1);
            return null;
        }
        @Override public CompletionStage<?> onClose(WebSocket w, int code, String reason) { die("브라우저 연결이 닫힘(closed)"); return null; }
        @Override public void onError(WebSocket w, Throwable error) { die("브라우저 연결이 끊김(disconnected) : " + error); }
    }

    private void on_message(String s) {
        Map<String, Object> m = Py.M(Json.parse(s));
        Object id = m.get("id");
        if (id != null) {
            CompletableFuture<Map<String, Object>> f = pending.remove((int) Py.lng(id));
            if (f != null) f.complete(m);
            return;
        }
        String method = Py.gs0(m, "method");
        if (method.equals("Page.loadEventFired")) { loads.incrementAndGet(); synchronized (loadLock) { loadLock.notifyAll(); } }
        else if (method.equals("Inspector.targetCrashed") || method.equals("Target.targetCrashed")) die("쪽이 죽음(Target crashed)");
        else if (method.equals("Target.detachedFromTarget") || method.equals("Target.targetDestroyed")) die("쪽이 닫힘(Target closed)");
    }

    private void die(String why) {
        if (dead) return;
        dead = true; deadWhy = why;
        for (CompletableFuture<Map<String, Object>> f : pending.values()) f.completeExceptionally(new RuntimeException(why));
        pending.clear();
        synchronized (loadLock) { loadLock.notifyAll(); }
    }

    /** 명령 하나를 보내고 답을 기다린다(120초). 쪽 세션이 열려 있으면 그 쪽에, 아니면 브라우저에 */
    public synchronized Map<String, Object> send(String method, Map<String, Object> params) { return send(method, params, TIMEOUT_MS); }
    private synchronized Map<String, Object> send(String method, Map<String, Object> params, long timeout_ms) {
        if (dead || ws == null) throw new RuntimeException(dead ? deadWhy : "브라우저 연결이 없음(closed)");
        int id = seq.incrementAndGet();
        Map<String, Object> msg = Py.dict("id", (long) id, "method", method, "params", params);
        if (session != null) msg.put("sessionId", session);
        CompletableFuture<Map<String, Object>> f = new CompletableFuture<>();
        pending.put(id, f);
        Map<String, Object> r;
        try {
            ws.sendText(Json.dumpsCompact(msg), true).get(timeout_ms, TimeUnit.MILLISECONDS);
            r = f.get(timeout_ms, TimeUnit.MILLISECONDS);
        } catch (TimeoutException ex) {
            pending.remove(id);
            throw new RuntimeException("Timeout " + timeout_ms + "ms exceeded : " + method);
        } catch (ExecutionException ex) {
            pending.remove(id);
            Throwable c = ex.getCause() != null ? ex.getCause() : ex;
            throw new RuntimeException(dead ? deadWhy : ("브라우저 연결이 끊김(disconnected) : " + c), c);
        } catch (InterruptedException ex) {
            pending.remove(id);
            Thread.currentThread().interrupt();
            throw new RuntimeException("중단됨 : " + method, ex);
        }
        Object err = r.get("error");
        if (err != null) throw new RuntimeException(method + " : " + Py.str(Py.get(err, "message")));
        Object res = r.get("result");
        return res == null ? Py.dict() : Py.M(res);
    }

    // ── 쪽 다루기 ────────────────────────────────────────
    /** 살아 있는지 — 프로세스 · 연결 · 쪽 */
    public boolean alive() { return !dead && proc != null && proc.isAlive() && ws != null && !ws.isInputClosed() && !ws.isOutputClosed(); }

    /** pg.emulate_media(media=…) — Playwright 처럼 색 구성 light · 움직임 no-preference · 강제 색 none 을 함께 보낸다 */
    public void emulate_media(String media) {
        send("Emulation.setEmulatedMedia", Py.dict("media", media, "features", Py.list(
                Py.dict("name", "prefers-color-scheme", "value", "light"),
                Py.dict("name", "prefers-reduced-motion", "value", "no-preference"),
                Py.dict("name", "forced-colors", "value", "none"))));
    }

    /** pg.goto(url, wait_until='load') */
    public void navigate(String url) {
        long before = loads.get();
        Map<String, Object> r = send("Page.navigate", Py.dict("url", url));
        if (Py.truthy(r.get("errorText"))) throw new RuntimeException("쪽을 열지 못함 : " + r.get("errorText") + " — " + url);
        long end = System.currentTimeMillis() + TIMEOUT_MS;
        synchronized (loadLock) {
            while (loads.get() <= before) {
                if (dead) throw new RuntimeException(deadWhy);
                long left = end - System.currentTimeMillis();
                if (left <= 0) throw new RuntimeException("Timeout " + TIMEOUT_MS + "ms exceeded : 쪽 열림(load) 기다리기");
                try { loadLock.wait(Math.min(left, 200)); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); throw new RuntimeException("중단됨", ex); }
            }
        }
    }

    /** 식 하나를 평가해 값으로 돌려받는다(약속이면 끝날 때까지 기다림). 값 꼴 : 정수 → Long · 소수 → Double · 배열 → List · 객체 → Map(차례 유지) · undefined/null → null */
    public Object evaluate(String expression) {
        Map<String, Object> r = send("Runtime.evaluate", Py.dict("expression", expression, "awaitPromise", true, "returnByValue", true));
        Object ex = r.get("exceptionDetails");
        if (ex != null) {
            Object e = Py.get(ex, "exception");
            String d = e != null ? Py.str(Py.or(Py.get(e, "description"), Py.get(e, "value"))) : Py.str(Py.get(ex, "text"));
            throw new RuntimeException("쪽 안의 스크립트 오류 : " + d);
        }
        return Py.get(r.get("result"), "value");
    }

    /** pg.evaluate('함수 글자', 인자) — 함수 글자를 그대로 두고 인자를 넘겨 부른다 */
    public Object call(String fn, Object... args) {
        StringBuilder b = new StringBuilder("(").append(fn).append("\n)(");
        for (int i = 0; i < args.length; i++) { if (i > 0) b.append(','); b.append(Json.dumpsU(args[i])); }
        return evaluate(b.append(')').toString());
    }

    /** pg.wait_for_function(식) — 식이 참이 될 때까지(화면 갱신 때마다 다시 봄) */
    public void wait_for(String expression) {
        evaluate("new Promise(r=>{const f=()=>{if(" + expression + ")r(1);else requestAnimationFrame(f)};f()})");
    }

    /**
     * pg.pdf(…) — Playwright crPdf 와 같은 인자로 Page.printToPDF. paper_w · paper_h 는 인치(없으면 8.5 × 11).
     * 여백 0 · 배율 1 · 머리글/바닥글 없음 · 꼬리표(tagged) · 책갈피 없음.
     */
    public void pdf(String path, Double paper_w, Double paper_h, boolean print_background, boolean prefer_css_page_size) {
        Map<String, Object> r = send("Page.printToPDF", Py.dict(
                "transferMode", "ReturnAsStream", "landscape", false, "displayHeaderFooter", false, "headerTemplate", "", "footerTemplate", "",
                "printBackground", print_background, "scale", 1L,
                "paperWidth", paper_w != null ? (Object) paper_w : (Object) 8.5, "paperHeight", paper_h != null ? (Object) paper_h : (Object) 11L,
                "marginTop", 0L, "marginBottom", 0L, "marginLeft", 0L, "marginRight", 0L, "pageRanges", "",
                "preferCSSPageSize", prefer_css_page_size, "generateTaggedPDF", false, "generateDocumentOutline", false));
        String h = Py.gs(r, "stream");
        java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream();
        while (true) {
            Map<String, Object> c = send("IO.read", Py.dict("handle", h));
            String data = Py.gs0(c, "data");
            byte[] bs = Py.truthy(c.get("base64Encoded")) ? Base64.getDecoder().decode(data) : data.getBytes(java.nio.charset.StandardCharsets.UTF_8);
            out.write(bs, 0, bs.length);
            if (Py.truthy(c.get("eof"))) break;
        }
        send("IO.close", Py.dict("handle", h));
        try {
            Path p = Paths.get(path);
            if (p.getParent() != null) Files.createDirectories(p.getParent());
            Files.write(p, out.toByteArray());
        } catch (IOException ex) { throw new RuntimeException("PDF 를 쓰지 못함 : " + path, ex); }
    }

    // ── 닫기 ─────────────────────────────────────────────
    /** 브라우저를 닫고(안 닫히면 죽이고) 임시 프로필을 지운다. 여러 번 불러도 된다 · 예외를 내지 않는다 */
    public void close() {
        try {
            if (ws != null && !dead && proc != null && proc.isAlive()) {
                session = null;
                try { send("Browser.close", Py.dict(), 5000); } catch (RuntimeException ignore) { }
            }
        } catch (RuntimeException ignore) { }
        dead = true; if (deadWhy.isEmpty()) deadWhy = "브라우저를 닫음(closed)";
        try { if (ws != null) ws.abort(); } catch (RuntimeException ignore) { }
        ws = null;
        if (proc != null) {
            try {
                if (!proc.waitFor(5, TimeUnit.SECONDS)) {
                    proc.descendants().forEach(ProcessHandle::destroyForcibly);
                    proc.destroyForcibly();
                    proc.waitFor(5, TimeUnit.SECONDS);
                }
            } catch (InterruptedException ex) { Thread.currentThread().interrupt(); proc.destroyForcibly(); }
            proc = null;
        }
        if (profile != null) {
            for (int k = 0; k < 20 && Files.exists(profile); k++) {       // 브라우저가 끝나며 마지막으로 쓰는 파일이 있을 수 있다 — 잠깐씩 다시
                Render.rmtree(profile);
                if (Files.exists(profile)) { try { Thread.sleep(100); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); break; } }
            }
            profile = null;
        }
    }
}
