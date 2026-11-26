package meai.sp;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Supplier;
import java.util.regex.Matcher;

/**
 * 파이썬 ga_proposal.py 의 **자료 부분** — 담보코드 입력 한 건을 읽어 모든 칸 값을 채우고(load), 세부내역(합산 계산서)의 줄을 만든다.
 * 옛 6쪽 지면 HTML(p0~p3 · mock · CSS · calc_table · calc_paginate · render · build · main)과 설계서 PDF 읽기(ga_head)는 여기 없다 —
 * 새 양식(GaV2)이 쓰는 지면 조각은 지면 단계에서 옮긴다.
 * 전역 상태(RID · VAL …)는 파이썬과 같이 static 이라 한 번에 한 건만 계산한다.
 */
public final class GaProposal {
    private GaProposal() {}

    public static final String BRAND = "메리츠 스마트 제안서";
    public static String won(Object v) { return GaCare.won(v); }

    /** 표지 「탑재상품」(GA 명칭 그대로) — {이름, 상품명 패턴}. 설계서 상품명을 읽는 규칙이지 화이트리스트가 아니다 */
    public static final String[][] GA_PRODUCTS = {
            {"(무)메리츠The건강한내Mom대로5.10.5보장보험", "The건강한\\s*(메리츠)?\\s*내Mom대로\\s*5\\.10\\.5"},
            {"(무)메리츠The건강한5.10.5보장보험", "The건강한\\s*5\\.10\\.5"},
            {"(무)알파Plus보장보험", "(?<!The좋은)\\s*(알파\\s*Plus|케어프리보험\\s*M-?\\s*Basket)"},
            {"(무)메리츠The좋은알파Plus보장보험", "The좋은\\s*(알파|케어프리)"},
            {"(무)내Mom같은어린이보험(태아전용포함)", "내Mom같은"},
            {"(무)내Mom대로보장보험", "^(?!.*(The좋은|5\\.10\\.5)).*내Mom대로\\s*보장보험"},
            {"(무)메리츠The좋은내Mom대로보장보험2607", "The좋은\\s*내Mom대로"},
            {"(무)메리츠통합간편건강보험(연,세만기형)", "^(?!.*355).*통합간편건강보험"},
            {"(무)메리츠통합간편건강보험(연,세만기형)2607(355입원,수술고지간편심사형)", "통합간편건강보험.*355"},
            {"(무)The가벼운간편355건강보험(세만기형)", "가벼운\\s*간편\\s*355"},
            {"(무)메리츠간편31건강보험2607", "간편\\s*31"},
            {"(무)메리츠또걸려도또받는암보험(연,세만기형)", "또\\s*걸려도\\s*또\\s*받는\\s*암보험"},
            {"(무)메리츠또걸려도또받는간편한암보험(연,세만기형)", "또\\s*걸려도\\s*또\\s*받는\\s*간편한\\s*암보험"},
            {"(무)메리츠또걸려도또받는암보험(맞춤간편심사형)(연,세만기형)", "또\\s*걸려도\\s*또\\s*받는\\s*암보험.*맞춤\\s*간편\\s*심사형"},
            {"(무)(메리츠)암보험(세만기형)2610", "^\\(무\\)\\(?메리츠\\)?암보험\\(세만기형\\)"},
            {"(무)(메리츠)암보험(연만기형)2610", "^\\(무\\)\\(?메리츠\\)?암보험\\(연만기형\\)"}};
    /** 상품명 → GA_PRODUCTS 의 자리(없으면 null). 더 구체적인 이름(긴 패턴)이 이긴다 */
    public static Long ga_product_idx(String product) {
        String p = Py.sub("\\s+", "", product == null ? "" : product);
        Long best = null;
        for (int i = 0; i < GA_PRODUCTS.length; i++) {
            if (!Py.has(GA_PRODUCTS[i][1].replace("\\s*", ""), p)) continue;
            if (best == null || GA_PRODUCTS[i][1].length() > GA_PRODUCTS[best.intValue()][1].length()) best = (long) i;
        }
        return best;
    }

    // ───────── 입력 읽기 + 공통 계산(한 건마다 load() 가 다시 채운다) ─────────
    public static List<Object> RID = new ArrayList<>();
    public static Map<String, Object> META = new LinkedHashMap<>();
    public static String WHO = "", PRODUCT = "", PREMIUM = "", SHORTP = "";
    public static long NRID = 0;
    /** 표지 · 머리줄 : 피보험자 이름 · 성별 · 보험나이 · 가계약번호 · 컨설턴트(넘겨받은 글자만 · 없으면 빈칸) */
    public static Map<String, Object> HEAD = new LinkedHashMap<>();
    /** 칸 key → Object[]{값, 지급 줄 List, 로그 List} — GaSpec.cell_value */
    public static Map<String, Object[]> VAL = new LinkedHashMap<>();
    /** 이 설계의 상품 라인(특약 마스터) */
    public static String LINE = "";

