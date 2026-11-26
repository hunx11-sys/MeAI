package meai.sp;

import java.io.IOException;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Function;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 파이썬 판(proposal_smart)의 동작을 자바에서 그대로 내기 위한 공통 도구.
 * 계산 · 지면 코드는 파이썬 함수와 1:1 로 옮기고, 언어 차이(정규식 · 반올림 · 글자 꼴 · 참/거짓 · 정렬)는 여기서만 맞춘다.
 * 규칙은 PORTING.md 를 본다.
 */
public final class Py {
    private Py() {}

    // ── 자료 폴더 ────────────────────────────────────────
    /** 자료(db.json · rules.json · ga_assets …)가 있는 폴더. 환경변수 SP_HOME → 시스템 속성 sp.home → ./data → ../proposal_smart 순서 */
    public static final String BASE = findBase();

    private static String findBase() {
        String e = System.getProperty("sp.home");
        if (e == null || e.isEmpty()) e = System.getenv("SP_HOME");
        if (e != null && !e.isEmpty()) return Paths.get(e).toAbsolutePath().normalize().toString();
        for (String c : new String[]{"data", "../proposal_smart", "proposal_smart", "."}) {
            Path p = Paths.get(c);
            if (Files.exists(p.resolve("rules.json")) && Files.exists(p.resolve("db.json"))) return p.toAbsolutePath().normalize().toString();
        }
        try {                                                    // 실행 파일(jar · classes) 옆의 자료 폴더 — 어느 폴더에서 실행해도 찾게
            Path here = Paths.get(Py.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toAbsolutePath();
            Path dir = Files.isDirectory(here) ? here : here.getParent();
            for (String c : new String[]{"data", "../data", "../../data", "../../../proposal_smart", "../../proposal_smart", "../proposal_smart"}) {
                Path p = dir.resolve(c);
                if (Files.exists(p.resolve("rules.json")) && Files.exists(p.resolve("db.json"))) return p.toAbsolutePath().normalize().toString();
            }
        } catch (Exception ignore) { }
        return Paths.get(".").toAbsolutePath().normalize().toString();
    }

    public static String path(String... parts) {
        Path p = Paths.get(BASE);
        for (String x : parts) p = p.resolve(x);
        return p.toString();
    }

    public static boolean exists(String p) { return Files.exists(Paths.get(p)); }

    public static String read(String p) {
        try {
            String s = new String(Files.readAllBytes(Paths.get(p)), StandardCharsets.UTF_8);
            return (s.length() > 0 && s.charAt(0) == '﻿') ? s.substring(1) : s;
        } catch (IOException ex) { throw new RuntimeException("파일을 읽지 못함 : " + p, ex); }
    }

    public static byte[] readBytes(String p) {
        try { return Files.readAllBytes(Paths.get(p)); } catch (IOException ex) { throw new RuntimeException("파일을 읽지 못함 : " + p, ex); }
    }

    public static void write(String p, String s) {
        try {
            Path q = Paths.get(p);
            if (q.getParent() != null) Files.createDirectories(q.getParent());
            Files.write(q, s.getBytes(StandardCharsets.UTF_8));
        } catch (IOException ex) { throw new RuntimeException("파일을 쓰지 못함 : " + p, ex); }
    }

    /** json.load(open(BASE/name)) */
    public static Object loadJson(String name) { return Json.parse(read(path(name))); }

    /** os.environ.get(name) — 시스템 속성(-Dname=… · 시험에서 System.setProperty)이 있으면 그것, 없으면 환경변수. 비어 있으면 null */
    public static String env(String name) {
        String v = System.getProperty(name);
        if (v == null) v = System.getenv(name);
        return (v == null || v.isEmpty()) ? null : v;
    }

    /** copy.deepcopy — dict · list 만 새로 만들고 나머지(글자 · 수)는 그대로 */
    public static Object deepcopy(Object o) {
        if (o instanceof Map) {
            LinkedHashMap<String, Object> m = new LinkedHashMap<>();
            for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) m.put((String) e.getKey(), deepcopy(e.getValue()));
            return m;
        }
        if (o instanceof List) {
            ArrayList<Object> l = new ArrayList<>();
            for (Object x : (List<?>) o) l.add(deepcopy(x));
            return l;
        }
        return o;
    }

    /** open(p, encoding='utf-8').read() — 글자 방식 읽기(줄 끝 \r\n · \r 을 \n 으로) */
    public static String readText(String p) {
        String s = read(p);
        return s.indexOf('\r') < 0 ? s : s.replace("\r\n", "\n").replace('\r', '\n');
    }

    /** pathlib.Path(p).as_uri() — file:///… (영문 · 숫자 · _.-~/ 밖의 글자는 %XX) */
    public static String as_uri(String p) {
        String s = Paths.get(p).toAbsolutePath().toString();
        String head = "file://";
        if (s.length() >= 2 && s.charAt(1) == ':' && Character.isLetter(s.charAt(0))) { head = "file:///" + s.substring(0, 2); s = s.substring(2).replace('\\', '/'); }
        StringBuilder b = new StringBuilder(head);
        for (byte x : s.getBytes(StandardCharsets.UTF_8)) {
            int c = x & 255;
            if ((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || (c >= '0' && c <= '9') || c == '_' || c == '.' || c == '-' || c == '~' || c == '/') b.append((char) c);
            else b.append('%').append("0123456789ABCDEF".charAt(c >> 4)).append("0123456789ABCDEF".charAt(c & 15));
        }
        return b.toString();
    }

    // ── 꼴 바꾸기 ────────────────────────────────────────
    @SuppressWarnings("unchecked")
    public static Map<String, Object> M(Object o) { return (Map<String, Object>) o; }
    @SuppressWarnings("unchecked")
    public static List<Object> L(Object o) { return (List<Object>) o; }
    public static String Str(Object o) { return (String) o; }

    /** dict(k1=v1, k2=v2 …) — 넣은 순서 유지 */
    public static Map<String, Object> dict(Object... kv) {
        LinkedHashMap<String, Object> m = new LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) m.put((String) kv[i], kv[i + 1]);
        return m;
    }

