from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
SETTINGS_FILE = DATA_DIR / "guild_settings.json"

# 현재 작업 폴더와 무관하게 프로젝트 루트의 .env를 읽도록 고정
# override=True: 셸에 빈 값이 있어도 .env 값을 우선 적용
load_dotenv(dotenv_path=ROOT_DIR / ".env", override=True, encoding="utf-8-sig")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")
