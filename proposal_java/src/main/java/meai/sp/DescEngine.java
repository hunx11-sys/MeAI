package meai.sp;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 파이썬 desc_engine.py 가운데 계산 엔진(scen_engine.ls_items)이 부르는 `life_items` 만 옮긴 것.
 * (설계서 PDF 에서 설명문을 읽는 부분은 옮기지 않는다 — 담보코드 입력에는 설명문이 없다)
 */
public final class DescEngine {
    private DescEngine() {}

    public static final Pattern LSITEM = Py.re("[-·]\\s*([^:\\n]{2,60}?)\\s*:\\s*([\\d,.]+)\\s*만원\\s*[(（]\\s*([^)）]{1,24})\\s*[)）]");

    /** 담보 설명문 → [{grp,label,cnt,amt,amt_pre}] · 항목표가 없으면 빈 목록 */
    public static List<Object> life_items(String desc) {
        String d = Py.sub("\\s+", " ", desc == null ? "" : desc);
        d = Py.split(d, "※").get(0);                               // ※ 주석부터는 항목표가 아니다
        List<Object> out = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        Matcher m = LSITEM.matcher(d);
        while (m.find()) {
            String label = Py.strip(m.group(1), " -·");
            String cnt = Py.sub("\\s+", "", m.group(3));
            double amt = Double.parseDouble(m.group(2).replace(",", ""));
            if (label.isEmpty() || amt <= 0) continue;
            String grp = cnt.contains("산정특례") ? "산정특례" : (label.contains("재활") ? "재활치료" : "주요치료");
            String key = Py.sub("\\s", "", label);
            if (seen.contains(key)) continue;
            seen.add(key);
            out.add(Py.dict("grp", grp, "label", label, "cnt", cnt, "amt", amt, "amt_pre", amt));
        }
        return out;
    }
}
