package meai.sp;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** 파이썬 ga_care.py — 간병인 칸. 튜플 (값, 근거 담보 목록) 은 Object[]{값, List} 로 돌려준다 */
public final class GaCare {
    private GaCare() {}

    public static final String SEND = "간병인 보내줌";

    /** 만원 → '1억 3,640' / '7,000' / '5.5' */
    public static String won(Object v0) {
        if (v0 == null) return "";
        double v = Py.num(v0);
        if (Math.abs(v - Py.round(v)) > 1e-6) return Py.rstrip(Py.rstrip(Py.fmt("%.1f", v), "0"), ".");
        long n = Py.round(v);
        if (n == 0) return "0";
        long eok = Math.floorDiv(n, 10000L), man = Math.floorMod(n, 10000L);
        if (eok != 0 && man != 0) return Py.fmt("%d억 %s", eok, Py.comma(man));
        if (eok != 0) return Py.fmt("%d억", eok);
        return Py.comma(man);
    }

    public static final Pattern _NURSE = Py.re("간호\\s*[·ㆍ․‧∙•・]?\\s*간병\\s*통합\\s*서비스(\\s*사용\\s*추가\\s*보장)?");
    public static String canon(String name) {
        return Py.sub(_NURSE, m -> "간호·간병통합서비스" + (Py.truthy(m.group(1)) ? " 사용추가보장" : ""), name == null ? "" : name);
    }

    public static List<Object> norm(List<Object> riders) {
        List<Object> out = new ArrayList<>();
        for (Object o : riders) {
            Map<String, Object> r = Py.M(o);
            String name = (String) r.get("name");
            String n = name.replace("치매주요질환입원일당", "질병입원일당");
            Map<String, Object> d = new LinkedHashMap<>(r);
            d.put("name", canon(n)); d.put("shown", n); d.put("dementia", name.contains("치매주요질환입원일당"));
            out.add(d);
        }
        return out;
    }

    public static final Pattern _AMT = Py.re("또는\\s*([\\d.,]+)\\s*(천원|만원|원)");
    /** 간병인지원 입원일당 담보의 「간병인 미사용 시 입원일당」(만원) */
    public static double daily(Map<String, Object> r) {
        Object man = r.get("man");
        if (Py.truthy(man) && Py.num(man) > 0) return Py.num(man);
        Object at = r.get("amount_text");
        Matcher m = Py.search(_AMT, Py.sub("\\s+", "", Py.truthy(at) ? (String) at : ""));
        if (m == null) return 0.0;
        double v = Py.toFloat(m.group(1).replace(",", ""));
        return m.group(2).equals("천원") ? v / 10 : (m.group(2).equals("원") ? v / 10000 : v);
    }

    private static String nm(Object r) { return (String) Py.M(r).get("name"); }

    public static List<Object> _dz(List<Object> rs) {
        List<Object> out = new ArrayList<>();
        for (Object r : rs) if (nm(r).contains("질병입원일당") && !nm(r).contains("요양성")) out.add(r);
        return out;
    }
    public static List<Object> _d180(List<Object> rs) {
        List<Object> out = new ArrayList<>();
        for (Object r : rs) if (!nm(r).contains("181일")) out.add(r);
        return out;
    }
    public static List<Object> support(List<Object> rs) {
        List<Object> out = new ArrayList<>();
        for (Object r : _dz(rs)) if (nm(r).contains("간병인지원") && !nm(r).contains("간호·간병")) out.add(r);
        return _d180(out);
    }
    public static List<Object> support_nh(List<Object> rs) {
        List<Object> out = new ArrayList<>();
        for (Object r : rs) if (nm(r).contains("간병인지원") && nm(r).contains("요양성특정질병입원일당") && nm(r).contains("(요양병원)")) out.add(r);
        return out;
    }
    public static List<Object> nurse_add(List<Object> rs) {
        List<Object> out = new ArrayList<>();
        for (Object r : _dz(rs)) if (nm(r).contains("간병인지원") && nm(r).contains("간호·간병통합서비스 사용추가보장")) out.add(r);
        return _d180(out);
    }
    public static List<Object> use(List<Object> rs, String kind) {
        List<Object> dz = _dz(rs), sel = new ArrayList<>();
        for (Object r : dz) {
            String n = nm(r);
            boolean ok;
            if (kind.equals("gen")) ok = n.contains("간병인사용") && !n.contains("(요양병원)") && !n.contains("간호·간병");
            else if (kind.equals("nh")) ok = n.contains("간병인사용") && n.contains("(요양병원)");
            else ok = n.contains("간호·간병통합서비스") && !n.contains("간병인지원");
            if (ok) sel.add(r);
        }
        return _d180(sel);
    }

    /** (미사용 일당 합(Double) 또는 null, 근거 담보) */
    public static Object[] unused(List<Object> rs) {
        List<Object> sp = support(rs);
        if (sp.isEmpty()) return new Object[]{null, new ArrayList<Object>()};
        List<Object> ds = new ArrayList<>();
        for (Object r : sp) ds.add(daily(Py.M(r)));
        return new Object[]{Py.sum(ds), sp};
    }
    public static Object[] nurse_total(List<Object> rs) {
        List<Object> a = nurse_add(rs);
        Object[] us = unused(rs);
        Object u = us[0];
        if (a.isEmpty() && u == null) return new Object[]{null, new ArrayList<Object>()};
        List<Object> mans = new ArrayList<>();
        for (Object r : a) mans.add(Py.M(r).get("man"));
        List<Object> both = new ArrayList<>(a);
        both.addAll(Py.L(us[1]));
        return new Object[]{Py.add(Py.sum(mans), Py.truthy(u) ? u : (Object) 0L), both};
    }

    /** 칸 값(표시용) — 열쇠 hosp · nh · nurse · unused · use_gen · use_nh · use_nurse, 값은 Object[]{값, 근거 담보 List} */
    public static Map<String, Object> cells(List<Object> riders) {
        List<Object> rs = norm(riders);
        Object[] un = unused(rs), nt = nurse_total(rs);
        List<Object> nh = new ArrayList<>(support_nh(rs));
        nh.addAll(support(rs));
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("hosp", new Object[]{!support(rs).isEmpty(), support(rs)});
        out.put("nh", new Object[]{!nh.isEmpty(), nh});
        out.put("nurse", new Object[]{nt[0], nt[1]});
        out.put("unused", new Object[]{un[0], un[1]});
        for (String k : new String[]{"gen", "nh", "nurse"}) {
            List<Object> sel = use(rs, k);
            Object v = null;
            if (!sel.isEmpty()) {
                List<Object> mans = new ArrayList<>();
                for (Object r : sel) mans.add(Py.M(r).get("man"));
                v = Py.sum(mans);
            }
            out.put("use_" + k, new Object[]{v, sel});
        }
        return out;
    }

    public static boolean dementia(List<Object> rs) {
        if (rs == null || rs.isEmpty()) return false;
        for (Object r : rs) if (!Py.truthy(Py.M(r).get("dementia"))) return false;
        return true;
    }
}
