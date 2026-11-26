package meai.sp;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * 파이썬 ga_spec.py — 스마트 제안서의 모든 칸을 자료로 적은 사양(CELLS) + 칸 값 계산(cell_value).
 * 숫자를 만들거나 추정하지 않는다 — 전부 ScenEngine.pay_lines 결과(또는 가입금액)를 그대로 적는다.
 * 튜플 (값, 지급 줄, 로그) 은 Object[]{값, List, List} 로 돌려준다.
 * 개발용 도구(run_universe · add_design_only · run_design · spec_dump 의 파일 쓰기)는 옮기지 않았다.
 */
public final class GaSpec {
    private GaSpec() {}

    public static String won(Object v) { return GaCare.won(v); }

    private static Map<String, Object> D(Object... kv) { return Py.dict(kv); }
    private static List<Object> A(Object... xs) { return Py.list(xs); }
    private static List<Object> plus(List<Object> a, Object... xs) { List<Object> o = new ArrayList<>(a); for (Object x : xs) o.add(x); return o; }

    public static final Map<String, Object> BASE_T = D("cause", "질병", "hosp", "상급종합", "room", null, "days", 0L, "grp", new ArrayList<Object>(), "dx", null);
    public static final List<Object> BG = A("뇌혈관질환"), HG = A("심장질환");

    /** sc(kcd, ev, **kw) */
    public static Map<String, Object> sc(String kcd, List<Object> ev, Map<String, Object> kw) {
        Map<String, Object> tg = new LinkedHashMap<>(BASE_T);
        if (kw != null) tg.putAll(kw);
        return D("kcd", kcd, "tags", tg, "itc_events", Py.deepcopy(ev != null && !ev.isEmpty() ? ev : new ArrayList<Object>()));
    }
    public static Map<String, Object> sc(String kcd, List<Object> ev, Object... kw) { return sc(kcd, ev, Py.dict(kw)); }
    public static Map<String, Object> sc_dx(String kcd, String fam) { return sc_dx(kcd, fam, null); }
    public static Map<String, Object> sc_dx(String kcd, String fam, List<Object> grp) {
        return D("kcd", kcd, "tags", D("dx", fam, "cause", "질병", "grp", new ArrayList<Object>(grp != null ? grp : new ArrayList<Object>())), "itc_events", new ArrayList<Object>());
    }
    /** sc_itc(kcd, key, hosp='상급종합', grp=None, fam=None, extra=None) */
    public static Map<String, Object> sc_itc(String kcd, String key, String hosp, List<Object> grp, String fam, Map<String, Object> extra) {
        Map<String, Object> tg = D("cause", "질병", "hosp", hosp, "room", null, "days", 0L, "grp", new ArrayList<Object>(grp != null ? grp : new ArrayList<Object>()), "dx", fam);
        List<Object> e = A("치료", key, "", A(key));
        if (Py.truthy(extra)) e.add(extra);
        return D("kcd", kcd, "tags", tg, "itc_events", A(e));
    }
    private static Map<String, Object> sc_itc(String kcd, String key, List<Object> grp, String fam, Map<String, Object> extra) { return sc_itc(kcd, key, "상급종합", grp, fam, extra); }

    // ── 주요수술보장 12칸 — 이름 → {시술명, 질병코드, 사례 조건(Map), 통합치료비 사건(List)} ──
    public static final Map<String, Object[]> GA_DZ = new LinkedHashMap<>();
    static {
        GA_DZ.put("백내장", new Object[]{"인공수정체 삽입", "H25.9", D("surg", "71", "surg7", "C061", "grp", A("백내장"), "adm", "out"), A(A("수술", "수정체 유화술", "", A("surg"), D("j", 1L)))});
        GA_DZ.put("디스크", new Object[]{"디스크절제술", "M51", D("surg", "9", "surg7", "B174", "grp", A("다빈도62대질병"), "anes", 1L), A(A("수술", "추간판 절제술", "", A("surg"), D("j", 3L)))});
        GA_DZ.put("무릎관절질환", new Object[]{"인공관절치환술", "M17", D("surg", "13-2", "surg7", "I032", "grp", A("관절염,생식기질환"), "anes", 1L), A(A("수술", "슬관절 전치환술", "", A("surg", "arthroplasty"), D("j", 2L)))});
        GA_DZ.put("담석증", new Object[]{"담낭절제술", "K80.0", D("surg", "36", "surg7", "H107", "grp", A("다빈도62대질병"), "anes", 1L), A(A("수술", "복강경 담낭 절제", "", A("surg"), D("j", 2L)))});
        GA_DZ.put("맹장염", new Object[]{"충수절제술", "K35", D("surg", "41", "surg7", "G212", "grp", A(), "anes", 1L), A(A("수술", "충수 절제", "", A("surg"), D("j", 2L)))});
        GA_DZ.put("갑상선결절", new Object[]{"고주파절제술", "D34", D("surg", "88-2", "surg7", "K080", "hc", A("PZ612"), "grp", A("다빈도62대질병"), "adm", "out"), A(A("수술", "고주파절제술", "", A("surg"), D("j", 2L)))});
        GA_DZ.put("유방양성종양", new Object[]{"맘모톰", "D24", D("surg", "4", "surg7", "J071", "grp", A("유방의장애"), "adm", "out"), A(A("수술", "맘모톰", "", A("surg", "vab"), D("j", 1L)))});
        GA_DZ.put("자궁근종", new Object[]{"복강경 수술", "D25.9", D("surg", "52", "surg7", "N031", "hc", A("R4128", "R4129"), "grp", A("다빈도62대질병"), "anes", 1L), A(A("수술", "복강경 근종절제술", "", A("surg"), D("j", 2L)))});
        GA_DZ.put("전립선비대증", new Object[]{"경요도 전립선절제술", "N40", D("surg", "88-3", "surg7", "M022", "grp", A("관절염,생식기질환")), A(A("수술", "경요도 전립선절제술", "", A("surg"), D("j", 1L)))});
        GA_DZ.put("치질", new Object[]{"치핵절제술", "K64", D("surg", "44", "surg7", "G271", "grp", A(), "anes", 1L), A(A("수술", "치핵 절제술", "", A("surg"), D("j", 1L)))});
        GA_DZ.put("요로결석", new Object[]{"체외충격파쇄석술", "N20.0", D("surg", "87", "surg7", "L092", "hc", A("R3504", "R3505", "R3506", "R3507", "R3508"), "grp", A(), "adm", "out"), A(A("수술", "체외충격파쇄석술", "", A("surg"), D("j", 2L)))});
        GA_DZ.put("골절진단", new Object[]{"골절수술", "S52.5", D("cause", "상해", "surg", "13-2", "surg7", "I286", "hc", A("N1601"), "grp", A()), A(A("수술", "골절 고정술", "", A("surg"), D("j", 2L)))});
    }
    public static final List<String> DZ_ORDER = new ArrayList<>(GA_DZ.keySet());
    public static Map<String, Object> sc_dz(String name, String hosp) {
        Object[] g = GA_DZ.get(name);
        Map<String, Object> kw = new LinkedHashMap<>(Py.M(g[2]));
        kw.put("hosp", hosp);
        return sc((String) g[1], Py.L(g[3]), kw);
    }

