package meai.sp;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.text.PDFTextStripper;
import org.apache.pdfbox.text.TextPosition;

/**
 * 인수 시험 — 받은 묶음이 정답(파이썬 판이 만든 결과)과 같은 결과를 내는지 파이썬 없이 확인한다.
 *
 *   java -jar smart-proposal.jar --selftest &lt;폴더&gt; [이름 …]
 *
 * 폴더에는 입력 &lt;이름&gt;.json · 정답 PDF &lt;이름&gt;.expected.pdf · 정답 요약 &lt;이름&gt;.expected.json 이 있다(golden/make_selftest.py 가 만든다).
 * 입력마다 PDF 를 만들어 &lt;폴더&gt;/out/&lt;이름&gt;.pdf 에 두고 견준다 :
 *   ① 요약(쪽수 · 간병인 쪽 · 세부내역 쪽수 · 담보 수 · 인식 수 · 상품 · 보험료 · 경고 · 계산 로그 글자)
 *   ② 쪽수 · 쪽 크기
 *   ③ 쪽별 글자 — 정답 PDF 와 만든 PDF 를 같은 방법(PDFBox)으로 읽어 공백을 지운 글자가 같은지 + 글자마다 자리가 0.5pt 안인지
 * 정답이 「만들지 않음」(입력 사양 위반 · 담보를 못 찾음 등)이면 같은 까닭으로 멈추는지 본다.
 * 다 같으면 「결과 : 전부 통과 — N건 · N쪽」 · 종료코드 0, 아니면 다른 곳을 적고 1.
 */
public final class SelfTest {
    private SelfTest() {}

    static final double TOL_PT = 0.5;
    static final String SEC_RE = " · [\\d.]+초$";      // 로그 넷째 줄 끝의 처리 시간

    /** 쪽의 글자를 자리와 함께 모은다(공백 글자는 뺀다) */
    static final class Glyphs extends PDFTextStripper {
        final List<Object[]> out = new ArrayList<>();      // {글자, x, y}
        Glyphs() throws IOException { super(); }
        @Override protected void processTextPosition(TextPosition t) {
            String u = t.getUnicode();
            if (u != null && !Py.strip(u).isEmpty()) out.add(new Object[]{u, (double) t.getXDirAdj(), (double) t.getYDirAdj()});
            super.processTextPosition(t);
        }
    }

    static String page_text(PDDocument d, int pno) throws IOException {
        PDFTextStripper st = new PDFTextStripper();
        st.setSortByPosition(true); st.setStartPage(pno + 1); st.setEndPage(pno + 1);
        return Py.sub("\\s+", "", st.getText(d));
    }

    static List<Object[]> page_glyphs(PDDocument d, int pno) throws IOException {
        Glyphs g = new Glyphs();
        g.setStartPage(pno + 1); g.setEndPage(pno + 1);
        g.getText(d);
        return g.out;
    }

