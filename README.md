# pyMatlabStylePlotter

`pyMatlabStylePlotter` provides MATLAB-like plotting commands and axes
interaction helpers for Python applications. The core interaction state is
backend-neutral, and the included adapter wires it to Matplotlib axes.

The project is useful when you want Matplotlib figures to behave closer to
MATLAB figures: active axes, `hold`, `axis`, view history, pan/zoom/rotate
tools, data cursor, selection, brushing, linked axes, and MATLAB-like plotting
argument forms.

## Features

- MATLAB-style plotting helpers: `plot`, `plot3`, `scatter`, `scatter3`,
  `stem`, `bar`, `area`, `fill`, `histogram`, `errorbar`, `imagesc`,
  `contour`, `contourf`, `surf`, `mesh`, `quiver`, `pcolor`, `subplot`, and
  more.
- MATLAB-style axes commands: `hold`, `grid`, `box`, `legend`, `colorbar`,
  `axis`, `xlim`, `ylim`, `zlim`, `clim`/`caxis`, `view`, `daspect`,
  `pbaspect`, ticks, tick labels, labels, title, and font/color properties.
- Exploration tools: `pan`, `zoom`, `rotate3d`, `datacursormode`,
  `selectmode`, and `brush`.
- Active axes state, per-axes UI state, home/back/forward view history, and
  linked axes.
- Matplotlib event bridge with MATLAB-like mouse and keyboard interaction.
- Demo with 2D/3D axes, MATLAB-style right-click context menu, data cursor
  markers, brushing, selection highlighting, and linked axes controls.

## Installation

From this repository:

```bash
python -m pip install -e ".[matplotlib,test]"
```

For runtime use with Matplotlib only:

```bash
python -m pip install -e ".[matplotlib]"
```

The package itself has no mandatory runtime dependency. Matplotlib support is
an optional extra.

## Quick Start

```python
import matplotlib.pyplot as plt

from py_matlab_style_plotter import MatplotlibAxesPlotter, MatplotlibEventBridge

fig, ax = plt.subplots()
plotter = MatplotlibAxesPlotter(ax)
bridge = MatplotlibEventBridge(plotter, fig.canvas)
bridge.connect()

plotter.plot([0, 1, 2, 3], [0, 1, 0, 1], "o-", DisplayName="demo")
plotter.grid("on")
plotter.legend("on")
plotter.hold("on")

plt.show()
```

## Demo

Run the included Matplotlib demo:

```bash
PYTHONPATH=src python examples/matplotlib_2d_3d_demo.py
```

The demo includes:

- a 2D axes and a 3D axes
- MATLAB-like right-click context menu
- pan, zoom, rotate3d, cursor, select, and brush modes
- data cursor markers that can be selected and deleted
- brush highlights for selected points only
- selected line highlighting
- home/back/forward view history
- keyboard shortcuts and linked axes controls

See [docs/USAGE.md](docs/USAGE.md) for the full usage guide and shortcut list.

## Basic Controls

In the demo:

- Right-click an axes to open the MATLAB-style context menu.
- Mouse wheel zooms the axes under the pointer.
- Double-click an axes to restore its home view.
- `p`, `z`, `r`, `d`, `s`, and `B` toggle pan, zoom, rotate3d, data cursor,
  select, and brush.
- `n` returns to none mode.
- `h` restores home; left/right arrows navigate view history.
- Delete removes selected lines or selected data cursor markers. If nothing is
  selected, Delete clears data tips.

## Development

Run the focused test suite used during development:

```bash
env MPLCONFIGDIR=/private/tmp/pyMatlabStylePlotter-mpl \
  python -m unittest \
  tests.test_matplotlib_adapter \
  tests.test_matplotlib_bridge \
  tests.test_interaction \
  tests.test_matplotlib_3d_overlay
```

Run syntax checks:

```bash
python -m py_compile \
  src/py_matlab_style_plotter/__init__.py \
  src/py_matlab_style_plotter/interaction.py \
  src/py_matlab_style_plotter/matplotlib_adapter.py \
  src/py_matlab_style_plotter/matplotlib_bridge.py \
  examples/matplotlib_2d_3d_demo.py
```

## Benchmark

Run the large-line benchmark:

```bash
env MPLCONFIGDIR=/private/tmp/pyMatlabStylePlotter-mpl \
  python benchmarks/plot_large_lines.py --repeats 1
```

The default benchmark draws 8 lines with 1,024,000 points each. On the
development machine with Matplotlib 3.11.0 and the Agg backend:

| Case | Create | First draw | Pan redraw |
| --- | ---: | ---: | ---: |
| raw Matplotlib | 0.121 s | 0.215 s | 0.164 s |
| `plotter.plot(x, y_matrix)` | 0.377 s | 0.187 s | 0.168 s |
| 8 separate `plotter.plot(x, y)` calls | 1.269 s | 0.188 s | 0.167 s |

For large datasets, prefer one matrix plot call, for example
`plotter.plot(x, y.T)`, instead of repeated single-line calls. This keeps
Matplotlib redraw and autoscale work batched.

## Project Layout

```text
src/py_matlab_style_plotter/
  interaction.py          Backend-neutral MATLAB-like state machine
  matplotlib_adapter.py   Matplotlib axes implementation
  matplotlib_bridge.py    Matplotlib event bridge

examples/
  matplotlib_2d_3d_demo.py

benchmarks/
  plot_large_lines.py

tests/
  test_interaction.py
  test_matplotlib_adapter.py
  test_matplotlib_bridge.py
```

## Status

This is an early-stage plotting and interaction library. The public surface is
designed around MATLAB-like semantics, but some commands are still intentionally
pragmatic Matplotlib mappings rather than exact MATLAB clones.
