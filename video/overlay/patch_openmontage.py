#!/usr/bin/env python3
"""오픈몽타주에 이 작업 환경용 작은 보정을 얹는다(MeAI 설치 스크립트가 부른다 · 몇 번 돌려도 같다).

    python patch_openmontage.py <오픈몽타주 폴더>

1. NASA : 자료 목록이 http:// 주소를 돌려준다. 이 환경은 암호화된 https 만 통과시키므로
   같은 파일을 https 로 받게 바꾼다(같은 파일이 https 로 열리는 것을 2026-11-22 확인).

원본 코드가 바뀌어 보정할 자리를 못 찾으면 그 항목만 건너뛰고 알린다(오류로 멈추지 않는다).
"""
from __future__ import annotations

import sys
from pathlib import Path

MARK = "# MeAI patch"


def patch(path: Path, old: str, new: str, label: str) -> None:
    s = path.read_text(encoding="utf-8")
    if MARK + ": " + label in s:
        print(f"    보정 이미 됨 : {label}")
        return
    if old not in s:
        print(f"    [건너뜀] 보정할 자리를 못 찾음 : {label} ({path.name})")
        return
    path.write_text(s.replace(old, new, 1), encoding="utf-8")
    print(f"    보정함 : {label}")


def main() -> int:
    om = Path(sys.argv[1])
    nasa = om / "tools/video/stock_sources/nasa.py"
    patch(
        nasa,
        "        asset_href = item.get(\"href\")\n        if not asset_href:\n            return None\n",
        "        asset_href = item.get(\"href\")\n        if not asset_href:\n            return None\n"
        f"        {MARK}: nasa-https\n"
        "        asset_href = asset_href.replace(\"http://\", \"https://\", 1)\n",
        "nasa-https",
    )
    patch(
        nasa,
        "        download_url = _encode_url_path(download_url)\n",
        "        download_url = _encode_url_path(download_url)\n"
        f"        {MARK}: nasa-https-download\n"
        "        if download_url.startswith(\"http://\"):\n"
        "            download_url = \"https://\" + download_url[len(\"http://\"):]\n",
        "nasa-https-download",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
