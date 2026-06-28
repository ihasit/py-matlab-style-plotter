# Usage Guide

This guide shows how to use `pyMatlabStylePlotter` with Matplotlib and how the
MATLAB-like interaction model is intended to work.

## 1. Install

From the repository root:

```bash
python -m pip install -e .
```

For development and tests:

```bash
python -m pip install -e ".[test]"
```

For local commands without installation, set `PYTHONPATH=src`.

## 2. Versioning and External Projects

The release version is managed in `pyproject.toml`:

```toml
version = "0.1.3"
```

Use semantic versioning:

- `PATCH`: compatible bug fixes, performance fixes, and documentation updates
- `MINOR`: compatible public API additions
- `MAJOR`: incompatible public API or behavior changes

Recommended release flow:

```bash
python -m unittest discover -s tests
git commit -m "Release v0.1.3"
git tag -a v0.1.3 -m "Release v0.1.3"
git push origin main
git push origin v0.1.3
```

On GitHub, pushing a `v*` tag triggers `.github/workflows/release.yml`. The
workflow:

- installs the build tools
- runs the unit tests
- builds both `sdist` and wheel artifacts with `python -m build`
- creates or updates the GitHub Release
- uploads `dist/*` as release assets

The generated wheel is universal for this pure-Python package, for example
`py_matlab_style_plotter-0.1.3-py3-none-any.whl`.

Do not commit generated package artifacts. `.gitignore` excludes `dist/`,
`build/`, `*.egg-info/`, and `*.whl`; GitHub Actions should recreate them for
each release tag.

For another local project, use editable install while developing:

```bash
python -m pip install -e /Users/ltk/Codes/tools/pyMatlabStylePlotter
```

For reproducible project dependencies, pin a Git tag:

```toml
[project]
dependencies = [
    "py-matlab-style-plotter @ git+file:///Users/ltk/Codes/tools/pyMatlabStylePlotter@v0.1.3",
]
```

If the repository is moved to an internal Git server, use the same tag pinning
pattern with a `git+ssh://` or `git+https://` URL.

## 3. Minimal Matplotlib Integration

```python
import matplotlib.pyplot as plt

from py_matlab_style_plotter import (
    MatplotlibAxesPlotter,
    MatplotlibContextMenu,
    MatplotlibContextMenuEventBridge,
)

fig, ax = plt.subplots()

plotter = MatplotlibAxesPlotter(ax)
context_menu = MatplotlibContextMenu(fig, plotter)
bridge = MatplotlibContextMenuEventBridge(plotter, fig.canvas, context_menu)
bridge.connect()

plotter.plot([0, 1, 2, 3], [0, 1, 0, 1], "o-", DisplayName="signal")
plotter.grid("on")
plotter.legend("on")

plt.show()
```

`MatplotlibAxesPlotter` owns the MATLAB-like axes behavior.  
`MatplotlibContextMenu` draws the MATLAB-style right-click menu.  
`MatplotlibContextMenuEventBridge` translates Matplotlib events into the
backend-neutral interaction state machine and routes right-clicks to the menu.

## 4. Plotting Commands

The plotter accepts common MATLAB-like calling forms:

```python
plotter.plot([1, 2, 3, 4])
plotter.plot([0, 1, 2, 3], [1, 3, 2, 4])
plotter.plot([0, 1, 2], [0, 1, 0], "r--o", LineWidth=2, DisplayName="demo")
```

For large data, prefer passing multiple lines as a matrix in one call:

```python
# y_matrix has shape (point_count, line_count)
plotter.plot(x, y_matrix)
```

This batches color-order handling, autoscale, view-history updates, and redraw
requests. Repeated single-line calls are supported, but they intentionally run
the MATLAB-like plot lifecycle for each call and are slower for million-point
datasets.

Supported command families include:

- Lines: `plot`, `plot3`, `line`, `stairs`, `errorbar`
- Markers and bars: `scatter`, `scatter3`, `stem`, `stem3`, `bar`, `barh`
- Filled and image data: `area`, `fill`, `histogram`, `imagesc`, `pcolor`
- Contours and surfaces: `contour`, `contourf`, `contour3`, `surf`, `mesh`,
  `waterfall`, `ribbon`
