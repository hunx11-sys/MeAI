package meai.sp;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 2단계 정답지 대조 — 담보 알아보기(Matcher_) · 상품 라인(BuildAll) · 담보코드 입력(CodeInput) · 간병인 칸(GaCare).
 * 정답은 golden/dump_match.py 가 만든다. 사용 : GoldenMatch <정답 폴더>
 */
public final class GoldenMatch {
    static List<Object> plainPairs(List<String[]> xs) { List<Object> o = new ArrayList<>(); for (String[] x : xs) o.add(Py.list(x[0], x[1])); return o; }
    static String rid(Object m) { return m == null ? null : Py.M(m).get("p") + "|" + Py.M(m).get("id"); }
    static List<Object> err(RuntimeException e, String type) { return Py.list(type, e.getMessage()); }

    public static void main(String[] a) {
        G.utf8();
        String dir = a[0];
        long t0 = System.currentTimeMillis();
        // ── 이름 × 상품 라인 ──
        Map<String, Object> N = Py.M(Json.parse(Py.read(dir + "/names.json")));
        List<Object> lines = Py.gl(N, "lines"), names = Py.gl(N, "names");
        for (int i = 0; i < names.size(); i++) G.same("base " + names.get(i), Py.gl(N, "base").get(i), Matcher_.base((String) names.get(i)));
        ScenEngine.ISSUES.clear();
        for (int li = 0; li < lines.size(); li++) {
            String ln = (String) lines.get(li);
            int n0 = ScenEngine.ISSUES.size();
            List<Object> col = Py.L(Py.gl(N, "match").get(li));
            for (int i = 0; i < names.size(); i++) {
                Object[] r = Matcher_.match((String) names.get(i), ln);
                G.same("match 「" + names.get(i) + "」 상품 라인 " + ln, col.get(i), Py.list(rid(r[0]), r[1], r[2]));
            }
            G.same("match 로그 · 상품 라인 " + ln, Py.gl(N, "issues").get(li), new ArrayList<>(ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size())));
        }
        List<Object> pmn = Py.gl(N, "pm_names");
        for (int li = 0; li < lines.size(); li++)
            for (int i = 0; i < pmn.size(); i++)
                G.same("parent_master 「" + pmn.get(i) + "」 " + lines.get(li), Py.L(Py.gl(N, "pm").get(li)).get(i), rid(Matcher_.parent_master((String) pmn.get(i), (String) lines.get(li))));
        for (Object o : Py.gl(N, "trail")) {
            List<Object> r = Py.L(o);
            String b = Matcher_.base((String) r.get(0));
            G.same("_trail_groups " + r.get(0), r.get(1), plainPairs(Matcher_._trail_groups(b)));
            G.same("_last_bracket " + r.get(0), r.get(2), Matcher_._last_bracket(b));
            G.same("_labtoks " + r.get(0), r.get(3), new ArrayList<Object>(Py.sorted(Matcher_._labtoks((String) r.get(0)))));
        }
        System.out.println("이름 " + names.size() + "개 × 상품 라인 " + lines.size() + " · 지금까지 다른 곳 " + G.bad + " · " + (System.currentTimeMillis() - t0) / 1000 + "초");

        // ── 낱 함수 ──
        Map<String, Object> F = Py.M(Json.parse(Py.read(dir + "/funcs.json")));
        for (Object o : Py.gl(F, "line_from_head")) { List<Object> r = Py.L(o); G.same("line_from_head " + r.get(0), r.get(1), BuildAll.line_from_head((String) r.get(0))); }
        for (Object o : Py.gl(F, "guess_line")) { List<Object> r = Py.L(o); G.same("guess_line", r.get(1), BuildAll.guess_line(Py.L(r.get(0)))); }
        for (Object o : Py.gl(F, "won")) { List<Object> r = Py.L(o); G.same("won " + r.get(0), r.get(1), GaCare.won(r.get(0))); }
        for (Object o : Py.gl(F, "canon")) { List<Object> r = Py.L(o); G.same("canon " + r.get(0), r.get(1), GaCare.canon((String) r.get(0))); }
        for (Object o : Py.gl(F, "man_of")) { List<Object> r = Py.L(o); G.same("man_of " + r.get(0), r.get(1), CodeInput.man_of(Py.lng(r.get(0)))); }
        for (Object o : Py.gl(F, "won_text")) { List<Object> r = Py.L(o); G.same("won_text " + r.get(0), r.get(1), CodeInput.won_text(Py.lng(r.get(0)))); }
        for (Object o : Py.gl(F, "clean")) { List<Object> r = Py.L(o); G.same("_clean " + r.get(0), r.get(1), CodeInput._clean((String) r.get(0))); }
        for (Object o : Py.gl(F, "g17")) { List<Object> r = Py.L(o); G.same("G17 " + r.get(0), r.get(1), Py.match(CodeInput.G17, CodeInput._clean((String) r.get(0))) != null); }
        for (Object o : Py.gl(F, "txt")) { List<Object> r = Py.L(o); G.same("_txt " + Py.reprObj(r.get(0)), r.get(2), CodeInput._txt(r.get(0), (int) Py.lng(r.get(1)))); }
        System.out.println("낱 함수 · 지금까지 다른 곳 " + G.bad);

