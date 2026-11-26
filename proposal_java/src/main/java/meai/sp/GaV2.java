package meai.sp;

import java.io.File;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 파이썬 ga_v2.py — GA 스마트 제안서 새 양식(v2)의 지면(HTML) 만들기와 한 건 조립.
 * 금액은 전부 GaSpec(= 계산 엔진)의 칸 값 그대로다 — 이 파일은 값을 계산하지 않고 그리기만 한다.
 * 브라우저 · PDF 조립은 Render · PdfKit 이 맡는다. 설계서 PDF 길 · calibrate · shrink_images 는 옮기지 않았다.
 */
public final class GaV2 {
    private GaV2() {}

    public static final String V2 = Py.path("ga_assets", "v2");
    public static final String ICONS = Paths.get(V2, "icons").toString();
    public static String won(Object v) { return GaCare.won(v); }
    public static final String SEND = GaCare.SEND;

    // ═══════════════ 글꼴 · 그리기 ═══════════════
    static String _b64(String p) { return Base64.getEncoder().encodeToString(Py.readBytes(p)); }
    static String _FONTS = null;
    public static String fonts_css() {
        if (_FONTS == null) {
            StringBuilder b = new StringBuilder();
            Object[][] F = {{400L, "Regular"}, {500L, "Medium"}, {600L, "SemiBold"}, {700L, "Bold"}, {800L, "ExtraBold"}};
            for (Object[] f : F) b.append(Py.fmt("@font-face{font-family:P;font-weight:%d;src:url(data:font/woff2;base64,%s)}", f[0], _b64(Py.path("ga_assets", Py.fmt("Pretendard-%s.woff2", f[1])))));
            _FONTS = b.toString();
        }
        return _FONTS;
    }
    static String _NOTO = null;
    /** Noto Sans KR(family N · SIL OFL · ga_assets/noto) — GA 시안 본문 글꼴 */
    public static String noto_css() {
        if (_NOTO == null) {
            String d = Py.path("ga_assets", "noto");
            long[] W = {400, 500, 700, 800};
            StringBuilder b = new StringBuilder();
            for (long w : W) b.append(Py.fmt("@font-face{font-family:N;font-weight:%d;src:url(data:font/woff2;base64,%s)}", w, _b64(Paths.get(d, Py.fmt("noto-sans-kr-%s-normal.woff2", Py.fmt("korean-%d", w))).toString())));
            String[][] NR = {{"109-400", "U+300C-300D"}, {"111-400", "U+203B"}, {"108-700", "U+2460-2473"}};
            for (String[] nr : NR) for (long w : W)
                b.append(Py.fmt("@font-face{font-family:N;font-weight:%d;src:url(data:font/woff2;base64,%s);unicode-range:%s}", w, _b64(Paths.get(d, Py.fmt("noto-sans-kr-%s-normal.woff2", nr[0])).toString()), nr[1]));
            _NOTO = b.toString();
        }
        return _NOTO;
    }
    static final Map<String, String> _ICO = new HashMap<>();
    public static String ico(String key) { return ico(key, 30); }
    public static String ico(String key, long px) {
        if (!_ICO.containsKey(key)) _ICO.put(key, _b64(Paths.get(ICONS, key + ".png").toString()));
        return Py.fmt("<img src=\"data:image/png;base64,%s\" style=\"width:%dpx;height:%dpx\">", _ICO.get(key), px, px);
    }

