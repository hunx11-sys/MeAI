package meai.sp;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * 파이썬 ga_overlay.py — GA 디자인 가안 그림 위에 글자만 얹는 지면(합성 방식) 중 새 양식(GaV2)이 쓰는 것.
 * 틀 그림(tpl_&lt;page&gt;.png)을 새로 굽는 일(파이썬 template 의 PIL 그리기)은 옮기지 않는다 — 자료 폴더에 구워 둔 그림을 그대로 쓴다.
 */
public final class GaOverlay {
    private GaOverlay() {}

    public static final String MOCK = Py.path("ga_assets", "mock");
    public static final long W = 1414, H = 2000;                    // 가안 픽셀
    public static final double MM_X = 210.0 / W, MM_Y = 297.0 / H;   // px → mm
    public static final double PX_PT = 0.1485 * 72 / 25.4;          // 가안 1px 의 글자 크기를 pt 로 (1px = 0.1485mm)

    public static boolean available() {
        if (!new File(MOCK).isDirectory()) return false;
        for (String f : new String[]{"cover1.jpg", "p1.jpg", "p2.jpg", "p3.jpg", "p4.jpg", "overlay_p1.json"}) if (!Py.exists(MOCK + File.separator + f)) return false;
        return true;
    }

    public static Map<String, Object> spec(String page) {
        String p = MOCK + File.separator + Py.fmt("overlay_%s.json", page);
        if (Py.exists(p)) return Py.M(Json.parse(Py.read(p)));
        return Py.dict("page", page, "size", Py.list(W, H), "fields", new LinkedHashMap<String, Object>());
    }

