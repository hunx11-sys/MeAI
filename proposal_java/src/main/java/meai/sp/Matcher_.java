package meai.sp;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 파이썬 matcher.py — 담보명 정규화 · 특약 마스터 매칭.
 * 설계서 PDF 표 읽기(read_proposal · _guide_rows)는 옮기지 않는다(자바 판은 담보코드 입력만 받는다).
 * 클래스 이름은 java.util.regex.Matcher 와 겹치지 않게 밑줄을 붙였다.
 */
public final class Matcher_ {
    private Matcher_() {}

    /** 파이썬이 던졌을 예외의 이름 · 글자를 그대로 싣는다(match 가 잡아 로그에 적는다) */
    public static class PyError extends RuntimeException {
        private static final long serialVersionUID = 1L;
        public final String type;
        public PyError(String type, String msg) { super(msg); this.type = type; }
    }

    public static final Map<String, Object> DB;
    static {
        Map<String, Object> db = Py.M(Py.loadJson("db.json"));
        String ex = Py.path("db_terms_extra.json");
        if (Py.exists(ex)) {
            Map<String, Object> d2 = new LinkedHashMap<>(db);                     // dict(DB, riders=DB['riders'] + extra['riders'])
            List<Object> rs = new ArrayList<>(Py.gl(db, "riders"));
            rs.addAll(Py.gl(Py.M(Json.parse(Py.read(ex))), "riders"));
            d2.put("riders", rs);
            db = d2;
        }
        DB = db;
    }
    public static final String GOJI = ScenEngine.GOJI;
    public static final String _A = "(?:" + ScenEngine.AMT_RE + ")";
    public static final String RENEW = "\\((?:\\d+년)?갱신\\)";
    public static final Pattern MIDDOT = Py.re("[·ㆍ․‧∙•・]");

    public static String base(String n) {
        return Py.sub(MIDDOT, "", Py.sub("\\s+", "", Py.sub(ScenEngine.VARTAG, "", Py.sub(RENEW, "", Py.sub(GOJI, "", n))).replace("[기본계약]", "").replace("┗", "")));
    }

    public static final String PRE_REN = "^갱신형";
    public static final Map<String, List<Object>> INDEX = new LinkedHashMap<>();
    public static final Map<String, List<Object>> BRACK = new LinkedHashMap<>();
    public static final Map<String, List<Object>> CHILD = new LinkedHashMap<>();
    static {
        for (Object o : Py.gl(DB, "riders")) {
            Map<String, Object> r = Py.M(o);
            String k = base((String) r.get("n"));
            INDEX.computeIfAbsent(k, x -> new ArrayList<>()).add(r);
            if (k.endsWith("]")) BRACK.computeIfAbsent(Py.sub("\\[[^\\[\\]]+\\]$", "", k), x -> new ArrayList<>()).add(r);
        }
        for (Object o : Py.gl(DB, "riders")) {
            Map<String, Object> r = Py.M(o);
            String id = (String) r.get("id");
            if (id.contains("-")) CHILD.computeIfAbsent(id.substring(0, id.lastIndexOf('-')), x -> new ArrayList<>()).add(r);
        }
    }
    private static final List<Object> EMPTY = java.util.Collections.unmodifiableList(new ArrayList<>());
    private static List<Object> idx(String k) { List<Object> v = INDEX.get(k); return v == null ? EMPTY : v; }
    private static List<Object> child(Object id) { List<Object> v = CHILD.get(id); return v == null ? EMPTY : v; }

    public static String _norm(String s) { return Py.sub("[\\s․·,]", "", s == null ? "" : s); }

    /** 이름 끝의 균형 잡힌 괄호 그룹을 뒤에서부터 떼어 낸다 → [{부모 후보, 꼬리 라벨}, …] */
    public static List<String[]> _trail_groups(String n) {
        List<String[]> out = new ArrayList<>();
        String rest = n;
        while (rest.endsWith(")")) {
            int depth = 0, i = rest.length() - 1;
            while (i >= 0) {
                char c = rest.charAt(i);
                if (c == ')') depth++;
                else if (c == '(') { depth--; if (depth == 0) break; }
                i--;
            }
            if (i < 0) break;
            out.add(new String[]{rest.substring(0, i), rest.substring(i + 1, rest.length() - 1)});
            rest = rest.substring(0, i);
        }
        return out;
    }

