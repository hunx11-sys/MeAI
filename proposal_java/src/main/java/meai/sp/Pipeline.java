package meai.sp;

/** 파이썬 pipeline.py 가운데 담보코드 입력(JSON) 길이 쓰는 것만 — 설계서 PDF 읽기 · 9쪽 판 조립은 옮기지 않는다 */
public final class Pipeline {
    private Pipeline() {}

    /** 계산할 담보를 하나도 읽지 못함(또는 만들지 않는 상품). 메시지는 화면 · 명령창에 그대로 보여 줄 쉬운 말 */
    public static class DesignUnreadable extends IllegalArgumentException {
        private static final long serialVersionUID = 1L;
        public DesignUnreadable(String msg) { super(msg); }
    }
}
