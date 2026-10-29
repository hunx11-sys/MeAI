// 모의 서버 응답 견본 뽑기 : node home_nudge/tools/dump_mock.js > 견본.json  (tools/check_contract.py 가 씀)
const M = require('../src/api/mock.js'), fs = require('fs'), path = require('path');
const D = path.join(__dirname, '..'), J = (p) => JSON.parse(fs.readFileSync(path.join(D, p), 'utf8'));
const data = { cfg: J('config/nudge.config.json'), cal: J('data/calendar.json'), quiz: J('data/quiz.json'), talks: J('data/talks798.json'), seed: J('data/seed.json'), ox: J('data/ox_bank.json') };
(async () => {
  const api = M.createMockApi(data, { latency: 0, issueOn: 'chat.custom', frozen: true });
  const out = {};
  out.Home = await api.getHome();
  out.ActionResult_attend = await api.attend();
  out.ActionResult_quiz = await api.answerQuiz(out.Home.quiz.id, 'O');
  out.ActionResult_reco = await api.event('reco.open', { customerId: 'c-504' });
  out.ActionResult_chat = await api.event('chat.custom', { customerId: 'c-504' });
  // 행운 존
  out.ActionResult_spin = await api.spinRoulette();
  const sp = out.ActionResult_spin.data;
  if (sp && sp.customers[0]) out.ActionResult_crm = await api.crmDone('r:' + sp.spinId, sp.customers[0]);
  out.ActionResult_pull = await api.pullSlot();
  out.ActionResult_chstart = await api.startChallenge();
  out.ActionResult_chans = await api.answerChallenge(out.ActionResult_chstart.data.runId, 0, 'O', 2300);
  out.ActionResult_tarot = await api.drawTarot(1);
  const sc = out.ActionResult_tarot.home.fun.scratch.cards[0];
  if (sc) out.ActionResult_scratch = await api.revealScratch(sc.id);
  out.ActionResult_nope = await api.spinRoulette();
  out.TalkPage = await api.listTalks({ cat: 'B', size: 5 });
  out.Talk = await api.getTalk(out.TalkPage.items[0].id);
  out.League = await api.getLeague('branch');
  out.ScopeRank = await api.getLeague('company');
  out.Record = await api.getRecord();
  out.Recap = await api.getRecap();
  out.OrgDash = await api.getOrgDash('hq');
  out.HqDash = await api.getHqDash();
  await api.demo.setTime('2026-10-30', '17:05');
  out.Home_friday = await api.getHome();
  process.stdout.write(JSON.stringify(out));
})();
