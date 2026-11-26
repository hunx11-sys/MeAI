package meai.sp;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.cos.COSArray;
import org.apache.pdfbox.cos.COSBase;
import org.apache.pdfbox.cos.COSDictionary;
import org.apache.pdfbox.cos.COSName;
import org.apache.pdfbox.cos.COSObject;
import org.apache.pdfbox.cos.COSStream;
import org.apache.pdfbox.multipdf.LayerUtility;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.graphics.form.PDFormXObject;
import org.apache.pdfbox.pdmodel.graphics.image.PDImageXObject;
import org.apache.pdfbox.text.PDFTextStripperByArea;
import org.apache.pdfbox.util.Matrix;

import javax.imageio.IIOImage;
import javax.imageio.ImageIO;
import javax.imageio.ImageWriteParam;
import javax.imageio.ImageWriter;
import javax.imageio.plugins.jpeg.JPEGImageWriteParam;
import javax.imageio.stream.MemoryCacheImageOutputStream;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.IdentityHashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.IntFunction;

/**
 * PDF 조립 — 파이썬 ga_v2._build 의 2)~5)(fitz insert_pdf · show_pdf_page · new_page · dedupe_images · jpeg_big · save · 제목 점검)를
 * Apache PDFBox 로 그대로 옮겼다. 좌표는 파이썬(fitz)처럼 「왼쪽 위가 0, 아래로 +」 인 pt 로 받고 여기서 PDF 좌표(아래가 0)로 뒤집는다.
 * 글자층은 원래 조각의 것을 그대로 둔다(완성 PDF 의 글자를 다시 읽는 인쇄 검증이 쓴다).
 */
public final class PdfKit {
    private PdfKit() {}

    public static String V2 = Py.path("ga_assets", "v2");
    public static String TPL = Paths.get(V2, "tpl.pdf").toString(), SLOTS = Paths.get(V2, "slots.json").toString();

    static Map<String, Object> _SL = null;
    public static Map<String, Object> slots() {
        if (_SL == null) _SL = Py.M(Json.parse(Py.read(SLOTS)));
        return _SL;
    }

    public static PDDocument open(String path) {
        try { return Loader.loadPDF(new File(path)); } catch (IOException ex) { throw new RuntimeException("PDF 를 열지 못함 : " + path, ex); }
    }

    public static int page_count(String path) {
        try (PDDocument d = open(path)) { return d.getNumberOfPages(); } catch (IOException ex) { throw new RuntimeException(ex); }
    }

    /** fitz 의 Rect — (x0, y0, x1, y1) · 왼쪽 위가 0 */
    public static double[] Rect(double x0, double y0, double x1, double y1) { return new double[]{x0, y0, x1, y1}; }

    static double[] page_rect(PDPage pg) { PDRectangle b = pg.getCropBox(); return new double[]{0, 0, b.getWidth(), b.getHeight()}; }

    /**
     * fitz page.show_pdf_page(rect, src, pno, clip=…) — 원본 쪽(form 으로 가져온 것 · 크기 srcW×srcH)의 clip 구역을 대상 쪽의 rect 안에
     * 가로세로 비율을 지킨 채(작은 쪽 배율) 가운데에 맞춰 얹는다. clip 이 null 이면 원본 쪽 전체.
     */
    public static void show_pdf_page(PDDocument doc, PDPage page, double[] rect, PDFormXObject form, double srcW, double srcH, double[] clip) throws IOException {
        double[] sr = clip == null ? new double[]{0, 0, srcW, srcH}
                : new double[]{Math.max(0, clip[0]), Math.max(0, clip[1]), Math.min(srcW, clip[2]), Math.min(srcH, clip[3])};
        double sw = sr[2] - sr[0], sh = sr[3] - sr[1], tw = rect[2] - rect[0], th = rect[3] - rect[1];
        double pageH = page.getCropBox().getHeight();
        double s = Math.min(tw / sw, th / sh);
        double scx = (sr[0] + sr[2]) / 2, scy = srcH - (sr[1] + sr[3]) / 2;          // 원본 구역 가운데(PDF 좌표)
        double tcx = (rect[0] + rect[2]) / 2, tcy = pageH - (rect[1] + rect[3]) / 2;  // 대상 구역 가운데(PDF 좌표)
        try (PDPageContentStream cs = new PDPageContentStream(doc, page, PDPageContentStream.AppendMode.APPEND, true, true)) {
            cs.saveGraphicsState();
            cs.transform(new Matrix((float) s, 0, 0, (float) s, (float) (tcx - s * scx), (float) (tcy - s * scy)));
            cs.addRect((float) sr[0], (float) (srcH - sr[3]), (float) sw, (float) sh);
            cs.clip();
            cs.drawForm(form);
            cs.restoreGraphicsState();
        }
    }

