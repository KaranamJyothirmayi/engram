import math
import os
from datetime import datetime, timezone

DECAY_RATE = float(os.environ.get("ENGRAM_DECAY_RATE", "0.005"))
RECALL_BOOST = float(os.environ.get("ENGRAM_RECALL_BOOST", "0.3"))


def current_strength(initial_strength: float, last_accessed_at: datetime) -> float:
    hours = (datetime.now(timezone.utc) - last_accessed_at).total_seconds() / 3600
    return initial_strength * math.exp(-DECAY_RATE * hours)


def reinforce(current: float, boost: float = RECALL_BOOST) -> float:
    return min(1.0, current + boost)
