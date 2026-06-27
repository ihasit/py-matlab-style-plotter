"""Small Matplotlib demo for MATLAB-like axes interaction.

Run with:

    PYTHONPATH=src python examples/matplotlib_2d_3d_demo.py

Controls:

- tool buttons toggle exclusive interaction modes
- wheel zooms the axes under the pointer
- zoom mode: click to zoom or left-drag a 2D axes to box-zoom
- pan mode: left-drag a 2D axes, hold Shift to constrain to one direction
- rotate3d mode: left-drag a 3D axes with low MATLAB-like sensitivity
- select mode: click the nearest line, Shift/Ctrl for multi-select
- brush mode: drag a rectangle to highlight lines with points inside it
- mode shortcuts: n none; p, z, r, d, s, B toggle pan, zoom, rotate3d, data cursor, select, brush
- h: home, left/right arrows: view back/forward, a/M/t/e/f/i/m/q/w/O/U/j/k: axis auto/manual/tight/equal/fill/image/normal/square/vis3d/off/on/ij/xy, 2: view(2), 3: view(3), o: hold toggle, v: selected visibility, g: grid, l: legend, x/y/b: link axes, escape: mode none
"""

from __future__ import annotations

import math
from contextlib import contextmanager
from types import MethodType

import matplotlib.pyplot as plt

from py_matlab_style_plotter import CoordinateReadout, MatplotlibAxesPlotter, MatplotlibEventBridge


_MATLAB_TOOLITEMS = (
    (None, None, None, None),
    ("None", "Clear MATLAB-like interaction mode", "hand", "matlab_none"),
    ("Pan", "MATLAB-like pan mode", "move", "matlab_pan"),
    ("Zoom", "MATLAB-like zoom mode", "zoom_to_rect", "matlab_zoom"),
    ("Rotate3D", "MATLAB-like rotate3d mode", "move", "matlab_rotate3d"),
    ("Cursor", "MATLAB-like data cursor mode", "help", "matlab_data_cursor"),
    ("Select", "MATLAB-like select mode", "hand", "matlab_select"),
    ("Brush", "MATLAB-like brush mode", "zoom_to_rect", "matlab_brush"),
    (None, None, None, None),
    ("Auto", "axis auto", "subplots", "matlab_axis_auto"),
    ("Tight", "axis tight", "subplots", "matlab_axis_tight"),
    ("Hold", "Toggle hold", "filesave", "matlab_hold"),
)
_MATLAB_TOOL_METHODS = tuple(item[3] for item in _MATLAB_TOOLITEMS if item[3] is not None)
_MISSING = object()


@contextmanager
def matlab_style_toolbar():
    toolbar_class = _current_toolbar_class()
    if toolbar_class is None or getattr(toolbar_class, "_py_matlab_style_extended", False):
        yield
        return

    original = toolbar_class.toolitems
    original_methods = {name: getattr(toolbar_class, name, _MISSING) for name in _MATLAB_TOOL_METHODS}
    toolbar_class.toolitems = original + _MATLAB_TOOLITEMS
    for method_name in _MATLAB_TOOL_METHODS:
        setattr(toolbar_class, method_name, _make_toolbar_method(method_name))
    toolbar_class._py_matlab_style_extended = True
    try:
        yield
    finally:
        toolbar_class.toolitems = original
        for method_name, method in original_methods.items():
            if method is _MISSING:
                delattr(toolbar_class, method_name)
            else:
                setattr(toolbar_class, method_name, method)
        toolbar_class._py_matlab_style_extended = False


def _make_toolbar_method(method_name):
    def toolbar_method(self, *args):
        action = getattr(getattr(self, "_actions", None), method_name, None)
        if action is not None:
            action(*args)

    return toolbar_method


def _current_toolbar_class():
    get_backend_mod = getattr(plt, "_get_backend_mod", None)
    if get_backend_mod is None:
        return None
    manager_class = getattr(get_backend_mod(), "FigureManager", None)
    return getattr(manager_class, "_toolbar2_class", None)


