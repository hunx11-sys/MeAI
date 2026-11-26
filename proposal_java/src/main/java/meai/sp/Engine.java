package meai.sp;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;

/**
 * 통합치료비 지급금액 계산 엔진 — 파이썬 engine.py(scen_engine 이 `itc` 로 부른다)를 그대로 옮긴 것.
 * 약관 지급금액표(product_data.json)만을 근거로 계산하며, 어떤 금액도 추정하지 않는다.
 */
public final class Engine {
    private Engine() {}

    public static final Map<String, Object> D = Py.M(Py.loadJson("product_data.json"));
    public static final List<Object> RIDERS = Py.gl(D, "RIDERS");
    public static final Map<String, Object> RM = new LinkedHashMap<>();
    public static final Map<String, Object> IT = Py.gm(D, "IT");
    public static final Map<String, Object> AMT = Py.gm(D, "AMT");
    public static final Map<String, Object> KCD = new LinkedHashMap<>();
    public static final List<Object> C32 = Py.gl(Py.gm(D, "EMB"), "c32");
    public static final List<Object> M61 = Py.gl(Py.gm(D, "EMB"), "m61");
    public static final List<Object> P60 = Py.gl(Py.gm(D, "EMB"), "p60");
    public static final Map<String, Object> DZ = new LinkedHashMap<>();

    static {
        for (Object r : RIDERS) RM.put(Py.gs(r, "id"), r);
        for (Object e : Py.gl(Py.gm(D, "EMB"), "kcd")) { List<Object> p = Py.L(e); KCD.put((String) p.get(0), p.get(1)); }
        for (Object d : Py.gl(D, "DZ")) DZ.put(Py.gs(d, "c"), d);
    }

    public static String cancer_cls(String code) {
        Matcher m = Py.match("^([CD])(\\d{2})(?:\\.(\\d+))?", code == null ? "" : code);
        if (m == null) return null;
        long n = Long.parseLong(m.group(2)); String s = m.group(3), t = m.group(1);
        if (t.equals("C")) {
            if (n > 97) return null;
            if (n == 44) return "skin";
            if (n == 73) return "thy";
            return "major";
        }
        if (n <= 9) return "cis";
        if (n == 45 || n == 46) return "major";
        if (n == 47 && s != null && !s.isEmpty() && "1345".indexOf(s.charAt(0)) >= 0) return "major";      // 별표3 : D47.1·3·4·5 = 악성신생물
        if (37 <= n && n <= 48) return "bord";
        return null;
    }

    public static String _in_list(List<Object> lst, String code) {
        boolean part = false;
        for (Object o : lst) {
            String e = (String) o;
            if (code.equals(e) || code.startsWith(e + ".") || (e.length() == 3 && Py.slice(code, null, 3).equals(e))) return "yes";
            if (e.startsWith(code + ".")) part = true;
        }
        return part ? "part" : "no";
    }

    public static String cover(Object rider, String code) {
        String ty = Py.gs(rider, "ty");
        if (ty.equals("CB") || ty.equals("CL") || ty.equals("C2") || ty.equals("CM")) {
            if (code.equals("D47")) return "part";
            return Py.truthy(cancer_cls(code)) ? "yes" : "no";
        }
        // 질병 통합치료비는 대상 질병을 따로 열거하지 않는다(약관 제1조) → 질병이면 지급. 상해 여부는 사례 태그(cause)로 scen_engine 이 거른다.
        switch (ty) {
            case "PR": return _in_list(P60, code);
            case "CV": return _in_list(C32, code);
            case "MS": return _in_list(M61, code);
            case "DZ": return "yes";
            default: return "no";
        }
    }

    /** 비급여 면역항암약물허가치료를 받으면 비급여 표적항암약물허가치료도 함께 인정. */
    public static List<Object> _ev_keys(List<Object> ev) {
        List<Object> k = Py.L(ev.get(3));
        if (k.contains("immune") && !k.contains("target")) {
            int i = k.indexOf("immune");
            List<Object> out = new ArrayList<>(k.subList(0, i));
            out.add("target");
            out.addAll(k.subList(i, k.size()));
            return out;
        }
        return k;
    }