    /** 틀 쪽 제목 자리의 글자 — 파이썬 title_of(pg.get_text(clip=Rect(185, 30, 450, 52)).strip()) */
    public static String title_of(PDDocument doc, int pno) throws IOException {
        PDFTextStripperByArea st = new PDFTextStripperByArea();
        st.setSortByPosition(true);
        st.addRegion("t", new Rectangle2D.Double(185, 30, 450 - 185, 52 - 30));
        st.extractRegions(doc.getPage(pno));
        return Py.strip(st.getTextForRegion("t"));
    }

    // ── 그림 다루기(파일 크기) ───────────────────────────
    /** 문서에 든 XObject 사전(/Resources /XObject)을 모두 모은다 — 쪽 · form · 무늬(Pattern) 속까지 */
    static List<COSDictionary> xobject_dicts(PDDocument d) {
        List<COSDictionary> out = new ArrayList<>();
        Set<COSBase> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        for (PDPage pg : d.getPages()) walk_res(pg.getCOSObject().getCOSDictionary(COSName.RESOURCES), out, seen);
        return out;
    }

    static void walk_res(COSDictionary res, List<COSDictionary> out, Set<COSBase> seen) {
        if (res == null || !seen.add(res)) return;
        COSDictionary xo = res.getCOSDictionary(COSName.XOBJECT);
        if (xo != null && seen.add(xo)) {
            out.add(xo);
            for (COSName k : new ArrayList<>(xo.keySet())) {
                COSBase v = xo.getDictionaryObject(k);
                if (v instanceof COSStream && COSName.FORM.equals(((COSStream) v).getCOSName(COSName.SUBTYPE)) && seen.add(v))
                    walk_res(((COSStream) v).getCOSDictionary(COSName.RESOURCES), out, seen);
            }
        }
        COSDictionary pat = res.getCOSDictionary(COSName.PATTERN);
        if (pat != null && seen.add(pat)) {
            for (COSName k : pat.keySet()) {
                COSBase v = pat.getDictionaryObject(k);
                if (v instanceof COSDictionary && seen.add(v)) walk_res(((COSDictionary) v).getCOSDictionary(COSName.RESOURCES), out, seen);
            }
        }
        COSDictionary gs = res.getCOSDictionary(COSName.EXT_G_STATE);
        if (gs != null && seen.add(gs)) {
            for (COSName k : gs.keySet()) {
                COSBase v = gs.getDictionaryObject(k);
                if (!(v instanceof COSDictionary)) continue;
                COSBase sm = ((COSDictionary) v).getDictionaryObject(COSName.SMASK);
                if (sm instanceof COSDictionary) {
                    COSBase g = ((COSDictionary) sm).getDictionaryObject(COSName.G);
                    if (g instanceof COSStream && seen.add(g)) walk_res(((COSStream) g).getCOSDictionary(COSName.RESOURCES), out, seen);
                }
            }
        }
    }

    static boolean is_image(COSBase v) { return v instanceof COSStream && COSName.IMAGE.equals(((COSStream) v).getCOSName(COSName.SUBTYPE)); }

