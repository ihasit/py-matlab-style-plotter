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
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from py_matlab_style_plotter import CoordinateReadout, MatplotlibAxesPlotter, MatplotlibEventBridge


_MATLAB_MENU_ITEMS = (
    ("None", "matlab_none"),
    ("Pan", "matlab_pan"),
    ("Zoom", "matlab_zoom"),
    ("Rotate3D", "matlab_rotate3d"),
    ("Cursor", "matlab_data_cursor"),
    ("Select", "matlab_select"),
    ("Brush", "matlab_brush"),
    None,
    (
        "Marker",
        (
            ("None", "matlab_marker_none"),
            ("Circle", "matlab_marker_circle"),
            ("Square", "matlab_marker_square"),
            ("Triangle", "matlab_marker_triangle"),
            ("X", "matlab_marker_x"),
            ("Plus", "matlab_marker_plus"),
            ("Point", "matlab_marker_point"),
        ),
    ),
    (
        "Line Style",
        (
            ("Solid", "matlab_line_solid"),
            ("Dashed", "matlab_line_dashed"),
            ("Dash-dot", "matlab_line_dashdot"),
            ("Dotted", "matlab_line_dotted"),
            ("None", "matlab_line_none"),
        ),
    ),
    (
        "Color",
        (
            ("Blue", "matlab_color_blue"),
            ("Orange", "matlab_color_orange"),
            ("Yellow", "matlab_color_yellow"),
            ("Purple", "matlab_color_purple"),
            ("Green", "matlab_color_green"),
            ("Cyan", "matlab_color_cyan"),
            ("Red", "matlab_color_red"),
            ("Black", "matlab_color_black"),
        ),
    ),
    None,
    (
        "View",
        (
            ("Home", "matlab_home"),
            ("Back", "matlab_back"),
            ("Forward", "matlab_forward"),
            None,
            ("View 2-D", "matlab_view_2"),
            ("View 3-D", "matlab_view_3"),
        ),
    ),
    (
        "Axis",
        (
            ("Auto", "matlab_axis_auto"),
            ("Manual", "matlab_axis_manual"),
            ("Tight", "matlab_axis_tight"),
            ("Equal", "matlab_axis_equal"),
            ("Fill", "matlab_axis_fill"),
            ("Image", "matlab_axis_image"),
            ("Normal", "matlab_axis_normal"),
            ("Square", "matlab_axis_square"),
            ("Vis3D", "matlab_axis_vis3d"),
            None,
            ("Off", "matlab_axis_off"),
            ("On", "matlab_axis_on"),
            ("IJ", "matlab_axis_ij"),
            ("XY", "matlab_axis_xy"),
        ),
    ),
    (
        "Display",
        (
            ("Hold", "matlab_hold"),
            ("Grid", "matlab_grid"),
            ("Legend", "matlab_legend"),
            ("Box", "matlab_box"),
            ("Colorbar", "matlab_colorbar"),
        ),
    ),
    (
        "Link Axes",
        (
            ("Link X", "matlab_link_x"),
            ("Link Y", "matlab_link_y"),
            ("Link X/Y", "matlab_link_xy"),
        ),
    ),
    (
        "Selection",
        (
            ("Hide Selected", "matlab_selected_visibility"),
            ("Clear Selection", "matlab_clear_selection"),
            ("Delete", "matlab_delete_selected"),
        ),
    ),
)
_MENU_ICON_BY_METHOD = {
    "matlab_none": "pointer",
    "matlab_pan": "pan",
    "matlab_zoom": "zoom",
    "matlab_rotate3d": "rotate",
    "matlab_data_cursor": "cursor",
    "matlab_select": "select",
    "matlab_brush": "brush",
    "matlab_marker_none": "marker_none",
    "matlab_marker_circle": "marker_circle",
    "matlab_marker_square": "marker_square",
    "matlab_marker_triangle": "marker_triangle",
    "matlab_marker_x": "marker_x",
    "matlab_marker_plus": "marker_plus",
    "matlab_marker_point": "marker_point",
    "matlab_line_solid": "line_solid",
    "matlab_line_dashed": "line_dashed",
    "matlab_line_dashdot": "line_dashdot",
    "matlab_line_dotted": "line_dotted",
    "matlab_line_none": "line_none",
    "matlab_color_blue": "color_blue",
    "matlab_color_orange": "color_orange",
    "matlab_color_yellow": "color_yellow",
    "matlab_color_purple": "color_purple",
    "matlab_color_green": "color_green",
    "matlab_color_cyan": "color_cyan",
    "matlab_color_red": "color_red",
    "matlab_color_black": "color_black",
    "matlab_home": "home",
    "matlab_back": "back",
    "matlab_forward": "forward",
    "matlab_view_2": "view2",
    "matlab_view_3": "view3",
    "matlab_axis_auto": "axis",
    "matlab_axis_manual": "axis_manual",
    "matlab_axis_tight": "axis_tight",
    "matlab_axis_equal": "axis_equal",
    "matlab_axis_fill": "axis_fill",
    "matlab_axis_image": "axis_image",
    "matlab_axis_normal": "axis_normal",
    "matlab_axis_square": "axis_square",
    "matlab_axis_vis3d": "axis_vis3d",
    "matlab_axis_off": "axis_off",
    "matlab_axis_on": "axis_on",
    "matlab_axis_ij": "axis_ij",
    "matlab_axis_xy": "axis_xy",
    "matlab_hold": "hold",
    "matlab_grid": "grid",
    "matlab_legend": "legend",
    "matlab_box": "box",
    "matlab_colorbar": "colorbar",
    "matlab_link_x": "link_x",
    "matlab_link_y": "link_y",
    "matlab_link_xy": "link_xy",
    "matlab_selected_visibility": "visibility",
    "matlab_clear_selection": "clear_selection",
    "matlab_delete_selected": "delete",
}
_MENU_ICON_BY_LABEL = {
    "Marker": "marker",
    "Line Style": "line",
    "Color": "color",
    "View": "view",
    "Axis": "axis",
    "Display": "display",
    "Link Axes": "link",
    "Selection": "selection",
}


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
    _COLORS = {
        "blue": (0.0, 0.4470, 0.7410),
        "orange": (0.8500, 0.3250, 0.0980),
        "yellow": (0.9290, 0.6940, 0.1250),
        "purple": (0.4940, 0.1840, 0.5560),
        "green": (0.4660, 0.6740, 0.1880),
        "cyan": (0.3010, 0.7450, 0.9330),
        "red": (0.6350, 0.0780, 0.1840),
        "black": (0.0, 0.0, 0.0),
    }

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

    def matlab_home(self, *_args) -> None:
        self.plotter.home()

    def matlab_back(self, *_args) -> None:
        self.plotter.back()

    def matlab_forward(self, *_args) -> None:
        self.plotter.forward()

    def matlab_view_2(self, *_args) -> None:
        self.bridge.apply_view(2)

    def matlab_view_3(self, *_args) -> None:
        self.bridge.apply_view(3)

    def matlab_axis_auto(self, *_args) -> None:
        self.plotter.axis("auto")

    def matlab_axis_manual(self, *_args) -> None:
        self.plotter.axis("manual")

    def matlab_axis_tight(self, *_args) -> None:
        self.plotter.axis("tight")

    def matlab_axis_equal(self, *_args) -> None:
        self.plotter.axis("equal")

    def matlab_axis_fill(self, *_args) -> None:
        self.plotter.axis("fill")

    def matlab_axis_image(self, *_args) -> None:
        self.plotter.axis("image")

    def matlab_axis_normal(self, *_args) -> None:
        self.plotter.axis("normal")

    def matlab_axis_square(self, *_args) -> None:
        self.plotter.axis("square")

    def matlab_axis_vis3d(self, *_args) -> None:
        self.plotter.axis("vis3d")

    def matlab_axis_off(self, *_args) -> None:
        self.plotter.axis("off")

    def matlab_axis_on(self, *_args) -> None:
        self.plotter.axis("on")

    def matlab_axis_ij(self, *_args) -> None:
        self.plotter.axis("ij")

    def matlab_axis_xy(self, *_args) -> None:
        self.plotter.axis("xy")

    def matlab_hold(self, *_args) -> None:
        self.plotter.hold("toggle")

    def matlab_grid(self, *_args) -> None:
        self.plotter.grid("toggle")

    def matlab_legend(self, *_args) -> None:
        self.plotter.legend("toggle")

    def matlab_box(self, *_args) -> None:
        self.plotter.box("toggle")

    def matlab_colorbar(self, *_args) -> None:
        self.plotter.colorbar("toggle")

    def matlab_link_x(self, *_args) -> None:
        self.plotter.toggle_link_x_axes()

    def matlab_link_y(self, *_args) -> None:
        self.plotter.toggle_link_y_axes()

    def matlab_link_xy(self, *_args) -> None:
        self.plotter.toggle_link_xy_axes()

    def matlab_marker_none(self, *_args) -> None:
        self._set_line_property("marker", "None")

    def matlab_marker_circle(self, *_args) -> None:
        self._set_line_property("marker", "o")

    def matlab_marker_square(self, *_args) -> None:
        self._set_line_property("marker", "s")

    def matlab_marker_triangle(self, *_args) -> None:
        self._set_line_property("marker", "^")

    def matlab_marker_x(self, *_args) -> None:
        self._set_line_property("marker", "x")

    def matlab_marker_plus(self, *_args) -> None:
        self._set_line_property("marker", "+")

    def matlab_marker_point(self, *_args) -> None:
        self._set_line_property("marker", ".")

    def matlab_line_solid(self, *_args) -> None:
        self._set_line_property("linestyle", "-")

    def matlab_line_dashed(self, *_args) -> None:
        self._set_line_property("linestyle", "--")

    def matlab_line_dashdot(self, *_args) -> None:
        self._set_line_property("linestyle", "-.")

    def matlab_line_dotted(self, *_args) -> None:
        self._set_line_property("linestyle", ":")

    def matlab_line_none(self, *_args) -> None:
        self._set_line_property("linestyle", "None")

    def matlab_color_blue(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["blue"])

    def matlab_color_orange(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["orange"])

    def matlab_color_yellow(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["yellow"])

    def matlab_color_purple(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["purple"])

    def matlab_color_green(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["green"])

    def matlab_color_cyan(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["cyan"])

    def matlab_color_red(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["red"])

    def matlab_color_black(self, *_args) -> None:
        self._set_line_property("color", self._COLORS["black"])

    def matlab_selected_visibility(self, *_args) -> None:
        self.plotter.toggle_selected_visibility()

    def matlab_clear_selection(self, *_args) -> None:
        self.plotter.clear_selection()

    def matlab_delete_selected(self, *_args) -> None:
        self.plotter.delete_selected()

    def _set_line_property(self, name, value):
        lines = self._target_lines()
        if not lines:
            return
        setter_name = f"set_{name}"
        axes_to_draw = set()
        for line in lines:
            setter = getattr(line, setter_name, None)
            if setter is None:
                continue
            setter(value)
            axes = getattr(line, "axes", None)
            if axes is not None:
                axes_to_draw.add(axes)
        for axes in axes_to_draw:
            self.plotter._draw_idle(axes)

    def _target_lines(self):
        selected = [state.line for state in self.plotter.selected_lines]
        if selected:
            return selected
        axes = self.plotter.active_axes or self.plotter.axes
        return list(getattr(axes, "lines", ())) if axes is not None else []


