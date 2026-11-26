package meai.sp;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 파이썬 code_input.py — 담보코드 입력(JSON)을 「설계서를 읽은 것」 과 같은 담보 줄로 바꾼다.
 * 입력 사양 · 담보 찾는 차례(이름 → 담보 식별표 → 계산 제외 + 로그)는 파이썬 판 그대로다.
 */
public final class CodeInput {
    private CodeInput() {}

    public static final long SCHEMA = 1;

    /** 입력 JSON 이 사양과 다름 — 메시지는 호출한 쪽에 그대로 보여 줄 쉬운 말 */
    public static class InputError extends IllegalArgumentException {
        private static final long serialVersionUID = 1L;
        public InputError(String msg) { super(msg); }
    }

    // ── 담보 식별표(있으면) ──
    /** 한 번 읽어 기억한다. 다시 읽게 하려면 null 로(시험용) */
    public static Map<String, Object> _CM = null;
    /** {'단위상품코드|담보코드': {'id': 특약 마스터 ID, 'p': 상품}} — 없으면 빈 표(이름으로만 찾는다). 경로 : GA_CODE_MAP 또는 자료 폴더의 code_map.json */
    public static Map<String, Object> code_map() {
        if (_CM == null) {
            String p = Py.env("GA_CODE_MAP");
            if (p == null) p = Py.path("code_map.json");
            Map<String, Object> cm = new LinkedHashMap<>();
            if (Py.exists(p)) {
                Map<String, Object> d = Py.M(Json.parse(Py.read(p)));
                Object mp = d.get("map");
                if (Py.truthy(mp)) cm = Py.M(mp);
                Map<String, Object> meta = new LinkedHashMap<>();
                for (Map.Entry<String, Object> e : d.entrySet()) if (!e.getKey().equals("map")) meta.put(e.getKey(), e.getValue());
                cm.put("_meta", meta);
            }
            _CM = cm;
        }
        return _CM;
    }
    private static Map<String, Object> _REC = null;
    public static Map<String, Object> master(Object p, Object i) {
        if (_REC == null) {
            Map<String, Object> rec = new HashMap<>();
            for (Object o : Py.gl(Matcher_.DB, "riders")) { Map<String, Object> r = Py.M(o); rec.put(r.get("p") + "\u0000" + r.get("id"), r); }
            _REC = rec;
        }
        return Py.M(_REC.get(p + "\u0000" + i));
    }

    // ── 입력 점검 ──
    public static String _txt(Object v) { return _txt(v, 200); }
    public static String _txt(Object v, int n) { return Py.head(Py.strip(Py.sub("\\s+", " ", Py.str(v != null ? v : ""))), n); }
    public static long _won(Object v, String where) {
        if (v == null || "".equals(v)) return 0;
        if (v instanceof Boolean) throw new InputError(Py.fmt("%s : 금액은 숫자(원)여야 합니다", where));
        double w; boolean isInt = false;
        if (v instanceof Number) { w = Py.num(v); isInt = Py.isInt(v); }
        else {
            String s = Py.sub("[,\\s원]", "", Py.str(v));
            if (Py.fullmatch("\\d+(\\.\\d+)?", s) == null) throw new InputError(Py.fmt("%s : 금액 「%s」 을 숫자(원)로 읽지 못했습니다", where, _txt(v, 30)));
            w = Double.parseDouble(asciiDigits(s));
        }
        if (w < 0 || w > 1e11) throw new InputError(Py.fmt("%s : 금액 %s 원이 범위를 벗어났습니다", where, _txt(v, 30)));
        return isInt ? Py.lng(v) : Py.round(w);
    }
    private static String asciiDigits(String s) {
        StringBuilder b = new StringBuilder(s.length());
        for (int i = 0; i < s.length(); i++) { char c = s.charAt(i); int d = Character.digit(c, 10); b.append(c != '.' && d >= 0 ? (char) ('0' + d) : c); }
        return b.toString();
    }
    private static final Map<String, String> SEX = new HashMap<>();
    static {
        SEX.put("M", "M"); SEX.put("F", "F"); SEX.put("남", "M"); SEX.put("여", "F"); SEX.put("남자", "M"); SEX.put("여자", "F"); SEX.put("1", "M"); SEX.put("2", "F");
    }