    /** 두 PDF 를 견준다 — 다른 곳을 글자로 돌려준다(없으면 빈 목록). 돌려주는 [0] = 쪽수 */
    static int compare_pdf(String want, String got, List<String> diff) throws IOException {
        try (PDDocument a = Loader.loadPDF(new File(want)); PDDocument b = Loader.loadPDF(new File(got))) {
            int n = a.getNumberOfPages();
            if (n != b.getNumberOfPages()) { diff.add(Py.fmt("쪽수 : 정답 %d쪽 ≠ 만든 것 %d쪽", n, b.getNumberOfPages())); return n; }
            for (int i = 0; i < n; i++) {
                PDRectangle ra = a.getPage(i).getMediaBox(), rb = b.getPage(i).getMediaBox();
                if (Math.abs(ra.getWidth() - rb.getWidth()) > 0.01 || Math.abs(ra.getHeight() - rb.getHeight()) > 0.01)
                    diff.add(Py.fmt("%d쪽 크기 : 정답 %.2f×%.2f ≠ 만든 것 %.2f×%.2f", i + 1, ra.getWidth(), ra.getHeight(), rb.getWidth(), rb.getHeight()));
                String ta = page_text(a, i), tb = page_text(b, i);
                if (!ta.equals(tb)) {
                    int k = 0, m = Math.min(ta.length(), tb.length());
                    while (k < m && ta.charAt(k) == tb.charAt(k)) k++;
                    diff.add(Py.fmt("%d쪽 글자 : %d번째부터 다름 — 정답 「…%s」 ≠ 만든 것 「…%s」", i + 1, k + 1,
                            Py.slice(ta, Math.max(0, k - 12), k + 24), Py.slice(tb, Math.max(0, k - 12), k + 24)));
                    continue;
                }
                List<Object[]> ga = page_glyphs(a, i), gb = page_glyphs(b, i);
                if (ga.size() != gb.size()) { diff.add(Py.fmt("%d쪽 글자 수 : 정답 %d ≠ 만든 것 %d", i + 1, ga.size(), gb.size())); continue; }
                Map<String, List<double[]>> pool = new LinkedHashMap<>();        // 글자 → 만든 PDF 에서의 자리들(차례에 기대지 않고 가까운 것끼리 짝짓는다)
                for (Object[] g : gb) pool.computeIfAbsent((String) g[0], x -> new ArrayList<>()).add(new double[]{(Double) g[1], (Double) g[2]});
                int miss = 0; String first = null;
                for (Object[] g : ga) {
                    List<double[]> c = pool.get((String) g[0]);
                    int hit = -1;
                    if (c != null) for (int j = 0; j < c.size(); j++) {
                        if (Math.abs(c.get(j)[0] - (Double) g[1]) <= TOL_PT && Math.abs(c.get(j)[1] - (Double) g[2]) <= TOL_PT) { hit = j; break; }
                    }
                    if (hit < 0) { miss++; if (first == null) first = Py.fmt("「%s」 (%.1f, %.1f)", g[0], g[1], g[2]); }
                    else c.remove(hit);
                }
                if (miss > 0) diff.add(Py.fmt("%d쪽 글자 자리 : %d자가 %.1fpt 안에 없음 — 첫 글자 %s", i + 1, miss, TOL_PT, first));
            }
            return n;
        }
    }

    static void same(List<String> diff, String what, Object want, Object got) {
        if (!Py.eq(want, got)) diff.add(Py.fmt("%s : 정답 %s ≠ 만든 것 %s", what, clip(Py.reprObj(want)), clip(Py.reprObj(got))));
    }
    static String clip(String s) { return s.length() > 160 ? s.substring(0, 160) + "…" : s; }

    static void same_log(List<String> diff, String want, String got) {
        if (want.equals(got)) return;
        String[] a = want.split("\n", -1), b = got.split("\n", -1);
        int k = 0;
        while (k < a.length && k < b.length && a[k].equals(b[k])) k++;
        diff.add(Py.fmt("계산 로그 %d번째 줄 : 정답 「%s」 ≠ 만든 것 「%s」", k + 1, clip(k < a.length ? a[k] : "(없음)"), clip(k < b.length ? b[k] : "(없음)")));
    }

