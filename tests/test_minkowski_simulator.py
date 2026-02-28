import random

from minkowski_simulator import (
    Event,
    IntervalType,
    WorldLine,
    classify_interval,
    conditional_simulation,
    light_vs_rest_interaction,
    spontaneous_events,
)


def test_interval_classification():
    assert classify_interval(Event(0, 0), Event(2, 1)) == IntervalType.TIMELIKE
    assert classify_interval(Event(0, 0), Event(1, 2)) == IntervalType.SPACELIKE
    assert classify_interval(Event(0, 0), Event(3, 3)) == IntervalType.NULL


def test_light_vs_rest_interaction_forward_only():
    hit = light_vs_rest_interaction(Event(0, 0), rest_x=5, light_direction=1)
    assert hit is not None
    assert hit.t == 5
    assert hit.x == 5

    miss = light_vs_rest_interaction(Event(0, 0), rest_x=5, light_direction=-1)
    assert miss is None


def test_spontaneous_events_reproducible():
    wl = WorldLine(0, 0.1)
    events = spontaneous_events(
        wl,
        t_start=0,
        t_end=1,
        dt=0.2,
        probability_per_step=0.5,
        rng=random.Random(1),
    )
    assert [round(e.t, 1) for e in events] == [0.0, 0.6, 0.8, 1.0]


def test_conditional_simulation():
    a = WorldLine(x0=-1, v=1, label="a")
    b = WorldLine(x0=1, v=-1, label="b")

    close = conditional_simulation(
        [a, b],
        t_start=0,
        t_end=2,
        dt=0.5,
        predicate=lambda _t, evs: abs(evs[0].x - evs[1].x) <= 0.5,
    )

    assert [e.t for e in close] == [1.0]