    /** 입력 JSON(글자 또는 이미 읽은 Map) → 점검한 Map. 사양과 다르면 InputError */
    public static Map<String, Object> parse(Object obj) {
        if (obj instanceof byte[]) obj = new String((byte[]) obj, java.nio.charset.StandardCharsets.UTF_8);
        if (obj instanceof String) {
            try { obj = Json.parse((String) obj); }
            catch (RuntimeException e) { throw new InputError(Py.fmt("JSON 으로 읽지 못했습니다 : %s", String.valueOf(e.getMessage()))); }
        }
        if (!(obj instanceof Map)) throw new InputError("맨 바깥은 { } 여야 합니다");
        Map<String, Object> o = Py.M(obj);
        Object sch = o.get("schema");
        if (sch != null && !Py.eq(sch, SCHEMA)) throw new InputError(Py.fmt("schema %s 는 지원하지 않습니다(지금 %d)", sch, SCHEMA));
        Object rs0 = o.get("riders");
        if (!(rs0 instanceof List) || ((List<?>) rs0).isEmpty()) throw new InputError("riders(담보 목록)가 비어 있습니다");
        List<Object> rs = Py.L(rs0);
        if (rs.size() > 2000) throw new InputError(Py.fmt("riders 가 %d개 — 한 설계의 담보로는 너무 많습니다", rs.size()));
        Object ins0 = Py.or(o.get("insured"), new LinkedHashMap<String, Object>()), ag0 = Py.or(o.get("agent"), new LinkedHashMap<String, Object>());
        if (!(ins0 instanceof Map) || !(ag0 instanceof Map)) throw new InputError("insured · agent 는 { } 여야 합니다");
        Map<String, Object> ins = Py.M(ins0), ag = Py.M(ag0);
        String sex = _txt(ins.get("sex"), 4).toUpperCase(java.util.Locale.ROOT);
        sex = SEX.getOrDefault(sex, "");
        String age = _txt(ins.get("age"), 6).replace("세", "");
        if (!age.isEmpty() && Py.fullmatch("\\d{1,3}", age) == null) throw new InputError(Py.fmt("insured.age 「%s」 는 숫자(보험나이)여야 합니다", age));
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("schema", SCHEMA);
        out.put("design_no", _txt(o.get("design_no"), 40));
        out.put("product", _txt(o.get("product"), 200));
        out.put("premium", _won(o.get("premium"), "premium"));
        out.put("insured", Py.dict("name", _txt(ins.get("name"), 30), "sex", sex, "age", age));
        out.put("agent", Py.dict("org", _txt(ag.get("org"), 40), "code", _txt(ag.get("code"), 20), "name", _txt(ag.get("name"), 20), "mobile", _txt(ag.get("mobile"), 20), "tel", _txt(ag.get("tel"), 20)));
        List<Object> outRs = new ArrayList<>();
        out.put("riders", outRs);
        if (((String) out.get("product")).isEmpty()) throw new InputError("product(상품명)가 없습니다 — 상품 라인을 정하는 데 씁니다");
        for (int i = 1; i <= rs.size(); i++) {
            Object r0 = rs.get(i - 1);
            if (!(r0 instanceof Map)) throw new InputError(Py.fmt("riders %d번째 : { } 여야 합니다", i));
            Map<String, Object> r = Py.M(r0);
            String nm = _txt(r.get("name"), 160);
            if (nm.isEmpty()) throw new InputError(Py.fmt("riders %d번째 : name(상품담보명)이 없습니다", i));
            Object no = Py.get(r, "no", (long) i);
            boolean isInt = Py.isInt(no);
            if (!isInt && Py.fullmatch("\\d{1,6}", Py.str(no)) == null) throw new InputError(Py.fmt("riders %d번째 : no 「%s」 는 숫자여야 합니다", i, _txt(no, 20)));
            long noL = isInt ? Py.lng(no) : Long.parseLong(asciiDigits(Py.str(no)));
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("no", noL);
            row.put("unit_code", _txt(r.get("unit_code"), 20));
            row.put("code", _txt(r.get("code"), 20));
            row.put("name", nm);
            row.put("amount", _won(r.get("amount"), Py.fmt("riders %d번째 amount", i)));
            row.put("unused_daily", _won(r.get("unused_daily"), Py.fmt("riders %d번째 unused_daily", i)));
            outRs.add(row);
        }
        return out;
    }