        // ── 입력 묶음 ──
        List<Object> cases = Py.L(Json.parse(Py.read(dir + "/cases.json"))), want = Py.L(Json.parse(Py.read(dir + "/inputs.json")));
        int nbad = 0, nstop = 0;
        for (int ci = 0; ci < cases.size(); ci++) {
            Map<String, Object> c = Py.M(cases.get(ci)), w = Py.M(want.get(ci));
            String id = (String) c.get("id");
            System.setProperty("GA_CODE_MAP", Py.truthy(c.get("cm")) ? (String) c.get("cm") : dir + "/_no_such_file.json");
            CodeInput._CM = null; ScenEngine.ISSUES.clear();
            Map<String, Object> r = new LinkedHashMap<>();
            r.put("id", id);
            Map<String, Object> p = null;
            try { p = CodeInput.parse(c.get("text")); }
            catch (CodeInput.InputError e) {
                nbad++;
                List<Object> we = Py.gl(w, "parse_err");
                if (we == null) { G.same(id + " parse", "받아들여야 함", "InputError " + e.getMessage()); continue; }
                String wm = (String) we.get(1), gm = e.getMessage();
                if (wm.startsWith("JSON 으로 읽지 못했습니다 : ")) G.same(id + " parse_err(JSON — 앞 글자만)", true, gm.startsWith("JSON 으로 읽지 못했습니다 : "));   // 파서가 내는 영문 까닭은 파이썬 json 모듈 글자라 같을 수 없다
                else G.same(id + " parse_err", we, Py.list("InputError", gm));
                G.same(id + " 열쇠", new ArrayList<>(w.keySet()), Py.list("id", "parse_err"));
                continue;
            }
            if (w.containsKey("parse_err")) { G.same(id + " parse", w.get("parse_err"), "받아들임"); continue; }
            r.put("parse", Py.deepcopy(p)); r.put("line", CodeInput.line_of(p)); r.put("label", CodeInput.label(p));
            r.put("tag", (Py.truthy(p.get("design_no")) && !Py.sub("[^A-Za-z0-9_-]+", "", (String) p.get("design_no")).isEmpty()) ? CodeInput.tag(p) : null);
            r.put("meta", CodeInput.meta(p));
            List<Object> rid;
            try { rid = CodeInput.riders(p); }
            catch (Pipeline.DesignUnreadable e) {
                nstop++;
                r.put("riders_err", err(e, "DesignUnreadable")); r.put("issues1", new ArrayList<>(ScenEngine.ISSUES));
                G.same(id, w, r); continue;
            }
            r.put("riders", Py.deepcopy(rid)); r.put("p_line", p.get("_line")); r.put("issues1", new ArrayList<>(ScenEngine.ISSUES)); r.put("recog", ScenEngine.recog(rid));
            int n0 = ScenEngine.ISSUES.size();
            r.put("head", CodeInput.head(p)); r.put("head_age", CodeInput.head(p, "33")); r.put("issues2", new ArrayList<>(ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size())));
            List<Object> nr = GaCare.norm(rid);
            r.put("norm", nr);
            List<Object> dl = new ArrayList<>();
            for (Object x : nr) dl.add(GaCare.daily(Py.M(x)));
            r.put("daily", dl);
            r.put("care", GaCare.cells(rid));
            r.put("care_sets", Py.dict("support", GaCare.support(nr), "support_nh", GaCare.support_nh(nr), "nurse_add", GaCare.nurse_add(nr), "use_gen", GaCare.use(nr, "gen"), "dz", GaCare._dz(nr),
                    "unused", GaCare.unused(nr), "nurse_total", GaCare.nurse_total(nr), "dementia", GaCare.dementia(nr)));
            G.same(id, w, r);
        }
        System.out.println("입력 " + cases.size() + "건(틀린 입력 " + nbad + " · 멈춤 " + nstop + ") · " + (System.currentTimeMillis() - t0) / 1000 + "초");
        G.finish("2단계(담보 알아보기 · 담보코드 입력 · 간병인 칸)");
    }
}
