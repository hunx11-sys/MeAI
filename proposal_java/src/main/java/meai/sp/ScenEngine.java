package meai.sp;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 설계 담보 전체(진단비·수술비·입원일당·치료비·통합치료비)에 대한 사례별 보상 계산 엔진 — 파이썬 scen_engine.py(다른 모듈이 `S` 로 부른다)를 그대로 옮긴 것.
 *
 *  ▣ 판정 근거는 두 가지뿐이다. ① 담보명 : rules.json 규칙표 + 담보명 토큰 ② 약관 KCD : 특약 마스터의 KCD 목록 · 그룹표 · 암분류(Engine.cancer_cls)
 *     ※ KCD 목록은 어떤 경우에도 코드에서 생성·추정하지 않는다.
 *  ▣ 규칙표에 없는 담보가 들어와도 예외를 던지지 않는다. 계산에서 제외하고 ISSUES 에 사유를 남긴다.
 *
 * 모듈 전역 상태(ISSUES · 캐시)는 static 이다 — 파이썬 판과 같이 한 프로세스에서 한 번에 한 건씩 계산한다.
 */
public final class ScenEngine {
    private ScenEngine() {}

    public static final String BASE = Py.BASE;

    // ══ 가입금액 표기 → 만원 ═══════════════════════════════════════════
    public static final String AMT_RE = "간병인지원"
            + "|(?=\\d)(?:\\d[\\d,]*억\\s*)?(?:\\d[\\d,]*천)?(?:\\d[\\d,]*백)?(?:\\d[\\d,]*십)?(?:\\d[\\d,]*)?만원"
            + "|\\d[\\d,]*억\\s*(?:\\d[\\d,]*천)?(?:\\d[\\d,]*백)?(?:\\d[\\d,]*십)?(?:\\d[\\d,]*만)?원?";
    public static final Pattern _AMT_FULL = Py.re("(?:(\\d+)억)?(?:(\\d+)천)?(?:(\\d+)백)?(?:(\\d+)십)?(\\d+)?(만)?원?");

    /** '1억5천만원' → 15000. 해석 불가·원 단위(5,000원)·현물(간병인지원)은 0. */
    public static long amt_to_man(String s) {
        s = Py.sub("[\\s,]", "", s == null ? "" : s);
        Matcher m = Py.fullmatch(_AMT_FULL, s);
        if (m == null) return 0;
        boolean any = false;
        long[] v = new long[5];
        for (int i = 0; i < 5; i++) {
            String g = m.group(i + 1);
            if (Py.truthy(g)) { any = true; v[i] = Long.parseLong(g); }
        }
        if (!any) return 0;
        if (!(v[0] != 0 || v[1] != 0 || v[2] != 0 || v[3] != 0 || Py.truthy(m.group(6)))) return 0;      // '5000원' 같은 원 단위 → 만원 미만 취급
        return v[0] * 10000 + v[1] * 1000 + v[2] * 100 + v[3] * 10 + v[4];
    }

    // ══ 규칙표 ══════════════════════════════════════════════════════════
    public static final Map<String, Object> RULEDOC = Py.M(Py.loadJson("rules.json"));
    public static final List<Object> RULES = Py.gl(RULEDOC, "rules");
    public static final Map<String, Object> KCDG = Py.gm(RULEDOC, "kcd_groups");
    public static final List<Object> FIVE_MAJOR = Py.L(KCDG.get("특정5대질병"));

    public static final Map<String, Object> G131 = Py.M(Py.loadJson("g131.json"));
    public static final Map<String, Object> SYN = Py.gm(Py.gm(Engine.D, "EMB"), "syn");     // 암종명 → KCD
    public static final Map<String, Object> G131X = new LinkedHashMap<>();                  // 그룹 라벨 → 그 별표의 제외코드
    private static final Map<String, Object> _DBJSON = Py.exists(Py.path("db.json")) ? Py.M(Py.loadJson("db.json")) : null;

    public static void _g131_from_master() {
        if (_DBJSON == null) return;
        Set<String> have = new HashSet<>();
        for (String k : G131.keySet()) have.add(Py.sub("[\\s․·,]", "", k));
        for (Object ro : Py.gl0(_DBJSON, "riders")) {
            Map<String, Object> r = Py.M(ro);
            Matcher m = Py.search("\\[([^\\[\\]]+)\\]$", Py.gs0(r, "n"));
            if (m != null && Py.match("^(갱신형)?13[01]대질병수술비", Py.gs(r, "n").replace(" ", "")) != null && Py.truthy(r.get("k"))) {
                String lab = Py.sub("[\\s․·,]", "", m.group(1));
                if (!have.contains(lab)) {
                    G131.put(lab, new ArrayList<>(Py.gl(r, "k"))); have.add(lab);
                    if (Py.truthy(r.get("x"))) G131X.put(lab, new ArrayList<>(Py.gl(r, "x")));
                }
            }
        }
    }

    // ══ 1-7종 수술분류표 — 수술코드 → 종 ═══════════
    public static final Map<String, Object> SURG7 = new LinkedHashMap<>();
    // ══ 신수술분류표 — 신수술비[기본]·[주요수술] 판정 ══
    public static Map<String, Object> NEWSURG = Py.dict("basic", new ArrayList<Object>(), "major", new LinkedHashMap<String, Object>());
    public static final Set<Object> _NEWSURG_BASIC = new HashSet<>();
    public static final String[][] NEWSURG_TYPE_KEY = {{"장기이식", "장기이식"}, {"개두", "개두및두부"}, {"개흉", "개흉"}, {"개복", "개복"}, {"각막", "각막조직피부이식및조직재건"}, {"경피적", "경피적"}};

    /** 사례의 1-7종 표기 : 정수(종) 그대로, 수술코드('F121' 등)는 분류표에서 종을 찾는다. 모르면 null. */
    public static Object surg7_grade(Object x) {
        if (x == null || Py.isInt(x) || x instanceof Boolean) return x;
        Object r = SURG7.get(Py.str(x).toUpperCase());
        return Py.truthy(r) ? Py.get(r, "grade") : null;
    }
    public static String surg7_name(Object x) {
        Object r = (x instanceof String) ? SURG7.get(Py.str(x).toUpperCase()) : null;
        return Py.truthy(r) ? Py.gs(r, "name") : "";
    }
    /** 수술코드 → 분류표의 수술구분 이름(예 B016 → '뇌동맥류수술'). 모르면 ''. */
    public static String surg7_group(Object x) {
        Object r = (x instanceof String) ? SURG7.get(Py.str(x).toUpperCase()) : null;
        return Py.truthy(r) ? (String) Py.or(Py.get(r, "group"), "") : "";
    }

    // ══ 1-5종 수술분류표Ⅱ — 항목번호 → 종, 질병코드 예외 ═══
    public static final Map<Object, Object> SURG5 = new LinkedHashMap<>();
    /** 사례의 1-5종 표기 : 정수(종) 그대로, 항목번호('33'·'88-1'·'C1' 등)는 분류표에서 종을 찾고 '단, ○○(KCD)로 인한 수술은 N종' 예외를 질병코드로 적용한다. */
    public static Object surg5_grade(Object x) { return surg5_grade(x, null); }
    public static Object surg5_grade(Object x, String kcd) {
        if (x == null || Py.isInt(x) || x instanceof Boolean) return x;
        Object it = SURG5.get(Py.str(x));
        if (!Py.truthy(it)) return null;
        for (Object eo : Py.gl0(it, "exceptions")) {
            String ek = Py.gs(eo, "kcd");
            if (Py.truthy(kcd) && (kcd.equals(ek) || kcd.startsWith(ek))) return Py.get(eo, "grade");
        }
        return Py.get(it, "grade");
    }
    public static String surg5_name(Object x) {
        Object it = (x instanceof String) ? SURG5.get(Py.str(x)) : null;
        return Py.truthy(it) ? Py.gs(it, "name") : "";
    }
    /** 사례 수술이 관혈(TRUE)인지 비관혈(FALSE)인지 — 모르면 null */
    public static Boolean surg_open(Map<String, Object> tg) {
        if (tg.containsKey("open")) return Py.truthy(tg.get("open"));
        Object j = tg.get("surg");
        if (!(j instanceof String) || !SURG5.containsKey(j)) return null;
        String js = (String) j;
        if (js.startsWith("88") || js.equals("C2")) return Boolean.FALSE;
        String nm = Py.gs(SURG5.get(js), "name");
        if (js.startsWith("C1") || nm.contains("관혈") || nm.contains("개흉") || nm.contains("개복") || nm.contains("개두")) return Boolean.TRUE;
        return null;
    }

    // 고지유형 꼬리표 — rules.json goji_tags 한 곳에서만 관리. matcher 도 이 GOJI 를 가져다 쓴다.
    public static final String GOJI;
    // 인수 · 전환 표시 — [특별조건부] · [계약전환용] · (출생전) 은 같은 특약이다
    public static final Pattern VARTAG = Py.re("\\[(?:특별조건부|계약전환용)\\]|\\(출생전\\)");
    /** 고지유형 꼬리표·인수 표시·공백 제거 — 규칙표 매칭에 쓰는 정규화 담보명 */
    public static String nname(String n) {
        return Py.sub("\\s+", "", Py.sub(VARTAG, "", Py.sub(GOJI, "", n == null ? "" : n)).replace("[기본계약]", "").replace("┗", ""));
    }

    // ══ 통합치료비 식별 ═══════════
    public static final Map<String, Object> ITC_MAP = new LinkedHashMap<>();
    public static final Map<String, Object> _ITC_NORM = new LinkedHashMap<>();
    /** 설계서의 '갱신형' 접두어를 뗀 이름 — 약관 지급금액표는 갱신 여부를 구분하지 않는다 */
    public static String noren(String n) { return Py.sub("^갱신형", "", nname(n)); }
    /** 약관 지급금액표가 있는 통합치료비면 그 id, 아니면 null. 「부모[세부보장]」 꼴은 세부보장 이름으로 본다 */
    public static String itc_id(String name) {
        Object hit = Py.or(_ITC_NORM.get(nname(name)), _ITC_NORM.get(noren(name)));
        if (Py.truthy(hit)) return (String) hit;
        Matcher m = Py.fullmatch("(.+?)\\[(.+)\\]", Py.strip(Py.sub(GOJI, "", name == null ? "" : name)));        // 고지 꼬리표는 떼고 본다
        if (m != null) return (String) Py.or(_ITC_NORM.get(nname(m.group(2))), _ITC_NORM.get(noren(m.group(2))));
        return null;
    }

    // ══ 통합생활지원비 식별 ════════════════════════════════════════════════
    public static Map<String, Object> LS = new LinkedHashMap<>();
    public static final String[][] _LS_PAT = {{"two_ls", "2대질환"}, {"inj_ls", "상해"}, {"dz_ls", "질병"}, {"ca_ls", "암"}};
    /** 통합생활지원비면 그 id(ca_ls·two_ls·dz_ls·inj_ls), 아니면 null */
    public static String ls_id(String name) {
        String nm = noren(name);
        if (!nm.contains("통합생활지원비")) return null;
        String head = Py.split(nm, "통합생활지원비").get(0);
        for (String[] p : _LS_PAT) if (head.contains(p[1]) && LS.containsKey(p[0])) return p[0];
        return null;
    }
    /** 가입금액(월간 총 지급금액) → 약관 항목표. 구간이 없으면 null — 금액을 추정하지 않는다. */
    public static Object ls_tier(String rid, Object man) {
        Object t = Py.or(Py.get(Py.or(LS.get(rid), new LinkedHashMap<String, Object>()), "tiers"), new LinkedHashMap<String, Object>());
        return Py.or(Py.get(t, Py.str(Py.toInt(man))), Py.get(t, Py.str(man)));
    }

    public static final Set<String> INJ_KNOWN = new LinkedHashSet<>();                      // 상해 통합치료비 : inj_itc.json 으로 별도 계산