    // ── 상품 라인 ──
    /** 특약 마스터의 상품 라인 — 설계서 PDF 와 같은 규칙(BuildAll.line_from_head · 상품명 글자) */
    public static String line_of(Map<String, Object> p) {
        String ln = BuildAll.line_from_head(Py.sub("\\s+", "", (String) p.get("product")));
        if (ln != null && !ln.isEmpty()) return ln;
        for (Object r : Py.gl(p, "riders")) if (((String) Py.M(r).get("name")).contains("통합간편가입")) return "통합간편";
        return "케어프리";
    }

    // ── 담보 줄 ──
    /** 원 → 만원. 만원 단위면 Long(설계서 읽기와 같은 꼴), 아니면 Double */
    public static Object man_of(long won) { return Math.floorMod(won, 10000L) == 0 ? (Object) Math.floorDiv(won, 10000L) : (Object) (won / 10000.0); }
    /** 세부내역 「가입금액」 표기용 — 설계서 글자 꼴(1천만원 · 30만원). 계산에는 쓰지 않는다 */
    public static String won_text(long won) {
        Object m = man_of(won);
        if (!Py.truthy(m)) return won != 0 ? Py.fmt("%s원", Py.comma(won)) : "";
        if (m instanceof Double) return Py.fmt("%s만원", Py.rstrip(Py.rstrip(Py.fmt("%.1f", m), "0"), "."));
        long mm = (Long) m;
        long eok = Math.floorDiv(mm, 10000L), r = Math.floorMod(mm, 10000L);
        long cheon = Math.floorDiv(r, 1000L); r = Math.floorMod(r, 1000L);
        long baek = Math.floorDiv(r, 100L), man = Math.floorMod(r, 100L);
        String s = (eok != 0 ? Py.fmt("%d억", eok) : "") + (cheon != 0 ? Py.fmt("%d천", cheon) : "") + (baek != 0 ? Py.fmt("%d백", baek) : "") + (man != 0 ? Py.fmt("%d", man) : "");
        return s + ((cheon != 0 || baek != 0 || man != 0) ? "만원" : "원");
    }
    public static final Pattern G17 = Py.re("^(?P<pre>(?:\\(\\d+년갱신\\))?\\s*(?:갱신형\\s*)?)수술비\\s*(?:\\(1-7종[^\\[\\]]*\\))?\\s*\\[(?P<c>질병|상해)(?P<g>[1-7])종\\]\\s*(?:\\(출생전\\))?$");
    public static String _clean(String n) { return Py.strip(Py.sub(ScenEngine.GOJI, "", n).replace("[기본계약]", "")); }

    /** 설계서 읽기가 만드는 줄과 같은 꼴 + 어떻게 찾았는지(how) */
    public static Map<String, Object> _row(Object no, String name, long won, String line, String unit, String code, String text) {
        Object[] mt = Matcher_.match(name, line);
        Map<String, Object> m = Py.M(mt[0]);
        Object b = mt[1], s2 = mt[2];
        String how = Py.truthy(m) ? "name" : null;
        Map<String, Object> cm = (Py.truthy(unit) && Py.truthy(code)) ? Py.M(code_map().get(Py.fmt("%s|%s", unit, code))) : null;
        if (Py.truthy(cm)) {
            Map<String, Object> cr = master(cm.get("p"), cm.get("id"));
            if (Py.truthy(cr) && !Py.truthy(m)) { m = cr; how = "code"; }
            else if (Py.truthy(cr) && Py.truthy(m) && !(set(cr.get("k")).equals(set(m.get("k"))) && set(cr.get("x")).equals(set(m.get("x"))) && set(cr.get("hc")).equals(set(m.get("hc"))))) {
                ScenEngine.log("검토필요", name, Py.fmt("담보 식별표의 특약(%s · %s)과 이름으로 찾은 특약(%s · %s)의 약관 자료가 다름 — 이름으로 찾은 것으로 계산", cm.get("id"), cm.get("p"), m.get("id"), m.get("p")));
            }
        }
        boolean has = Py.truthy(m);
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("no", no);
        row.put("name", _clean(name));
        row.put("man", man_of(won));
        row.put("amount_text", text != null ? text : won_text(won));
        row.put("cat", has ? m.get("c") : null);
        row.put("codes", has ? Py.or(m.get("k"), new ArrayList<Object>()) : new ArrayList<Object>());
        row.put("excl", has ? Py.or(m.get("x"), new ArrayList<Object>()) : new ArrayList<Object>());
        row.put("hc", has ? Py.or(m.get("hc"), new ArrayList<Object>()) : new ArrayList<Object>());
        row.put("benefit", b);
        row.put("sub", s2);
        row.put("matched", has);
        row.put("itc", ScenEngine.itc_id(name));
        row.put("sub_rec", has && Py.gs0(m, "n").contains("["));
        row.put("mname", has ? m.get("n") : null);
        row.put("unit_code", unit);
        row.put("code", code);
        row.put("how", how);
        return row;
    }
    private static Set<Object> set(Object l) { return l == null ? new HashSet<>() : new HashSet<>(Py.L(l)); }

