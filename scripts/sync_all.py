#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""약관 데이터 한 번 바꾸면 세 산출물(세일즈북 생성기 · 스마트 제안서 · 영업지원도구 배포판)을 한꺼번에 맞추는 묶음 명령.

  저장소 루트에서 :  python3 scripts/sync_all.py                 # 전부(약관 재추출 포함 · 10분 안팎)
                     python3 scripts/sync_all.py --skip-terms     # 약관 PDF 재추출은 건너뛰고(tool.html 만 바뀌었을 때 · 2분 안팎)
                     python3 scripts/sync_all.py --designs <설계서PDF폴더>   # + 설계서로 지면 점검(H6)·회귀 스냅샷

원천은 둘뿐이다 — ① tool.html 의 DATA(영업지원도구 특약 데이터 · 감수본) ② 저장소 루트의 약관 PDF.
어느 쪽이 바뀌었든 이 스크립트 하나로 아래 순서가 돈다. 중간에 하나라도 실패하면 거기서 멈춘다(반쪽짜리 산출물을 남기지 않기 위해).

  1. tool.html → proposal_smart/db.json                      (extract_db.py)
  2. 약관 PDF → proposal_smart/db_terms_extra.json             (extract_terms_extra.py · 상품마다 · meta.sources 에 적힌 PDF)
  3. 점검 하네스 H1~H5 (+ --designs 면 H6)                     (proposal_smart/harness.py)
  4. 세일즈북 생성기 docs/guidebook_proto.html 다시 조립         (build_guidebook_proto.py — 1·2 의 마스터를 안에 넣는다)
  5. 영업지원도구 배포판 : 폐쇄망 zip · 메일발송용 · 올인원 HTML · 반출 JSON + 검증
  6. (--designs) 회귀 스냅샷 : 직전 sync 스냅샷과 쪽별 글자 비교 — 바뀐 쪽이 있으면 화면에 찍는다(의도한 변경인지 사람이 본다)