    /** 끝의 균형 잡힌 [○○] 안쪽 */
    public static String _last_bracket(String s) {
        int depth = 0;
        for (int i = s.length() - 1; i >= 0; i--) {
            char c = s.charAt(i);
            if (c == ']') depth++;
            else if (c == '[') { depth--; if (depth == 0) return Py.slice(s, i + 1, -1); }
        }
        return s;
    }

    private static String _label(Map<String, Object> k) {
        String bk = base((String) k.get("n"));
        return bk.endsWith("]") ? _norm(_last_bracket(bk)) : _norm(bk);
    }
    private static String _rawlabel(Map<String, Object> k) {
        String bk = base((String) k.get("n"));
        return bk.endsWith("]") ? _last_bracket(bk) : bk;
    }

    /** 설계서가 세부급부를 (○○) 괄호로 적은 담보 → 마스터의 그 세부보장 레코드. 반환 {hit 목록, 라벨} 또는 {null, null} */
    public static Object[] _sub_pick(String n, String line) {
        for (String[] pl : _trail_groups(n)) {
            String parent = pl[0], lab = pl[1];
            List<Object> ps = idx(parent);
            if (ps.isEmpty()) {
                List<String> ks = new ArrayList<>();
                for (String k : INDEX.keySet()) {
                    if (k.isEmpty() || !(parent.startsWith(k) || k.startsWith(parent))) continue;
                    boolean any = false;
                    for (Object r : INDEX.get(k)) if (!child(Py.M(r).get("id")).isEmpty()) { any = true; break; }
                    if (any) ks.add(k);
                }
                List<String> fit = new ArrayList<>();
                for (String k : ks) {
                    if (!k.startsWith(parent)) continue;
                    boolean all = true;
                    for (Object g : Py.findall("\\([^()]*\\)", k.substring(parent.length()))) if (!n.contains((String) g)) { all = false; break; }
                    if (all) fit.add(k);
                }
                if (!ks.isEmpty()) ps = INDEX.get(maxLen(fit.isEmpty() ? ks : fit));
            }
            List<Object> kids = new ArrayList<>();
            if (Py.truthy(line)) for (Object r : ps) if (Objects.equals(Py.M(r).get("p"), line)) kids.addAll(child(Py.M(r).get("id")));
            if (kids.isEmpty()) for (Object r : ps) kids.addAll(child(Py.M(r).get("id")));
            if (kids.isEmpty()) continue;
            String key = _norm(lab);
            List<Object> hit = new ArrayList<>();
            for (Object k : kids) if (_label(Py.M(k)).equals(key)) hit.add(k);
            if (!hit.isEmpty()) return new Object[]{hit, lab};
            for (Object k : kids) if (_label(Py.M(k)).startsWith(key)) hit.add(k);
            if (!hit.isEmpty()) return new Object[]{hit, lab};
            if (!key.isEmpty()) {
                for (Object k : kids) {
                    String l = _label(Py.M(k));
                    if ((l.endsWith(key + "진단비") || l.endsWith(key + "수술비") || l.endsWith(key + "치료비")) && l.length() > key.length() + 3) hit.add(k);
                }
            }
            if (hit.size() == 1) return new Object[]{hit, lab};
            hit = new ArrayList<>();
            Set<String> want = _labtoks(lab);
            for (Object k : kids) if (_labtoks(_rawlabel(Py.M(k))).equals(want)) hit.add(k);
            if (!hit.isEmpty()) return new Object[]{hit, lab};
        }
        return new Object[]{null, null};
    }

    /** max(ks, key=len) — 길이가 같으면 앞의 것 */
    private static String maxLen(List<String> ks) {
        String best = null;
        for (String k : ks) if (best == null || k.length() > best.length()) best = k;
        return best;
    }