    // 담보 → 항목표. ① 설계서 설명문 항목표 ② 약관 지급금액표(life_support.json — 서로 다른 상품 약관에서 같은 표임을 대조한 것만)
    public static final Map<String, Object[]> _LS_ITEMS = new HashMap<>();
    private static String _numKey(Object v) {
        if (v == null) return "None";
        if (v instanceof Number) { double d = ((Number) v).doubleValue(); return (d == Math.rint(d) && !Double.isInfinite(d)) ? Long.toString((long) d) : Py.repr(d); }
        return Py.reprObj(v);
    }
    /** 담보 → {항목표(List), 근거(String)} · 근거는 'paper'(상품설명서) · 'book'(약관) · null(없음). 기억 열쇠는 담보의 내용(이름 · 가입금액 · 설명문). 로그는 기억에서 꺼낼 때도 다시 남긴다 */
    public static Object[] ls_items(Map<String, Object> r) {
        String key = Py.reprObj(r.get("name")) + "\u0001" + _numKey(r.get("man")) + "\u0001" + Py.or(r.get("desc"), "");
        if (_LS_ITEMS.containsKey(key)) {
            Object[] c = _LS_ITEMS.get(key);
            for (Object a : (List<?>) c[1]) { String[] t = (String[]) a; log(t[0], t[1], t[2]); }
            return (Object[]) c[0];
        }
        List<Object> logs = new ArrayList<>();
        final String rname = (String) Py.at(r, "name");
        String rid = ls_id(rname);
        Object[] res = new Object[]{new ArrayList<Object>(), null};
        if (Py.truthy(rid)) {
            Object v = Py.or(LS.get(rid), new LinkedHashMap<String, Object>());
            Object book = ls_tier(rid, Py.at(r, "man"));
            List<Object> paper;
            try { paper = DescEngine.life_items((String) Py.or(r.get("desc"), "")); }
            catch (RuntimeException ex) { paper = new ArrayList<>(); }
            if (Py.truthy(paper) && Py.truthy(book)) {
                if (!Py.eq(_ls_k(paper), _ls_k(Py.L(book)))) {
                    String reason = "상품설명서 설명문과 약관 지급금액표의 항목·금액이 달라 설명문 기준으로 표시함";
                    logs.add(new String[]{"교차대조", rname, reason}); log("교차대조", rname, reason);
                }
            }
            if (Py.truthy(paper)) res = new Object[]{paper, "paper"};
            else if (Py.truthy(book) && Py.len(Py.or(Py.get(v, "srcs"), new ArrayList<Object>())) >= 2) res = new Object[]{book, "book"};
            else if (Py.truthy(book)) {
                String reason = "이 상품 약관·설명문에서 항목표를 확인하지 못해 계산·지면에서 제외 (다른 상품 약관 1곳에만 있어 대조 불가)";
                logs.add(new String[]{"근거부족", rname, reason}); log("근거부족", rname, reason);
            } else {
                String reason = Py.fmt("가입금액 %g만원 구간의 항목표가 설명문에도 약관에도 없어 계산·지면에서 제외", Py.at(r, "man"));
                logs.add(new String[]{"금액표없음", rname, reason}); log("금액표없음", rname, reason);
            }
        }
        _LS_ITEMS.put(key, new Object[]{res, logs});
        return res;
    }
    private static List<Object> _ls_k(List<Object> xs) {
        List<Object> t = new ArrayList<>();
        for (Object x : xs) t.add(Py.list(Py.sub("\\s", "", Py.gs(x, "label")), Py.get(x, "amt")));
        return Py.sorted(t);
    }

    // 유사암 = 제자리암(cis) · 경계성종양(bord) · 기타피부암(skin) · 갑상선암(thy) — 약관 별표87-2 그대로.
    public static final List<String> SIM_CLS = java.util.Collections.unmodifiableList(java.util.Arrays.asList("cis", "bord", "thy", "skin"));   // contains(null) 이 되는 목록

    /** 담보명이나 세부급부 라벨이 암 구분을 못박았으면 사례의 암 구분이 그에 맞는지. '…포함' 은 범위를 넓히는 말이라 좁히지 않는다. */
    public static boolean cancer_scope_ok(String text, String kcd) {
        String t = Py.sub("[\\s․·,]", "", text == null ? "" : text);
        if (t.isEmpty() || t.contains("포함")) return true;
        String dc = Engine.cancer_cls(kcd);
        if (dc == null) return true;
        if (Py.has("유사암[^)]{0,8}제외", t)) return dc.equals("major");
        boolean thy = t.contains("갑상선암"), skin = t.contains("기타피부암");
        if (thy && skin) return dc.equals("thy") || dc.equals("skin");
        if (thy) return dc.equals("thy");
        if (skin) return dc.equals("skin");
        if (t.contains("유사암")) return SIM_CLS.contains(dc);
        return true;
    }