    public static List<Object> list(Object... xs) {
        ArrayList<Object> a = new ArrayList<>(xs.length);
        for (Object x : xs) a.add(x);
        return a;
    }

    /** d.get(k) — d 가 null 이면 null */
    public static Object get(Object d, String k) { return d == null ? null : ((Map<?, ?>) d).get(k); }
    /** d.get(k, dflt) — 열쇠가 있으면(값이 None 이어도) 그 값 */
    public static Object get(Object d, String k, Object dflt) {
        Map<?, ?> m = (Map<?, ?>) d;
        return (m != null && m.containsKey(k)) ? m.get(k) : dflt;
    }
    /** d.get(k) or dflt */
    public static Object getOr(Object d, String k, Object dflt) { Object v = get(d, k); return truthy(v) ? v : dflt; }
    public static String gs(Object d, String k) { return (String) get(d, k); }
    /** (d.get(k) or '') */
    public static String gs0(Object d, String k) { Object v = get(d, k); return v == null ? "" : (String) v; }
    public static List<Object> gl(Object d, String k) { return L(get(d, k)); }
    /** (d.get(k) or []) */
    public static List<Object> gl0(Object d, String k) { Object v = get(d, k); return v == null ? new ArrayList<>() : L(v); }
    public static Map<String, Object> gm(Object d, String k) { return M(get(d, k)); }

    // ── 참 · 거짓 ────────────────────────────────────────
    /** 파이썬의 bool(x) */
    public static boolean truthy(Object o) {
        if (o == null) return false;
        if (o instanceof Boolean) return (Boolean) o;
        if (o instanceof String) return !((String) o).isEmpty();
        if (o instanceof Long || o instanceof Integer) return ((Number) o).longValue() != 0;
        if (o instanceof Number) return ((Number) o).doubleValue() != 0.0;
        if (o instanceof Collection) return !((Collection<?>) o).isEmpty();
        if (o instanceof Map) return !((Map<?, ?>) o).isEmpty();
        if (o instanceof Object[]) return ((Object[]) o).length > 0;
        return true;
    }
    /** a or b */
    public static Object or(Object a, Object b) { return truthy(a) ? a : b; }
    public static String orS(String a, String b) { return (a != null && !a.isEmpty()) ? a : b; }

    // ── 수 ───────────────────────────────────────────────
    public static boolean isInt(Object o) { return o instanceof Long || o instanceof Integer || o instanceof java.math.BigInteger; }
    public static boolean isFloat(Object o) { return o instanceof Double || o instanceof Float; }
    /** isinstance(x, (int, float)) and not isinstance(x, bool) */
    public static boolean isNum(Object o) { return o instanceof Number; }
    public static double num(Object o) {
        if (o instanceof Number) return ((Number) o).doubleValue();
        if (o instanceof Boolean) return ((Boolean) o) ? 1 : 0;
        throw new IllegalArgumentException("수가 아님 : " + o);
    }
    public static long lng(Object o) {
        if (o instanceof Number) return ((Number) o).longValue();
        if (o instanceof Boolean) return ((Boolean) o) ? 1 : 0;
        throw new IllegalArgumentException("수가 아님 : " + o);
    }
    /** 계산 결과를 파이썬 꼴로 되돌린다 : 두 값이 모두 정수였으면 Long, 아니면 Double */
    public static Object box(Object a, Object b, double r) { return (isIntLike(a) && isIntLike(b)) ? (Object) Long.valueOf((long) r) : (Object) Double.valueOf(r); }
    private static boolean isIntLike(Object o) { return isInt(o) || o instanceof Boolean; }
    /** a + b (수) — 정수끼리면 Long, 하나라도 float 면 Double */
    public static Object add(Object a, Object b) { return (isIntLike(a) && isIntLike(b)) ? (Object) (lng(a) + lng(b)) : (Object) (num(a) + num(b)); }
    public static Object sub(Object a, Object b) { return (isIntLike(a) && isIntLike(b)) ? (Object) (lng(a) - lng(b)) : (Object) (num(a) - num(b)); }
    public static Object mul(Object a, Object b) { return (isIntLike(a) && isIntLike(b)) ? (Object) (lng(a) * lng(b)) : (Object) (num(a) * num(b)); }
    /** a / b — 파이썬의 참 나눗셈(늘 float) */
    public static double div(Object a, Object b) { return num(a) / num(b); }
    /** a // b — 정수끼리면 내림 나눗셈 Long */
    public static Object floordiv(Object a, Object b) {
        if (isIntLike(a) && isIntLike(b)) return Math.floorDiv(lng(a), lng(b));
        return Math.floor(num(a) / num(b));
    }
    /** sum(xs) — 파이썬처럼 0(int)에서 시작해 float 를 만나면 float */
    public static Object sum(Iterable<?> xs) {
        long li = 0; double d = 0; boolean fl = false;
        for (Object x : xs) {
            if (!fl && isIntLike(x)) li += lng(x);
            else { if (!fl) { fl = true; d = li; } d += num(x); }
        }
        return fl ? (Object) d : (Object) li;
    }
    /** round(x) — 반은 짝수 쪽으로(파이썬 3) */
    public static long round(double x) { return (long) Math.rint(x); }
    /** round(x, n) — 이진 값 그대로를 반-짝수로(파이썬과 같은 결과) */
    public static double round(double x, int n) {
        if (Double.isNaN(x) || Double.isInfinite(x)) return x;
        return new BigDecimal(x).setScale(n, RoundingMode.HALF_EVEN).doubleValue();
    }
    /** int(x) — 0 쪽으로 버림 */
    public static long toInt(Object o) {
        if (o instanceof String) return Long.parseLong(((String) o).trim());
        if (isInt(o) || o instanceof Boolean) return lng(o);
        return (long) num(o);
    }
    public static double toFloat(Object o) { return (o instanceof String) ? Double.parseDouble(((String) o).trim()) : num(o); }