    public static Set<String> _labtoks(String l) {
        Set<String> out = new HashSet<>();
        for (String t : Py.resplit("[(),\\s]+", l)) if (!t.isEmpty()) out.add(Py.sub("치료비$", "치료", t));
        return out;
    }

    private static List<Object> pick(String k, String line) {
        List<Object> all = idx(k), own = new ArrayList<>();
        for (Object r : all) if (Objects.equals(Py.M(r).get("p"), line)) own.add(r);
        return own.isEmpty() ? all : own;
    }

    /** 정규화된 담보명 하나로 마스터를 찾는다. 반환 {후보 목록(List), 대괄호 세부(String), 끝괄호 꼬리(String)} */
    public static Object[] _find(String n, String line) {
        String b = null, s = null;
        List<Object> c = pick(n, line);
        if (c.isEmpty() && n.contains("[")) {
            Matcher m0 = Py.search("\\[([^\\[\\]]+)\\]", n);
            if (m0 == null) throw new PyError("AttributeError", "'NoneType' object has no attribute 'group'");
            b = m0.group(1);
            c = pick(Py.sub("\\[[^\\[\\]]+\\]", "", n), line);
            if (!c.isEmpty()) {
                String key = _norm(b);
                List<Object> kids = new ArrayList<>();
                for (Object r : c) kids.addAll(child(Py.M(r).get("id")));
                if (kids.isEmpty()) {
                    String pn = Py.sub("\\[[^\\[\\]]+\\]", "", n);
                    String pn2 = Py.match(PRE_REN, pn) != null ? Py.sub(PRE_REN, "", pn) : "갱신형" + pn;
                    List<Object> ps = new ArrayList<>(idx(pn));
                    ps.addAll(idx(pn2));
                    for (Object r : ps) if (Objects.equals(Py.M(r).get("p"), line)) kids.addAll(child(Py.M(r).get("id")));
                    if (kids.isEmpty()) for (Object r : ps) kids.addAll(child(Py.M(r).get("id")));
                }
                List<Object> hit = new ArrayList<>();
                for (Object k : kids) if (_lab(Py.M(k)).equals(key)) hit.add(k);
                if (hit.isEmpty()) for (Object k : kids) if (_lab(Py.M(k)).startsWith(key)) hit.add(k);
                if (hit.size() == 1) c = hit;
            }
        }
        if (c.isEmpty()) {
            Object[] hp = _sub_pick(n, line);
            if (hp[0] != null && !Py.L(hp[0]).isEmpty()) return new Object[]{hp[0], hp[1], null};
        }
        if (c.isEmpty() && Py.has("\\([^()]+\\)$", n)) {
            s = Py.search("\\(([^()]+)\\)$", n).group(1);
            c = pick(Py.sub("\\([^()]+\\)$", "", n), line);
        }
        if (c.isEmpty()) c = pick(Py.sub("\\([^()]*\\)", "", n), line);
        if (c.isEmpty()) {
            for (Object go : Py.findall("\\(([^()]+)\\)", n)) {
                String g = (String) go;
                String tok = "(" + g + ")";
                int at = n.indexOf(tok);
                String key = at < 0 ? n : n.substring(0, at) + n.substring(at + tok.length());      // n.replace('(g)', '', 1)
                List<Object> cand = new ArrayList<>();
                List<Object> br = BRACK.get(key);
                if (br != null) for (Object r : br) {
                    String bn = base((String) Py.M(r).get("n"));
                    int i = bn.lastIndexOf('[');
                    if ((i < 0 ? bn : bn.substring(i + 1)).contains(g)) cand.add(r);
                }
                if (Py.truthy(line)) {
                    List<Object> own = new ArrayList<>();
                    for (Object r : cand) if (Objects.equals(Py.M(r).get("p"), line)) own.add(r);
                    if (!own.isEmpty()) cand = own;
                }
                if (!cand.isEmpty()) { c = Py.list(cand.get(0)); b = g; break; }
            }
        }
        if (c.isEmpty()) {
            List<String> ks = new ArrayList<>();
            for (String k : INDEX.keySet()) if (!k.isEmpty() && (n.startsWith(k) || k.startsWith(n))) ks.add(k);
            if (!ks.isEmpty()) c = pick(maxLen(ks), line);
        }
        return new Object[]{c, b, s};
    }
    private static String _lab(Map<String, Object> k) {
        Matcher m = Py.search("\\[([^\\[\\]]+)\\]$", base((String) k.get("n")));
        return _norm(m == null ? "" : m.group(1));
    }

