from __future__ import annotations

import re


def safe_ticket_channel_name(raw: str, fallback: str) -> str:
    base = raw.strip().lower()
    base = re.sub(r"\s+", "-", base)
    base = re.sub(r"[^a-z0-9가-힣_-]", "", base)
    if not base:
        base = fallback
    return base[:90]