    static String hex(byte[] b) { StringBuilder s = new StringBuilder(); for (byte x : b) s.append(String.format("%02x", x)); return s.toString(); }

    static boolean lossy_last(COSStream s) {
        COSBase f = s.getDictionaryObject(COSName.FILTER);
        COSBase last = f instanceof COSArray ? (((COSArray) f).size() > 0 ? ((COSArray) f).getObject(((COSArray) f).size() - 1) : null) : f;
        return COSName.DCT_DECODE.equals(last) || COSName.JPX_DECODE.equals(last) || COSName.CCITTFAX_DECODE.equals(last) || COSName.JBIG2_DECODE.equals(last);
    }

    /** 스트림 알맹이의 지문 — 무손실 압축은 푼 바이트, JPEG 따위는 담긴 바이트 그대로 */
    static String stream_md5(COSStream s) throws IOException {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            try (InputStream in = lossy_last(s) ? s.createRawInputStream() : s.createInputStream()) {
                byte[] buf = new byte[65536]; int n;
                while ((n = in.read(buf)) > 0) md.update(buf, 0, n);
            }
            return hex(md.digest());
        } catch (java.security.NoSuchAlgorithmException ex) { throw new RuntimeException(ex); }
    }

    /** 색 공간 · 풀이표 같은 딸린 값의 꼴(가리키는 번호가 달라도 내용이 같으면 같게) */
    static String sig(COSBase b, int depth) throws IOException {
        if (b instanceof COSObject) b = ((COSObject) b).getObject();
        if (b == null) return "null";
        if (depth > 6) return "…";
        if (b instanceof COSStream) return "S" + stream_md5((COSStream) b);
        if (b instanceof COSArray) { StringBuilder s = new StringBuilder("["); for (COSBase x : (COSArray) b) s.append(sig(x, depth + 1)).append(' '); return s.append(']').toString(); }
        if (b instanceof COSDictionary) {
            List<String> ks = new ArrayList<>();
            for (COSName k : ((COSDictionary) b).keySet()) ks.add(k.getName());
            Collections.sort(ks);
            StringBuilder s = new StringBuilder("<");
            for (String k : ks) s.append(k).append('=').append(sig(((COSDictionary) b).getDictionaryObject(k), depth + 1)).append(' ');
            return s.append('>').toString();
        }
        return b.toString();
    }

    static String image_key(COSStream im) throws IOException {
        StringBuilder k = new StringBuilder(stream_md5(im));
        for (COSName n : new COSName[]{COSName.WIDTH, COSName.HEIGHT, COSName.BITS_PER_COMPONENT, COSName.COLORSPACE, COSName.IMAGE_MASK, COSName.DECODE,
                COSName.MASK, COSName.SMASK, COSName.DECODE_PARMS, COSName.INTERPOLATE})
            k.append('|').append(sig(im.getDictionaryObject(n), 0));
        if (lossy_last(im)) k.append('|').append(sig(im.getDictionaryObject(COSName.FILTER), 0));
        return k.toString();
    }

    static int remap(List<COSDictionary> dicts, Map<COSBase, COSStream> mp) {
        int n = 0;
        for (COSDictionary xo : dicts)
            for (COSName k : new ArrayList<>(xo.keySet())) {
                COSStream to = mp.get(xo.getDictionaryObject(k));
                if (to != null) { xo.setItem(k, to); n++; }
            }
        return n;
    }

    /** 같은 그림(픽셀 · 투명도 같음)이 여러 번 들어가 있으면 첫 그림 하나만 가리키게 고친다 — 남는 사본은 저장할 때 빠진다 */
    public static int dedupe_images(PDDocument d) throws IOException {
        List<COSDictionary> dicts = xobject_dicts(d);
        Map<String, COSStream> seen = new LinkedHashMap<>();
        Map<COSBase, COSStream> mp = new IdentityHashMap<>();
        Set<COSBase> done = Collections.newSetFromMap(new IdentityHashMap<>());
        for (COSDictionary xo : dicts)
            for (COSName k : xo.keySet()) {
                COSBase v = xo.getDictionaryObject(k);
                if (!is_image(v) || !done.add(v)) continue;
                String h = image_key((COSStream) v);
                COSStream first = seen.get(h);
                if (first == null) seen.put(h, (COSStream) v); else mp.put(v, first);
            }
        if (mp.isEmpty()) return 0;
        remap(dicts, mp);
        return mp.size();
    }

    /** 큰 불투명 그림(폭 1000px 이상 · RGB · 투명도 없음 · 아직 JPEG 가 아닌 것)은 JPEG 로 다시 담는다 — 크기만 줄고 모양은 같다 */
    public static int jpeg_big(PDDocument d, int q) throws IOException {
        List<COSDictionary> dicts = xobject_dicts(d);
        Map<COSBase, COSStream> mp = new IdentityHashMap<>();
        Set<COSBase> done = Collections.newSetFromMap(new IdentityHashMap<>());
        for (COSDictionary xo : dicts)
            for (COSName k : xo.keySet()) {
                COSBase v = xo.getDictionaryObject(k);
                if (!is_image(v) || !done.add(v)) continue;
                COSStream im = (COSStream) v;
                if (im.getDictionaryObject(COSName.SMASK) != null || im.getInt(COSName.WIDTH, 0) < 1000) continue;
                if (COSName.DCT_DECODE.equals(im.getDictionaryObject(COSName.FILTER))) continue;
                if (im.getBoolean(COSName.IMAGE_MASK, false) || im.getDictionaryObject(COSName.MASK) != null) continue;
                PDImageXObject px = new PDImageXObject(new org.apache.pdfbox.pdmodel.common.PDStream(im), null);
                int w = im.getInt(COSName.WIDTH, 0), h = im.getInt(COSName.HEIGHT, 0);
                BufferedImage rgb; COSBase cspace;
                if (px.getColorSpace().getNumberOfComponents() == 3 && im.getInt(COSName.BITS_PER_COMPONENT, 0) == 8 && im.getDictionaryObject(COSName.DECODE) == null
                        && !(px.getColorSpace() instanceof org.apache.pdfbox.pdmodel.graphics.color.PDLab)) {
                    // 담긴 RGB 값을 그대로(색 변환 없이) JPEG 로 — 색 공간 표시는 원래 것을 둔다(파이썬 판 replace_image 와 같음)
                    byte[] raw;
                    try (InputStream in = im.createInputStream()) { raw = in.readAllBytes(); }
                    if (raw.length < w * h * 3) continue;
                    rgb = new BufferedImage(w, h, BufferedImage.TYPE_INT_RGB);
                    int[] px3 = new int[w * h];
                    for (int i = 0, j = 0; i < px3.length; i++, j += 3) px3[i] = ((raw[j] & 255) << 16) | ((raw[j + 1] & 255) << 8) | (raw[j + 2] & 255);
                    rgb.setRGB(0, 0, w, h, px3, 0, w);
                    cspace = im.getItem(COSName.COLORSPACE);
                } else if (px.getColorSpace() instanceof org.apache.pdfbox.pdmodel.graphics.color.PDIndexed) {
                    BufferedImage src = px.getImage();
                    if (src.getColorModel().hasAlpha()) continue;
                    rgb = new BufferedImage(src.getWidth(), src.getHeight(), BufferedImage.TYPE_INT_RGB);
                    rgb.getGraphics().drawImage(src, 0, 0, null);
                    cspace = COSName.DEVICERGB;
                } else continue;
                byte[] jpg = jpeg_bytes(rgb, q);
                COSStream nw = d.getDocument().createCOSStream();
                try (OutputStream os = nw.createRawOutputStream()) { os.write(jpg); }
                nw.setItem(COSName.TYPE, COSName.XOBJECT); nw.setItem(COSName.SUBTYPE, COSName.IMAGE);
                nw.setItem(COSName.FILTER, COSName.DCT_DECODE);
                nw.setInt(COSName.WIDTH, rgb.getWidth()); nw.setInt(COSName.HEIGHT, rgb.getHeight());
                nw.setInt(COSName.BITS_PER_COMPONENT, 8); nw.setItem(COSName.COLORSPACE, cspace);
                mp.put(v, nw);
            }
        if (!mp.isEmpty()) remap(dicts, mp);
        return mp.size();
    }
    public static int jpeg_big(PDDocument d) throws IOException { return jpeg_big(d, 88); }

    /** JPEG 로 담기 — 파이썬 판(MuPDF)과 같은 설정 : 품질 q · 색 표본을 줄이지 않음(4:4:4) · 점진식 · 허프만표 최적화 */
    static byte[] jpeg_bytes(BufferedImage im, int q) throws IOException {
        ImageWriter w = ImageIO.getImageWritersByFormatName("jpeg").next();
        try {
            JPEGImageWriteParam p = new JPEGImageWriteParam(null);
            p.setCompressionMode(ImageWriteParam.MODE_EXPLICIT);
            p.setCompressionQuality(q / 100f);
            p.setOptimizeHuffmanTables(true);
            p.setProgressiveMode(ImageWriteParam.MODE_DEFAULT);
            javax.imageio.metadata.IIOMetadata md = w.getDefaultImageMetadata(javax.imageio.ImageTypeSpecifier.createFromRenderedImage(im), p);
            String fmt = "javax_imageio_jpeg_image_1.0";
            org.w3c.dom.Node root = md.getAsTree(fmt);
            org.w3c.dom.NodeList cs = ((org.w3c.dom.Element) root).getElementsByTagName("componentSpec");
            for (int i = 0; i < cs.getLength(); i++) {
                org.w3c.dom.Element e = (org.w3c.dom.Element) cs.item(i);
                e.setAttribute("HsamplingFactor", "1"); e.setAttribute("VsamplingFactor", "1");
            }
            md.setFromTree(fmt, root);
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            try (MemoryCacheImageOutputStream out = new MemoryCacheImageOutputStream(bo)) {
                w.setOutput(out);
                w.write(null, new IIOImage(im, null, md), p);
            }
            return bo.toByteArray();
        } finally { w.dispose(); }
    }

    // ── 조립 ─────────────────────────────────────────────
    /**
     * 파이썬 ga_v2._build 의 1)~5) — HTML 글자를 받아 브라우저로 그리고 틀 위에 합쳐 한 파일로 만든다.
     *
     * @param tag        중간 파일 이름 머리(파이썬 GP.tag_of)
     * @param out_pdf    완성 PDF 경로
     * @param cs_html    표지 · 보장요약(cover_summary_html())
     * @param ov_html    틀 5쪽(암 ① ② · 뇌혈관 · 심장 · 안내사항) 위에 얹을 값(overlay_html()) — 꼭 5쪽
     * @param pages_html 새로 그리는 쪽(주요수술 ① ② + 간병인 쪽) 전체 HTML
     * @param detail_html 세부내역 HTML(스스로 쪽을 나눔 · window.REPORT 를 남김)
     * @param dov_html   세부내역 쪽수 n → 그 쪽들 위에 얹을 값(detail_overlay_html(n))
     * @return dict(pages=전체 쪽수, cs_pages=표지 · 요약 쪽수, fit, over, detail_pages, rep, warn)
     *         — warn 은 파이썬과 같은 글자(「새 쪽 넘침 …」 · 「글자층 경고 : …」)
     */
    public static Map<String, Object> assemble(String tag, String out_pdf, String cs_html, String ov_html, String pages_html, String detail_html, IntFunction<String> dov_html) {
        try {
            Files.createDirectories(Paths.get(Render.TMP));
            File of = new File(out_pdf).getAbsoluteFile();
            if (of.getParentFile() != null) Files.createDirectories(of.getParentFile().toPath());
            List<Object> warn = new ArrayList<>();
            // 1) 표지 · 보장요약
            String p_cs = Paths.get(Render.TMP, tag + "_cs.pdf").toString();
            Render.pdf_css(Render._goto(cs_html, "cs"), p_cs);
            // 2) 시안 틀 + 값
            Map<String, Object> SL = slots();
            List<Object> order = Py.gl(SL, "pages");
            String p_ov = Paths.get(Render.TMP, tag + "_ov.pdf").toString();
            Render.pdf_css(Render._goto(ov_html, "ov"), p_ov);
            // 3) 새로 그리는 쪽
            String p_h = Paths.get(Render.TMP, tag + "_html.pdf").toString();
            List<Object> fo = Render.render_pages(pages_html, p_h, "html");
            List<Object> fit = Py.L(fo.get(0)), over = Py.L(fo.get(1));
            if (Py.truthy(over)) warn.add(Py.fmt("새 쪽 넘침 %s", over));
            // 4) 세부내역
            String p_d = Paths.get(Render.TMP, tag + "_detail.pdf").toString();
            Map<String, Object> rep = Render.render_detail_html(detail_html, p_d);
            int n = page_count(p_d);
            String p_do = Paths.get(Render.TMP, tag + "_detail_ov.pdf").toString();
            Render.pdf_css(Render._goto(dov_html.apply(n), "dov"), p_do);

            int cs_pages, total;
            try (PDDocument out = new PDDocument();
                 PDDocument tpl = open(TPL); PDDocument tplF = open(TPL);       // tpl = 쪽으로 옮길 것 · tplF = 다른 쪽 위에 얹을 것(로고 · 세부내역 바탕)
                 PDDocument cs = open(p_cs); PDDocument ov = open(p_ov); PDDocument hd = open(p_h); PDDocument dc = open(p_d); PDDocument dov = open(p_do)) {
                if (ov.getNumberOfPages() != 5) throw new AssertionError(ov.getNumberOfPages());
                if (dov.getNumberOfPages() < n) throw new AssertionError("세부내역 덧쪽 수 " + dov.getNumberOfPages() + " < " + n);
                LayerUtility lu = new LayerUtility(out);
                cs_pages = cs.getNumberOfPages();
                // 5) 묶기 : 표지 · 요약 → 암① 암② 뇌 심 → 수술 ① ② → 간병 → 세부내역 → 안내사항
                for (PDPage pg : cs.getPages()) out.importPage(pg);
                List<PDPage> tp = new ArrayList<>();
                for (int i = 0; i < 5; i++) {
                    PDPage pg = out.importPage(tpl.getPage(i));
                    if (i == 4) out.removePage(pg);                         // 안내사항은 맨 뒤에 붙인다
                    double[] r = page_rect(pg); PDPage sp = ov.getPage(i); double[] sr = page_rect(sp);
                    show_pdf_page(out, pg, r, lu.importPageAsForm(ov, sp), sr[2], sr[3], null);
                    tp.add(pg);
                }
                PDPage t0 = tplF.getPage(0); double[] t0r = page_rect(t0); PDFormXObject f0 = lu.importPageAsForm(tplF, t0);
                for (PDPage sp : hd.getPages()) {      // 로고 · 경고문 : 틀(암①)에서 그대로
                    PDPage pg = out.importPage(sp);
                    show_pdf_page(out, pg, Rect(30.5, 31.0, 186.0, 51.5), f0, t0r[2], t0r[3], Rect(30.5, 31.0, 186.0, 51.5));
                    show_pdf_page(out, pg, Rect(449.5, 33.0, 566.0, 50.0), f0, t0r[2], t0r[3], Rect(449.5, 33.0, 566.0, 50.0));
                }
                Map<String, Object> ct = null;
                for (Object x : Py.gl(Py.gm(SL, "slots"), "detail")) if ("content".equals(Py.gs(x, "key"))) ct = Py.M(x);
                double top = Py.num(ct.get("top")), height = Py.num(ct.get("height"));
                PDPage t5 = tplF.getPage(5); double[] t5r = page_rect(t5); PDFormXObject f5 = lu.importPageAsForm(tplF, t5);
                PDRectangle t5box = t5.getCropBox();
                for (int i = 0; i < n; i++) {
                    PDPage pg = new PDPage(new PDRectangle(t5box.getWidth(), t5box.getHeight()));
                    out.addPage(pg);
                    double[] r = page_rect(pg);
                    show_pdf_page(out, pg, r, f5, t5r[2], t5r[3], null);
                    PDPage dp = dc.getPage(i); double[] dr = page_rect(dp);
                    show_pdf_page(out, pg, Rect(0, top, 595, top + height), lu.importPageAsForm(dc, dp), dr[2], dr[3], null);
                    PDPage op = dov.getPage(i); double[] or = page_rect(op);
                    show_pdf_page(out, pg, r, lu.importPageAsForm(dov, op), or[2], or[3], null);
                }
                out.addPage(tp.get(4));
                dedupe_images(out); jpeg_big(out);
                Files.deleteIfExists(of.toPath());
                out.save(of);
                total = out.getNumberOfPages();
            }
            // 점검 : 틀 쪽 제목이 그대로인가(글꼴 꼬임) · 글자층 오류
            try (PDDocument chk = open(of.getPath()); PDDocument tpl = open(TPL)) {
                String[] ks = {"ca1", "ca2", "brain", "heart"};
                for (int j = 0; j < ks.length; j++) {
                    if (!title_of(chk, cs_pages + j).equals(title_of(tpl, order.indexOf(ks[j])))) throw new RuntimeException(Py.fmt("틀 쪽 제목이 바뀜 : %s", ks[j]));
                }
            }
            String err = pdftotext_err(of.getPath());
            if (!err.isEmpty()) warn.add("글자층 경고 : " + Py.slice(err, null, 200));
            return Py.dict("pages", (long) total, "cs_pages", (long) cs_pages, "fit", fit, "over", over, "detail_pages", (long) n, "rep", rep, "warn", warn);
        } catch (IOException ex) { throw new RuntimeException("PDF 조립 실패 : " + ex.getMessage(), ex); }
    }

    /** pdftotext 가 있으면 글자층을 읽혀 보고 오류 글자(stderr)를 돌려준다(없으면 빈 글자) — 파이썬 판과 같은 점검 */
    static String pdftotext_err(String pdf) {
        try {
            Process p = new ProcessBuilder("pdftotext", pdf, "-").redirectOutput(ProcessBuilder.Redirect.DISCARD).start();
            String err = new String(p.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);
            p.waitFor();
            return Py.strip(err);
        } catch (IOException ex) { return ""; }                       // pdftotext 가 없는 PC
        catch (InterruptedException ex) { Thread.currentThread().interrupt(); return ""; }
    }

    /**
     * 한 건을 통째로 — 파이썬 ga_v2.build 의 임시 폴더 · 다시 하기 규칙 : 건마다 job_* 폴더를 만들고 끝나면 지운다.
     * 브라우저가 죽어서 난 오류(closed · crash · Target · disconnected)면 새로 띄워 한 번 더 한다.
     */
    public static Map<String, Object> build_from_html(String tag, String out_pdf, String cs_html, String ov_html, String pages_html, String detail_html, IntFunction<String> dov_html) {
        String root = Render.begin_job();
        try {
            try {
                return assemble(tag, out_pdf, cs_html, ov_html, pages_html, detail_html, dov_html);
            } catch (RuntimeException e) {
                Render.close_browser();                               // 실패한 건 뒤에는 크로뮴을 새로 띄운다
                if (!Py.has("closed|crash|Target|disconnected", String.valueOf(e.getMessage()))) throw e;
                return assemble(tag, out_pdf, cs_html, ov_html, pages_html, detail_html, dov_html);
            }
        } finally { Render.end_job(root); }
    }
}
