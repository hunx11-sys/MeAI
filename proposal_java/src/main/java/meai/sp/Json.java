package meai.sp;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * JSON 읽기 · 쓰기(바깥 부품 없이).
 * 읽은 값의 꼴은 파이썬 json.load 와 같게 맞춘다 :
 *   object → LinkedHashMap&lt;String,Object&gt;(넣은 순서 유지) · array → ArrayList&lt;Object&gt; ·
 *   정수 → Long · 소수 → Double · true/false → Boolean · null → null
 * 쓰기(dumps)는 파이썬 json.dumps 기본 꼴(", " · ": " · ensure_ascii=True)과 글자까지 같게 낸다.
 */
public final class Json {
    private Json() {}

    // ── 읽기 ─────────────────────────────────────────────
    public static Object parse(String s) {
        P p = new P(s);
        p.ws();
        Object v = p.val();
        p.ws();
        if (p.i != s.length()) throw new IllegalArgumentException("JSON 뒤에 남는 글자 : " + p.i);
        return v;
    }

    private static final class P {
        final String s; int i = 0;
        P(String s) { this.s = (s.length() > 0 && s.charAt(0) == '﻿') ? s.substring(1) : s; }
        void ws() { while (i < s.length()) { char c = s.charAt(i); if (c == ' ' || c == '\n' || c == '\r' || c == '\t') i++; else break; } }
        Object val() {
            if (i >= s.length()) throw err("값이 없음");
            char c = s.charAt(i);
            switch (c) {
                case '{': return obj();
                case '[': return arr();
                case '"': return str();
                case 't': lit("true"); return Boolean.TRUE;
                case 'f': lit("false"); return Boolean.FALSE;
                case 'n': lit("null"); return null;
                default:
                    if (c == 'N' && s.startsWith("NaN", i)) { i += 3; return Double.NaN; }
                    if (c == 'I' && s.startsWith("Infinity", i)) { i += 8; return Double.POSITIVE_INFINITY; }
                    if (c == '-' && s.startsWith("-Infinity", i)) { i += 9; return Double.NEGATIVE_INFINITY; }
                    return num();
            }
        }
        void lit(String w) { if (!s.startsWith(w, i)) throw err("알 수 없는 값"); i += w.length(); }
        IllegalArgumentException err(String m) { return new IllegalArgumentException("JSON 오류(" + m + ") 위치 " + i); }
        Map<String, Object> obj() {
            LinkedHashMap<String, Object> m = new LinkedHashMap<>();
            i++; ws();
            if (i < s.length() && s.charAt(i) == '}') { i++; return m; }
            while (true) {
                ws();
                if (i >= s.length() || s.charAt(i) != '"') throw err("열쇠는 문자열");
                String k = str(); ws();
                if (i >= s.length() || s.charAt(i) != ':') throw err(": 없음");
                i++; ws();
                m.put(k, val()); ws();
                if (i >= s.length()) throw err("} 없음");
                char c = s.charAt(i++);
                if (c == '}') return m;
                if (c != ',') throw err(", 없음");
            }
        }
        List<Object> arr() {
            ArrayList<Object> a = new ArrayList<>();
            i++; ws();
            if (i < s.length() && s.charAt(i) == ']') { i++; return a; }
            while (true) {
                ws(); a.add(val()); ws();
                if (i >= s.length()) throw err("] 없음");
                char c = s.charAt(i++);
                if (c == ']') return a;
                if (c != ',') throw err(", 없음");
            }
        }
        String str() {
            StringBuilder b = new StringBuilder();
            i++;
            while (true) {
                if (i >= s.length()) throw err("문자열이 안 닫힘");
                char c = s.charAt(i++);
                if (c == '"') return b.toString();
                if (c != '\\') { b.append(c); continue; }
                if (i >= s.length()) throw err("\\ 뒤가 없음");
                char e = s.charAt(i++);
                switch (e) {
                    case '"': b.append('"'); break;
                    case '\\': b.append('\\'); break;
                    case '/': b.append('/'); break;
                    case 'b': b.append('\b'); break;
                    case 'f': b.append('\f'); break;
                    case 'n': b.append('\n'); break;
                    case 'r': b.append('\r'); break;
                    case 't': b.append('\t'); break;
                    case 'u': b.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); i += 4; break;
                    default: throw err("알 수 없는 \\" + e);
                }
            }
        }
        Object num() {
            int a = i; boolean fl = false;
            if (i < s.length() && s.charAt(i) == '-') i++;
            while (i < s.length()) {
                char c = s.charAt(i);
                if (c >= '0' && c <= '9') i++;
                else if (c == '.' || c == 'e' || c == 'E' || c == '+' || c == '-') { fl = true; i++; }
                else break;
            }
            String t = s.substring(a, i);
            if (t.isEmpty() || t.equals("-")) throw err("숫자가 아님");
            if (fl) return Double.valueOf(t);
            try { return Long.valueOf(t); } catch (NumberFormatException ex) { return new java.math.BigInteger(t); }
        }
    }

    // ── 쓰기 ─────────────────────────────────────────────
    /** json.dumps(o) — ensure_ascii=True, separators (', ', ': ') */
    public static String dumps(Object o) { return dumps(o, true, null, ", ", ": ", false); }
    /** json.dumps(o, ensure_ascii=False) */
    public static String dumpsU(Object o) { return dumps(o, false, null, ", ", ": ", false); }
    /** json.dumps(o, ensure_ascii=False, separators=(',', ':')) */
    public static String dumpsCompact(Object o) { return dumps(o, false, null, ",", ":", false); }
    /** json.dumps(o, ensure_ascii=…, indent=…, sort_keys=…) — indent 가 null 이 아니면 파이썬처럼 줄 끝 구분자는 "," */
    public static String dumps(Object o, boolean ensureAscii, Integer indent, String itemSep, String keySep, boolean sortKeys) {
        StringBuilder b = new StringBuilder();
        if (indent != null && itemSep.equals(", ")) itemSep = ",";
        w(b, o, ensureAscii, indent, itemSep, keySep, sortKeys, 0);
        return b.toString();
    }

    private static void nl(StringBuilder b, Integer indent, int lv) {
        if (indent == null) return;
        b.append('\n');
        for (int k = 0; k < indent * lv; k++) b.append(' ');
    }

    @SuppressWarnings("unchecked")
    private static void w(StringBuilder b, Object o, boolean ea, Integer indent, String is, String ks, boolean sort, int lv) {
        if (o == null) { b.append("null"); return; }
        if (o instanceof Boolean) { b.append(((Boolean) o) ? "true" : "false"); return; }
        if (o instanceof String) { q(b, (String) o, ea); return; }
        if (o instanceof Double || o instanceof Float) {
            double d = ((Number) o).doubleValue();
            if (Double.isNaN(d)) b.append("NaN");
            else if (Double.isInfinite(d)) b.append(d > 0 ? "Infinity" : "-Infinity");
            else b.append(Py.repr(d));
            return;
        }
        if (o instanceof Number) { b.append(o.toString()); return; }
        if (o instanceof Map) {
            Map<Object, Object> m = (Map<Object, Object>) o;
            if (m.isEmpty()) { b.append("{}"); return; }
            List<Object> keys = new ArrayList<>(m.keySet());
            if (sort) keys.sort((x, y) -> Py.str(x).compareTo(Py.str(y)));
            b.append('{');
            boolean first = true;
            for (Object k : keys) {
                if (!first) b.append(is);
                first = false;
                nl(b, indent, lv + 1);
                q(b, keyStr(k), ea); b.append(ks);
                w(b, m.get(k), ea, indent, is, ks, sort, lv + 1);
            }
            nl(b, indent, lv);
            b.append('}');
            return;
        }
        if (o instanceof Iterable) {
            b.append('[');
            boolean first = true, any = false;
            for (Object x : (Iterable<Object>) o) {
                if (!first) b.append(is);
                first = false; any = true;
                nl(b, indent, lv + 1);
                w(b, x, ea, indent, is, ks, sort, lv + 1);
            }
            if (any) nl(b, indent, lv);
            b.append(']');
            return;
        }
        if (o instanceof Object[]) { w(b, java.util.Arrays.asList((Object[]) o), ea, indent, is, ks, sort, lv); return; }
        throw new IllegalArgumentException("JSON 으로 못 쓰는 값 : " + o.getClass());
    }

    private static String keyStr(Object k) {
        if (k == null) return "null";
        if (k instanceof Boolean) return ((Boolean) k) ? "true" : "false";
        if (k instanceof Double) return Py.repr((Double) k);
        return k.toString();
    }

    private static void q(StringBuilder b, String s, boolean ea) {
        b.append('"');
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '"': b.append("\\\""); break;
                case '\\': b.append("\\\\"); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                case '\b': b.append("\\b"); break;
                case '\f': b.append("\\f"); break;
                default:
                    if (c < 0x20 || (ea && c > 0x7e)) b.append(String.format("\\u%04x", (int) c));
                    else b.append(c);
            }
        }
        b.append('"');
    }
}
