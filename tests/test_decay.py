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


def test_custom_decay_fn_is_called():
    from engram.decay import current_strength
    calls = []

    def my_decay(strength: float, hours: float) -> float:
        calls.append((strength, hours))
        return strength * 0.5

    past = datetime.now(timezone.utc) - timedelta(hours=10)
    result = current_strength(0.8, past, decay_fn=my_decay)

    assert len(calls) == 1
    assert calls[0][0] == pytest.approx(0.8)
    assert calls[0][1] == pytest.approx(10.0, abs=0.1)
    assert result == pytest.approx(0.4)


def test_custom_decay_fn_result_matches_expected():
    from engram.decay import current_strength

    def power_law(strength: float, hours: float) -> float:
        return strength / (1 + 0.01 * hours)

    past = datetime.now(timezone.utc) - timedelta(hours=100)
    result = current_strength(1.0, past, decay_fn=power_law)
    assert result == pytest.approx(1.0 / (1 + 0.01 * 100), rel=0.01)


def test_default_used_when_decay_fn_not_set():
    import math

    from engram.decay import DECAY_RATE, current_strength

    past = datetime.now(timezone.utc) - timedelta(hours=50)
    result = current_strength(1.0, past)
    expected = math.exp(-DECAY_RATE * 50)
    assert result == pytest.approx(expected, rel=0.01)


def test_configure_validates_decay_fn_signature():
    import engram

    engram.reset()

    with pytest.raises(TypeError, match="2 positional arguments"):
        engram.configure(decay_fn=lambda x: x)

    engram.reset()


def test_configure_rejects_non_callable():
    import engram

    engram.reset()

    with pytest.raises(TypeError, match="callable"):
        engram.configure(decay_fn="not_a_function")  # type: ignore[arg-type]

    engram.reset()

