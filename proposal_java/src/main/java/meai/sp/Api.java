package meai.sp;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.Semaphore;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 파이썬 api.py 의 **담보코드 입력 길** — 같은 주소 · 같은 응답 꼴(JDK 내장 HTTP 서버 · 바깥 부품 없음).
 *
 *   GET  /health                헬스체크
 *   POST /v1/ga2/json/pdf       담보 목록 JSON → 새 양식 PDF
 *   POST /v1/ga2/json/all       담보 목록 JSON → 새 양식 PDF(base64) + 쪽수 · 계산 로그 · 담보마다 찾은 특약
 *   POST /v1/ga2/json/check     담보 목록 JSON → PDF 를 만들지 않고 입력 점검 + 담보 인식 결과만
 *
 * 설계서 PDF 를 올리는 주소(/v1/ga2/pdf 등)는 자바 판에 없다(400 으로 알려 준다).
 * 생성은 한 번에 1건(작업 스레드 하나 — 브라우저를 그 스레드에서만 쓴다) · 2건까지 받아 두고 나머지는 180초 기다린 뒤 503.
 */
public final class Api {
    private Api() {}

    /** 계산 판(파이썬 api.VERSION 과 같은 값)과 자바 판 표시 */
    public static final String ENGINE_VERSION = "v9.14";
    public static final String VERSION = ENGINE_VERSION + "-java";
    public static final int JSON_MAX = 2 * 1024 * 1024;                 // 담보코드 입력(JSON) 상한 2MB
    static final Semaphore LOCK = new Semaphore(2, true);                // 생성 요청은 2건까지 받아 두고(1건 처리 + 1건 대기) 나머지는 180초 기다린 뒤 503
    static final ReentrantLock GA_LOCK = new ReentrantLock();            // 실제 계산은 한 번에 한 건 — 설계 상태 · 계산 로그가 static 이다
    public static final long GA2_TIMEOUT = timeout_env();                // 새 양식 1건 제한 시간(초)
    static volatile boolean BROKEN = false;                              // 작업이 제한 시간을 넘겨 멈추면 true — /health 가 503
    static final String TMP_PREFIX = Py.fmt("sp_in_%d_", ProcessHandle.current().pid());
    static final ExecutorService GA2_WORKER = Executors.newSingleThreadExecutor(r -> { Thread t = new Thread(r, "ga2"); t.setDaemon(true); return t; });
    static final Map<String, Object> CARE_NM = Py.dict("support", "간병인 지원", "use", "간병인 사용", "none", "간병인 지원 · 사용 함께(둘 다 미가입)");

    private static long timeout_env() {
        String e = Py.env("GA2_TIMEOUT");
        try { return (e == null || e.isEmpty()) ? 600 : Long.parseLong(e.trim()); } catch (NumberFormatException ex) { return 600; }
    }

    /** 처리 중에 서버가 꺼져 남은 중간 파일을 치운다 — 만든 지 1시간 넘은 것만 */
    public static int sweep() { return sweep(3600); }
    public static int sweep(long max_age) {
        int n = 0;
        File[] ds = new File(System.getProperty("java.io.tmpdir")).listFiles((d, nm) -> nm.startsWith("sp_in_"));
        if (ds != null) for (File d : ds) {
            if (System.currentTimeMillis() / 1000.0 - d.lastModified() / 1000.0 > max_age) { rmtree(d.toPath()); n++; }
        }
        try { n += Render.sweep_tmp(max_age); } catch (RuntimeException ignore) { }
        return n;
    }
    static void rmtree(Path p) {
        try (java.util.stream.Stream<Path> w = Files.walk(p)) {
            w.sorted(java.util.Comparator.reverseOrder()).forEach(x -> { try { Files.deleteIfExists(x); } catch (IOException ignore) { } });
        } catch (IOException ignore) { }
    }

