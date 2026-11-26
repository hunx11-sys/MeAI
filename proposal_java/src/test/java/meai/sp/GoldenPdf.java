package meai.sp;

import java.io.File;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

/**
 * 5단계 정답지 대조(자바 쪽) — 파이썬 판이 브라우저에 넘긴 HTML(golden/dump_html.py 가 받아 적은 것)을 그대로 넣어
 * 자바 조립(Render · PdfKit.assemble)으로 PDF 를 만든다. 쪽수 · 배율(fit) · 경고가 파이썬과 같은지 여기서 보고,
 * 글자 · 픽셀 · 파일 크기는 golden/cmp_pdf.py 가 두 PDF 를 놓고 견준다.
 * 사용 : GoldenPdf <정답지 폴더> <출력 폴더> [이름 …]      (이름을 안 주면 폴더의 *.golden.json 전부)
 */
public final class GoldenPdf {
    public static void main(String[] a) throws Exception {
        System.setOut(new java.io.PrintStream(new java.io.FileOutputStream(java.io.FileDescriptor.out), true, "UTF-8"));
        String gdir = a[0], odir = a[1];
        new File(odir).mkdirs();
        List<String> names = new ArrayList<>();
        if (a.length > 2) names.addAll(Arrays.asList(a).subList(2, a.length));
        else for (String f : new File(gdir).list()) if (f.endsWith(".golden.json")) names.add(f.substring(0, f.length() - ".golden.json".length()));
        java.util.Collections.sort(names);
        Map<String, Object> fonts = Py.M(Json.parse(Py.read(gdir + "/fonts.json")));
        String FONTS = Py.gs(fonts, "fonts_css"), NOTO = Py.gs(fonts, "noto_css");
        int bad = 0, n = 0;
        for (String nm : names) {
            Map<String, Object> g = Py.M(Json.parse(Py.read(gdir + "/" + nm + ".golden.json")));
            if (!Py.truthy(g.get("ok"))) { System.out.println(Py.fmt("%-34s 건너뜀(파이썬 판이 만들지 않은 입력)", nm)); continue; }
            java.util.HashMap<String, String> H = new java.util.HashMap<>();
            for (Object o : Py.gl(g, "htmls")) { List<Object> x = Py.L(o); H.put((String) x.get(0), ((String) x.get(1)).replace("@@NOTO@@", NOTO).replace("@@FONTS@@", FONTS)); }
            Map<String, Object> info = Py.gm(g, "info");
            long t0 = System.currentTimeMillis();
            String out = odir + "/" + nm + ".java.pdf";
            long gn = Py.lng(info.get("detail_pages"));
            Map<String, Object> r = PdfKit.build_from_html(nm, out, H.get("cs"), H.get("ov"), H.get("html"), H.get("detail"), k -> {
                if (k != gn) throw new RuntimeException("세부내역 쪽수가 파이썬과 다름 : 자바 " + k + " · 파이썬 " + gn);
                return H.get("dov");
            });
            double sec = (System.currentTimeMillis() - t0) / 1000.0;
            List<String> diff = new ArrayList<>();
            if (!Py.eq(r.get("pages"), info.get("pages"))) diff.add("쪽수 " + r.get("pages") + " ≠ " + info.get("pages"));
            if (!Py.eq(r.get("detail_pages"), info.get("detail_pages"))) diff.add("세부내역 쪽수 " + r.get("detail_pages") + " ≠ " + info.get("detail_pages"));
            if (!Json.dumpsU(r.get("fit")).equals(Json.dumpsU(info.get("fit")))) diff.add("fit " + Json.dumpsU(r.get("fit")) + " ≠ " + Json.dumpsU(info.get("fit")));
            if (!Json.dumpsU(r.get("warn")).equals(Json.dumpsU(info.get("warn")))) diff.add("warn " + Json.dumpsU(r.get("warn")) + " ≠ " + Json.dumpsU(info.get("warn")));
            r.put("sec", Py.round(sec, 1)); r.put("diff", new ArrayList<Object>(diff));
            Py.write(odir + "/" + nm + ".java.json", Json.dumpsU(r));
            n++; if (!diff.isEmpty()) bad++;
            System.out.println(Py.fmt("%-34s %s · %d쪽 · 세부내역 %d쪽 · %.1f초 · %.2fMB%s", nm, diff.isEmpty() ? "같음" : "다름", r.get("pages"), r.get("detail_pages"), sec,
                    new File(out).length() / 1048576.0, diff.isEmpty() ? "" : "  ← " + String.join(" / ", diff)));
        }
        Render.close_browser();
        System.out.println(bad == 0 ? "결과 : 전부 통과 — " + n + "건(쪽수 · 배율 · 경고)" : "결과 : 다른 건 " + bad + " / " + n);
        System.exit(bad == 0 ? 0 : 1);
    }
}
