package meai.sp;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 4단계 정답지 대조 — 자바가 만든 쪽별 HTML 이 파이썬 판(golden/dump_html.py)과 글자 하나까지 같은지 + info · 로그 · EXTRA · 칸 값 · 담보 줄.
 * 사용 : GoldenHtml &lt;정답 폴더&gt; &lt;입력 JSON 폴더&gt; &lt;자바 PDF 를 둘 폴더&gt; [이름 …]      (환경변수 GA_CODE_MAP 은 정답지를 뽑을 때와 같게)
 * 완성 PDF 는 &lt;자바 PDF 폴더&gt;/&lt;이름&gt;.java.pdf(+ .java.json) 로 남는다 — golden/cmp_pdf.py · golden/verify_java_pdf.py 가 이어서 견준다.
 */
public final class GoldenHtml {
    static String strip(String h, String fonts, String noto) { return (noto.isEmpty() ? h : h.replace(noto, "@@NOTO@@")).replace(fonts, "@@FONTS@@"); }

    static void htmlSame(String what, String want, String got) {
        G.n++;
        if (want.equals(got)) return;
        G.bad++;
        int i = 0, n = Math.min(want.length(), got.length());
        while (i < n && want.charAt(i) == got.charAt(i)) i++;
        if (G.shown++ < G.MAXSHOW)
            System.out.println("다름 [" + what + "] " + i + "번째 글자부터(길이 파이썬 " + want.length() + " · 자바 " + got.length() + ")\n   파이썬 …" + want.substring(Math.max(0, i - 80), Math.min(want.length(), i + 80))
                    + "…\n   자바   …" + got.substring(Math.max(0, i - 80), Math.min(got.length(), i + 80)) + "…");
    }

    /** 파이썬 dump 의 plain() 과 같은 꼴로 — Object[] → 목록 · Set → 정렬한 목록 · 그 밖(Pattern 등) → 글자 */
    @SuppressWarnings("unchecked")
    static Object plain(Object o) {
        if (o == null || o instanceof String || o instanceof Number || o instanceof Boolean) return o;
        if (o instanceof Object[]) { List<Object> a = new ArrayList<>(); for (Object x : (Object[]) o) a.add(plain(x)); return a; }
        if (o instanceof Map) { Map<String, Object> m = new LinkedHashMap<>(); for (Map.Entry<Object, Object> e : ((Map<Object, Object>) o).entrySet()) m.put(String.valueOf(e.getKey()), plain(e.getValue())); return m; }
        if (o instanceof java.util.Set) { List<Object> a = new ArrayList<>(); for (Object x : Py.sorted((java.util.Set<Object>) o)) a.add(plain(x)); return a; }
        if (o instanceof Iterable) { List<Object> a = new ArrayList<>(); for (Object x : (Iterable<Object>) o) a.add(plain(x)); return a; }
        return Py.str(o);
    }

    public static void main(String[] a) throws Exception {
        G.utf8();
        String gdir = a[0], idir = a[1], odir = a[2];
        List<String> only = Arrays.asList(a).subList(3, a.length);
        new File(odir).mkdirs();
        Map<String, Object> fj = Py.M(Json.parse(Py.read(gdir + "/fonts.json")));
        String FONTS = GaV2.fonts_css(), NOTO = GaV2.noto_css();
        G.same("fonts_css", fj.get("fonts_css"), FONTS);
        G.same("noto_css", fj.get("noto_css"), NOTO);
        G.same("FIT_JS", Txt.FIT_JS, Render.FIT_JS);
        G.same("CLIP_JS", Txt.CLIP_JS, Render.CLIP_JS);
        String[] files = new File(gdir).list((d, n) -> n.endsWith(".golden.json"));
        Arrays.sort(files);
        int done = 0;
        long t00 = System.currentTimeMillis();
        for (String fn : files) {
            String name = fn.substring(0, fn.length() - ".golden.json".length());
            if (!only.isEmpty() && !only.contains(name)) continue;
            Map<String, Object> g = Py.M(Json.parse(Py.read(gdir + "/" + fn)));
            String in = idir + "/" + name + ".json";
            if (!new File(in).exists()) in = Py.path("ga_docs", name + ".json");
            if (!new File(in).exists()) { System.out.println("입력 없음 : " + name); G.bad++; continue; }
            long t0 = System.currentTimeMillis();
            int bad0 = G.bad;
            if (!Py.truthy(g.get("ok"))) {
                String err = null;
                try { GaV2.build(CodeInput.parse(Py.read(in)), odir + "/" + name + ".java.pdf"); }
                catch (RuntimeException ex) { err = ex.getMessage(); }
                G.same(name + " 오류 글자", g.get("error"), err);
            } else {
                Map<String, Object> p = CodeInput.parse(Py.read(in));
                Object[] r = GaV2.build(p, odir + "/" + name + ".java.pdf");
                List<Object> gh = Py.gl(g, "htmls");
                G.same(name + " html 개수", (long) gh.size(), (long) GaV2.LAST_HTML.size());
                for (int i = 0; i < Math.min(gh.size(), GaV2.LAST_HTML.size()); i++) {
                    List<Object> w = Py.L(gh.get(i));
                    String[] j = GaV2.LAST_HTML.get(i);
                    G.same(name + " html 이름", w.get(0), j[0]);
                    htmlSame(name + " · " + w.get(0), (String) w.get(1), strip(j[1], FONTS, NOTO));
                }
                Map<String, Object> info = new LinkedHashMap<>(Py.M(r[2]));
                info.remove("sec");
                G.same(name + " info", g.get("info"), plain(info));
                Py.write(odir + "/" + name + ".java.json", Json.dumpsU(plain(info)));
                String lg = Py.sub("[\\d.]+초\\n", "초\n", Py.read((String) r[1]), 1), lw = Py.sub("[\\d.]+초\\n", "초\n", (String) g.get("log"), 1);
                G.same(name + " log", lw, lg);
                G.same(name + " extra", g.get("extra"), plain(GaV2.EXTRA));
                Map<String, Object> val = new LinkedHashMap<>();
                for (Map.Entry<String, Object[]> e : GaProposal.VAL.entrySet()) val.put(e.getKey(), Py.list(plain(e.getValue()[0]), plain(e.getValue()[1])));
                G.same(name + " val", g.get("val"), val);
                G.same(name + " rid", g.get("rid"), plain(GaProposal.RID));
                G.same(name + " product", g.get("product"), GaProposal.PRODUCT);
                G.same(name + " premium", g.get("premium"), GaProposal.PREMIUM);
                G.same(name + " nrid", g.get("nrid"), GaProposal.NRID);
                G.same(name + " issues", g.get("issues"), plain(ScenEngine.issues_grouped()));
            }
            done++;
            System.out.println(String.format("%-34s %s · %.1f초", name, G.bad == bad0 ? "같음" : "다른 곳 " + (G.bad - bad0), (System.currentTimeMillis() - t0) / 1000.0));
        }
        Render.close_browser();
        System.out.println("설계 " + done + "건 · " + (System.currentTimeMillis() - t00) / 1000 + "초");
        G.finish("4단계(쪽별 HTML · info · 로그 · EXTRA · 칸 값 · 담보 줄)");
    }
}
