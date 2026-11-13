/* =====================================================================
   MeAI 질병 검색 사전 (meai-lex) — 일상 병명 · 신체부위 말 → 공식 병명
   ---------------------------------------------------------------------
   쓰는 곳 : 특약검색기(tool.html) 질병 검색 · 보상시뮬레이터(tool.html 안 SIMSRC)
   원본    : ui/meai-lex.js  →  python3 scripts/apply_lex.py 로 두 곳에 같은 글을 끼운다.
             (tool.html 을 직접 고치지 말고 이 파일을 고친 뒤 다시 끼운다)

   ▣ 절대 규칙 — 이 사전은 질병코드(KCD)를 하나도 갖고 있지 않다.
     · 사전은 「일상 말 → 공식 병명 글자」만 적는다. 코드는 언제나 특약검색기 DATA 의
       codenames(공식 KCD 코드 → 병명) 와 synonyms(감수된 질병 묶음) 에서만 나온다.
     · 값 앞에 # 이 붙으면 synonyms 의 묶음 이름이다(예 '#뇌졸중' = DATA.synonyms['뇌졸중']).
     · = 이 붙으면 공식 병명 전체와 같아야 한다(예 '=식도염' — 결핵성 식도염은 빼고).
     · 아무것도 없으면 공식 병명 안에 들어 있는 글자다(띄어쓰기 · '-' · '·' · ',' 는 무시).
     · 값마다 codenames 에서 1개 이상 찾아져야 한다(점검 : node scripts/check_lex.js).
       찾아지지 않는 값은 쓰지 않는다 — 모르면 넣지 않는다.

   ▣ 찾는 순서 (create(...).expand)
     1) LAY  : 일상 병명 사전에 있으면 그 공식 병명 글자로 찾는다(대장용종 → 결장의 용종 · 직장용종)
     2) 띄어쓰기 무시 : '궤양성대장염' → '궤양성 대장염'
     3) 낱말 나누기 : 질의를 WORD 표의 낱말로 나눈 뒤, 낱말마다 같은 뜻 표기 중 하나가
        병명에 모두 들어 있어야 한다(대장용종 → [결장|직장|대장] + [용종]).
        · 부정 접두어(비/불/무/미/非) 바로 뒤에 붙은 글자는 반대 뜻이라 맞추지 않는다(외상 ≠ 비외상성).
        · 한 글자 낱말(위 · 간 · 폐 · 뇌 …)은 홀로 선 말일 때만 맞춘다(위 ≠ 부위 · 위팔).
        · BLOCK 의 낱말(대장균 · 비염증 · 간질 · 부위 · 부갑상선)에 걸친 자리는 맞추지 않는다(대장 ≠ 대장균 · 위의 ≠ 부위의).
   ===================================================================== */
