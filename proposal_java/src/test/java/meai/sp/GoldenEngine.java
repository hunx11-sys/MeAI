package meai.sp;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.regex.Pattern;

/**
 * 1단계 정답지 대조 — Engine · ScenEngine 이 파이썬 engine.py · scen_engine.py 와 같은 결과를 내는지.
 * 정답은 golden/dump_engine.py 가 만든다(names.json · funcs.json · inputs.json · out_*.json).
 * 사용 : GoldenEngine <정답 폴더> [묶음 이름 …]   (묶음 이름을 주면 그 묶음만 — head 는 이름 · 낱 함수)
 * 견주기는 깊이 · 차례(사전의 열쇠 차례 포함) · 수 꼴(Long/Double)까지 본다. 느슨하게 하지 않는다.
 */
public final class GoldenEngine {
    static long bad = 0, n = 0;
    static final int SHOW = 60;

    static void diff(String where, Object want, Object got) {
        bad++;
        if (bad <= SHOW) System.out.println("다름 [" + where + "]\n    파이썬 = " + cut(Py.reprObj(want)) + "\n    자바   = " + cut(Py.reprObj(got)));
    }
    static String cut(String s) { return s.length() > 600 ? s.substring(0, 600) + " …" : s; }

    /** 깊이 · 차례 · 수 꼴까지 같은가. 다르면 첫 다른 곳을 찍는다 */
    @SuppressWarnings("unchecked")
    static boolean same(String where, Object w, Object g) {
        n++;
        if (g instanceof Object[]) g = java.util.Arrays.asList((Object[]) g);
        if (g instanceof java.util.Set) g = new ArrayList<Object>((java.util.Set<Object>) g);
        if (w == null || g == null) { if (w != g) { diff(where, w, g); return false; } return true; }
        if (w instanceof Map) {
            if (!(g instanceof Map)) { diff(where, w, g); return false; }
            Map<Object, Object> a = (Map<Object, Object>) w, b = (Map<Object, Object>) g;
            if (a.size() != b.size()) { diff(where + " 열쇠 수", new ArrayList<>(a.keySet()), new ArrayList<>(b.keySet())); return false; }
            Iterator<Map.Entry<Object, Object>> ia = a.entrySet().iterator(), ib = b.entrySet().iterator();
            while (ia.hasNext()) {
                Map.Entry<Object, Object> x = ia.next(), y = ib.next();
                if (!x.getKey().equals(y.getKey())) { diff(where + " 열쇠 차례", new ArrayList<>(a.keySet()), new ArrayList<>(b.keySet())); return false; }
                if (!same(where + "." + x.getKey(), x.getValue(), y.getValue())) return false;
            }
            return true;
        }
        if (w instanceof List) {
            if (!(g instanceof List)) { diff(where, w, g); return false; }
            List<Object> a = (List<Object>) w, b = (List<Object>) g;
            if (a.size() != b.size()) { diff(where + " 길이 " + a.size() + "≠" + b.size(), a, b); return false; }
            for (int i = 0; i < a.size(); i++) if (!same(where + "[" + i + "]", a.get(i), b.get(i))) return false;
            return true;
        }
        if (w instanceof Number) {
            if (!(g instanceof Number) || Py.isInt(w) != Py.isInt(g)) { diff(where + " 수 꼴", w, g); return false; }
            boolean ok = Py.isInt(w) ? Py.lng(w) == Py.lng(g) : Py.num(w) == Py.num(g);
            if (!ok) diff(where, w, g);
            return ok;
        }
        if (!w.equals(g)) { diff(where, w, g); return false; }
        return true;
    }