    public static int run(String dir, List<String> only) throws IOException {
        File d = new File(dir);
        String[] fs = d.list((x, nm) -> nm.endsWith(".expected.json"));
        if (fs == null || fs.length == 0) { System.out.println("시험 세트가 없습니다(<이름>.json · <이름>.expected.json · <이름>.expected.pdf) : " + dir); return 1; }
        Arrays.sort(fs);
        File out = new File(d, "out"); out.mkdirs();
        int n = 0, pages = 0, bad = 0;
        long t0 = System.currentTimeMillis();
        for (String f : fs) {
            String nm = f.substring(0, f.length() - ".expected.json".length());
            if (!only.isEmpty() && !only.contains(nm)) continue;
            n++;
            List<String> diff = new ArrayList<>();
            int np = 0; String note = "";
            long t1 = System.currentTimeMillis();
            try {
                Map<String, Object> want = Py.M(Json.parse(Py.read(new File(d, f).getPath())));
                boolean cm = Py.truthy(want.get("code_map"));
                if (!cm) CodeInput._CM = new LinkedHashMap<>();                 // 정답을 담보 식별표 없이 만들었으면 같은 조건으로(이름으로만 찾는다)
                else { CodeInput._CM = null; if (!Py.truthy(CodeInput.code_map())) diff.add("이 정답은 담보 식별표(GA_CODE_MAP)를 준 상태로 만든 것입니다 — 식별표를 주고 다시 돌려 주세요"); }
                if (want.get("version") != null && !Api.ENGINE_VERSION.equals(want.get("version")))
                    note = Py.fmt(" (정답은 %s 로 만든 것 · 이 프로그램은 %s)", want.get("version"), Api.ENGINE_VERSION);
                String pdf = new File(out, nm + ".pdf").getPath();
                Map<String, Object> got;
                try {
                    Map<String, Object> p = CodeInput.parse(Py.read(new File(d, nm + ".json").getPath()));
                    Object[] r = GaV2.build(p, pdf);
                    Map<String, Object> info = Py.M(r[2]);
                    long matched = 0;
                    for (Object x : GaProposal.RID) if (Py.truthy(Py.get(x, "matched"))) matched++;
                    got = Py.dict("ok", true, "pages", info.get("pages"), "care", info.get("care"), "detail_pages", info.get("detail_pages"), "riders", info.get("riders"),
                            "matched", matched, "product", GaProposal.PRODUCT, "premium", GaProposal.PREMIUM, "warn", info.get("warn"),
                            "log", Py.sub(Py.re(SEC_RE, Py.MULTI), "", Py.readText((String) r[1])));
                } catch (CodeInput.InputError ex) { got = Py.dict("ok", false, "error_type", "InputError", "error", ex.getMessage()); }
                catch (Pipeline.DesignUnreadable ex) { got = Py.dict("ok", false, "error_type", "DesignUnreadable", "error", ex.getMessage()); }
                if (!Py.eq(want.get("ok"), got.get("ok"))) {
                    diff.add(Py.truthy(want.get("ok")) ? Py.fmt("정답은 만들었는데 이 프로그램은 멈춤 — %s : %s", got.get("error_type"), got.get("error"))
                            : Py.fmt("정답은 멈춤(%s)인데 이 프로그램은 만듦", want.get("error_type")));
                } else if (!Py.truthy(want.get("ok"))) {
                    same(diff, "멈춘 까닭 갈래", want.get("error_type"), got.get("error_type"));
                    String J = "JSON 으로 읽지 못했습니다";                        // 그 뒤의 까닭은 파이썬 · 자바가 서로 다른 글자를 낸다
                    if (!(Py.gs0(want, "error").startsWith(J) && Py.gs0(got, "error").startsWith(J))) same(diff, "멈춘 까닭 글자", want.get("error"), got.get("error"));
                } else {
                    for (String k : new String[]{"pages", "care", "detail_pages", "riders", "matched", "product", "premium", "warn"}) same(diff, k, want.get(k), got.get(k));
                    same_log(diff, Py.gs0(want, "log"), Py.gs0(got, "log"));
                    String wp = new File(d, nm + ".expected.pdf").getPath();
                    if (!Py.exists(wp)) diff.add("정답 PDF 가 없음 : " + nm + ".expected.pdf");
                    else np = compare_pdf(wp, pdf, diff);
                }
            } catch (RuntimeException | IOException ex) {
                diff.add(Py.fmt("오류 — %s: %s", ex.getClass().getSimpleName(), ex.getMessage()));
            }
            pages += np;
            double sec = (System.currentTimeMillis() - t1) / 1000.0;
            if (diff.isEmpty()) System.out.println(Py.fmt("통과 %-26s %s · %.1f초%s", nm, np > 0 ? Py.fmt("%d쪽", np) : "만들지 않음(정답과 같은 까닭)", sec, note));
            else {
                bad++;
                System.out.println(Py.fmt("실패 %-26s 다른 곳 %d%s", nm, diff.size(), note));
                for (int i = 0; i < Math.min(diff.size(), 12); i++) System.out.println("      " + diff.get(i));
            }
        }
        CodeInput._CM = null;
        if (n == 0) { System.out.println("고른 이름의 시험이 없습니다"); return 1; }
        System.out.println();
        System.out.println(bad == 0 ? Py.fmt("결과 : 전부 통과 — %d건 · %d쪽 · %.0f초 (만든 PDF : %s)", n, pages, (System.currentTimeMillis() - t0) / 1000.0, out.getPath())
                : Py.fmt("결과 : 실패 %d건 / %d건 (만든 PDF : %s)", bad, n, out.getPath()));
        return bad == 0 ? 0 : 1;
    }
}