- Vector/polar/other helpers: `quiver`, `polarplot`, `polarhistogram`, `pie`,
  `pareto`, `heatmap`, `spy`, `annotation`

MATLAB-style Name/Value properties are normalized where practical. For
example, `DisplayName` maps to Matplotlib's `label`.

## 5. Axes State

Common MATLAB-like axes helpers:

```python
plotter.hold("on")
plotter.grid("on")
plotter.grid("minor")
plotter.box("on")
plotter.legend("toggle")
plotter.colorbar("on")

plotter.axis("tight")
plotter.axis("equal")
plotter.axis("normal")
plotter.xlim([0, 10])
plotter.ylim("auto")
plotter.clim([0, 1])
```

The plotter tracks UI state per axes, including:

- limit modes: `auto` / `manual`
- aspect and box aspect
- axis visibility and directions
- scales, ticks, tick labels, grid state, font/color state
- active axes and view history

## 6. View History

The view history is scoped to axes. It supports MATLAB-like home/back/forward:

```python
plotter.push_current_view()
plotter.home()
plotter.back()
plotter.forward()

plotter.can_home()
plotter.can_back()
plotter.can_forward()
```

For 3D axes, view history includes camera state and z limits.

## 7. Interaction Modes

Use the tool helpers directly:

```python
plotter.pan("on")
plotter.zoom("toggle")
plotter.rotate3d("off")
plotter.datacursormode("on")
plotter.selectmode("on")
plotter.brush("on")
```

When a non-`none` mode is active, the Matplotlib adapter shows a small mode
label in the active axes. Disable it if your application provides its own
status indicator:

```python
plotter.mode_label_enabled = False
```

Or use the event bridge keyboard shortcuts in the demo:

| Key | Action |
| --- | --- |
| `n` | none mode |
| `p` | pan |
| `z` | zoom |
| `r` | rotate3d |
| `d` | data cursor |
| `s` | select |
| `B` | brush |
| `h` | home |
| left/right arrow | back/forward |
| delete/backspace | delete selected object, or clear data tips if nothing is selected |
| `v` | toggle selected visibility |
| `g` | grid toggle |
| `l` | legend toggle |
| `x`, `y`, `b` | link x, y, or x/y axes |

Axis shortcuts in the demo:

| Key | Command |
| --- | --- |
| `a` | `axis auto` |
| `M` | `axis manual` |
| `t` | `axis tight` |
| `e` | `axis equal` |
| `f` | `axis fill` |
| `i` | `axis image` |
| `m` | `axis normal` |
| `q` | `axis square` |
| `w` | `axis vis3d` |
| `O` | `axis off` |
| `U` | `axis on` |
| `j` | `axis ij` |
| `k` | `axis xy` |
| `2` | `view(2)` |
| `3` | `view(3)` |

## 8. Large Data Benchmark

Run the included benchmark:

```bash
env MPLCONFIGDIR=/private/tmp/pyMatlabStylePlotter-mpl \
  python benchmarks/plot_large_lines.py --repeats 1
```

Default data size: 8 lines, 1,024,000 points per line. Current reference result
on the development machine with Matplotlib 3.11.0 and the Agg backend:

| Case | Create | First draw | Pan redraw |
| --- | ---: | ---: | ---: |
| raw Matplotlib | 0.121 s | 0.215 s | 0.164 s |
| matrix plotter call | 0.377 s | 0.187 s | 0.168 s |
| repeated plotter calls | 1.269 s | 0.188 s | 0.167 s |

## 9. Right-Click Context Menu

The library includes a figure-level context menu rather than Matplotlib button
widgets, so opening the menu does not create extra axes.

```python
context_menu = MatplotlibContextMenu(fig, plotter)
bridge = MatplotlibContextMenuEventBridge(plotter, fig.canvas, context_menu)
bridge.connect()
```

The menu includes:

- modes: None, Pan, Zoom, Rotate3D, Cursor, Select, Brush
- marker, line style, and color submenus
- view controls: Home, Back, Forward, View 2-D, View 3-D
- axis controls: Auto, Manual, Tight, Equal, Fill, Image, Normal, Square,
  Vis3D, On/Off, IJ/XY