    /** 산정특례대상 진단비 — 「산정특례대상으로 등록된 경우」가 지급사유다. 반환 {지급 가능 여부(Boolean), 진단 태그} */
    public static Object[] special_reg(Map<String, Object> r, Map<String, Object> sc, String nm, Object dx) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        if (Py.has("중복암|재등록암", nm)) {
            log("조건부", Py.gs(r, "name"), "암 산정특례 재등록(중복암 · 5년 뒤 재등록) 조건 — 사례로 단정할 수 없어 계산 제외"); return new Object[]{false, dx};
        }
        if (Py.has("\\(암|유사암|뇌·수막|뇌수막", nm)) return new Object[]{true, dx};
        if (Py.has("뇌혈관|심장", nm)) {
            Set<Object> acts = _acts(sc, true);
            if (!(Py.truthy(tg.get("surg")) || acts.contains("surg") || acts.contains("thromb"))) return new Object[]{false, dx};
            Object ser = Py.or(tg.get("series"), ""); Object grp = Py.or(tg.get("grp"), new ArrayList<Object>());
            if (nm.contains("뇌혈관") && ("brain".equals(dx) || "brain".equals(ser) || _in(grp, "뇌혈관질환"))) return new Object[]{true, "brain"};
            if (nm.contains("심장") && ("heart".equals(dx) || "heart".equals(ser) || _in(grp, "심장질환"))) return new Object[]{true, "heart"};
            return new Object[]{false, dx};
        }
        log("조건부", Py.gs(r, "name"), "산정특례 등록 조건(중증화상·중증외상·희귀·중증난치·결핵 등)은 사례로 단정할 수 없어 계산 제외"); return new Object[]{false, dx};
    }
    /** x in c — c 가 목록이면 원소, 문자열이면 부분 문자열(파이썬 in) */
    private static boolean _in(Object c, String x) {
        if (c instanceof String) return ((String) c).contains(x);
        if (c instanceof Collection) return ((Collection<?>) c).contains(x);
        if (c instanceof Map) return ((Map<?, ?>) c).containsKey(x);
        return false;
    }

    // 통합치료비·통합생활지원비의 항목 한정 면책 — 「종합병원 전신마취치료」항목에만 적용되는 질병 목록(규칙표 kcd_groups)
    public static final String ANES_X_GROUP = "전신마취치료 항목면책(질병 통합치료비·질병 통합생활지원비)";
    public static final Map<String, Object> ITC_ITEM_X = Py.dict("dz", Py.dict("anes6", ANES_X_GROUP), "pre", Py.dict("anes6", "전신마취치료 항목면책(암전후관련 통합치료비)"));

    public static Set<Object> _ls_evkeys(Map<String, Object> sc) {
        Set<Object> ks = new HashSet<>();
        for (Object evo : Py.gl0(sc, "itc_events")) {
            List<Object> ev = Py.L(evo);
            if (ev.size() > 3) ks.addAll(Py.L(Py.or(ev.get(3), new ArrayList<Object>())));
        }
        return ks;
    }

    /** 이 사례 단계에서 통합생활지원비가 얼마 나오는지 → {[{항목명, 금액, 구분}] (List&lt;Object[]&gt;), 한도 적용 여부(Boolean)} · 합계는 월간 한도(가입금액)까지 */
    public static Object[] ls_lines(Map<String, Object> r, Map<String, Object> sc) {
        Object[] li = ls_items(r);
        List<Object> items = Py.L(li[0]);
        if (!Py.truthy(items)) return new Object[]{new ArrayList<Object[]>(), false};
        Map<String, Object> tg = Py.M(Py.or(sc.get("tags"), new LinkedHashMap<String, Object>()));
        String rid = ls_id(Py.gs(r, "name"));
        // 원인 조건 — 상해 통합생활지원비는 상해 치료만, 질병·암은 대상상병 치료만. 2대질환은 원인을 가리지 않는다.
        if ("inj_ls".equals(rid) && !"상해".equals(tg.get("cause"))) return new Object[]{new ArrayList<Object[]>(), false};
        boolean inj_case = "상해".equals(tg.get("cause"));
        Set<Object> ks = _ls_evkeys(sc);
        String code = (String) Py.or(sc.get("kcd"), "");
        String dc = Engine.cancer_cls(code);
        Object dx = Py.or(tg.get("dx"), "");
        Object grp = Py.or(tg.get("grp"), new ArrayList<Object>());
        Object ser = Py.or(tg.get("series"), "");
        boolean brain = "brain".equals(dx) || "brain".equals(ser) || _in(grp, "뇌혈관질환");
        boolean heart = "heart".equals(dx) || "heart".equals(ser) || _in(grp, "심장질환");
        // 입원·재활처럼 진단 태그가 없는 단계도 사례 질병코드가 약관 산정특례 목록에 들면 그 계열로 본다
        brain = brain || code_hit(Py.L(Py.or(KCDG.get("중증질환자(뇌혈관질환) 산정특례대상"), new ArrayList<Object>())), code);
        heart = heart || code_hit(Py.L(Py.or(KCDG.get("중증질환자(심장질환) 산정특례대상"), new ArrayList<Object>())), code);
        boolean anes = Py.truthy(tg.get("anes"));                          // 전신마취 수술인지는 사례에 명시된 것만 본다
        Object anes_h = Py.or(tg.get("anes_h"), 0L);                       // 마취시간(시간 · 사례의 가정값)
        boolean surgstep = Py.truthy(tg.get("surg")) || ks.contains("surg");
        boolean icu = Py.truthy(tg.get("icu")) || ks.contains("icu");
        boolean chemo = Py.truthy(tg.get("chemo")) || ks.contains("chemo");
        boolean rad = Py.truthy(tg.get("rad")) || ks.contains("rad");
        boolean thromb = ks.contains("thromb");
        boolean rehab = ks.contains("rehab");
        boolean regstep = surgstep || thromb;                              // 뇌·심장 산정특례 등록 사유(수술 또는 혈전용해)
        List<Object[]> got = new ArrayList<>();
        for (Object ito : items) {
            Map<String, Object> it = Py.M(ito);
            String lb = Py.sub("\\s", "", Py.gs(it, "label"));
            Object amt = Py.at(it, "amt");
            if (Py.cmp(amt, 0L) <= 0) continue;
            String ig = Py.gs(it, "grp");
            if (inj_case && ("dz_ls".equals(rid) || "ca_ls".equals(rid)) && !"산정특례".equals(ig)) continue;
            if (!"산정특례".equals(ig)) {
                if ("two_ls".equals(rid) && !(brain || heart)) continue;
                if ("ca_ls".equals(rid) && dc == null) continue;
            }
            boolean hit = false;
            if ("산정특례".equals(ig)) {
                if (lb.contains("유사암") && !lb.contains("제외")) hit = Py.truthy(dx) && SIM_CLS.contains(dc);
                else if (lb.contains("암(") || lb.startsWith("중증질환자(암")) hit = Py.truthy(dx) && "major".equals(dc);
                else if (lb.contains("뇌·수막") || lb.contains("뇌·수막의양성신생물")) hit = Py.truthy(dx) && Py.match("^D3[23]", code) != null;
                else if (lb.contains("뇌혈관")) hit = brain && regstep;
                else if (lb.contains("심장")) hit = heart && regstep;
                else hit = false;                                          // 희귀·중증난치·중증화상·중증외상 — 사례로 단정하지 않는다
            } else if (lb.contains("전신마취")) {
                hit = anes && hosp_ok("종합", tg.get("hosp"));
                if (lb.contains("6시간이상")) hit = hit && Py.cmp(anes_h, 6L) >= 0;
                else if (lb.contains("4시간이상")) hit = hit && Py.cmp(anes_h, 4L) >= 0;
                if ("ca_ls".equals(rid)) hit = hit && _ls_cancer_row(lb, dc);
                else if ("dz_ls".equals(rid) && hit && code_hit(Py.L(Py.or(KCDG.get(ANES_X_GROUP), new ArrayList<Object>())), code)) {
                    hit = false; log("면책", Py.gs(r, "name"), Py.fmt("%s — 약관 제17조② 항목 한정 면책 질병(%s)이라 전신마취 항목 제외", it.get("label"), code));
                }
            } else if (lb.contains("중환자실")) {
                hit = icu;
            } else if (lb.contains("항암방사선")) {
                hit = rad && _ls_cancer_row(lb, dc);
            } else if (lb.contains("항암약물")) {
                hit = chemo && _ls_cancer_row(lb, dc);
            } else if (lb.contains("혈전용해")) {
                hit = thromb;
            } else if (lb.contains("재활")) {
                hit = rehab && lb.contains("전문재활") && !lb.contains("전문외") && !lb.contains("외래");
            }
            if (hit) got.add(new Object[]{it.get("label"), amt, ig});
        }
        List<Object> as = new ArrayList<>();
        for (Object[] g : got) as.add(g[1]);
        Object tot = Py.sum(as);
        if (Py.cmp(tot, Py.at(r, "man")) <= 0) return new Object[]{got, false};
        // 월간 총 지급금액 한도 — 한 달에 받는 합계는 가입금액까지
        List<Object[]> out = new ArrayList<>();
        Object left = Py.at(r, "man");
        for (Object[] g : Py.sorted(got, x -> Py.sub(0L, x[1]))) {
            if (Py.cmp(left, 0L) <= 0) break;
            Object take = Py.min2(g[1], left);
            out.add(new Object[]{g[0], take, g[2]}); left = Py.sub(left, take);
        }
        return new Object[]{out, true};
    }

    /** '암(유사암제외) 항암…' / '유사암 항암…' 행 가리기 */
    public static boolean _ls_cancer_row(String lb, String dc) {
        if (lb.startsWith("유사암")) return SIM_CLS.contains(dc);
        if (lb.contains("암(유사암제외)")) return "major".equals(dc);
        return dc != null;
    }

    public static final List<Object> ISSUES = new ArrayList<>();                             // 미분류·검토필요 로그(운영 점검용)
    public static void log(String kind, String name, String reason) {
        for (int i = ISSUES.size() - 1; i >= 0; i--) {                                        // if it not in ISSUES — 같은 로그는 한 번만
            Map<String, Object> e = Py.M(ISSUES.get(i));
            if (java.util.Objects.equals(e.get("사유"), reason) && java.util.Objects.equals(e.get("담보"), name) && java.util.Objects.equals(e.get("구분"), kind) && e.size() == 3) return;
        }
        ISSUES.add(Py.dict("구분", kind, "담보", name, "사유", reason));
    }

    // 특약 마스터(db.json)가 담고 있는 상품 — 로그 문구에 '어느 약관 데이터에 없는지'를 적기 위해 읽는다
    public static final List<Object> DB_PRODUCTS = _DBJSON != null ? Py.L(Py.or(Py.get(Py.or(_DBJSON.get("meta"), new LinkedHashMap<String, Object>()), "products"), new ArrayList<Object>())) : new ArrayList<>();

    // 약관이 질병코드 별표 대신 정의 조문으로 정해 목록이 원래 없는 세부보장 — 「마스터 보강 필요」 가 아니다
    public static final Map<String, Object> NO_KCD_BY_TERMS = Py.dict(
            "중증화상및부식", "약관이 체표면적 기준(신체표면적 20% 이상 3도 화상 · 부식, 제6조)으로 정하여 기준에서 제외함 — 질병코드 목록 없음");

    /** 'KCD 목록이 없다'는 로그를 두 경우로 가른다 — 담보 자체가 마스터에 없다(matched False) / 마스터에는 있는데 목록만 비어 있다 */
    public static String no_master_why(Map<String, Object> r, String what) {
        if (Boolean.FALSE.equals(r.get("matched"))) {
            return Py.fmt("이 담보는 특약 마스터(약관 데이터 : %s)에 없다 — 설계 상품의 약관이 데이터에 없어 %s을 붙일 수 없으므로 지급 판정 제외. "
                    + "다른 상품의 같은 이름 담보로 대신 계산하지 않음(약관 데이터 추가 전까지 빈칸)", Py.orS(Py.join("·", DB_PRODUCTS), "db.json"), what);
        }
        String nm = Py.sub("\\s", "", Py.gs0(r, "name"));
        for (Map.Entry<String, Object> e : NO_KCD_BY_TERMS.entrySet()) if (nm.contains(e.getKey())) return (String) e.getValue();
        return Py.fmt("특약 마스터에 %s이 없어 지급 판정 제외 (마스터 보강 필요)", what);
    }

    /** 같은 구분·사유의 로그를 담보 그룹 1줄로 묶는다. 담보명은 '담보목록'에 모두 남긴다. */
    public static List<Object> issues_grouped() { return issues_grouped(null); }
    public static List<Object> issues_grouped(List<Object> items) {
        List<Object> out = new ArrayList<>();
        Map<String, Integer> idx = new HashMap<>();
        for (Object ito : (items == null ? ISSUES : items)) {
            Map<String, Object> it = Py.M(ito);
            String key = Py.reprObj(it.get("구분")) + "\u0001" + Py.reprObj(it.get("사유"));
            if (idx.containsKey(key)) {
                Map<String, Object> g = Py.M(out.get(idx.get(key)));
                List<Object> lst = Py.gl(g, "담보목록");
                if (!lst.contains(it.get("담보"))) lst.add(it.get("담보"));
                g.put("담보", lst.size() > 1 ? Py.fmt("%s 외 %d건", lst.get(0), (long) (lst.size() - 1)) : lst.get(0));
            } else {
                idx.put(key, out.size());
                Map<String, Object> g = new LinkedHashMap<>(it);
                g.put("담보목록", Py.list(it.get("담보")));
                out.add(g);
            }
        }
        return out;
    }

    /** 담보 인식 상태 집계 — 「마스터」 · 「부모연결」 · 「규칙만」 · 「계산제외」. 넷의 합 = 담보 수. */
    public static Map<String, Object> recog(List<Object> riders) {
        Map<String, Object> c = Py.dict("마스터", 0L, "부모연결", 0L, "규칙만", 0L, "계산제외", 0L, "규칙만목록", new ArrayList<Object>(), "계산제외목록", new ArrayList<Object>());
        for (Object ro : riders) {
            Map<String, Object> r = Py.M(ro);
            if (Py.truthy(r.get("matched"))) {
                String k = Py.truthy(r.get("via")) ? "부모연결" : "마스터";
                c.put(k, Py.lng(c.get(k)) + 1); continue;
            }
            if (Py.truthy(r.get("itc")) || Py.truthy(ls_id((String) Py.at(r, "name")))) {             // 통합치료비·생활지원비는 금액표 엔진이 계산
                c.put("규칙만", Py.lng(c.get("규칙만")) + 1); Py.gl(c, "규칙만목록").add(r.get("name")); continue;
            }
            Map<String, Object> rule = classify(Py.gs(r, "name"));
            Map<String, Object> o = Py.M(Py.or(Py.get(Py.or(rule, new LinkedHashMap<String, Object>()), "opt"), new LinkedHashMap<String, Object>()));
            boolean calc = rule != null && HANDLER.containsKey(rule.get("kind"))
                    && !(("codes".equals(o.get("kcd")) || "codes_listed".equals(o.get("kcd"))) && !Py.truthy(r.get("codes")));
            if (calc) { c.put("규칙만", Py.lng(c.get("규칙만")) + 1); Py.gl(c, "규칙만목록").add(r.get("name")); }
            else { c.put("계산제외", Py.lng(c.get("계산제외")) + 1); Py.gl(c, "계산제외목록").add(r.get("name")); }
        }
        return c;
    }

    public static final Map<String, Map<String, Object>> _CC = new HashMap<>();
    public static final Pattern _XSUB = Py.re("\\[[^\\]]*(진단비|치료비|수술비|입원일당|통원일당)[^\\]]*\\]");
    public static final Pattern _SUBN = Py.re("\\[([^\\[\\]]+)\\]\\]*$");   // 겹대괄호의 안쪽 세부보장도 읽는다

    public static Map<String, Object> _rule_for(String nm) {
        for (Object ro : RULES) {
            Map<String, Object> r = Py.M(ro);
            if (!((Pattern) r.get("_m")).matcher(nm).find()) continue;
            Pattern x = (Pattern) r.get("_x");
            if (x != null && x.matcher(nm).find()) continue;
            // 부모 담보명에 '사망·후유장해'가 섞여 있어도 세부급부가 진단비·치료비 등 계산 대상이면 사망·후유장해 규칙을 건너뛴다
            if ("life".equals(r.get("kind")) && _XSUB.matcher(nm).find()) continue;
            return r;
        }
        return null;
    }

    /** 담보명 → 규칙(rules.json 의 한 줄 · `_m` `_x` 는 컴파일한 패턴). 없으면 null. 세부급부가 있는 담보(부모[세부])는 세부급부가 보상 유형을 정한다 */
    public static Map<String, Object> classify(String name) {
        String nm = nname(name);
        if (_CC.containsKey(nm)) return _CC.get(nm);
        Map<String, Object> hit = _rule_for(nm);
        Matcher m = Py.search(_SUBN, nm);
        if (m != null) {
            Map<String, Object> sub = _rule_for(m.group(1));
            if (sub != null && (hit == null || (!Py.truthy(Py.get(Py.or(hit.get("opt"), new LinkedHashMap<String, Object>()), "by_benefit")) && !java.util.Objects.equals(sub.get("kind"), hit.get("kind")))))
                hit = sub;
        }
        _CC.put(nm, hit);
        return hit;
    }

    // ══ 담보명 토큰 ════════════════════════════════════════════════════
    public static final String[][] HOSP = {{"상급종합병원", "상급종합"}, {"요양병원", "요양"}, {"종합병원", "종합"}};
    public static Map<String, Object> tokens(String nm) {
        Map<String, Object> t = new LinkedHashMap<>();
        t.put("cause", (nm.contains("상해") || nm.contains("재해")) ? "상해" : (nm.contains("질병") ? "질병" : null));
        t.put("ex_hosp", nm.contains("요양병원제외") ? "요양" : null);            // '(요양병원제외)' 는 요양병원 입원을 빼는 조건이지 요양병원 요구가 아니다
        String _nm = nm.replace("요양병원제외", "");
        String hosp = null;
        for (String[] kv : HOSP) if (_nm.contains(kv[0])) { hosp = kv[1]; break; }
        t.put("hosp", hosp);
        t.put("room", (nm.contains("1인실") && !nm.contains("2-3인실")) ? "1인실" : (nm.contains("2-3인실") ? "2-3인실" : null));
        Matcher m = Py.search("(\\d+)일한도", nm);        t.put("limit", m != null ? (Object) Long.parseLong(m.group(1)) : null);
        m = Py.search("\\((\\d+)일이상", nm);             t.put("minday", m != null ? (Object) Long.parseLong(m.group(1)) : null);
        m = Py.search("[\\[(](상해|질병)?(\\d)종[,\\])]", nm);
        t.put("gkind", m != null ? m.group(1) : null);   t.put("gj", m != null ? (Object) Long.parseLong(m.group(2)) : null);
        t.put("icu", nm.contains("중환자실"));
        t.put("visit", nm.contains("통원"));
        t.put("plus", nm.contains("(plus)"));
        t.put("ex", Py.findall("특정(\\d)대질병(?:및[^()\\[\\]]*?)?제외", nm));      // 「특정6대질병및혀유착증제외」 도 특정6대 제외
        return t;
    }

    // ══ KCD 판정 ═══════════════════════════════════════════════════════
    public static final Map<String, Object> HRANK = Py.dict("의원", 0L, "병원", 1L, "종합", 2L, "상급종합", 3L);
    /** 담보가 요구하는 병원 종별(need)을 사례의 병원(have)이 충족하는지. 상급종합병원은 종합병원 조건도 함께 충족한다. */
    public static boolean hosp_ok(Object need, Object have) {
        if (!Py.truthy(need)) return true;
        if ("요양".equals(need) || "요양".equals(have)) return need.equals(have);
        if (have == null || "모든".equals(have)) return false;
        return Py.lng(HRANK.containsKey(have) ? HRANK.get(have) : (Object) 0L) >= Py.lng(HRANK.containsKey(need) ? HRANK.get(need) : (Object) 0L);
    }

    /** 암·유사암(제자리암 포함) 여부 */
    public static boolean is_cancer(String kcd) { return Py.truthy(Engine.cancer_cls(kcd)); }

    public static final Pattern RNG = Py.re("^([A-Z])(\\d{2})~([A-Z])(\\d{2})$");
    // 세분류 범위 표기 — 'Q26.0~Q26.4'
    public static final Pattern RNG_SUB = Py.re("^([A-Z]\\d{2})\\.(\\d{1,2})~([A-Z]\\d{2})\\.(\\d{1,2})$");
    private static final Pattern _M3 = Py.re("^([A-Z])(\\d{2})");
    private static boolean _isdigit(String s) {
        if (s.isEmpty()) return false;
        for (int i = 0; i < s.length(); i++) if (!Character.isDigit(s.charAt(i))) return false;
        return true;
    }
    /** 약관 KCD 목록(개별코드·세분류·범위표기 A15~A19·제외표기 !N74.0 모두 지원) 대조 */
    public static boolean code_hit(List<Object> codes, String kcd) {
        if (!Py.truthy(codes)) return false;
        String c3 = Py.split(kcd, ".").get(0);
        Matcher m3 = Py.match(_M3, c3);
        for (Object eo : codes) {                                   // 제외 코드가 먼저
            String e = (String) eo;
            if (e.startsWith("!")) {
                String x = Py.strip(e.substring(1));
                if (kcd.equals(x) || kcd.startsWith(x + ".") || (x.length() == 3 && c3.equals(x))) return false;
            }
        }
        for (Object eo : codes) {
            String e = Py.strip((String) eo);
            if (e.startsWith("!")) continue;
            if (kcd.equals(e) || kcd.startsWith(e + ".") || c3.equals(e) || e.startsWith(kcd + ".")) return true;
            if (e.indexOf('~') < 0) continue;                       // 아래 두 패턴은 '~' 가 있어야 걸린다(빠른 길 · 결과 같음)
            Matcher r = Py.match(RNG, e);
            if (r != null && m3 != null && r.group(1).equals(m3.group(1)) && m3.group(1).equals(r.group(3))
                    && Long.parseLong(r.group(2)) <= Long.parseLong(m3.group(2)) && Long.parseLong(m3.group(2)) <= Long.parseLong(r.group(4)))
                return true;
            Matcher rs = Py.match(RNG_SUB, e);                      // 'Q26.0~Q26.4' — 세분류 자리로 비교
            if (rs != null && rs.group(1).equals(rs.group(3)) && rs.group(3).equals(c3) && kcd.contains(".")) {
                String sub = kcd.substring(kcd.indexOf('.') + 1); int w = rs.group(2).length();
                String sw = Py.slice(sub, null, w);
                if (_isdigit(sw) && Long.parseLong(rs.group(2)) <= Long.parseLong(sw) && Long.parseLong(sw) <= Long.parseLong(rs.group(4)))
                    return true;
            }
        }
        return false;
    }

    /** 특약 마스터의 제외코드(x : 보상하지 않는 질병)에 해당하면 true */
    public static boolean excluded(Map<String, Object> r, String kcd) {
        List<Object> ex = Py.L(Py.or(r.get("excl"), new ArrayList<Object>()));
        return Py.truthy(ex) && code_hit(ex, kcd);
    }

    public static final Map<String, Object> C13 = Py.exists(Py.path("cancer13.json")) ? Py.M(Py.loadJson("cancer13.json")) : Py.dict("groups", new LinkedHashMap<String, Object>(), "alias", new LinkedHashMap<String, Object>());
    public static final Map<String, Object> _C13N = new LinkedHashMap<>();
    /** 세부급부 암종명 → 약관 별표 「암종별(13종)통합암(전이포함)(유사암제외) 분류표」 질병코드 */
    public static List<Object> c13_codes(String name) {
        return Py.L(_C13N.get(Py.sub("[\\s()·,]|전이포함", "", name == null ? "" : name)));
    }

    public static String g131_key(String label) {
        String l = Py.sub("[\\s․·,]", "", label == null ? "" : label);
        for (String cand : new String[]{l, Py.sub("다빈도\\d+대질병", "다빈도64대질병", l)}) {   // 다빈도61대·62대는 그 별표 그대로, 없을 때만 64대 통합표
            for (String k : G131.keySet()) if (Py.sub("[\\s․·,]", "", k).equals(cand)) return k;
        }
        return null;
    }

    public static String _pn(Object s) { return Py.sub("[\\s․·,]", "", s == null ? "" : (String) s); }
    /** 약관 KCD 목록이 없는 담보 : 사례가 선언한 질병군(grp)이 담보명·세부급부에 들어 있으면 대상으로 본다. */
    public static boolean grp_hit(String nm, Map<String, Object> sc) { return grp_hit(nm, sc, null); }
    public static boolean grp_hit(String nm, Map<String, Object> sc, Map<String, Object> r) {
        String lab = _pn(Py.or(Py.or(Py.get(r, "benefit"), Py.get(r, "sub")), ""));
        for (Object go : Py.L(Py.or(Py.get(sc.get("tags"), "grp"), new ArrayList<Object>()))) {
            String g = _pn(go);
            if (!g.isEmpty() && (_pn(nm).contains(g) || g.equals(lab))) return true;
        }
        return false;
    }

    public static final Map<String, Object> DXFAM = Py.dict("cancer", "암", "sim_cancer", "암", "brain", "뇌", "heart", "심장");

    public static boolean _BRAIN3(String c) { return c.startsWith("I6") || c.startsWith("G45"); }
    public static boolean _HEART3(String c) { String p = Py.slice(c, null, 2); return p.equals("I2") || p.equals("I4") || p.equals("I5"); }
    public static final Map<List<Object>, Boolean> _SPAN = new HashMap<>();

    /** 약관 KCD 목록이 뇌(I6·G45)와 심장(I2·I4·I5) 두 계열에 모두 걸쳐 있는가. */
    public static boolean spans_brain_heart(List<Object> codes) {
        Boolean hit = _SPAN.get(codes);
        if (hit != null) return hit;
        Set<String> c3 = new LinkedHashSet<>();
        for (Object eo : codes) {
            String e = Py.strip((String) eo);
            int a = 0; while (a < e.length() && e.charAt(a) == '!') a++;
            e = e.substring(a);
            Matcher m = Py.match(RNG, e);
            if (m != null) {
                for (long i = Long.parseLong(m.group(2)); i <= Long.parseLong(m.group(4)); i++) c3.add(Py.fmt("%s%02d", m.group(1), i));
            } else {
                c3.add(Py.split(e, ".").get(0));
            }
        }
        boolean b = false, h = false;
        for (String c : c3) { if (_BRAIN3(c)) b = true; if (_HEART3(c)) h = true; }
        _SPAN.put(new ArrayList<>(codes), b && h);
        return b && h;
    }

    /** 세부급부/하위그룹 라벨이 뇌·심장 질병군을 가리키면 그 계열 코드에만 지급. 담보의 약관 KCD 목록이 두 계열에 걸쳐 있을 때만 좁힌다 */
    public static boolean sub_ok(Map<String, Object> r, String kcd) {
        List<Object> codes = Py.L(Py.or(r.get("codes"), new ArrayList<Object>()));
        if (!spans_brain_heart(codes)) return true;
        String lab = (Py.str(Py.or(r.get("sub"), "")) + Py.str(Py.or(r.get("benefit"), "")) + Py.str(Py.get(r, "name", ""))).replace(" ", "");
        boolean brain = lab.contains("뇌졸중") || lab.contains("뇌혈관") || lab.contains("뇌출혈") || lab.contains("뇌경색");
        boolean heart = lab.contains("심장") || lab.contains("허혈성") || lab.contains("심근경색") || lab.contains("협심증");
        if (brain && !heart) return _BRAIN3(kcd);
        if (heart && !brain) return _HEART3(kcd);
        return true;
    }

    private static boolean _hc_meet(Object a, Object b) {
        Collection<?> x = (Collection<?>) Py.or(a, new ArrayList<Object>()), y = (Collection<?>) Py.or(b, new ArrayList<Object>());
        if (x.isEmpty() || y.isEmpty()) return false;
        Set<Object> s = new HashSet<>(x);
        for (Object v : y) if (s.contains(v)) return true;
        return false;
    }

    /** mode : major / sim / major_or_sim / major_thy_skin / by_name_cancer / codes / codes_listed / g131 / group / hc / none · o : 규칙 opt */
    public static boolean kcd_ok(Object mode, Map<String, Object> r, Map<String, Object> sc, String nm) { return kcd_ok(mode, r, sc, nm, null); }
    public static boolean kcd_ok(Object mode, Map<String, Object> r, Map<String, Object> sc, String nm, Map<String, Object> o) {
        String kcd = (String) Py.at(sc, "kcd");
        if (mode == null || "none".equals(mode)) return true;
        Map<String, Object> tg = Py.gm(sc, "tags");
        if ("hc".equals(mode)) {                                    // 약관 별표의 진료행위(수가)코드 ∩ 사례 단계의 수가코드
            if (!Py.truthy(r.get("hc"))) {                          // 목록이 비어 있으면 조용히 0 이 아니라 사유를 남긴다
                log("수가코드없음", Py.gs(r, "name"), no_master_why(r, "약관 별표 진료행위(수가)코드 목록")); return false;
            }
            return _hc_meet(r.get("hc"), tg.get("hc"));
        }
        if ("major".equals(mode)) return "major".equals(Engine.cancer_cls(kcd));
        if ("sim".equals(mode)) { String c = Engine.cancer_cls(kcd); return "cis".equals(c) || "bord".equals(c) || "thy".equals(c) || "skin".equals(c); }
        if ("major_or_sim".equals(mode)) return Py.truthy(Engine.cancer_cls(kcd));
        if ("major_thy_skin".equals(mode)) { String c = Engine.cancer_cls(kcd); return "major".equals(c) || "thy".equals(c) || "skin".equals(c); }
        if ("by_name_cancer".equals(mode)) {                        // 세부보장명이 대상 암을 정하는 담보 : 기타피부암 → skin · 갑상선암 → thy · 그 밖 → major
            String want = nm.contains("기타피부암") ? "skin" : (nm.contains("갑상선암") ? "thy" : "major");
            return want.equals(Engine.cancer_cls(kcd));
        }
        if ("g131".equals(mode)) {
            // 세부보장 레코드에 약관 KCD 목록이 있으면 그 목록이 우선
            if (Py.truthy(r.get("codes")) && (Py.truthy(r.get("sub_rec")) || Py.has("\\[[^\\]]+\\]\\s*$", Py.gs(r, "name")))) return code_hit(Py.gl(r, "codes"), kcd);
            String key = g131_key((String) Py.or(Py.or(r.get("benefit"), r.get("sub")), ""));
            if (Py.truthy(key)) return code_hit(Py.gl(G131, key), kcd) && !(Py.truthy(G131X.get(key)) && code_hit(Py.gl(G131X, key), kcd));
            if (Py.truthy(r.get("codes")) && Py.has("\\[[^\\]]+\\]\\s*$", Py.gs(r, "name"))) return code_hit(Py.gl(r, "codes"), kcd);
            return grp_hit(nm, sc, r);
        }
        if ("group".equals(mode)) {
            String key = (String) Py.get(Py.or(o, new LinkedHashMap<String, Object>()), "grp");      // 규칙이 그룹표를 직접 지정한 경우
            if (!Py.truthy(key)) {
                // 담보명에 들어 있는 그룹명 중 가장 긴 것 — '10대특정암(전이포함)'이 '10대특정암'보다 우선 · 그룹명 띄어쓰기 무시
                String _n = nm.replace(" ", "");
                key = null;
                for (String g : KCDG.keySet()) {
                    if (!g.startsWith("_") && _n.contains(g.replace(" ", "")) && (key == null || g.length() > key.length())) key = g;
                }
            }
            Object lst = Py.truthy(key) ? KCDG.get(key) : null;
            if (!Py.truthy(lst)) {
                log("KCD없음", Py.gs(r, "name"), Py.orS(key, "세부급부") + " 분류표가 규칙표에 없어 지급 판정 제외 (약관 별표 보강 필요)"); return false;
            }
            return code_hit(Py.L(lst), kcd);
        }
        if ("codes_listed".equals(mode)) {
            // 약관이 대상 질병을 정해 둔 검사비 담보 — 마스터에 목록이 없는 담보는 종전대로
            if (!Py.truthy(r.get("codes"))) {
                log("검토필요", Py.gs(r, "name"), "특약 마스터에 약관 KCD 목록이 없어 질병 조건 없이 계산 — 약관에 대상 질병 제한이 있는지 확인 필요");
                return true;
            }
            return sub_ok(r, kcd) && code_hit(Py.gl(r, "codes"), kcd);
        }
        if ("codes".equals(mode)) {
            if (!sub_ok(r, kcd)) return false;
            if (Py.truthy(r.get("codes"))) return code_hit(Py.gl(r, "codes"), kcd);
            if (grp_hit(nm, sc, r)) return true;
            log("KCD없음", Py.gs(r, "name"), no_master_why(r, "약관 KCD 목록"));
            return false;
        }
        return false;
    }

    // ══ 구조별 지급 계산 ═══════════════════════════════════════════════
    public static Set<Object> _acts(Map<String, Object> sc) { return _acts(sc, false); }
    public static Set<Object> _acts(Map<String, Object> sc, boolean with_done) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        Set<Object> a = new HashSet<>(Py.L(Py.or(tg.get("acts"), new ArrayList<Object>())));
        if (with_done) a.addAll(Py.L(Py.or(tg.get("done"), new ArrayList<Object>())));
        for (Object evo : Py.L(Py.or(sc.get("itc_events"), new ArrayList<Object>()))) {
            List<Object> ev = Py.L(evo);
            if (ev.size() > 3) a.addAll(Py.L(ev.get(3)));
        }
        if (Py.truthy(tg.get("surg"))) a.add("surg");
        // 전신마취 — 사례에 anes=1 이 적힌 단계만 본다. 마취시간 anes_h 가 4·6시간 이상이면 그 구간 행위(anes4 · anes6)도 받은 것으로 본다
        if (Py.truthy(tg.get("anes"))) {
            a.add("anes");
            Object _h = Py.or(tg.get("anes_h"), 0L);
            if (Py.cmp(_h, 4L) >= 0) a.add("anes4");
            if (Py.cmp(_h, 6L) >= 0) a.add("anes6");
        }
        if (a.contains("immune")) a.add("target");      // 면역항암 치료 시 표적항암약물허가치료 합산(약관)
        return a;
    }

    /** 핸들러 — 지급 줄 [(금액, 사유, 구분, 빈도[, 덧붙일 값])] 을 Object[] 목록으로 돌려준다 */
    public interface Handler { List<Object[]> h(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t); }
    private static List<Object[]> NONE() { return new ArrayList<>(); }
    private static List<Object[]> one(Object... tuple) { List<Object[]> l = new ArrayList<>(); l.add(tuple); return l; }

    public static List<Object[]> h_dx(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        Object dx = tg.get("dx");
        if (Py.truthy(o.get("reg"))) {                                            // 산정특례 등록 조건부 진단비
            Object[] sr = special_reg(r, sc, nm, dx);
            dx = sr[1];
            if (!((Boolean) sr[0])) return NONE();
        }
        if (!Py.truthy(dx) && !"상해".equals(o.get("cause"))) return NONE();
        if (Py.truthy(o.get("fam")) && !_inObj(o.get("fam"), dx == null ? null : DXFAM.get(dx))) return NONE();
        if (Py.truthy(o.get("cause")) && !Py.eq(tg.get("cause"), o.get("cause"))) return NONE();
        if (Py.truthy(tg.get("recur")) != "recur".equals(o.get("stage"))) return NONE();     // 재진단 단계에서는 재진단암 진단비만
        if (!kcd_ok(o.get("kcd"), r, sc, nm, o)) return NONE();
        Object freq = nm.contains("연간1회한") ? "year" : Py.get(o, "freq", "once");
        return one(Py.at(r, "man"), Py.get(o, "why", "진단확정"), Py.get(o, "group", "진단비"), freq);
    }
    /** x in c (c 는 목록 — 원소가 null 일 수도 있다) */
    private static boolean _inObj(Object c, Object x) {
        if (c instanceof String) return x instanceof String && ((String) c).contains((String) x);
        for (Object y : (Collection<?>) c) if (Py.eq(x, y)) return true;
        return false;
    }

    public static final Map<String, Map<String, Object>> _GRADE_T = new HashMap<>();
    /** 수가코드 → 종 표(약관 분류표를 extract_*.py 로 읽은 것). 파일이 없으면 빈 표 */
    public static Map<String, Object> grade_table(String key) {
        if (!_GRADE_T.containsKey(key)) {
            String p = Py.path(key + ".json");
            _GRADE_T.put(key, Py.exists(p) ? Py.M(Py.or(Py.get(Json.parse(Py.read(p)), "grades"), new LinkedHashMap<String, Object>())) : new LinkedHashMap<>());
        }
        return _GRADE_T.get(key);
    }

    public static List<Object[]> h_surg(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags"); Object j = tg.get("surg");
        String rname = (String) Py.at(r, "name"); String kcd = (String) Py.at(sc, "kcd");
        if (!_acts(sc).contains("surg")) return NONE();
        Object cause = Py.or(t.get("cause"), o.get("cause"));
        if (Py.truthy(cause) && !Py.eq(Py.get(tg, "cause", "질병"), cause)) return NONE();
        if (!hosp_ok(t.get("hosp"), tg.get("hosp"))) return NONE();
        if ("1-5".equals(o.get("grade"))) {
            if (!Py.truthy(t.get("gj"))) return NONE();
            if (Py.truthy(t.get("gkind")) && !Py.eq(t.get("gkind"), Py.get(tg, "cause", "질병"))) return NONE();
            Object j5 = surg5_grade(j, kcd);                   // 정수 또는 분류표 항목번호
            if (j5 == null) {
                log("검토필요", rname, Py.fmt("1-5종 수술분류표에 없는 항목 %s — 계산 제외", j)); return NONE();
            }
            if (!Py.eq(t.get("gj"), j5)) return NONE();
            if (Py.truthy(o.get("plus")) && Py.cmp(Py.get(tg, "surg_cnt", 1L), 2L) < 0) return NONE();
        } else if ("1-7".equals(o.get("grade"))) {
            if (Py.has("\\[(상해|질병)\\d-\\d종\\]", rname.replace(" ", ""))) {      // 종 범위 부모 행([질병4-7종]) — 금액은 ┗ 종별 세부 행에 있다
                log("검토필요", rname, "1-7종 수술비 부모 행(종 범위 표기) — 종별 세부 행만 계산"); return NONE();
            }
            Object g7 = surg7_grade(tg.get("surg7"));          // 정수 또는 분류표 수술코드
            if (g7 == null) {
                log("검토필요", rname, Py.truthy(tg.get("surg7")) ? Py.fmt("1-7종 수술분류표에 없는 수술코드 %s — 계산 제외", tg.get("surg7"))
                        : "1-7종 수술분류표 종 구분이 사례에 없어 계산 제외");
                return NONE();
            }
            if (Py.truthy(t.get("gj")) && !Py.eq(t.get("gj"), g7)) return NONE();
        } else if (Py.truthy(o.get("new"))) {                 // 신수술비[기본]·[주요수술] — 사례 수술코드(ADRG)로만 판정
            String code = Py.str(Py.or(tg.get("surg7"), "")).toUpperCase();
            List<String> sp = Py.split(Py.sub(GOJI, "", rname), "]");
            String lab0 = sp.get(sp.size() - 1).replace(" ", "");          // 세부보장 글자 : 대괄호 뒤 괄호
            if (!Py.has("입원|통원|장기이식|개두|개흉|개복|각막|경피적", lab0)) {
                log("검토필요", rname, "신수술비 부모 행 — 세부보장(입원/통원 · 수술종류) 행만 계산"); return NONE();
            }
            if (code.isEmpty()) {
                log("검토필요", rname, "신수술분류표 판정에 쓸 수술코드(ADRG)가 사례에 없어 계산 제외"); return NONE();
            }
            String _type;
            if ("basic".equals(o.get("new"))) {
                if (!_NEWSURG_BASIC.contains(code)) {
                    log("검토필요", rname, Py.fmt("신수술분류표[기본]에 없는 수술코드 %s — 계산 제외", code)); return NONE();
                }
                String adm = "out".equals(tg.get("adm")) ? "out" : "in";        // 사례 가정 : 적지 않으면 2일 이상 입원 수술
                if (lab0.contains("입원") != adm.equals("in")) return NONE();
                _type = adm.equals("in") ? "입원" : "통원";
            } else {
                String ck = (String) Py.or(cause, "질병");
                Object typ = Py.get(Py.get(Py.or(NEWSURG.get("major"), new LinkedHashMap<String, Object>()), ck, new LinkedHashMap<String, Object>()), code);
                if (!Py.truthy(typ)) {
                    log("검토필요", rname, Py.fmt("%s 신수술분류표[주요수술]에 없는 수술코드 %s — 계산 제외", ck, code)); return NONE();
                }
                String want = null;
                for (String[] kv : NEWSURG_TYPE_KEY) if (lab0.contains(kv[0])) { want = kv[1]; break; }
                if (!Py.eq(want, typ)) return NONE();
                _type = (String) typ;
            }
            String why = Py.str(Py.get(o, "why", "수술 1회")).replace("{code}", code).replace("{type}", _type);
            return one(Py.at(r, "man"), why, Py.get(o, "group", "수술비"), Py.get(o, "freq", "each"));
        } else if (!Py.truthy(j)) return NONE();
        if (_inObj(Py.or(o.get("ex"), new ArrayList<Object>()), "cancer") && is_cancer(kcd)) return NONE();
        for (Object g : Py.gl(t, "ex")) {                                   // 특정N대질병 제외 담보 — N 에 맞는 제외 목록으로
            Object lst = KCDG.get(Py.fmt("특정%s대질병", g));
            if (!Py.truthy(lst)) {
                log("검토필요", rname, Py.fmt("특정%s대질병 제외목록이 규칙표에 없음 — 특정5대질병 기준으로 판정", g)); lst = FIVE_MAJOR;
            }
            // 대장 용종·양성신생물 내시경 절제(사례 태그 five_major)는 특정5대·6대의 ① 항 — 특정2대에는 없다
            if ((("5".equals(g) || "6".equals(g)) && Py.truthy(tg.get("five_major"))) || code_hit(Py.L(lst), kcd)) return NONE();
        }
        if (!kcd_ok(o.get("kcd"), r, sc, nm, o)) return NONE();
        String _pg = "";
        if (Py.truthy(o.get("grade_table"))) {
            // 종별로 금액이 다른 수가코드 수술비(폴립및양성종양수술비 1-6종) — 사례 수가코드의 종과 같은 [N종] 줄만 지급한다
            Map<String, Object> gt = grade_table((String) o.get("grade_table"));
            List<Object> cg = new ArrayList<>();
            Set<Object> rh = new HashSet<>(Py.L(Py.or(r.get("hc"), new ArrayList<Object>())));
            for (Object c : new LinkedHashSet<>(Py.L(Py.or(tg.get("hc"), new ArrayList<Object>())))) {
                if (!rh.contains(c)) continue;
                Object g = gt.get(c);
                if (g != null && !Py.in(g, cg)) cg.add(g);
            }
            if (cg.isEmpty()) {
                log("검토필요", rname, Py.fmt("종별 분류표(%s)에 사례 수가코드가 없어 계산 제외", o.get("grade_table"))); return NONE();
            }
            List<Object> cgs = Py.sorted(cg);
            List<Object> cgt = new ArrayList<>();
            for (Object g : cgs) cgt.add(Py.str(g));
            if (cg.size() > 1) {
                log("검토필요", rname, Py.fmt("사례 수가코드가 여러 종(%s)에 걸쳐 종을 하나로 정할 수 없어 계산 제외", Py.join("·", cgt))); return NONE();
            }
            Matcher mg = Py.search("[\\[(](\\d)종[\\])]\\s*$", Py.sub(GOJI, "", rname).replace(" ", ""));
            if (mg != null && !Py.in(Long.parseLong(mg.group(1)), cg)) return NONE();
            _pg = Py.join("·", cgt);
        }
        // 관혈/비관혈로 나뉜 담보(5대질환수술비[관혈]·[비관혈], 32대질병관혈수술비) — 한 번의 수술은 둘 중 하나다.
        String lab = rname.replace(" ", "");
        if (Py.truthy(o.get("open_rate"))) {
            // 한 담보가 관혈 · 비관혈 지급률을 따로 정한 것(척추질병수술비(연간1회한)(관혈,비관혈) — 관혈 100% · 비관혈 50% · 각각 연간 1회)
            Boolean op = surg_open(tg);
            if (op == null) {
                log("검토필요", rname, "관혈·비관혈 구분이 사례에 없어 계산 제외"); return NONE();
            }
            Object rate = Py.at(o.get("open_rate"), op ? "open" : "closed");
            double a = Py.num(Py.mul(Py.at(r, "man"), rate)) / 100.0;
            Object amt = (a == (double) (long) a) ? (Object) Long.valueOf((long) a) : (Object) Double.valueOf(a);
            String why = Py.str(Py.get(o, "why", "수술 1회")).replace("{approach}", op ? "관혈" : "비관혈").replace("{rate}", Py.fmtG(rate));
            return one(amt, why, Py.get(o, "group", "수술비"), Py.get(o, "freq", "year"));
        }
        if (lab.contains("관혈")) {
            Boolean op = surg_open(tg);
            if (op == null) {
                log("검토필요", rname, "관혈·비관혈 구분이 사례에 없어 계산 제외"); return NONE();
            }
            if (op != !lab.contains("비관혈")) return NONE();
        }
        Object _jj = Py.or(Py.or(t.get("gj"), "1-7".equals(o.get("grade")) ? surg7_grade(tg.get("surg7")) : surg5_grade(j, kcd)), "");
        Matcher mgl = Py.search("[\\[(]([^\\[\\]()]+)[\\])]\\s*$", rname);
        String _gl = Py.strip((String) Py.or(Py.or(Py.or(r.get("benefit"), r.get("sub")), mgl != null ? mgl.group(1) : ""), ""));
        String why = Py.strip(Py.str(Py.get(o, "why", "수술 1회")).replace("{j}", Py.str(_jj)).replace("{g}", _gl).replace("{pg}", _pg));
        Object freq = lab.contains("연간1회한") ? "year" : Py.get(o, "freq", "each");     // 약관이 연간 1회로 정한 수술비
        return one(Py.at(r, "man"), why, Py.get(o, "group", "수술비"), freq);
    }

    public static List<Object[]> h_day(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags"); Object mode = Py.get(o, "mode", "day");
        Object man = Py.at(r, "man");
        if (Py.truthy(t.get("cause")) && !Py.eq(tg.get("cause"), t.get("cause"))) return NONE();
        if (Py.truthy(t.get("ex_hosp")) && Py.eq(tg.get("hosp"), t.get("ex_hosp"))) return NONE();
        if (!hosp_ok(t.get("hosp"), tg.get("hosp"))) return NONE();
        if (Py.truthy(t.get("room")) && !Py.eq(tg.get("room"), t.get("room"))) return NONE();
        if (Py.truthy(o.get("need_surg")) && !Py.truthy(tg.get("surg"))) return NONE();
        if (!kcd_ok(o.get("kcd"), r, sc, nm, o)) return NONE();
        if ("daycare".equals(mode)) {                                // 낮병동 입원(급여) 1일당 — 사례 태그 daycare 일수
            Object n = Py.get(tg, "daycare", 0L);
            if (!Py.truthy(n)) return NONE();
            n = Py.min2(n, Py.or(t.get("limit"), n));
            return one(Py.mul(man, n), Py.fmt("낮병동 입원 %d일 × %d만원", n, man), Py.get(o, "group", "입원일당"), "each");
        }
        if ("visit".equals(mode)) {
            Object n = Py.get(tg, "visits", 0L);
            if (!Py.truthy(n)) return NONE();
            n = Py.min2(n, Py.or(t.get("limit"), n));
            return one(Py.mul(man, n), Py.fmt("통원 %d회 × %d만원", n, man), Py.get(o, "group", "통원일당"), "each");
        }
        if ("icu".equals(mode) || Py.truthy(t.get("icu"))) {
            Object d = Py.get(tg, "icu", 0L);
            if (!Py.truthy(d)) return NONE();
            return one(Py.mul(man, d), Py.fmt("중환자실 %d일", d), Py.get(o, "group", "입원일당"), "each");
        }
        Object days = Py.get(tg, "days", 0L);
        if (!Py.truthy(days)) return NONE();
        if (Py.truthy(t.get("minday")) && Py.cmp(days, t.get("minday")) < 0) return NONE();
        Object d = Py.min2(days, Py.or(t.get("limit"), days));
        if (Py.truthy(t.get("minday")) && Py.cmp(t.get("minday"), 1L) > 0)
            d = Py.max2(0L, Py.min2(Py.add(Py.sub(days, t.get("minday")), 1L), Py.or(t.get("limit"), days)));
        if (!Py.truthy(d)) return NONE();
        return one(Py.mul(man, d), Py.fmt("입원 %d일 × %d만원", d, man), Py.get(o, "group", "입원일당"), "each");
    }

    public static final String[][] _EXAM_KEYS = {{"내시경", "x_endo"}, {"MRI", "x_mri"}, {"(?<![A-Z])CT", "x_ct"}, {"PET|양전자", "x_pet"}, {"초음파", "x_us"},
            {"생검|조직병리", "x_bio"}, {"단일유전자", "x_gene"}, {"NGS", "x_ngs"}};

    /** 약관 지급금액표가 치료 「구분」마다 지급률을 따로 정한 담보 — 건선특정치료비(rules.json tx_psoriasis opt.parts) */
    public static List<Object[]> _tx_parts(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        if (Py.truthy(tg.get("nc"))) return NONE();
        if (Py.truthy(t.get("cause")) && !Py.eq(tg.get("cause"), t.get("cause"))) return NONE();
        if (!kcd_ok(o.get("kcd"), r, sc, nm, o)) return NONE();
        List<Object[]> out = new ArrayList<>();
        for (Object po : Py.L(Py.at(o, "parts"))) {
            Map<String, Object> p = Py.M(po);
            if (Py.truthy(p.get("hc_listed"))) {
                if (!_hc_meet(r.get("hc"), tg.get("hc"))) continue;
                Object d = tg.get("psor_light_days");
                if (d == null) {
                    log("검토필요", Py.gs(r, "name"), Py.fmt("%s : 연간 치료일수가 사례에 없어 지급 판정 제외(약관 연간 %d일 이상)", Py.at(p, "label"), Py.get(p, "min_days", 0L))); continue;
                }
                if (Py.cmp(d, Py.get(p, "min_days", 0L)) < 0) continue;
            } else {
                Object dd = Py.or(tg.get("psor_drug_days"), 0L), inj = Py.or(tg.get("psor_inj"), 0L);
                if (!((Py.truthy(p.get("min_drug_days")) && Py.cmp(dd, p.get("min_drug_days")) >= 0) || (Py.truthy(p.get("min_inj")) && Py.cmp(inj, p.get("min_inj")) >= 0))) continue;
            }
            out.add(new Object[]{Py.num(Py.mul(Py.at(r, "man"), Py.at(p, "rate"))) / 100.0, Py.fmt("%s · 가입금액의 %s%% · 연간 1회", Py.at(p, "label"), Py.fmtG(Py.at(p, "rate"))), Py.get(o, "group", "치료비"), "year"});
        }
        return out;
    }

    private static boolean _meet(Set<?> a, Set<?> b) { for (Object x : a) if (b.contains(x)) return true; return false; }

    public static List<Object[]> h_tx(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        String rname = (String) Py.at(r, "name"); String kcd = (String) Py.at(sc, "kcd");
        if (Py.truthy(o.get("parts"))) return _tx_parts(r, o, sc, nm, t);
        Set<Object> need = new LinkedHashSet<>(Py.L(Py.or(o.get("acts"), new ArrayList<Object>())));
        if (Py.truthy(o.get("by_benefit"))) {                                   // 세부급부명으로 치료행위·암종 결정 (26종 항암방사선및약물치료비 등)
            String b = (String) Py.or(r.get("benefit"), "");
            if (b.isEmpty()) { log("검토필요", rname, "세부급부(암종·치료)가 없는 부모 담보 — 계산 제외"); return NONE(); }
            if (b.contains("방사선")) need = new LinkedHashSet<>(List.of("rad"));
            else if (b.contains("약물")) need = new LinkedHashSet<>(List.of("chemo"));
            Matcher inner = Py.search("치료비\\((.+)\\)$", b);
            String raw = inner != null ? inner.group(1) : b;
            List<Object> codes = c13_codes(raw);                                    // 약관 별표 「암종별(13종)」 분류표 우선
            if (!Py.truthy(codes)) {                                                // 표에 없는 암종명은 기존 코드 사전으로 보조 판정
                List<String> kinds = Py.resplit("과|및|,|·", Py.sub("\\(전이포함\\)", "", raw));
                codes = new ArrayList<>();
                for (String k : kinds) {
                    String ks = Py.strip(k);
                    for (Map.Entry<String, Object> e : SYN.entrySet()) if (e.getKey().equals(ks)) codes.addAll(Py.L(e.getValue()));
                }
            }
            if (!Py.truthy(codes)) {
                log("KCD없음", rname, "세부급부 암종 \"" + raw + "\"이 약관 별표 「암종별(13종)」 분류표·코드 사전에 없어 계산 제외"); return NONE();
            }
            if (!code_hit(codes, kcd)) return NONE();
        }
        // 약관 별표 1-7종 수술분류표의 수술구분으로 가리는 담보(예 '뇌동맥류수술' = B011~B018)
        if (Py.truthy(o.get("surg7_grp")) && !Py.eq(surg7_group(tg.get("surg7")), o.get("surg7_grp"))) return NONE();
        // 마스터에 수가코드 목록이 실린 담보만 그 목록과 대조한다. 목록이 없는 담보는 종전대로.
        if (Py.truthy(o.get("hc_listed")) && Py.truthy(Py.or(r.get("hc"), new ArrayList<Object>()))) {
            if (!_hc_meet(r.get("hc"), tg.get("hc"))) return NONE();
        }
        // 방사선·약물을 한 규칙으로 보는 담보(tx_chemo_rad)의 세부보장이 한쪽만 정했으면 그 치료만
        if (Py.truthy(o.get("split_by_label"))) {
            Matcher ml = Py.search("\\[([^\\[\\]]+)\\]$", nm);
            String lab = Py.sub("\\s", "", (String) Py.or(Py.or(Py.or(r.get("benefit"), r.get("sub")), ""), ml != null ? ml.group(1) : ""));
            if (Py.has("항암방사선치료비?", lab)) need = new LinkedHashSet<>(List.of("rad"));       // 정보계 · 설계서 라벨은 「치료」로 끝난다
            else if (Py.has("항암약물치료비?", lab)) need = new LinkedHashSet<>(List.of("chemo"));
        }
        if (Py.truthy(o.get("exam_by_name"))) {
            Set<Object> ek = new LinkedHashSet<>();
            for (String[] pk : _EXAM_KEYS) if (Py.has(pk[0], nm)) ek.add(pk[1]);
            if (!ek.isEmpty()) need = ek;
        }
        if (!need.isEmpty() && !_meet(need, _acts(sc))) return NONE();
        if (Py.truthy(o.get("not_acts")) && _meet(new HashSet<>(Py.gl(o, "not_acts")), _acts(sc))) return NONE();   // 서로 배타적인 세부보장(특정표적 ↔ 특정면역)
        Set<Object> allneed = new HashSet<>(Py.L(Py.or(o.get("acts_all"), new ArrayList<Object>())));          // 둘 다 받아야 지급되는 담보
        if (!allneed.isEmpty() && !_acts(sc, true).containsAll(allneed)) return NONE();
        if (Py.truthy(o.get("need_cnt")) && Py.cmp(Py.get(tg, "tx_cnt", 0L), o.get("need_cnt")) < 0) return NONE();
        if (Py.truthy(o.get("circ_cnt"))) {                           // 특정순환계질환 통합치료 생활비 — 「연간 특정순환계질환 통합치료횟수」
            Matcher m = Py.search("(\\d)회이상", Py.sub("\\s", "", nm + Py.or(r.get("benefit"), "") + Py.or(r.get("sub"), "")));
            if (m == null) { log("검토필요", rname, "담보명에 「N회이상」이 없어 연간 통합치료횟수 기준을 알 수 없음 — 계산 제외"); return NONE(); }
            List<Object> ev = Py.L(Py.or(sc.get("itc_events"), new ArrayList<Object>()));
            long n = _acts(sc, true).contains("thromb") ? 1 : 0;                                              // 혈전용해치료 연간 1회한
            long ns = 0;
            for (Object eo : ev) { List<Object> e = Py.L(eo); if (e.size() > 3 && Py.L(e.get(3)).contains("surg")) ns++; }
            n += ns != 0 ? ns : (Py.truthy(tg.get("surg")) ? 1 : 0);                                           // 수술 1회당
            n += (Py.cmp(Py.or(tg.get("icu"), 0L), 4L) >= 0 && hosp_ok("종합", tg.get("hosp"))) ? 1 : 0;        // 종합병원 중환자실 4일이상 연간 1회한
            if ("II".equals(o.get("circ_cnt"))) {                       // 특정순환계질환 통합치료비Ⅱ — 주요치료Ⅱ 7항목 : 위 셋 + CRRT · 인공호흡기 · 저체온요법 · 부분체외순환
                Set<Object> ad = _acts(sc, true);
                for (String k : new String[]{"crrt", "vent", "hypo", "ecmo"}) if (ad.contains(k)) n++;
            }
            if (n < Long.parseLong(m.group(1))) return NONE();
        }
        Object nd = o.get("need_drug");
        Matcher m2 = Py.search("[\\[(](\\d)종(?:및\\d종)?이상", nm);                       // [1종이상]·(2종및3종이상) 담보명 표기 우선
        if (m2 != null) nd = Long.parseLong(m2.group(1));
        if (Py.truthy(nd) && Py.cmp(Py.get(tg, "drug", 0L), nd) < 0) return NONE();          // 연간 약물종류 개수 조건
        boolean _hc_step = Py.truthy(o.get("hc_listed")) && _hc_meet(r.get("hc"), tg.get("hc"));   // 약관 수가코드 시술을 받은 단계
        if (need.isEmpty() && !Py.truthy(tg.get("dx")) && !"hc".equals(o.get("kcd")) && !_hc_step) return NONE();     // 수가코드 담보는 진단 단계가 아니어도 해당 시술이 있으면 지급
        // 비급여(전액본인부담) 전용 담보는 그 치료의 비용이 비급여일 때만 지급한다
        if (Py.has("비급여|전액본인부담", nm) && !Py.truthy(tg.get("nc"))) return NONE();
        // 급여 항암치료비(담보명 '(급여')는 비급여 치료 단계에서는 지급하지 않는다
        if (Py.truthy(o.get("covered_only")) && Py.has("\\(급여", nm) && !Py.has("비급여", nm) && Py.truthy(tg.get("nc"))) return NONE();
        if (Py.truthy(t.get("cause")) && !Py.eq(tg.get("cause"), t.get("cause"))) return NONE();
        if (!hosp_ok(t.get("hosp"), tg.get("hosp"))) return NONE();
        // 담보명·세부급부 라벨이 암 구분을 못박은 담보는 그 구분의 암에만
        if (!cancer_scope_ok(nm, kcd) || !cancer_scope_ok((String) Py.or(Py.or(r.get("sub"), r.get("benefit")), ""), kcd)) return NONE();
        if (!kcd_ok(o.get("kcd"), r, sc, nm, o)) return NONE();
        Object freq = Py.get(o, "freq", "year");
        if (nm.contains("계속받는") || nm.contains("연간1회한")) freq = "year";
        else if (nm.contains("최초1회한")) freq = "once";
        Object man = Py.at(r, "man");
        // 「(2종및3종이상)」 세부보장은 2종이상·3종이상 두 구분을 각각 연간 1회 지급
        if (Py.has("2종및3종이상", nm) && Py.cmp(Py.get(tg, "drug", 0L), 3L) >= 0) {
            List<Object[]> two = new ArrayList<>();
            two.add(new Object[]{man, "연간 약물종류 2종이상 구분", Py.get(o, "group", "치료비"), freq});
            two.add(new Object[]{man, "연간 약물종류 3종이상 구분", Py.get(o, "group", "치료비"), freq});
            return two;
        }
        String why = Py.str(Py.get(o, "why", "약관 대상 치료"));
        if ("year".equals(freq) && "once".equals(o.get("freq"))) why = why.replace("최초 1회", "연간 1회");
        else if ("once".equals(freq) && "year".equals(Py.get(o, "freq", "year"))) why = why.replace("연간 1회", "최초 1회").replace("연 1회", "최초 1회");
        // 「계속받는」 연간형이 두번째 해부터 지급률을 낮추는 담보 — 첫 지급 줄은 가입금액 그대로, 「반복(연 1회)」 집계에는 repeat(가입금액 × 지급률)
        if ("year".equals(freq) && o.get("repeat_rate") != null && nm.contains("계속받는")) {
            Object rr = o.get("repeat_rate");
            return one(man, Py.fmt("%s · 첫번째 100%% · 두번째 해부터 가입금액의 %s%%", why, Py.fmtG(rr)), Py.get(o, "group", "치료비"), freq,
                    Py.dict("repeat", Py.num(Py.mul(man, rr)) / 100.0));
        }
        return one(man, why, Py.get(o, "group", "치료비"), freq);
    }

    /** 최대두배받는2대질환치료비(포인트적립형) — 사례에서 받은 2대질환치료로 포인트를 매기고, 담보명의 점수 구간에 이르면 그 구간의 지급률만큼 최초 1회 지급 */
    public static List<Object[]> h_point2(Map<String, Object> r, Map<String, Object> o, Map<String, Object> sc, String nm, Map<String, Object> t) {
        Map<String, Object> tg = Py.gm(sc, "tags");
        String rname = (String) Py.at(r, "name");
        if (!kcd_ok("codes", r, sc, nm, o)) return NONE();
        Matcher m = Py.search("(\\d)점이상", Py.or(r.get("benefit"), "") + nm);
        if (m == null) {
            log("검토필요", rname, "점수 구간(1~4점이상)이 담보명에 없어 계산 제외"); return NONE();
        }
        long k = Long.parseLong(m.group(1)); Object rate = Py.get(Py.or(o.get("rate"), new LinkedHashMap<String, Object>()), Long.toString(k));
        if (rate == null) {
            log("검토필요", rname, Py.fmt("%d점이상 지급률이 규칙표에 없어 계산 제외", k)); return NONE();
        }
        Set<Object> a = _acts(sc); long dz = 0;
        if (a.contains("thromb")) dz = 1;
        if (a.contains("surg")) {
            Boolean op = surg_open(tg);
            if (op == null) log("검토필요", rname, "관혈·비관혈 구분이 사례에 없어 수술 점수 제외");
            else dz = Math.max(dz, op ? 2 : 1);
        }
        Object d = Py.or(Py.get(tg, "icu", 0L), 0L);
        long ic = Py.cmp(d, 8L) >= 0 ? 2 : (Py.cmp(d, 4L) >= 0 ? 1 : 0);
        long pts = Math.min(4, dz + ic);
        if (pts < k) return NONE();
        double amt = Py.num(Py.mul(Py.at(r, "man"), rate)) / 100.0;
        String why = Py.fmt("2대질환치료포인트 %d점(치료 %d점 + 중환자실 %d점) → %d점이상 구간 · 가입금액의 %s%% · 최초 1회", pts, dz, ic, k, Py.fmtG(rate));
        return one(amt, why, Py.get(o, "group", "치료비"), "once");
    }

    public static final Map<String, Handler> HANDLER = new LinkedHashMap<>();

    // ══ 진입점 ═════════════════════════════════════════════════════════
    /**
     * riders : 설계 담보 목록(Map : name, man, cat, codes, benefit, sub, itc …)
     * sc     : {'kcd','tags',...}  →  [{'name','amt','why','group','no','freq', …}]
     * 파이썬처럼 sc 에 itc_events 가 없으면 넣고, 비급여 단계면 tags 를 복사해 nc=1 을 단다(sc 가 바뀐다).
     */
    public static List<Object> pay_lines(List<Object> riders, Map<String, Object> sc) {
        List<Object> out = new ArrayList<>();
        if (!sc.containsKey("itc_events")) sc.put("itc_events", new ArrayList<Object>());
        // 사례 단계가 비급여(전액본인부담)인지 태그로 옮긴다
        boolean anync = false;
        for (Object eo : Py.gl(sc, "itc_events")) {
            List<Object> e = Py.L(eo);
            if (e.size() > 4 && Py.truthy(Py.get(Py.or(e.get(4), new LinkedHashMap<String, Object>()), "nc"))) { anync = true; break; }
        }
        if (anync) {
            Map<String, Object> tg2 = new LinkedHashMap<>(Py.gm(sc, "tags")); tg2.put("nc", 1L); sc.put("tags", tg2);
        }
        for (Object ro : riders) {
            Map<String, Object> r = Py.M(ro);
            try {
                if (Py.cmp(Py.or(r.get("man"), 0L), 0L) <= 0) continue;
                String n = (String) Py.at(r, "name"); String nm = nname(n);
                String kcd = (String) Py.at(sc, "kcd");
                Map<String, Object> tg = Py.gm(sc, "tags");
                // 세부보장을 둥근 괄호로 적은 담보는 매칭된 마스터 세부보장 레코드의 이름으로 규칙을 판정한다
                if (Py.truthy(r.get("mname")) && Py.gs(r, "mname").contains("[") && !nm.contains("[")) nm = nname(Py.gs(r, "mname"));
                if (excluded(r, kcd)) continue;         // 약관 제외코드(보상하지 않는 질병)에 해당 — 지급 없음
                // 1) 통합치료비 — 약관 지급금액표 엔진에 위임
                if (Py.truthy(r.get("itc"))) {
                    String rid = (String) r.get("itc");
                    if (!Py.truthy(sc.get("itc_events"))) continue;
                    // 담보명이 원인을 못박은 통합치료비는 그 원인일 때만
                    Map<String, Object> _t = tokens(nm); Object _c = _t.get("cause");
                    if (Py.truthy(_c) && !Py.eq(tg.get("cause"), _c)) continue;
                    // 담보명이 병원 종별을 못박은 통합치료비는 그 종별 이상에서 받은 치료만
                    if (Py.truthy(_t.get("hosp")) && !hosp_ok(_t.get("hosp"), tg.get("hosp"))) continue;
                    List<Object> evs = new ArrayList<>();
                    for (Object eo : Py.gl(sc, "itc_events")) {
                        List<Object> e = Py.L(eo);
                        // 사례 단계에 1-5종 표시(j)가 없는 수술은 사례의 1-5종 분류표 항목(tags.surg)으로 종을 정한다
                        Object eopt = Py.or(e.size() > 4 ? e.get(4) : null, new LinkedHashMap<String, Object>());
                        if (e.size() > 3 && Py.L(Py.or(e.get(3), new ArrayList<Object>())).contains("surg") && !Py.truthy(Py.get(eopt, "j"))) {
                            Object _j = surg5_grade(tg.get("surg"), kcd);
                            if (Py.isInt(_j) || _j instanceof Boolean) {
                                List<Object> e2 = new ArrayList<>(e.subList(0, Math.min(4, e.size())));
                                Map<String, Object> o2 = new LinkedHashMap<>(Py.M(eopt)); o2.put("j", _j);
                                e2.add(o2); e = e2;
                            }
                        }
                        evs.add(e);
                    }
                    // 6시간 이상 전신마취 단계(anes_h ≥ 6)면 「종합병원 전신마취치료(6시간이상)(급여)」 항목도 받은 것으로 본다
                    if (_acts(sc).contains("anes6") && hosp_ok("종합", tg.get("hosp")) && !_any_key(evs, "anes6")) {
                        evs.add(Py.list("치료", "전신마취(6시간이상)", "", Py.list("anes6")));
                    }
                    // 항목 한정 면책 — 질병 통합치료비 · 암전후 통합치료비는 아래 질병 치료의 전신마취(6시간이상) 항목만 지급하지 않는다
                    Set<Object> xk = new LinkedHashSet<>();
                    for (Map.Entry<String, Object> e : Py.M(Py.get(ITC_ITEM_X, rid, new LinkedHashMap<String, Object>())).entrySet()) {
                        if (code_hit(Py.L(Py.or(KCDG.get(e.getValue()), new ArrayList<Object>())), kcd)) xk.add(e.getKey());
                    }
                    if (!xk.isEmpty()) {
                        boolean any = false;
                        for (Object eo : evs) { List<Object> e = Py.L(eo); if (e.size() > 3 && _meet(new HashSet<>(Py.L(Py.or(e.get(3), new ArrayList<Object>()))), xk)) { any = true; break; } }
                        if (any) log("면책", n, Py.fmt("약관 항목 한정 면책 질병(%s) — 전신마취치료(6시간이상) 항목 제외", kcd));
                    }
                    // 「종합병원 중환자실치료」 항목은 종합병원 이상에서만
                    if (!hosp_ok("종합", tg.get("hosp"))) {
                        Object rm = Py.at(Engine.RM, rid);
                        boolean hasIcu = false;
                        if (!Engine.cover(rm, kcd).equals("no")) {
                            for (Object it : Py.L(Py.at(Engine.IT, Py.gs(rm, "ty")))) if ("icu".equals(Py.at(it, "k"))) { hasIcu = true; break; }
                            if (hasIcu && _any_key(evs, "icu"))
                                log("병원종별", n, Py.fmt("「종합병원 중환자실치료」 항목은 종합병원 이상에서만 지급 — 사례 병원(%s)이라 0", Py.or(tg.get("hosp"), "미지정")));
                        }
                        Set<Object> xk2 = new LinkedHashSet<>(xk); xk2.add("icu"); xk = xk2;
                    }
                    Map<String, Object> res;
                    try {
                        res = Engine.calc_rider(rid, Py.at(r, "man"), kcd, Py.dict("e", evs), Py.truthy(Py.get(sc, "within1y", false)), xk);
                    } catch (Py.KeyError ke) {
                        log("금액표없음", n, Py.fmt("가입금액 %s만원이 약관 지급금액표에 없어 계산 제외 (설계 금액 확인 필요)", Py.at(r, "man")));
                        continue;
                    }
                    List<Object> lines = Py.gl(res, "lines");
                    for (Object l : lines) {                    // 약관 수가코드 목록 밖의 검사 → 0원 + 사유
                        if ("def".equals(Py.get(l, "why")))
                            log("수가코드제외", n, Py.fmt("%s 0원 — %s", Engine.item_label(rid, Py.at(l, "i")), Py.or(Py.get(l, "nor"), "약관이 정한 수가코드에 해당하지 않음")));
                    }
                    if (Py.cmp(res.get("total"), 0L) > 0) {
                        List<Object> parts = new ArrayList<>(); List<Object> eas = new ArrayList<>();
                        List<Object> its = Py.L(Py.at(Engine.IT, Py.gs(Py.at(Engine.RM, rid), "ty")));
                        for (Object l : lines) {
                            if (Py.cmp(Py.at(l, "amt"), 0L) > 0) {
                                parts.add(Py.fmt("%s %s", Engine.item_label(rid, Py.at(l, "i")), Py.commaF(Py.at(l, "amt"), 0)));
                                if ("o".equals(Py.at(its.get((int) Py.lng(Py.at(l, "i"))), "p"))) eas.add(Py.at(l, "amt"));
                            }
                        }
                        String det = Py.join(" · ", parts);
                        Object ea = Py.sum(eas);
                        out.add(Py.dict("name", n, "amt", res.get("total"), "why", det + (Py.truthy(res.get("capped")) ? "  (연간 한도 적용)" : ""),
                                "group", "통합치료비", "no", r.get("no"), "freq", "year",
                                "each", Py.min2(ea, res.get("cap")), "rule", "itc", "itc", rid));
                    }
                    continue;
                }
                // 2) 통합생활지원비 — 산정특례 등록·치료 항목마다 월 단위 지급(가입금액 = 월간 한도)
                if (Py.truthy(ls_id(n))) {
                    Object[] ll = ls_lines(r, sc);
                    @SuppressWarnings("unchecked") List<Object[]> lines = (List<Object[]>) ll[0];
                    boolean capped = (Boolean) ll[1];
                    if (!lines.isEmpty()) {
                        List<Object> sps = new ArrayList<>(), all = new ArrayList<>(), ws = new ArrayList<>(), rest = new ArrayList<>();
                        for (Object[] l : lines) {
                            if ("산정특례".equals(l[2])) sps.add(l[1]); else rest.add(Py.list(l[0], l[1]));
                            all.add(l[1]);
                            ws.add(Py.fmt("%s %s", l[0], Py.commaF(l[1], 0)));
                        }
                        // 산정특례는 '등록당' 지급 — 한 사례에서 두 단계에 걸쳐 세지 않도록 따로 싣는다
                        out.add(Py.dict("name", n, "amt", Py.sum(all), "group", "통합생활지원비",
                                "why", Py.join(" · ", ws) + (capped ? "  (월간 한도 적용)" : ""),
                                "no", r.get("no"), "freq", "year", "rule", "ls_monthly",
                                "sp", Py.sum(sps), "ls_rest", rest));
                    }
                    continue;
                }
                // 3) 규칙표 판정
                Map<String, Object> rule = classify(nm);                          // nm = 세부보장 둥근 괄호 표기는 마스터 이름으로 바꾼 것
                if (rule == null) {
                    log("미분류", n, "규칙표에 해당 담보 유형이 없어 계산 제외 (rules.json 보강 필요)");
                    continue;
                }
                if ("itc_unknown".equals(rule.get("kind"))) {            // 금액표 미연동 통합치료비 — 정액 치료비로 오계산되지 않게 제외
                    if (!INJ_KNOWN.contains(nm) && !INJ_KNOWN.contains(noren(nm)))
                        log("금액표없음", n, "약관 지급금액표(product_data.json RIDERS)에 없는 통합치료비 — 계산 제외 (금액표 보강 필요)");
                    continue;
                }
                Map<String, Object> ropt = Py.M(Py.or(rule.get("opt"), new LinkedHashMap<String, Object>()));
                if ("skip".equals(rule.get("kind")) && Py.truthy(ropt.get("log"))) {
                    log("조건부", n, (String) ropt.get("log")); continue;   // 병기·상태 조건이 붙어 사례로 단정할 수 없는 담보
                }
                Handler h = HANDLER.get(rule.get("kind"));
                if (h == null) continue;                       // care·life·nonmed·skip = 사례 계산 대상 아님
                for (Object[] item : h.h(r, ropt, sc, nm, tokens(nm))) {
                    Object amt = item[0], why = item[1], grp = item[2], freq = item[3];
                    Map<String, Object> extra = item.length > 4 ? Py.M(item[4]) : new LinkedHashMap<>();   // 5번째 : 줄에 덧붙일 값(repeat = 두번째 해부터의 연간 금액)
                    if (Py.cmp(amt, 0L) > 0) {
                        if (Boolean.FALSE.equals(r.get("matched"))) {        // 설계서 담보가 특약 마스터에 없는데 규칙표로 지급 계산됨 — 근거를 남긴다
                            String note = (String) Py.or(Py.or(ropt.get("note"), rule.get("label")), "-");
                            int e = note.length();
                            while (e > 0 && ". ".indexOf(note.charAt(e - 1)) >= 0) e--;
                            log("마스터없음", n, Py.fmt("특약 마스터(약관 데이터 : %s)에 없는 담보인데 규칙표 %s 로 계산됨 — 근거 : %s. 해당 상품 약관으로 확인 필요",
                                    Py.orS(Py.join("·", DB_PRODUCTS), "db.json"), rule.get("id"), note.substring(0, e)));
                        }
                        Map<String, Object> line = Py.dict("name", n, "amt", amt, "why", why, "group", grp, "no", r.get("no"), "freq", freq, "rule", rule.get("id"));
                        line.putAll(extra);
                        out.add(line);
                    }
                }
            } catch (RuntimeException ex) {                          // 어떤 담보가 와도 생성이 중단되지 않게 한다
                log("오류", Py.str(Py.get(r, "name", "?")), Py.fmt("%s: %s", _pyExName(ex), _pyExMsg(ex)));
            }
        }
        return out;
    }
    private static boolean _any_key(List<Object> evs, String k) {
        for (Object eo : evs) { List<Object> e = Py.L(eo); if (e.size() > 3 && Py.L(Py.or(e.get(3), new ArrayList<Object>())).contains(k)) return true; }
        return false;
    }
    /** 파이썬 예외 이름에 가깝게 — 로그 글자(「오류」)용. 정상 자료에서는 나오지 않는다 */
    private static String _pyExName(RuntimeException ex) {
        if (ex instanceof Py.KeyError) return "KeyError";
        if (ex instanceof NullPointerException || ex instanceof ClassCastException || ex instanceof IllegalArgumentException) return "TypeError";
        if (ex instanceof IndexOutOfBoundsException) return "IndexError";
        if (ex instanceof NumberFormatException) return "ValueError";
        return ex.getClass().getSimpleName();
    }
    private static String _pyExMsg(RuntimeException ex) { return ex.getMessage() == null ? "" : ex.getMessage(); }

    public static Object total(List<Object> lines) {
        List<Object> a = new ArrayList<>();
        for (Object l : lines) a.add(Py.at(l, "amt"));
        return Py.sum(a);
    }
    /** mode: 'first' 최초 지급 / 'year' 반복(연간 1회) / 'each' 수술할 때마다 */
    public static Object total_by(List<Object> lines, String mode) {
        Object s = 0L;
        for (Object lo : lines) {
            Map<String, Object> l = Py.M(lo);
            if (mode.equals("first")) s = Py.add(s, Py.at(l, "amt"));
            else if (mode.equals("year")) s = Py.add(s, !"once".equals(l.get("freq")) ? Py.get(l, "repeat", Py.at(l, "amt")) : (Object) 0L);   // repeat = 두번째 해부터의 연간 금액
            else s = Py.add(s, Py.get(l, "each", "each".equals(l.get("freq")) ? Py.at(l, "amt") : (Object) 0L));
        }
        return s;
    }

    /** 설계 담보 전체를 규칙표에 대조한 결과 — 인계·운영 점검용 */
    public static Map<String, Object> audit(List<Object> riders) {
        Map<String, Object> by = new LinkedHashMap<>(); List<Object> un = new ArrayList<>();
        for (Object ro : riders) {
            Map<String, Object> r = Py.M(ro);
            if (Py.truthy(r.get("itc"))) {
                by.put("itc", Py.lng(Py.get(by, "itc", 0L)) + 1); continue;
            }
            Map<String, Object> rule = classify((String) Py.at(r, "name"));
            if (rule == null) {
                un.add(r.get("name")); by.put("미분류", Py.lng(Py.get(by, "미분류", 0L)) + 1);
            } else {
                String k = (String) rule.get("kind");
                by.put(k, Py.lng(Py.get(by, k, 0L)) + 1);
            }
        }
        return Py.dict("담보수", (long) riders.size(), "구조별", by, "미분류", un, "규칙수", (long) RULES.size(), "인식", recog(riders));
    }

    // ── 모듈을 읽을 때 한 번 하는 일(파이썬과 같은 차례) ─────────────────
    static {
        for (Object ro : RULES) {
            Map<String, Object> r = Py.M(ro);
            r.put("_m", Py.re(Py.gs(r, "m")));
            r.put("_x", Py.truthy(r.get("x")) ? Py.re(Py.gs(r, "x")) : null);
        }
        _g131_from_master();
        if (Py.exists(Py.path("surg7.json"))) for (Object r : Py.gl(Py.loadJson("surg7.json"), "rows")) SURG7.put(Py.gs(r, "code"), r);
        if (Py.exists(Py.path("surg_new.json"))) NEWSURG = Py.M(Py.loadJson("surg_new.json"));
        _NEWSURG_BASIC.addAll(Py.L(Py.or(NEWSURG.get("basic"), new ArrayList<Object>())));
        if (Py.exists(Py.path("surg5.json"))) for (Object i : Py.gl(Py.loadJson("surg5.json"), "items")) SURG5.put(Py.get(i, "no"), i);
        List<String> gt = new ArrayList<>();
        for (Object t : Py.gl(RULEDOC, "goji_tags")) gt.add(Py.escape((String) t));
        GOJI = "(?:\\((?:" + Py.join("|", gt) + ")\\)|\\([^()]{1,24}가입\\))";
        for (Object r : Engine.RIDERS) ITC_MAP.put(Py.gs(r, "nm"), Py.get(r, "id"));
        ITC_MAP.put("암 통합치료비(주요치료)(비급여(전액본인부담 포함))", "ca_ncm");
        ITC_MAP.put("특정순환계질환 통합치료비Ⅱ", "circ");
        for (Map.Entry<String, Object> e : ITC_MAP.entrySet()) _ITC_NORM.put(nname(e.getKey()), e.getValue());
        if (Py.exists(Py.path("life_support.json"))) LS = Py.M(Py.loadJson("life_support.json"));
        if (Py.exists(Py.path("inj_itc.json"))) for (String k : Py.M(Py.loadJson("inj_itc.json")).keySet()) INJ_KNOWN.add(nname(k));
        for (Map.Entry<String, Object> e : Py.gm(C13, "groups").entrySet()) _C13N.put(Py.sub("[\\s()·,]|전이포함", "", e.getKey()), e.getValue());
        for (Map.Entry<String, Object> e : Py.M(Py.or(C13.get("alias"), new LinkedHashMap<String, Object>())).entrySet()) {
            String k = Py.sub("[\\s()·,]|전이포함", "", e.getKey());
            if (!_C13N.containsKey(k)) _C13N.put(k, Py.at(Py.gm(C13, "groups"), e.getValue()));
        }
        HANDLER.put("dx", ScenEngine::h_dx);
        HANDLER.put("surg", ScenEngine::h_surg);
        HANDLER.put("day", ScenEngine::h_day);
        HANDLER.put("tx", ScenEngine::h_tx);
        HANDLER.put("point2", ScenEngine::h_point2);
    }
}
