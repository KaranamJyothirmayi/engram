import math
import os
from datetime import datetime, timezone

DECAY_RATE = float(os.environ.get("ENGRAM_DECAY_RATE", "0.005"))


def validate_decay_rate(decay_rate: float) -> float:
    rate = float(decay_rate)
    if not math.isfinite(rate) or rate < 0:
        raise ValueError(f"decay_rate must be a finite number >= 0, got {decay_rate!r}")
    return rate


def current_strength(
    initial_strength: float,
    last_accessed_at: datetime,
    decay_rate: float | None = None,
) -> float:
    rate = DECAY_RATE if decay_rate is None else decay_rate
    hours = (datetime.now(timezone.utc) - last_accessed_at).total_seconds() / 3600
    return initial_strength * math.exp(-rate * hours)


def reinforce(current: float, boost: float = 0.3) -> float:
    return min(1.0, current + boost)