    private static final Map<String, List<Object>> _FB = new LinkedHashMap<>();
    /** 꼬리 오른쪽 블록(「소속 : … | 코드 : … | 소속 : …」) 전체 상자 — ft.* 값 상자의 띠에서 왼쪽으로 첫 글자가 나오는 곳까지 */
    public static List<Object> footer_box(String page, Map<String, Object> sp0) {
        Map<String, Object> sp = sp0 != null ? sp0 : Py.gm(spec(page), "fields");
        List<List<Object>> bs = new ArrayList<>();
        for (String k : sp.keySet()) if (k.startsWith("ft.")) bs.add(Py.gl(sp.get(k), "box"));
        if (bs.isEmpty()) return null;
        Object y1 = bs.get(0).get(1), y2 = bs.get(0).get(3), x2m = bs.get(0).get(2), xs0 = bs.get(0).get(0);
        for (List<Object> b : bs) { y1 = Py.min2(y1, b.get(1)); y2 = Py.max2(y2, b.get(3)); x2m = Py.max2(x2m, b.get(2)); xs0 = Py.min2(xs0, b.get(0)); }
        Object x2 = Py.add(x2m, 8L);
        String ck = page + "|" + Py.reprObj(bs);
        List<Object> hit = _FB.get(ck);
        if (hit != null) return new ArrayList<>(hit);
        BufferedImage im;
        try { im = javax.imageio.ImageIO.read(new File(MOCK, page + ".jpg")); } catch (IOException ex) { throw new RuntimeException("가안 그림을 읽지 못함 : " + page + ".jpg", ex); }
        Object xs = xs0;
        int gap = 0;                                  // ft 상자 왼쪽으로 가며 빈 칸이 40px 이어지는 곳 = 왼쪽 안내 문구와의 경계
        int ya = (int) Py.toInt(y1), yb = (int) Py.toInt(y2);
        for (int x = (int) Py.toInt(xs0) - 1; x > 600; x--) {
            boolean dark = false;
            for (int y = ya; y < yb; y++) if (luma(im.getRGB(x, y)) < 150) { dark = true; break; }
            if (dark) { xs = (long) x; gap = 0; }
            else { gap++; if (gap >= 40) break; }
        }
        List<Object> out = Py.list(Py.sub(xs, 8L), Py.sub(y1, 2L), Py.min2((Object) W, Py.add(x2, 4L)), Py.add(y2, 2L));
        _FB.put(ck, out);
        return new ArrayList<>(out);
    }
    /** PIL convert('L') : L = R*299/1000 + G*587/1000 + B*114/1000(정수 셈) */
    static int luma(int rgb) {
        int r = (rgb >> 16) & 255, g = (rgb >> 8) & 255, b = rgb & 255;
        return (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16;
    }

    /** 가안 그림에서 값 자리의 견본 글자를 지운 틀 그림(png) 경로 — 구워 둔 것을 쓴다(없으면 파이썬 판에서 한 번 만든다) */
    public static String template(String page) {
        String out = MOCK + File.separator + Py.fmt("tpl_%s.png", page);
        if (!Py.exists(out)) throw new RuntimeException("틀 그림이 없습니다 : " + out + " — 파이썬 판(ga_overlay.template)으로 한 번 만들어 자료 폴더에 넣어 주세요");
        return out;
    }

    public static String page_css() {
        return ".mockpg{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;background-size:210mm 297mm;background-repeat:no-repeat;background-color:#fff}"
                + ".ov{position:absolute;display:flex;align-items:center;white-space:nowrap;line-height:1;letter-spacing:-.3pt;font-family:\"Pretendard\",\"GANG\",\"Malgun Gothic\",sans-serif}"
                + ".ov.l{justify-content:flex-start} .ov.r{justify-content:flex-end} .ov.c{justify-content:center} .ov i{font-style:normal;margin-left:1px}"
                + ".ov.wrap{white-space:normal;line-height:1.18;word-break:keep-all;align-items:center}";
    }

    public static String page_open(String page) { return page_open(page, ""); }
    public static String page_open(String page, String cls) {
        return Py.fmt("<div class=\"page mockpg %s\" style=\"background-image:url('%s')\">", cls, Py.as_uri(template(page)));
    }

    /** 파이썬 str.isdigit() — 십진 숫자 + 위 첨자 · 동그라미 숫자 같은 「숫자 글자」 */
    static boolean isdigit(int c) {
        if (Character.isDigit(c)) return true;
        return c == 0xB2 || c == 0xB3 || c == 0xB9 || (c >= 0x2070 && c <= 0x2079 && c != 0x2071 && c != 0x2072 && c != 0x2073) || (c >= 0x2080 && c <= 0x2089)
                || (c >= 0x2460 && c <= 0x2468) || (c >= 0x2474 && c <= 0x247C) || (c >= 0x2488 && c <= 0x2490) || c == 0x24EA || (c >= 0x24F5 && c <= 0x24FD) || c == 0x24FF
                || (c >= 0x2776 && c <= 0x277E) || (c >= 0x2780 && c <= 0x2788) || (c >= 0x278A && c <= 0x2792) || (c >= 0x1369 && c <= 0x1371);
    }
    /** 글자 폭 어림(px · Pretendard 기준 가정값) — 한글 0.95em · 숫자·영문 0.58em · 쉼표·점 0.3em · 빈칸 0.28em */
    public static double est_width(String text, double font_px, String unit, Object unit_px) {
        double w = 0.0;
        for (int i = 0; i < text.length(); ) {
            int ch = text.codePointAt(i); i += Character.charCount(ch);
            if (ch == ',' || ch == '.') w += 0.3;
            else if (ch == ' ') w += 0.28;
            else if (isdigit(ch) || ch < 128) w += 0.58;
            else w += 0.95;
        }
        w *= font_px;
        if (Py.truthy(unit)) w += (Py.truthy(unit_px) ? Py.num(unit_px) : font_px * 0.62) * 0.95 * unit.codePointCount(0, unit.length()) + 2;
        return w;
    }
    /** 상자 폭에 맞게 글자 크기를 줄인 상자 사본 */
    public static Map<String, Object> fit(Map<String, Object> f, String text) { return fit(f, text, null); }
    public static Map<String, Object> fit(Map<String, Object> f, String text, String unit) {
        Map<String, Object> ff = new LinkedHashMap<>(f);
        List<Object> box = Py.gl(f, "box");
        double bw = Py.num(Py.sub(Py.sub(box.get(2), box.get(0)), 4L));
        double w = est_width(text, Py.num(Py.get(f, "font_px", 24L)), unit, f.get("unit_font_px"));
        if (w > bw && w > 0) {
            double k = Math.max(0.55, bw / w);
            ff.put("font_px", Py.num(Py.get(f, "font_px", 24L)) * k);
            if (Py.truthy(f.get("unit_font_px"))) ff.put("unit_font_px", Py.num(f.get("unit_font_px")) * k);
        }
        return ff;
    }

    /** 상자(f) 자리에 inner(HTML)를 놓는다 */
    public static String field_html(Map<String, Object> f, String inner) { return field_html(f, inner, ""); }
    public static String field_html(Map<String, Object> f, String inner, String cls) {
        List<Object> box = Py.gl(f, "box");
        double x1 = Py.num(box.get(0)), y1 = Py.num(box.get(1)), x2 = Py.num(box.get(2)), y2 = Py.num(box.get(3));
        double fpx = Py.num(Py.get(f, "font_px", 24L));
        double upx = f.containsKey("unit_font_px") ? Py.num(f.get("unit_font_px")) : Math.max(12, fpx * 0.62);
        String st = Py.fmt("left:%.2fmm;top:%.2fmm;width:%.2fmm;height:%.2fmm;font-size:%.2fpt;font-weight:%d;color:%s;--u:%.2fpt;--uc:%s;--na:%s",
                x1 * MM_X, y1 * MM_Y, (x2 - x1) * MM_X, (y2 - y1) * MM_Y, fpx * PX_PT, Py.get(f, "weight", 700L), Py.get(f, "color", "#111111"),
                upx * PX_PT, Py.get(f, "unit_color", "#111111"), Py.get(f, "na_color", "#C4C4C4"));
        if (Py.truthy(f.get("na_font_px"))) st += Py.fmt(";--naf:%.2fpt", Py.num(f.get("na_font_px")) * PX_PT);
        String a = (String) Py.get(f, "align", "right");
        String al = "left".equals(a) ? "l" : ("center".equals(a) ? "c" : "r");
        return Py.fmt("<div class=\"ov %s %s\" style=\"%s\">%s</div>", al, cls, st, inner);
    }

    /** 표지·머리·꼬리의 글(상품명 · 피보험자 · 번호 …). 긴 상품명은 줄바꿈(shrink_over), 그 밖은 한 줄로 상자에 맞게 줄인다 */
    public static String text_html(String s, Map<String, Object> f, String unit, Long shrink_over) {
        String cls = "";
        Map<String, Object> ff;
        int len = s.codePointCount(0, s.length());
        if (shrink_over != null && shrink_over != 0 && len > shrink_over) {
            ff = new LinkedHashMap<>(f);
            ff.put("font_px", Py.num(Py.get(f, "font_px", 24L)) * Math.max(0.7, shrink_over / (double) len));
            cls = "wrap";
        } else ff = fit(f, s, unit);
        String inner = s + (Py.truthy(unit) ? Py.fmt("<i style=\"font-size:var(--u);color:var(--uc);font-weight:500\">%s</i>", unit) : "");
        return field_html(ff, inner, cls);
    }

    /** 연한 회색(미가입 글자색)인가 */
    public static boolean is_light(Object hexcolor) {
        try {
            String h = Py.lstrip((String) hexcolor, "#");
            int r = Integer.parseInt(h.substring(0, 2), 16), g = Integer.parseInt(h.substring(2, 4), 16), b = Integer.parseInt(h.substring(4, 6), 16);
            return Math.min(r, Math.min(g, b)) > 0xA8;
        } catch (RuntimeException ex) { return false; }
    }
    private static String rsplit1(String k) { int i = k.lastIndexOf('.'); return i < 0 ? k : k.substring(0, i); }
    private static final String[] STYLE_KEYS = {"font_px", "weight", "color", "unit_font_px", "unit_color"};
    /**
     * 칸 값의 종류에 맞는 상자 스타일 — 가안 견본이 「미가입」(연회색 · 작은 글자)이던 칸에 숫자가 오면 같은 표의 이웃 칸(숫자 스타일)을 빌리고,
     * 숫자 칸에 「미가입」이 오면 이웃 미가입 칸의 글자 크기를 na_font_px 로 준다
     */
    public static Map<String, Object> style_for(Map<String, Object> sp, String key, Object v) {
        Map<String, Object> f = new LinkedHashMap<>(Py.M(sp.get(key)));
        boolean light = is_light(Py.get(f, "color", "#111111"));
        String pre = rsplit1(key);
        List<Map<String, Object>> sib = new ArrayList<>();
        for (Map.Entry<String, Object> e : sp.entrySet()) if (!e.getKey().equals(key) && rsplit1(e.getKey()).equals(pre)) sib.add(Py.M(e.getValue()));
        if (sib.isEmpty()) {
            String pre2 = rsplit1(pre);
            for (Map.Entry<String, Object> e : sp.entrySet()) if (!e.getKey().equals(key) && e.getKey().startsWith(pre2 + ".")) sib.add(Py.M(e.getValue()));
        }
        if (v == null || v instanceof String) {
            if (!light && v == null) {
                Map<String, Object> g = null;
                for (Map<String, Object> x : sib) if (is_light(Py.get(x, "color", ""))) { g = x; break; }
                f.put("na_font_px", g != null ? g.get("font_px") : (Object) (Py.num(Py.get(f, "font_px", 24L)) * 0.72));
            }
            if (v instanceof String && light) {
                Map<String, Object> g = null;
                for (Map<String, Object> x : sib) if (!is_light(Py.get(x, "color", ""))) { g = x; break; }
                if (g != null) for (String k2 : STYLE_KEYS) if (g.containsKey(k2)) f.put(k2, g.get(k2));
            }
            return f;
        }
        if (light) {                                   // 숫자가 올 자리인데 견본은 미가입 → 이웃 숫자 칸 스타일(검정 우선, 없으면 빨강)
            Map<String, Object> g = null;
            for (Map<String, Object> x : sib) {
                String c = ((String) Py.get(x, "color", "")).toLowerCase();
                if (!is_light(Py.get(x, "color", "")) && !(c.equals("#f23a2b") || c.equals("#ee3823") || c.equals("#ec3925") || c.equals("#ed3925"))) { g = x; break; }
            }
            if (g == null) for (Map<String, Object> x : sib) if (!is_light(Py.get(x, "color", ""))) { g = x; break; }
            if (g != null) for (String k2 : STYLE_KEYS) if (g.containsKey(k2)) f.put(k2, g.get(k2));
        }
        return f;
    }
}