    /** 입력 점검 + 담보 인식 결과(PDF 를 만들지 않는다) — /v1/ga2/json/check 와 명령줄 --check 가 같이 쓴다 */
    public static Map<String, Object> check(Map<String, Object> p) {
        GA_LOCK.lock();
        try {
            ScenEngine.ISSUES.clear();
            List<Object> rid = CodeInput.riders(p);
            long matched = 0;
            for (Object r : rid) if (Py.truthy(Py.get(r, "matched"))) matched++;
            return Py.dict("ok", true, "format", "ga2-json-check", "line", p.get("_line"), "rider_count", (long) rid.size(), "matched", matched,
                    "recog", ScenEngine.recog(rid), "riders", rid, "issues", ScenEngine.issues_grouped());
        } finally { GA_LOCK.unlock(); }
    }

    /** 새 양식 한 건 — 작업 스레드(GA2_WORKER) 안에서만 부른다 */
    static Map<String, Object> ga2_build(Map<String, Object> src, String out) {
        GA_LOCK.lock();
        try {
            Object[] r = GaV2.build(src, out);
            List<Object> rid = GaProposal.RID;
            long matched = 0;
            for (Object x : rid) if (Py.truthy(Py.get(x, "matched"))) matched++;
            return Py.dict("info", r[2], "log", Py.readText((String) r[1]), "premium", GaProposal.PREMIUM, "riders", rid, "matched", matched, "body", Py.readBytes(out));
        } finally { GA_LOCK.unlock(); }
    }

    static byte[] _json(Object o) { return Json.dumpsU(o).getBytes(StandardCharsets.UTF_8); }

    // ── 응답 ────────────────────────────────────────────────
    static void _cors(HttpExchange x) {
        x.getResponseHeaders().set("Access-Control-Allow-Origin", "*");
        x.getResponseHeaders().set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        x.getResponseHeaders().set("Access-Control-Allow-Headers", "Content-Type");
    }
    static void _send(HttpExchange x, int code, byte[] body, String ctype, String fname) throws IOException {
        x.getResponseHeaders().set("Server", "SmartProposal/" + VERSION);
        x.getResponseHeaders().set("Content-Type", ctype);
        if (fname != null) x.getResponseHeaders().set("Content-Disposition", Py.fmt("inline; filename=\"%s\"; filename*=UTF-8''%s", fname, fname));
        _cors(x);
        x.sendResponseHeaders(code, body.length == 0 ? -1 : body.length);
        if (body.length > 0) try (OutputStream o = x.getResponseBody()) { o.write(body); }
        System.err.println(Py.fmt("[api] %s - \"%s %s\" %d", x.getRemoteAddress().getAddress().getHostAddress(), x.getRequestMethod(), x.getRequestURI().getRawPath(), (long) code));
    }
    static void _send(HttpExchange x, int code, byte[] body) throws IOException { _send(x, code, body, "application/json; charset=utf-8", null); }
    static void _err(HttpExchange x, int code, String msg) throws IOException { _send(x, code, _json(Py.dict("ok", false, "error", msg))); }

    static void handle(HttpExchange x) {
        try {
            String m = x.getRequestMethod(), path = x.getRequestURI().getRawPath();
            if (m.equals("OPTIONS")) { _cors(x); x.sendResponseHeaders(204, -1); }
            else if (m.equals("GET")) do_GET(x, path);
            else if (m.equals("POST")) do_POST(x, path);
            else _err(x, 501, "Unsupported method : " + m);
        } catch (IOException ex) {
            System.err.println("[api] 응답을 보내지 못함 : " + ex);
        } catch (Throwable ex) {
            ex.printStackTrace();
            try { _err(x, 500, Py.fmt("생성 중 오류 : %s", ex.getMessage() != null ? ex.getMessage() : ex.getClass().getSimpleName())); } catch (IOException ignore) { }
        } finally { x.close(); }
    }

