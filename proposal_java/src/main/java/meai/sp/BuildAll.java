package meai.sp;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

/** 파이썬 build_all.py 가운데 상품 라인 읽기(PDF 없이 도는 부분) */
public final class BuildAll {
    private BuildAll() {}

    public static final List<String> NEW_LINES_2611 = Arrays.asList("올케어암", "올케어암간편", "올케어뇌심", "올케어뇌심간편", "올케어수술비", "올케어골키퍼",
            "OnlyYou통합", "OnlyYou통합간편", "성공파트너", "상해안심", "프리미엄건강", "프리미엄간편");

    /** guess_line(riders, pdf=None) 의 PDF 없는 길 — 고지 구분자(통합간편가입)만 본다 */
    public static String guess_line(List<Object> riders) {
        StringBuilder names = new StringBuilder();
        boolean first = true;
        for (Object o : riders) { if (!first) names.append(' '); first = false; names.append((String) ((Map<?, ?>) o).get("name")); }
        if (names.indexOf("통합간편가입") >= 0) return "통합간편";
        return "케어프리";
    }

    /** 설계서 첫 쪽 글자(또는 상품명 · 띄어쓰기 없이) → 상품 라인. 못 읽으면 null */
    public static String line_from_head(String head) {
        if (head.contains("통합간편건강보험")) return "통합간편";
        if (Py.has("\\(무\\)내Mom대로보장보험", head)) return "내Mom대로";
        if (head.contains("내Mom같은어린이보험")) return "내Mom같은어린이";
        if (head.contains("간편31건강보험")) return "간편31";
        if (head.contains("The건강한내Mom대로5.10.5")) return "The건강한내Mom대로5.10.5";
        if (head.contains("The건강한5.10.5")) return "The건강한5.10.5";
        if (head.contains("The좋은내Mom대로")) return "The좋은내Mom대로";
        if (head.contains("The가벼운간편355")) return "The가벼운간편355";
        if (Py.has("The좋은(케어프리보험|알파Plus)", head)) return "The좋은케어프리";
        if (head.contains("올케어보장꽉채운암보험")) return head.contains("맞춤간편") ? "올케어암간편" : "올케어암";
        if (head.contains("올케어꽉채운뇌심보험")) return head.contains("맞춤간편") ? "올케어뇌심간편" : "올케어뇌심";
        if (head.contains("올케어꽉채운수술비보험")) return "올케어수술비";
        if (head.contains("올케어꽉채운골키퍼건강보험")) return "올케어골키퍼";
        if (Py.search("OnlyYou통합보험", head, Py.I) != null) return head.contains("355간편") ? "OnlyYou통합간편" : "OnlyYou통합";
        if (head.contains("성공파트너종합보험")) return "성공파트너";
        if (head.contains("상해안심보험")) return "상해안심";
        if (head.contains("프리미엄간편보험")) return "프리미엄간편";
        if (head.contains("프리미엄건강보험")) return "프리미엄건강";
        return null;
    }
}