    /** 담보명 → {마스터 레코드(Map 또는 null), 대괄호 세부, 끝괄호 꼬리}. 어떤 이름이 와도 멈추지 않는다 — 실패하면 미매칭 + 로그 */
    public static Object[] match(String name) { return match(name, null); }
    public static Object[] match(String name, String line) {
        try {
            return _match(name, line);
        } catch (PyError ex) {
            ScenEngine.log("검토필요", name, Py.fmt("특약 마스터 매칭 중 오류(%s: %s) — 미매칭으로 두고 계속", ex.type, ex.getMessage()));
            return new Object[]{null, null, null};
        } catch (RuntimeException ex) {
            ScenEngine.log("검토필요", name, Py.fmt("특약 마스터 매칭 중 오류(%s: %s) — 미매칭으로 두고 계속", ex.getClass().getSimpleName(), String.valueOf(ex.getMessage())));
            return new Object[]{null, null, null};
        }
    }

    public static Object[] _match(String name, String line) {
        String n = base(name);
        Object[] f = _find(n, line);
        List<Object> c = Py.L(f[0]);
        Object b = f[1], s = f[2];
        String alt = Py.match(PRE_REN, n) != null ? Py.sub(PRE_REN, "", n) : "갱신형" + n;
        if (c.isEmpty()) {
            f = _find(alt, line);
            c = Py.L(f[0]); b = f[1]; s = f[2];
        } else if (Py.truthy(line) && !Objects.equals(Py.M(c.get(0)).get("p"), line)) {
            Object[] f2 = _find(alt, line);
            List<Object> c2 = Py.L(f2[0]);
            if (!c2.isEmpty() && Objects.equals(Py.M(c2.get(0)).get("p"), line)) { c = c2; b = f2[1]; s = f2[2]; }
        }
        return new Object[]{c.isEmpty() ? null : c.get(0), b, s};
    }

    public static final Pattern SUBREF = Py.re("세부\\s*보장\\s*참조");
    public static final Pattern GRADE_RANGE = Py.re("\\[(상해|질병)\\d-\\d종\\]");

    /** 부모 행 담보명 → 마스터 레코드. 종 범위 표기를 마스터 표기로 바꿔 찾는다. 없으면 null */
    public static Map<String, Object> parent_master(String name) { return parent_master(name, null); }
    public static Map<String, Object> parent_master(String name, String line) {
        return Py.M(match(Py.sub(GRADE_RANGE, g -> "[" + g.group(1) + "]", name), line)[0]);
    }

    /** ┗ 세부 행에 부모 마스터를 물린다. 부모가 없거나 부모도 마스터에 없으면 그대로 */
    public static Map<String, Object> _link(Map<String, Object> row, Map<String, Object> parent, String name) {
        if (!Py.truthy(parent) || !Py.truthy(parent.get("m")) || !Py.lstrip(name).startsWith("┗")) return row;
        Map<String, Object> pm = Py.M(parent.get("m"));
        row.put("cat", pm.get("c"));
        row.put("codes", Py.or(pm.get("k"), new ArrayList<Object>()));
        row.put("excl", Py.or(pm.get("x"), new ArrayList<Object>()));
        row.put("hc", Py.or(pm.get("hc"), new ArrayList<Object>()));
        row.put("matched", Boolean.TRUE);
        row.put("via", parent.get("name"));
        row.put("via_id", pm.get("id"));
        return row;
    }
}