    /** 설계도 캡처 · 견본용(GA_MASK=1) : 피보험자 · 가계약번호 · 소속 · 컨설턴트 · 전화를 가린다(계산과 무관) */
    public static Map<String, Object> _mask(Map<String, Object> h) {
        if ("1".equals(Py.env("GA_MASK"))) {
            Map<String, Object> m = new LinkedHashMap<>(h);
            m.put("name", Py.truthy(h.get("name")) ? "○○○" : h.get("name"));
            m.put("no", Py.truthy(h.get("no")) ? Py.rep("●", ((String) h.get("no")).length()) : h.get("no"));
            m.put("org", Py.truthy(h.get("org")) ? "○○본부" : h.get("org"));
            m.put("agent_name", Py.truthy(h.get("agent_name")) ? "○○○" : h.get("agent_name"));
            m.put("mobile", Py.truthy(h.get("mobile")) ? "010-****-****" : h.get("mobile"));
            m.put("tel", Py.truthy(h.get("tel")) ? "0*-****-****" : h.get("tel"));
            m.put("code", Py.truthy(h.get("code")) ? "*****" : h.get("code"));
            m.put("agent", "");
            return m;
        }
        return h;
    }

    public static boolean is_data(Object design) { return design instanceof Map; }
    /** 산출물 파일 이름용(ASCII) */
    public static String tag_of(Object design) { return is_data(design) ? CodeInput.tag(Py.M(design)) : ascii_name((String) design); }
    public static String label_of(Object design) {
        if (is_data(design)) return CodeInput.label(Py.M(design));
        String s = (String) design;
        return s.substring(s.lastIndexOf('/') + 1);
    }

    /** 담보코드 입력 한 건(CodeInput.parse 를 거친 Map)을 읽어 모든 칸 값을 채운다 */
    public static void load(Map<String, Object> design) { load(design, ""); }
    public static void load(Map<String, Object> design, String age0) {
        ScenEngine.ISSUES.clear(); GaSpec.clear_cache();
        META = CodeInput.meta(design); _refuse_excluded();
        RID = CodeInput.riders(design); LINE = (String) design.get("_line");
        String ia = (String) Py.gm(design, "insured").get("age");
        final String age = Py.truthy(age0) ? age0 : (Py.truthy(ia) ? (ia + "세") : "");
        _fill(() -> _mask(CodeInput.head(design, age)), age);
    }
    /** 제작하지 않기로 한 상품(rules.json > exclude_products)은 만들지 않는다 */
    public static void _refuse_excluded() {
        String nm = Py.sub("\\s+", "", Py.gs0(META, "product"));
        for (Object x0 : Py.L(Py.get(ScenEngine.RULEDOC, "exclude_products", new ArrayList<Object>()))) {
            Map<String, Object> x = Py.M(x0);
            if (!nm.isEmpty() && Py.has((String) x.get("m"), nm))
                throw new Pipeline.DesignUnreadable(Py.fmt("이 상품은 스마트 제안서를 만들지 않는 상품입니다 — %s. %s", Py.gs0(x, "nm"), Py.gs0(x, "why")));
        }
    }
    public static void _fill(Supplier<Map<String, Object>> head_fn, String age) {
        String sex = Py.gs0(META, "sex");
        WHO = Py.fmt("고객님 (%s%s)", sex.equals("F") ? "여" : (sex.equals("M") ? "남" : ""), Py.truthy(age) ? (" · " + age) : "");
        PRODUCT = Py.strip(Py.sub("\\s+", " ", Py.gs0(META, "product")).replace("( ", "("));
        PREMIUM = Py.gs0(META, "premium");
        NRID = RID.size();
        String sp = Py.strip(Py.resplit("보장보험|건강보험|암보험", PRODUCT).get(0).replace("(무) 메리츠 ", "").replace("(무)메리츠", ""));
        SHORTP = (sp.isEmpty() ? PRODUCT : sp).replace("%", "%%");
        HEAD = head_fn.get();
        Map<String, Object[]> v = new LinkedHashMap<>();
        for (Object c : GaSpec.CELLS) v.put((String) Py.M(c).get("key"), GaSpec.cell_value(Py.M(c), RID));
        VAL = v;
    }
    /** 「민메리 (여자, 20세)」 — 읽은 것만 */
    public static String who_line() {
        List<Object> xs = new ArrayList<>();
        for (String k : new String[]{"sex", "age"}) if (Py.truthy(HEAD.get(k))) xs.add(HEAD.get(k));
        String inner = Py.join(", ", xs);
        String s = Py.strip(Py.gs0(HEAD, "name") + (!inner.isEmpty() ? Py.fmt(" (%s)", inner) : ""));
        return s.isEmpty() ? "-" : s;
    }
    /** 1쪽 머리줄 : 상품명 · 피보험자(이름, 성별, 보험나이) · 월 보험료 · 가계약번호 */
    public static String head_bar() {
        return Py.fmt("<div class=\"hb\"><span><em>상품명</em>%s</span><span><em>피보험자</em>%s</span><span><em>월 보험료</em>%s</span><span><em>가계약번호</em>%s</span></div>",
                Py.orS(PRODUCT, "-"), who_line(), Py.orS(PREMIUM, "-"), Py.truthy(HEAD.get("no")) ? HEAD.get("no") : "-");
    }
    public static Object V(String key) { return VAL.get(key)[0]; }
    public static List<Object> L(String key) { return Py.L(VAL.get(key)[1]); }
    public static long F(List<Object> lines) { return Py.round(Py.num(ScenEngine.total_by(lines, "first"))); }