    /** 점검한 입력 → 담보 줄(설계서 읽기와 같은 꼴). p['_line'] 에 상품 라인을 적어 둔다 */
    public static List<Object> riders(Map<String, Object> p) { return riders(p, line_of(p)); }
    /** 상품 라인을 밖에서 정해 주는 꼴(정보계 전 줄 대조용 — 파이썬 audit_rows 가 line_of 를 바꿔 끼우는 것과 같다) */
    public static List<Object> riders(Map<String, Object> p, String line) {
        p.put("_line", line);
        List<Object> out = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        for (Object o : Py.gl(p, "riders")) {
            Map<String, Object> r = Py.M(o);
            String nm = (String) r.get("name");
            long won = Py.lng(r.get("amount"));
            String base = _clean(nm);
            if (Py.has(Matcher_.GRADE_RANGE, base.replace(" ", ""))) {
                ScenEngine.log("검토필요", nm, "종 범위 부모 줄 — 종별 세부 줄만 계산(이 줄은 건너뜀)"); continue;
            }
            String k = r.get("no") + "\u0000" + ScenEngine.nname(nm);
            if (seen.contains(k)) { ScenEngine.log("검토필요", nm, "같은 번호 · 같은 이름 담보가 두 번 들어옴 — 한 번만 계산"); continue; }
            seen.add(k);
            Matcher g = Py.match(G17, base);
            if (g != null) {
                if (won == 0) { ScenEngine.log("검토필요", nm, "가입금액이 0 — 계산하지 않음"); continue; }
                String pre = Py.strip(Py.sub("\\(\\d+년갱신\\)\\s*", "", g.group("pre")));
                pre = !pre.isEmpty() ? (pre + " ") : "";
                String pname = Py.fmt("%s수술비(1-7종, 연간3회한)[%s%s종]", pre, g.group("c"), Long.parseLong(g.group("g")) <= 3 ? "1-3" : "4-7");
                String child = Py.fmt("┗ %s수술비[%s%s종]", pre, g.group("c"), g.group("g"));
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("no", r.get("no")); row.put("name", child); row.put("man", man_of(won)); row.put("amount_text", won_text(won)); row.put("cat", null);
                row.put("codes", new ArrayList<Object>()); row.put("excl", new ArrayList<Object>()); row.put("hc", new ArrayList<Object>());
                row.put("benefit", Py.fmt("%s%s종", g.group("c"), g.group("g")));
                row.put("sub", null); row.put("matched", Boolean.FALSE); row.put("itc", ScenEngine.itc_id(child)); row.put("sub_rec", Boolean.FALSE); row.put("mname", null);
                row.put("unit_code", r.get("unit_code")); row.put("code", r.get("code")); row.put("how", null);
                row = Matcher_._link(row, Py.dict("name", pname, "m", Matcher_.parent_master(pname, line)), child);
                row.put("how", Py.truthy(row.get("matched")) ? "name" : null);
                out.add(row); continue;
            }
            if (base.contains("간병인지원") && !base.contains("사용추가보장")) {
                long ud = Py.lng(r.get("unused_daily")) != 0 ? Py.lng(r.get("unused_daily")) : won;
                out.add(_row(r.get("no"), nm, 0, line, (String) r.get("unit_code"), (String) r.get("code"), "간병인지원" + (ud != 0 ? (" 또는 " + won_text(ud)) : ""))); continue;
            }
            if (won == 0) { ScenEngine.log("검토필요", nm, "가입금액이 0 — 부모 줄(세부보장 참조)이거나 금액이 빠진 담보 · 계산하지 않음"); continue; }
            out.add(_row(r.get("no"), nm, won, line, (String) r.get("unit_code"), (String) r.get("code"), null));
        }
        if (out.isEmpty() || Py.lng(ScenEngine.recog(out).get("계산제외")) >= out.size()) {
            throw new Pipeline.DesignUnreadable(Py.fmt("담보 %d건을 받았지만 특약 마스터 · 규칙표에서 하나도 찾지 못했습니다(상품 : %s). 아직 등록하지 않은 상품 · 약관이거나 담보명이 정보계 원문과 다를 수 있습니다.", Py.gl(p, "riders").size(), p.get("product")));
        }
        return out;
    }

