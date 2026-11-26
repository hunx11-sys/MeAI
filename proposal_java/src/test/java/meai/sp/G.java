package meai.sp;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.Map;

/** 정답지 대조 공용 — 값 · 차례 · 수 꼴(정수/소수)까지 엄격하게 견준다 */
final class G {
    private G() {}
    static int bad = 0, n = 0, shown = 0, MAXSHOW = 60;

    static void utf8() {
        try { System.setOut(new java.io.PrintStream(new java.io.FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8")); }
        catch (java.io.UnsupportedEncodingException e) { throw new RuntimeException(e); }
    }
    static String cut(String s) { return s.length() > 300 ? s.substring(0, 300) + "…" : s; }

    /** 같으면 null, 다르면 「어디가 어떻게」 */
    static String diff(Object want, Object got, String path) {
        if (got instanceof Object[]) got = Arrays.asList((Object[]) got);
        if (want instanceof Object[]) want = Arrays.asList((Object[]) want);
        if (want == null || got == null) return (want == null && got == null) ? null : path + " : 파이썬=" + cut(Py.reprObj(want)) + " 자바=" + cut(Py.reprObj(got));
        if (want instanceof Boolean || got instanceof Boolean)
            return (want instanceof Boolean && got instanceof Boolean && want.equals(got)) ? null : path + " : 파이썬=" + cut(Py.reprObj(want)) + " 자바=" + cut(Py.reprObj(got));
        if (want instanceof Number || got instanceof Number) {
            boolean ok = want instanceof Number && got instanceof Number && Py.isInt(want) == Py.isInt(got)
                    && (Py.isInt(want) ? Py.lng(want) == Py.lng(got) : Double.compare(Py.num(want), Py.num(got)) == 0);
            return ok ? null : path + " : 파이썬=" + Py.reprObj(want) + (Py.isInt(want) ? "(정수)" : "(소수)") + " 자바=" + cut(Py.reprObj(got)) + (got instanceof Number ? (Py.isInt(got) ? "(정수)" : "(소수)") : "");
        }
        if (want instanceof String || got instanceof String)
            return want.equals(got) ? null : path + " : 파이썬=" + cut(Py.reprObj(want)) + " 자바=" + cut(Py.reprObj(got));
        if (want instanceof List) {
            if (!(got instanceof List)) return path + " : 파이썬은 목록, 자바=" + cut(Py.reprObj(got));
            List<?> a = (List<?>) want, b = (List<?>) got;
            if (a.size() != b.size()) {
                int k = 0;
                while (k < Math.min(a.size(), b.size()) && diff(a.get(k), b.get(k), "") == null) k++;
                return path + " : 길이 파이썬 " + a.size() + " · 자바 " + b.size() + " (처음 다른 자리 " + k + " : 파이썬=" + cut(k < a.size() ? Py.reprObj(a.get(k)) : "없음") + " 자바=" + cut(k < b.size() ? Py.reprObj(b.get(k)) : "없음") + ")";
            }
            for (int i = 0; i < a.size(); i++) { String d = diff(a.get(i), b.get(i), path + "[" + i + "]"); if (d != null) return d; }
            return null;
        }
        if (want instanceof Map) {
            if (!(got instanceof Map)) return path + " : 파이썬은 사전, 자바=" + cut(Py.reprObj(got));
            Map<?, ?> a = (Map<?, ?>) want, b = (Map<?, ?>) got;
            List<Object> ka = new ArrayList<>(a.keySet()), kb = new ArrayList<>(b.keySet());
            if (!ka.equals(kb)) return path + " : 열쇠(차례 포함) 파이썬=" + cut(ka.toString()) + " 자바=" + cut(kb.toString());
            Iterator<?> it = ka.iterator();
            while (it.hasNext()) { Object k = it.next(); String d = diff(a.get(k), b.get(k), path + "." + k); if (d != null) return d; }
            return null;
        }
        return want.equals(got) ? null : path + " : 꼴이 다름 " + want.getClass() + " · " + got.getClass();
    }

    static boolean same(String what, Object want, Object got) {
        n++;
        String d = diff(want, got, "");
        if (d == null) return true;
        bad++;
        if (shown++ < MAXSHOW) System.out.println("다름 [" + what + "]" + d);
        return false;
    }
    /** 규칙 · 마스터 Map 에 든 Pattern 등 JSON 에 없는 값은 빼고 본다 */
    static void finish(String title) {
        System.out.println(bad == 0 ? "결과 : 전부 통과 — " + title + " 점검 " + n + "개" : "결과 : 다른 곳 " + bad + " / " + n + " — " + title);
        System.exit(bad == 0 ? 0 : 1);
    }
}