    // ── 암 사례 ──
    public static final Map<String, Object> CS = new LinkedHashMap<>();
    static {
        CS.put("robot", sc("C16", A(A("수술", "로봇수술", "", A("surg", "robot"), D("nc", 1L))), "surg", "C1", "surg7", "G081"));
        CS.put("lap", sc("C16", A(A("수술", "복강경", "", A("surg"))), "surg", "C1", "surg7", "G081"));
        CS.put("open", sc("C16", A(A("수술", "개복", "", A("surg"))), "surg", "C1", "surg7", "G082"));
        CS.put("endo", sc("C16", A(A("수술", "내시경 절제", "", A("surg"))), "surg", "C2", "surg7", "G503"));
        CS.put("chemo", sc("C16", A(A("항암", "항암약물(급여)", "", A("chemo"))), "chemo", 1L));
        CS.put("target1", sc("C16", A(A("항암", "표적(비급여)", "", A("chemo", "target"), D("nc", 1L))), "chemo", 1L, "target", 1L, "drug", 1L));
        CS.put("immune1", sc("C16", A(A("항암", "면역(비급여)", "", A("chemo", "immune"), D("nc", 1L))), "chemo", 1L, "target", 1L, "drug", 1L));
        CS.put("two", sc("C16", A(A("항암", "표적+면역(비급여) 2종", "", A("chemo", "target", "immune"), D("nc", 1L))), "chemo", 1L, "target", 1L, "drug", 2L));
        CS.put("two3", sc("C16", A(A("항암", "표적+면역(비급여) 3종", "", A("chemo", "target", "immune"), D("nc", 1L))), "chemo", 1L, "target", 1L, "drug", 3L));
        CS.put("rad", sc("C16", A(A("방사선", "항암방사선(급여)", "", A("rad")))));
        CS.put("imrt", sc("C16", A(A("방사선", "세기조절", "", A("rad", "imrt")))));
        CS.put("proton", sc("C16", A(A("방사선", "양성자(비급여)", "", A("rad", "proton"), D("nc", 1L)))));
        CS.put("carbon", sc("C16", A(A("방사선", "중입자(비급여)", "", A("rad", "carbon"), D("nc", 1L)))));
    }
    private static Map<String, Object> cs(String k) { return Py.M(CS.get(k)); }
    public static final Map<String, Object> DXS = D("일반암", sc_dx("C16", "cancer"), "유사암", sc_dx("C73", "sim_cancer"), "전이암", sc_dx("C78.7", "cancer"));
    public static final Map<String, Object> BDX = D("뇌졸중", sc_dx("I63", "brain", BG), "뇌혈관", sc_dx("I67.1", "brain", BG));
    public static final Map<String, Object> HDX = D("허혈성심장", sc_dx("I20", "heart", plus(HG, "허혈성심장질환")), "급성심근경색", sc_dx("I21", "heart", plus(HG, "허혈성심장질환")));

