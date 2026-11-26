package meai.sp;

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * 명령줄 — 파이썬 `python ga_v2.py --json` 과 같은 일을 한다(출력 글자 · 종료코드 0 / 1 / 2 · _log.txt).
 *
 *   java -jar smart-proposal.jar --json &lt;입력.json&gt; [결과.pdf] [나이]     담보코드 입력 → 새 양식 PDF
 *   java -jar smart-proposal.jar --check &lt;입력.json&gt;                     PDF 없이 입력 점검 + 담보 인식 결과(JSON)
 *   java -jar smart-proposal.jar serve [호스트] [포트]                     HTTP 서버(기본 127.0.0.1 8080)
 *   java -jar smart-proposal.jar --version
 *
 * 환경변수(= 시스템 속성 -D 로도) : SP_HOME 자료 폴더 · GA_CODE_MAP 담보 식별표 · GA_CHROMIUM 브라우저 경로 · GA_MASK=1 개인정보 가림 · GA_V2_KEEP=1 중간 파일 남김
 */
public final class Main {
    private Main() {}

    static final String USAGE = "사용 : java -jar smart-proposal.jar --json <입력.json> [결과.pdf]\n"
            + "       java -jar smart-proposal.jar --check <입력.json>\n"
            + "       java -jar smart-proposal.jar serve [호스트] [포트]";

    public static void main(String[] argv) {
        try {
            System.setOut(new PrintStream(new FileOutputStream(FileDescriptor.out), true, "UTF-8"));
            System.setErr(new PrintStream(new FileOutputStream(FileDescriptor.err), true, "UTF-8"));
        } catch (java.io.UnsupportedEncodingException ignore) { }
        int rc;
        try { rc = run(argv); }
        catch (Throwable ex0) {
            Throwable ex = (ex0 instanceof ExceptionInInitializerError && ex0.getCause() != null) ? ex0.getCause() : ex0;
            System.out.println(Py.fmt("! 만들지 못했습니다 : %s: %s", ex.getClass().getSimpleName(), ex.getMessage()));
            if (!Py.exists(Py.path("rules.json"))) System.out.println("  자료 폴더(rules.json · db.json · ga_assets …)를 찾지 못했습니다 — 환경변수 SP_HOME 또는 -Dsp.home=<폴더> 로 알려 주세요(지금 : " + Py.BASE + ")");
            ex.printStackTrace();
            rc = 1;
        }
        try { Render.close_browser(); } catch (Throwable ignore) { }
        System.out.flush(); System.err.flush();
        System.exit(rc);
    }

    public static int run(String[] argv) throws Exception {
        List<String> args = new ArrayList<>();
        for (String a : argv) if (!Py.strip(a).isEmpty()) args.add(a);
        String age = "";
        if (!args.isEmpty() && Py.fullmatch("\\d{1,3}세?", args.get(args.size() - 1)) != null && !(args.get(0).equals("serve"))) {
            age = args.remove(args.size() - 1);
            age = age.endsWith("세") ? age : age + "세";
        }
        if (args.isEmpty()) { System.out.println(USAGE); return 1; }
        String cmd = args.get(0);
        if (cmd.equals("--version") || cmd.equals("-v")) { System.out.println(Api.VERSION); return 0; }
        if (cmd.equals("serve")) {
            String host = args.size() > 1 ? args.get(1) : "127.0.0.1";
            int port = args.size() > 2 ? Integer.parseInt(args.get(2)) : 8080;
            Api.serve(host, port);
            return 0;
        }
        if (cmd.equals("--check")) {
            if (args.size() < 2) { System.out.println("사용 : java -jar smart-proposal.jar --check <입력.json>"); return 1; }
            try {
                System.out.println(Json.dumpsU(Api.check(CodeInput.parse(Py.read(args.get(1))))));
            } catch (CodeInput.InputError ex) { System.out.println(Py.fmt("! 입력이 사양과 다릅니다 — %s", ex.getMessage())); return 2; }
            return 0;
        }
        if (cmd.equals("--json")) {      // 담보코드 입력 : --json <입력.json> [결과.pdf]  (사양 CodeInput)
            if (args.size() < 2) { System.out.println("사용 : java -jar smart-proposal.jar --json <입력.json> [결과.pdf]"); return 1; }
            try {
                Map<String, Object> p = CodeInput.parse(Py.read(args.get(1)));
                Object[] r = GaV2.build(p, args.size() > 2 ? args.get(2) : null, age);
                Map<String, Object> info = Py.M(r[2]);
                List<Object> warn = Py.gl(info, "warn");
                System.out.println(Py.fmt("→ %s  (%d쪽 · 간병인 %s · 세부내역 %d쪽 · 담보 %d건)%s", r[0], info.get("pages"), Py.join("+", Py.gl(info, "care")), info.get("detail_pages"), info.get("riders"),
                        !warn.isEmpty() ? ("  ※ " + Py.join(" / ", warn)) : ""));
            } catch (CodeInput.InputError ex) { System.out.println(Py.fmt("! 입력이 사양과 다릅니다 — %s", ex.getMessage())); return 2; }
            catch (Pipeline.DesignUnreadable ex) { System.out.println(Py.fmt("! 만들지 않았습니다 — %s", ex.getMessage())); return 2; }
            return 0;
        }
        System.out.println(USAGE);
        return 1;
    }
}
