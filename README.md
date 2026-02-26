# Minkowski Spacetime Simulator

A compact 1+1D Minkowski spacetime simulator in Python.

## What it models

- **Events** (`t, x` points in spacetime)
- **World lines** for inertial objects (`x(t) = x0 + v(t-t0)`)
- **Interval type** between events:
  - timelike
  - spacelike
  - null (lightlike)
- **Null lines** (light trajectories at speed `c`)
- **Conditional simulations** (run custom logic at every timestep)
- **Spontaneous events** (random events along a world line)

## Quick start

```bash
python minkowski_simulator.py
```

## Usage examples

```python
from minkowski_simulator import (
    Event,
    WorldLine,
    classify_interval,
    light_vs_rest_interaction,
    spontaneous_events,
    conditional_simulation,
)

# 1) Interval classification
print(classify_interval(Event(0, 0), Event(3, 3)).value)  # null

# 2) Light-speed object vs object at rest
meet = light_vs_rest_interaction(
    light_start=Event(t=0, x=0),
    rest_x=5,
    light_direction=1,
    c=1.0,
)
print(meet)  # Event(t=5, x=5, ...)

# 3) Spontaneous events on a world line
ship = WorldLine(x0=0.0, v=0.4, label="ship")
blips = spontaneous_events(
    ship,
    t_start=0,
    t_end=10,
    dt=0.5,
    probability_per_step=0.2,
)

# 4) Conditional simulation (emit event when two objects are close)
a = WorldLine(x0=-1, v=1, label="a")
b = WorldLine(x0=1, v=-1, label="b")
close = conditional_simulation(
    [a, b],
    t_start=0,
    t_end=2,
    dt=0.1,
    predicate=lambda t, evs: abs(evs[0].x - evs[1].x) < 0.2,
)
```

## Test

```bash
python -m pytest -q
```

## HTML simulator

Open the interactive simulator in your browser:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000/index.html`.

Features in the HTML view:
- add events and world lines
- visualize null (lightlike) lines (`|v| = c`)
- classify intervals as timelike/spacelike/null
- run light-vs-rest interaction simulation
- generate spontaneous and conditional events