    /** [(이름, 사례), …] — Object[]{String, Map} */
    public static List<Object[]> brain_steps(String hosp) {
        List<Object[]> o = new ArrayList<>();
        o.add(new Object[]{"혈전용해치료", sc("I63", A(A("시술", "혈전용해", "", A("thromb"))), "series", "brain", "hosp", hosp)});
        o.add(new Object[]{"혈전용해+혈전제거술", sc("I63", A(A("시술", "혈전용해", "", A("thromb")), A("시술", "혈전제거술", "", A("surg"))), "surg", "88-1", "surg7", "B027", "grp", plus(BG, "뇌졸중", "특정31대질병"), "hosp", hosp, "acts", A("thrombectomy"))});
        o.add(new Object[]{"코일색전술", sc("I67.1", A(A("시술", "코일 색전술", "", A("surg"))), "surg", "88-1", "surg7", "B016", "grp", plus(BG, "특정31대질병"), "hosp", hosp, "anes", 1L)});
        o.add(new Object[]{"개두 수술", sc("I61", A(A("수술", "혈종제거 개두술", "", A("surg"))), "surg", "59", "surg7", "B031", "grp", plus(BG, "뇌졸중", "뇌출혈", "특정31대질병"), "hosp", hosp, "anes", 1L)});
        return o;
    }
    public static List<Object[]> heart_steps(String hosp) {
        List<Object[]> o = new ArrayList<>();
        o.add(new Object[]{"혈전용해치료", sc("I21", A(A("시술", "혈전용해", "", A("thromb"))), "series", "heart", "hosp", hosp)});
        o.add(new Object[]{"혈전용해+혈전제거술", sc("I21", A(A("시술", "혈전용해", "", A("thromb")), A("시술", "혈전제거술", "", A("surg"))), "surg", "88-1", "surg7", "F121", "grp", plus(HG, "허혈성심장질환", "특정31대질병"), "hosp", hosp, "acts", A("thrombectomy"))});
        o.add(new Object[]{"스텐트삽입술", sc("I20", A(A("시술", "스텐트 삽입", "", A("surg"))), "surg", "88-1", "surg7", "F133", "grp", plus(HG, "허혈성심장질환", "특정31대질병"), "hosp", hosp)});
        o.add(new Object[]{"개흉 수술", sc("I20", A(A("수술", "관상동맥 우회술", "", A("surg"))), "surg", "24", "surg7", "F042", "grp", plus(HG, "허혈성심장질환", "특정31대질병"), "hosp", hosp, "anes", 1L, "anes_h", 6L)});
        return o;
    }
    public static final List<Object[]> _b = brain_steps("상급종합"), _h = heart_steps("상급종합");
    public static final Map<String, Object> _b_thrombectomy = sc("I63", A(A("시술", "혈전제거술", "", A("surg"))), "surg", "88-1", "surg7", "B027", "grp", plus(BG, "뇌졸중", "특정31대질병"), "hosp", "상급종합", "acts", A("thrombectomy"));
    public static final Map<String, Object> _b_stent = sc("I65.2", A(A("시술", "스텐트 삽입", "", A("surg"))), "surg", "88-1", "surg7", "B026", "grp", plus(BG, "뇌졸중", "특정31대질병"), "hosp", "상급종합");
    public static final Map<String, Object> _h_thrombectomy = sc("I21", A(A("시술", "혈전제거술", "", A("surg"))), "surg", "88-1", "surg7", "F121", "grp", plus(HG, "허혈성심장질환", "특정31대질병"), "hosp", "상급종합", "acts", A("thrombectomy"));
    public static final List<Object[]> P1_TX_B = new ArrayList<>(), P1_TX_H = new ArrayList<>();
    static {
        P1_TX_B.add(new Object[]{"혈전용해", _b.get(0)[1]}); P1_TX_B.add(new Object[]{"혈전제거", _b_thrombectomy}); P1_TX_B.add(new Object[]{"혈전용해+혈전제거", _b.get(1)[1]});
        P1_TX_B.add(new Object[]{"코일색전술", _b.get(2)[1]}); P1_TX_B.add(new Object[]{"개두수술", _b.get(3)[1]});
        P1_TX_H.add(new Object[]{"혈전용해", _h.get(0)[1]}); P1_TX_H.add(new Object[]{"혈전제거", _h_thrombectomy}); P1_TX_H.add(new Object[]{"혈전용해+혈전제거", _h.get(1)[1]});
        P1_TX_H.add(new Object[]{"스텐트삽입술", _h.get(2)[1]}); P1_TX_H.add(new Object[]{"개흉수술", _h.get(3)[1]});
    }
    public static final String[][] SEV = {{"중환자실치료", "icu"}, {"부분체외순환", "ecmo"}, {"CRRT(지속적신대체요법)", "crrt"}, {"인공호흡기", "vent"}, {"저체온요법", "hypo"}};
    public static final String[][] EX_CA = {{"내시경", "x_endo"}, {"MRI촬영", "x_mri"}, {"PET(양전자단층촬영)", "x_pet"}, {"특정단일유전자", "x_gene"}, {"초음파", "x_us"}, {"CT촬영", "x_ct"}, {"특정생검조직", "x_bio"}, {"특정NGS유전자", "x_ngs"}};
    public static final String[][] EX_BH = {{"MRI 촬영", "x_mri"}, {"PET(양전자단층촬영)", "x_pet"}, {"CT 촬영", "x_ct"}};

    // ═══════════════ 칸 목록 (렌더 순서) ═══════════════
    public static final List<Object> CELLS = new ArrayList<>();
    public static final Map<String, Object> KEY = new LinkedHashMap<>();
    /** add(key, page, section, row, col, kind, sc_=None, mode='first', need=None, direct=None, note='', sc_name='', na_if_empty=False) */
    public static void add(String key, long page, String section, String row, String col, String kind, Map<String, Object> sc_, String mode, List<Object> need, Object direct, String note, String sc_name, boolean na_if_empty) {
        int cnt = 0;
        for (Object x : CELLS) if (Py.lng(Py.M(x).get("page")) == page) cnt++;
        Map<String, Object> c = D("id", Py.fmt("P%d-%03d", page, cnt + 1), "key", key, "page", page, "section", section, "row", row, "col", col,
                "label", Py.truthy(row) ? Py.fmt("%s · %s", row, col) : col, "kind", kind, "sc", sc_, "sc_name", sc_name, "mode", mode, "need", need, "direct", direct, "note", note, "na_if_empty", na_if_empty);
        if (KEY.containsKey(key)) throw new IllegalStateException(key);
        CELLS.add(c); KEY.put(key, c);
    }
    private static void eng(String key, long page, String section, String row, String col, Map<String, Object> sc_, String mode, List<Object> need, String sc_name, boolean na, String note) {
        add(key, page, section, row, col, "engine", sc_, mode, need, null, note, sc_name, na);
    }
    private static void care(String key, String col, String row, String direct, String note) { add(key, 1, "간병인보장", row, col, "care", null, "first", null, direct, note, "", false); }

    /** 1쪽 열 묶음 — {머리, [ {칸 이름, 열쇠, 사례, 집계, need, 사례 설명}, … ]} */
    public static final List<Object[]> _ca1 = new ArrayList<>(), _bh1 = new ArrayList<>();
    private static Object[] it(String n, String k, Object s_, String md, List<Object> need, String nm) { return new Object[]{n, k, s_, md, need, nm}; }
    private static List<Object[]> its(Object[]... xs) { List<Object[]> o = new ArrayList<>(); for (Object[] x : xs) o.add(x); return o; }
    public static final String[][] SG = {{"내시경수술", "endo"}, {"개복·개흉", "open"}, {"복강경·흉강경", "lap"}, {"다빈치로봇암수술", "robot"}};
    public static final String[][] ROWS3 = {{"최초 지급시", "first"}, {"반복(연 1회)", "year"}, {"수술할 때마다", "each"}};
    public static final String[][] CM = {{"화학항암", "chemo"}, {"표적항암", "target1"}, {"면역항암(카티포함)", "immune1"}};
    public static final String[][] RD = {{"항암방사선", "rad"}, {"세기조절", "imrt"}, {"양성자", "proton"}, {"중입자", "carbon"}};

