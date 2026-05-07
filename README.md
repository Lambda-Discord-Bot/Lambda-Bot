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

## 7) 프로젝트 구조 (기능별 분리)

```text
bot/
  core/                         # 봇 실행/클라이언트/락
  shared/                       # 공통 권한/브랜딩/임베드 유틸
  features/
    admin/                      # 관리자 패널 기능
      cogs/
      views/
      modals/
      helpers/
    ticket/                     # 문의 기능
      cogs/
      views/
      modals/
      helpers/
    music/                      # 음악 기능
      cogs/
      views/
      modals/
      helpers/
      services/
  services/                     # 데이터 저장/로그/재생 핵심 서비스
  ui/                           # 기존 경로 호환 래퍼
  cogs/                         # 기존 경로 호환 래퍼
  utils/                        # 기존 경로 호환 래퍼
```
