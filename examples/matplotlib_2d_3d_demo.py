"""Matplotlib gallery demo for MATLAB-like plotting and interaction.

Run with:

    python examples/matplotlib_2d_3d_demo.py

Controls:

- right-click an axes to open the MATLAB-like context menu
- wheel zooms the axes under the pointer
- zoom mode: left-drag a 2D axes to box-zoom
- pan mode: left-drag a 2D axes, hold Shift to constrain to one direction
- rotate3d mode: left-drag a 3D axes with low MATLAB-like sensitivity
- cursor mode: click a line or scatter point; Ctrl-click creates another label
- select mode: click the nearest line, Shift/Ctrl for multi-select
- brush mode: drag a rectangle to highlight line markers inside it
- shortcuts: n none; p/z/r/d/s/B pan/zoom/rotate3d/cursor/select/brush
- h home, left/right view history, 2/3 view presets, g grid, l legend
"""

from __future__ import annotations

import os
import math
import sys
import tempfile
from pathlib import Path

import matplotlib

_REPO_SRC = Path(__file__).resolve().parents[1] / "src"
if _REPO_SRC.exists() and str(_REPO_SRC) not in sys.path:
    sys.path.insert(0, str(_REPO_SRC))


def _prefer_gui_backend() -> None:
    if os.environ.get("MPLBACKEND"):
        return
    for backend in ("QtAgg", "TkAgg", "MacOSX"):
        try:
            matplotlib.use(backend, force=True)
            return
        except Exception:
            continue


_prefer_gui_backend()

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


class DemoContextMenu(MatplotlibContextMenu):
    def __init__(self, fig, plotter: DemoPlotter):
        super().__init__(fig, plotter)
        self._demo_plotter = plotter

    def _on_press(self, event) -> bool:
        handled = super()._on_press(event)
        error = self.actions.last_export_error
        path = self.actions.last_export_path
        if error:
            self._demo_plotter._last_readout = f"Export: {error}"
            self._demo_plotter._refresh_status()
            self.fig.canvas.draw_idle()
        elif path is not None:
            self._demo_plotter._last_readout = f"Exported: {path}"
            self._demo_plotter._refresh_status()
            self.fig.canvas.draw_idle()
        return handled


def _wave_data(count: int = 180):
    xs = [i * 0.055 for i in range(count)]
    sin_y = [math.sin(x) for x in xs]
    cos_y = [0.75 * math.cos(x * 0.8) for x in xs]
    envelope = [0.35 + 0.04 * math.sin(x * 2.0) for x in xs]
    return xs, sin_y, cos_y, envelope


def _surface_data(size: int = 34):
    values = [3.2 * (2 * i / (size - 1) - 1) for i in range(size)]
    x_grid = []
    y_grid = []
    z_grid = []
    for y in values:
        x_row = []
        y_row = []
        z_row = []
        for x in values:
            radius = (x * x + y * y) ** 0.5 + 1.0e-9
            z = math.sin(radius * 2.6) / (1.0 + 0.22 * radius)
            x_row.append(x)
            y_row.append(y)
            z_row.append(z)
        x_grid.append(x_row)
        y_grid.append(y_row)
        z_grid.append(z_row)
    return x_grid, y_grid, z_grid


def _heat_data(rows: int = 34, cols: int = 42):
    data = []
    for row in range(rows):
        y = 2.4 * (2 * row / (rows - 1) - 1)
        values = []
        for col in range(cols):
            x = 3.0 * (2 * col / (cols - 1) - 1)
            values.append(math.sin(x * 2.2) * math.cos(y * 2.7) + 0.35 * math.sin((x + y) * 1.4))
        data.append(values)
    return data


def _sparse_pattern(size: int = 38):
    matrix = []
    for row in range(size):
        values = []
        for col in range(size):
            value = 1 if row == col or (row + col) % 11 == 0 or (row * 3 + col * 5) % 37 == 0 else 0
            values.append(value)
        matrix.append(values)
    return matrix


def _format_axes(ax, title: str, *, grid: bool = True):
    ax.set_title(title, fontsize=10)
    if grid:
        ax.grid(True, alpha=0.25)
    ax.tick_params(labelsize=8)


