from __future__ import annotations

import asyncio
import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import discord

logger = logging.getLogger(__name__)

YOUTUBE_DOMAIN_PATTERN = re.compile(r"(?:youtube\.com|youtu\.be|music\.youtube\.com)", re.IGNORECASE)
URL_PATTERN = re.compile(r"^https?://", re.IGNORECASE)


class MusicServiceError(Exception):
    pass


class RepeatMode(str, Enum):
    NONE = "none"
    ONE = "one"
    ALL = "all"


@dataclass
class MusicTrack:
    title: str
    webpage_url: str
    stream_url: str
    requester_id: int
    duration: int | None = None
    thumbnail_url: str | None = None
    uploader: str | None = None


@dataclass
class GuildMusicState:
    queue: list[MusicTrack] = field(default_factory=list)
    history: list[MusicTrack] = field(default_factory=list)
    current: MusicTrack | None = None
    repeat_mode: RepeatMode = RepeatMode.NONE
    idle_task: asyncio.Task | None = None


class MusicPlayerService:
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self._states: dict[int, GuildMusicState] = {}
        self._locks: dict[int, asyncio.Lock] = {}

    def _get_lock(self, guild_id: int) -> asyncio.Lock:
        lock = self._locks.get(guild_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[guild_id] = lock
        return lock

    def get_state(self, guild_id: int) -> GuildMusicState:
        state = self._states.get(guild_id)
        if state is None:
            state = GuildMusicState()
            self._states[guild_id] = state
        return state

    async def connect_to_member_voice(self, member: discord.Member) -> discord.VoiceClient:
        voice_state = member.voice
        if voice_state is None or voice_state.channel is None:
            raise MusicServiceError("먼저 음성 채널에 입장해주세요.")

        voice_client = member.guild.voice_client
        try:
            if voice_client is None:
                # reconnect=False: 내부 재시도 루프를 줄여 들락날락 현상을 완화
                return await voice_state.channel.connect(timeout=20.0, reconnect=False, self_deaf=True)

            if not voice_client.is_connected():
                try:
                    await voice_client.disconnect(force=True)
                except Exception:  # noqa: BLE001
                    pass
                return await voice_state.channel.connect(timeout=20.0, reconnect=False, self_deaf=True)

            if voice_client.channel is not None and voice_client.channel.id != voice_state.channel.id:
                await voice_client.move_to(voice_state.channel)

            return voice_client
        except asyncio.TimeoutError as exc:
            raise MusicServiceError("음성 채널 연결 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.") from exc
        except Exception as exc:  # noqa: BLE001
            close_code = getattr(exc, "code", None)
            if close_code == 4017:
                raise MusicServiceError(
                    "디스코드 음성 서버 연결(4017)에 실패했습니다. "
                    "잠시 후 다시 시도하거나, 음성 채널을 나갔다가 다시 입장해보세요."
                ) from exc
            raise MusicServiceError(f"음성 채널 연결에 실패했습니다: {exc.__class__.__name__}") from exc

    def _validate_music_input(self, query: str, settings: dict) -> tuple[bool, str]:
        value = query.strip()
        if not value:
            raise MusicServiceError("재생할 곡 제목 또는 유튜브 URL을 입력해주세요.")

        is_url = bool(URL_PATTERN.match(value))
        if is_url:
            if not YOUTUBE_DOMAIN_PATTERN.search(value):
                raise MusicServiceError("유튜브 URL만 재생할 수 있습니다.")

        return is_url, value

    async def _extract_track(self, query: str, settings: dict, requester_id: int) -> MusicTrack:
        is_url, value = self._validate_music_input(query, settings)

        try:
            import yt_dlp
        except ImportError as exc:
            raise MusicServiceError("`yt-dlp`가 설치되지 않았습니다. `pip install -r requirements.txt`를 먼저 실행해주세요.") from exc

        ytdl_options: dict[str, Any] = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": True,
            "default_search": "ytsearch1",
            "nocheckcertificate": True,
            "extract_flat": False,
            "source_address": "0.0.0.0",
        }

        extract_target = value if is_url else f"ytsearch1:{value}"

        def _worker() -> dict[str, Any]:
            with yt_dlp.YoutubeDL(ytdl_options) as ydl:
                data = ydl.extract_info(extract_target, download=False)
                if data is None:
                    raise MusicServiceError("곡 정보를 가져오지 못했습니다.")
                if "entries" in data:
                    entries = data.get("entries") or []
                    if not entries:
                        raise MusicServiceError("검색 결과를 찾지 못했습니다.")
                    data = entries[0]
                return data

        info = await asyncio.to_thread(_worker)
        stream_url = info.get("url")
        if not stream_url:
            raise MusicServiceError("오디오 스트림 URL을 가져오지 못했습니다.")

        title = str(info.get("title") or "제목 없음")
        webpage_url = str(info.get("webpage_url") or value)
        duration_raw = info.get("duration")
        duration = int(duration_raw) if isinstance(duration_raw, (int, float)) else None
        thumbnail_url_raw = info.get("thumbnail")
        thumbnail_url = str(thumbnail_url_raw) if thumbnail_url_raw else None
        uploader_raw = info.get("uploader") or info.get("channel")
        uploader = str(uploader_raw) if uploader_raw else None

        return MusicTrack(
            title=title,
            webpage_url=webpage_url,
            stream_url=stream_url,
            requester_id=requester_id,
            duration=duration,
            thumbnail_url=thumbnail_url,
            uploader=uploader,
        )

    def _build_audio_source(self, stream_url: str, volume: int) -> discord.AudioSource:
        ffmpeg_executable = self._resolve_ffmpeg_executable()
        if ffmpeg_executable is None:
            raise MusicServiceError(
                "ffmpeg 실행 파일을 찾지 못했습니다. "
                "PATH를 설정하거나 FFMPEG_PATH 환경변수에 ffmpeg.exe 경로를 지정해주세요."
            )

        ffmpeg_options = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }
        source = discord.FFmpegPCMAudio(stream_url, executable=ffmpeg_executable, **ffmpeg_options)
        return discord.PCMVolumeTransformer(source, volume=max(1, min(100, volume)) / 100)

    def _resolve_ffmpeg_executable(self) -> str | None:
        configured = os.getenv("FFMPEG_PATH", "").strip()
        if configured and os.path.isfile(configured):
            return configured

        found = shutil.which("ffmpeg")
        if found:
            return found

        local_appdata = os.getenv("LOCALAPPDATA", "")
        if local_appdata:
            gyan_default = os.path.join(
                local_appdata,
                "Microsoft",
                "WinGet",
                "Packages",
                "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe",
                "ffmpeg-8.1.1-full_build",
                "bin",
                "ffmpeg.exe",
            )
            if os.path.isfile(gyan_default):
                return gyan_default

        return None

    def _cancel_idle_task(self, guild_id: int) -> None:
        state = self.get_state(guild_id)
        if state.idle_task is not None and not state.idle_task.done():
            state.idle_task.cancel()
        state.idle_task = None

    async def enqueue(self, guild: discord.Guild, query: str, requester: discord.Member, settings: dict) -> tuple[MusicTrack, bool, int]:
        if not bool(settings.get("music_enabled", True)):
            raise MusicServiceError("현재 서버에서 음악 기능이 OFF 상태입니다.")

        track = await self._extract_track(query, settings, requester.id)
        guild_id = guild.id

        async with self._get_lock(guild_id):
            state = self.get_state(guild_id)
            state.queue.append(track)
            queue_size = len(state.queue)
            self._cancel_idle_task(guild_id)

            voice_client = guild.voice_client
            started_now = voice_client is not None and state.current is None and not voice_client.is_playing() and not voice_client.is_paused()
            if started_now:
                await self._play_next_locked(guild, settings)

        return track, started_now, queue_size

    async def _play_next_locked(self, guild: discord.Guild, settings: dict) -> None:
        guild_id = guild.id
        state = self.get_state(guild_id)
        voice_client = guild.voice_client
        if voice_client is None or not voice_client.is_connected():
            state.current = None
            return

        next_track: MusicTrack | None = None

        if state.repeat_mode == RepeatMode.ONE and state.current is not None:
            next_track = state.current
        else:
            if state.current is not None and state.repeat_mode in (RepeatMode.NONE, RepeatMode.ALL):
                state.history.append(state.current)
                if len(state.history) > 100:
                    state.history = state.history[-100:]

            if state.queue:
                next_track = state.queue.pop(0)
            elif state.repeat_mode == RepeatMode.ALL and state.history:
                state.queue = list(state.history)
                state.history.clear()
                next_track = state.queue.pop(0) if state.queue else None

        if next_track is None:
            state.current = None
            self._schedule_idle_disconnect(guild, settings)
            return

        state.current = next_track

        try:
            source = self._build_audio_source(next_track.stream_url, int(settings.get("music_default_volume", 50)))
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to build source: %s", exc)
            state.current = None
            raise MusicServiceError("오디오 소스를 준비하는 데 실패했습니다. ffmpeg 설치 여부를 확인해주세요.") from exc

        def _after_play(error: Exception | None) -> None:
            if error:
                logger.warning("Voice playback error in guild %s: %s", guild_id, error)
            future = asyncio.run_coroutine_threadsafe(self._advance_after_play(guild_id), self.bot.loop)
            try:
                future.result()
            except Exception:  # noqa: BLE001
                logger.exception("Failed advancing queue for guild %s", guild_id)

        voice_client.play(source, after=_after_play)

    async def _advance_after_play(self, guild_id: int) -> None:
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return

        settings = await self.bot.settings_service.get_guild_settings(guild_id)
        async with self._get_lock(guild_id):
            await self._play_next_locked(guild, settings)

    def _schedule_idle_disconnect(self, guild: discord.Guild, settings: dict) -> None:
        guild_id = guild.id
        minutes = int(settings.get("music_auto_disconnect_minutes", 10))
        seconds = max(1, minutes) * 60

        async def _idle_worker() -> None:
            try:
                await asyncio.sleep(seconds)
                state = self.get_state(guild_id)
                voice_client = guild.voice_client
                if voice_client is None:
                    return
                if voice_client.is_playing() or voice_client.is_paused() or state.queue or state.current is not None:
                    return
                await voice_client.disconnect(force=True)
            except asyncio.CancelledError:
                return
            except Exception:  # noqa: BLE001
                logger.exception("Idle disconnect failed for guild %s", guild_id)

        self._cancel_idle_task(guild_id)
        state = self.get_state(guild_id)
        state.idle_task = asyncio.create_task(_idle_worker())

    async def pause(self, guild: discord.Guild) -> None:
        voice_client = guild.voice_client
        if voice_client is None or not voice_client.is_playing():
            raise MusicServiceError("현재 재생 중인 곡이 없습니다.")
        voice_client.pause()

    async def resume(self, guild: discord.Guild) -> None:
        voice_client = guild.voice_client
        if voice_client is None or not voice_client.is_paused():
            raise MusicServiceError("현재 일시정지된 곡이 없습니다.")
        voice_client.resume()

    async def skip(self, guild: discord.Guild) -> None:
        voice_client = guild.voice_client
        if voice_client is None or not (voice_client.is_playing() or voice_client.is_paused()):
            raise MusicServiceError("스킵할 곡이 없습니다.")
        voice_client.stop()

    async def stop(self, guild: discord.Guild) -> None:
        state = self.get_state(guild.id)
        state.queue.clear()
        state.history.clear()
        state.current = None

        voice_client = guild.voice_client
        if voice_client is not None and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()

    async def disconnect(self, guild: discord.Guild) -> None:
        state = self.get_state(guild.id)
        state.queue.clear()
        state.history.clear()
        state.current = None
        self._cancel_idle_task(guild.id)

        voice_client = guild.voice_client
        if voice_client is not None:
            await voice_client.disconnect(force=True)

    def cycle_repeat_mode(self, guild_id: int) -> RepeatMode:
        state = self.get_state(guild_id)
        if state.repeat_mode == RepeatMode.NONE:
            state.repeat_mode = RepeatMode.ONE
        elif state.repeat_mode == RepeatMode.ONE:
            state.repeat_mode = RepeatMode.ALL
        else:
            state.repeat_mode = RepeatMode.NONE
        return state.repeat_mode

    def shuffle_queue(self, guild_id: int) -> int:
        import random

        state = self.get_state(guild_id)
        random.shuffle(state.queue)
        return len(state.queue)

    def get_queue_snapshot(self, guild_id: int) -> tuple[MusicTrack | None, list[MusicTrack], RepeatMode]:
        state = self.get_state(guild_id)
        return state.current, list(state.queue), state.repeat_mode

    def is_connected(self, guild: discord.Guild) -> bool:
        voice_client = guild.voice_client
        return voice_client is not None and voice_client.is_connected()
