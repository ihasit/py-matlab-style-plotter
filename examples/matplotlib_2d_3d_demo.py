"""Small Matplotlib demo for MATLAB-like axes interaction.

Run with:

    PYTHONPATH=src python examples/matplotlib_2d_3d_demo.py

Controls:

- right-click an axes to open the MATLAB-like context menu
- wheel zooms the axes under the pointer
- zoom mode: click to zoom or left-drag a 2D axes to box-zoom
- pan mode: left-drag a 2D axes, hold Shift to constrain to one direction
- rotate3d mode: left-drag a 3D axes with low MATLAB-like sensitivity
- select mode: click the nearest line, Shift/Ctrl for multi-select
- brush mode: drag a rectangle to highlight lines with points inside it
- mode shortcuts: n none; p, z, r, d, s, B toggle pan, zoom, rotate3d, data cursor, select, brush
- h: home, left/right arrows: view back/forward, a/M/t/e/f/i/m/q/w/O/U/j/k: axis auto/manual/tight/equal/fill/image/normal/square/vis3d/off/on/ij/xy, 2: view(2), 3: view(3), o: hold toggle, v: selected visibility, g: grid, l: legend, x/y/b: link axes, delete: delete selection, escape: mode none
"""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
from py_matlab_style_plotter import (
    CoordinateReadout,
    MatplotlibAxesPlotter,
    MatplotlibContextMenu,
    MatplotlibContextMenuEventBridge,
)


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
    fig = plt.figure(figsize=(10, 5.4))
    ax2d = fig.add_subplot(1, 2, 1)
    ax3d = fig.add_subplot(1, 2, 2, projection="3d")

    xs = [i * 0.05 for i in range(240)]
    ax2d.plot(xs, [math.sin(x) for x in xs], label="sin", marker="o", markevery=16)
    ax2d.plot(xs, [math.cos(x) for x in xs], label="cos", marker="s", markevery=16)
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
    context_menu = MatplotlibContextMenu(fig, plotter)
    bridge = MatplotlibContextMenuEventBridge(plotter, fig.canvas, context_menu)
    bridge.connect()
    fig._py_matlab_style_context_menu = context_menu
    plotter.push_current_view(ax2d)
    plotter.set_active_axes(ax3d)
    plotter.push_current_view(ax3d)
    plotter.set_active_axes(ax2d)

    fig.canvas.manager.set_window_title("pyMatlabStylePlotter demo")
    plt.show()


if __name__ == "__main__":
    main()
