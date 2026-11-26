package meai.sp;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;

/** Py · Json 이 파이썬과 같은 글자를 내는지 — 정답은 golden/py_selftest.py 가 만든다. 사용 : PySelfTest <정답.json> */
public final class PySelfTest {
    static int bad = 0, n = 0;
    static void eq(String what, Object want, Object got) {
        n++;
        if (!Py.eq(want, got)) { bad++; if (bad <= 40) System.out.println("다름 [" + what + "] 파이썬=" + Py.reprObj(want) + " 자바=" + Py.reprObj(got)); }
    }
    public static void main(String[] a) throws Exception {
        System.setOut(new java.io.PrintStream(new java.io.FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8"));
        Map<String, Object> g = Py.M(Json.parse(Py.read(a[0])));
        for (Object o : Py.gl(g, "repr")) { List<Object> r = Py.L(o); eq("repr", r.get(1), Py.repr(Py.num(r.get(0)))); }
        for (Object o : Py.gl(g, "round0")) { List<Object> r = Py.L(o); eq("round " + r.get(0), r.get(1), Py.round(Py.num(r.get(0)))); }
        for (Object o : Py.gl(g, "round1")) { List<Object> r = Py.L(o); eq("round1 " + r.get(0), r.get(1), Py.round(Py.num(r.get(0)), 1)); }
        for (Object o : Py.gl(g, "round2")) { List<Object> r = Py.L(o); eq("round2 " + r.get(0), r.get(1), Py.round(Py.num(r.get(0)), 2)); }
        for (Object o : Py.gl(g, "fmt")) { List<Object> r = Py.L(o); eq("fmt " + r.get(0) + " " + Py.reprObj(r.get(1)), r.get(2), Py.fmt((String) r.get(0), Py.L(r.get(1)).toArray())); }
        for (Object o : Py.gl(g, "comma")) { List<Object> r = Py.L(o); eq("comma", r.get(1), Py.comma(r.get(0))); }
        for (Object o : Py.gl(g, "re")) {
            List<Object> r = Py.L(o); String p = (String) r.get(0), s = (String) r.get(1);
            List<Object> all = new ArrayList<>();
            Matcher m = Py.re(p).matcher(s);
            while (m.find()) all.add(m.group());
            eq("finditer " + p, r.get(2), all);
            eq("findall " + p, r.get(3), Py.findall(p, s));
            eq("sub " + p, r.get(4), Py.sub(p, "<\\g<0>>", s));
        }
        for (Object o : Py.gl(g, "sub")) { List<Object> r = Py.L(o); eq("sub " + r.get(0), r.get(3), Py.sub((String) r.get(0), (String) r.get(1), (String) r.get(2))); }
        for (Object o : Py.gl(g, "split")) { List<Object> r = Py.L(o); eq("split " + r.get(0), r.get(2), new ArrayList<Object>(Py.resplit((String) r.get(0), (String) r.get(1)))); }
        for (Object o : Py.gl(g, "str")) { List<Object> r = Py.L(o); eq("str", r.get(1), Py.str(r.get(0))); }
        for (Object o : Py.gl(g, "json")) {
            List<Object> r = Py.L(o);
            eq("json", r.get(1), Json.dumps(r.get(0))); eq("jsonU", r.get(2), Json.dumpsU(r.get(0))); eq("jsonC", r.get(3), Json.dumpsCompact(r.get(0)));
            eq("jsonI", r.get(4), Json.dumps(r.get(0), false, 1, ", ", ": ", false));
        }
        System.out.println(bad == 0 ? "결과 : 전부 통과 — 점검 " + n + "개" : "결과 : 다른 곳 " + bad + " / " + n);
        System.exit(bad == 0 ? 0 : 1);
    }
}