    /** 칸 값 표시 — 숫자(만원) · null(미가입) · '간병인 보내줌' · '면책' */
    public static String M(Object v) { return M(v, false); }
    public static String M(Object v, boolean big) {
        if (v == null) return "<span class=\"na\">미가입</span>";
        if (v instanceof String) return v.equals(GaCare.SEND) ? Py.fmt("<span class=\"txt\">%s</span>", v) : Py.fmt("<span class=\"na\">%s</span>", v);
        return Py.fmt("<b class=\"v%s%s\">%s<i>만원</i></b>", Math.abs(Py.num(v)) < 1e-9 ? " z" : "", big ? " big" : "", won(v));
    }
    public static String _ns(Object x) { return Py.sub("\\s+", "", Py.truthy(x) ? (String) x : ""); }

    // ───────── 보장금액 세부내역(보장요약 칸의 합산 계산서) ─────────
    /** 지급 줄 이름과 같은 설계 담보의 가입금액(만원) — 못 찾으면 null */
    public static Object _man_of(String name) {
        String want = _ns(name);
        for (Object r0 : RID) {
            Map<String, Object> r = Py.M(r0);
            String rn = _ns(r.get("name"));
            if (rn.equals(want) || rn.replace("치매주요질환입원일당", "질병입원일당").equals(want))
                return (Py.truthy(r.get("man")) || !((String) r.get("name")).contains("간병인지원")) ? r.get("man") : (Object) GaCare.daily(r);
        }
        return null;
    }
    /** 세부내역 특약명 — 26종 항암방사선및약물치료비의 꼬리 [세부급부명]은 뗀다 */
    public static String disp_name(String name) {
        String n = Py.strip(Py.sub("\\s+", " ", name));
        if (Py.match("^(?:\\(\\d+년갱신\\)\\s*)?(?:갱신형\\s*)?26종", n) != null) n = Py.sub("\\s*\\[[^\\[\\]]*(\\([^()]*\\))*[^\\[\\]]*\\]\\s*$", "", n);
        return n;
    }
    /** 담보명 옆 연한 글자 — 몇 종(1-5종 · 1-7종 수술비) · 통합치료비/통합생활지원비는 어느 항목에서 나왔나 */
    public static String line_note(Map<String, Object> l) {
        String why = Py.gs0(l, "why"), rule = Py.gs0(l, "rule");
        if ("통합치료비".equals(l.get("group")) || rule.equals("itc") || rule.equals("ls_monthly")) {
            List<Object> items = new ArrayList<>();
            for (String p : Py.resplit("\\s·\\s", Py.split(why, "(연간 한도").get(0))) {
                String x = Py.strip(Py.sub("\\s*[\\d,.]+\\s*$", "", p));
                if (!x.isEmpty()) items.add(x);
            }
            return Py.join(", ", items);
        }
        Matcher m = rule.startsWith("surg_grade") ? Py.search("(?<![-\\d])(\\d)종", why) : null;
        return m != null ? m.group(0) : "";
    }
    /** 칸 하나 → Object[]{구분, 값, 줄 List&lt;Object[]{특약명, 메모, 가입금액, 지급액}&gt;}. 그 칸의 집계 방식으로 실제 합산된 줄만 적는다 */
    public static Object[] calc_row(Map<String, Object> c) {
        Object[] val = VAL.get(c.get("key"));
        Object v = val[0];
        List<Object> lines = Py.L(val[1]);
        List<Object[]> used = new ArrayList<>();
        if ("engine".equals(c.get("kind"))) {
            for (Object l : lines) { Object a = GaSpec.counts(Py.M(l), (String) c.get("mode")); if (Py.truthy(a)) used.add(new Object[]{l, a}); }
        } else {
            for (Object l : lines) used.add(new Object[]{l, Py.M(l).get("amt")});
        }
        String lab = Py.truthy(c.get("row")) ? Py.fmt("[%s] %s", c.get("row"), c.get("col")) : (String) c.get("col");
        lab = lab.replace("(현물지원)", "").replace("(금액지원)", "");
        List<Object[]> rows = new ArrayList<>();
        if (v != null) for (Object[] u : used) {
            String nm = (String) Py.M(u[0]).get("name");
            rows.add(new Object[]{disp_name(nm), line_note(Py.M(u[0])), _man_of(nm), u[1]});
        }
        return new Object[]{lab, v, rows};
    }
    /** 세부내역은 보장요약(1쪽) 칸만 — [ {제목, [calc_row …]} … ] */
    @SuppressWarnings("unchecked")
    public static List<Object[]> calc_sections() {
        List<String> ca = new ArrayList<>(), bh = new ArrayList<>(), dz = new ArrayList<>(), care = new ArrayList<>();
        for (Object[] g : GaSpec._ca1) for (Object[] it : (List<Object[]>) g[1]) ca.add("p1.ca." + it[1]);
        for (Object[] g : GaSpec._bh1) for (Object[] it : (List<Object[]>) g[1]) bh.add("p1.bh." + it[1]);
        for (String n : GaSpec.DZ_ORDER) dz.add("p1.dz." + n);
        for (String k : new String[]{"hosp", "nh", "nurse", "unused", "use_gen", "use_nh", "use_nurse"}) care.add("p1.care." + k);
        List<Object[]> out = new ArrayList<>();
        out.add(new Object[]{"암 보장 세부 내역", keys(ca)});
        out.add(new Object[]{"뇌,심 보장 세부 내역", keys(bh)});
        out.add(new Object[]{"주요수술 보장 세부 내역", keys(dz)});
        out.add(new Object[]{"간병인 보장 세부 내역", keys(care)});
        return out;
    }
    private static List<Object[]> keys(List<String> ks) {
        List<Object[]> o = new ArrayList<>();
        for (String k : ks) o.add(calc_row(Py.M(GaSpec.KEY.get(k))));
        return o;
    }

