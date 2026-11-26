package meai.sp;

import java.util.Map;

/** GaV2.master_rows()(설계도용) 가 파이썬 판과 같은지 — 정답은 golden/dump_master_rows.py. 사용 : GoldenMasterRows <정답.json> */
public final class GoldenMasterRows {
    public static void main(String[] a) {
        G.utf8();
        Map<String, Object> g = Py.M(Json.parse(Py.read(a[0])));
        G.same("master_rows", g.get("rows"), GaV2.master_rows());
        G.same("남은 로그 수", g.get("issues"), (long) ScenEngine.ISSUES.size());
        System.out.println("줄 " + Py.gl(g, "rows").size());
        G.finish("master_rows(설계도용 · 수술 카드 줄 × 특약)");
    }
}
