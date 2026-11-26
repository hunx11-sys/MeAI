# 설계도용 master_rows()(특약 마스터 전체 × 수술 12개 사례 → 카드 다섯 줄 중 어느 줄) 정답지 — 사용 : python3 golden/dump_master_rows.py <출력.json>
import sys, os, json, warnings
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', '..', 'proposal_smart'))
import ga_v2 as GV, scen_engine as S
rows = GV.master_rows()
json.dump(dict(rows=rows, issues=len(S.ISSUES)), open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
print('master_rows', len(rows))