class MatlabContextMenu:
    """Figure-level context menu that does not create Matplotlib Axes."""

    def __init__(self, fig, actions: MatlabToolbarActions, plotter: DemoPlotter) -> None:
        self.fig = fig
        self.actions = actions
        self.plotter = plotter
        self._artists = []
        self._items = []
        self._submenu_parent = None
        self._hover_patch = None

    def _open(self, x: float, y: float, axes) -> None:
        self.close()
        self.plotter.set_active_axes(axes)
        self._draw_menu(_MATLAB_MENU_ITEMS, x, y, level=0)
        self.fig.canvas.draw_idle()

    def close(self) -> None:
        if not self._artists:
            return
        for artist in list(self._artists):
            artist.remove()
        self._artists.clear()
        self._items.clear()
        self._submenu_parent = None
        self._hover_patch = None
        self.fig.canvas.draw_idle()

    def _draw_menu(self, items, x: float, y: float, *, level: int, parent_patch=None) -> None:
        entries = list(items)
        row_height = 0.034
        separator_height = 0.009
        padding_x = 0.014
        icon_width = 0.024
        text_x = padding_x + icon_width + 0.008
        padding_y = 0.006
        menu_width = self._menu_width(entries)
        menu_height = padding_y * 2 + sum(separator_height if item is None else row_height for item in entries)
        x = min(max(x, 0.01), 0.99 - menu_width)
        y = min(max(y, menu_height + 0.01), 0.99)
        background = self._add_patch(
            x,
            y - menu_height,
            menu_width,
            menu_height,
            face="#ffffff",
            edge="#6f6f6f",
            line=0.8,
            z=20_000 + level * 100,
        )
        current_y = y - padding_y
        for item in entries:
            if item is None:
                sep_y = current_y - separator_height / 2
                self._add_patch(
                    x + 0.006,
                    sep_y,
                    menu_width - 0.012,
                    0.001,
                    face="#d0d0d0",
                    edge="#d0d0d0",
                    line=0.0,
                    z=20_002 + level * 100,
                )
                current_y -= separator_height
                continue
            label, action_or_submenu = item
            item_y = current_y - row_height
            patch = self._add_patch(
                x,
                item_y,
                menu_width,
                row_height,
                face="#ffffff",
                edge="#ffffff",
                line=0.0,
                z=20_001 + level * 100,
            )
            self._add_text(
                x + text_x,
                item_y + row_height / 2,
                label,
                ha="left",
                size=8,
                color="#1f1f1f",
                z=20_003 + level * 100,
            )
            submenu = action_or_submenu if isinstance(action_or_submenu, tuple) else None
            method_name = None if submenu is not None else action_or_submenu
            icon_kind = _MENU_ICON_BY_LABEL.get(label) if submenu is not None else _MENU_ICON_BY_METHOD.get(action_or_submenu)
            if icon_kind is not None:
                self._draw_menu_icon(icon_kind, x + padding_x, item_y + row_height / 2, icon_width, row_height, level)
            if submenu is not None:
                self._add_text(
                    x + menu_width - 0.014,
                    item_y + row_height / 2,
                    ">",
                    ha="right",
                    size=8,
                    color="#404040",
                    z=20_003 + level * 100,
                )
            else:
                self._draw_menu_sample(action_or_submenu, x, item_y, menu_width, row_height, level)
            self._items.append(
                {
                    "patch": patch,
                    "method": method_name,
                    "submenu": submenu,
                    "level": level,
                    "parent": parent_patch,
                    "menu_x": x,
                    "menu_y": y - menu_height,
                    "menu_width": menu_width,
                    "menu_height": menu_height,
                }
            )
            current_y -= row_height

    def _draw_menu_sample(self, method_name: str, x: float, y: float, width: float, height: float, level: int):
        sample_x = x + width - 0.044
        sample_y = y + height / 2
        if method_name.startswith("matlab_color_"):
            color_name = method_name.removeprefix("matlab_color_")
            color = self.actions._COLORS.get(color_name)
            if color is not None:
                self._add_patch(
                    sample_x,
                    sample_y - 0.007,
                    0.022,
                    0.014,
                    face=color,
                    edge="#5f5f5f",
                    line=0.4,
                    z=20_004 + level * 100,
                )
            return
        if method_name.startswith("matlab_line_") and method_name != "matlab_line_none":
            line_text = {
                "matlab_line_solid": "----",
                "matlab_line_dashed": "- - -",
                "matlab_line_dashdot": "- . -",
                "matlab_line_dotted": ". . .",
            }.get(method_name)
            if line_text:
                self._add_text(sample_x, sample_y, line_text, ha="left", size=8, color="#202020", z=20_004 + level * 100)
            return
        if method_name.startswith("matlab_marker_") and method_name != "matlab_marker_none":
            marker_text = {
                "matlab_marker_circle": "o",
                "matlab_marker_square": "s",
                "matlab_marker_triangle": "^",
                "matlab_marker_x": "x",
                "matlab_marker_plus": "+",
                "matlab_marker_point": ".",
            }.get(method_name)
            if marker_text:
                self._add_text(sample_x + 0.012, sample_y, marker_text, ha="center", size=9, color="#202020", z=20_004 + level * 100)

    def _draw_menu_icon(self, kind: str, x: float, y: float, width: float, height: float, level: int) -> None:
        cx = x + width / 2
        z = 20_004 + level * 100
        left = x + width * 0.22
        right = x + width * 0.78
        top = y + height * 0.22
        bottom = y - height * 0.22
        accent = "#0072BD"
        if kind.startswith("color_"):
            self._draw_color_icon(kind, x, y, width, height, z)
            return
        if kind.startswith("marker_"):
            self._draw_marker_icon(kind, cx, y, z)
            return
        if kind.startswith("line_"):
            self._draw_line_icon(kind, x, y, width, z)
            return
        if kind in {"pointer", "select"}:
            self._add_line([left, right], [top, bottom], color="#202020", width=1.0, z=z)
            self._add_line([left, left + width * 0.26], [top, top - height * 0.02], color="#202020", width=1.0, z=z)
            self._add_line([left, left + width * 0.06], [top, top - height * 0.23], color="#202020", width=1.0, z=z)
        elif kind == "pan":
            self._add_line([left, right], [y, y], color="#202020", width=1.0, z=z)
            self._add_line([cx, cx], [bottom, top], color="#202020", width=1.0, z=z)
            self._add_line([left, left + width * 0.12], [y, y + height * 0.08], color="#202020", width=1.0, z=z)
            self._add_line([left, left + width * 0.12], [y, y - height * 0.08], color="#202020", width=1.0, z=z)
            self._add_line([right, right - width * 0.12], [y, y + height * 0.08], color="#202020", width=1.0, z=z)
            self._add_line([right, right - width * 0.12], [y, y - height * 0.08], color="#202020", width=1.0, z=z)
        elif kind == "zoom":
            self._add_marker(cx - width * 0.05, y + height * 0.04, "o", color="#202020", size=5.2, z=z, fill="none")
            self._add_line([cx + width * 0.12, right], [y - height * 0.08, bottom], color="#202020", width=1.0, z=z)
        elif kind == "rotate":
            self._add_marker(cx, y, "o", color="#202020", size=6.2, z=z, fill="none")
            self._add_line([cx + width * 0.14, right], [y + height * 0.12, y + height * 0.20], color="#202020", width=1.0, z=z)
            self._add_line([right, right - width * 0.08], [y + height * 0.20, y + height * 0.08], color="#202020", width=1.0, z=z)
        elif kind == "cursor":
            self._add_line([left, right], [y, y], color="#202020", width=0.9, z=z)
            self._add_line([cx, cx], [bottom, top], color="#202020", width=0.9, z=z)
        elif kind == "brush":
            self._add_patch(x + width * 0.28, y - height * 0.12, width * 0.36, height * 0.24, face=accent, edge=accent, line=0.0, z=z)
            self._add_line([x + width * 0.60, right], [y - height * 0.02, bottom], color=accent, width=1.0, z=z)
        elif kind == "marker":
            self._add_marker(cx, y, "o", color=accent, size=5.8, z=z)
        elif kind == "line":
            self._draw_line_icon("line_solid", x, y, width, z)
        elif kind == "color":
            self._draw_color_swatch(x, y, width, height, "#0072BD", z)
        elif kind in {"view", "view2", "view3"}:
            self._draw_outline_box(x, y, width, height, z)
        elif kind.startswith("axis"):
            self._add_line([left, left], [bottom, top], color="#202020", width=1.0, z=z)
            self._add_line([left, right], [bottom, bottom], color="#202020", width=1.0, z=z)
        elif kind == "display":
            self._draw_outline_box(x, y, width, height, z)
            self._add_patch(cx - width * 0.12, y - height * 0.10, width * 0.24, height * 0.20, face="#202020", edge="#202020", line=0.0, z=z)
        elif kind == "grid":
            self._draw_outline_box(x, y, width, height, z)
            self._add_line([cx, cx], [bottom, top], color="#202020", width=0.6, z=z)
            self._add_line([left, right], [y, y], color="#202020", width=0.6, z=z)
        elif kind == "legend":
            for offset in (-0.11, 0.0, 0.11):
                self._add_line([left, right], [y + height * offset, y + height * offset], color="#202020", width=0.8, z=z)
        elif kind == "box":
            self._draw_outline_box(x, y, width, height, z)
        elif kind == "colorbar":
            self._draw_color_swatch(x, y, width, height, "#D95319", z)
        elif kind.startswith("link"):
            self._add_marker(cx - width * 0.12, y, "o", color="#202020", size=4.2, z=z, fill="none")
            self._add_marker(cx + width * 0.12, y, "o", color="#202020", size=4.2, z=z, fill="none")
            self._add_line([cx - width * 0.04, cx + width * 0.04], [y, y], color="#202020", width=0.8, z=z)
        elif kind == "selection":
            self._draw_outline_box(x, y, width, height, z)
            self._add_line([cx - width * 0.12, cx - width * 0.02, cx + width * 0.18], [y, bottom + height * 0.10, top - height * 0.06], color=accent, width=1.0, z=z)
        elif kind == "visibility":
            self._add_marker(cx, y, "o", color="#202020", size=6.0, z=z, fill="none")
            self._add_marker(cx, y, "o", color="#202020", size=2.0, z=z)
        elif kind == "clear_selection":
            self._draw_x_icon(x, y, width, height, z)
        elif kind == "delete":
            self._draw_x_icon(x, y, width, height, z)
            self._add_line([left, right], [top, top], color="#202020", width=0.8, z=z)
        elif kind == "home":
            self._add_line([left, cx, right], [y, top, y], color="#202020", width=1.0, z=z)
            self._add_line([left + width * 0.10, left + width * 0.10, right - width * 0.10, right - width * 0.10], [y, bottom, bottom, y], color="#202020", width=1.0, z=z)
        elif kind == "back":
            self._add_line([right, left, right], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "forward":
            self._add_line([left, right, left], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "hold":
            self._add_text(cx, y, "H", ha="center", size=8, color="#202020", z=z)

    def _draw_marker_icon(self, kind: str, x: float, y: float, z: int) -> None:
        marker = {
            "marker_none": "x",
            "marker_circle": "o",
            "marker_square": "s",
            "marker_triangle": "^",
            "marker_x": "x",
            "marker_plus": "+",
            "marker_point": ".",
        }.get(kind, "o")
        fill = "none" if kind == "marker_none" else "#0072BD"
        self._add_marker(x, y, marker, color="#0072BD", size=5.8, z=z, fill=fill)

    def _draw_line_icon(self, kind: str, x: float, y: float, width: float, z: int) -> None:
        if kind == "line_none":
            self._draw_x_icon(x, y, width, width, z, color="#0072BD")
            return
        style = {
            "line_solid": "-",
            "line_dashed": "--",
            "line_dashdot": "-.",
            "line_dotted": ":",
        }.get(kind, "-")
        self._add_line([x + width * 0.16, x + width * 0.84], [y, y], color="#0072BD", width=1.4, z=z, style=style)

    def _draw_color_icon(self, kind: str, x: float, y: float, width: float, height: float, z: int) -> None:
        color = {
            "color_blue": "#0072BD",
            "color_orange": "#D95319",
            "color_yellow": "#EDB120",
            "color_purple": "#7E2F8E",
            "color_green": "#77AC30",
            "color_cyan": "#4DBEEE",
            "color_red": "#A2142F",
            "color_black": "#000000",
        }.get(kind, "#0072BD")
        self._draw_color_swatch(x, y, width, height, color, z)

    def _draw_color_swatch(self, x: float, y: float, width: float, height: float, color: str, z: int) -> None:
        swatch_width = min(width * 0.62, 0.014)
        swatch_height = min(height * 0.46, 0.014)
        self._add_patch(
            x + (width - swatch_width) / 2,
            y - swatch_height / 2,
            swatch_width,
            swatch_height,
            face=color,
            edge="#5f5f5f",
            line=0.35,
            z=z,
        )

    def _draw_outline_box(self, x: float, y: float, width: float, height: float, z: int) -> None:
        box_width = width * 0.52
        box_height = height * 0.42
        self._add_patch(
            x + (width - box_width) / 2,
            y - box_height / 2,
            box_width,
            box_height,
            face="none",
            edge="#202020",
            line=0.8,
            z=z,
        )

    def _draw_x_icon(self, x: float, y: float, width: float, height: float, z: int, *, color: str = "#202020") -> None:
        left = x + width * 0.28
        right = x + width * 0.72
        top = y + height * 0.18
        bottom = y - height * 0.18
        self._add_line([left, right], [top, bottom], color=color, width=1.0, z=z)
        self._add_line([left, right], [bottom, top], color=color, width=1.0, z=z)

    def _menu_width(self, entries) -> float:
        labels = [item[0] for item in entries if item is not None]
        longest = max((len(label) for label in labels), default=8)
        return max(0.18, min(0.25, 0.105 + longest * 0.008))

    def _add_patch(self, x, y, width, height, *, face, edge, line, z):
        patch = Rectangle(
            (x, y),
            width,
            height,
            transform=self.fig.transFigure,
            facecolor=face,
            edgecolor=edge,
            linewidth=line,
            zorder=z,
        )
        self.fig.patches.append(patch)
        patch._remove_method = self.fig.patches.remove
        self._artists.append(patch)
        return patch

    def _add_line(self, xs, ys, *, color, width, z, style="-"):
        line = Line2D(
            xs,
            ys,
            transform=self.fig.transFigure,
            color=color,
            linewidth=width,
            linestyle=style,
            solid_capstyle="round",
            zorder=z,
        )
        self.fig.lines.append(line)
        line._remove_method = self.fig.lines.remove
        self._artists.append(line)
        return line

    def _add_marker(self, x, y, marker, *, color, size, z, fill=None):
        marker_face = color if fill is None else fill
        line = Line2D(
            [x],
            [y],
            transform=self.fig.transFigure,
            marker=marker,
            markersize=size,
            markeredgecolor=color,
            markerfacecolor=marker_face,
            color=color,
            linestyle="None",
            zorder=z,
        )
        self.fig.lines.append(line)
        line._remove_method = self.fig.lines.remove
        self._artists.append(line)
        return line

    def _add_text(self, x, y, label, *, ha, size, color, z):
        text = self.fig.text(
            x,
            y,
            label,
            ha=ha,
            va="center",
            fontsize=size,
            color=color,
            zorder=z,
        )
        self._artists.append(text)
        return text

    def _clear_submenus(self) -> None:
        if self._submenu_parent is None:
            return
        keep_artists = []
        for artist in self._artists:
            if getattr(artist, "get_zorder", lambda: 0)() >= 20_100:
                artist.remove()
                continue
            keep_artists.append(artist)
        self._items = [item for item in self._items if item["level"] == 0]
        self._artists = keep_artists
        self._submenu_parent = None
        if self._hover_patch is not None and self._hover_patch not in {item["patch"] for item in self._items}:
            self._hover_patch = None

    def _on_press(self, event) -> bool:
        if event.x is None or event.y is None:
            return False
        figure_xy = self.fig.transFigure.inverted().transform((event.x, event.y))
        if self._items:
            for item in reversed(self._items):
                patch = item["patch"]
                x, y = patch.get_xy()
                if x <= figure_xy[0] <= x + patch.get_width() and y <= figure_xy[1] <= y + patch.get_height():
                    if self._hover_patch is not patch:
                        if self._hover_patch is not None:
                            self._hover_patch.set_facecolor("#ffffff")
                        patch.set_facecolor("#dbeafe")
                        self._hover_patch = patch
                    if item["submenu"] is not None:
                        self._clear_submenus()
                        self._submenu_parent = patch
                        self._draw_menu(
                            item["submenu"],
                            x + patch.get_width() - 0.002,
                            y + patch.get_height(),
                            level=item["level"] + 1,
                            parent_patch=patch,
                        )
                        self.fig.canvas.draw_idle()
                        return True
                    self.close()
                    getattr(self.actions, item["method"])()
                    return True
            self.close()
            return True
        if event.inaxes is None or not self._is_right_click(getattr(event, "button", None)):
            return False
        if getattr(self.plotter.mode, "value", self.plotter.mode) == "zoom":
            return False
        self._open(float(figure_xy[0]), float(figure_xy[1]), event.inaxes)
        return True

    def _is_right_click(self, button) -> bool:
        if button == 3:
            return True
        name = getattr(button, "name", str(button)).lower()
        return name in {"right", "button3", "mousebutton.right"}


class ContextMenuEventBridge(MatplotlibEventBridge):
    def __init__(self, plotter: DemoPlotter, canvas, context_menu: MatlabContextMenu) -> None:
        super().__init__(plotter, canvas)
        self.context_menu = context_menu

    def _on_button_press(self, event) -> None:
        if self.context_menu._on_press(event):
            return
        super()._on_button_press(event)


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
    actions = MatlabToolbarActions(None, plotter)
    context_menu = MatlabContextMenu(fig, actions, plotter)
    bridge = ContextMenuEventBridge(plotter, fig.canvas, context_menu)
    actions.bridge = bridge
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
