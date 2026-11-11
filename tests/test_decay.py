from datetime import datetime, timedelta, timezone

import pytest


def test_strength_at_zero_elapsed_is_unchanged():
    from engram.decay import current_strength
    now = datetime.now(timezone.utc)
    assert current_strength(1.0, now) == pytest.approx(1.0, abs=0.001)


def test_strength_decays_over_time():
    from engram.decay import current_strength
    past = datetime.now(timezone.utc) - timedelta(hours=200)
    result = current_strength(1.0, past)
    assert result < 0.37  # e^(-0.005 * 200) ≈ 0.368


def test_strength_scales_with_initial():
    from engram.decay import current_strength
    past = datetime.now(timezone.utc) - timedelta(hours=100)
    full = current_strength(1.0, past)
    half = current_strength(0.5, past)
    assert half == pytest.approx(full * 0.5, rel=0.01)


def test_reinforce_adds_boost():
    from engram.decay import reinforce
    assert reinforce(0.5) == pytest.approx(0.8, abs=0.001)


def test_reinforce_caps_at_one():
    from engram.decay import reinforce
    assert reinforce(0.9) == 1.0
    assert reinforce(1.0) == 1.0


def test_custom_decay_rate_overrides_global():
    from engram.decay import DECAY_RATE, current_strength

    past = datetime.now(timezone.utc) - timedelta(hours=100)
    assert current_strength(1.0, past, DECAY_RATE * 10) < current_strength(1.0, past)
    assert current_strength(1.0, past, 0.0) == pytest.approx(1.0)


@pytest.mark.parametrize("bad", [-0.1, float("nan"), float("inf")])
def test_validate_decay_rate_rejects_bad_values(bad):
    from engram.decay import validate_decay_rate

    with pytest.raises(ValueError):
        validate_decay_rate(bad)
