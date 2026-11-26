package meai.sp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 3단계 정답지 대조 — 칸 정의(GaSpec) · 칸 값 · 세부내역 줄(GaProposal 자료 부분) · 정보계 전 줄 한 담보 설계.
 * 정답은 golden/dump_cells.py 가 만든다. 사용 : GoldenCells <정답 폴더> <2단계 정답 폴더> [spec] [designs] [rows]
 */
public final class GoldenCells {
    static List<Object> pairs(List<Object[]> xs) { List<Object> o = new ArrayList<>(); for (Object[] x : xs) o.add(Arrays.asList(x)); return o; }
    static List<Object> strs(String[][] xs) { List<Object> o = new ArrayList<>(); for (String[] x : xs) o.add(new ArrayList<Object>(Arrays.asList(x))); return o; }
    @SuppressWarnings("unchecked")
    static List<Object> groups(List<Object[]> gs) {
        List<Object> o = new ArrayList<>();
        for (Object[] g : gs) {
            List<Object> items = new ArrayList<>();
            for (Object[] it : (List<Object[]>) g[1]) items.add(Py.list(it[0], it[1], it[3], it[4], it[5]));
            o.add(Py.list(g[0], items));
        }
        return o;
    }
    static Map<String, Object> adhoc(Map<String, Object> sc_, String mode) { return Py.dict("kind", "engine", "sc", sc_, "mode", mode, "need", null, "na_if_empty", false, "key", "adhoc"); }
    static List<Object> issues() { return new ArrayList<>(ScenEngine.ISSUES); }
    static List<Object> issuesFrom(int n0) { return new ArrayList<>(ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size())); }

    static void spec(String dir) {
        Map<String, Object> sp = Py.M(Json.parse(Py.read(dir + "/spec.json")));
        List<Object> wc = Py.gl(sp, "cells");
        G.same("CELLS 길이", (long) wc.size(), (long) GaSpec.CELLS.size());
        for (int i = 0; i < Math.min(wc.size(), GaSpec.CELLS.size()); i++) G.same("CELLS #" + i + " " + Py.M(wc.get(i)).get("key"), wc.get(i), GaSpec.CELLS.get(i));
        G.same("KEY 차례", sp.get("key_order"), new ArrayList<Object>(GaSpec.KEY.keySet()));
        G.same("DZ_ORDER", sp.get("dz_order"), new ArrayList<Object>(GaSpec.DZ_ORDER));
        Map<String, Object> dz = new LinkedHashMap<>();
        for (Map.Entry<String, Object[]> e : GaSpec.GA_DZ.entrySet()) dz.put(e.getKey(), Arrays.asList(e.getValue()));
        G.same("GA_DZ", sp.get("ga_dz"), dz);
        G.same("CS", sp.get("cs"), GaSpec.CS); G.same("DXS", sp.get("dxs"), GaSpec.DXS); G.same("BDX", sp.get("bdx"), GaSpec.BDX); G.same("HDX", sp.get("hdx"), GaSpec.HDX);
        G.same("_b_thrombectomy", sp.get("b_thr"), GaSpec._b_thrombectomy); G.same("_b_stent", sp.get("b_stent"), GaSpec._b_stent); G.same("_h_thrombectomy", sp.get("h_thr"), GaSpec._h_thrombectomy);
        G.same("P1_TX_B", sp.get("p1_tx_b"), pairs(GaSpec.P1_TX_B)); G.same("P1_TX_H", sp.get("p1_tx_h"), pairs(GaSpec.P1_TX_H));
        G.same("brain_steps", sp.get("brain"), pairs(GaSpec.brain_steps("종합"))); G.same("heart_steps", sp.get("heart"), pairs(GaSpec.heart_steps("병원")));
        for (Object o : Py.gl(sp, "sc_dz")) { List<Object> r = Py.L(o); G.same("sc_dz " + r.get(0) + " " + r.get(1), r.get(2), GaSpec.sc_dz((String) r.get(0), (String) r.get(1))); }
        G.same("_ca1", sp.get("ca1"), groups(GaSpec._ca1)); G.same("_bh1", sp.get("bh1"), groups(GaSpec._bh1));
        G.same("SEV", sp.get("sev"), strs(GaSpec.SEV)); G.same("EX_CA", sp.get("ex_ca"), strs(GaSpec.EX_CA)); G.same("EX_BH", sp.get("ex_bh"), strs(GaSpec.EX_BH));
        G.same("SG", sp.get("sg"), strs(GaSpec.SG)); G.same("ROWS3", sp.get("rows3"), strs(GaSpec.ROWS3)); G.same("CM", sp.get("cm"), strs(GaSpec.CM)); G.same("RD", sp.get("rd"), strs(GaSpec.RD));
        G.same("INJ_ACT", sp.get("inj_act"), GaSpec.INJ_ACT); G.same("BASE_T", sp.get("base_t"), GaSpec.BASE_T);
        ScenEngine.ISSUES.clear();
        List<Object> uni = GaSpec.universe(), wu = Py.gl(sp, "universe");
        G.same("universe 길이", (long) wu.size(), (long) uni.size());
        for (int i = 0; i < Math.min(wu.size(), uni.size()); i++) G.same("universe #" + i + " " + Py.M(wu.get(i)).get("name"), wu.get(i), uni.get(i));
        G.same("universe 로그", sp.get("universe_issues"), issues());
        G.same("PARENTS", sp.get("parents"), new ArrayList<Object>(Py.sorted(GaSpec.PARENTS))); G.same("DBID 수", sp.get("dbid_n"), (long) GaSpec.DBID.size());
        for (Object o : Py.gl(sp, "sub_label")) { List<Object> r = Py.L(o); G.same("_sub_label " + r.get(0), r.get(1), GaSpec._sub_label((String) r.get(0))); }
        for (Object o : Py.gl(sp, "sckeys")) { List<Object> r = Py.L(o); G.same("사례 열쇠(sort_keys)", r.get(1), Json.dumps(r.get(0), false, null, ", ", ": ", true)); }
        for (Object o : Py.gl(sp, "ga_product_idx")) { List<Object> r = Py.L(o); G.same("ga_product_idx " + r.get(0), r.get(1), GaProposal.ga_product_idx((String) r.get(0))); }
        for (Object o : Py.gl(sp, "ascii_name")) { List<Object> r = Py.L(o); G.same("ascii_name " + r.get(0), r.get(1), GaProposal.ascii_name((String) r.get(0))); }
        for (Object o : Py.gl(sp, "M")) { List<Object> r = Py.L(o); G.same("M " + r.get(0), r.get(2), GaProposal.M(r.get(0), (Boolean) r.get(1))); }
        for (Object o : Py.gl(sp, "tokens_of")) { List<Object> r = Py.L(o); G.same("tokens_of " + r.get(0), r.get(1), GaSpec.tokens_of(r.get(0))); }
        for (Object o : Py.gl(sp, "disp_name")) { List<Object> r = Py.L(o); G.same("disp_name " + r.get(0), r.get(1), GaProposal.disp_name((String) r.get(0))); }
        System.out.println("칸 사양 · 칸 " + GaSpec.CELLS.size() + " · 우주 " + uni.size() + " · 지금까지 다른 곳 " + G.bad);
    }

    static Map<String, Object> valMap() { Map<String, Object> m = new LinkedHashMap<>(); m.putAll(GaProposal.VAL); return m; }

    @SuppressWarnings("unchecked")
    static void designs(String dir, String mdir) {
        List<Object> cases = Py.L(Json.parse(Py.read(mdir + "/cases.json")));
        Map<String, Object> idx = Py.M(Json.parse(Py.read(dir + "/designs_index.json")));
        int loaded = 0, stopped = 0, total = 0;
        for (int part = 0; part < Py.lng(idx.get("parts")); part++) {
            for (Object w0 : Py.L(Json.parse(Py.read(dir + Py.fmt("/designs_%02d.json", part))))) {
                Map<String, Object> w = Py.M(w0), c = Py.M(cases.get((int) Py.lng(w.get("i"))));
                String id = (String) c.get("id");
                total++;
                System.setProperty("GA_CODE_MAP", Py.truthy(c.get("cm")) ? (String) c.get("cm") : dir + "/_no_such_file.json");
                CodeInput._CM = null; System.clearProperty("GA_MASK");
                Map<String, Object> p;
                try { p = CodeInput.parse(c.get("text")); }
                catch (CodeInput.InputError e) { G.same(id + " 틀린 입력", w.get("skip"), "parse"); continue; }
                if (w.containsKey("skip")) { G.same(id + " 틀린 입력이어야 함", w.get("skip"), null); continue; }
                boolean excl = id.contains("제외 상품 시험용");
                List<Object> ex = null;
                if (excl) {
                    if (!ScenEngine.RULEDOC.containsKey("exclude_products")) ScenEngine.RULEDOC.put("exclude_products", new ArrayList<Object>());
                    ex = Py.gl(ScenEngine.RULEDOC, "exclude_products");
                    ex.add(Py.dict("m", "시험용제외상품", "nm", "시험용 제외 상품", "why", "자체 시험"));
                }
                try {
                    GaProposal.load(p);
                    if (w.containsKey("err")) { G.same(id + " 멈춰야 함", w.get("err"), "계산함"); continue; }
                    loaded++;
                    G.same(id + " VAL", w.get("val"), valMap());
                    G.same(id + " RID", w.get("rid"), GaProposal.RID);
                    G.same(id + " 머리", Py.list(w.get("nrid"), w.get("product"), w.get("premium"), w.get("who"), w.get("shortp"), w.get("head"), w.get("line"), w.get("meta"), w.get("who_line"), w.get("head_bar")),
                            Py.list(GaProposal.NRID, GaProposal.PRODUCT, GaProposal.PREMIUM, GaProposal.WHO, GaProposal.SHORTP, GaProposal.HEAD, GaProposal.LINE, GaProposal.META, GaProposal.who_line(), GaProposal.head_bar()));
                    G.same(id + " 로그", w.get("issues"), issues());
                    G.same(id + " 로그 묶음", w.get("grouped"), ScenEngine.issues_grouped());
                    List<Object> secs = new ArrayList<>();
                    for (Object[] s : GaProposal.calc_sections()) {
                        List<Object> rws = new ArrayList<>();
                        for (Object[] row : (List<Object[]>) s[1]) rws.add(Py.list(row[0], row[1], pairs((List<Object[]>) row[2]), GaProposal.calc_units(row)));
                        secs.add(Py.list(s[0], rws));
                    }
                    G.same(id + " 세부내역", w.get("sections"), secs);
                    Map<String, Object> F = new LinkedHashMap<>(), M = new LinkedHashMap<>(), T = new LinkedHashMap<>();
                    List<Object> notes = new ArrayList<>();
                    for (String k : GaProposal.VAL.keySet()) {
                        if ("engine".equals(Py.M(GaSpec.KEY.get(k)).get("kind"))) F.put(k, GaProposal.F(GaProposal.L(k)));
                        M.put(k, GaProposal.M(GaProposal.V(k))); T.put(k, GaSpec.tokens_of(GaProposal.V(k)));
                    }
                    for (String k : GaProposal.VAL.keySet()) for (Object l : GaProposal.L(k)) { if (notes.size() >= 4000) break; notes.add(Py.list(Py.M(l).get("name"), GaProposal.line_note(Py.M(l)), GaProposal._man_of((String) Py.M(l).get("name")))); }
                    G.same(id + " F", w.get("F"), F); G.same(id + " M", w.get("M"), M); G.same(id + " tokens", w.get("tokens"), T); G.same(id + " 줄 메모 · 가입금액", w.get("notes"), notes);
                    List<Object> dzup = new ArrayList<>(), thx = new ArrayList<>();
                    for (String n : GaSpec.DZ_ORDER) dzup.add(GaSpec.cell_value(adhoc(GaSpec.sc_dz(n, "상급종합"), "first"), GaProposal.RID));
                    G.same(id + " 상급종합 수술", w.get("dzup"), dzup);
                    for (Map<String, Object> sc_ : Arrays.asList(GaSpec._b_thrombectomy, GaSpec._h_thrombectomy))
                        for (String md : new String[]{"first", "year", "each"}) thx.add(GaSpec.cell_value(adhoc(sc_, md), GaProposal.RID));
                    G.same(id + " 혈전제거 단독", w.get("thx"), thx);
                    G.same(id + " 끝 로그", w.get("issues_end"), issues());
                    G.same(id + " 끝 로그 묶음", w.get("grouped_end"), ScenEngine.issues_grouped());
                    G.same(id + " recog", w.get("recog"), ScenEngine.recog(GaProposal.RID));
                    G.same(id + " tag", w.get("tag"), !Py.sub("[^A-Za-z0-9_-]+", "", Py.gs0(p, "design_no")).isEmpty() ? GaProposal.tag_of(p) : null);
                    G.same(id + " label", w.get("label"), GaProposal.label_of(p));
                    if (w.containsKey("mask")) {
                        System.setProperty("GA_MASK", "1");
                        GaProposal.load(CodeInput.parse(c.get("text")), "33세");
                        G.same(id + " 가림", w.get("mask"), Py.dict("head", GaProposal.HEAD, "who", GaProposal.WHO, "who_line", GaProposal.who_line(), "head_bar", GaProposal.head_bar(), "issues", issues()));
                        System.clearProperty("GA_MASK");
                    }
                } catch (Pipeline.DesignUnreadable e) {
                    stopped++;
                    G.same(id + " 멈춤", w.get("err"), Py.list("DesignUnreadable", e.getMessage()));
                    G.same(id + " 멈춤 로그", w.get("issues"), issues());
                } finally {
                    if (excl) ex.remove(ex.size() - 1);
                    System.clearProperty("GA_MASK");
                }
            }
        }
        G.same("계산한 설계 수", idx.get("loaded"), (long) loaded);
        System.out.println("설계 묶음 · 입력 " + total + "건 · 계산 " + loaded + " · 멈춤 " + stopped + " · 지금까지 다른 곳 " + G.bad);
    }

    static Object[] cells_of(List<Object> rid) {
        if (rid == null || rid.isEmpty()) return new Object[]{null, new ArrayList<Object>()};
        GaSpec.clear_cache();
        int n0 = ScenEngine.ISSUES.size();
        List<Object> out = new ArrayList<>();
        for (Object c : GaSpec.CELLS) out.add(GaSpec.cell_value(Py.M(c), rid)[0]);
        for (String n : GaSpec.DZ_ORDER) out.add(GaSpec.cell_value(adhoc(GaSpec.sc_dz(n, "상급종합"), "first"), rid)[0]);
        List<Object> iss = issuesFrom(n0);
        ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size()).clear();
        GaSpec.clear_cache();
        return new Object[]{out, iss};
    }

    static void rows(String dir) {
        Map<String, Object> idx = Py.M(Json.parse(Py.read(dir + "/rows_index.json")));
        CodeInput._CM = new LinkedHashMap<>();                       // 이름 길만(담보 식별표 없이)
        ScenEngine.ISSUES.clear();
        long n = 0, t0 = System.currentTimeMillis();
        for (int part = 0; part < Py.lng(idx.get("parts")); part++) {
            for (Object e0 : Py.L(Json.parse(Py.read(dir + Py.fmt("/rows_%02d.json", part))))) {
                Map<String, Object> e = Py.M(e0);
                String line = (String) e.get("line"), nm = (String) e.get("name"), what = "「" + nm + "」 상품 라인 " + line;
                n++;
                int n0 = ScenEngine.ISSUES.size();
                List<Object> ra;
                try { ra = CodeInput.riders(Py.dict("product", "x", "riders", Py.list(Py.dict("no", 1L, "unit_code", "", "code", "", "name", nm, "amount", 10000000L, "unused_daily", 20000L))), line); }
                catch (Pipeline.DesignUnreadable ex) { ra = new ArrayList<>(); }
                List<Object> i1 = issuesFrom(n0);
                ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size()).clear();
                G.same("담보 줄 " + what, e.get("rows"), ra);
                G.same("담보 줄 로그 " + what, e.get("i1"), i1);
                Object[] a = cells_of(ra);
                G.same("칸 값 " + what, e.get("cells"), a[0]);
                G.same("칸 로그 " + what, e.get("i2"), a[1]);
                for (Object alt0 : Py.gl(e, "alt")) {
                    Map<String, Object> al = Py.M(alt0);
                    List<Object> cid = Py.gl(al, "cid");
                    Map<String, Object> cr = CodeInput.master(cid.get(0), cid.get(1));
                    Map<String, Object> first = !ra.isEmpty() ? new LinkedHashMap<>(Py.M(ra.get(0)))
                            : Py.dict("no", 1L, "name", CodeInput._clean(nm), "man", 1000L, "amount_text", "1천만원", "benefit", null, "sub", null, "itc", ScenEngine.itc_id(nm), "unit_code", "", "code", "", "how", "code");
                    first.put("cat", cr.get("c")); first.put("codes", Py.or(cr.get("k"), new ArrayList<Object>())); first.put("excl", Py.or(cr.get("x"), new ArrayList<Object>())); first.put("hc", Py.or(cr.get("hc"), new ArrayList<Object>()));
                    first.put("mname", cr.get("n")); first.put("sub_rec", Py.gs0(cr, "n").contains("[")); first.put("matched", true);
                    List<Object> rb = new ArrayList<>();
                    rb.add(first);
                    if (!ra.isEmpty()) rb.addAll(ra.subList(1, ra.size()));
                    G.same("식별표 길 담보 줄 " + what + " " + cid, al.get("rows"), rb);
                    Object[] b = cells_of(rb);
                    G.same("식별표 길 칸 값 " + what + " " + cid, al.get("cells"), b[0]);
                    G.same("식별표 길 칸 로그 " + what + " " + cid, al.get("i3"), b[1]);
                }
            }
            System.out.println("정보계 전 줄 · " + n + " / " + idx.get("groups") + " 묶음 · 지금까지 다른 곳 " + G.bad + " · " + (System.currentTimeMillis() - t0) / 1000 + "초");
        }
        G.same("묶음 수", idx.get("groups"), n);
        G.same("남은 로그 수", idx.get("leftover_issues"), (long) ScenEngine.ISSUES.size());
    }

    public static void main(String[] a) {
        G.utf8();
        Set<String> only = new HashSet<>(Arrays.asList(a).subList(2, a.length));
        if (only.isEmpty()) only.addAll(Arrays.asList("spec", "designs", "rows"));
        if (only.contains("spec")) spec(a[0]);
        if (only.contains("designs")) designs(a[0], a[1]);
        if (only.contains("rows")) rows(a[0]);
        G.finish("3단계(칸 사양 · 칸 값 · 세부내역 줄 · 정보계 전 줄)");
    }
}
