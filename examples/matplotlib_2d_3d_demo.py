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

import matplotlib.pyplot as plt
from matplotlib.widgets import Button

from py_matlab_style_plotter import CoordinateReadout, MatplotlibAxesPlotter, MatplotlibEventBridge


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


def main() -> None:
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
    plotter.push_current_view(ax2d)
    plotter.set_active_axes(ax3d)
    plotter.push_current_view(ax3d)
    plotter.set_active_axes(ax2d)

    fig.subplots_adjust(bottom=0.28)
    buttons = {
        "None": fig.add_axes((0.04, 0.16, 0.09, 0.055)),
        "Pan": fig.add_axes((0.15, 0.16, 0.09, 0.055)),
        "Zoom": fig.add_axes((0.26, 0.16, 0.09, 0.055)),
        "Rotate3D": fig.add_axes((0.37, 0.16, 0.12, 0.055)),
        "Cursor": fig.add_axes((0.51, 0.16, 0.09, 0.055)),
        "Select": fig.add_axes((0.62, 0.16, 0.09, 0.055)),
        "Brush": fig.add_axes((0.73, 0.16, 0.09, 0.055)),
        "Home": fig.add_axes((0.20, 0.075, 0.10, 0.055)),
        "Back": fig.add_axes((0.32, 0.075, 0.10, 0.055)),
        "Forward": fig.add_axes((0.44, 0.075, 0.11, 0.055)),
        "Auto": fig.add_axes((0.57, 0.075, 0.10, 0.055)),
        "Tight": fig.add_axes((0.69, 0.075, 0.10, 0.055)),
        "Hold": fig.add_axes((0.81, 0.075, 0.10, 0.055)),
    }
    widgets = {label: Button(button_axes, label) for label, button_axes in buttons.items()}

    widgets["None"].on_clicked(lambda _event: bridge.set_mode("none"))
    widgets["Pan"].on_clicked(lambda _event: bridge.toggle_mode("pan"))
    widgets["Zoom"].on_clicked(lambda _event: bridge.toggle_mode("zoom"))
    widgets["Rotate3D"].on_clicked(lambda _event: bridge.toggle_mode("rotate3d"))
    widgets["Cursor"].on_clicked(lambda _event: bridge.toggle_mode("data_cursor"))
    widgets["Select"].on_clicked(lambda _event: bridge.toggle_mode("select"))
    widgets["Brush"].on_clicked(lambda _event: bridge.toggle_mode("brush"))
    widgets["Home"].on_clicked(lambda _event: plotter.home())
    widgets["Back"].on_clicked(lambda _event: plotter.back())
    widgets["Forward"].on_clicked(lambda _event: plotter.forward())
    widgets["Auto"].on_clicked(lambda _event: plotter.axis("auto"))
    widgets["Tight"].on_clicked(lambda _event: plotter.axis("tight"))
    widgets["Hold"].on_clicked(lambda _event: plotter.hold("toggle"))

    fig.canvas.manager.set_window_title("pyMatlabStylePlotter demo")
    plt.show()


if __name__ == "__main__":
    main()