    // ── 글자 꼴 ──────────────────────────────────────────
    /** repr(float) — 가장 짧게 되돌아오는 표기(파이썬 꼴 : 1e+16 · 1e-05 · 1.0) */
    public static String repr(double d) {
        if (Double.isNaN(d)) return "nan";
        if (Double.isInfinite(d)) return d > 0 ? "inf" : "-inf";
        if (d == 0) return (1 / d < 0) ? "-0.0" : "0.0";
        String digits = null; int exp = 0;                     // 값 = 0.digits × 10^exp · 되돌아오는 가장 짧은 자릿수(JDK 판에 기대지 않게 직접 찾는다)
        BigDecimal exact = new BigDecimal(Math.abs(d));
        for (int p = 1; p <= 17; p++) {
            BigDecimal r = exact.round(new java.math.MathContext(p, RoundingMode.HALF_EVEN));
            if (r.doubleValue() == Math.abs(d)) {
                digits = r.unscaledValue().toString();
                exp = digits.length() - r.scale();
                break;
            }
        }
        if (digits == null) { BigDecimal r = exact.round(new java.math.MathContext(17, RoundingMode.HALF_EVEN)); digits = r.unscaledValue().toString(); exp = digits.length() - r.scale(); }
        int end = digits.length();
        while (end > 1 && digits.charAt(end - 1) == '0') end--;
        digits = digits.substring(0, end);
        int n = digits.length();
        int sci = exp - 1;                                     // d.ddd × 10^sci
        StringBuilder b = new StringBuilder();
        if (d < 0) b.append('-');
        if (sci < -4 || sci >= 16) {
            b.append(digits.charAt(0));
            if (n > 1) b.append('.').append(digits, 1, n);
            b.append('e').append(sci < 0 ? '-' : '+');
            int a = Math.abs(sci);
            if (a < 10) b.append('0');
            b.append(a);
        } else if (exp <= 0) {
            b.append("0.");
            for (int k = 0; k < -exp; k++) b.append('0');
            b.append(digits);
        } else if (exp >= n) {
            b.append(digits);
            for (int k = 0; k < exp - n; k++) b.append('0');
            b.append(".0");
        } else {
            b.append(digits, 0, exp).append('.').append(digits, exp, n);
        }
        return b.toString();
    }

    /** str(x) */
    public static String str(Object o) {
        if (o == null) return "None";
        if (o instanceof String) return (String) o;
        if (o instanceof Boolean) return ((Boolean) o) ? "True" : "False";
        if (o instanceof Double || o instanceof Float) return repr(((Number) o).doubleValue());
        if (o instanceof Number) return o.toString();
        return reprObj(o);
    }

    /** repr(x) — 문자열은 따옴표를 두른다 */
    public static String reprObj(Object o) {
        if (o instanceof String) {
            String s = (String) o;
            boolean sq = s.indexOf('\'') >= 0 && s.indexOf('"') < 0;
            char qc = sq ? '"' : '\'';
            StringBuilder b = new StringBuilder().append(qc);
            for (int i = 0; i < s.length(); i++) {
                char c = s.charAt(i);
                if (c == '\\') b.append("\\\\");
                else if (c == qc) b.append('\\').append(c);
                else if (c == '\n') b.append("\\n");
                else if (c == '\r') b.append("\\r");
                else if (c == '\t') b.append("\\t");
                else b.append(c);
            }
            return b.append(qc).toString();
        }
        if (o instanceof Map) {
            StringBuilder b = new StringBuilder("{");
            boolean f = true;
            for (Map.Entry<?, ?> e : ((Map<?, ?>) o).entrySet()) {
                if (!f) b.append(", ");
                f = false;
                b.append(reprObj(e.getKey())).append(": ").append(reprObj(e.getValue()));
            }
            return b.append('}').toString();
        }
        if (o instanceof List) {
            StringBuilder b = new StringBuilder("[");
            boolean f = true;
            for (Object x : (List<?>) o) { if (!f) b.append(", "); f = false; b.append(reprObj(x)); }
            return b.append(']').toString();
        }
        if (o instanceof Object[]) {                       // 튜플
            Object[] a = (Object[]) o;
            StringBuilder b = new StringBuilder("(");
            for (int i = 0; i < a.length; i++) { if (i > 0) b.append(", "); b.append(reprObj(a[i])); }
            if (a.length == 1) b.append(',');
            return b.append(')').toString();
        }
        return str(o);
    }

