from __future__ import annotations

import atexit
import os
from pathlib import Path


class SingleInstanceLock:
    def __init__(self, lock_file: Path) -> None:
        self.lock_file = lock_file

    @staticmethod
    def _is_process_running(pid: int) -> bool:
        if pid <= 0:
            return False
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    def acquire(self) -> None:
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        current_pid = os.getpid()

        if self.lock_file.exists():
            try:
                previous_pid = int(self.lock_file.read_text(encoding="utf-8").strip())
            except (ValueError, OSError):
                previous_pid = -1

            if previous_pid != current_pid and self._is_process_running(previous_pid):
                raise RuntimeError(
                    f"이미 실행 중인 봇 프로세스가 있습니다. (PID: {previous_pid})\n"
                    "기존 프로세스를 종료한 뒤 다시 실행해주세요."
                )

        self.lock_file.write_text(str(current_pid), encoding="utf-8")

        def _cleanup_lock() -> None:
            try:
                if self.lock_file.exists():
                    content = self.lock_file.read_text(encoding="utf-8").strip()
                    if content == str(current_pid):
                        self.lock_file.unlink()
            except OSError:
                pass

        atexit.register(_cleanup_lock)