def _build_gallery(plotter: DemoPlotter, axes: dict[str, object]) -> None:
    xs, sin_y, cos_y, envelope = _wave_data()

    ax = axes["lines"]
    plotter.plot(xs, sin_y, "b-o", axes=ax, DisplayName="sin", markevery=18)
    plotter.hold("on")
    plotter.plot(xs, cos_y, "r-s", axes=ax, DisplayName="cos", markevery=(6, 18))
    plotter.xline(2.0, "--k", "x=2", axes=ax)
    plotter.yline(0.0, ":k", "zero", axes=ax)
    plotter.hold("off")
    _format_axes(ax, "plot, markers, xline, yline")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes["log"]
    xlog = [0.12 + i * 0.09 for i in range(1, 90)]
    plotter.loglog(xlog, [x**1.7 for x in xlog], "b-", axes=ax, DisplayName="x^1.7")
    plotter.hold("on")
    plotter.semilogy(xlog, [math.exp(0.42 * x) for x in xlog], "r--", axes=ax, DisplayName="exp")
    plotter.hold("off")
    _format_axes(ax, "loglog and semilogy")
    ax.legend(loc="lower right", fontsize=8)

    ax = axes["error_scatter"]
    sample_x = [i * 0.35 for i in range(24)]
    sample_y = [math.sin(x) + 0.08 * math.cos(5 * x) for x in sample_x]
    err = [0.08 + 0.04 * abs(math.sin(x * 1.8)) for x in sample_x]
    plotter.errorbar(sample_x, sample_y, err, axes=ax, DisplayName="errorbar", Color="#0072BD")
    plotter.hold("on")
    plotter.scatter(
        sample_x,
        [y + 0.45 for y in sample_y],
        [32 + 18 * abs(math.cos(x)) for x in sample_x],
        "#D95319",
        axes=ax,
        DisplayName="scatter dots",
    )
    plotter.hold("off")
    _format_axes(ax, "errorbar and scatter")
    ax.legend(loc="lower left", fontsize=8)

    ax = axes["bars"]
    categories = [1, 2, 3, 4, 5]
    plotter.bar(categories, [4.0, 6.0, 5.2, 7.0, 4.8], axes=ax, DisplayName="bar")
    plotter.hold("on")
    plotter.barh([1.25, 2.25, 3.25, 4.25, 5.25], [2.4, 2.9, 2.1, 3.2, 2.7], axes=ax, DisplayName="barh")
    plotter.hold("off")
    _format_axes(ax, "bar and barh")
    ax.legend(loc="upper left", fontsize=8)

    ax = axes["area_fill"]
    area_x = [i * 0.18 for i in range(48)]
    area_a = [0.35 + 0.22 * math.sin(x) for x in area_x]
    area_b = [0.25 + 0.12 * math.cos(1.7 * x) for x in area_x]
    plotter.area(area_x, area_a, area_b, axes=ax, DisplayName="area")
    plotter.hold("on")
    polygon_x = [1.4, 2.3, 3.1, 2.6, 1.5]
    polygon_y = [0.15, 0.72, 0.32, -0.10, -0.08]
    plotter.fill(polygon_x, polygon_y, "#EDB120", axes=ax, alpha=0.45, DisplayName="fill")
    plotter.hold("off")
    _format_axes(ax, "area and fill")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes["hist_stem"]
    hist_values = [math.sin(i * 0.17) + 0.35 * math.sin(i * 0.53) for i in range(220)]
    plotter.histogram(hist_values, axes=ax, bins=22, DisplayName="histogram")
    plotter.hold("on")
    stem_x = [i * 0.35 - 2.5 for i in range(15)]
    stem_y = [0.45 * math.cos(x * 1.5) for x in stem_x]
    plotter.stem(stem_x, stem_y, axes=ax, DisplayName="stem", Marker="o")
    plotter.hold("off")
    _format_axes(ax, "histogram and stem")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes["image"]
    heat = _heat_data()
    plotter.imagesc(heat, axes=ax)
    plotter.hold("on")
    plotter.contour(heat, 8, axes=ax, colors="black", linewidths=0.55)
    plotter.hold("off")
    _format_axes(ax, "imagesc and contour", grid=False)

    ax = axes["field"]
    grid = [i * 0.45 - 2.0 for i in range(10)]
    x_points = []
    y_points = []
    u_points = []
    v_points = []
    for y in grid:
        for x in grid:
            x_points.append(x)
            y_points.append(y)
            u_points.append(-y * 0.25 + 0.1 * math.sin(x))
            v_points.append(x * 0.25 + 0.1 * math.cos(y))
    plotter.contourf(_heat_data(12, 12), 8, axes=ax, cmap="Blues", alpha=0.55)
    plotter.hold("on")
    plotter.quiver(x_points, y_points, u_points, v_points, axes=ax, Color="#0072BD")
    plotter.hold("off")
    _format_axes(ax, "contourf and quiver")

    ax = axes["sparse"]
    plotter.spy(_sparse_pattern(), axes=ax, markersize=3.0)
    _format_axes(ax, "spy sparsity pattern", grid=False)

    ax = axes["plot3"]
    theta = [i * 0.09 for i in range(180)]
    radius = [1.0 + 0.12 * math.sin(4 * t) for t in theta]
    z = [i / 34 for i in range(len(theta))]
    plotter.plot3(
        [r * math.cos(t) for r, t in zip(radius, theta)],
        [r * math.sin(t) for r, t in zip(radius, theta)],
        z,
        "b-",
        axes=ax,
        DisplayName="plot3",
    )
    plotter.hold("on")
    dots = list(range(0, len(theta), 12))
    plotter.scatter3(
        [radius[i] * math.cos(theta[i]) for i in dots],
        [radius[i] * math.sin(theta[i]) for i in dots],
        [z[i] for i in dots],
        34,
        "#D95319",
        axes=ax,
        DisplayName="scatter3",
    )
    plotter.hold("off")
    _format_axes(ax, "plot3 and scatter3")
    ax.legend(loc="upper left", fontsize=8)

    ax = axes["surface"]
    _x_grid, _y_grid, z_grid = _surface_data()
    plotter.surf(z_grid, axes=ax, cmap="viridis", linewidth=0.0, antialiased=True)
    _format_axes(ax, "surf")

    ax = axes["mesh"]
    _x_grid, _y_grid, z_grid = _surface_data(28)
    plotter.mesh(z_grid, axes=ax, color="#0072BD", linewidth=0.45)
    _format_axes(ax, "mesh")

    ax = axes["waterfall"]
    _x_grid, _y_grid, z_grid = _surface_data(30)
    plotter.waterfall(z_grid, axes=ax, color="#7E2F8E", linewidth=0.6)
    _format_axes(ax, "waterfall")

    for key in ("plot3", "surface", "mesh", "waterfall"):
        axes[key].view_init(elev=28, azim=-42)


