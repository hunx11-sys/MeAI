// MeAI 설치 스크립트(video/openmontage_setup.sh)가 오픈몽타주의 remotion-composer/ 에 복사해 넣는 설정.
// 오픈몽타주 원본에는 없는 파일이다.
//
// 하는 일 : 화면을 찍는 브라우저를 인터넷에서 새로 내려받지 않고, 이 컴퓨터에 이미 있는 것을 쓴다.
// (이 작업 환경은 그 내려받기 주소가 막혀 있어서, 이 설정이 없으면 렌더가 시작도 못 한다.)
import { Config } from "@remotion/cli/config";
import fs from "fs";

const candidates = [
  process.env.OPENMONTAGE_CHROME,
  "/opt/pw-browsers/chromium_headless_shell",
].filter(Boolean) as string[];

const found = candidates.find((p) => fs.existsSync(p));
if (found) {
  Config.setBrowserExecutable(found);
  Config.setChromeMode("headless-shell");
}