    static void do_GET(HttpExchange x, String path) throws IOException {
        if (path.equals("/") || path.equals("/index.html")) {
            String h = "<!doctype html><meta charset=\"utf-8\"><title>Smart Proposal API (Java)</title><h1>스마트 제안서 API " + VERSION + "</h1>"
                    + "<p>담보코드 입력(JSON) 전용입니다 — <code>POST /v1/ga2/json/pdf</code> · <code>/v1/ga2/json/all</code> · <code>/v1/ga2/json/check</code> · <code>GET /health</code></p>";
            _send(x, 200, h.getBytes(StandardCharsets.UTF_8), "text/html; charset=utf-8", null);
            return;
        }
        if (path.equals("/health")) {
            if (BROKEN) { _send(x, 503, _json(Py.dict("ok", false, "version", VERSION, "error", "새 양식 작업이 멈춰 있습니다 — 서버를 다시 켜 주세요"))); return; }
            _send(x, 200, _json(Py.dict("ok", true, "version", VERSION, "engine", "java", "java", System.getProperty("java.version"), "llm", false, "network", false,
                    "formats", Py.dict("ga2", "/v1/ga2/json/*"))));
            return;
        }
        _err(x, 404, "not found : " + path);
    }

    static void drain(HttpExchange x) {
        try (InputStream in = x.getRequestBody()) { byte[] b = new byte[65536]; long tot = 0; int k; while ((k = in.read(b)) > 0 && (tot += k) < 128L * 1024 * 1024) { } } catch (IOException ignore) { }
    }

    static void do_POST(HttpExchange x, String path) throws IOException {
        if (!(path.startsWith("/v1/proposal") || path.startsWith("/v1/ga"))) { drain(x); _err(x, 404, "not found : " + path); return; }
        if (path.startsWith("/v1/ga2/json/")) { _ga2_json(x, path); return; }
        drain(x);
        _err(x, 400, "자바 판은 담보코드 입력(JSON)만 받습니다 — /v1/ga2/json/pdf · /v1/ga2/json/all · /v1/ga2/json/check 를 써 주세요(설계서 PDF 업로드는 파이썬 판에 있습니다)");
    }