    public static final long CALC_PAGES = 1, CALC_BUDGET = 50, _LINE_CH = 46;
    /** 세부내역 한 줄 묶음의 분량(옛 6쪽 지면의 쪽 나누기 단위 — 새 양식은 브라우저가 나눈다) */
    @SuppressWarnings("unchecked")
    public static double calc_units(Object[] row) {
        String lab = (String) row[0];
        List<Object[]> rs = (List<Object[]>) row[2];
        double n = 0.15;
        if (rs.isEmpty()) return n + 1;
        for (Object[] r : rs) {
            String nm = (String) r[0], note = (String) r[1];
            n += Math.max(1, (long) Math.ceil((nm.length() + (Py.truthy(note) ? note.length() + 3 : 0)) / (double) _LINE_CH));
        }
        return n + 0.3 * Math.max(0, (long) Math.ceil(lab.length() / 14.0) - 1);
    }

    /** 산출물 파일명은 ASCII — 한글 파일명은 영문 · 숫자만 남기고, 없으면 design */
    public static String ascii_name(String path) {
        String base = path.substring(path.lastIndexOf('/') + 1);
        int dot = base.lastIndexOf('.');
        int lead = 0;
        while (lead < base.length() && base.charAt(lead) == '.') lead++;
        String stem = dot >= lead ? base.substring(0, dot) : base;      // os.path.splitext — 맨 앞의 점들은 확장자로 보지 않는다
        String a = Py.strip(Py.sub("[^A-Za-z0-9_-]+", "_", stem), "_");
        if (!Py.has("[A-Za-z]", a)) a = "design" + (!a.isEmpty() ? "_" + a : "");
        return a;
    }
}