    @SuppressWarnings("unchecked")
    private static void cols(List<Object[]> groups, int rowsN, String prefix, String section) {
        for (int i = 0; i < rowsN; i++) {
            for (Object[] g : groups) {
                String h = (String) g[0];
                List<Object[]> items = (List<Object[]>) g[1];
                if (i >= items.size()) continue;
                Object[] x = items.get(i);
                eng(prefix + x[1], 1, section, h, (String) x[0], Py.M(x[2]), (String) x[3], Py.L(x[4]), (String) x[5], h.equals("진단금"), "");
            }
        }
    }

    static {
        // ── 1쪽 보장요약 ──
        _ca1.add(new Object[]{"진단금", its(it("일반암", "dx.일반암", DXS.get("일반암"), "first", null, "일반암 진단(C16 위암)"),
                it("유사암", "dx.유사암", DXS.get("유사암"), "first", null, "유사암 진단(C73 갑상선암)"),
                it("전이암", "dx.전이암", DXS.get("전이암"), "meta_only", A("전이암", "진단"), "전이암 진단(C78.7 간 전이) — 담보명에 「전이암」이 든 진단비 줄만 · 일반암 진단비는 원발암에서 이미 받은 것으로 보고 제외"))});
        _ca1.add(new Object[]{"수술", its(it("내시경", "sg.endo", cs("endo"), "first", null, "위암 내시경 절제"), it("개복/개흉", "sg.open", cs("open"), "first", null, "위암 개복수술"),
                it("복강경/흉강경", "sg.lap", cs("lap"), "first", null, "위암 복강경수술"), it("로봇암수술", "sg.robot", cs("robot"), "first", null, "위암 다빈치로봇수술(비급여)"))});
        _ca1.add(new Object[]{"항암약물", its(it("화학항암", "cm.chemo", cs("chemo"), "first", null, "위암 항암약물(급여)"), it("표적항암", "cm.target1", cs("target1"), "first", null, "위암 표적항암(비급여, 약물 1종)"),
                it("면역항암", "cm.immune1", cs("immune1"), "first", null, "위암 면역항암(비급여, 약물 1종)"),
                it("표적(면역) 2가지 약물", "cm.two", cs("two"), "first", null, "위암 표적+면역항암(비급여) 약물 2종 — 항암약물·항암방사선약물·표적·면역·암통합치료비(면역항암 가정)·(2종이상)·(2종및3종이상) 담보 합산, 3종이상 담보 제외"))});
        _ca1.add(new Object[]{"항암방사선", its(it("항암방사선", "rd.rad", cs("rad"), "first", null, "위암 항암방사선(급여)"), it("세기조절", "rd.imrt", cs("imrt"), "first", null, "위암 세기조절방사선"),
                it("양성자", "rd.proton", cs("proton"), "first", null, "위암 양성자(비급여)"), it("중입자", "rd.carbon", cs("carbon"), "first", null, "위암 중입자(비급여)"))});
        cols(_ca1, 4, "p1.ca.", "암보장");

        _bh1.add(new Object[]{"진단금", its(it("뇌졸중", "dx.뇌졸중", BDX.get("뇌졸중"), "first", null, "뇌졸중 진단(I63 뇌경색)"),
                it("뇌혈관", "dx.뇌혈관", BDX.get("뇌혈관"), "first", null, "뇌혈관질환 진단(I67.1 비파열 뇌동맥류 · 뇌졸중이 아닌 뇌혈관질환)"),
                it("급성심근경색", "dx.급성심근경색", HDX.get("급성심근경색"), "first", null, "급성심근경색 진단(I21)"), it("허혈성심장", "dx.허혈성심장", HDX.get("허혈성심장"), "first", null, "허혈성심장질환 진단(I20 협심증)"))});
        List<Object[]> tb = new ArrayList<>(), th = new ArrayList<>(), sv = new ArrayList<>();
        for (Object[] x : P1_TX_B) tb.add(it((String) x[0], "txb." + x[0], x[1], "first", null, "뇌 · " + x[0] + " · 상급종합병원"));
        for (Object[] x : P1_TX_H) th.add(it((String) x[0], "txh." + x[0], x[1], "first", null, "심장 · " + x[0] + " · 상급종합병원"));
        for (String[] x : SEV) sv.add(it(x[0], "sev." + x[1], sc_itc("I63", x[1], BG, null, null), "itc_only", null, Py.fmt("뇌경색(I63) %s · 상급종합병원 · 통합치료비 항목만", x[0])));
        _bh1.add(new Object[]{"뇌 치료 및 수술", tb});
        _bh1.add(new Object[]{"심장 치료 및 수술", th});
        _bh1.add(new Object[]{"중증치료", sv});
        cols(_bh1, 5, "p1.bh.", "뇌·심보장");

        for (String n : DZ_ORDER) {
            Object[] g = GA_DZ.get(n);
            String nm = n.equals("골절진단") ? "골절진단 골절수술 — 손목 골절(S52.5 상해) 진단 후 고정술(1-5종 2종) · 병원급 · 골절진단비·상해수술비·골절수술비·1-5종·상해 통합치료비(2종수술 항목) 합산"
                    : Py.fmt("%s %s (%s) · %s", n, g[0], g[1], "out".equals(Py.M(g[2]).get("adm")) ? "통원 시술 가정" : "병원급");
            eng("p1.dz." + n, 1, "주요수술보장", n, (String) g[0], sc_dz(n, "병원"), "first", null, nm, false, "");
        }
        care("p1.care.hosp", "병·의원(요양병원제외)", "간병인지원(현물지원)", "hosp", "「간병인지원 질병입원일당(1일이상 180일한도)」 가입 → 간병인 보내줌 · 없으면 미가입(181일이상만 가입해도 미가입 · GA 결정 2026-10-08)");
        care("p1.care.nh", "요양병원", "간병인지원(현물지원)", "nh", "「간병인지원 요양성특정질병입원일당(…)(요양병원)」 또는 「간병인지원 질병입원일당(1일이상 180일한도)」 가입 → 간병인 보내줌 · 둘 다 없으면 미가입(소유자 2026-10-08)");
        care("p1.care.nurse", "간호간병통합서비스 1일", "간병인지원(현물지원)", "nurse", "「간병인지원 질병입원일당(간호·간병통합서비스 사용추가보장)」 가입금액 + 간병인 미사용 시 입원일당(Ⅰ 가입금액 · Ⅶ 5천원 · Ⅵ 0)");
        care("p1.care.unused", "미사용시 1일", "간병인지원(현물지원)", "unused", "간병인지원 질병입원일당 담보의 설계서 금액(Ⅰ 가입금액 · Ⅶ 「또는 5천원」 · Ⅵ 금액 없음 → 0)");
        care("p1.care.use_gen", "병원,의원(요양병원제외) 1일", "간병인사용(금액지원)", "use_gen", "「간병인사용 질병입원일당」(요양병원 전용·간호간병 제외) 1일이상 담보 가입금액 합");
        care("p1.care.use_nh", "요양병원 1일", "간병인사용(금액지원)", "use_nh", "「간병인사용 질병입원일당(…)(요양병원)」 가입금액");
        care("p1.care.use_nurse", "간호간병통합서비스 1일", "간병인사용(금액지원)", "use_nurse", "「간호·간병통합서비스 사용 질병입원일당」(단독 특약) 가입금액");

        // ── 2쪽 암보장 ──
        for (String[] x : EX_CA) eng("p2.ex." + x[1], 2, "암검사(8종)", "", x[0], sc_itc("C16", x[1], null, "cancer", null), "itc_only", null, Py.fmt("위암(C16) %s · 상급종합병원 · 통합치료비 항목만", x[0]), false, "");
        eng("p2.dx.일반암", 2, "암진단", "", "일반암", Py.M(DXS.get("일반암")), "first", null, "일반암 진단(C16)", true, "");
        eng("p2.dx.유사암", 2, "암진단", "", "유사암", Py.M(DXS.get("유사암")), "first", null, "유사암 진단(C73)", true, "");
        eng("p2.dx.전이암", 2, "암진단", "", "전이암", Py.M(DXS.get("전이암")), "meta_only", A("전이암", "진단"), "전이암 진단(C78.7) · 전이암 담보 줄만", false, "");
        for (String[] r : ROWS3) for (String[] x : SG) eng(Py.fmt("p2.sg.%s.%s", x[1], r[1]), 2, "암수술", r[0], x[0], cs(x[1]), r[1], null, Py.fmt("위암 %s", x[0]), false, "");
        for (int ri = 0; ri < 2; ri++) {
            String[] r = ROWS3[ri];
            for (String[] x : CM) eng(Py.fmt("p2.cm.%s.%s", x[1], r[1]), 2, "항암약물치료", r[0], x[0], cs(x[1]), r[1], null, Py.fmt("위암 %s(약물 1종)", x[0]), false, "");
            if (r[1].equals("first")) eng("p2.cm.two", 2, "항암약물치료", "표적(면역) 개수별", "2가지약물", cs("two"), "first", null, "위암 표적+면역항암(비급여) 약물 2종 — 보장요약 「표적(면역) 2가지 약물」 칸과 같은 사례", false, "");
            else eng("p2.cm.two3", 2, "항암약물치료", "표적(면역) 개수별", "3가지약물", cs("two3"), "first", null, "위암 표적+면역항암(비급여) 약물 3종 — (3종이상)·(2종및3종이상 3종 구분) 담보까지", false, "");
        }
        for (int ri = 0; ri < 2; ri++) {
            String[] r = ROWS3[ri];
            for (String[] x : RD) eng(Py.fmt("p2.rd.%s.%s", x[1], r[1]), 2, "항암방사선치료", r[0], x[0], cs(x[1]), r[1], null, Py.fmt("위암 %s", x[0]), false, "");
        }
        eng("p2.rh.in", 2, "암재활치료", "연 20회", "입원 재활", sc_itc("C16", "rehab", null, "cancer", D("n", 1L)), "itc_only", null, "위암 재활치료 1회(회당 금액) · 상급종합 · 통합치료비 항목만 — 연 20회 한도는 줄 제목에만(소유자 2026-11-03 : 합산액이 아니라 회당 금액)", false, "");
        eng("p2.rh.out", 2, "암재활치료", "연 20회", "외래 재활", sc_itc("C16", "rehab", null, "cancer", D("n", 1L)), "itc_only", null, "(입원 칸과 같은 값)", false, "입원·외래 구분 없이 같은 사례 값");
        add("p2.dis", 2, "암후유장해", "", "3-100% 암후유장해", "direct", null, "first", null, D("keys", A("암", "후유장해"), "exclude", A("재활자금")),
                "담보명(세트 특약은 세부보장 이름)에 '암'과 '후유장해'가 모두 들어간 담보의 가입금액 합 — 계산 아님. 「…후유장해재활자금」 은 다른 보장이라 뺀다(v9.07)", "", false);

        // ── 3쪽 뇌·심보장 ──
        for (String[] x : EX_BH) eng("p3.ex." + x[1], 3, "뇌·심검사(3종)", "", x[0], sc_itc("I63", x[1], BG, null, null), "itc_only", null, Py.fmt("뇌경색(I63) %s · 상급종합 · 통합치료비 항목만", x[0]), false, "");
        eng("p3.dx.뇌혈관", 3, "뇌·심진단", "", "뇌혈관", Py.M(BDX.get("뇌혈관")), "first", null, "뇌혈관질환 진단(I67.1)", true, "");
        eng("p3.dx.뇌졸중", 3, "뇌·심진단", "", "뇌졸중", Py.M(BDX.get("뇌졸중")), "first", null, "뇌졸중 진단(I63)", true, "");
        eng("p3.dx.허혈성심장", 3, "뇌·심진단", "", "허혈성심장", Py.M(HDX.get("허혈성심장")), "first", null, "허혈성심장질환 진단(I20)", true, "");
        for (String[] r : ROWS3) {
            List<Object[]> st = brain_steps("상급종합");
            for (int i = 0; i < st.size(); i++) eng(Py.fmt("p3.b%d.%s", i, r[1]), 3, "뇌질환 치료 및 수술", r[0], (String) st.get(i)[0], Py.M(st.get(i)[1]), r[1], null, Py.fmt("%s · 뇌 · 상급종합", st.get(i)[0]), false, "");
        }
        for (String[] r : ROWS3) {
            List<Object[]> st = heart_steps("상급종합");
            for (int i = 0; i < st.size(); i++) eng(Py.fmt("p3.h%d.%s", i, r[1]), 3, "심질환 치료 및 수술", r[0], (String) st.get(i)[0], Py.M(st.get(i)[1]), r[1], null, Py.fmt("%s · 심장 · 상급종합", st.get(i)[0]), false, "");
        }
        for (String[] x : SEV) eng("p3.sev." + x[1], 3, "뇌·심 중증치료", "반복(연 1회)", x[0], sc_itc("I63", x[1], BG, null, null), "itc_only", null, Py.fmt("뇌경색(I63) %s · 상급종합 · 통합치료비 항목(연간)", x[0]), false, "");
        eng("p3.rh.in", 3, "뇌·심 재활치료", "연 15회", "입원 재활", sc_itc("I63", "rehab", BG, null, D("n", 1L)), "itc_only", null, "뇌경색 재활 1회(회당 금액) · 상급종합 · 통합치료비 항목만 — 연 15회 한도는 줄 제목에만(소유자 2026-11-03)", false, "");
        eng("p3.rh.out", 3, "뇌·심 재활치료", "연 15회", "외래 재활", sc_itc("I63", "rehab", BG, null, D("n", 1L)), "itc_only", null, "(입원 칸과 같은 값)", false, "");
    }