class DemoPlotter(MatplotlibAxesPlotter):
    def __init__(self, axes, status_text):
        super().__init__(axes)
        self.status_text = status_text
        self._last_readout = ""
        self._refresh_status()

    def on_coordinate_readout_changed(self, readout: CoordinateReadout | None) -> None:
        self._last_readout = readout.text if readout is not None else ""
        self._refresh_status()
        axes = self.active_axes or self.axes
        if axes is not None:
            self._draw_idle(axes)

    def on_mode_changed(self, mode):
        self._refresh_status()

    def hold(self, value=None):
        enabled = super().hold(value)
        self._refresh_status()
        axes = self.active_axes or self.axes
        if axes is not None:
            self._draw_idle(axes)
        return enabled

    def _refresh_status(self):
        hold_text = "on" if self.hold_enabled else "off"
        parts = [f"Mode: {self.mode.value}", f"Hold: {hold_text}"]
        if self._last_readout:
            parts.append(self._last_readout)
        self.status_text.set_text(" | ".join(parts))


class MatlabToolbarActions:
    def __init__(self, bridge: MatplotlibEventBridge, plotter: DemoPlotter) -> None:
        self.bridge = bridge
        self.plotter = plotter

    def matlab_none(self, *_args) -> None:
        self.bridge.set_mode("none")

    def matlab_pan(self, *_args) -> None:
        self.bridge.toggle_mode("pan")

    def matlab_zoom(self, *_args) -> None:
        self.bridge.toggle_mode("zoom")

    def matlab_rotate3d(self, *_args) -> None:
        self.bridge.toggle_mode("rotate3d")

    def matlab_data_cursor(self, *_args) -> None:
        self.bridge.toggle_mode("data_cursor")

    def matlab_select(self, *_args) -> None:
        self.bridge.toggle_mode("select")

    def matlab_brush(self, *_args) -> None:
        self.bridge.toggle_mode("brush")

    def matlab_axis_auto(self, *_args) -> None:
        self.plotter.axis("auto")

    def matlab_axis_tight(self, *_args) -> None:
        self.plotter.axis("tight")

    def matlab_hold(self, *_args) -> None:
        self.plotter.hold("toggle")


def main() -> None:
    with matlab_style_toolbar():
        fig = plt.figure(figsize=(10, 5))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")

    xs = [i * 0.05 for i in range(240)]
    ax2d.plot(xs, [math.sin(x) for x in xs], label="sin")
    ax2d.plot(xs, [math.cos(x) for x in xs], label="cos")
    ax2d.set_title("2D axes")
    ax2d.grid(True)
    ax2d.legend(loc="upper right")

    theta = [i * 0.08 for i in range(180)]
    z = [i / 40 for i in range(180)]
    r = [1 + 0.15 * math.sin(4 * t) for t in theta]
    ax3d.plot([rr * math.cos(t) for rr, t in zip(r, theta)], [rr * math.sin(t) for rr, t in zip(r, theta)], z)
    ax3d.set_title("3D axes")
    ax3d.view_init(elev=30, azim=-37.5)

    status_text = fig.text(0.08, 0.015, "", ha="left", va="center", fontsize=9)
    plotter = DemoPlotter(ax2d, status_text)
    bridge = MatplotlibEventBridge(plotter, fig.canvas)
    bridge.connect()
    toolbar = getattr(getattr(fig.canvas, "manager", None), "toolbar", None)
    if toolbar is not None:
        toolbar._actions = MatlabToolbarActions(bridge, plotter)
        for method_name in _MATLAB_TOOL_METHODS:
            setattr(toolbar, method_name, MethodType(_make_toolbar_method(method_name), toolbar))
    plotter.push_current_view(ax2d)
    plotter.set_active_axes(ax3d)
    plotter.push_current_view(ax3d)
    plotter.set_active_axes(ax2d)

    fig.canvas.manager.set_window_title("pyMatlabStylePlotter demo")
    plt.show()


if __name__ == "__main__":
    main()