def _create_axes(fig):
    spec = fig.add_gridspec(
        4,
        4,
        left=0.045,
        right=0.985,
        bottom=0.075,
        top=0.94,
        wspace=0.32,
        hspace=0.44,
    )
    return {
        "lines": fig.add_subplot(spec[0, 0]),
        "log": fig.add_subplot(spec[0, 1]),
        "error_scatter": fig.add_subplot(spec[0, 2]),
        "bars": fig.add_subplot(spec[0, 3]),
        "area_fill": fig.add_subplot(spec[1, 0]),
        "hist_stem": fig.add_subplot(spec[1, 1]),
        "image": fig.add_subplot(spec[1, 2]),
        "field": fig.add_subplot(spec[1, 3]),
        "sparse": fig.add_subplot(spec[2, 0]),
        "plot3": fig.add_subplot(spec[2, 1], projection="3d"),
        "surface": fig.add_subplot(spec[2, 2], projection="3d"),
        "mesh": fig.add_subplot(spec[2, 3], projection="3d"),
        "waterfall": fig.add_subplot(spec[3, 0], projection="3d"),
    }


def main() -> None:
    fig = plt.figure(figsize=(15.5, 10.5))
    fig.suptitle("pyMatlabStylePlotter gallery: plotting API and MATLAB-like axes interaction", fontsize=13)
    axes = _create_axes(fig)

    status_text = fig.text(0.045, 0.028, "", ha="left", va="center", fontsize=9)
    first_axes = axes["lines"]
    plotter = DemoPlotter(first_axes, status_text)
    with plotter.batch_draw_idle():
        _build_gallery(plotter, axes)

    context_menu = DemoContextMenu(fig, plotter)
    bridge = MatplotlibContextMenuEventBridge(plotter, context_menu=context_menu)
    bridge.connect()
    fig._py_matlab_style_context_menu = context_menu
    fig._py_matlab_style_bridge = bridge
    fig._py_matlab_style_plotter = plotter

    with plotter.batch_draw_idle():
        for ax in axes.values():
            plotter.set_active_axes(ax)
            plotter.push_current_view(ax)
        plotter.set_active_axes(first_axes)

    fig.canvas.manager.set_window_title("pyMatlabStylePlotter gallery")
    if matplotlib.get_backend().lower() != "agg":
        plt.show()
        return
    output = Path(tempfile.gettempdir()) / "py_matlab_style_plotter_gallery.png"
    fig.savefig(output, dpi=120)
    print(output)


if __name__ == "__main__":
    main()
