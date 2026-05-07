# Discord Lambda bot

`discord.py` 기반 관리자 패널 + 문의/음악 시스템 봇입니다.

## 1) 설치

```powershell
cd "C:\Users\hyunw\Desktop\Discord Lambda Bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2) 환경 변수 설정

`.env.example`을 복사해 `.env` 파일을 만들고 토큰을 입력하세요.

```powershell
Copy-Item .env.example .env
notepad .env
```

필수 값:
- `DISCORD_TOKEN`

선택 값:
- `TEST_GUILD_ID` (개발 서버 ID, 설정 시 슬래시 명령어 반영이 빠름)

## 3) 실행

```powershell
python run.py
```

## 4) 음악 기능 추가 준비 (필수)

음악 재생은 로컬에 `ffmpeg`가 설치되어 있어야 합니다.

Windows 예시 확인:
```powershell
ffmpeg -version
```

명령이 없으면 ffmpeg 설치 후 `PATH` 등록이 필요합니다.

## 5) 봇 권한(권장)

- `Manage Channels`
- `Send Messages`
- `Embed Links`
- `Attach Files`
- `Read Message History`
- `View Channels`
- `Connect`
- `Speak`

## 6) 주요 명령어

- `/람다패널등록 [채널]`
- `/람다문의관리 패널 [채널]`
- `/람다문의관리 카테고리 [카테고리]`
- `/람다문의관리 로그 [채널]`
- `/람다문의관리 멘션역할 추가 [역할]`
- `/람다문의관리 멘션역할 제거 [역할]`
- `/람다문의관리 멘션역할 목록`
- `/람다문의관리 멘션역할 초기화`
- `/람다문의관리 초기화`
- `/람다음악관리 패널 [채널]`
- `/람다음악관리 볼륨 [1~100]`
- `/람다음악관리 초기화`

## 7) 프로젝트 구조 (한눈에 보기)

```text
bot/
├─ core/              # 실행, 봇 클라이언트, 중복 실행 방지
├─ features/          # 기능별 코드
│  ├─ admin/          # 관리자 패널
│  ├─ ticket/         # 문의 시스템
│  └─ music/          # 음악 시스템
├─ services/          # 설정 저장(JSON), 문의 로그, 음악 재생 핵심
├─ shared/            # 공통 코드(권한 체크, 임베드 공통, 브랜딩)
├─ cogs/              # 레거시 import 호환용
├─ ui/                # 레거시 import 호환용
└─ utils/             # 레거시 import 호환용
```

처음 수정할 때는 보통 아래만 보면 됩니다.
- 관리자 기능: `bot/features/admin`
- 문의 기능: `bot/features/ticket`
- 음악 기능: `bot/features/music`
- 서버별 설정 저장: `bot/services/settings_service.py`