    // ── 표지 · 머리줄 ──
    private static String joinNonEmpty(Object... xs) {
        List<Object> a = new ArrayList<>();
        for (Object x : xs) if (Py.truthy(x)) a.add(x);
        return Py.join(" ", a);
    }
    /** build_all.auto_meta 와 같은 열쇠 */
    public static Map<String, Object> meta(Map<String, Object> p) {
        Map<String, Object> ins = Py.gm(p, "insured"), ag = Py.gm(p, "agent");
        long prem = Py.lng(p.get("premium"));
        return Py.dict("insured", Py.truthy(ins.get("name")) ? ins.get("name") : "고객", "premium", prem != 0 ? (Py.comma(prem) + "원") : "", "product", p.get("product"),
                "head", "", "agent", joinNonEmpty(ag.get("org"), ag.get("name")), "issued", "", "sex", ins.get("sex"));
    }
    /** ga_proposal.ga_head 와 같은 열쇠 — 넘겨받은 글자 그대로(없으면 빈칸 + 로그) */
    public static Map<String, Object> head(Map<String, Object> p) { return head(p, ""); }
    public static Map<String, Object> head(Map<String, Object> p, String age) {
        Map<String, Object> ins = Py.gm(p, "insured"), ag = Py.gm(p, "agent");
        String a = Py.truthy(age) ? age : (String) ins.get("age");
        if (Py.truthy(a) && !a.endsWith("세")) a += "세";
        String sx = "F".equals(ins.get("sex")) ? "여자" : ("M".equals(ins.get("sex")) ? "남자" : "");
        Map<String, Object> h = Py.dict("name", ins.get("name"), "sex", sx, "age", a, "no", p.get("design_no"), "agent", joinNonEmpty(ag.get("org"), ag.get("name")),
                "org", ag.get("org"), "agent_name", ag.get("name"), "mobile", ag.get("mobile"), "tel", ag.get("tel"), "code", ag.get("code"));
        List<Object> missing = new ArrayList<>();
        String[][] chk = {{"피보험자 이름", "name"}, {"성별", "sex"}, {"보험나이", "age"}, {"가계약번호", "no"}, {"컨설턴트 소속", "org"}, {"컨설턴트 이름", "agent_name"}};
        for (String[] c : chk) if (!Py.truthy(h.get(c[1]))) missing.add(c[0]);
        if (!missing.isEmpty()) ScenEngine.ISSUES.add(Py.dict("구분", "표지", "담보", "-", "사유", "입력에 없는 표지 항목 : " + Py.join(" · ", missing) + " (빈칸 「-」으로 둠)"));
        return h;
    }
    /** 산출물 파일 이름용(ASCII) */
    public static String tag(Map<String, Object> p) {
        String a = Py.sub("[^A-Za-z0-9_-]+", "", Py.truthy(p.get("design_no")) ? (String) p.get("design_no") : "");
        return "code_" + (!a.isEmpty() ? Py.tail(a, 24) : new java.text.SimpleDateFormat("yyyyMMdd_HHmmss").format(new java.util.Date()));
    }
    public static String label(Map<String, Object> p) {
        return Py.fmt("담보코드 입력 · 가계약번호 %s · 담보 %d건", Py.truthy(p.get("design_no")) ? p.get("design_no") : "-", Py.gl(p, "riders").size());
    }
}