    /** 담보코드 입력 — 본문은 JSON(사양 CodeInput). 입력이 사양과 다르면 400 + 이유, 만들지 않는 경우 422 */
    static void _ga2_json(HttpExchange x, String path) throws IOException {
        if (!(path.equals("/v1/ga2/json/pdf") || path.equals("/v1/ga2/json/all") || path.equals("/v1/ga2/json/check"))) { drain(x); _err(x, 404, "not found : " + path); return; }
        long n;
        try { String cl = x.getRequestHeaders().getFirst("Content-Length"); n = (cl == null || cl.trim().isEmpty()) ? 0 : Long.parseLong(cl.trim()); } catch (NumberFormatException ex) { n = 0; }
        if (n <= 0) { drain(x); _err(x, 400, "본문이 비어 있습니다 — 담보 목록 JSON 을 보내 주세요"); return; }
        if (n > JSON_MAX) { drain(x); _err(x, 400, Py.fmt("JSON 상한(%dMB)을 넘었습니다", (long) (JSON_MAX / 1024 / 1024))); return; }
        byte[] raw = x.getRequestBody().readNBytes((int) n);
        Map<String, Object> p;
        try {
            String txt = StandardCharsets.UTF_8.newDecoder().onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT).decode(ByteBuffer.wrap(raw)).toString();
            if (!txt.isEmpty() && txt.charAt(0) == '﻿') txt = txt.substring(1);
            p = CodeInput.parse(txt);
        } catch (CharacterCodingException ex) {
            _err(x, 400, "본문을 UTF-8 로 읽지 못했습니다"); return;
        } catch (CodeInput.InputError ex) {
            _err(x, 400, Py.fmt("입력이 사양과 다릅니다 — %s", ex.getMessage())); return;
        }
        sweep();
        Path tmp = Files.createTempDirectory(TMP_PREFIX);
        boolean got;
        try { got = LOCK.tryAcquire(180, TimeUnit.SECONDS); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); got = false; }
        if (!got) { rmtree(tmp); _err(x, 503, "처리 대기가 길어졌습니다 — 잠시 후 다시 시도해 주세요"); return; }
        try {
            if (path.equals("/v1/ga2/json/check")) { _send(x, 200, _json(check(p))); return; }
            if (BROKEN) { _err(x, 503, "새 양식 작업이 멈춰 있습니다 — 서버를 다시 켜 주세요"); return; }
            Map<String, Object> r;
            final Map<String, Object> pp = p;
            final String out = tmp.resolve("ga2_proposal.pdf").toString();
            Future<Map<String, Object>> fu = GA2_WORKER.submit(() -> ga2_build(pp, out));
            try {
                r = fu.get(GA2_TIMEOUT, TimeUnit.SECONDS);
            } catch (TimeoutException ex) {
                BROKEN = true;
                _err(x, 504, Py.fmt("처리 시간이 %d초를 넘었습니다 — 서버를 다시 켜 주세요", GA2_TIMEOUT)); return;
            } catch (ExecutionException ex) {
                Throwable c = ex.getCause() != null ? ex.getCause() : ex;
                if (c instanceof RuntimeException) throw (RuntimeException) c;
                if (c instanceof Error) throw (Error) c;
                throw new RuntimeException(c);
            } catch (InterruptedException ex) { Thread.currentThread().interrupt(); throw new RuntimeException(ex); }
            byte[] body = (byte[]) r.get("body");
            if (path.equals("/v1/ga2/json/pdf")) { _send(x, 200, body, "application/pdf", "ga2_proposal.pdf"); return; }
            Map<String, Object> i = Py.M(r.get("info"));
            List<Object> ko = new ArrayList<>();
            for (Object k : Py.gl(i, "care")) ko.add(Py.at(CARE_NM, k));
            Map<String, Object> o = new LinkedHashMap<>();
            o.put("ok", true); o.put("format", "ga2"); o.put("input", "json"); o.put("line", p.get("_line")); o.put("product", i.get("product")); o.put("premium", r.get("premium"));
            o.put("pages", i.get("pages")); o.put("detail_pages", i.get("detail_pages"));
            o.put("care_pages", i.get("care")); o.put("care_pages_ko", ko);
            o.put("rider_count", i.get("riders")); o.put("matched", r.get("matched")); o.put("warn", i.get("warn"));
            o.put("elapsed_sec", i.get("sec")); o.put("log", r.get("log")); o.put("riders", r.get("riders"));
            o.put("pdf_base64", Base64.getEncoder().encodeToString(body));
            _send(x, 200, _json(o));
        } catch (Pipeline.DesignUnreadable ex) {
            _err(x, 422, Py.fmt("만들지 않았습니다 — %s", ex.getMessage()));
        } catch (RuntimeException | Error ex) {
            ex.printStackTrace();
            _err(x, 500, Py.fmt("생성 중 오류 : %s", (ex.getMessage() != null && !ex.getMessage().isEmpty()) ? ex.getMessage() : ex.getClass().getSimpleName()));
        } finally {
            LOCK.release();
            rmtree(tmp);
        }
    }

    /** 서버를 띄운다(끝나지 않는다 — Ctrl+C 로 종료) */
    public static void serve(String host, int port) throws IOException {
        Files.createDirectories(Paths.get(Py.path("out")));
        int n = sweep();
        if (n > 0) System.out.println(Py.fmt("지난번에 처리 중 남은 임시 파일 %d개를 지웠습니다", (long) n));
        HttpServer srv = HttpServer.create(new InetSocketAddress(host, port), 64);
        srv.createContext("/", Api::handle);
        srv.setExecutor(Executors.newCachedThreadPool(r -> { Thread t = new Thread(r, "http"); t.setDaemon(true); return t; }));
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try { GA2_WORKER.submit(Render::close_browser).get(20, TimeUnit.SECONDS); } catch (Exception ignore) { }      // 띄워 둔 크로뮴은 그 스레드에서 닫는다
            GA2_WORKER.shutdownNow();
        }));
        srv.start();
        System.out.println(Py.fmt("스마트 제안서 API %s — http://%s:%d  (Ctrl+C 로 종료)", VERSION, host, (long) port));
        System.out.println("  담보코드 입력(JSON) 전용 : POST /v1/ga2/json/pdf · /v1/ga2/json/all · /v1/ga2/json/check · GET /health");
        try { Thread.currentThread().join(); } catch (InterruptedException ex) { Thread.currentThread().interrupt(); }
    }
}