    // ═══════════════ 계산 ═══════════════
    /** 담보명에서 「무슨 보장인지」 를 말하는 부분 — 세트 특약의 세부보장 줄은 대괄호 안(세부보장 이름)으로 본다 */
    public static String _sub_label(String name) {
        String n = Py.strip(Py.sub("\\((?:[^()]{0,30}가입)\\)|\\[기본계약\\]", "", name == null ? "" : name));
        if (!n.endsWith("]")) return n;
        int d = 0;
        for (int i = n.length() - 1; i >= 0; i--) {
            char c = n.charAt(i);
            if (c == ']') d++;
            else if (c == '[') {
                d--;
                if (d == 0) {
                    String inner = Py.slice(n, i + 1, -1);
                    return inner.endsWith("]") ? _sub_label(inner) : inner;
                }
            }
        }
        return n;
    }

    private static final IdentityHashMap<List<Object>, Map<String, Object[]>> _CACHE = new IdentityHashMap<>();
    public static void clear_cache() { _CACHE.clear(); }
    /** 같은 사례는 한 설계 안에서 한 번만 계산한다. 반환 Object[]{지급 줄 List, 이 호출로 쌓인 로그 List} */
    public static Object[] pay(List<Object> riders, Map<String, Object> s_) {
        String k = Json.dumps(s_, false, null, ", ", ": ", true);
        Map<String, Object[]> m = _CACHE.get(riders);
        if (m == null) { m = new java.util.HashMap<>(); _CACHE.put(riders, m); }
        Object[] hit = m.get(k);
        if (hit != null) return hit;
        int n0 = ScenEngine.ISSUES.size();
        List<Object> L = ScenEngine.pay_lines(riders, Py.M(Py.deepcopy(s_)));
        Object[] v = new Object[]{L, new ArrayList<>(ScenEngine.ISSUES.subList(n0, ScenEngine.ISSUES.size()))};
        m.put(k, v);
        return v;
    }