- display controls: Hold, Grid, Legend, Box, Colorbar
- link axes: Link X, Link Y, Link X/Y
- selection: Hide Selected, Clear Selection, Delete

The current interaction mode is marked with a check in the mode section.

Marker, line, and color commands require selected lines. When no line is
selected, those menu entries are disabled.

## 10. Data Cursor, Select, and Brush

### Data Cursor

Data cursor mode creates a fixed data tip at the nearest line point within
pick tolerance. Data tips include Z values for 3D lines.

Each data tip has a visible marker. In Select mode, clicking that marker
selects the data tip. Press Delete to remove only that data tip.

### Select

Select mode clicks the nearest line or data cursor marker:

- clicking a line selects and highlights the whole line
- Shift/Ctrl/Cmd adds to selection or toggles an existing selection
- clicking empty space clears selection unless a multi-select modifier is held
- Delete removes selected lines or selected data tips

Selected lines receive a visible overlay highlight. The overlay is internal
and is excluded from picking, brushing, and legends.

### Brush

Brush mode drag-selects data points in a rectangular region:

- brushed points are highlighted with marker overlays
- the whole line is not selected or highlighted
- Shift/Ctrl/Cmd additive brushing keeps existing brushed points
- non-additive brushing clears previous brush/selection state first

This matches MATLAB's brush behavior more closely than treating brush as line
selection.

## 11. 3D Behavior

The default 3D interaction is intentionally separated by mode:

- `rotate3d` mode rotates the 3D camera
- brush/select/cursor do not rotate the 3D axes
- Matplotlib's native 3D mouse rotation is disabled when a 3D axes becomes
  active, so only this library's interaction mode handles rotation

3D pan and zoom default to camera operations:

```python
plotter.pan_3d_mode = "camera"   # default
plotter.zoom_3d_mode = "camera"  # default
```

Set either to `"limits"` to use x/y limit changes instead.

Useful 3D camera helpers:

```python
plotter.view(2)
plotter.view(3)
plotter.view([45, 30])
plotter.camzoom(1.2)
plotter.camorbit(10, -5)
plotter.camroll(15)
plotter.camdolly(0.1, 0.0, 0.0)
plotter.camproj("orthographic")
```

## 12. Linked Axes

Link axes in a figure:

```python
axes = [ax1, ax2]
plotter.linkaxes(axes, "x")
plotter.linkaxes(axes, "y")
plotter.linkaxes(axes, "xy")
plotter.linkaxes(axes, "off")
```

The initial linked view uses the union of existing limits. Later pan, zoom,
and explicit limit commands synchronize linked axes.

## 13. Running Tests

Recommended local verification:

```bash
env MPLCONFIGDIR=/private/tmp/pyMatlabStylePlotter-mpl \
  python -m unittest \
  tests.test_matplotlib_adapter \
  tests.test_matplotlib_bridge \
  tests.test_matplotlib_context_menu \
  tests.test_interaction \
  tests.test_matplotlib_3d_overlay
```

Syntax check:

```bash
python -m py_compile \
  src/py_matlab_style_plotter/__init__.py \
  src/py_matlab_style_plotter/interaction.py \
  src/py_matlab_style_plotter/matplotlib_adapter.py \
  src/py_matlab_style_plotter/matplotlib_bridge.py \
  examples/matplotlib_2d_3d_demo.py
```

## 14. Notes for Integrators

- The base state machine is in `interaction.py` and does not require
  Matplotlib.
- Backend adapters should implement drawing, limit, camera, and UI hooks.
- For Matplotlib apps, use `MatplotlibAxesPlotter` plus
  `MatplotlibContextMenuEventBridge` when you want the built-in right-click
  menu, or `MatplotlibEventBridge` when your app owns all UI.
- If your app has its own toolbar, query `pan_state()`, `zoom_state()`, and
  `rotate3d_state()` for active state and tool properties.
- Use `button_down_filter`, `action_pre_callback`, and `action_post_callback`
  to integrate with custom GUI event lifecycles.
