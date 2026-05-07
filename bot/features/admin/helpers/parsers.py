from __future__ import annotations


def parse_on_off(value: str) -> bool | None:
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized in {"on", "o", "1", "true", "허용", "예", "y"}:
        return True
    if normalized in {"off", "x", "0", "false", "차단", "아니오", "n"}:
        return False
    return None