    public static String _ns(Object x) { return Py.sub("\\s+", "", Py.truthy(x) ? (String) x : ""); }
    /** 이 지급 줄이 칸의 집계 방식(mode)에 들어가는 금액 — 수 꼴(Long/Double)은 줄의 것 그대로, 안 들어가면 0(Long) */
    public static Object counts(Map<String, Object> l, String mode) {
        final Object ZERO = 0L;
        switch (mode) {
            case "first": return l.get("amt");
            case "year": return !"once".equals(l.get("freq")) ? (l.get("repeat") != null ? l.get("repeat") : l.get("amt")) : ZERO;
            case "each": return l.containsKey("each") ? l.get("each") : ("each".equals(l.get("freq")) ? l.get("amt") : ZERO);
            case "itc_only": return "통합치료비".equals(l.get("group")) ? l.get("amt") : ZERO;
            case "ms_only": return "ms".equals(l.get("itc")) ? l.get("amt") : ZERO;
            case "meta_only": { String n = _ns(l.get("name")); return (n.contains("전이암") && n.contains("진단")) ? l.get("amt") : ZERO; }
            case "reg_only": return "dx_special_case".equals(l.get("rule")) ? l.get("amt") : ZERO;
            default: return ZERO;
        }
    }

    // 상해 통합치료비(실속형) — 엔진(pay_lines)은 이 특약을 계산하지 않고 inj_itc.json 금액표로 따로 더한다
    public static final Map<String, Object> INJ_ITC = Py.M(Py.loadJson("inj_itc.json"));
    public static final Map<String, Object> INJ_ACT = D("MRI", "x_mri", "CT", "x_ct", "골밀도", "x_bmd", "흡인", "aspir", "신경차단", "block", "화상처치", "burn", "도수정복", "reduction",
            "창상봉합술치료(안면부,", "suture_face", "창상봉합술치료(안면부이외", "suture", "깁스", "cast", "부목", "splint", "CRRT", "crrt",
            "인공호흡기", "vent", "저체온", "hypo", "체외순환", "ecmo", "전신마취", "anes6", "중환자실", "icu");
    /** 반환 Object[]{지급 줄 List, 로그 List} */
    public static Object[] inj_lines(List<Object> riders, Map<String, Object> s_) {
        List<Object> out = new ArrayList<>(), iss = new ArrayList<>();
        Object tg = s_.get("tags");
        if (!"상해".equals(Py.get(Py.truthy(tg) ? tg : null, "cause"))) return new Object[]{out, iss};
        List<Object> ev = Py.truthy(s_.get("itc_events")) ? Py.gl(s_, "itc_events") : new ArrayList<>();
        Set<Object> acts = new HashSet<>();
        Set<Long> js = new HashSet<>();
        for (Object e0 : ev) {
            List<Object> e = Py.L(e0);
            if (e.size() > 3) acts.addAll(Py.L(e.get(3)));
            if (e.size() > 4 && e.get(4) instanceof Map && Py.truthy(Py.M(e.get(4)).get("j"))) js.add(Py.toInt(Py.M(e.get(4)).get("j")));
        }
        for (Object r0 : riders) {
            Map<String, Object> r = Py.M(r0);
            String rn = (String) r.get("name");
            for (Map.Entry<String, Object> ke : INJ_ITC.entrySet()) {
                String kn = ScenEngine.nname(ke.getKey());
                if (!(kn.equals(ScenEngine.nname(rn)) || kn.equals(ScenEngine.noren(rn)))) continue;
                Map<String, Object> tiers = Py.M(ke.getValue());
                List<Object> items = Py.truthy(r.get("man")) ? Py.L(tiers.get(Long.toString(Py.toInt(r.get("man"))))) : null;
                if (!Py.truthy(items)) {
                    iss.add(D("구분", "계산제외", "담보", rn, "사유", Py.fmt("가입금액 %s만원이 약관 지급금액표(inj_itc.json)에 없음", r.get("man")))); continue;
                }
                List<Object> parts = new ArrayList<>();
                Object tot = 0L;
                for (Object it0 : items) {
                    Map<String, Object> it = Py.M(it0);
                    String l = (String) it.get("l");
                    Object amt;
                    if (((String) it.get("c")).startsWith("수술")) amt = (acts.contains("surg") && js.contains(Long.parseLong(l.substring(0, 1)))) ? it.get("amt") : (Object) 0L;
                    else {
                        String key = null;
                        for (Map.Entry<String, Object> a : INJ_ACT.entrySet()) if (l.contains(a.getKey())) { key = (String) a.getValue(); break; }
                        amt = (key != null && !key.isEmpty() && acts.contains(key)) ? it.get("amt") : (Object) 0L;
                    }
                    if (Py.truthy(amt)) { parts.add(Py.fmt("%s %s", l, Py.comma(amt))); tot = Py.add(tot, amt); }
                }
                if (Py.truthy(tot)) out.add(D("name", rn, "amt", Math.min(Py.num(tot), Py.num(r.get("man"))), "why", Py.join(" · ", parts), "rule", "itc", "group", "통합치료비", "freq", "each", "no", r.get("no")));
            }
        }
        return new Object[]{out, iss};
    }

