# -*- coding: utf-8 -*-
"""설계 PDF + 담보 JSON → 보장 지면(설계에 있는 계열만, 최대 9쪽) 생성 후 담보사항이 끝나는 쪽 뒤에 삽입."""
import json, re, subprocess, sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import pdfplumber
from build_pdf import merge
def page_count(p):
    with pdfplumber.open(p) as pdf: return len(pdf.pages)

def last_cover_page(pdf_path):
    """'보장보험료 합계'가 마지막으로 나오는 쪽 = 담보사항 종료 쪽"""
    n = 0
    with pdfplumber.open(pdf_path) as pdf:
        for i, p in enumerate(pdf.pages):
            t = p.extract_text() or ''
            if '보장보험료 합계' in t or '보장보험료합계' in t.replace(' ',''): n = i+1
    return n or 3
def auto_meta(pdf_path):
    """원본 상품설명서 첫 쪽들에서 피보험자·보험료·상품명·계약사항·영업담당자·발행정보를 자동 추출"""
    with pdfplumber.open(pdf_path) as pdf:
        t1 = pdf.pages[0].extract_text() or ''
        t2 = (pdf.pages[1].extract_text() or '') + '\n' + (pdf.pages[2].extract_text() or '')
    def g(pat, t, d=''):
        mm = re.search(pat, t); return mm.group(1).strip() if mm else d
    m = {}
    m['insured'] = g(r'피보험자\s+(\S+)', t1, '고객')
    m['premium'] = g(r'보험료\s+([\d,]+)\s*원', t1, '') + '원'
    m['product'] = g(r'(\(무\)[^\n]+)', t1, '')
    m['head'] = g(r'(계약사항\s*:[^\n]+)', t2, '').replace('~', '~ ').replace('  ', ' ')
    m['agent'] = g(r'영업담당자\s+(.+?)\s+발행정보', t2, '')
    # 발행 일시는 텍스트 추출 순서가 들쭉날쭉해 날짜 패턴을 직접 찾고, 이름은 '발행정보' 다음 줄에서 가져온다
    dt = re.search(r'(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2})', t2)
    nm = re.search(r'발행정보\s*\n\s*([가-힣]{2,5})\s*\n', t2)
    m['issued'] = ((dt.group(1).replace(' ', '&nbsp;&nbsp;') if dt else '') + '<br>' + (nm.group(1) if nm else '')).strip('<br>')
    m['sex'] = insured_sex(pdf_path)
    return m

def insured_sex(pdf_path):
    """피보험자 성별(v8.19) : 상품설명서 뒤쪽 '갱신담보 예상보험료' 표의 '피보험자명 ○○ 생년월일 남/여, **년' 을 읽는다.
       그 줄이 없으면 '계약자명 ○○(남, 1978. …)' 로, 그것도 없으면 빈 값('') → 생성기가 담보명(유방·자궁 / 전립선)으로 추정하고, 끝내 모르면 성별 중립 사례를 쓴다.
       반환 : 'M' | 'F' | ''"""
    with pdfplumber.open(pdf_path) as pdf:
        pages = [(p.extract_text() or '') for p in pdf.pages]
    full = '\n'.join(pages)
    mm = re.search(r'피보험자명[^\n]{0,40}?생년월일\s*(남|여)', full) or re.search(r'피보험자명\s*\S+\s*\((남|여)\s*,', full)
    if not mm: mm = re.search(r'계약자명\s*\S+\s*\((남|여)\s*,', full)
    return {'남': 'M', '여': 'F'}.get(mm.group(1), '') if mm else ''

def guess_line(riders):
    """담보명 고지유형 꼬리표로 특약 마스터의 상품 라인을 추정"""
    names = ' '.join(r['name'] for r in riders)
    if '통합간편가입' in names: return '통합간편'
    return '케어프리'

if __name__=='__main__':
    if len(sys.argv) == 3:                      # python build_all.py 원본.pdf 결과.pdf  → 완전 자동
        orig, out = sys.argv[1], sys.argv[2]
        cust = os.path.join(BASE, 'out', '_auto_cust.json'); os.makedirs(os.path.join(BASE, 'out'), exist_ok=True)
        c = auto_meta(orig)
        import matcher
        rows = matcher.read_proposal(orig)
        c['riders'] = matcher.read_proposal(orig, line=guess_line(rows))
        try:
            import desc_engine
            c['riders'], c['desc_info'] = desc_engine.attach(c['riders'], orig)
        except Exception as e:
            c['desc_info'] = {'ok': False, 'err': str(e)}
        c['src'] = os.path.basename(orig)
        json.dump(c, open(cust, 'w', encoding='utf-8'), ensure_ascii=False)
        print('자동 인식 —', c['insured'], c['premium'], '· 담보', len(c['riders']), '건 · 매칭', sum(1 for r in c['riders'] if r.get('matched')), '건')
    else:
        cust, orig, out = sys.argv[1], sys.argv[2], sys.argv[3]
    c = json.load(open(cust, encoding='utf-8'))
    ia = last_cover_page(orig); c['insert_after'] = ia; c['base_pages'] = page_count(orig)
    json.dump(c, open(cust,'w',encoding='utf-8'), ensure_ascii=False)
    os.makedirs(os.path.join(BASE,'out'), exist_ok=True)
    html = os.path.join(BASE,'out','_tmp.html'); pdf = os.path.join(BASE,'out','_tmp.pdf')
    subprocess.check_call([sys.executable, os.path.join(BASE,'gen2.py'), cust, html])
    audit = json.load(open(os.path.splitext(html)[0] + '_audit.json', encoding='utf-8'))['요약']
    if not audit.get('생성쪽수'):                # 암·뇌·심장·통합치료비 계열 담보가 없는 설계(운전자·치아 등) → 원본 그대로(v8.4)
        import shutil; shutil.copyfile(orig, out)
        print('스마트제안서 미첨부 — 대상 담보 없음 · 원본 그대로 출력 :', out, '(', c['base_pages'], '쪽 )'); sys.exit(0)
    subprocess.check_call([sys.executable, os.path.join(BASE,'render.py'), html, pdf])
    new = page_count(pdf)                      # 생성 쪽수는 gen2 구성에 따라 자동 반영
    print('담보사항 종료 쪽', ia, '· 생성', new, '쪽 → 총', merge(orig, pdf, out, insert_after=ia, new=new), '쪽')