    public static Map<String, Object> calc_rider(String rider_id, Object tier, String code, Map<String, Object> path) { return calc_rider(rider_id, tier, code, path, false, null); }
    public static Map<String, Object> calc_rider(String rider_id, Object tier, String code, Map<String, Object> path, boolean within_1y) { return calc_rider(rider_id, tier, code, path, within_1y, null); }

    /**
     * path = {'e': [ [단계, 치료명, 설명, [치료키], {옵션}], ... ]} — 옵션 nc · j · n · no · nor.
     * skip_keys : 이 사례 질병에 항목 한정 면책이 걸린 치료키(예 anes6) — 그 항목은 0 · why='excl'.
     * 금액표에 없는 특약 · 가입금액이면 파이썬처럼 KeyError(Py.KeyError)를 던진다.
     */
    public static Map<String, Object> calc_rider(String rider_id, Object tier, String code, Map<String, Object> path, boolean within_1y, Collection<?> skip_keys) {
        Map<String, Object> r = Py.M(Py.at(RM, rider_id));
        String ty = Py.gs(r, "ty");
        List<Object> items = Py.L(Py.at(IT, ty));
        List<Object> A = Py.L(Py.at(Py.at(AMT, ty), Py.str(tier)));
        Map<String, Object> res = Py.dict("id", rider_id, "tier", tier, "cov", cover(r, code), "lines", new ArrayList<Object>(),
                "raw", 0L, "total", 0L, "cap", 0L, "capped", Boolean.FALSE);
        if (res.get("cov").equals("no")) return res;
        List<Object> lines = Py.gl(res, "lines");
        String dc = cancer_cls(code);
        boolean sp = Py.match("^C(73|61)", code) != null;                                   // 특정암(로봇수술 금액 구분)
        boolean inj = ty.equals("MS") && Py.match("^S(06|25|26)", code) != null;            // 주요손상
        boolean half = Py.truthy(r.get("half"));
        Object f = (half && within_1y && !inj) ? (Object) Double.valueOf(0.5) : (Object) Long.valueOf(1);   // 1년 이내 감액
        Map<Integer, Boolean> used = new LinkedHashMap<>();
        Object rehab = 0L;
        List<Object> evs = Py.gl(path, "e");
        for (int ei = 0; ei < evs.size(); ei++) {
            List<Object> ev = Py.L(evs.get(ei));
            Map<String, Object> o = Py.M(Py.or(ev.size() > 4 ? ev.get(4) : null, new LinkedHashMap<String, Object>()));
            Map<String, Object> _no = Py.M(Py.or(o.get("no"), new LinkedHashMap<String, Object>()));
            List<Object> off = Py.L(_no.get(ty) != null ? _no.get(ty) : Py.or(_no.get("all"), new ArrayList<Object>()));
            for (Object ko : _ev_keys(ev)) {
                String k = (String) ko;
                if (Py.truthy(skip_keys) && skip_keys.contains(k)) {
                    lines.add(Py.dict("ei", (long) ei, "k", k, "amt", 0L, "why", "excl")); continue;
                }
                List<Integer> cands = new ArrayList<>();
                for (int i = 0; i < items.size(); i++) if (k.equals(Py.get(items.get(i), "k"))) cands.add(i);
                if (cands.isEmpty()) {
                    lines.add(Py.dict("ei", (long) ei, "k", k, "amt", 0L, "why", "none")); continue;
                }
                if (off.contains(k)) {
                    lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) cands.get(0), "amt", 0L, "why", "def",
                            "nor", Py.get(Py.or(o.get("nor"), new LinkedHashMap<String, Object>()), k))); continue;
                }
                List<Integer> el = new ArrayList<>();
                for (int i : cands) {
                    Map<String, Object> it = Py.M(items.get(i));
                    if ((!Py.truthy(it.get("cl")) || Py.in(dc, Py.L(it.get("cl"))))
                            && (!it.containsKey("sp") || Py.truthy(it.get("sp")) == sp)
                            && (!Py.truthy(it.get("j")) || Py.eq(it.get("j"), o.get("j")))) el.add(i);
                }
                if (el.isEmpty()) {
                    lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) cands.get(0), "amt", 0L, "why", "cls")); continue;
                }
                int i = el.get(0); Map<String, Object> it = Py.M(items.get(i));
                if (Py.truthy(it.get("nc")) && !Py.truthy(o.get("nc"))) {
                    lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) i, "amt", 0L, "why", "nc")); continue;
                }
                Object base = Py.mul(A.get(i), f);
                String p = Py.gs(it, "p");
                if (p.equals("y")) {                                     // 연간 1회
                    if (Py.truthy(used.get(i))) lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) i, "amt", 0L, "why", "once"));
                    else { used.put(i, Boolean.TRUE); lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) i, "amt", base)); }
                } else if (p.equals("o")) {                              // 수술 1회당
                    lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) i, "amt", base));
                } else {                                                 // 재활 : 1일 1회 · 연간 한도
                    Object req = Py.get(o, "n", 1L);
                    Object n = Py.max2(0L, Py.min2(req, Py.sub(Py.at(it, "max"), rehab)));
                    rehab = Py.add(rehab, n);
                    lines.add(Py.dict("ei", (long) ei, "k", k, "i", (long) i, "amt", Py.mul(base, n), "n", n,
                            "req", req, "max", it.get("max"), "why", Py.cmp(n, req) < 0 ? "max" : ""));
                }
            }
        }
        List<Object> amts = new ArrayList<>();
        for (Object l : lines) amts.add(Py.get(l, "amt"));
        res.put("raw", Py.sum(amts));
        res.put("cap", Py.mul(tier, (half && within_1y) ? (Object) Double.valueOf(0.5) : (Object) Long.valueOf(1)));   // 연간 총 지급 한도
        res.put("total", Py.min2(res.get("raw"), res.get("cap")));
        res.put("capped", Py.cmp(res.get("raw"), res.get("cap")) > 0);
        return res;
    }

    public static Set<String> groups_for(String code) {
        Set<String> g = new LinkedHashSet<>();
        for (Object r : RIDERS) if (!cover(r, code).equals("no")) g.add(Py.gs(r, "g"));
        return g;
    }

    public static List<Object> shown_ids(Map<String, Object> combo, String code) {
        Set<String> g = groups_for(code);
        List<Object> out = new ArrayList<>();
        for (Object r : RIDERS) {
            String rid = Py.gs(r, "id");
            if (combo.containsKey(rid) && g.contains(Py.gs(RM.get(rid), "g"))) out.add(rid);
        }
        return out;
    }

    public static Map<String, Object> calc_all(Map<String, Object> combo, String code, Map<String, Object> path) { return calc_all(combo, code, path, false); }
    public static Map<String, Object> calc_all(Map<String, Object> combo, String code, Map<String, Object> path, boolean within_1y) {
        Map<String, Object> out = new LinkedHashMap<>();
        for (Object rid : shown_ids(combo, code)) out.put((String) rid, calc_rider((String) rid, combo.get(rid), code, path, within_1y, null));
        return out;
    }

    public static String item_label(String rider_id, Object idx) {
        return Py.gs(Py.L(Py.at(IT, Py.gs(Py.at(RM, rider_id), "ty"))).get((int) Py.lng(idx)), "l");
    }

    public static Map<String, Object> disease(String code) { return Py.M(DZ.get(code)); }

    public static String disease_name(String code) {
        Object d = DZ.get(code);
        if (Py.truthy(d)) return Py.gs(d, "n");
        return (String) Py.or(Py.or(KCD.get(code), KCD.get(Py.slice(code, null, 3))), code);
    }
}