    public static boolean has_need(Map<String, Object> c, List<Object> riders) {
        if (!Py.truthy(c.get("need"))) return true;
        for (Object r0 : riders) {
            Map<String, Object> r = Py.M(r0);
            boolean all = true;
            String rn = _ns(r.get("name"));
            for (Object w : Py.gl(c, "need")) if (!rn.contains(_ns(w))) { all = false; break; }
            if (all && Py.truthy(r.get("man")) && Py.num(r.get("man")) > 0) return true;
        }
        return false;
    }

    /** 칸 값 — Object[]{값, 지급 줄 List, 로그 List}. 값 : Double(만원) / null(미가입) / '간병인 보내줌' (간병인 · direct 칸은 가입금액 꼴 그대로 Long 또는 Double) */
    public static Object[] cell_value(Map<String, Object> c, List<Object> riders) {
        String k = (String) c.get("kind");
        if (k.equals("care")) {
            String direct = (String) c.get("direct");
            Object[] cc = (Object[]) GaCare.cells(riders).get(direct);
            Object v = cc[0];
            List<Object> lines = new ArrayList<>();
            for (Object r0 : Py.L(cc[1])) {
                Map<String, Object> r = Py.M(r0);
                String rn = (String) r.get("name");
                lines.add(D("name", Py.truthy(r.get("shown")) ? r.get("shown") : rn,
                        "amt", ((direct.equals("unused") || direct.equals("nurse")) && !rn.contains("간호·간병")) ? (Object) GaCare.daily(r) : r.get("man"),
                        "why", Py.truthy(r.get("man")) ? "설계서 가입금액 그대로" : "설계서 금액란(또는 N천원)", "rule", "direct", "dementia", r.get("dementia")));
            }
            if (direct.equals("hosp") || direct.equals("nh")) return new Object[]{Py.truthy(v) ? GaCare.SEND : null, lines, new ArrayList<Object>()};
            return new Object[]{v, lines, new ArrayList<Object>()};
        }
        if (k.equals("direct")) {
            Map<String, Object> d = Py.gm(c, "direct");
            List<Object> rs = new ArrayList<>(), lines = new ArrayList<>(), mans = new ArrayList<>();
            for (Object r0 : riders) {
                String lab = _sub_label((String) Py.M(r0).get("name"));
                boolean ok = true;
                for (Object a : Py.gl(d, "keys")) if (!lab.contains((String) a)) { ok = false; break; }
                if (ok) for (Object x : Py.L(Py.get(d, "exclude", new ArrayList<Object>()))) if (lab.contains((String) x)) { ok = false; break; }
                if (ok) rs.add(r0);
            }
            for (Object r0 : rs) { Map<String, Object> r = Py.M(r0); mans.add(r.get("man")); lines.add(D("name", r.get("name"), "amt", r.get("man"), "why", "가입금액 그대로", "rule", "direct")); }
            return new Object[]{rs.isEmpty() ? null : Py.sum(mans), lines, new ArrayList<Object>()};
        }
        Map<String, Object> s_ = Py.gm(c, "sc");
        String mode = (String) c.get("mode");
        Object[] p = pay(riders, s_);
        List<Object> L = Py.L(p[0]), iss = Py.L(p[1]);
        Object[] ij = inj_lines(riders, s_);
        if (!Py.L(ij[0]).isEmpty() || !Py.L(ij[1]).isEmpty()) {
            L = new ArrayList<>(L); L.addAll(Py.L(ij[0]));
            iss = new ArrayList<>(iss); iss.addAll(Py.L(ij[1]));
        }
        if (mode.equals("ms_only")) {
            boolean any = false;
            for (Object r : riders) if ("ms".equals(Py.M(r).get("itc"))) { any = true; break; }
            if (!any) return new Object[]{null, L, iss};
        }
        if (!has_need(c, riders)) return new Object[]{null, L, iss};
        List<Object> cs_ = new ArrayList<>();
        boolean anyc = false;
        for (Object l : L) { Object a = counts(Py.M(l), mode); cs_.add(a); if (Py.truthy(a)) anyc = true; }
        if (Py.truthy(c.get("na_if_empty")) && !anyc) return new Object[]{null, L, iss};
        return new Object[]{Py.num(Py.sum(cs_)), L, iss};
    }

