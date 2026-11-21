import math
import os
from collections.abc import Callable
from datetime import datetime, timezone

DECAY_RATE = float(os.environ.get("ENGRAM_DECAY_RATE", "0.005"))


def current_strength(
    initial_strength: float,
    last_accessed_at: datetime,
    decay_fn: Callable[[float, float], float] | None = None,
) -> float:
    hours = (datetime.now(timezone.utc) - last_accessed_at).total_seconds() / 3600
    # if custom_function present, call it else the default
    if decay_fn is not None:
        return decay_fn(initial_strength, hours)
    
    return initial_strength * math.exp(-DECAY_RATE * hours)


def reinforce(current: float, boost: float = 0.3) -> float:
    return min(1.0, current + boost)