    /** 천 단위 쉼표 — '{:,}'.format(n) · format(n, ',') */
    public static String comma(Object n) {
        if (isInt(n)) return String.format("%,d", lng(n));
        String r = repr(num(n));
        int dot = r.indexOf('.');
        String ip = dot < 0 ? r : r.substring(0, dot), fp = dot < 0 ? "" : r.substring(dot);
        boolean neg = ip.startsWith("-");
        if (neg) ip = ip.substring(1);
        return (neg ? "-" : "") + String.format("%,d", Long.parseLong(ip)) + fp;
    }

    /** format(x, ',.Nf') — 천 단위 쉼표 + 소수 N 자리(반은 짝수로) */
    public static String commaF(Object x, int prec) {
        double d = num(x);
        BigDecimal bd = new BigDecimal(Math.abs(d)).setScale(prec, RoundingMode.HALF_EVEN);
        String t = bd.toPlainString();
        int dot = t.indexOf('.');
        String ip = dot < 0 ? t : t.substring(0, dot), fp = dot < 0 ? "" : t.substring(dot);
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < ip.length(); i++) { if (i > 0 && (ip.length() - i) % 3 == 0) b.append(','); b.append(ip.charAt(i)); }
        boolean neg = d < 0 || (d == 0 && 1 / d < 0);
        return (neg ? "-" : "") + b + fp;
    }
    /** format(x, 'g') */
    public static String fmtG(Object x) { return fmt("%g", x); }
    /** min(a, b) — 같으면 앞의 것(파이썬과 같음 · 수 꼴 유지) */
    public static Object min2(Object a, Object b) { return cmp(b, a) < 0 ? b : a; }
    /** max(a, b) — 같으면 앞의 것 */
    public static Object max2(Object a, Object b) { return cmp(b, a) > 0 ? b : a; }
    /** x in 목록 — 파이썬의 == 로 견준다(1 == 1.0) */
    public static boolean in(Object x, Collection<?> xs) {
        if (xs == null) return false;
        for (Object y : xs) if (eq(x, y)) return true;
        return false;
    }
    /** 사전의 키 오류(KeyError) — 파이썬이 d[k] 에서 던지는 것을 같은 자리에서 던진다 */
    public static final class KeyError extends RuntimeException {
        public KeyError(Object key) { super(reprObj(key)); }
    }
    /** d[k] — 없으면 KeyError */
    public static Object at(Object d, Object k) {
        Map<?, ?> m = (Map<?, ?>) d;
        if (m == null || !m.containsKey(k)) throw new KeyError(k);
        return m.get(k);
    }

    /**
     * 파이썬의 '서식' % (값 …) — %s %r %d %i %f %g %x %c %% 와 깃발(- 0 + 빈칸) · 너비 · 정밀도.
     * 값이 하나일 때도 가변 인자로 준다 : Py.fmt("%d건", n)
     */
    public static String fmt(String f, Object... a) {
        StringBuilder b = new StringBuilder();
        int ai = 0, n = f.length();
        for (int i = 0; i < n; i++) {
            char c = f.charAt(i);
            if (c != '%') { b.append(c); continue; }
            i++;
            if (i >= n) throw new IllegalArgumentException("서식이 % 로 끝남");
            if (f.charAt(i) == '%') { b.append('%'); continue; }
            boolean left = false, zero = false, plus = false, space = false;
            for (; i < n; i++) {
                char g = f.charAt(i);
                if (g == '-') left = true; else if (g == '0') zero = true; else if (g == '+') plus = true; else if (g == ' ') space = true; else if (g == '#') { } else break;
            }
            int width = 0;
            if (i < n && f.charAt(i) == '*') { width = (int) lng(a[ai++]); i++; }
            else while (i < n && Character.isDigit(f.charAt(i))) width = width * 10 + (f.charAt(i++) - '0');
            int prec = -1;
            if (i < n && f.charAt(i) == '.') {
                i++; prec = 0;
                if (i < n && f.charAt(i) == '*') { prec = (int) lng(a[ai++]); i++; }
                else while (i < n && Character.isDigit(f.charAt(i))) prec = prec * 10 + (f.charAt(i++) - '0');
            }
            char t = f.charAt(i);
            Object v = (t == '%') ? null : a[ai++];
            String body; boolean numeric = false, neg = false;
            switch (t) {
                case 's': body = str(v); if (prec >= 0 && body.length() > prec) body = body.substring(0, prec); break;
                case 'r': body = reprObj(v); break;
                case 'c': body = (v instanceof String) ? (String) v : String.valueOf((char) lng(v)); break;
                case 'd': case 'i': case 'u': {
                    long x = (v instanceof Double || v instanceof Float) ? (long) num(v) : lng(v);
                    neg = x < 0; body = Long.toString(Math.abs(x));
                    if (prec >= 0) while (body.length() < prec) body = "0" + body;
                    numeric = true; break;
                }
                case 'x': body = Long.toHexString(lng(v)); numeric = true; break;
                case 'X': body = Long.toHexString(lng(v)).toUpperCase(); numeric = true; break;
                case 'f': case 'F': {
                    double x = num(v); neg = x < 0 || (x == 0 && 1 / x < 0);
                    body = new BigDecimal(Math.abs(x)).setScale(prec < 0 ? 6 : prec, RoundingMode.HALF_EVEN).toPlainString();
                    numeric = true; break;
                }
                case 'g': case 'G': {
                    double x = num(v); neg = x < 0;
                    body = fmtG(Math.abs(x), prec < 0 ? 6 : (prec == 0 ? 1 : prec));
                    numeric = true; break;
                }
                case 'e': case 'E': {
                    double x = num(v); neg = x < 0;
                    body = fmtE(Math.abs(x), prec < 0 ? 6 : prec);
                    numeric = true; break;
                }
                default: throw new IllegalArgumentException("모르는 서식 %" + t);
            }
            String sign = "";
            if (numeric) sign = neg ? "-" : (plus ? "+" : (space ? " " : ""));
            int pad = width - sign.length() - body.length();
            if (pad <= 0) b.append(sign).append(body);
            else if (left) { b.append(sign).append(body); for (int k = 0; k < pad; k++) b.append(' '); }
            else if (zero && numeric) { b.append(sign); for (int k = 0; k < pad; k++) b.append('0'); b.append(body); }
            else { for (int k = 0; k < pad; k++) b.append(' '); b.append(sign).append(body); }
        }
        if (ai != a.length) throw new IllegalArgumentException("서식과 값의 수가 다름 : " + f);
        return b.toString();
    }

    private static String fmtE(double x, int prec) {
        if (x == 0) { StringBuilder z = new StringBuilder("0"); if (prec > 0) { z.append('.'); for (int k = 0; k < prec; k++) z.append('0'); } return z.append("e+00").toString(); }
        BigDecimal bd = new BigDecimal(x);
        int e = bd.precision() - bd.scale() - 1;
        BigDecimal m = bd.movePointLeft(e).setScale(prec, RoundingMode.HALF_EVEN);
        if (m.compareTo(BigDecimal.TEN) >= 0) { e++; m = bd.movePointLeft(e).setScale(prec, RoundingMode.HALF_EVEN); }
        int ae = Math.abs(e);
        return m.toPlainString() + "e" + (e < 0 ? "-" : "+") + (ae < 10 ? "0" : "") + ae;
    }

    private static String fmtG(double x, int p) {
        if (x == 0) return "0";
        BigDecimal bd = new BigDecimal(x).round(new java.math.MathContext(p, RoundingMode.HALF_EVEN));
        int e = bd.precision() - bd.scale() - 1;
        String s;
        if (e < -4 || e >= p) {
            String m = bd.movePointLeft(e).stripTrailingZeros().toPlainString();
            int ae = Math.abs(e);
            s = m + "e" + (e < 0 ? "-" : "+") + (ae < 10 ? "0" : "") + ae;
        } else {
            s = bd.stripTrailingZeros().toPlainString();
        }
        return s;
    }

    /** s[a:b] — null 은 생략, 음수는 뒤에서부터 */
    public static String slice(String s, Integer a, Integer b) {
        int n = s.length();
        int x = a == null ? 0 : (a < 0 ? Math.max(0, n + a) : Math.min(a, n));
        int y = b == null ? n : (b < 0 ? Math.max(0, n + b) : Math.min(b, n));
        return x >= y ? "" : s.substring(x, y);
    }
    public static <T> List<T> slice(List<T> s, Integer a, Integer b) {
        int n = s.size();
        int x = a == null ? 0 : (a < 0 ? Math.max(0, n + a) : Math.min(a, n));
        int y = b == null ? n : (b < 0 ? Math.max(0, n + b) : Math.min(b, n));
        return x >= y ? new ArrayList<>() : new ArrayList<>(s.subList(x, y));
    }
    /** s.strip() — 파이썬 공백(유니코드 공백 포함) */
    public static String strip(String s) {
        int a = 0, b = s.length();
        while (a < b && isSpace(s.charAt(a))) a++;
        while (b > a && isSpace(s.charAt(b - 1))) b--;
        return s.substring(a, b);
    }
    public static String lstrip(String s) { int a = 0; while (a < s.length() && isSpace(s.charAt(a))) a++; return s.substring(a); }
    public static String rstrip(String s) { int b = s.length(); while (b > 0 && isSpace(s.charAt(b - 1))) b--; return s.substring(0, b); }
    /** s.rstrip(chars) */
    public static String rstrip(String s, String chars) { int b = s.length(); while (b > 0 && chars.indexOf(s.charAt(b - 1)) >= 0) b--; return s.substring(0, b); }
    /** s.lstrip(chars) */
    public static String lstrip(String s, String chars) { int a = 0; while (a < s.length() && chars.indexOf(s.charAt(a)) >= 0) a++; return s.substring(a); }
    /** s[:n] — 글자(코드 포인트) 수로 자른다 */
    public static String head(String s, int n) { return s.codePointCount(0, s.length()) <= n ? s : s.substring(0, s.offsetByCodePoints(0, n)); }
    /** s[-n:] */
    public static String tail(String s, int n) { int c = s.codePointCount(0, s.length()); return c <= n ? s : s.substring(s.offsetByCodePoints(0, c - n)); }
    /** s.strip(chars) */
    public static String strip(String s, String chars) {
        int a = 0, b = s.length();
        while (a < b && chars.indexOf(s.charAt(a)) >= 0) a++;
        while (b > a && chars.indexOf(s.charAt(b - 1)) >= 0) b--;
        return s.substring(a, b);
    }
    public static boolean isSpace(char c) {
        return c == ' ' || (c >= 0x09 && c <= 0x0d) || (c >= 0x1c && c <= 0x1f) || c == 0x85 || c == 0xa0 || c == 0x1680
                || (c >= 0x2000 && c <= 0x200a) || c == 0x2028 || c == 0x2029 || c == 0x202f || c == 0x205f || c == 0x3000;
    }
    /** s.split() — 공백 덩어리로 나눔(빈 조각 없음) */
    public static List<String> split(String s) {
        ArrayList<String> out = new ArrayList<>();
        int n = s.length(), i = 0;
        while (i < n) {
            while (i < n && isSpace(s.charAt(i))) i++;
            int j = i;
            while (j < n && !isSpace(s.charAt(j))) j++;
            if (j > i) out.add(s.substring(i, j));
            i = j;
        }
        return out;
    }
    /** s.split(sep) — 글자 그대로(정규식 아님) · 빈 조각 유지 */
    public static List<String> split(String s, String sep) {
        ArrayList<String> out = new ArrayList<>();
        int i = 0;
        while (true) {
            int j = s.indexOf(sep, i);
            if (j < 0) { out.add(s.substring(i)); return out; }
            out.add(s.substring(i, j));
            i = j + sep.length();
        }
    }
    /** sep.join(xs) */
    public static String join(String sep, Iterable<?> xs) {
        StringBuilder b = new StringBuilder();
        boolean f = true;
        for (Object x : xs) { if (!f) b.append(sep); f = false; b.append((String) x); }
        return b.toString();
    }
    /** s * n */
    public static String rep(String s, long n) { return n <= 0 ? "" : s.repeat((int) n); }
    /** len(x) */
    public static int len(Object o) {
        if (o instanceof String) return ((String) o).length();
        if (o instanceof Collection) return ((Collection<?>) o).size();
        if (o instanceof Map) return ((Map<?, ?>) o).size();
        if (o instanceof Object[]) return ((Object[]) o).length;
        throw new IllegalArgumentException("len 을 못 재는 값");
    }

    // ── 같음 · 차례 ──────────────────────────────────────
    /** a == b (파이썬) — 1 == 1.0 은 참, 목록 · 사전은 속까지 */
    public static boolean eq(Object a, Object b) {
        if (a == b) return true;
        if (a == null || b == null) return false;
        if (a instanceof Number && b instanceof Number) {
            if (isInt(a) && isInt(b)) return lng(a) == lng(b);
            return num(a) == num(b);
        }
        if (a instanceof Boolean && b instanceof Number) return num(a) == num(b);
        if (b instanceof Boolean && a instanceof Number) return num(a) == num(b);
        if (a instanceof List && b instanceof List) {
            List<?> x = (List<?>) a, y = (List<?>) b;
            if (x.size() != y.size()) return false;
            for (int i = 0; i < x.size(); i++) if (!eq(x.get(i), y.get(i))) return false;
            return true;
        }
        if (a instanceof Object[] && b instanceof Object[]) return eq(java.util.Arrays.asList((Object[]) a), java.util.Arrays.asList((Object[]) b));
        if (a instanceof Map && b instanceof Map) {
            Map<?, ?> x = (Map<?, ?>) a, y = (Map<?, ?>) b;
            if (x.size() != y.size()) return false;
            for (Map.Entry<?, ?> e : x.entrySet()) { if (!y.containsKey(e.getKey()) || !eq(e.getValue(), y.get(e.getKey()))) return false; }
            return true;
        }
        return a.equals(b);
    }

    /** 파이썬의 < 차례 : 수끼리 · 문자열끼리(코드 값 순) · 목록/튜플은 앞에서부터. None 은 견줄 수 없으므로 오류 */
    public static int cmp(Object a, Object b) {
        if (a instanceof Number && b instanceof Number) {
            if (isInt(a) && isInt(b)) return Long.compare(lng(a), lng(b));
            return Double.compare(num(a), num(b));
        }
        if (a instanceof Boolean || b instanceof Boolean) {
            if ((a instanceof Boolean || a instanceof Number) && (b instanceof Boolean || b instanceof Number)) return Double.compare(num(a), num(b));
        }
        if (a instanceof String && b instanceof String) return ((String) a).compareTo((String) b);
        if (a instanceof Object[]) a = java.util.Arrays.asList((Object[]) a);
        if (b instanceof Object[]) b = java.util.Arrays.asList((Object[]) b);
        if (a instanceof List && b instanceof List) {
            List<?> x = (List<?>) a, y = (List<?>) b;
            int n = Math.min(x.size(), y.size());
            for (int i = 0; i < n; i++) { if (!eq(x.get(i), y.get(i))) return cmp(x.get(i), y.get(i)); }
            return Integer.compare(x.size(), y.size());
        }
        throw new IllegalArgumentException("차례를 견줄 수 없는 값 : " + reprObj(a) + " · " + reprObj(b));
    }
    public static final Comparator<Object> CMP = Py::cmp;

    /** sorted(xs, key=…, reverse=…) — 안정 정렬(파이썬과 같음) */
    public static <T> List<T> sorted(Collection<T> xs, Function<? super T, ?> key, boolean reverse) {
        ArrayList<T> a = new ArrayList<>(xs);
        Comparator<T> c = (x, y) -> cmp(key.apply(x), key.apply(y));
        if (reverse) { java.util.Collections.reverse(a); a.sort(c); java.util.Collections.reverse(a); }   // 파이썬 reverse=True 는 같은 값의 원래 순서를 유지
        else a.sort(c);
        return a;
    }
    public static <T> List<T> sorted(Collection<T> xs, Function<? super T, ?> key) { return sorted(xs, key, false); }
    public static <T> List<T> sorted(Collection<T> xs) { return sorted(xs, x -> x, false); }

    // ── 정규식 ───────────────────────────────────────────
    public static final int I = Pattern.CASE_INSENSITIVE | Pattern.UNICODE_CASE, S = Pattern.DOTALL, MULTI = Pattern.MULTILINE;
    private static final int BASE_FLAGS = Pattern.UNICODE_CHARACTER_CLASS | Pattern.UNIX_LINES;
    private static final ConcurrentHashMap<String, Pattern> RX = new ConcurrentHashMap<>();

    /** re.compile(pat) — 파이썬 정규식을 자바 정규식으로 바꿔 한 번만 컴파일한다 */
    public static Pattern re(String pat) { return re(pat, 0); }
    public static Pattern re(String pat, int flags) {
        String k = flags + "\u0000" + pat;
        Pattern p = RX.get(k);
        if (p == null) { p = Pattern.compile(toJavaRegex(pat), BASE_FLAGS | flags); RX.put(k, p); }
        return p;
    }

    /**
     * 파이썬 정규식 → 자바 정규식. 다르게 읽히는 곳만 고친다 :
     *  · 글자 묶음 [...] 안의 맨 [ 와 && (자바는 묶음 속 묶음 · 교집합으로 읽는다) · 묶음 맨 앞의 ]
     *  · (?P&lt;이름&gt; → (?&lt;이름&gt; · (?P=이름) → \k&lt;이름&gt; · \Z → \z
     *  · 수량이 아닌 { } (자바는 오류)
     */
    public static String toJavaRegex(String p) {
        StringBuilder b = new StringBuilder(p.length() + 8);
        int n = p.length();
        boolean in = false;
        for (int i = 0; i < n; i++) {
            char c = p.charAt(i);
            if (c == '\\') {
                if (i + 1 < n) {
                    char d = p.charAt(i + 1);
                    if (d == 'Z') b.append("\\z");
                    else if (d == 'w') b.append(in ? "\\p{L}\\p{N}_" : "[\\p{L}\\p{N}_]");      // 파이썬 \w = 글자 · 수(①·Ⅱ 같은 수 글자 포함) · 밑줄(결합 부호는 아님)
                    else if (d == 'W' && !in) b.append("[^\\p{L}\\p{N}_]");
                    else b.append(c).append(d);
                    i++;
                } else b.append("\\\\");
                continue;
            }
            if (in) {
                if (c == ']') { in = false; b.append(c); }
                else if (c == '[') {
                    if (i + 1 < n && p.charAt(i + 1) == ':') b.append("\\[");   // 파이썬은 [:alpha:] 를 모른다 — 글자 그대로
                    else b.append("\\[");
                }
                else if (c == '&' && i + 1 < n && p.charAt(i + 1) == '&') { b.append("&\\&"); i++; }
                else b.append(c);
                continue;
            }
            if (c == '[') {
                in = true; b.append(c);
                if (i + 1 < n && p.charAt(i + 1) == '^') { b.append('^'); i++; }
                if (i + 1 < n && p.charAt(i + 1) == ']') { b.append("\\]"); i++; }
                continue;
            }
            if (c == '(' && p.startsWith("(?P<", i)) { b.append("(?<"); i += 3; continue; }
            if (c == '(' && p.startsWith("(?P=", i)) {
                int j = p.indexOf(')', i);
                b.append("\\k<").append(p, i + 4, j).append('>'); i = j; continue;
            }
            if (c == '{') {
                int j = i + 1;
                while (j < n && (Character.isDigit(p.charAt(j)) || p.charAt(j) == ',')) j++;
                boolean quant = j < n && p.charAt(j) == '}' && j > i + 1 && Character.isDigit(p.charAt(i + 1));
                b.append(quant ? "{" : "\\{");
                continue;
            }
            if (c == '}') {
                int j = b.length() - 1;                           // 바로 앞이 수량 {m,n 이면 그대로
                while (j >= 0 && (Character.isDigit(b.charAt(j)) || b.charAt(j) == ',')) j--;
                boolean quant = j >= 0 && b.charAt(j) == '{' && (j == 0 || b.charAt(j - 1) != '\\') && j < b.length() - 1;
                b.append(quant ? "}" : "\\}");
                continue;
            }
            b.append(c);
        }
        return b.toString();
    }

    /** re.search(pat, s) — 못 찾으면 null */
    public static Matcher search(String pat, String s) { return search(re(pat), s); }
    public static Matcher search(String pat, String s, int flags) { return search(re(pat, flags), s); }
    public static Matcher search(Pattern p, String s) { Matcher m = p.matcher(s); return m.find() ? m : null; }
    /** re.match(pat, s) — 맨 앞에서부터 */
    public static Matcher match(String pat, String s) { return match(re(pat), s); }
    public static Matcher match(Pattern p, String s) { Matcher m = p.matcher(s); return m.lookingAt() ? m : null; }
    /** re.fullmatch(pat, s) */
    public static Matcher fullmatch(String pat, String s) { return fullmatch(re(pat), s); }
    public static Matcher fullmatch(Pattern p, String s) { Matcher m = p.matcher(s); return m.matches() ? m : null; }
    /** bool(re.search(pat, s)) */
    public static boolean has(String pat, String s) { return re(pat).matcher(s).find(); }
    public static boolean has(Pattern p, String s) { return p.matcher(s).find(); }
    /** m.group(i) — 파이썬은 안 걸린 묶음이 None */
    public static String g(Matcher m, int i) { return m.group(i); }

    /** re.sub(pat, repl, s) — repl 은 파이썬 꼴(\1 · \g&lt;1&gt; · \g&lt;이름&gt; · \n) */
    public static String sub(String pat, String repl, String s) { return sub(re(pat), repl, s, 0); }
    public static String sub(Pattern p, String repl, String s) { return sub(p, repl, s, 0); }
    public static String sub(String pat, String repl, String s, int count) { return sub(re(pat), repl, s, count); }
    public static String sub(Pattern p, String repl, String s, int count) {
        if (repl.indexOf('\\') < 0) return subFn(p, m -> repl, s, count);
        return subFn(p, m -> expand(m, repl), s, count);
    }
    /** re.sub(pat, 함수, s) */
    public static String sub(String pat, Function<Matcher, String> f, String s) { return subFn(re(pat), f, s, 0); }
    public static String sub(Pattern p, Function<Matcher, String> f, String s) { return subFn(p, f, s, 0); }
    private static String subFn(Pattern p, Function<Matcher, String> f, String s, int count) {
        Matcher m = p.matcher(s);
        StringBuilder b = new StringBuilder();
        int last = 0, k = 0;
        while (m.find()) {
            b.append(s, last, m.start()).append(f.apply(m));
            last = m.end();
            if (count > 0 && ++k >= count) break;
        }
        return b.append(s, last, s.length()).toString();
    }
    private static String expand(Matcher m, String r) {
        StringBuilder b = new StringBuilder();
        int n = r.length();
        for (int i = 0; i < n; i++) {
            char c = r.charAt(i);
            if (c != '\\' || i + 1 >= n) { b.append(c); continue; }
            char d = r.charAt(++i);
            if (d >= '0' && d <= '9') {
                int g = d - '0';
                if (i + 1 < n && Character.isDigit(r.charAt(i + 1)) && (g * 10 + (r.charAt(i + 1) - '0')) <= m.groupCount()) g = g * 10 + (r.charAt(++i) - '0');
                String v = m.group(g);
                if (v != null) b.append(v);
            } else if (d == 'g' && i + 1 < n && r.charAt(i + 1) == '<') {
                int j = r.indexOf('>', i);
                String name = r.substring(i + 2, j);
                String v = name.chars().allMatch(Character::isDigit) ? m.group(Integer.parseInt(name)) : m.group(name);
                if (v != null) b.append(v);
                i = j;
            } else if (d == 'n') b.append('\n');
            else if (d == 't') b.append('\t');
            else if (d == 'r') b.append('\r');
            else if (d == '\\') b.append('\\');
            else b.append('\\').append(d);
        }
        return b.toString();
    }

    /**
     * re.findall(pat, s) — 묶음이 없으면 걸린 글자(String), 하나면 그 묶음(String · 안 걸렸으면 ""),
     * 둘 이상이면 List&lt;Object&gt;(묶음마다 · 안 걸렸으면 "")
     */
    public static List<Object> findall(String pat, String s) { return findall(re(pat), s); }
    public static List<Object> findall(Pattern p, String s) {
        ArrayList<Object> out = new ArrayList<>();
        Matcher m = p.matcher(s);
        int gc = m.groupCount();
        while (m.find()) {
            if (gc == 0) out.add(m.group());
            else if (gc == 1) out.add(m.group(1) == null ? "" : m.group(1));
            else {
                ArrayList<Object> t = new ArrayList<>(gc);
                for (int i = 1; i <= gc; i++) t.add(m.group(i) == null ? "" : m.group(i));
                out.add(t);
            }
        }
        return out;
    }
    /** re.split(pat, s) — 묶음이 있으면 그 글자도 끼워 넣는다(파이썬과 같음) */
    public static List<String> resplit(String pat, String s) { return resplit(re(pat), s); }
    public static List<String> resplit(Pattern p, String s) {
        ArrayList<String> out = new ArrayList<>();
        Matcher m = p.matcher(s);
        int last = 0;
        while (m.find()) {
            if (m.end() == m.start() && (m.start() == 0 || m.start() == s.length())) continue;   // 파이썬 3.7+ : 빈 걸림도 나누지만 양 끝은 빈 조각이 생김 — 쓰는 곳이 생기면 맞춘다
            out.add(s.substring(last, m.start()));
            for (int i = 1; i <= m.groupCount(); i++) out.add(m.group(i));
            last = m.end();
        }
        out.add(s.substring(last));
        return out;
    }
    /** re.escape(s) */
    public static String escape(String s) {
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if ("()[]{}?*+-|^$\\.&~# \t\n\r\u000b\f".indexOf(c) >= 0) b.append('\\');
            b.append(c);
        }
        return b.toString();
    }
}