    // ═══════════════ 한 건 읽기 → 칸 값 ═══════════════
    public static Object V(String key) { return GaProposal.VAL.containsKey(key) ? GaProposal.VAL.get(key)[0] : null; }
    public static List<Object> LN(String key) { return GaProposal.VAL.containsKey(key) ? Py.L(GaProposal.VAL.get(key)[1]) : new ArrayList<>(); }
    public static boolean isnum(Object x) { return x instanceof Number; }
    public static Object[] adhoc(Map<String, Object> sc_, String mode) {
        Map<String, Object> c = Py.dict("kind", "engine", "sc", sc_, "mode", mode, "need", null, "na_if_empty", false, "key", "adhoc");
        return GaSpec.cell_value(c, GaProposal.RID);
    }
    public static final Map<String, Object> EXTRA = new LinkedHashMap<>();
    public static void load(Map<String, Object> design) { load(design, ""); }
    public static void load(Map<String, Object> design, String age) {
        GaProposal.load(design, age);
        EXTRA.clear();
        Object[][] sides = {{"b", GaSpec._b_thrombectomy}, {"h", GaSpec._h_thrombectomy}};
        for (Object[] sd : sides)                                          // 기계적 혈전제거술(카테터) 단독 — 5열 표의 둘째 열
            for (String md : new String[]{"first", "year", "each"}) EXTRA.put(Py.fmt("thx.%s.%s", sd[0], md), adhoc(Py.M(sd[1]), md));
        for (String n : GaSpec.DZ_ORDER) EXTRA.put("dzup." + n, adhoc(GaSpec.sc_dz(n, "상급종합"), "first"));      // 수술 카드 「상급종합」 열 = 같은 사례를 상급종합병원에서
        EXTRA.put("care", care_flags());
        EXTRA.put("unj", unjoined_all(design));                           // 수술 카드의 「미가입」 · 「해당 없음」 을 가르는 바탕
    }
    /** (값, 지급 줄, 집계 방식) */
    public static Object[] _raw(String key) {
        if (EXTRA.containsKey(key)) {
            Object[] e = (Object[]) EXTRA.get(key);
            return new Object[]{e[0], e[1], key.startsWith("thx.") ? key.substring(key.lastIndexOf('.') + 1) : "first"};
        }
        Object c = GaSpec.KEY.get(key);
        return new Object[]{V(key), LN(key), Py.truthy(c) ? Py.M(c).get("mode") : "first"};
    }
    /** 칸 값(표시용). 계산 엔진이 0 을 냈는데 그 칸에 해당하는 가입 특약이 아예 없으면 「미가입」(null) */
    public static Object VX(String key) {
        if (key.equals("ex_ca_total")) return tsum("p2.dx.일반암", "p2.sg.robot.first", "p2.cm.immune1.first");
        if (key.equals("ex_brain_total")) return tsum("p3.dx.뇌졸중", "p3.b1.first", "p3.sev.icu");
        if (key.equals("ex_heart_total")) return tsum("p3.dx.허혈성심장", "p3.h2.first", "p3.h2.year");
        Object[] r = _raw(key);
        Object v = r[0];
        List<Object> L = Py.L(r[1]);
        String mode = (String) r[2];
        String base = ("first".equals(mode) || "year".equals(mode) || "each".equals(mode)) ? "first" : mode;
        if (isnum(v) && Math.abs(Py.num(v)) < 1e-9) {
            boolean any = false;
            for (Object l : L) if (Py.truthy(GaSpec.counts(Py.M(l), base))) { any = true; break; }
            if (!any) return null;
        }
        return v;
    }
    public static final String ESC_NOTE = "※ 체증형 수술비 가입 시, 상기 예시 금액보다 더 큰 금액이 지급될 수 있습니다.";
    public static final Pattern ESC10 = Py.re("\\(\\s*체증형\\s*,\\s*10년후\\s*2배지급\\s*\\)");
    public static final String ESC10_NOTE = "※ 「10년후 2배지급」 체증형 특약은 가입금액 기준 예시(10년 후 2배 지급)";
    public static final Pattern ESCTAG = Py.re("\\s*\\(\\s*(?:25%)?체증형(?:\\s*,\\s*10년후\\s*2배지급)?\\s*\\)");
    public static final double ESC10_X = 262.0;
    public static final List<String> DX10_SUM = java.util.Arrays.asList("p1.ca.dx.일반암", "p1.ca.dx.유사암", "p1.ca.dx.전이암", "p1.bh.dx.뇌졸중", "p1.bh.dx.뇌혈관", "p1.bh.dx.급성심근경색", "p1.bh.dx.허혈성심장");
    /** (칸 금액, [(특약명, 지급액)]) → 계약 10년 후 금액. 체증형 지급액이 없거나 줄 합이 칸 금액과 다르면 null */
    public static Object esc10_after(Object v, List<Object[]> pairs) {
        if (!isnum(v) || Py.num(v) <= 0) return null;
        List<Object> es = new ArrayList<>(), all = new ArrayList<>();
        for (Object[] p : pairs) { if (Py.has(ESC10, p[0] == null ? "" : (String) p[0])) es.add(p[1]); all.add(p[1]); }
        Object esc = Py.sum(es);
        if (!Py.truthy(esc)) return null;
        if (Math.abs(Py.num(Py.sub(Py.sum(all), v))) > 0.01) {
            ScenEngine.log("검토필요", "10년 후 금액", Py.fmt("칸 금액 %s ≠ 지급 줄 합 %s — 10년 후 금액을 적지 않음", v, Py.sum(all)));
            return null;
        }
        return Py.add(v, esc);
    }
    public static Object dx10(String key) {
        Object[] r = _raw(key);
        List<Object[]> pairs = new ArrayList<>();
        for (Object l : Py.L(r[1])) pairs.add(new Object[]{Py.M(l).get("name"), Py.M(l).get("amt")});
        return esc10_after(r[0], pairs);
    }
    public static String dx10_text(Object v10) { return dx10_text(v10, true); }
    public static String dx10_text(Object v10, boolean lng) {
        String[] tu = fmt(v10, !lng ? "만원" : "만");
        return Py.fmt(lng ? "계약 10년 후 진단 시 %s%s" : "10년 후 %s%s", tu[0], Py.orS(tu[1], "원"));
    }
    /** 틀 쪽(암 ① · 뇌혈관 · 심장)의 진단금 자리 아래 둘째 줄 — [dict(key, cx, base, size, n, text)] */
    public static List<Map<String, Object>> dx10_subs(String pk) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Object o : Py.L(Py.get(Py.gm(slots(), "slots"), pk, new ArrayList<Object>()))) {
            Map<String, Object> s_ = Py.M(o);
            String kind = (String) s_.get("kind"), key = (String) s_.get("key");
            boolean main = (pk.equals("ca1") && "amt".equals(kind) && key.startsWith("p2.dx.")) || ((pk.equals("brain") || pk.equals("heart")) && "amt_desc".equals(kind));
            if (!main) continue;
            Object v10 = dx10(key);
            if (v10 == null) continue;
            boolean n = "N".equals(s_.get("ff"));
            out.add(Py.dict("key", key, "cx", s_.get("cx"), "base", Py.num(s_.get("base")) + (n ? 7.7 : 9.6), "size", n ? 6.0 : 6.6, "n", n, "text", dx10_text(v10)));
        }
        return out;
    }
    public static boolean has_esc10() {
        for (Object r : GaProposal.RID) if (Py.has(ESC10, Py.gs0(r, "name")) && Py.num(Py.or(Py.get(r, "man"), 0L)) > 0) return true;
        return false;
    }
    public static Double tsum(String... keys) {
        List<Object> ns = new ArrayList<>();
        for (String k : keys) { Object x = VX(k); if (isnum(x)) ns.add(x); }
        return !ns.isEmpty() ? (Double) Py.num(Py.sum(ns)) : null;
    }

    /** (숫자 글자, 단위) — null 은 미가입. 「1억」 처럼 만 단위가 없으면 단위를 붙이지 않는다 */
    public static String[] fmt(Object v) { return fmt(v, "만"); }
    public static String[] fmt(Object v, String unit) {
        if (v == null) return new String[]{null, ""};
        if (v instanceof String) return new String[]{(String) v, ""};
        String t = won(v);
        return new String[]{t, t.endsWith("억") ? "" : unit};
    }

    // ═══════════════ 간병인 가입 상태(설계서 담보 이름 · 가입금액만 읽는다 — GaCare) ═══════════════
    /** 담보가 맡는 입원 날짜(1회 입원 기준) — 담보 이름의 기간 그대로 */
    public static long[] span(String name) {
        String n = _ns(name);
        if (n.contains("181일")) return new long[]{181, 365};
        Matcher m = Py.search("(\\d+)일한도", n);
        return m != null ? new long[]{1, Long.parseLong(m.group(1))} : new long[]{1, 180};
    }
    private static List<Object> cat(List<?>... ls) { List<Object> o = new ArrayList<>(); for (List<?> l : ls) o.addAll(l); return o; }
    private static String nm(Object r) { return (String) Py.M(r).get("name"); }
    private static Object amt_of(List<Object> L) {
        if (L.isEmpty()) return null;
        List<Object> xs = new ArrayList<>();
        for (Object r : L) xs.add(Py.M(r).get("man"));
        return Py.sum(xs);
    }
    private static Object daily_sum(List<Object> L) {
        List<Object> xs = new ArrayList<>();
        for (Object r : L) xs.add(GaCare.daily(Py.M(r)));
        return Py.sum(xs);
    }
    private static Object nurse_of(List<Object> add, List<Object> sp) {      // 간호 · 간병통합서비스 병동 1일 = 사용추가보장 + (Ⅰ형) 간병인 미사용 입원일당
        if (add.isEmpty() && sp.isEmpty()) return null;
        List<Object> xs = new ArrayList<>();
        for (Object r : add) xs.add(Py.M(r).get("man"));
        return Py.add(Py.sum(xs), daily_sum(sp));
    }
    private static long lim_of(List<Object> L) {
        long mx = 0; boolean any = false;
        for (Object r : L) { long v = span(nm(r))[1]; if (!any || v > mx) mx = v; any = true; }
        return any ? mx : 0;
    }
    private static List<Object> names_of(List<Object> L) {
        List<Object> o = new ArrayList<>();
        for (Object r : L) o.add(Py.truthy(Py.M(r).get("shown")) ? Py.M(r).get("shown") : Py.M(r).get("name"));
        return o;
    }
    private static boolean any_in(List<Object> L, String part) { for (Object r : L) if (nm(r).contains(part)) return true; return false; }
    /** 간병인 지원 · 사용 표(1~180일 / 181일 이상)의 칸 값 — {f, [], []} */
    public static Object[] care_flags() {
        List<Object> rs = GaCare.norm(GaProposal.RID), dz = GaCare._dz(rs);
        List<Object> sup180 = GaCare.support(rs), supnh = GaCare.support_nh(rs), nadd180 = GaCare.nurse_add(rs);
        List<Object> sup181 = new ArrayList<>(), nadd181 = new ArrayList<>(), use181 = new ArrayList<>(), usenh181 = new ArrayList<>(), unurse181 = new ArrayList<>();
        for (Object r : dz) {
            String n = nm(r);
            boolean is181 = n.contains("181일");
            if (n.contains("간병인지원") && is181 && !n.contains("간호·간병")) sup181.add(r);
            if (n.contains("간병인지원") && is181 && n.contains("간호·간병통합서비스 사용추가보장")) nadd181.add(r);
            if (n.contains("간병인사용") && is181 && !n.contains("간호·간병") && !n.contains("(요양병원)")) use181.add(r);
            if (n.contains("간호·간병통합서비스") && !n.contains("간병인지원") && is181) unurse181.add(r);
        }
        for (Object r : rs) { String n = nm(r); if (n.contains("간병인사용") && n.contains("요양성특정질병입원일당") && n.contains("181일")) usenh181.add(r); }
        List<Object> ugen = GaCare.use(rs, "gen"), unh = GaCare.use(rs, "nh"), unurse = GaCare.use(rs, "nurse");
        List<Object> sups = cat(sup180, sup181, supnh);
        Map<String, Object> f = new LinkedHashMap<>();
        f.put("sup180", sup180); f.put("sup181", sup181); f.put("supnh", supnh);
        f.put("unused180", !sup180.isEmpty() ? daily_sum(sup180) : null); f.put("unused181", !sup181.isEmpty() ? daily_sum(sup181) : null);
        f.put("nurse180", nurse_of(nadd180, sup180)); f.put("nurse181", nurse_of(nadd181, sup181));
        f.put("use_gen", amt_of(ugen)); f.put("use_nh", amt_of(unh)); f.put("use_nurse", amt_of(unurse)); f.put("use181", amt_of(use181)); f.put("usenh181", amt_of(usenh181)); f.put("use_nurse181", amt_of(unurse181));
        f.put("lim_sup", lim_of(sup180)); f.put("lim_gen", lim_of(ugen)); f.put("lim_nh", lim_of(unh));
        f.put("type1", any_in(sups, "(Ⅰ)")); f.put("type6", any_in(sups, "(Ⅵ)"));
        f.put("use_esc", any_in(cat(ugen, unh, use181, usenh181), "체증")); f.put("use_plus", any_in(cat(ugen, use181), "(plus)"));
        f.put("sup_names", names_of(cat(sup180, sup181, supnh, nadd180, nadd181))); f.put("use_names", names_of(cat(ugen, unh, unurse, use181, usenh181, unurse181)));
        if (!(Py.eq(f.get("nurse180"), GaCare.nurse_total(rs)[0]) && Py.eq(f.get("unused180"), GaCare.unused(rs)[0]))) throw new AssertionError("간병인 표 1~180일 열 ≠ 보장요약 칸");
        boolean has_sup = !(sup180.isEmpty() && sup181.isEmpty() && supnh.isEmpty() && nadd180.isEmpty() && nadd181.isEmpty());
        f.put("has_sup", has_sup);
        boolean has_use = false;
        for (String k : new String[]{"use_gen", "use_nh", "use181", "usenh181"}) if (Py.truthy(f.get(k))) has_use = true;
        f.put("has_use", has_use);
        boolean inj = false;
        for (Object r : rs) if (Py.has("간병인(지원|사용)", nm(r)) && nm(r).contains("상해입원일당")) { inj = true; break; }
        f.put("inj_only", !has_sup && !has_use && inj);
        List<Object> pages = new ArrayList<>();
        if (has_sup) pages.add("support");
        if (has_use) pages.add("use");
        if (pages.isEmpty()) pages.add("none");
        f.put("pages", pages);
        return new Object[]{f, new ArrayList<Object>(), new ArrayList<Object>()};
    }
    public static Map<String, Object> CF() { return Py.M(((Object[]) EXTRA.get("care"))[0]); }

    // ═══════════════ 틀 위에 값 얹기 ═══════════════
    public static Map<String, Object> slots() { return PdfKit.slots(); }
    public static final double K_BASE = 0.8125;      // Pretendard : 글자 크기 1 에 대한 「상자 위 → 기준선」 거리
    public static final double K_N = 0.8875;         // Noto Sans KR 의 같은 값
    public static String _at(Object cx, Object x0, Object x1, double base, double size, String inner, String align, String extra, double k) {
        double top = base - k * size;
        String pos;
        if (align.equals("center")) pos = Py.fmt("left:%.2fpt;width:300pt;text-align:center", Py.num(cx) - 150);
        else if (align.equals("left")) pos = Py.fmt("left:%.2fpt;text-align:left", x0);
        else pos = Py.fmt("right:%.2fpt;text-align:right", Py.num(Py.gl(slots(), "size").get(0)) - Py.num(x1));
        return Py.fmt("<div class=\"o\" style=\"%s;top:%.2fpt;font-size:%.2fpt;%s\">%s</div>", pos, top, size, extra, inner);
    }
    static String at_c(Object cx, double base, double size, String inner, String extra, double k) { return _at(cx, null, null, base, size, inner, "center", extra, k); }
    static String at_l(Object x0, double base, double size, String inner, String extra, double k) { return _at(null, x0, null, base, size, inner, "left", extra, k); }
    static String at_r(Object x1, double base, double size, String inner, String extra, double k) { return _at(null, null, x1, base, size, inner, "right", extra, k); }
    private static double d(Object m, String k) { return Py.num(Py.M(m).get(k)); }
    public static String amt_html(Map<String, Object> s, Object v) {
        String[] tu = fmt(v);
        boolean N = "N".equals(s.get("ff"));
        if (tu[0] == null) return Py.fmt("<span style=\"font-size:%.2fpt;color:#AAAAAA;font-weight:%d\">미가입</span>", d(s, "size") * 0.755, N ? 500L : 600L);
        if (v instanceof String) return Py.fmt("<span style=\"color:#E5432F;font-weight:800;font-size:%.2fpt\">%s</span>", d(s, "size") * 0.8, tu[0]);
        return Py.fmt("<b style=\"color:%s\">%s</b>%s", s.get("color"), tu[0],
                Py.truthy(tu[1]) ? Py.fmt("<span style=\"font-size:%.2fpt;color:%s;font-weight:%d;margin-left:.4pt\">%s</span>", s.get("usize"), s.get("ucolor"), N ? 700L : 600L, tu[1]) : "");
    }
    /** 값 자리 하나 — 시안 쪽(뇌 · 심)은 Noto(N), 앞 판 쪽(암)은 Pretendard. 「미가입」 은 견본의 미가입 기준선(nbase)에 */
    public static String _slot_at(Map<String, Object> s, Object v, String inner) {
        boolean n = "N".equals(s.get("ff"));
        double base = v == null ? Py.num(Py.get(s, "nbase", s.get("base"))) : d(s, "base");
        return at_c(s.get("cx"), base, d(s, "size"), inner, "font-weight:800" + (n ? ";font-family:N,P;letter-spacing:0" : ""), n ? K_N : K_BASE);
    }
    /** 재활 칸 — 「1일 2만」 + 「(연간 최대 30만)」 */
    public static String rehab_html(Map<String, Object> s, Object v, long times) {
        String f = "font-family:N,P;letter-spacing:0";
        if (!isnum(v))
            return at_c(s.get("cx"), d(s, "base") + 4.0, d(s, "size"), Py.fmt("<span style=\"font-size:10.9pt;color:#AAAAAA;font-weight:500\">%s</span>", v == null ? "미가입" : v), f, K_N);
        String a = Py.fmt("<span style=\"font-size:%.2fpt;font-weight:500;color:%s\">1일 </span><b style=\"font-weight:800;color:%s\">%s</b><span style=\"font-size:%.2fpt;font-weight:500;color:%s\">만</span>",
                s.get("psize"), s.get("color"), s.get("color"), won(v), s.get("psize"), s.get("color"));
        String[] tu = fmt(Py.mul(v, times));
        String b = Py.fmt("<span style=\"color:%s;font-weight:400\">(연간 최대 %s%s)</span>", s.get("color2"), tu[0], tu[1]);
        return at_c(s.get("cx"), d(s, "base"), d(s, "size"), a, f, K_N) + at_c(s.get("cx"), d(s, "base2"), d(s, "size2"), b, f, K_N);
    }
    public static String who_html() { return who_html(6.0, "#666666", "#222222"); }
    public static String who_html(double sz) { return who_html(sz, "#666666", "#222222"); }
    public static String who_html(double sz, String lab, String val) {
        Map<String, Object> h = GaProposal.HEAD;
        String sep = Py.fmt("<i style=\"display:inline-block;width:.6pt;height:%.1fpt;background:#C9C9C9;margin:0 %.1fpt;vertical-align:-.6pt\"></i>", sz, sz * 0.9);
        return Py.fmt("<span style=\"color:%s\">소속 : </span><b style=\"color:%s\">%s</b>%s<span style=\"color:%s\">코드 : </span><b style=\"color:%s\">%s</b>%s<span style=\"color:%s\">컨설턴트 : </span><b style=\"color:%s\">%s</b>",
                lab, val, Py.or(h.get("org"), "-"), sep, lab, val, Py.or(h.get("code"), "-"), sep, lab, val, Py.or(h.get("agent_name"), "-"));
    }
    public static List<Object[]> _paid(String key) { return _paid(key, "first"); }
    public static List<Object[]> _paid(String key, String mode) {
        Object c = GaSpec.KEY.get(key);
        String md = c == null ? mode : (String) Py.M(c).get("mode");
        List<Object[]> out = new ArrayList<>();
        for (Object l : LN(key)) { Object a = GaSpec.counts(Py.M(l), md); if (Py.truthy(a)) out.add(new Object[]{Py.M(l).get("name"), a}); }
        return out;
    }
    public static String _short_rider(String n) {
        Matcher m = Py.search("\\[([^\\[\\]]+)\\]\\s*$", n);
        String n2 = m != null ? m.group(1) : n;
        return Py.strip(Py.sub("^\\(\\d+년갱신\\)갱신형\\s*|\\(건강가입\\)", "", n2));
    }
    private static List<Object> as_lists(List<Object[]> a) { List<Object> o = new ArrayList<>(); for (Object[] x : a) o.add(java.util.Arrays.asList(x)); return o; }
    /** 두 진단 칸이 같은 특약(들)로만 나오면 「중복 지급 안 됨」 안내 */
    public static String dx_note(String k1, String k2) {
        List<Object[]> a = _paid(k1), b = _paid(k2);
        if (a.isEmpty() || b.isEmpty() || !Py.eq(Py.sorted(as_lists(a)), Py.sorted(as_lists(b)))) return "";
        List<Object> ns = new ArrayList<>();
        for (Object[] x : a) ns.add(Py.fmt("%s %s만원", _short_rider((String) x[0]), won(x[1])));
        return Py.fmt("※ 두 진단 항목은 동일 특약(%s)으로 보장되며, 중복하여 지급되지 않습니다.", Py.join(" · ", ns));
    }
    /** 혈전용해 + 혈전제거 칸에 「통합치료 생활비」 가 들어 있으면 그 까닭 */
    public static String life_note(String key) {
        List<Object> xs = new ArrayList<>();
        for (Object[] p : _paid(key)) if (((String) p[0]).contains("생활비")) xs.add(p[1]);
        if (xs.isEmpty()) return "";
        return Py.fmt("※ 혈전용해 + 혈전제거술 : 종류가 다른 치료 2회라 최초 지급시 · 연간 1회 금액에 「특정순환계질환 통합치료 생활비」 %s만원(연 1회)이 더해져 있습니다.", won(Py.sum(xs)));
    }
    public static final long DX_MW = 140;      // 뇌 · 심 진단금 칸(금액 + 설명 글자) 너비(pt) — 억 + 나머지 금액만 이 너비 안으로 줄인다(v9.14)
    public static boolean eok_rest(Object v) { return isnum(v) && won(v).contains("억 "); }
    public static final Map<String, Object> TOTAL_MW = Py.dict("ca2", 117L, "brain", 82L, "heart", 82L);
    public static final String FW_JS = Txt.FW_JS;
    /** 틀 5쪽(암① · 암② · 뇌 · 심 · 안내사항) 위에 얹을 값 글자 — 쪽 크기 그대로, 배경은 투명 */
    public static String overlay_html() {
        Map<String, Object> SL = slots();
        Object W = Py.gl(SL, "size").get(0), H = Py.gl(SL, "size").get(1);
        StringBuilder pages = new StringBuilder();
        for (String pk : new String[]{"ca1", "ca2", "brain", "heart", "notice"}) {
            StringBuilder o = new StringBuilder();
            for (Object s0 : Py.gl(Py.gm(SL, "slots"), pk)) {
                Map<String, Object> s = Py.M(s0);
                String k = (String) s.get("kind"), key = (String) s.get("key");
                boolean nf = pk.equals("brain") || pk.equals("heart");
                if (k.equals("amt") || k.equals("total")) {
                    Object v = VX(key);
                    String inner = amt_html(s, v);
                    if (k.equals("total")) inner = Py.fmt("<span class=\"fw\" data-mw=\"%s\">%s</span>", Py.at(TOTAL_MW, pk), inner);
                    o.append(_slot_at(s, v, inner));
                } else if (k.equals("amt_desc")) {
                    Object v = VX(key);
                    String inner = amt_html(s, v) + ((Py.truthy(s.get("desc")) && v != null)
                            ? Py.fmt("<span style=\"font-size:%.2fpt;color:%s;font-weight:500;margin-left:2.4pt\">%s</span>", Py.get(s, "dsize", 7.7), Py.get(s, "dcolor", "#666666"), s.get("desc")) : "");
                    if (eok_rest(v)) inner = Py.fmt("<span class=\"fw\" data-mw=\"%s\">%s</span>", DX_MW, inner);
                    o.append(_slot_at(s, v, inner));
                } else if (k.equals("rehab")) {
                    String b = key.equals("rh_ca") ? "p2.rh.in" : "p3.rh.in";
                    long times = key.equals("rh_ca") ? 20 : 15;
                    if (!key.equals("rh_ca") && !key.equals("rh_bh")) throw new Py.KeyError(key);
                    o.append(rehab_html(s, VX(b), times));
                } else if (k.equals("note")) {
                    String t = key.equals("dx_note") ? (pk.equals("brain") ? dx_note("p3.dx.뇌혈관", "p3.dx.뇌졸중") : dx_note("p3.dx.허혈성심장", "p1.bh.dx.급성심근경색"))
                            : (Py.or(GaProposal.HEAD.get("no"), "-") + ")");
                    if (Py.truthy(t)) o.append(at_l(s.get("x0"), d(s, "base"), d(s, "size"), Py.fmt("<span style=\"color:%s\">%s</span>", s.get("color"), t),
                            "white-space:nowrap;" + (nf ? "font-family:N,P;font-weight:400;letter-spacing:0" : "font-weight:500"), nf ? K_N : K_BASE));
                } else if (k.equals("life")) {
                    String t = life_note(pk.equals("brain") ? "p3.b1.first" : "p3.h1.first");
                    if (Py.truthy(t)) o.append(at_r(s.get("x1"), d(s, "top") + 6.0, 6.2, Py.fmt("<span style=\"color:#6B6B73\">%s</span>", t), "white-space:nowrap;font-family:N,P;font-weight:400;letter-spacing:0", K_N));
                } else if (k.equals("footer")) {
                    o.append(at_r(s.get("x1"), d(s, "base"), d(s, "size"), who_html(d(s, "size")), "white-space:nowrap;font-weight:500" + (nf ? ";font-family:N,P;letter-spacing:0" : ""), nf ? K_N : K_BASE));
                } else throw new RuntimeException(Py.fmt("모르는 자리 종류 : %s", k));
            }
            for (Map<String, Object> d_ : dx10_subs(pk)) {      // 진단금 둘째 줄(체증형 10년 뒤 2배가 든 칸에만)
                boolean n = (Boolean) d_.get("n");
                o.append(at_c(d_.get("cx"), Py.num(d_.get("base")), Py.num(d_.get("size")), Py.fmt("<span style=\"color:#555555\">%s</span>", d_.get("text")),
                        "font-weight:600" + (n ? ";font-family:N,P;letter-spacing:0;font-weight:500" : ""), n ? K_N : K_BASE));
            }
            pages.append(Py.fmt("<div class=\"pg\">%s</div>", o.toString()));
        }
        String css = Py.fmt("@page{size:%spt %spt;margin:0}html,body{margin:0;background:transparent;font-family:P;-webkit-print-color-adjust:exact;print-color-adjust:exact}"
                + ".pg{position:relative;width:%spt;height:%spt;overflow:hidden;page-break-after:always}.o{position:absolute;line-height:1;white-space:nowrap;font-variant-numeric:tabular-nums;letter-spacing:-.15pt}"
                + ".fw{display:inline-block;transform-origin:50%% 80%%}", W, H, W, H);
        return Py.fmt("<!doctype html><html><head><meta charset=\"utf-8\"><style>%s%s%s</style></head><body>%s%s</body></html>", fonts_css(), noto_css(), css, pages.toString(), FW_JS);
    }

    public static final String[] BRAIN_COLS = {"p3.b0.%s", "thx.b.%s", "p3.b1.%s", "p3.b2.%s", "p3.b3.%s"};
    public static final String[] HEART_COLS = {"p3.h0.%s", "thx.h.%s", "p3.h1.%s", "p3.h2.%s", "p3.h3.%s"};

    // ═══════════════ 새로 그리는 쪽(HTML) ═══════════════
    static String CSS = null;
    public static String css() {
        if (CSS == null) CSS = fonts_css() + noto_css() + Py.readText(Paths.get(V2, "v2.css").toString());
        return CSS;
    }
    public static String head(String title) { return Py.fmt("<div class=\"hd\"><span class=\"ttl\">%s</span></div>", title); }
    public static String foot(String note) { return Py.fmt("<div class=\"ft\"><span>%s</span><span class=\"who\">%s</span></div>", note, who_html()); }
    public static String page(String title, String body, String note, String attrs, String cls) {
        return Py.fmt("<div class=\"page%s\"%s>%s<div class=\"cnt\">%s</div>%s</div>", cls, attrs, head(title), body, foot(note));
    }

    // ── 주요수술 ① ② — 수술 12개 · 6장씩 두 쪽 · 카드마다 고정 다섯 줄 ──
    public static final Map<String, Object> DZ_ICON = Py.dict("백내장", "s_cataract", "디스크", "s_disc", "무릎관절질환", "s_knee", "담석증", "s_gallstone", "맹장염", "s_appendix", "갑상선결절", "s_thyroid",
            "유방양성종양", "s_breast", "자궁근종", "s_uterus", "전립선비대증", "s_prostate", "치질", "s_hemorrhoid", "요로결석", "s_kidneystone", "골절진단", "s_fracture");
    public static final Map<String, Object> DZ_SEX = Py.dict("유방양성종양", "여성", "자궁근종", "여성", "전립선비대증", "남성");
    /** 질병코드 이름 : kcdnames.json 에 없는 두 칸만 약관 별표 글자 그대로(코드를 만들지 않는다) */
    public static final Map<String, Object> KCD_TERMS = Py.dict("M17", new String[]{"M17", "무릎관절증"}, "N40", new String[]{"N40~N45, N47~N51", "남성 생식기관의 질환"});
    static Map<String, Object> _KN = null;
    public static String kcd_chip(String code) {
        if (_KN == null) _KN = Py.M(Py.loadJson("kcdnames.json"));
        String c3 = Py.split(code, ".").get(0), c, n;
        if (KCD_TERMS.containsKey(c3)) { String[] t = (String[]) KCD_TERMS.get(c3); c = t[0]; n = t[1]; }
        else { c = c3; n = (String) Py.or(Py.or(_KN.get(c3), _KN.get(code)), ""); }
        return Py.truthy(n) ? Py.fmt("<i class=\"c\">%s %s</i>", c, n) : Py.fmt("<i class=\"c\">%s</i>", c);
    }
    /** 「┗ 수술비[상해2종]」 처럼 부모 특약 아래 세부 줄로 실린 담보는 부모 이름(via)을 앞에 붙여 읽는다 */
    public static String eff_name(String n, Object no) {
        if (!Py.lstrip(n == null ? "" : n).startsWith("┗")) return n;
        Map<String, Object> r = null;
        if (no != null) for (Object x : GaProposal.RID) if (Py.eq(Py.get(x, "no"), no)) { r = Py.M(x); break; }
        if (!Py.truthy(r)) { r = null; for (Object x : GaProposal.RID) if (n.equals(Py.M(x).get("name"))) { r = Py.M(x); break; } }
        return Py.or(Py.get(r, "via"), "") + " " + Py.strip(n.replace("┗", ""));
    }
    public static List<String> rid_names() {
        List<String> o = new ArrayList<>();
        for (Object r : GaProposal.RID) if (Py.num(Py.or(Py.get(r, "man"), 0L)) > 0) o.add(eff_name((String) Py.M(r).get("name"), Py.get(r, "no")));
        return o;
    }
    public static String _ns(Object x) { return Py.sub("\\s+", "", Py.truthy(x) ? (String) x : ""); }
    public static final Map<String, String[]> ROWS = new LinkedHashMap<>();
    public static final Map<String, String> ROW_NAME = new LinkedHashMap<>();
    static {
        ROWS.put("질병", new String[]{"g1", "s15", "s17", "s131", "etc"}); ROWS.put("상해", new String[]{"g1", "s15", "s17", "fsg", "fdx"});
        ROW_NAME.put("g1", "%s수술비 군"); ROW_NAME.put("s15", "1-5종 수술비[%s]"); ROW_NAME.put("s17", "1-7종 수술비[%s]"); ROW_NAME.put("etc", "그 외 수술비");
        ROW_NAME.put("fsg", "골절수술비 및 그 외 수술비"); ROW_NAME.put("fdx", "골절 진단비");
    }
    public static final Pattern G1_RE = Py.re("^(?:\\(\\d+년갱신\\))?(?:갱신형)?(?:종합병원|상급종합병원)?(?:질병|상해)수술비");
    public static String cause_of(String name) { return name.equals("골절진단") ? "상해" : "질병"; }
    /** 다섯 줄 나누기 — 특약 이름으로만(금액 · 지급 여부는 엔진 값 그대로) */
    public static String grp_of(String n, String cause) {
        String m = ScenEngine.nname(n);
        if (m.contains("1-5종")) return "s15";
        if (m.contains("1-7종")) return "s17";
        if (Py.match(G1_RE, m) != null) return "g1";
        if (cause.equals("질병")) return Py.has("13[01]대질병수술비", m) ? "s131" : "etc";
        return ((m.contains("골절") && m.contains("진단")) || m.contains("상해진단비")) ? "fdx" : "fsg";
    }
    /** 수술 하나에 지급되는 특약 — [{특약 이름(부모 이름 포함), 지급 줄, 모든 병원 금액, 상급종합 금액}] */
    public static List<Object[]> surg_lines(String name) {
        Map<String, Object[]> A = new LinkedHashMap<>();
        Object[][] src = {{2, LN("p1.dz." + name)}, {3, ((Object[]) Py.at(EXTRA, "dzup." + name))[1]}};
        for (Object[] il : src) {
            int i = (Integer) il[0];
            for (Object l0 : Py.L(il[1])) {
                Map<String, Object> l = Py.M(l0);
                Object a = GaSpec.counts(l, "first");
                if (!Py.truthy(a)) continue;
                String ln = (String) l.get("name");
                if (!A.containsKey(ln)) A.put(ln, new Object[]{eff_name(ln, l.get("no")), l, 0.0, 0.0});
                A.get(ln)[i] = (Double) A.get(ln)[i] + Py.num(a);
            }
        }
        return new ArrayList<>(A.values());
    }
    /** 이 설계에 그 줄의 특약이 있는가(상품 마스터로 미가입 줄을 못 만들 때만 쓴다) */
    public static boolean sg_have(String g, String cause) {
        for (String n : rid_names())
            if (Py.has("상해|골절|화상|외상", n) == cause.equals("상해") && Py.has("수술|통합치료비|골절", n) && grp_of(n, cause).equals(g)) return true;
        return false;
    }
    /** 체증형 중 최대 지급률이 2배(200%)로 약관 지급금액표에서 확인된 것만 「최대 2배」 를 붙인다 */
    public static final String[] ESC2 = {"수술비Ⅱ\\(1-5종\\)\\(체증형\\)", "(뇌혈관질환|허혈성심장질환)수술비Ⅱ?\\(25%체증형\\)", "(암수술비\\(유사암제외\\)|유사암수술비)\\(25%체증형\\)"};
    private static String grade_in(String s) { Matcher m = Py.search("\\[(?:질병|상해)(\\d종)\\]", s); return m != null ? m.group(1) : ""; }
    /** 카드 줄 이름 — 갱신 · 가입형 꼬리표를 떼고 1-5종 · 1-7종은 「1-5종 수술비 [질병2종]」 꼴로 */
    public static String rider_label(String full, Map<String, Object> l) {
        String s = Py.strip(Py.sub("\\s+", " ", full));
        s = Py.sub("^\\(\\d+년갱신\\)\\s*", "", s); s = Py.sub("^갱신형\\s*", "", s);
        s = Py.strip(Py.sub("\\s*\\((건강가입|통합간편가입|편한가입|31간편가입|간편가입)\\)", "", s));
        if (s.contains("1-5종") || s.contains("1-7종")) {
            String g = Py.orS(grade_in(s), GaProposal.line_note(l));
            String cause = s.contains("상해") ? "상해" : "질병";
            if (s.contains("태아고급형")) return Py.fmt("태아고급형 수술비(1-7종) [%s%s]", cause, g);
            return Py.fmt("%s 수술비 [%s%s]", s.contains("1-5종") ? "1-5종" : "1-7종", cause, g);
        }
        s = Py.sub(ESCTAG, "", s);
        return s.replace("131대질병수술비", "131대 질병수술비").replace("130대질병수술비", "130대 질병수술비");
    }
    public static String fam_key(String name) { return fam_key(name, null); }
    /** 같은 특약 판정 열쇠 — 갱신형 · 고지 꼬리표 · 띄어쓰기를 떼고, 종별 행은 특약 단위(원인 포함)로 · 체증형은 일반형과 같은 특약 */
    public static String fam_key(String name, Object via) {
        String n = ScenEngine.nname(Py.lstrip(name == null ? "" : name).startsWith("┗") ? (Py.or(via, "") + " " + name) : name);
        n = Py.sub("^(?:\\(\\d+년갱신\\))?(?:갱신형)?", "", n);
        Matcher m = Py.match("^(질병|상해)신수술비\\[(기본|주요수술)\\]", n);
        if (m != null) return Py.fmt("신수술비%s|%s", m.group(2), m.group(1));
        Matcher c1 = Py.search("\\[(질병|상해)\\d?(?:-\\d)?종\\]", n);
        if (c1 == null) c1 = Py.search("^(질병|상해)", n);
        String cz = c1 != null ? c1.group(1) : "";
        if (n.contains("1-7종")) return (n.contains("태아고급형") ? "1-7종태아|" : "1-7종|") + cz;
        if (n.contains("1-5종")) return (n.contains("plus") ? "1-5종plus|" : "1-5종|") + cz;
        return Py.sub(ESCTAG, "", n);
    }
    public static String unj_label(String name) { return unj_label(name, null); }
    /** 미가입 줄 이름 — 종별 행은 특약 단위로, 그 밖은 카드의 특약 이름 규칙 그대로 */
    public static String unj_label(String name, Object via) {
        String k = fam_key(name, via);
        if (k.startsWith("1-7종|")) return Py.fmt("1-7종 수술비 [%s]", Py.split(k, "|").get(1));
        if (k.startsWith("1-7종태아|")) return Py.fmt("태아고급형 수술비(1-7종) [%s]", Py.split(k, "|").get(1));
        if (k.startsWith("신수술비")) return Py.fmt("%s 신수술비[%s]", Py.split(k, "|").get(1), Py.slice(Py.split(k, "|").get(0), 4, null));
        if (k.startsWith("1-5종plus|")) return Py.fmt("1-5종 수술비(plus · 연간2회이상) [%s]", Py.split(k, "|").get(1));
        if (k.startsWith("1-5종|")) return Py.fmt("1-5종 수술비 [%s]", Py.split(k, "|").get(1));
        return rider_label(name, new LinkedHashMap<String, Object>());
    }
    /** 특약 마스터 레코드 한 건을 수술 사례에 태울 꼴로(지급 여부만 본다) */
    public static Map<String, Object> _uni_fix(Map<String, Object> u) {
        Matcher m = Py.match("^[^\\[]*신수술비\\[[^\\]]*\\]\\[(.*)\\]$", (String) u.get("name"));
        if (m != null) { u = new LinkedHashMap<>(u); u.put("name", m.group(1)); }
        String un = (String) u.get("name"), k = null;
        for (String x : GaSpec.INJ_ITC.keySet()) { String xn = ScenEngine.nname(x); if (xn.equals(ScenEngine.nname(un)) || xn.equals(ScenEngine.noren(un))) { k = x; break; } }
        if (Py.truthy(k)) {
            Long mn = null;
            for (String t : Py.gm(GaSpec.INJ_ITC, k).keySet()) { long v = Py.toInt(t); if (mn == null || v < mn) mn = v; }
            if (mn == null) throw new IllegalArgumentException("min() arg is an empty sequence");
            u = new LinkedHashMap<>(u); u.put("man", mn);
        }
        return u;
    }
    private static String full_of(Map<String, Object> u, String lname) { return Py.lstrip(lname).startsWith("┗") ? (Py.or(u.get("via"), "") + " " + lname) : lname; }
    /** 설계도용 — 특약 마스터 전체를 수술 12개 사례(모든 병원 · 상급종합)에 태워, 지급되는 특약이 카드 다섯 줄 중 어느 줄로 가는지 */
    public static List<Object> master_rows() {
        List<Object> uni = new ArrayList<>();
        Map<Object, Map<String, Object>> by = new HashMap<>();
        for (Object u0 : GaSpec.universe()) { Map<String, Object> u = _uni_fix(Py.M(u0)); uni.add(u); by.put(u.get("db_id"), u); }
        int n0 = ScenEngine.ISSUES.size();
        List<Object> out = new ArrayList<>();
        try {
            for (String n : GaSpec.DZ_ORDER) {
                String cause = cause_of(n);
                Map<List<Object>, Map<String, Object>> seen = new LinkedHashMap<>();
                String[][] kh = {{"any", "병원"}, {"top", "상급종합"}};
                for (String[] k : kh) {
                    List<Object> all = cat(Py.L(GaSpec.pay(uni, GaSpec.sc_dz(n, k[1]))[0]), Py.L(GaSpec.inj_lines(uni, GaSpec.sc_dz(n, k[1]))[0]));
                    for (Object l0 : all) {
                        Map<String, Object> l = Py.M(l0);
                        if (Py.num(GaSpec.counts(l, "first")) <= 0) continue;
                        Map<String, Object> u = by.get(l.get("no"));
                        if (u == null) u = new LinkedHashMap<>();
                        String ln = (String) l.get("name"), full = full_of(u, ln);
                        List<Object> sk = Py.list(l.get("no"), ln);
                        Map<String, Object> r = seen.get(sk);
                        if (r == null) {
                            r = Py.dict("surg", n, "cause", cause, "row", grp_of(full, cause), "db_id", l.get("no"), "name", ln, "via", Py.or(u.get("via"), ""), "product", Py.or(u.get("product"), ""), "any", false, "top", false,
                                    "note", ln.contains("성장판") ? "성장판손상 진단이 따로 필요 — 미가입 줄에는 싣지 않음" : (ln.contains("태아") ? "태아 가입 설계에만 — 미가입 줄에는 싣지 않음" : ""));
                            seen.put(sk, r);
                        }
                        r.put(k[0], true);
                    }
                }
                out.addAll(seen.values());
            }
        } finally {
            ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size()).clear(); GaSpec.clear_cache();
        }
        return out;
    }
    private static int row_index(String cause, String g) {
        String[] rw = ROWS.get(cause);
        for (int i = 0; i < rw.length; i++) if (rw[i].equals(g)) return i;
        throw new IllegalArgumentException(Py.fmt("tuple.index(x): x not in tuple — %s", g));
    }
    /** {수술 이름: [{미가입 줄 이름, 묶음}]} — 상품 라인 마스터 전체를 엔진에 돌려 그 수술에 지급되는데 설계에 없는 특약. 상품 라인을 못 믿으면 null */
    public static Map<String, Object> unjoined_all(Object design) {
        String line = GaProposal.LINE;
        Set<String> mine = new LinkedHashSet<>(), mine_base = new LinkedHashSet<>();
        for (Object r : Py.gl(GaSpec.DB, "riders")) if (Py.eq(Py.get(r, "p"), line)) { mine.add(ScenEngine.nname(Py.gs(r, "n"))); mine_base.add(Py.sub(ESCTAG, "", ScenEngine.noren(Py.gs(r, "n")))); }
        List<Object> joined = new ArrayList<>(), known = new ArrayList<>();
        for (Object r : GaProposal.RID) if (Py.num(Py.or(Py.get(r, "man"), 0L)) > 0) joined.add(r);
        for (Object r : joined) {
            String via = Py.sub(Matcher_.GRADE_RANGE, g -> Py.fmt("[%s]", g.group(1)), (String) Py.or(Py.get(r, "via"), ""));
            if (mine.contains(ScenEngine.nname((String) Py.or(Py.get(r, "mname"), ""))) || mine.contains(ScenEngine.nname(via))) known.add(r);
        }
        if (joined.isEmpty() || known.size() < 0.6 * joined.size()) {
            ScenEngine.log("검토필요", "주요수술 미가입 줄", Py.fmt("설계 담보 %d건 중 %d건만 상품 라인 「%s」 마스터에 있음 — 미가입 줄을 싣지 않음", joined.size(), known.size(), line));
            return null;
        }
        boolean has130 = false;
        for (String n : mine) if (n.contains("130대질병수술비")) { has130 = true; break; }
        EXTRA.put("n131", has130 ? "130대 질병수술비" : "131대 질병수술비");      // 이 상품의 질병군 수술비 이름(통합간편 · 간편 = 130대)
        List<Object> uni = new ArrayList<>();
        Map<Object, Map<String, Object>> byid = new HashMap<>();
        for (Object u0 : GaSpec.universe()) {
            Map<String, Object> u = Py.M(u0);
            if (Py.eq(u.get("product"), line)) { }
            else if ("설계서 종별 행".equals(u.get("product")) && mine_base.contains(Py.sub(ESCTAG, "", ScenEngine.noren((String) Py.or(u.get("via"), ""))))) { }
            else continue;
            String un = (String) u.get("name");
            if (un.contains("성장판")) continue;                                 // 성장판손상골절진단비 — 의사의 「성장판손상」 진단이 따로 있어야 한다
            if (un.contains("태아")) continue;                                   // 태아 특약은 태아 가입 설계에만
            Map<String, Object> x = _uni_fix(u);
            uni.add(x);
            byid.putIfAbsent(x.get("db_id"), x);
        }
        Set<String> have = new LinkedHashSet<>();
        for (Object r : joined) have.add(fam_key((String) Py.M(r).get("name"), Py.get(r, "via")));
        for (Object r : joined) if (Py.truthy(Py.get(r, "mname"))) have.add(fam_key((String) Py.M(r).get("mname")));
        int n0 = ScenEngine.ISSUES.size();
        Map<String, Object> out = new LinkedHashMap<>();
        try {
            for (String n : GaSpec.DZ_ORDER) {
                final String cause = cause_of(n);
                Map<String, Object[]> seen = new LinkedHashMap<>();
                for (String hosp : new String[]{"병원", "상급종합"}) {
                    List<Object> all = cat(Py.L(GaSpec.pay(uni, GaSpec.sc_dz(n, hosp))[0]), Py.L(GaSpec.inj_lines(uni, GaSpec.sc_dz(n, hosp))[0]));
                    for (Object l0 : all) {
                        Map<String, Object> l = Py.M(l0);
                        if (Py.num(GaSpec.counts(l, "first")) <= 0) continue;
                        Map<String, Object> u = byid.get(l.get("no"));
                        if (!Py.truthy(u)) u = new LinkedHashMap<>();
                        String ln = (String) l.get("name");
                        String k = fam_key(ln, u.get("via"));
                        if (have.contains(k) || seen.containsKey(k)) continue;
                        seen.put(k, new Object[]{unj_label(ln, u.get("via")), grp_of(full_of(u, ln), cause)});
                    }
                }
                List<Object[]> vals = Py.sorted(new ArrayList<>(seen.values()),      // 줄 순서 → 줄 안은 기본(질병수술비) · 종합병원 · 상급종합 순
                        x -> Py.list((long) row_index(cause, (String) x[1]), ((String) x[0]).contains("상급종합"), ((String) x[0]).contains("종합병원"), x[0]));
                out.put(n, vals);
            }
        } finally {
            ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size()).clear(); GaSpec.clear_cache();      // 가상의 마스터 계산은 이 설계의 감사 로그 · 계산 캐시에 남기지 않는다
        }
        return out;
    }
    /** 1-5종 · 1-7종 줄의 종 — 특약 이름의 [질병2종] 또는 지급 줄의 종 메모 */
    public static String _grade(String full, Map<String, Object> l, String cause) { return Py.orS(grade_in(full), GaProposal.line_note(l)); }
    /** {[{줄 이름, 상태, 모든 병원, 상급종합, 꼬리표들}] 다섯 줄, 합계, 합계}. 상태 : on 금액 · no 미가입 · na 해당 없음 */
    @SuppressWarnings("unchecked")
    public static Object[] card_rows(String name) {
        String cause = cause_of(name);
        Map<String, List<Object[]>> by = new LinkedHashMap<>();
        for (String g : ROWS.get(cause)) by.put(g, new ArrayList<>());
        for (Object[] r : surg_lines(name)) {
            String g = grp_of((String) r[0], cause);
            if (!by.containsKey(g)) throw new Py.KeyError(g);
            by.get(g).add(r);
        }
        Object unjAll = EXTRA.get("unj");
        List<Object[]> unj = unjAll != null ? (List<Object[]>) Py.M(unjAll).get(name) : null;
        String u131 = (String) Py.or(EXTRA.get("n131"), "131대 질병수술비");
        List<Object[]> rows = new ArrayList<>();
        for (String g : ROWS.get(cause)) {
            List<Object[]> L = by.get(g);
            List<Object> as = new ArrayList<>(), us = new ArrayList<>();
            for (Object[] r : L) { as.add(r[2]); us.add(r[3]); }
            Object a = Py.sum(as), u = Py.sum(us);
            List<String[]> tags = new ArrayList<>();
            List<String> names = new ArrayList<>();
            if (unj != null) for (Object[] x : unj) if (g.equals(x[1])) names.add((String) x[0]);
            String lab;
            if (g.equals("s15") || g.equals("s17")) {
                Set<String> grs = new LinkedHashSet<>();
                for (Object[] r : L) grs.add(_grade((String) r[0], Py.M(r[1]), cause));
                grs.remove("");
                List<String> gr = Py.sorted(grs);
                lab = Py.fmt(ROW_NAME.get(g), cause + (gr.size() == 1 ? gr.get(0) : ""));
                boolean fetus = false, esc = false, esc2 = false;
                for (Object[] r : L) {
                    String f = (String) r[0];
                    if (f.contains("태아고급형")) fetus = true;
                    if (f.contains("체증")) esc = true;
                    for (String p_ : ESC2) if (Py.has(p_, _ns(f))) esc2 = true;
                }
                if (fetus) tags.add(new String[]{"b", "태아고급형"});      // 분류표 · 제외 질병이 다른 특약이라 이름을 밝힌다
                if (esc) tags.add(new String[]{"e", esc2 ? "체증형 · 최대 2배 체증" : "체증형"});
            } else if (g.equals("s131")) {
                if (!L.isEmpty()) {
                    lab = Py.sub("^(13[01]대 질병수술비)\\s*\\(([^()]+)\\)$", "\\1[\\2]", rider_label((String) L.get(0)[0], Py.M(L.get(0)[1])));
                    lab = Py.sub("질병수술비\\s+\\[", "질병수술비[", lab);
                } else lab = !names.isEmpty() ? names.get(0) : u131;
            } else lab = ROW_NAME.get(g).contains("%s") ? Py.fmt(ROW_NAME.get(g), cause) : ROW_NAME.get(g);
            if (L.size() > 1) tags.add(new String[]{"s", "합산"});
            String st;
            if (Py.num(a) > 0 || Py.num(u) > 0) st = "on";
            else if (unj != null) st = !names.isEmpty() ? "no" : "na";
            else st = sg_have(g, cause) ? "na" : "no";
            rows.add(new Object[]{lab, st, a, u, tags});
        }
        List<Object> ta = new ArrayList<>(), tu = new ArrayList<>();
        for (Object[] r : rows) { ta.add(r[2]); tu.add(r[3]); }
        return new Object[]{rows, Py.sum(ta), Py.sum(tu)};
    }
    public static final Map<String, Object> DZ_RANK = Py.dict("백내장", "50대 이후 다빈도 수술 1위", "디스크", "전체 다빈도 수술 2위", "무릎관절질환", "60-70대 다빈도 수술 3위", "치질", "20-40대 다빈도 수술 1위(제왕절개 제외)");
    public static final String RANK_SRC = "[출처 : 국민건강보험공단 2025년 주요수술 통계연보 – 전체·연령대별 다빈도 수술 순위]";
    public static final String SURG_FOOT = "상기 예시 금액은 이 설계의 특약별 가입금액 기준으로, 수술명, 수술코드에 따라 보험금은 달라질 수 있습니다.<br>세부 내용은 약관을 참고해 주시기 바랍니다.";
    private static String m_(Object v) { return Py.num(v) > 0 ? Py.fmt("<b>%s만</b>", won(v)) : "<span class=\"dash\">–</span>"; }
    @SuppressWarnings("unchecked")
    public static String card(String name) {
        Object[] dz = GaSpec.GA_DZ.get(name);
        Object proc = dz[0];
        String kcd = (String) dz[1];
        Object[] cr = card_rows(name);
        List<Object[]> rows = (List<Object[]>) cr[0];
        Object ta = cr[1], tu = cr[2];
        Object want = V("p1.dz." + name);
        if (isnum(want) && Math.abs(Py.num(Py.sub(ta, want))) > 0.01) throw new RuntimeException(Py.fmt("수술 카드 합계(%s)가 보장요약 칸(%s)과 다름 : %s", ta, want, name));
        boolean none = Py.num(ta) <= 0 && Py.num(tu) <= 0;
        StringBuilder rs = new StringBuilder();
        for (Object[] r : rows) {
            String lab = (String) r[0], st = (String) r[1];
            StringBuilder tg = new StringBuilder();
            for (String[] t : (List<String[]>) r[4]) tg.append(Py.fmt("<i class=\"tg %s\">%s</i>", t[0], t[1]));
            if (st.equals("on")) rs.append(Py.fmt("<div class=\"sc-r\"><span>%s%s</span>%s%s</div>", _esc(lab), tg.toString(), m_(r[2]), m_(r[3])));
            else rs.append(Py.fmt("<div class=\"sc-r off\"><span>%s</span><span></span><span class=\"%s\">%s</span></div>", _esc(lab), st.equals("no") ? "pill" : "nx", st.equals("no") ? "미가입" : "해당 없음"));
        }
        Object sex = DZ_SEX.get(name);
        String chips = kcd_chip(kcd) + (Py.truthy(sex) ? Py.fmt("<i class=\"%s\">%s</i>", "남성".equals(sex) ? "m" : "f", sex) : "") + (DZ_RANK.containsKey(name) ? Py.fmt("<i>%s</i>", DZ_RANK.get(name)) : "");
        String a1 = none ? "<span class=\"na\">미가입</span>" : Py.fmt("<b>%s<small>만</small></b>", won(ta));
        String a2 = none ? "<span class=\"na\">미가입</span>" : Py.fmt("<b>%s<small>만</small></b>", won(tu));
        return Py.fmt("<div class=\"sc\"><div class=\"sc-h\"><span class=\"sc-ic\">%s</span><div class=\"sc-n\"><b>%s</b><span>%s</span></div>"
                + "<div class=\"sc-a\"><span>모든 병원</span>%s</div><div class=\"sc-a u\"><span>상급종합</span>%s</div></div>"
                + "<div class=\"sc-k\">%s</div><div class=\"sc-t\"><div class=\"sc-r hd\"><span>보장(특약)</span><span>모든 병원</span><span>상급종합</span></div>%s</div></div>",
                ico((String) Py.at(DZ_ICON, name), 39), name.replace("골절진단", "골절"), proc, a1, a2, chips, rs.toString());
    }
    public static String need_surg() {
        return Py.fmt("<div class=\"cv-h\"><b>늘어나는 수술 부담</b><span>수술 건수도, 1건당 진료비도 매년 증가</span></div>"
                + "<div class=\"cv-need\"><div>%s<div class=\"k\">연간 주요수술 건수</div><div class=\"v\">215<small>만건</small></div></div>"
                + "<div>%s<div class=\"k\">수술 1건당 평균 진료비</div><div class=\"v\">496<small>만</small></div></div></div>"
                + "<div class=\"cv-src\">[출처 : 국민건강보험공단 2025년 주요수술 통계연보]</div>", _ic("need_surgery"), _ic("care_cost"));
    }
    public static String page_surg(int i) {
        List<String> names = Py.slice(GaSpec.DZ_ORDER, i * 6, (i + 1) * 6);
        String no = "①②".substring(i, i + 1);
        StringBuilder cards = new StringBuilder();
        for (String n : names) cards.append(card(n));
        String body = (i == 0 ? need_surg() : "") + Py.fmt("<div class=\"cv-tab sg%d\"><b>다빈도 수술별 보장금액 %s</b></div>", (long) i, no)
                + Py.fmt("<div class=\"cards2\">%s</div>", cards.toString())
                + Py.fmt("<div class=\"sc-note\">%s</div>", ESC_NOTE + (has_esc10() ? "<span style=\"white-space:nowrap\">&ensp;" + ESC10_NOTE + "</span>" : ""))
                + (i == 1 ? Py.fmt("<div class=\"sc-src\">%s</div>", RANK_SRC) : "");
        return page(Py.fmt("주요수술 보장 %s", no), body, SURG_FOOT, Py.fmt(" data-zmax=\"1\" data-gap=\"%s\"", i == 0 ? 14L : 12L), " nt sgp two" + (i != 0 ? " sfill" : ""));
    }

    // ── 간병인 — 표(1~180일 / 181일 이상) + 지원 장점 / 청구 방법 + 「니즈에 맞게 선택하세요」 ──
    public static String _ic(String key) { return Py.fmt("<span class=\"cv-ic\">%s</span>", ico(key, 53)); }
    public static String need_care() {
        return Py.fmt("<div class=\"cv-h\"><b>돈 많이 드는 간병비</b><span>간병비는 건강보험이 적용되지 않는 전액 본인부담</span></div>"
                + "<div class=\"cv-need\"><div>%s<div class=\"k\">한 달 평균 간병비</div><div class=\"v\">370<small>만</small></div></div>"
                + "<div>%s<div class=\"k\">국민 사적 간병비<small>(연간 추정)</small></div><div class=\"v\">10<small>조원</small></div></div></div>"
                + "<div class=\"cv-src\">[출처 : 보건복지부 2023년 발표 자료 · 보건복지부 소개 서울대 사적 간병비 추정(2022년) / 지역 · 환자 상태에 따라 편차가 큼]</div>", _ic("care_cost"), _ic("private_care"));
    }
    public static final String C_NA = "<span class=\"na\">미가입</span>";
    public static final String C_EXC = "<span class=\"na\">보장 제외</span>";      // 간병인사용 181일 이상 특약은 요양병원을 보장하지 않는다 — 「미가입」 이 아니라 「보장 제외」
    public static final String C_DASH = "<span class=\"na\">-</span>";             // 간병인 미사용 일당이 없음(시안 표기)
    public static String _sub(String t) { return Py.fmt("<span class=\"sub\">(%s)</span>", t); }
    public static String c_send(Object on) { return c_send(on, ""); }
    public static String c_send(Object on, String sub) { return Py.truthy(on) ? Py.fmt("<span class=\"snd\">%s</span>%s", SEND, sub) : C_NA; }
    public static String c_day(Object v) { return c_day(v, "", C_NA); }
    public static String c_day(Object v, String sub) { return c_day(v, sub, C_NA); }
    /** 1일 ○만 — null 은 미가입 */
    public static String c_day(Object v, String sub, String none) {
        if (v == null) return none;
        return Py.fmt("<span class=\"d\">1일<b>%s</b><i>만</i></span>%s", won(v), sub);
    }
    /** 간병인 미사용 시 — 일당이 있으면 「1일 ○만」, 없으면 「-」 */
    public static String c_unused(Object v, String sub) { return (isnum(v) && Py.num(v) > 0) ? c_day(v, sub) : C_DASH; }
    public static String _tbl(String[][] rows, String cls) {
        StringBuilder b = new StringBuilder();
        for (String[] r : rows) b.append(Py.fmt("<tr>%s<td>%s</td><td>%s</td></tr>", r[0], r[1], r[2]));
        return Py.fmt("<table class=\"cv-t %s\"><colgroup><col style=\"width:20%%\"><col style=\"width:13.93%%\"><col style=\"width:32.98%%\"><col></colgroup>"
                + "<tr><th colspan=\"2\">구분</th><th>1~180일</th><th>181일 이상</th></tr>%s</table>", cls, b.toString());
    }
    public static String _lim(Object n) { return (Py.truthy(n) && Py.num(n) < 180) ? _sub(Py.fmt("1회 입원 %d일 한도", n)) : ""; }
    /** 간병인 지원일당 표 */
    public static String tbl_support(Map<String, Object> cf, String cls, boolean notes) {
        String co = "<span class=\"snd\">실손보장</span>" + _sub("*한도 내 실손 보장"), lim = _lim(cf.get("lim_sup"));
        Object nurse = cf.get("nurse180");
        String nsub = lim;
        if (Py.truthy(cf.get("use_nurse")) && !Py.truthy(cf.get("has_use"))) {      // 간병인사용 담보 없이 「간호 · 간병통합서비스 사용 질병입원일당」 만 있으면 이 표에 더해 보인다
            nurse = Py.add(Py.or(nurse, 0L), cf.get("use_nurse")); nsub = _sub(Py.fmt("통합서비스 사용일당 %s만 포함", won(cf.get("use_nurse"))));
        }
        Object u181 = cf.get("unused181");
        String usub = "";
        if (u181 == null && Py.truthy(cf.get("supnh"))) { u181 = daily_sum(Py.L(cf.get("supnh"))); usub = _sub("요양병원 · 요양성 특정질병"); }
        boolean s180 = Py.truthy(cf.get("sup180"));
        return "<div class=\"cv-tab\"><b>간병인 지원일당</b><span>현물지원 · 메리츠가 간병인을 보내드려요</span></div>" + _tbl(new String[][]{
                {"<td class=\"l\" rowspan=\"2\">간병인 사용 시</td><td class=\"l\">병·의원</td>", c_send(cf.get("sup180"), lim), c_send(cf.get("sup181"))},
                {"<td class=\"l\">요양병원</td>", c_send(cf.get("sup180"), lim), c_send(cf.get("supnh"), _sub("*요양성특정질병 보장"))},
                {"<td class=\"l\" colspan=\"2\">공동간병인 사용 시</td>", s180 ? (co + lim) : C_NA, (Py.truthy(cf.get("sup181")) || Py.truthy(cf.get("supnh"))) ? co : C_NA},
                {"<td class=\"l\" colspan=\"2\">간호·간병통합서비스 사용 시</td>", c_day(nurse, nsub), c_day(cf.get("nurse181"))},
                {"<td class=\"l\" colspan=\"2\">간병인 미사용 시</td>", c_unused(cf.get("unused180"), lim), c_unused(u181, usub)}}, cls)
                + (notes ? "<div class=\"cv-note\">※ 한도 내 실손보장: 간병인 이용한 실제 비용을 간병인 지원 공시금액 한도 내 실손 보장(2026년 기준 간병인 지원 공시금액: 1일 140,400원)<br>"
                + "※ 181일 이상 보장은 1회 입원당 최대 185일까지입니다.<br>※ 요양병원 181일 이상은 요양성 특정질병으로 입원한 경우만 해당합니다.<br>"
                + "&nbsp;&nbsp;*요양성 특정질병: 약관 분류표가 정한 치매질환 · 뇌혈관질환(뇌내출혈, 뇌경색증 등) · 신경계질환(파킨슨병 등)</div>" : "");
    }
    /** 간병인 사용일당 표 */
    public static String tbl_use(Map<String, Object> cf, String cls, boolean notes) {
        Object lg = cf.get("lim_gen");
        String g = _sub("요양병원 제외" + ((Py.truthy(lg) && Py.num(lg) < 180) ? Py.fmt(" · 1회 입원 %d일 한도", lg) : ""));
        List<Object> nt = Py.list("※ 181일 이상 보장은 1회 입원당 최대 185일까지입니다.", "※ 간병인 사용일당 체증형 가입 시 최대 200%까지 체증됩니다. (보장 예시는 가입금액 기준)");
        if (Py.truthy(cf.get("use_plus"))) nt.add("※ 병·의원 금액은 간병인 사용금액이 1일당 7만원 이상(또는 1일 8시간 이상)인 경우 기준이며, 그 미만이면 50%를 지급합니다.");
        return "<div class=\"cv-tab\"><b>간병인 사용일당</b><span>금액지원 · 간병인 사용일수를 계산하여 일당으로 드려요</span></div>" + _tbl(new String[][]{
                {"<td class=\"l\" rowspan=\"2\">간병인 사용 시</td><td class=\"l\">병·의원</td>", c_day(cf.get("use_gen"), g), c_day(cf.get("use181"), _sub("요양·정신·한방병원 제외"))},
                {"<td class=\"l\">요양병원</td>", c_day(cf.get("use_nh"), _lim(cf.get("lim_nh"))), Py.truthy(cf.get("usenh181")) ? c_day(cf.get("usenh181"), _sub("요양성 특정질병 보장")) : C_EXC},
                {"<td class=\"l\" colspan=\"2\">간호·간병통합서비스 사용 시</td>", c_day(cf.get("use_nurse")), c_day(cf.get("use_nurse181"))}}, cls)
                + (notes ? "<div class=\"cv-note\">" + Py.join("<br>", nt) + "</div>" : "");
    }
    public static String two_ways() { return two_ways("", 25.3); }
    /** 「간병인 지원 · 사용 원하는 니즈에 맞게 선택하세요」 — 모든 간병인 쪽 아래 */
    public static String two_ways(String cls, double mt) {
        return Py.fmt("<div class=\"cv-h\" style=\"margin-top:%spt\"><b>간병인 지원 · 사용 원하는 니즈에 맞게 선택하세요</b></div>"
                + "<div class=\"cv-two %s\"><div>%s<div class=\"x\"><small>간병인이 필요하다면</small><b>간병인 지원 입원일당</b><p>메리츠에서 간병인을 직접 보내드려요</p></div></div>"
                + "<div>%s<div class=\"x\"><small>간병비가 필요하다면</small><b>간병인 사용 입원일당</b><p>간병인을 사용한 일수만큼 일당으로 드려요</p></div></div></div>", mt, cls, _ic("caregiver"), _ic("care_cost"));
    }
    public static final String CARE_FOOT = "* 금액은 이 설계의 특약별 가입금액 기준입니다.";
    public static String page_care_support(Map<String, Object> cf) {
        String[][] A = {{"전화 1통으로 간병인 신청", "전화 <b>1688-0090</b>으로 간편하게 신청"}, {"추가 비용 없음", "물가가 올라도, 간병인 비용이 올라도 자기부담금 <b>0원</b>"}, {"언제든지 간병인 교체 가능", "전화 <b>1688-0090</b>으로 교체 신청 가능"}};
        StringBuilder adv = new StringBuilder();
        for (int i = 0; i < A.length; i++) adv.append(Py.fmt("<div class=\"cv-adv\"><span class=\"n\">%d</span><span class=\"t\">%s</span><span class=\"x\">%s</span></div>", (long) (i + 1), A[i][0], A[i][1]));
        String body = need_care() + tbl_support(cf, "sup", true) + "<div class=\"cv-h\" style=\"margin-top:15.7pt\"><b>간병인 지원 장점</b><span>간병인을 직접 구하지 않아도 되고, 간병비용 걱정이 없어요</span></div>" + adv + two_ways("sm", 18.1);
        return page("간병인 보장(간병인 지원)", body, CARE_FOOT, " data-zmax=\"1\" data-gap=\"14\"", " nt cvp");
    }
    public static String page_care_use(Map<String, Object> cf) {
        String[][] A = {{"간병인 사용", "약관이 정한 간병인<br>(병원 소속 · 간병 업체 등)"}, {"서류 준비", "입원 확인서<br>간병인 사용 영수증 등"}, {"보험금 청구", "모바일 앱, 홈페이지,<br>고객센터로 청구"}, {"보험금 지급", "보험금 심사 후 지급"}};
        StringBuilder steps = new StringBuilder();
        for (int i = 0; i < A.length; i++) steps.append(Py.fmt("<div><div class=\"h\"><span class=\"n\">%d</span><b>%s</b></div><p>%s</p></div>", (long) (i + 1), A[i][0], A[i][1]));
        String body = need_care() + tbl_use(cf, "use", true) + Py.fmt("<div class=\"cv-h\" style=\"margin-top:28.5pt\"><b>청구 방법</b></div><div class=\"cv-steps\">%s</div>", steps.toString()) + two_ways("md", 27.9);
        return page("간병인 보장(간병인 사용)", body, CARE_FOOT, " data-zmax=\"1\" data-gap=\"14\"", " nt cvp");
    }
    /** 간병인 지원 · 사용 둘 다 없을 때 — 두 표를 한 쪽에 같이 */
    public static String page_care_none(Map<String, Object> cf) {
        String foot = Py.truthy(cf.get("inj_only")) ? "* 이 설계의 간병인 보장은 상해 입원에만 있습니다(위 표는 질병 입원 기준)." : "* 이 설계에는 간병인 지원 · 사용 보장이 없습니다.";
        return page("간병인 보장", need_care() + tbl_support(cf, "none", false) + tbl_use(cf, "none", false) + two_ways(), foot, " data-zmax=\"1\" data-gap=\"14\"", " nt cvp");
    }

    // ═══════════════ 보장금액 세부내역(글씨 키움 · 쪽 나눔 자동) ═══════════════
    public static final String DETAIL_CSS = Txt.DETAIL_CSS, DETAIL_COLS = Txt.DETAIL_COLS, DETAIL_HEAD = Txt.DETAIL_HEAD, DETAIL_JS = Txt.DETAIL_JS;
    public static String detail_x10(Object v10) { String[] tu = fmt(v10, "만원"); return tu[0] + Py.orS(tu[1], "원"); }
    public static String _esc(String t) { return (t == null ? "" : t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"); }
    /** GaProposal.calc_sections()(보장요약 칸의 합산 계산서) → 표 묶음. 구분 보장금액 = 특약별 합(다르면 멈춘다) */
    @SuppressWarnings("unchecked")
    public static List<Object> detail_groups() {
        List<Object> out = new ArrayList<>();
        for (Object[] sc : GaProposal.calc_sections()) {
            String title = (String) sc[0];
            List<Object> groups = new ArrayList<>();
            Map<String, Object> sec = Py.dict("title", title.replace("뇌,심", "뇌 · 심"), "groups", groups);
            for (Object[] row : (List<Object[]>) sc[1]) {
                String lab = (String) row[0];
                Object v = row[1];
                List<Object[]> rs = (List<Object[]>) row[2];
                Matcher m = Py.match("\\[([^\\]]+)\\]\\s*(.*)", lab);
                String cat = m != null ? m.group(1) : "", item = m != null ? m.group(2) : lab;
                List<Object> amts = new ArrayList<>();
                for (Object[] r : rs) amts.add(r[3]);
                if (isnum(v) && !rs.isEmpty() && Math.abs(Py.num(Py.sub(Py.sum(amts), v))) > 0.01) throw new RuntimeException(Py.fmt("세부내역 합계 불일치 : %s %s ≠ %s", lab, v, Py.sum(amts)));
                long n = Math.max(1, rs.size());
                String k = Py.fmt("<td class=\"k\" rowspan=\"%d\"><small>%s</small><b>%s</b></td>", n, _esc(cat), _esc(item).replace("(", "<wbr>(").replace(",", ",<wbr>"));
                String[] tu = fmt(v, "만원");
                String a;
                if (tu[0] == null) a = Py.fmt("<td class=\"m na\" rowspan=\"%d\"><span class=\"pill\">미가입</span></td>", n);
                else if (v instanceof String) a = Py.fmt("<td class=\"m\" rowspan=\"%d\"><b class=\"tx\">%s</b></td>", n, _esc(tu[0]));
                else {
                    Object v10 = null;
                    if (Py.match("\\[진단금?\\]", lab) != null) {      // 진단금 구분에만 둘째 줄
                        List<Object[]> pairs = new ArrayList<>();
                        for (Object[] r : rs) pairs.add(new Object[]{r[0], r[3]});
                        v10 = esc10_after(v, pairs);
                    }
                    String x10 = v10 != null ? Py.fmt("<div class=\"x10\">계약 10년 후 진단 시<br><b>%s</b></div>", detail_x10(v10)) : "";
                    a = Py.fmt("<td class=\"m\" rowspan=\"%d\"><b>%s</b><span>%s</span>%s</td>", n, tu[0], Py.orS(tu[1], "원"), x10);
                }
                String g;
                if (rs.isEmpty()) g = Py.fmt("<tbody class=\"g\"><tr>%s%s<td class=\"n none\" colspan=\"3\">이 설계에는 가입되지 않은 보장입니다</td></tr></tbody>", k, a);
                else {
                    StringBuilder trs = new StringBuilder();
                    for (int i = 0; i < rs.size(); i++) {
                        Object[] r = rs.get(i);
                        String nm_ = (String) r[0], note = (String) r[1];
                        Object man = r[2], amt = r[3];
                        String ga = man == null ? "" : (won(man) + (won(man).endsWith("억") ? "원" : "만원"));
                        String ea = won(amt) + (won(amt).endsWith("억") ? "원" : "만원");
                        String nmh = _esc(nm_) + (Py.truthy(note) ? Py.fmt("<span class=\"sub\"> : %s</span>", _esc(note)) : "");
                        String lg_ga = eok_rest(man) ? " lg" : "", lg_ea = eok_rest(amt) ? " lg" : "";
                        trs.append(Py.fmt("<tr>%s<td class=\"n\">%s</td><td class=\"ga%s\">%s</td><td class=\"ea%s\">%s</td></tr>", i == 0 ? (k + a) : "", nmh, lg_ga, ga, lg_ea, ea));
                    }
                    g = Py.fmt("<tbody class=\"g\">%s</tbody>", trs.toString());
                }
                groups.add(g);
            }
            out.add(sec);
        }
        return out;
    }
    /** 세부내역 HTML(스스로 쪽을 나누는 스크립트 포함) — 파이썬 render_detail 이 브라우저에 넘기는 글자 */
    public static String detail_html() {
        List<Object> secs = detail_groups();
        return Py.fmt("<!doctype html><html><head><meta charset=\"utf-8\"><style>%s%s</style></head><body><div id=\"root\"></div><script>const SECTIONS=%s;const COLS=%s;const HEAD=%s;%s</script></body></html>",
                fonts_css(), DETAIL_CSS, Json.dumpsU(secs), Json.dumps(DETAIL_COLS), Json.dumps(DETAIL_HEAD), DETAIL_JS);
    }
    public static String detail_overlay_html(int n) {
        Map<String, Object> SL = slots();
        Object W = Py.gl(SL, "size").get(0), H = Py.gl(SL, "size").get(1);
        Map<String, Object> pn = null, ft = null;
        for (Object x : Py.gl(Py.gm(SL, "slots"), "detail")) { if ("pageno".equals(Py.gs(x, "key"))) pn = Py.M(x); if ("footer".equals(Py.gs(x, "key"))) ft = Py.M(x); }
        StringBuilder pages = new StringBuilder();
        for (int i = 0; i < n; i++)
            pages.append(Py.fmt("<div class=\"pg\">%s%s</div>", at_r(pn.get("x1"), d(pn, "base"), d(pn, "size"), Py.fmt("<span style=\"color:#777\">%d / %d</span>", (long) (i + 1), (long) n), "", K_BASE),
                    at_r(ft.get("x1"), d(ft, "base"), d(ft, "size"), who_html(d(ft, "size"), "#333333", "#111111"), "white-space:nowrap;font-weight:500", K_BASE)));
        String css = Py.fmt("@page{size:%spt %spt;margin:0}html,body{margin:0;background:transparent;font-family:P;-webkit-print-color-adjust:exact;print-color-adjust:exact}"
                + ".pg{position:relative;width:%spt;height:%spt;overflow:hidden;page-break-after:always}.o{position:absolute;line-height:1;white-space:nowrap}", W, H, W, H);
        return Py.fmt("<!doctype html><html><head><meta charset=\"utf-8\"><style>%s%s</style></head><body>%s</body></html>", fonts_css(), css, pages.toString());
    }

    // ═══════════════ 표지 · 보장요약(GA 양식 · GaProposal 그대로) ═══════════════
    public static final String[] FOOT_MAX = {"상기 보장 예시는 상급종합병원 기준 최대 보장금액 예시이며, 급여·비급여 여부, 의료기관 종류, 치료 방법에 따라", "보험금이 달라질 수 있습니다. 세부 내용은 약관을 참고해 주시기 바랍니다."};
    public static String _pt_text(double x0, double base, double size, String text, String color) { return _pt_text(x0, base, size, text, color, 400, "N,P"); }
    public static String _pt_text(double x0, double base, double size, String text, String color, long weight, String ff) {
        return Py.fmt("<div style=\"position:absolute;left:%.2fpt;top:%.2fpt;font-size:%.2fpt;line-height:1;color:%s;font-weight:%d;white-space:nowrap;font-family:%s;letter-spacing:0\">%s</div>",
                x0, base - (ff.startsWith("N") ? K_N : K_BASE) * size, size, color, weight, ff, text);
    }
    public static String _pt_box(double x0, double y0, double x1, double y1, String color) {
        return Py.fmt("<div style=\"position:absolute;left:%.2fpt;top:%.2fpt;width:%.2fpt;height:%.2fpt;background:%s\"></div>", x0, y0, x1 - x0, y1 - y0, color);
    }
    /** 보장요약 칸 값 — 0 은 「미가입」 으로 보인다(GA 최종 시안) */
    public static String summary_cells() {
        Map<String, Object> sp = Py.gm(GaOverlay.spec("p1"), "fields");
        StringBuilder out = new StringBuilder();
        for (Object c0 : GaSpec.CELLS) {
            Map<String, Object> c = Py.M(c0);
            if (!Py.eq(c.get("page"), 1L)) continue;
            String key = (String) c.get("key");
            if (!sp.containsKey(key)) { out.append(Py.fmt("<!-- 자리 없음 %s -->", key)); continue; }
            Object v = V(key);
            if (isnum(v) && Math.abs(Py.num(v)) < 1e-9) v = null;
            Map<String, Object> f = GaOverlay.style_for(sp, key, v);
            if (isnum(v)) f = GaOverlay.fit(f, won(v), "만원");
            else if (v instanceof String) f = GaOverlay.fit(f, (String) v);
            out.append(GaOverlay.field_html(f, GaProposal.M(v), "val"));
            Map<String, Object> d_ = dx10_sum(key);
            if (Py.truthy(d_)) out.append(_pt_text_r(Py.num(d_.get("x1")), Py.num(d_.get("base")), Py.num(d_.get("size")), (String) d_.get("text"), "#555555", 500, "N,P"));
        }
        return out.toString();
    }
    /** 보장요약 진단금 칸의 둘째 줄 자리(칸 상자 오른쪽 아래) — 그리기와 인쇄 검증이 같이 쓴다 */
    public static Map<String, Object> dx10_sum(String key) {
        if (!DX10_SUM.contains(key)) return null;
        Object v10 = dx10(key);
        if (v10 == null) return null;
        Map<String, Object> sp = GaOverlay.spec("p1");
        double k = 594.96 / Py.num(Py.gl(sp, "size").get(0));
        List<Object> box = Py.gl(Py.gm(Py.gm(sp, "fields"), key), "box");
        double x1 = Py.num(box.get(2)) * k, y1 = Py.num(box.get(3)) * k;
        return Py.dict("key", key, "x1", x1 - 1.2, "base", y1 - 0.2, "size", 5.5, "text", dx10_text(v10, false));
    }
    public static String _pt_text_r(double x1, double base, double size, String text, String color, long weight, String ff) {
        return Py.fmt("<div style=\"position:absolute;right:%.2fpt;top:%.2fpt;font-size:%.2fpt;line-height:1;color:%s;font-weight:%d;white-space:nowrap;font-family:%s;letter-spacing:0\">%s</div>",
                594.96 - x1, base - (ff.startsWith("N") ? K_N : K_BASE) * size, size, color, weight, ff, text);
    }
    /** 보장요약 = GA 가안 그림 + 값(합성 모드) + 시안의 고친 글자 세 군데(「다빈치로봇」 · 체증형 주석 · 바닥 안내 두 줄) */
    public static String summary_page() {
        Map<String, Object> sp = Py.gm(GaOverlay.spec("p1"), "fields");
        String prem = Py.orS(GaProposal.PREMIUM, "").replace("원", "");
        String body = GaProposal._ov_text(sp, "hdr.dno", "설계번호 : " + Py.or(GaProposal.HEAD.get("no"), "-")) + GaProposal._ov_text(sp, "hdr.product", Py.orS(GaProposal.PRODUCT, "-"), null, 52L) + GaProposal._ov_text(sp, "hdr.insured", GaProposal.who_line())
                + GaProposal._ov_text(sp, "hdr.premium", Py.orS(prem, "-"), !prem.isEmpty() ? "원" : null, null) + summary_cells() + GaProposal._ov_footer(sp);
        String fix = _pt_box(155.5, 299.5, 218.0, 313.0, "#FCFCFC") + _pt_text(157.59, 310.5, 9.8, "다빈치로봇", "#222222", 500, "Pretendard,P")      // 가안 그림의 「로봇암수술」 → 「다빈치로봇」
                + _pt_text(33.0, 771.75, 6.6, ESC_NOTE, "#777777")
                + (has_esc10() ? _pt_text(ESC10_X, 771.75, 6.6, ESC10_NOTE, "#777777") : "")
                + _pt_box(30.0, 781.5, 400.0, 803.5, "#FFFFFF") + _pt_text(32.39, 791.25, 7.2, FOOT_MAX[0], "#777777") + _pt_text(32.39, 800.25, 7.2, FOOT_MAX[1], "#777777");
        return GaOverlay.page_open("p1") + body + fix + "</div>";
    }
    public static String cover_summary_html() {
        if (!GaProposal.MOCK_MODE) throw new RuntimeException("자바 판은 가안 합성 모드만 지원합니다(GA_MOCK=0 · ga_assets/mock 자료 없음은 지원하지 않음)");
        return Py.fmt("<!doctype html><html><head><meta charset=\"utf-8\"><style>%s%s%s</style></head><body>%s</body></html>",
                GaProposal._font_css() + fonts_css() + noto_css(), GaProposal.CSS, GaOverlay.page_css() + GaProposal.MOCK_CSS, GaProposal.p0_mock() + summary_page());
    }

    // ═══════════════ 묶기 ═══════════════
    /** 마지막으로 만든 HTML(정답지 대조 · 점검용) — [이름, html] 차례대로 cs · ov · html · detail · dov */
    public static final List<String[]> LAST_HTML = new ArrayList<>();
    /**
     * 담보코드 입력 한 건(CodeInput.parse 를 거친 Map) → 새 양식 PDF · 로그. 돌려주는 것 : {out_pdf, log, info}.
     * 중간 파일은 한 건마다 임시 폴더에 만들고 끝나면 지운다(GA_V2_KEEP=1 이면 남겨 둔다).
     */
    public static Object[] build(Map<String, Object> design, String out_pdf) { return build(design, out_pdf, ""); }
    public static Object[] build(Map<String, Object> design, String out_pdf, String age) {
        String root = Render.begin_job();
        try {
            try {
                return _build(design, out_pdf, age);
            } catch (Pipeline.DesignUnreadable e) {
                throw e;                                                   // 만들지 않는 상품 등 — 크로뮴은 멀쩡하다(이유를 그대로 올린다)
            } catch (RuntimeException | AssertionError e) {
                Render.close_browser();                                    // 실패한 건 뒤에는 크로뮴을 새로 띄운다
                if (!Py.has("closed|crash|Target|disconnected", String.valueOf(e.getMessage()))) throw e;
                return _build(design, out_pdf, age);                       // 크로뮴이 죽어서 난 오류면 새로 띄워 한 번 더
            }
        } finally { Render.end_job(root); }
    }
    /** os.path.splitext(p)[0] — 마지막 경로 조각의 마지막 점 앞까지(맨 앞의 점들은 확장자로 보지 않는다) */
    static String splitext0(String p) {
        int sep = Math.max(p.lastIndexOf('/'), p.lastIndexOf(File.separatorChar));
        int dot = p.lastIndexOf('.');
        if (dot <= sep) return p;
        int lead = sep + 1;
        while (lead < dot && p.charAt(lead) == '.') lead++;
        return lead == dot ? p : p.substring(0, dot);
    }
    public static final Map<String, Object> CARE_KO = Py.dict("support", "간병인 지원", "use", "간병인 사용", "none", "지원 · 사용 함께(둘 다 미가입)");
    public static Object[] _build(Map<String, Object> design, String out_pdf0, String age) {
        long t0 = System.nanoTime();
        String out_pdf = Py.truthy(out_pdf0) ? out_pdf0 : Py.path("ga_output", GaProposal.tag_of(design) + "_GA2.pdf");
        load(design, age);
        Map<String, Object> cf = CF();
        String tag = GaProposal.tag_of(design);
        LAST_HTML.clear();
        // 1) 표지 · 보장요약  2) 시안 틀 + 값  3) 새로 그리는 쪽  4) 세부내역 — HTML 을 파이썬 판과 같은 차례로 만든다(로그 차례가 같게)
        String cs = cover_summary_html();
        String ov = overlay_html();
        StringBuilder pages = new StringBuilder(page_surg(0)).append(page_surg(1));
        for (Object k : Py.gl(cf, "pages")) {
            if ("support".equals(k)) pages.append(page_care_support(cf));
            else if ("use".equals(k)) pages.append(page_care_use(cf));
            else if ("none".equals(k)) pages.append(page_care_none(cf));
            else throw new Py.KeyError(k);
        }
        String ph = Py.fmt("<!doctype html><html><head><meta charset=\"utf-8\"><style>%s</style></head><body>%s</body></html>", css(), pages.toString());
        String dh = detail_html();
        LAST_HTML.add(new String[]{"cs", cs}); LAST_HTML.add(new String[]{"ov", ov}); LAST_HTML.add(new String[]{"html", ph}); LAST_HTML.add(new String[]{"detail", dh});
        // 5) 그리기 · 묶기 : 표지 · 요약 → 암① 암② 뇌 심 → 수술 ① ② → 간병 → 세부내역 → 안내사항
        Map<String, Object> r = PdfKit.assemble(tag, out_pdf, cs, ov, ph, dh, n -> { String h = detail_overlay_html(n); LAST_HTML.add(new String[]{"dov", h}); return h; });
        List<Object> warn = Py.gl(r, "warn");
        long n = Py.lng(r.get("detail_pages"));
        Map<String, Object> info = Py.dict("design", GaProposal.label_of(design), "product", GaProposal.PRODUCT, "pages", r.get("pages"), "care", cf.get("pages"), "detail_pages", n, "warn", warn,
                "sec", Py.round((System.nanoTime() - t0) / 1e9, 1), "riders", GaProposal.NRID, "fit", r.get("fit"));
        String log = splitext0(out_pdf) + "_log.txt";
        StringBuilder f = new StringBuilder();
        List<Object> ck = new ArrayList<>();
        for (Object k : Py.gl(cf, "pages")) ck.add(Py.at(CARE_KO, k));
        f.append(Py.fmt("원본 설계서 : %s\n상품 : %s\n보험료 : %s\n담보 %d건 · %d쪽 · 간병인 쪽 : %s · 세부내역 %d쪽 · %.1f초\n\n", info.get("design"), GaProposal.PRODUCT, GaProposal.PREMIUM, GaProposal.NRID, info.get("pages"),
                Py.join(" + ", ck), n, info.get("sec")));
        f.append("[지면 경고] " + (!warn.isEmpty() ? Py.join(" / ", warn) : "없음") + "\n\n[계산 로그 — 빈칸 · 0원의 이유]\n");
        for (Object it : ScenEngine.issues_grouped()) f.append(Py.fmt("- [%s] %s — %s\n", Py.get(it, "구분"), Py.get(it, "담보"), Py.get(it, "사유")));
        Py.write(log, f.toString());
        return new Object[]{out_pdf, log, info};
    }
}