var MeaiLex = (function () {
  'use strict';

  /* ── 1) 일상 병명 → 공식 병명 글자(또는 '#동의어 묶음') ──
     키는 띄어쓰기 없이 적는다(검색할 때 띄어쓰기는 지운다). */
  var LAY = {
    /* 소화기 */
    '대장용종': ['결장의 용종', '직장용종'],
    '장용종': ['결장의 용종', '직장용종'],
    '대장폴립': ['결장의 용종', '직장용종'],
    '폴립': ['용종'],
    '위용종': ['위 및 십이지장의 용종'],
    '십이지장용종': ['위 및 십이지장의 용종'], '위십이지장용종': ['위 및 십이지장의 용종'], '십이지장폴립': ['위 및 십이지장의 용종'],
    '위폴립': ['위 및 십이지장의 용종'],
    '비용종': ['코용종'],
    '코폴립': ['코용종'],
    '대장선종': ['결장, 직장, 항문 및 항문관의 양성 신생물', '결장의 양성 신생물', '직장의 양성 신생물', '직장구불결장접합부의 양성 신생물'],
    '대장양성종양': ['결장, 직장, 항문 및 항문관의 양성 신생물', '결장의 양성 신생물', '직장의 양성 신생물', '직장구불결장접합부의 양성 신생물'],
    '위선종': ['위의 양성 신생물'],
    '치질': ['치핵'],
    '치루': ['항문 및 직장부의 열창 및 누공'],
    '항문농양': ['항문 및 직장부의 농양'],
    '역류성식도염': ['위-식도역류', '=식도염'],
    '위식도역류': ['위-식도역류'],
    '역류성위염': ['위-식도역류'],
    '과민성대장': ['과민대장'],
    '과민성대장증후군': ['과민대장'],
    '대장염': ['대장염', '결장염'],
    '대장게실': ['장의 게실병'],
    '게실염': ['장의 게실병'],
    '변비': ['기타 기능성 장장애'],
    '서혜부탈장': ['사타구니탈장'],
    '담석': ['#담석증'],
    '쓸개돌': ['#담석증'],
    '담낭결석': ['담석증', '담낭의 결석'],
    /* 순환기 · 뇌 */
    '중풍': ['#뇌졸중'],
    '동맥경화': ['죽상경화증'],
    '죽상경화': ['죽상경화증'],
    '하지정맥류': ['하지의 정맥류'],
    '정계정맥류': ['음낭정맥류'],
    '대동맥박리': ['대동맥동맥류 및 박리'],
    '대동맥류': ['대동맥동맥류', '대동맥류'],
    '심낭염': ['심장막염'],
    '판막질환': ['판막장애', '판막질환', '판막의 심내막염'],
    '심장판막증': ['판막장애', '판막질환', '판막의 심내막염'],
    '뇌진탕': ['두개내손상'],
    '뇌수막종': ['수막의 양성 신생물'],
    '수막종': ['수막의 양성 신생물'],
    '뇌하수체종양': ['뇌하수체의 양성 신생물'],
    '뇌하수체선종': ['뇌하수체의 양성 신생물'],
    '안면마비': ['안면신경장애'],
    '구안와사': ['안면신경장애'],
    '삼차신경통': ['삼차신경의 장애'],
    '루게릭': ['운동신경세포병'],
    '루게릭병': ['운동신경세포병'],
    '다발성경화증': ['다발경화증'],
    '수면무호흡증': ['수면무호흡'],
    '반신마비': ['편마비'],
    /* 대사 · 내분비 · 혈액 */
    '고지혈증': ['지질단백질대사장애'],
    '고지혈': ['지질단백질대사장애'],
    '이상지질혈증': ['지질단백질대사장애'],
    '고콜레스테롤혈증': ['지질단백질대사장애'],
    '콜레스테롤': ['지질단백질대사장애'],
    '갑상선결절': ['기타 비독성 고이터'],
    '갑상샘결절': ['기타 비독성 고이터'],
    '갑상선혹': ['기타 비독성 고이터', '갑상선의 양성 신생물'],
    '하시모토': ['자가면역성 갑상선염'],
    '하시모토갑상선염': ['자가면역성 갑상선염'],
    '그레이브스병': ['갑상선독증'],
    '당뇨발': ['말초순환계 합병증을 동반한'],
    '당뇨망막병증': ['당뇨병성 망막병증'],
    '재생불량성빈혈': ['무형성빈혈'],
    '혈우병': ['유전성 제8인자결핍', '유전성 제9인자결핍'],
    '자반증': ['혈소판감소성 자반'],
    '다발성골수종': ['다발골수종'],
    '골수종': ['다발골수종'],
    /* 근골격 · 외상 */
    '허리디스크': ['기타 추간판장애'],
    '요추디스크': ['기타 추간판장애'],
    '목디스크': ['경추간판장애'],
    '경추디스크': ['경추간판장애'],
    '추간판탈출': ['#추간판탈출증'],
    '척추관협착증': ['기타 척추병증', '신경관의'],
    '척추관협착': ['기타 척추병증', '신경관의'],
    '척추협착증': ['기타 척추병증', '신경관의'],
    '협착증': ['기타 척추병증', '신경관의'],
    '척추측만증': ['척주측만증'],
    '측만증': ['척주측만증'],
    '척추후만증': ['척주후만증'],
    '강직성척추염': ['강직척추염'],
    '퇴행성관절염': ['관절증'],
    '골관절염': ['관절증'],
    '류머티즘': ['류마티스'],
    '류마티즘': ['류마티스'],
    '류머티스': ['류마티스'],
    '쇼그렌': ['쉐그렌'],
    '쇼그렌증후군': ['쉐그렌'],
    '회전근개': ['어깨 및 위팔 부위의 근육 및 힘줄의 손상'],
    '회전근개파열': ['어깨 및 위팔 부위의 근육 및 힘줄의 손상'],
    '반월상연골': ['반달연골의 찢김', '무릎관절연골의 찢김'],
    '반월상연골파열': ['반달연골의 찢김', '무릎관절연골의 찢김'],
    '반월판': ['반달연골의 찢김', '무릎관절연골의 찢김'],
    '무릎연골': ['반달연골의 찢김', '무릎관절연골의 찢김'],
    '무릎연골파열': ['반달연골의 찢김', '무릎관절연골의 찢김'],
    '십자인대파열': ['십자인대의 파열'],
    '아킬레스건': ['아킬레스힘줄'],
    '아킬레스건파열': ['아킬레스힘줄'],
    '손목터널증후군': ['팔의 단일신경병증'],
    '손목터널': ['팔의 단일신경병증'],
    '수근관증후군': ['팔의 단일신경병증'],
    '테니스엘보': ['외측상과염'],
    '골프엘보': ['내측상과염'],
    '고관절골절': ['대퇴골 경부의 골절', '대퇴골 전자부 골절', '전자하 골절'],
    '압박골절': ['흉추의 골절', '요추의 골절', '병적 골절을 동반한 골다공증'],
    '척추압박골절': ['흉추의 골절', '요추의 골절', '병적 골절을 동반한 골다공증'],
    '코뼈골절': ['두개골 및 안면골의 골절'],
    '발목염좌': ['발목 및 발 부위의 관절 및 인대의 탈구, 염좌 및 긴장'],
    '발목삠': ['발목 및 발 부위의 관절 및 인대의 탈구, 염좌 및 긴장'],
    '지방종': ['지방종성'],
    /* 호흡기 · 이비인후 · 눈 */
    '축농증': ['만성 부비동염'],
    '독감': ['인플루엔자바이러스', '바이러스가 확인되지 않은 인플루엔자'],
    '인플루엔자': ['인플루엔자바이러스', '바이러스가 확인되지 않은 인플루엔자'],
    '감기': ['급성 비인두염', '급성 상기도감염'],
    '비염': ['알레르기성 비염', '만성 비염'],
    '알레르기비염': ['알레르기성 비염'],
    '편도염': ['편도 및 아데노이드의 만성 질환', '편도주위농양'],
    '편도선염': ['편도 및 아데노이드의 만성 질환', '편도주위농양'],
    '만성폐쇄성폐질환': ['만성 폐쇄성 폐질환'],
    'copd': ['만성 폐쇄성 폐질환'],
    '폐결핵': ['호흡기결핵'],
    '메니에르': ['내이의 질환'],
    '난청': ['귀의 기타 장애'],
    '다래끼': ['맥립종'],
    '포도막염': ['홍채섬모체염'],
    /* 비뇨 · 생식 */
    '신장결석': ['신장 및 요관의 결석'],
    '콩팥결석': ['신장 및 요관의 결석'],
    '요관결석': ['신장 및 요관의 결석'],
    '방광결석': ['방광의 결석'],
    '콩팥병': ['만성 콩팥병'],
    '만성신장병': ['만성 콩팥병'],
    '사구체신염': ['신염증후군'],
    '자궁근종': ['자궁의 평활근종'],
    '유방결절': ['유방의 상세불명의 덩이', '양성 유방형성이상', '유방의 양성 신생물'],
    '유방혹': ['유방의 상세불명의 덩이', '양성 유방형성이상', '유방의 양성 신생물'],
    '유방멍울': ['유방의 상세불명의 덩이'],
    /* 유방 · 기관별 혹 · 폴립 · 물혹(2026-11-13 소유자 요청 「유방 폴립이랑 이런 것」) — 공식 병명에 「폴립」이 없어 가장 가까운 공식 병명으로 */
    '유방폴립': ['유방의 양성 신생물', '양성 유방형성이상', '유방의 상세불명의 덩이'],
    '유방용종': ['유방의 양성 신생물', '양성 유방형성이상', '유방의 상세불명의 덩이'],
    '유방종양': ['유방의 양성 신생물', '양성 유방형성이상', '유방의 상세불명의 덩이'],
    '유방양성종양': ['유방의 양성 신생물'],
    '섬유선종': ['유방의 양성 신생물'],
    '유방섬유선종': ['유방의 양성 신생물'],
    '유방낭종': ['양성 유방형성이상'],
    '유방물혹': ['양성 유방형성이상'],
    '유방염': ['유방의 염증성 장애'],
    '유선염': ['유방의 염증성 장애'],
    '유방비대': ['유방의 비대'],
    '여유증': ['유방의 비대'],
    '갑상선혹': ['기타 비독성 고이터', '갑상선의 양성 신생물'],
    '갑상선물혹': ['기타 비독성 고이터'],
    '갑상선종양': ['갑상선의 양성 신생물', '갑상선 및 기타 내분비선의 악성 신생물'],
    '난소혹': ['난소의 양성 신생물'],
    '난소종양': ['난소의 양성 신생물'],
    '자궁혹': ['자궁의 평활근종', '자궁의 기타 양성 신생물'],
    '담낭용종': ['담낭의 기타 질환'],
    '담낭폴립': ['담낭의 기타 질환'],
    '쓸개용종': ['담낭의 기타 질환'],
    '간혹': ['간의 양성 신생물'],
    '간종양': ['간의 양성 신생물'],
    '간혈관종': ['간의 양성 신생물', '모든 부위의 혈관종 및 림프관종'],
    '혈관종': ['모든 부위의 혈관종 및 림프관종'],
    '췌장혹': ['췌장의 양성 신생물'],
    '췌장낭종': ['췌장의 양성 신생물', '췌장의 기타 질환'],
    '지방종': ['양성 지방종성 신생물'],
    '피지낭종': ['피부 및 피하조직의 모낭낭종'],
    '표피낭종': ['피부 및 피하조직의 모낭낭종'],
    '피부혹': ['피부 및 피하조직의 모낭낭종', '피부의 기타 양성 신생물', '양성 지방종성 신생물'],
    '음낭물혹': ['음낭수종 및 정액류'],
    '자궁경부암': ['자궁경부의 악성 신생물'],
    '자궁내막암': ['자궁체부의 악성 신생물'],
    '자궁체부암': ['자궁체부의 악성 신생물'],
    '고환암': ['고환의 악성 신생물'],
    '혀암': ['혀뿌리의 악성 신생물', '혀의 기타 및 상세불명 부분의 악성 신생물'],
    '설암': ['혀뿌리의 악성 신생물', '혀의 기타 및 상세불명 부분의 악성 신생물'],
    '골육종': ['골 및 관절연골의 악성'],
    '뼈암': ['골 및 관절연골의 악성'],
    '상피내암': ['#제자리암'],
    /* 감염 · 기타 */
    '에이즈': ['사람면역결핍바이러스병'],
    'hiv': ['사람면역결핍바이러스병'],
    '유행성출혈열': ['신장증후군을 동반한 출혈열'],
    '신증후군출혈열': ['신장증후군을 동반한 출혈열'],
    '사랑니': ['매몰치 및 매복치'],
    '매복치': ['매몰치 및 매복치'],
    '풍치': ['치은염 및 치주질환']
  };

  /* ── 2) 같은 뜻 낱말표 : 일상 말 · 신체부위 ↔ 공식 병명에 쓰인 표기 ──
     키는 질의를 나누는 낱말, 값은 병명에서 찾을 표기(하나만 있으면 된다). */
  var WORD = {
    /* 장기 */
    '대장': ['결장', '직장', '대장'], '큰창자': ['결장', '직장', '대장'],
    '소장': ['소장'], '작은창자': ['소장'], '창자': ['장'],
    '쓸개': ['담낭'], '담낭': ['담낭'], '쓸개관': ['담관', '담도'], '담관': ['담관', '담도'], '담도': ['담도', '담관'],
    '이자': ['췌장'], '췌장': ['췌장'],
    '콩팥': ['신장', '콩팥'], '신장': ['신장', '콩팥'],
    '허파': ['폐'], '폐': ['폐'],
    '염통': ['심장'], '심장': ['심장'],
    '갑상샘': ['갑상선'], '갑상선': ['갑상선'], '부갑상샘': ['부갑상선'], '부갑상선': ['부갑상선'],
    '맹장': ['맹장', '충수'], '충수': ['충수'],
    '위': ['위'], '간': ['간'], '뇌': ['뇌', '대뇌'], '식도': ['식도'], '십이지장': ['십이지장'],
    '항문': ['항문'], '직장': ['직장'], '결장': ['결장'],
    '방광': ['방광'], '요관': ['요관'], '요도': ['요도'], '전립선': ['전립선'], '고환': ['고환'],
    '자궁': ['자궁'], '자궁경부': ['자궁경부'], '난소': ['난소'], '유방': ['유방'],
    '골수': ['골수'], '혈관': ['혈관'], '림프절': ['림프절'], '피부': ['피부'],
    /* 머리 · 얼굴 */
    '머리': ['머리', '두개'], '두개': ['두개'], '얼굴': ['안면'], '안면': ['안면'],
    '코': ['코'], '귀': ['귀'], '눈': ['눈', '안구'], '입': ['입', '구강'], '혀': ['혀'],
    /* 뼈 · 관절 */
    '척추': ['척추', '척주'], '척주': ['척주', '척추'],
    '목뼈': ['경추'], '경추': ['경추'], '등뼈': ['흉추'], '흉추': ['흉추'], '허리뼈': ['요추'], '요추': ['요추'],
    '꼬리뼈': ['미추', '미골'], '엉치뼈': ['천골'],
    '갈비뼈': ['늑골'], '늑골': ['늑골'], '빗장뼈': ['쇄골'], '쇄골': ['쇄골'], '어깨뼈': ['견갑골'], '견갑골': ['견갑골'],
    '넓적다리뼈': ['대퇴골'], '허벅지뼈': ['대퇴골'], '대퇴골': ['대퇴골'], '허벅지': ['대퇴'], '넓적다리': ['대퇴'],
    '무릎뼈': ['무릎뼈'], '슬개골': ['무릎뼈'], '무릎': ['무릎'],
    '종아리': ['아래다리'], '정강이': ['아래다리'], '팔뚝': ['아래팔'], '상완': ['위팔', '상완'], '위팔': ['위팔'],
    '고관절': ['고관절'], '엉덩이': ['엉덩이', '고관절'], '어깨': ['어깨'], '팔꿈치': ['팔꿈치'],
    '손목': ['손목'], '발목': ['발목'], '손가락': ['손가락'],
    /* 병 · 다친 모양 */
    '암': ['악성신생물'], '종양': ['신생물', '종양'], '혹': ['신생물'], '양성종양': ['양성신생물'],
    '용종': ['용종'], '결석': ['결석'], '결절': ['결절'], '낭종': ['낭종'], '선종': ['선종'],
    '디스크': ['추간판'], '추간판': ['추간판'],
    '인대': ['인대'], '힘줄': ['힘줄'], '연골': ['연골'],
    '파열': ['파열', '찢김'], '찢어짐': ['찢김', '파열'], '찢김': ['찢김', '파열'],
    '염좌': ['염좌'], '삠': ['염좌'], '골절': ['골절'], '부러짐': ['골절'], '탈구': ['탈구'],
    '화상': ['화상'], '동상': ['동상'], '출혈': ['출혈'], '경색': ['경색'], '궤양': ['궤양'], '협착': ['협착'],
    '마비': ['마비'], '손상': ['손상'], '농양': ['농양'], '혈전': ['혈전'], '정맥류': ['정맥류'], '동맥류': ['동맥류'],
    '박리': ['박리'], '결핵': ['결핵'], '탈장': ['탈장'], '천공': ['천공'], '폐색': ['폐색'], '외상': ['외상']
  };

  /* 짧은 낱말로 맞추면 안 되는 긴 낱말(검색어가 그 긴 낱말을 포함할 때는 허용) */
  var BLOCK = ['대장균', '비염증', '간질', '부위', '부갑상선'];
  /* 앞 낱말에 붙여 읽는 꼬리(쓸개염 → 담낭염 · 콩팥병 → 신장병) */
  var SUFFIX = { '염': 1, '증': 1, '병': 1 };
  /* 버리는 토씨 */
  var STOP = { '의': 1, '및': 1 };
  /* 연관 검색에서 '같은 병 낱말'로 쓰기엔 너무 넓은 말 */
  var GENERIC = { '암': 1, '악성신생물': 1, '신생물': 1, '양성신생물': 1, '종양': 1, '혹': 1 };
  var NEG = ['비', '불', '무', '미', '非'];
  var HANGUL = /[가-힣]/;

  function norm(s) { return String(s == null ? '' : s).toLowerCase().replace(/[\s\-·,‐–]/g, ''); }

  function create(codenames, synonyms) {
    codenames = codenames || {}; synonyms = synonyms || {};
    var LIST = [];   // {code, name, n(정규화), o(원문 소문자)}
    for (var c in codenames) {
      if (!/^[A-Z]\d/.test(c)) continue;       // 코드 → 병명 짝만 (거꾸로 적힌 항목은 건너뜀)
      var nm = String(codenames[c]);
      LIST.push({ code: c, name: nm, n: norm(nm), o: nm.toLowerCase() });
    }
    var WKEYS = Object.keys(WORD).sort(function (a, b) { return b.length - a.length; });
    var LAYN = {}; for (var k in LAY) LAYN[norm(k)] = LAY[k];

    /* 낱말 a 가 n 의 idx 자리에서 BLOCK 낱말의 일부로만 걸린 것인가
       · BLOCK 낱말이 a 를 품는 경우(대장 ⊂ 대장균)  · a 의 앞머리가 BLOCK 낱말의 꼬리인 경우(위의… ← 부위의…)
       검색어(qTok)가 그 BLOCK 낱말을 품으면 사용자 뜻이므로 막지 않는다. */
    function blockedAt(n, a, idx, qTok) {
      for (var i = 0; i < BLOCK.length; i++) {
        var b = BLOCK[i];
        if (b === a || qTok.indexOf(b) >= 0) continue;
        var o = b.indexOf(a);
        if (o >= 0 && n.substr(idx - o, b.length) === b) return true;
        for (var s = 1; s < b.length; s++) {
          if (idx >= s && a.indexOf(b.slice(s)) === 0 && n.substr(idx - s, s) === b.slice(0, s)) return true;
        }
      }
      return false;
    }
    /* 병명 n(정규화) 안에서 낱말 a 가 맞는가 — 부정 접두어 · BLOCK 규칙 */
    function okAt(n, a, idx, qTok) {
      var prev = idx > 0 ? n.charAt(idx - 1) : '';
      if (NEG.indexOf(prev) >= 0 && NEG.indexOf(qTok.charAt(0)) < 0) return false;
      return !blockedAt(n, a, idx, qTok);
    }
    function hasMulti(n, a, qTok) {
      var idx = n.indexOf(a);
      while (idx >= 0) { if (okAt(n, a, idx, qTok)) return true; idx = n.indexOf(a, idx + 1); }
      return false;
    }
    /* 한 글자 낱말 : 앞뒤가 한글이 아닐 때만(뒤에 '의' 는 허용) */
    function hasSingle(o, a) {
      var idx = o.indexOf(a);
      while (idx >= 0) {
        var p = idx > 0 ? o.charAt(idx - 1) : '', q = o.charAt(idx + 1);
        if (!(p && HANGUL.test(p)) && (!q || !HANGUL.test(q) || q === '의')) return true;
        idx = o.indexOf(a, idx + 1);
      }
      return false;
    }
    function hasAlt(e, a, qTok) { return a.length === 1 ? hasSingle(e.o, a) : hasMulti(e.n, a, qTok); }

    /* 공식 병명 글자 하나 → 코드들 */
    function byFragment(f) {
      var fn = norm(f), out = [];
      if (fn.length < 2) return out;
      for (var i = 0; i < LIST.length; i++) if (hasMulti(LIST[i].n, fn, fn)) out.push(LIST[i].code);
      return out;
    }
    function byTarget(t) {
      if (t.charAt(0) === '#') return (synonyms[t.slice(1)] || []).slice();
      if (t.charAt(0) === '=') { var en = norm(t.slice(1)); return LIST.filter(function (e) { return e.n === en; }).map(function (e) { return e.code; }); }
      return byFragment(t);
    }

    /* 질의를 낱말로 나누기 (가장 긴 낱말 먼저) */
    function tokenize(q) {
      var toks = [];
      String(q == null ? '' : q).split(/[\s,·]+/).forEach(function (w) { tokWord(norm(w), toks); });
      return toks;
    }
    function tokWord(s, toks) {
      var raw = '', i = 0;
      function flushRaw() {
        if (!raw) return;
        if (STOP[raw]) { raw = ''; return; }
        if (SUFFIX[raw] && toks.length) { var L = toks[toks.length - 1]; L.alts = L.alts.map(function (a) { return a + raw; }); L.t += raw; }
        else toks.push({ t: raw, alts: [raw], eq: false });
        raw = '';
      }
      while (i < s.length) {
        var hit = null;
        for (var j = 0; j < WKEYS.length; j++) { var w = WKEYS[j]; if (s.substr(i, w.length) === w) { hit = w; break; } }
        if (hit) {
          flushRaw();
          var alts = WORD[hit];
          toks.push({ t: hit, alts: alts.slice(), eq: !(alts.length === 1 && alts[0] === hit) });
          i += hit.length;
        } else { raw += s.charAt(i); i++; }
      }
      flushRaw();
    }
    function byTokens(toks) {
      var out = [];
      if (!toks.length) return out;
      for (var i = 0; i < LIST.length; i++) {
        var e = LIST[i], all = true;
        for (var t = 0; t < toks.length && all; t++) {
          var tk = toks[t], any = false;
          for (var a = 0; a < tk.alts.length && !any; a++) any = hasAlt(e, tk.alts[a], tk.t);
          all = any;
        }
        if (all) out.push(e.code);
      }
      return out;
    }

    var CACHE = {}, NCACHE = 0;
    /* 질의 → { codes, via:'lay'|'nospace'|'token'|'', alias, targets }
       opt.nospace(기본 true · 'exact' 면 공식 병명 전체가 같을 때만) · opt.token(기본 true)
       opt.eqOnly(낱말 나누기는 같은 뜻 바꿈 낱말이 있을 때만) */
    function expand(q, opt) {
      opt = opt || {};
      var key = norm(q) + '|' + (opt.nospace === false ? 0 : opt.nospace === 'exact' ? 2 : 1) + (opt.token === false ? 0 : 1) + (opt.eqOnly ? 1 : 0);
      if (CACHE[key]) return CACHE[key];
      var qn = norm(q), r = { codes: [], via: '', alias: '', targets: [] };
      if (qn.length >= 2) {
        var lay = LAYN[qn];
        if (lay) {
          var set = {};
          lay.forEach(function (t) { byTarget(t).forEach(function (c) { set[c] = 1; }); });
          r.codes = Object.keys(set); r.via = 'lay'; r.targets = lay.slice();
          if (lay.length === 1 && lay[0].charAt(0) === '#' && synonyms[lay[0].slice(1)]) r.alias = lay[0].slice(1);
        }
        if (!r.codes.length && opt.nospace !== false) {
          var c1 = opt.nospace === 'exact'
            ? LIST.filter(function (e) { return e.n === qn; }).map(function (e) { return e.code; })
            : byFragment(qn);
          if (c1.length) { r.codes = c1; r.via = 'nospace'; }
        }
        if (!r.codes.length && opt.token !== false) {
          var toks = tokenize(qn);
          var useful = toks.length >= 2 || (toks.length === 1 && toks[0].eq);
          if (opt.eqOnly) useful = toks.some(function (t) { return t.eq; });
          if (useful) { var c2 = byTokens(toks); if (c2.length) { r.codes = c2; r.via = 'token'; } }
        }
      }
      if (++NCACHE > 400) { CACHE = {}; NCACHE = 0; }
      CACHE[key] = r;
      return r;
    }
    /* 묶음 동의어로만 가는 별칭(중풍 → 뇌졸중) */
    function canon(q) {
      var t = String(q || '').trim();
      if (synonyms[t]) return t;
      var lay = LAYN[norm(t)];
      if (lay && lay.length === 1 && lay[0].charAt(0) === '#' && synonyms[lay[0].slice(1)]) return lay[0].slice(1);
      return t;
    }
    /* 기존 글자 검색에서 막을 자리인가(대장 ≠ 대장균 · 비염 ≠ 비염증성) — 원래 검색의 부분일치용 */
    function blocked(name, idx, q) { return blockedAt(name, q, idx, q); }
    function nameOf(c) { return codenames[c] || ''; }

    /* 연관 검색 : 찾은 공식 병명 · 같은 병 낱말 · 겹치는 동의어 묶음 · 같은 3자리 갈래 */
    function related(q, codes, max) {
      max = max || 6;
      var qn = norm(q), cq = norm(canon(q)), out = [], seen = {};
      function add(label) {
        var ln = norm(label);
        if (!label || seen[ln] || ln === qn || ln === cq || out.length >= max) return;
        seen[ln] = 1; out.push(label);
      }
      codes = codes || [];
      var ex = expand(q), inCodes = {};
      codes.forEach(function (c) { inCodes[c] = 1; });
      // (a) 넓혀 찾은 공식 병명(3개까지)
      if (ex.via && ex.via !== 'nospace') codes.slice(0, 3).forEach(function (c) { add(nameOf(c)); });
      // (b) 같은 병 낱말(마지막 낱말 · 암 · 신생물처럼 너무 넓은 말은 빼고)을 가진 다른 병명
      var toks = tokenize(ex.alias || (ex.targets.length && /^[^#=]/.test(ex.targets[0]) ? ex.targets[0] : q));
      var last = toks.length ? toks[toks.length - 1] : null;
      function sharing(tok, n) {
        return LIST.filter(function (e) { return !inCodes[e.code] && e.code.indexOf('~') < 0 && tok.alts.some(function (a) { return hasAlt(e, a, tok.t); }); })
          .sort(function (x, y) { return x.name.length - y.name.length; }).slice(0, n);
      }
      if (last && !GENERIC[last.t] && !last.alts.some(function (a) { return GENERIC[a]; }) && last.alts.every(function (a) { return a.length >= 2; }))
        sharing(last, 4).forEach(function (e) { add(e.name); });
      // (c) 코드가 겹치는 동의어 묶음
      if (codes.length) {
        var cs = {}; codes.forEach(function (c) { cs[c] = 1; cs[c.split('.')[0]] = 1; });
        var syn = [];
        for (var k in synonyms) {
          var arr = synonyms[k] || [], hit = 0;
          for (var i = 0; i < arr.length; i++) if (cs[arr[i]]) hit++;
          if (hit) syn.push([k, arr.length]);
        }
        syn.sort(function (x, y) { return x[1] - y[1] || x[0].length - y[0].length; });
        syn.slice(0, 2).forEach(function (s2) { add(s2[0]); });
      }
      // (b2) 같은 장기(첫 낱말)를 가진 다른 병명
      var first = toks.length > 1 && !ex.alias ? toks[0] : null;
      if (first && WORD[first.t] && !GENERIC[first.t] && first.alts.every(function (a) { return a.length >= 2; }))
        sharing(first, 2).forEach(function (e) { add(e.name); });
      // (d) 아직 적으면 같은 3자리 갈래의 다른 병명
      if (out.length < 4) {
        var cats = {}; codes.slice(0, 12).forEach(function (c) { cats[c.slice(0, 3)] = 1; });
        LIST.forEach(function (e) { if (!inCodes[e.code] && cats[e.code.slice(0, 3)] && e.code.indexOf('~') < 0) add(e.name); });
      }
      return out;
    }

    /* 결과가 없을 때 : 글자가 가장 많이 겹치는 이름(두 글자 묶음 비교) */
    function bigrams(s) { var o = {}; for (var i = 0; i < s.length - 1; i++) o[s.substr(i, 2)] = 1; return o; }
    var POOL = null;
    function pool() {
      if (POOL) return POOL;
      var seen = {}, p = [];
      function put(label, kind) { var n = norm(label); if (n.length < 2 || seen[n]) return; seen[n] = 1; p.push({ label: label, n: n, g: bigrams(n), kind: kind }); }
      Object.keys(synonyms).forEach(function (k) { put(k, 'syn'); });
      Object.keys(LAY).forEach(function (k) { put(k, 'lay'); });
      LIST.forEach(function (e) { if (e.code.indexOf('~') < 0) put(e.name, 'name'); });
      POOL = p; return p;
    }
    function closest(q, max, ok) {
      max = max || 6;
      var qn = norm(q); if (qn.length < 2) return [];
      var qg = bigrams(qn), nq = Object.keys(qg).length || 1;
      var toks = tokenize(qn).filter(function (t) { return t.t.length >= 2 || t.eq; });
      var scored = [];
      pool().forEach(function (e) {
        // BLOCK 낱말에 걸친 이름은 권하지 않는다(대장출혈 → 장출혈성 대장균감염 ✗)
        for (var b = 0; b < BLOCK.length; b++) {
          var bw = BLOCK[b];
          if (e.n.indexOf(bw) >= 0 && qn.indexOf(bw) < 0 && toks.some(function (t) { return bw.indexOf(t.t) >= 0; })) return;
        }
        var hit = 0; for (var g in qg) if (e.g[g]) hit++;
        var ne = Object.keys(e.g).length || 1, s = 2 * hit / (nq + ne);
        toks.forEach(function (t) { if (t.alts.some(function (a) { return a.length >= 2 && e.n.indexOf(a) >= 0; })) s += 0.25; });
        if (e.kind !== 'name') s += 0.05;
        if (s >= 0.3 && e.n !== qn) scored.push([s, e.label]);
      });
      scored.sort(function (a, b) { return b[0] - a[0] || a[1].length - b[1].length; });
      var out = [];
      for (var i = 0; i < scored.length && out.length < max && i < 40; i++) {
        if (!ok || ok(scored[i][1])) out.push(scored[i][1]);
      }
      return out;
    }

    /* 자동완성용 : 일상 병명 키와 그 공식 병명 */
    function layEntries() {
      return Object.keys(LAY).map(function (k) {
        var ex = expand(k);
        return { text: k, codes: ex.codes, names: ex.codes.map(function (c) { return { code: c, name: nameOf(c) }; }), alias: ex.alias };
      }).filter(function (x) { return x.codes.length; });
    }

    return { expand: expand, canon: canon, related: related, closest: closest, tokenize: tokenize,
             blocked: blocked, layEntries: layEntries, byTarget: byTarget, norm: norm, nameOf: nameOf };
  }

  return { create: create, LAY: LAY, WORD: WORD, BLOCK: BLOCK, norm: norm };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = MeaiLex;