    public static List<Object> tokens_of(Object v) {
        if (v == null) return Py.list("미가입");
        if (v instanceof String) return Py.list(v);
        return Py.list(won(v));
    }
    public static Object[] cell_tokens(Map<String, Object> c, List<Object> riders) {
        Object[] r = cell_value(c, riders);
        return new Object[]{tokens_of(r[0]), r[1], r[2]};
    }

    // ═══════════════ 특약 마스터 우주 ═══════════════
    public static final Map<String, Object> DB = Matcher_.DB;
    public static final Map<String, Object> DBID = new LinkedHashMap<>();
    public static final Set<String> PARENTS = new LinkedHashSet<>();
    static {
        for (Object o : Py.gl(DB, "riders")) {
            Map<String, Object> r = Py.M(o);
            String id = (String) r.get("id");
            DBID.put(id, r);
            if (Py.match("^[^-]+-\\d+$", id) != null) PARENTS.add(Py.split(id, "-").get(0));
        }
    }
    private static long min_man(String name) {
        String iid = ScenEngine.itc_id(name), lsid = ScenEngine.ls_id(name);
        long man = 100;
        if (Py.truthy(iid)) {
            Long best = null;
            for (String k : Py.gm(Engine.AMT, Py.gs(Py.M(Engine.RM.get(iid)), "ty")).keySet()) { long v = Long.parseLong(k.trim()); if (best == null || v < best) best = v; }
            man = best;
        } else if (Py.truthy(lsid)) {
            Object ls = ScenEngine.LS.get(lsid);
            Object t = Py.get(Py.truthy(ls) ? ls : null, "tiers");
            if (Py.truthy(t)) {
                String bk = null;
                for (String k : Py.M(t).keySet()) if (bk == null || Double.parseDouble(k) < Double.parseDouble(bk)) bk = k;
                man = (long) Double.parseDouble(bk);
            }
        }
        return man;
    }
    private static Object orEmpty(Object v) { return Py.truthy(v) ? v : new ArrayList<Object>(); }
    /** 특약 마스터 전체(세부보장이 따로 있는 부모 특약 · 1-7종 부모는 빼고, 종별 줄을 덧붙인다) */
    public static List<Object> universe() {
        List<Object> out = new ArrayList<>();
        List<Object> riders = Py.gl(DB, "riders");
        for (Object o : riders) {
            Map<String, Object> rec = Py.M(o);
            if (PARENTS.contains(rec.get("id"))) continue;
            String name = (String) rec.get("n");
            if (Py.has("수술비\\s*\\(1-7종", name)) continue;
            Object[] m = Matcher_.match(name);
            String iid = ScenEngine.itc_id(name);
            long man = min_man(name);
            out.add(D("no", rec.get("id"), "name", name, "man", man, "cat", rec.get("c"), "codes", orEmpty(rec.get("k")), "excl", orEmpty(rec.get("x")),
                    "hc", orEmpty(rec.get("hc")), "benefit", m[1], "sub", m[2], "matched", true, "itc", iid, "product", rec.get("p"), "db_id", rec.get("id")));
        }
        for (String cause : new String[]{"질병", "상해"}) {
            Map<String, Object> parent = null;
            String want = ScenEngine.nname(Py.fmt("수술비(1-7종, 연간3회한)[%s]", cause));
            for (Object o : riders) if (ScenEngine.nname(Py.gs(o, "n")).equals(want)) { parent = Py.M(o); break; }
            for (int j = 1; j < 8; j++) {
                String nm = Py.fmt("┗ 수술비[%s%d종]", cause, j);
                out.add(D("no", Py.fmt("row-%s%d", cause, j), "name", nm, "man", 100L, "cat", Py.get(parent, "c"), "codes", orEmpty(Py.get(parent, "k")), "excl", orEmpty(Py.get(parent, "x")),
                        "hc", new ArrayList<Object>(), "benefit", null, "sub", null, "matched", true, "itc", null, "product", "설계서 종별 행", "db_id", Py.fmt("row-%s%d", cause, j), "via", Py.get(parent, "n")));
            }
        }
        Map<String, Object> p15 = null;
        for (Object o : riders) if ("수술비Ⅱ(1-5종)".equals(Py.gs(o, "n"))) { p15 = Py.M(o); break; }
        for (String cause : new String[]{"질병", "상해"}) {
            for (int j = 1; j < 6; j++) {
                String nm = Py.fmt("수술비Ⅱ(1-5종)[%s%d종]", cause, j);
                out.add(D("no", Py.fmt("row15-%s%d", cause, j), "name", nm, "man", 100L, "cat", Py.get(p15, "c"), "codes", new ArrayList<Object>(), "excl", orEmpty(Py.get(p15, "x")), "hc", new ArrayList<Object>(),
                        "benefit", Py.fmt("%s%d종", cause, j), "sub", null, "matched", true, "itc", null, "product", "설계서 종별 행", "db_id", Py.fmt("row15-%s%d", cause, j), "via", Py.get(p15, "n")));
                Map<String, Object> pp = null;
                String pn = Py.fmt("%s 1-5종수술비(plus)(연간2회이상)", cause);
                for (Object o : riders) if (pn.equals(Py.gs(o, "n"))) { pp = Py.M(o); break; }
                nm = Py.fmt("%s 1-5종수술비(plus)(연간2회이상)(%d종,연간1회한)", cause, j);
                out.add(D("no", Py.fmt("rowplus-%s%d", cause, j), "name", nm, "man", 100L, "cat", Py.get(pp, "c"), "codes", new ArrayList<Object>(), "excl", orEmpty(Py.get(pp, "x")), "hc", new ArrayList<Object>(),
                        "benefit", null, "sub", Py.fmt("%d종,연간1회한", j), "matched", true, "itc", null, "product", "설계서 종별 행", "db_id", Py.fmt("rowplus-%s%d", cause, j), "via", Py.get(pp, "n")));
            }
        }
        return out;
    }
}