끝나면 무엇이 몇 건 바뀌었는지 요약을 찍는다. 커밋은 하지 않는다(사람이 요약을 보고 한다)."""
import argparse, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PS = os.path.join(ROOT, 'proposal_smart')
PY = sys.executable


def run(title, cmd, cwd):
    print('\n▶ %s\n  $ %s' % (title, ' '.join(cmd)), flush=True)
    t = time.time()
    r = subprocess.run(cmd, cwd=cwd)
    if r.returncode:
        print('\n✖ 실패 : %s (종료코드 %d) — 여기서 멈춥니다. 위 출력을 보고 고친 뒤 다시 돌리세요.' % (title, r.returncode))
        sys.exit(r.returncode)
    print('  ✓ %.0f초' % (time.time() - t), flush=True)


def riders(path):
    d = json.load(open(path, encoding='utf-8'))
    return {r['id']: r for r in d['riders']}


def diff_master(before, after, label):
    """특약 마스터가 얼마나 바뀌었는지 한 줄 요약 — 질병코드(k)·제외코드(x)·수가코드(hc)·이름 기준"""
    added = [i for i in after if i not in before]; removed = [i for i in before if i not in after]
    ch = {'k': 0, 'x': 0, 'hc': 0, 'n': 0}
    for i in after:
        if i in before:
            for f in ch:
                if (before[i].get(f) or ([] if f != 'n' else '')) != (after[i].get(f) or ([] if f != 'n' else '')): ch[f] += 1
    print('  %s : %d건 → %d건 · 신규 %d · 삭제 %d · 질병코드 바뀜 %d · 제외코드 바뀜 %d · 수가코드 바뀜 %d · 이름 바뀜 %d'
          % (label, len(before), len(after), len(added), len(removed), ch['k'], ch['x'], ch['hc'], ch['n']))
    return added, removed, ch


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--skip-terms', action='store_true', help='약관 PDF 재추출(2단계)을 건너뛴다')
    ap.add_argument('--skip-dist', action='store_true', help='영업지원도구 배포판(5단계)을 건너뛴다')
    ap.add_argument('--designs', help='설계서 PDF 폴더(개인정보 · 저장소 밖) — 있으면 H6 지면 점검과 회귀 스냅샷까지')
    a = ap.parse_args()

    db_p, ex_p = os.path.join(PS, 'db.json'), os.path.join(PS, 'db_terms_extra.json')
    db0 = riders(db_p); ex0 = riders(ex_p) if os.path.exists(ex_p) else {}

    # 1. tool.html → db.json
    run('1. 영업지원도구 데이터(tool.html) → 특약 마스터 db.json', [PY, 'extract_db.py', '../tool.html'], PS)

    # 2. 약관 PDF → db_terms_extra.json (meta.sources 에 적힌 상품·PDF 를 그대로 다시 뽑는다)
    if not a.skip_terms:
        meta = json.load(open(ex_p, encoding='utf-8'))['meta'] if os.path.exists(ex_p) else {}
        import re
        prefix = {}
        for r in ex0.values(): prefix.setdefault(r['p'], re.match(r'^(\D+(?:31)?)', r['id']).group(1))
        for prod, pdf in (meta.get('sources') or {}).items():
            path = os.path.join(ROOT, pdf)
            if not os.path.exists(path):
                print('  ! 약관 PDF 가 없어 건너뜀 : %s (%s)' % (pdf, prod)); continue
            run('2. 약관 → 보강 마스터 : %s' % prod, [PY, 'extract_terms_extra.py', path, prod, prefix.get(prod, prod[:2])], PS)
    else:
        print('\n▶ 2. 약관 PDF 재추출 건너뜀(--skip-terms)')

    print('\n▶ 마스터 변화')
    diff_master(db0, riders(db_p), 'db.json(영업지원도구 감수본)')
    if os.path.exists(ex_p): diff_master(ex0, riders(ex_p), 'db_terms_extra.json(약관 파싱 보강)')

    # 3. 하네스
    cmd = [PY, 'harness.py'] + (['--designs', a.designs] if a.designs else [])
    run('3. 점검 하네스 H1~H5%s' % (' + H6(설계서)' if a.designs else ''), cmd, PS)

    # 4. 세일즈북 생성기
    run('4. 세일즈북 생성기 다시 조립(docs/guidebook_proto.html)', [PY, 'scripts/build_guidebook_proto.py'], ROOT)

    # 5. 영업지원도구 배포판
    if not a.skip_dist:
        run('5-1. 폐쇄망 배포 zip', [PY, 'scripts/build_package.py'], ROOT)
        run('5-2. 메일발송용 대체 파일', [PY, 'scripts/build_mail.py'], ROOT)
        run('5-3. 올인원 HTML', [PY, 'scripts/build_allinone.py'], ROOT)
        run('5-4. 반출 JSON·설명서', [PY, 'scripts/build_export.py'], ROOT)
        run('5-5. 반출 파일 검증', [PY, 'scripts/verify_export.py'], ROOT)
    else:
        print('\n▶ 5. 배포판 건너뜀(--skip-dist)')

    # 6. 회귀 스냅샷 (설계서가 있을 때) — 직전 sync 스냅샷과 비교
    if a.designs:
        reg = os.path.join(PS, 'out', 'regress')
        prev, now = os.path.join(reg, 'sync_prev.json'), os.path.join(reg, 'sync_now.json')
        if os.path.exists(now): os.replace(now, prev)
        run('6. 회귀 스냅샷(sync_now)', [PY, 'regress.py', 'snap', 'sync_now', a.designs], PS)
        if os.path.exists(prev):
            print('\n▶ 6. 직전 sync 와 비교 — 바뀐 쪽이 의도한 것인지 확인하세요')
            subprocess.run([PY, 'regress.py', 'diff', 'sync_prev', 'sync_now'], cwd=PS)
        else:
            print('  (직전 sync 스냅샷이 없어 비교는 다음 실행부터)')

    print('\n■ 끝. 바뀐 파일은 git status 로 보고, README 변경 기록(proposal_smart/README.md 맨 위)·api.py VERSION 을 올린 뒤 커밋하세요.')


if __name__ == '__main__':
    main()
