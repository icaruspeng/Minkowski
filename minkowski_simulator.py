"""Minkowski spacetime simulator (1+1 dimensions).

Features:
- Events and world lines
- Interval classification: timelike / spacelike / null
- Null lines (lightlike world lines)
- Conditional simulation hooks
- Spontaneous event generation
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Optional
import random


class IntervalType(str, Enum):
    """Classification for spacetime separation."""

    TIMELIKE = "timelike"
    SPACELIKE = "spacelike"
    NULL = "null"


@dataclass(frozen=True)
class Event:
    """A point in 1+1D spacetime.

    Attributes:
        t: Time coordinate.
        x: Space coordinate.
        label: Optional human-readable name.
    """

    t: float
    x: float
    label: str = ""


@dataclass(frozen=True)
class WorldLine:
    """Inertial world line in 1+1D spacetime.

    x(t) = x0 + v * (t - t0)
    """

    x0: float
    v: float
    t0: float = 0.0
    label: str = ""

    def position_at(self, t: float) -> float:
        return self.x0 + self.v * (t - self.t0)

    def event_at(self, t: float, label: str = "") -> Event:
        return Event(t=t, x=self.position_at(t), label=label or self.label)


def spacetime_interval_squared(a: Event, b: Event, c: float = 1.0) -> float:
    """Compute s^2 = (c Δt)^2 - (Δx)^2."""

    dt = b.t - a.t
    dx = b.x - a.x
    return (c * dt) ** 2 - dx**2


def classify_interval(a: Event, b: Event, c: float = 1.0, tol: float = 1e-9) -> IntervalType:
    """Classify interval between two events as timelike/spacelike/null."""

    s2 = spacetime_interval_squared(a, b, c=c)
    if abs(s2) <= tol:
        return IntervalType.NULL
    if s2 > 0:
        return IntervalType.TIMELIKE
    return IntervalType.SPACELIKE


def null_line_through(event: Event, direction: int = 1, c: float = 1.0, label: str = "light") -> WorldLine:
    """Create a lightlike world line through an event.

    direction=+1 for right-moving light, -1 for left-moving light.
    """

    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or +1")
    return WorldLine(x0=event.x, v=direction * c, t0=event.t, label=label)


def intersection_time(a: WorldLine, b: WorldLine, tol: float = 1e-12) -> Optional[float]:
    """Return coordinate time where two inertial world lines intersect, if unique."""

    # a.x0 + a.v(t-a.t0) = b.x0 + b.v(t-b.t0)
    av = a.v
    bv = b.v
    denom = av - bv
    if abs(denom) <= tol:
        # Parallel (or identical) in this frame.
        return None

    a_const = a.x0 - a.v * a.t0
    b_const = b.x0 - b.v * b.t0
    return (b_const - a_const) / denom


def intersection_event(a: WorldLine, b: WorldLine, label: str = "interaction") -> Optional[Event]:
    t = intersection_time(a, b)
    if t is None:
        return None
    x = a.position_at(t)
    return Event(t=t, x=x, label=label)


def light_vs_rest_interaction(
    light_start: Event,
    rest_x: float,
    light_direction: int = 1,
    c: float = 1.0,
) -> Optional[Event]:
    """Interaction of a light-speed object with an object at rest.

    Returns the meeting event if it occurs at t >= light_start.t, else None.
    """

    light = null_line_through(light_start, direction=light_direction, c=c, label="photon")
    rest = WorldLine(x0=rest_x, v=0.0, t0=light_start.t, label="rest-object")

    meet = intersection_event(light, rest, label="light-rest interaction")
    if meet is None:
        return None
    if meet.t < light_start.t:
        return None
    return meet


def spontaneous_events(
    worldline: WorldLine,
    t_start: float,
    t_end: float,
    dt: float,
    probability_per_step: float,
    rng: Optional[random.Random] = None,
    label_prefix: str = "spontaneous",
) -> List[Event]:
    """Generate random spontaneous events along a world line."""

    if dt <= 0:
        raise ValueError("dt must be > 0")
    if not (0.0 <= probability_per_step <= 1.0):
        raise ValueError("probability_per_step must be in [0, 1]")

    rng = rng or random.Random()
    out: List[Event] = []
    idx = 0
    t = t_start
    while t <= t_end + 1e-12:
        if rng.random() < probability_per_step:
            out.append(worldline.event_at(t, label=f"{label_prefix}-{idx}"))
            idx += 1
        t += dt
    return out


def conditional_simulation(
    worldlines: Iterable[WorldLine],
    t_start: float,
    t_end: float,
    dt: float,
    predicate: Callable[[float, List[Event]], bool],
    label: str = "conditional",
) -> List[Event]:
    """Sample world lines through time and emit events when a predicate is true.

    predicate signature: predicate(t, sampled_events_at_t) -> bool
    """

    if dt <= 0:
        raise ValueError("dt must be > 0")

    lines = list(worldlines)
    out: List[Event] = []
    t = t_start
    while t <= t_end + 1e-12:
        sample = [w.event_at(t, label=w.label) for w in lines]
        if predicate(t, sample):
            centroid_x = sum(e.x for e in sample) / max(1, len(sample))
            out.append(Event(t=t, x=centroid_x, label=label))
        t += dt
    return out


def demo() -> None:
    """Run a minimal demonstration."""

    c = 1.0
    a = Event(t=0.0, x=0.0, label="A")
    b = Event(t=2.0, x=1.0, label="B")
    print(f"Interval A->B: {classify_interval(a, b, c=c).value}")

    photon_hit = light_vs_rest_interaction(light_start=Event(0.0, 0.0), rest_x=5.0, light_direction=1, c=c)
    print("Photon/rest interaction:", photon_hit)

    ship = WorldLine(x0=0.0, v=0.4, label="ship")
    bursts = spontaneous_events(ship, 0.0, 10.0, dt=0.5, probability_per_step=0.2, rng=random.Random(42))
    print(f"Spontaneous events on ship world line: {len(bursts)}")

    chaser = WorldLine(x0=-3.0, v=0.8, label="chaser")
    target = WorldLine(x0=3.0, v=0.0, label="target")
    near_events = conditional_simulation(
        [chaser, target],
        t_start=0.0,
        t_end=10.0,
        dt=0.1,
        predicate=lambda _t, evs: abs(evs[0].x - evs[1].x) < 0.5,
        label="close-approach",
    )
    print(f"Conditional close-approach samples: {len(near_events)}")


if __name__ == "__main__":
    demo()