    static Object deepcopy(Object o) {
        if (o instanceof Map) { Map<String, Object> m = new LinkedHashMap<>(); for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) m.put((String) e.getKey(), deepcopy(e.getValue())); return m; }
        if (o instanceof List) { List<Object> l = new ArrayList<>(); for (Object x : (List<?>) o) l.add(deepcopy(x)); return l; }
        return o;
    }

    static Map<String, Object> ruleView(Map<String, Object> r) {
        if (r == null) return null;
        Map<String, Object> v = new LinkedHashMap<>();
        for (Map.Entry<String, Object> e : r.entrySet()) if (!e.getKey().equals("_m") && !e.getKey().equals("_x")) v.put(e.getKey(), e.getValue());
        return v;
    }
    static String bits(List<Boolean> b) { StringBuilder s = new StringBuilder(); for (boolean x : b) s.append(x ? '1' : '0'); return s.toString(); }

    static void names(String dir) {
        Map<String, Object> G = Py.M(Json.parse(Py.read(dir + "/names.json")));
        same("GOJI", G.get("GOJI"), ScenEngine.GOJI);
        same("AMT_RE", G.get("AMT_RE"), ScenEngine.AMT_RE);
        same("ITC_NORM", G.get("ITC_NORM"), ScenEngine._ITC_NORM);
        same("INJ_KNOWN", G.get("INJ_KNOWN"), new ArrayList<Object>(new TreeSet<>(ScenEngine.INJ_KNOWN)));
        same("G131", G.get("G131"), ScenEngine.G131);
        same("G131X", G.get("G131X"), ScenEngine.G131X);
        same("C13N", G.get("C13N"), ScenEngine._C13N);
        same("DB_PRODUCTS", G.get("DB_PRODUCTS"), ScenEngine.DB_PRODUCTS);
        same("nrules", G.get("nrules"), (long) ScenEngine.RULES.size());
        for (Object o : Py.gl(G, "amt")) { List<Object> r = Py.L(o); same("amt_to_man " + r.get(0), r.get(1), ScenEngine.amt_to_man((String) r.get(0))); }
        List<Object> names = Py.gl(G, "names"), res = Py.gl(G, "res");
        Pattern amtRe = Py.re(ScenEngine.AMT_RE);
        for (int i = 0; i < names.size(); i++) {
            String nm0 = (String) names.get(i); Map<String, Object> w = Py.M(res.get(i));
            String nm = ScenEngine.nname(nm0);
            same("classify 「" + nm0 + "」", w.get("classify"), ruleView(ScenEngine.classify(nm0)));
            same("nname 「" + nm0 + "」", w.get("nname"), nm);
            same("noren 「" + nm0 + "」", w.get("noren"), ScenEngine.noren(nm0));
            same("tokens 「" + nm0 + "」", w.get("tokens"), ScenEngine.tokens(nm));
            same("itc_id 「" + nm0 + "」", w.get("itc_id"), ScenEngine.itc_id(nm0));
            same("ls_id 「" + nm0 + "」", w.get("ls_id"), ScenEngine.ls_id(nm0));
            List<Object> am = new ArrayList<>();
            for (Object a : Py.findall(amtRe, nm0)) am.add(Py.list(a, ScenEngine.amt_to_man((String) a)));
            same("이름 속 금액 「" + nm0 + "」", w.get("amt"), am);
        }
        System.out.println("이름 함수 : 이름 " + names.size() + "개 · 지금까지 다른 곳 " + bad);
    }

    static void funcs(String dir) {
        Map<String, Object> F = Py.M(Json.parse(Py.read(dir + "/funcs.json")));
        List<Object> codes = Py.gl(F, "codes");
        List<Object> cc = new ArrayList<>(), ic = new ArrayList<>(), dn = new ArrayList<>(), gf = new ArrayList<>(), si = new ArrayList<>();
        Map<String, Object> combo = Py.gm(F, "combo");
        for (Object c : codes) {
            String k = (String) c;
            cc.add(Engine.cancer_cls(k)); ic.add(ScenEngine.is_cancer(k)); dn.add(Engine.disease_name(k));
            gf.add(new ArrayList<Object>(new TreeSet<>(Engine.groups_for(k)))); si.add(Engine.shown_ids(combo, k));
        }
        cc.add(Engine.cancer_cls(null));
        same("cancer_cls", F.get("cancer_cls"), cc); same("is_cancer", F.get("is_cancer"), ic); same("disease_name", F.get("disease_name"), dn);
        same("groups_for", F.get("groups_for"), gf); same("shown_ids", F.get("shown_ids"), si);
        for (Object ro : Engine.RIDERS) {
            String id = Py.gs(ro, "id");
            List<Object> cv = new ArrayList<>(), il = new ArrayList<>();
            for (Object c : codes) cv.add(Engine.cover(ro, (String) c));
            same("cover " + id, Py.get(F.get("cover"), id), cv);
            for (int i = 0; i < Py.L(Engine.IT.get(Py.gs(ro, "ty"))).size(); i++) il.add(Engine.item_label(id, (long) i));
            same("item_label " + id, Py.get(F.get("item_label"), id), il);
        }
        List<Object> paths = Py.gl(F, "paths");
        int k = 0;
        for (Object o : Py.gl(F, "calc_rider")) {
            List<Object> r = Py.L(o); List<Object> pc = Py.L(paths.get((int) Py.lng(r.get(2))));
            Object got;
            try { got = Engine.calc_rider((String) r.get(0), r.get(1), (String) pc.get(0), Py.M(deepcopy(pc.get(1))), (Boolean) r.get(3), r.get(4) == null ? null : Py.L(r.get(4))); }
            catch (Py.KeyError ex) { got = "KeyError"; }
            if (r.get(5) instanceof String && got instanceof Map) got = "no error";
            same("calc_rider #" + (k++) + " " + r.get(0) + " " + r.get(1) + " 경로" + r.get(2) + " 1년이내=" + r.get(3), r.get(5), got);
        }
        List<Object> cal = Py.gl(F, "calc_all");
        for (int pi = 0; pi < cal.size(); pi++) {
            List<Object> r = Py.L(cal.get(pi));
            same("calc_all " + r.get(0), r.get(1), Engine.calc_all(combo, (String) r.get(0), Py.M(deepcopy(Py.L(paths.get(pi)).get(1)))));
        }
        List<Object> hk = Py.gl(F, "hit_kcds"), lists = Py.gl(F, "hit_lists");
        for (int i = 0; i < lists.size(); i++) {
            List<Boolean> b = new ArrayList<>();
            for (Object kc : hk) b.add(ScenEngine.code_hit(Py.L(lists.get(i)), (String) kc));
            same("code_hit 목록#" + i + " " + cut(Py.reprObj(lists.get(i))), Py.gl(F, "code_hit").get(i), bits(b));
            same("spans_brain_heart 목록#" + i, Py.gl(F, "spans").get(i), ScenEngine.spans_brain_heart(Py.L(lists.get(i))));
        }
        for (Object o : Py.gl(F, "hosp_ok")) { List<Object> r = Py.L(o); same("hosp_ok " + r.get(0) + "/" + r.get(1), r.get(2), ScenEngine.hosp_ok(r.get(0), r.get(1))); }
        for (Object o : Py.gl(F, "surg5")) {
            List<Object> r = Py.L(o);
            same("surg5_grade " + r.get(0) + "/" + r.get(1), r.get(2), ScenEngine.surg5_grade(r.get(0), (String) r.get(1)));
            same("surg5_name " + r.get(0), r.get(3), ScenEngine.surg5_name(r.get(0)));
        }
        for (Object o : Py.gl(F, "surg7")) {
            List<Object> r = Py.L(o);
            same("surg7_grade " + r.get(0), r.get(1), ScenEngine.surg7_grade(r.get(0)));
            same("surg7_name " + r.get(0), r.get(2), ScenEngine.surg7_name(r.get(0)));
            same("surg7_group " + r.get(0), r.get(3), ScenEngine.surg7_group(r.get(0)));
        }
        for (Object o : Py.gl(F, "surg_open")) { List<Object> r = Py.L(o); same("surg_open " + Py.reprObj(r.get(0)), r.get(1), ScenEngine.surg_open(Py.M(r.get(0)))); }
        for (Object o : Py.gl(F, "c13_codes")) { List<Object> r = Py.L(o); same("c13_codes " + r.get(0), r.get(1), ScenEngine.c13_codes((String) r.get(0))); }
        for (Object o : Py.gl(F, "g131_key")) { List<Object> r = Py.L(o); same("g131_key " + r.get(0), r.get(1), ScenEngine.g131_key((String) r.get(0))); }
        List<Object> st = Py.gl(F, "scope_texts"), sk = Py.gl(F, "scope_kcds");
        for (int i = 0; i < st.size(); i++) {
            List<Boolean> b = new ArrayList<>();
            for (Object kc : sk) b.add(ScenEngine.cancer_scope_ok((String) st.get(i), (String) kc));
            same("cancer_scope_ok 「" + st.get(i) + "」", Py.gl(F, "cancer_scope_ok").get(i), bits(b));
        }
        for (Object o : Py.gl(F, "ls_tier")) { List<Object> r = Py.L(o); same("ls_tier " + r.get(0) + "/" + r.get(1), r.get(2), ScenEngine.ls_tier((String) r.get(0), r.get(1))); }
        for (Object o : Py.gl(F, "life_items")) { List<Object> r = Py.L(o); same("life_items", r.get(1), DescEngine.life_items((String) r.get(0))); }
        System.out.println("낱 함수 : 지금까지 다른 곳 " + bad);
    }

    static void bundle(String dir, Map<String, Object> in, String bid) {
        long t0 = System.currentTimeMillis();
        List<Object> riders = Py.L(deepcopy(Py.get(in.get("bundles"), bid)));
        List<Object> scs = Py.gl(in, "scs"), meta = Py.gl(in, "sc_meta");
        Map<String, Object> W = Py.M(Json.parse(Py.read(dir + "/out_" + bid.replaceAll("[^A-Za-z0-9_.-]", "_") + ".json")));
        List<Object> calls = Py.gl(W, "calls");
        ScenEngine.ISSUES.clear();
        long b0 = bad, nl = 0;
        for (Object co : calls) {
            Map<String, Object> c = Py.M(co);
            int i = (int) Py.lng(c.get("sc"));
            String where = bid + " · 사례#" + i + " " + Py.reprObj(meta.get(i));
            int n0 = ScenEngine.ISSUES.size();
            Map<String, Object> s = Py.M(deepcopy(scs.get(i)));
            List<Object> L = ScenEngine.pay_lines(riders, s);
            nl += L.size();
            List<Object> wl = Py.gl(c, "lines");
            if (wl.size() != L.size()) {
                List<Object> wn = new ArrayList<>(), gn = new ArrayList<>();
                for (Object l : wl) wn.add(Py.get(l, "no") + ":" + Py.get(l, "name"));
                for (Object l : L) gn.add(Py.get(l, "no") + ":" + Py.get(l, "name"));
                List<Object> onlyW = new ArrayList<>(wn), onlyG = new ArrayList<>(gn);
                for (Object x : gn) onlyW.remove(x);
                for (Object x : wn) onlyG.remove(x);
                diff(where + " 지급 줄 수 " + wl.size() + "≠" + L.size() + " (파이썬에만 / 자바에만)", onlyW, onlyG); n++;
            } else {
                for (int k = 0; k < wl.size(); k++) same(where + " 줄#" + k + " 「" + Py.get(wl.get(k), "name") + "」", wl.get(k), L.get(k));
            }
            same(where + " total_by first", c.get("first"), ScenEngine.total_by(L, "first"));
            same(where + " total_by year", c.get("year"), ScenEngine.total_by(L, "year"));
            same(where + " total_by each", c.get("each"), ScenEngine.total_by(L, "each"));
            same(where + " total", c.get("total"), ScenEngine.total(L));
            same(where + " 로그", c.get("issues"), new ArrayList<>(ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size())));
            same(where + " 사례(계산 뒤)", c.get("sc_after"), s);
        }
        same(bid + " recog", W.get("recog"), ScenEngine.recog(riders));
        same(bid + " audit", W.get("audit"), ScenEngine.audit(riders));
        same(bid + " issues_grouped", W.get("issues_grouped"), ScenEngine.issues_grouped());
        same(bid + " 로그 수", W.get("n_issues"), (long) ScenEngine.ISSUES.size());
        System.out.println(Py.fmt("%s : 담보 %d · 사례 %d · 지급 줄 %d · 다른 곳 %d · %.0f초", bid, (long) riders.size(), (long) calls.size(), nl, bad - b0, (System.currentTimeMillis() - t0) / 1000.0));
    }

    public static void main(String[] a) throws Exception {
        System.setOut(new java.io.PrintStream(new java.io.FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8"));
        String dir = a[0];
        List<String> only = new ArrayList<>();
        for (int i = 1; i < a.length; i++) only.add(a[i]);
        if (only.isEmpty() || only.contains("head")) { names(dir); funcs(dir); }
        Map<String, Object> in = Py.M(Json.parse(Py.read(dir + "/inputs.json")));
        for (String bid : Py.gm(in, "plan").keySet()) {
            if (!only.isEmpty() && !only.contains(bid)) continue;
            bundle(dir, in, bid);
        }
        System.out.println(bad == 0 ? "결과 : 전부 통과 — 점검 " + n + "개" : "결과 : 다른 곳 " + bad + " / 점검 " + n + "개");
        System.exit(bad == 0 ? 0 : 1);
    }
}
