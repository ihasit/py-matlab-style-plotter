"""MATLAB-style Matplotlib figure context menu."""

from __future__ import annotations

import csv
from datetime import datetime
import importlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

from .matplotlib_adapter import MatplotlibAxesPlotter
from .matplotlib_bridge import MatplotlibEventBridge

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
            ("Auto View", "matlab_auto_view"),
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
        "Color Scale",
        (
            ("Auto Limits", "matlab_clim_auto"),
            ("Set Limits...", "matlab_clim_set"),
            None,
            (
                "Colormap",
                (
                    ("Viridis", "matlab_colormap_viridis"),
                    ("Plasma", "matlab_colormap_plasma"),
                    ("Gray", "matlab_colormap_gray"),
                    ("Hot", "matlab_colormap_hot"),
                    ("Jet", "matlab_colormap_jet"),
                    ("Turbo", "matlab_colormap_turbo"),
                ),
            ),
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
        "Export Data",
        (
            ("CSV", "matlab_export_csv"),
            ("JSON", "matlab_export_json"),
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
    "matlab_none": "none",
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
    "matlab_auto_view": "auto_view",
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
    "matlab_clim_auto": "colorbar",
    "matlab_clim_set": "axis_manual",
    "matlab_colormap_viridis": "color_viridis",
    "matlab_colormap_plasma": "color_plasma",
    "matlab_colormap_gray": "color_gray",
    "matlab_colormap_hot": "color_hot",
    "matlab_colormap_jet": "color_jet",
    "matlab_colormap_turbo": "color_turbo",
    "matlab_link_x": "link_x",
    "matlab_link_y": "link_y",
    "matlab_link_xy": "link_xy",
    "matlab_export_csv": "csv",
    "matlab_export_json": "json",
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
    "Color Scale": "colorbar",
    "Colormap": "color",
    "Link Axes": "link",
    "Export Data": "export",
    "Selection": "selection",
}
_SELECTION_REQUIRED_LABELS = {"Marker", "Line Style", "Color"}
_MAPPABLE_REQUIRED_LABELS = {"Color Scale", "Colormap"}
_MODE_BY_METHOD = {
    "matlab_none": "none",
    "matlab_pan": "pan",
    "matlab_zoom": "zoom",
    "matlab_rotate3d": "rotate3d",
    "matlab_data_cursor": "data_cursor",
    "matlab_select": "select",
    "matlab_brush": "brush",
}
_MARKER_BY_METHOD = {
    "matlab_marker_none": "None",
    "matlab_marker_circle": "o",
    "matlab_marker_square": "s",
    "matlab_marker_triangle": "^",
    "matlab_marker_x": "x",
    "matlab_marker_plus": "+",
    "matlab_marker_point": ".",
}
_LINESTYLE_BY_METHOD = {
    "matlab_line_solid": "-",
    "matlab_line_dashed": "--",
    "matlab_line_dashdot": "-.",
    "matlab_line_dotted": ":",
    "matlab_line_none": "None",
}
_COLOR_BY_METHOD = {
    "matlab_color_blue": "blue",
    "matlab_color_orange": "orange",
    "matlab_color_yellow": "yellow",
    "matlab_color_purple": "purple",
    "matlab_color_green": "green",
    "matlab_color_cyan": "cyan",
    "matlab_color_red": "red",
    "matlab_color_black": "black",
}
_COLORMAP_BY_METHOD = {
    "matlab_colormap_viridis": "viridis",
    "matlab_colormap_plasma": "plasma",
    "matlab_colormap_gray": "gray",
    "matlab_colormap_hot": "hot",
    "matlab_colormap_jet": "jet",
    "matlab_colormap_turbo": "turbo",
}
_COLOR_ICON_BY_KIND = {
    "color_blue": "#0072BD",
    "color_orange": "#D95319",
    "color_yellow": "#EDB120",
    "color_purple": "#7E2F8E",
    "color_green": "#77AC30",
    "color_cyan": "#4DBEEE",
    "color_red": "#A2142F",
    "color_black": "#000000",
    "color_viridis": "#440154",
    "color_plasma": "#9C179E",
    "color_gray": "#808080",
    "color_hot": "#FF6A00",
    "color_jet": "#0072BD",
    "color_turbo": "#24A884",
}
_MARKER_ICON_BY_KIND = {
    "marker_circle": "o",
    "marker_square": "s",
    "marker_triangle": "^",
    "marker_x": "x",
    "marker_plus": "+",
    "marker_point": ".",
}
_LINE_ICON_BY_KIND = {
    "line_solid": "-",
    "line_dashed": "--",
    "line_dashdot": "-.",
    "line_dotted": ":",
}


def draw_menu_icon_on_axes(ax, kind: str, *, disabled: bool = False) -> None:
    """Draw a menu icon into ``ax`` using 0..1 axes-fraction coordinates."""

    ax.set_axis_off()
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    cx = 0.5
    cy = 0.5
    left = 0.22
    right = 0.78
    top = 0.72
    bottom = 0.28
    accent = "#8f8f8f" if disabled else "#0072BD"
    base = "#8f8f8f" if disabled else "#111111"

    def add_line(xs, ys, *, color=base, width=None, style="-"):
        if width is None:
            width = 1.25 if disabled else 1.65
        line = Line2D(xs, ys, color=color, linewidth=width, linestyle=style, transform=ax.transAxes, clip_on=False)
        ax.add_line(line)
        return line

    def add_marker(x, y, marker, *, color=base, size=6.0, fill=None):
        face = "none" if fill == "none" else color if fill is None else fill
        line = Line2D(
            [x],
            [y],
            color=color,
            marker=marker,
            linestyle="None",
            markersize=size,
            markeredgecolor=color,
            markerfacecolor=face,
            markeredgewidth=1.35 if disabled else 1.75,
            transform=ax.transAxes,
            clip_on=False,
        )
        ax.add_line(line)
        return line

    def add_patch(x, y, width, height, *, face, edge, line=None):
        if line is None:
            line = 1.0 if disabled else 1.25
        patch = Rectangle(
            (x, y),
            width,
            height,
            transform=ax.transAxes,
            facecolor=face,
            edgecolor=edge,
            linewidth=line,
            clip_on=False,
        )
        ax.add_patch(patch)
        return patch

    def add_text(x, y, text, *, size=8, color=base):
        return ax.text(x, y, text, ha="center", va="center", fontsize=size, color=color, transform=ax.transAxes, clip_on=False)

    def draw_x(color=base):
        add_line([0.28, 0.72], [0.68, 0.32], color=color)
        add_line([0.28, 0.72], [0.32, 0.68], color=color)

    def draw_box():
        add_patch(0.24, 0.29, 0.52, 0.42, face="none", edge=base)

    def draw_swatch(color):
        add_patch(0.19, 0.27, 0.62, 0.46, face=color, edge="#5f5f5f", line=0.35)

    if kind.startswith("color_"):
        draw_swatch("#c8c8c8" if disabled else _COLOR_ICON_BY_KIND.get(kind, "#0072BD"))
    elif kind.startswith("marker_"):
        color = accent
        if kind == "marker_none":
            add_marker(cx, cy, "o", color=color, size=5.8, fill="none")
            add_line([0.20, 0.80], [0.20, 0.80], color=color)
        else:
            marker = _MARKER_ICON_BY_KIND.get(kind, "o")
            add_marker(cx, cy, marker, color=color, size=5.8, fill=color)
    elif kind.startswith("line_"):
        color = accent
        if kind == "line_none":
            draw_x(color)
        else:
            add_line([0.16, 0.84], [cy, cy], color=color, width=1.55 if disabled else 1.9, style=_LINE_ICON_BY_KIND.get(kind, "-"))
    elif kind == "none":
        add_marker(cx, cy, "o", color=base, size=6.2, fill="none")
        add_line([left, right], [bottom, top], color=base, width=1.0)
    elif kind in {"pointer", "select"}:
        add_line([left, right], [top, bottom])
        add_line([left, 0.48], [top, 0.70])
        add_line([left, 0.28], [top, 0.49])
    elif kind == "pan":
        add_line([left, right], [cy, cy])
        add_line([cx, cx], [bottom, top])
        add_line([left, 0.34], [cy, 0.58])
        add_line([left, 0.34], [cy, 0.42])
        add_line([right, 0.66], [cy, 0.58])
        add_line([right, 0.66], [cy, 0.42])
    elif kind == "zoom":
        add_marker(0.45, 0.54, "o", size=5.2, fill="none")
        add_line([0.62, right], [0.42, bottom])
    elif kind == "rotate":
        add_marker(cx, cy, "o", size=6.2, fill="none")
        add_line([0.64, right], [0.62, 0.70])
        add_line([right, 0.70], [0.70, 0.58])
    elif kind == "cursor":
        add_line([left, right], [cy, cy], width=0.9)
        add_line([cx, cx], [bottom, top], width=0.9)
    elif kind == "brush":
        add_patch(0.28, 0.38, 0.36, 0.24, face=accent, edge=accent, line=0.0)
        add_line([0.60, right], [0.48, bottom], color=accent)
    elif kind == "marker":
        add_marker(cx, cy, "o", color=accent, size=5.8, fill=accent)
    elif kind == "line":
        add_line([0.16, 0.84], [cy, cy], color=accent, width=1.55 if disabled else 1.9)
    elif kind == "color":
        draw_swatch(accent)
    elif kind in {"view", "view2", "view3", "box"}:
        draw_box()
    elif kind.startswith("axis"):
        add_line([left, left], [bottom, top])
        add_line([left, right], [bottom, bottom])
    elif kind == "display":
        draw_box()
        add_patch(0.38, 0.40, 0.24, 0.20, face=base, edge=base, line=0.0)
    elif kind == "grid":
        draw_box()
        add_line([cx, cx], [bottom, top], width=0.6)
        add_line([left, right], [cy, cy], width=0.6)
    elif kind == "legend":
        for y in (0.39, 0.50, 0.61):
            add_line([left, right], [y, y], width=0.8)
    elif kind == "colorbar":
        draw_swatch("#D95319")
    elif kind.startswith("link"):
        add_marker(0.38, cy, "o", size=4.2, fill="none")
        add_marker(0.62, cy, "o", size=4.2, fill="none")
        add_line([0.46, 0.54], [cy, cy], width=0.8)
    elif kind == "selection":
        draw_box()
        add_line([0.38, 0.48, 0.68], [cy, 0.38, 0.66], color=accent)
    elif kind == "visibility":
        add_marker(cx, cy, "o", size=6.0, fill="none")
        add_marker(cx, cy, "o", size=2.0)
    elif kind == "clear_selection":
        draw_x()
    elif kind == "delete":
        draw_x()
        add_line([left, right], [top, top], width=0.8)
    elif kind == "home":
        add_line([left, cx, right], [cy, top, cy])
        add_line([0.32, 0.32, 0.68, 0.68], [cy, bottom, bottom, cy])
    elif kind == "auto_view":
        draw_box()
        add_line([0.30, 0.70], [cy, cy], color=accent)
        add_line([cx, cx], [0.34, 0.66], color=accent)
    elif kind == "back":
        add_line([right, left, right], [top, cy, bottom], width=1.2)
    elif kind == "forward":
        add_line([left, right, left], [top, cy, bottom], width=1.2)
    elif kind == "hold":
        add_text(cx, cy, "H", size=8)
    elif kind == "export":
        add_line([0.30, 0.70], [0.34, 0.34], color=accent)
        add_line([cx, cx], [0.68, 0.40], color=accent)
        add_line([0.39, cx, 0.61], [0.51, 0.38, 0.51], color=accent)
    elif kind in {"csv", "json"}:
        add_text(cx, cy, "C" if kind == "csv" else "J", size=8, color=accent)


class MatplotlibContextMenuActions:
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

    def __init__(
        self,
        bridge: MatplotlibEventBridge | None,
        plotter: MatplotlibAxesPlotter,
        *,
        export_path_provider: Callable[[str, Any], str | Path | None] | None = None,
    ) -> None:
        self.bridge = bridge
        self.plotter = plotter
        self.export_path_provider = export_path_provider
        self.last_export_path: Path | None = None
        self.last_export_error: str | None = None

    def set_bridge(self, bridge: MatplotlibEventBridge) -> None:
        self.bridge = bridge

    def _require_bridge(self) -> MatplotlibEventBridge:
        if self.bridge is None:
            raise RuntimeError("Matplotlib context menu actions require a connected event bridge.")
        return self.bridge

    def matlab_none(self, *_args) -> None:
        self._require_bridge().set_mode("none")

    def matlab_pan(self, *_args) -> None:
        self._require_bridge().toggle_mode("pan")

    def matlab_zoom(self, *_args) -> None:
        self._require_bridge().toggle_mode("zoom")

    def matlab_rotate3d(self, *_args) -> None:
        self._require_bridge().toggle_mode("rotate3d")

    def matlab_data_cursor(self, *_args) -> None:
        self._require_bridge().toggle_mode("data_cursor")

    def matlab_select(self, *_args) -> None:
        self._require_bridge().toggle_mode("select")

    def matlab_brush(self, *_args) -> None:
        self._require_bridge().toggle_mode("brush")

    def matlab_home(self, *_args) -> None:
        self.plotter.home()

    def matlab_auto_view(self, *_args) -> None:
        self.plotter.auto_view()

    def matlab_back(self, *_args) -> None:
        self.plotter.back()

    def matlab_forward(self, *_args) -> None:
        self.plotter.forward()

    def matlab_view_2(self, *_args) -> None:
        self._require_bridge().apply_view(2)

    def matlab_view_3(self, *_args) -> None:
        self._require_bridge().apply_view(3)

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

    def matlab_clim_auto(self, *_args) -> None:
        self.plotter.clim("auto")

    def matlab_clim_set(self, *_args) -> None:
        axes = self.plotter.active_axes
        if axes is None:
            return
        current = self.plotter.clim()
        initial = "" if current is None else f"{current[0]}, {current[1]}"
        text = self._prompt_text("Set Color Limits", "Enter color limits as min,max:", initial)
        if text is None:
            return
        limits = self._parse_clim_text(text)
        if limits is None:
            return
        self.plotter.clim(limits)
        self._set_mappable_clim(axes, limits)

    def _set_mappable_clim(self, axes: Any, limits: tuple[float, float]) -> None:
        for artist in [*getattr(axes, "images", []), *getattr(axes, "collections", [])]:
            set_clim = getattr(artist, "set_clim", None)
            if callable(set_clim):
                set_clim(*limits)
        self.plotter._draw_idle(axes)

    def matlab_colormap_viridis(self, *_args) -> None:
        self._set_colormap("viridis")

    def matlab_colormap_plasma(self, *_args) -> None:
        self._set_colormap("plasma")

    def matlab_colormap_gray(self, *_args) -> None:
        self._set_colormap("gray")

    def matlab_colormap_hot(self, *_args) -> None:
        self._set_colormap("hot")

    def matlab_colormap_jet(self, *_args) -> None:
        self._set_colormap("jet")

    def matlab_colormap_turbo(self, *_args) -> None:
        self._set_colormap("turbo")

    def _set_colormap(self, name: str) -> None:
        axes = self.plotter.active_axes
        if axes is None:
            return
        self.plotter.colormap(name, axes=axes)

    def matlab_link_x(self, *_args) -> None:
        self.plotter.toggle_link_x_axes()

    def matlab_link_y(self, *_args) -> None:
        self.plotter.toggle_link_y_axes()

    def matlab_link_xy(self, *_args) -> None:
        self.plotter.toggle_link_xy_axes()

    def matlab_export_csv(self, *_args) -> Path | None:
        return self.export_data("csv")

    def matlab_export_json(self, *_args) -> Path | None:
        return self.export_data("json")

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

    def _parse_clim_text(self, text: str) -> tuple[float, float] | None:
        parts = [part.strip() for part in text.replace(";", ",").split(",") if part.strip()]
        if len(parts) != 2:
            return None
        try:
            lo, hi = (float(parts[0]), float(parts[1]))
        except ValueError:
            return None
        if lo == hi:
            return None
        return lo, hi

    def _prompt_text(self, title: str, label: str, initial: str = "") -> str | None:
        text, attempted = self._qt_prompt_text(title, label, initial)
        if attempted:
            return text
        text, attempted = self._tk_prompt_text(title, label, initial)
        if attempted:
            return text
        return None

    def _qt_prompt_text(self, title: str, label: str, initial: str = "") -> tuple[str | None, bool]:
        QtWidgets = self._qt_widgets_module()
        if QtWidgets is None:
            return None, False
        app = QtWidgets.QApplication.instance()
        if app is None:
            return None, False
        try:
            text, ok = QtWidgets.QInputDialog.getText(None, title, label, text=initial)
        except Exception:
            return None, False
        return (str(text) if ok else None), True

    def _tk_prompt_text(self, title: str, label: str, initial: str = "") -> tuple[str | None, bool]:
        try:
            tkinter = importlib.import_module("tkinter")
            simpledialog = importlib.import_module("tkinter.simpledialog")
        except Exception:
            return None, False
        root = None
        try:
            root = tkinter.Tk()
            root.withdraw()
            try:
                root.attributes("-topmost", True)
            except Exception:
                pass
            text = simpledialog.askstring(title, label, initialvalue=initial, parent=root)
        except Exception:
            return None, False
        finally:
            if root is not None:
                try:
                    root.destroy()
                except Exception:
                    pass
        return text, True

    def export_data(self, fmt: str, path: str | Path | None = None, axes: Any = None) -> Path | None:
        self.last_export_error = None
        self.last_export_path = None
        fmt = fmt.lower().strip()
        if fmt not in {"csv", "json"}:
            raise ValueError("export format must be 'csv' or 'json'")
        axes = axes if axes is not None else self.plotter.active_axes
        if axes is None:
            self.last_export_error = "No active axes to export."
            return None
        data = self.collect_axes_data(axes)
        if not data["artists"]:
            self.last_export_error = "No visible plotted data to export."
            return None
        export_path = self._resolve_export_path(fmt, path, axes)
        if export_path is None:
            self.last_export_error = "No export path selected."
            return None
        export_path.parent.mkdir(parents=True, exist_ok=True)
        if fmt == "csv":
            self._write_csv(export_path, data)
        else:
            export_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        self.last_export_path = export_path
        return export_path

    def collect_axes_data(self, axes: Any) -> dict[str, Any]:
        artists: list[dict[str, Any]] = []
        for index, line in enumerate(getattr(axes, "lines", []) or []):
            payload = self._line_payload(line, index)
            if payload is not None:
                artists.append(payload)
        for index, collection in enumerate(getattr(axes, "collections", []) or []):
            payload = self._collection_payload(collection, index)
            if payload is not None:
                artists.append(payload)
        for index, image in enumerate(getattr(axes, "images", []) or []):
            payload = self._image_payload(image, index)
            if payload is not None:
                artists.append(payload)
        for index, patch in enumerate(getattr(axes, "patches", []) or []):
            payload = self._patch_payload(patch, index)
            if payload is not None:
                artists.append(payload)
        title = ""
        get_title = getattr(axes, "get_title", None)
        if callable(get_title):
            title = str(get_title())
        return {"axes_title": title, "artist_count": len(artists), "artists": artists}

    def _resolve_export_path(self, fmt: str, path: str | Path | None, axes: Any) -> Path | None:
        if path is None and self.export_path_provider is not None:
            provided = self.export_path_provider(fmt, axes)
            if provided is None:
                return None
            path = provided
        if path is None:
            path, attempted = self._qt_save_file_path(fmt, axes)
            if attempted and path is None:
                self.last_export_error = "Save dialog was cancelled."
                return None
        if path is None:
            path, attempted = self._tk_save_file_path(fmt)
            if attempted and path is None:
                self.last_export_error = "Save dialog was cancelled."
                return None
        if path is None:
            self.last_export_error = "No GUI save dialog is available."
            return None
        export_path = Path(path)
        if export_path.suffix.lower() != f".{fmt}":
            export_path = export_path.with_suffix(f".{fmt}")
        return export_path

    def _default_export_path(self, fmt: str) -> Path:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return Path.cwd() / f"py_matlab_style_plotter_export_{stamp}.{fmt}"

    def _qt_save_file_path(self, fmt: str, axes: Any) -> tuple[Path | None, bool]:
        QtWidgets = self._qt_widgets_module()
        if QtWidgets is None:
            return None, False
        app = QtWidgets.QApplication.instance()
        figure = getattr(axes, "figure", None)
        canvas = getattr(figure, "canvas", None)
        parent = canvas if isinstance(canvas, QtWidgets.QWidget) else None
        if app is None and parent is None:
            return None, False
        default_path = self._default_export_path(fmt)
        if fmt == "csv":
            file_filter = "CSV files (*.csv);;All files (*)"
            title = "Export Plot Data as CSV"
        else:
            file_filter = "JSON files (*.json);;All files (*)"
            title = "Export Plot Data as JSON"
        try:
            selected, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
                parent,
                title,
                str(default_path),
                file_filter,
            )
        except Exception:
            return None, False
        return (Path(selected) if selected else None), True

    def _tk_save_file_path(self, fmt: str) -> tuple[Path | None, bool]:
        try:
            tkinter = importlib.import_module("tkinter")
            filedialog = importlib.import_module("tkinter.filedialog")
        except Exception:
            return None, False
        default_path = self._default_export_path(fmt)
        filetypes = [("CSV files", "*.csv"), ("All files", "*")] if fmt == "csv" else [("JSON files", "*.json"), ("All files", "*")]
        title = "Export Plot Data as CSV" if fmt == "csv" else "Export Plot Data as JSON"
        root = None
        try:
            root = tkinter.Tk()
            root.withdraw()
            try:
                root.attributes("-topmost", True)
            except Exception:
                pass
            selected = filedialog.asksaveasfilename(
                parent=root,
                title=title,
                initialdir=str(default_path.parent),
                initialfile=default_path.name,
                defaultextension=f".{fmt}",
                filetypes=filetypes,
            )
        except Exception:
            return None, False
        finally:
            if root is not None:
                try:
                    root.destroy()
                except Exception:
                    pass
        return (Path(selected) if selected else None), True

    def _qt_widgets_module(self) -> Any | None:
        for module_name in (
            "PySide6.QtWidgets",
            "PyQt6.QtWidgets",
            "PyQt5.QtWidgets",
            "PySide2.QtWidgets",
        ):
            module = sys.modules.get(module_name)
            if module is not None:
                return module
        try:
            from matplotlib.backends.qt_compat import QtWidgets

            return QtWidgets
        except Exception:
            pass
        for module_name in (
            "PySide6.QtWidgets",
            "PyQt6.QtWidgets",
            "PyQt5.QtWidgets",
            "PySide2.QtWidgets",
        ):
            try:
                return importlib.import_module(module_name)
            except Exception:
                continue
        return None

    def _line_payload(self, line: Any, index: int) -> dict[str, Any] | None:
        if not self._exportable_artist(line):
            return None
        data_3d = self._line_data_3d(line)
        if data_3d is not None:
            x_values, y_values, z_values = data_3d
        else:
            data = self.plotter.get_original_data(line)
            if data is None:
                get_xdata = getattr(line, "get_xdata", None)
                get_ydata = getattr(line, "get_ydata", None)
                if not callable(get_xdata) or not callable(get_ydata):
                    return None
                data = (get_xdata(), get_ydata())
            x_values, y_values = data[:2]
            z_values = None
        points = self._points_from_columns(x=x_values, y=y_values, z=z_values)
        if not points:
            return None
        return {"type": "line", "index": index, "label": self._artist_label(line), "points": points}

    def _line_data_3d(self, line: Any) -> tuple[Any, Any, Any] | None:
        get_data_3d = getattr(line, "get_data_3d", None)
        if callable(get_data_3d):
            try:
                data = get_data_3d()
            except (TypeError, ValueError):
                data = None
            if data is not None and len(data) >= 3:
                return data[0], data[1], data[2]
        get_zdata = getattr(line, "get_zdata", None)
        if not callable(get_zdata):
            return None
        try:
            z_values = get_zdata()
            get_xdata = getattr(line, "get_xdata", None)
            get_ydata = getattr(line, "get_ydata", None)
            if not callable(get_xdata) or not callable(get_ydata):
                return None
            return get_xdata(), get_ydata(), z_values
        except (TypeError, ValueError):
            return None

    def _collection_payload(self, collection: Any, index: int) -> dict[str, Any] | None:
        if not self._exportable_artist(collection):
            return None
        offsets3d = getattr(collection, "_offsets3d", None)
        if offsets3d is not None and len(offsets3d) >= 3:
            points = self._points_from_columns(x=offsets3d[0], y=offsets3d[1], z=offsets3d[2])
        else:
            get_offsets = getattr(collection, "get_offsets", None)
            if not callable(get_offsets):
                return None
            try:
                offsets = get_offsets()
            except (TypeError, ValueError):
                return None
            rows = self._as_rows(offsets)
            points = [
                {"point_index": point_index, "x": row[0], "y": row[1]}
                for point_index, row in enumerate(rows)
                if len(row) >= 2
            ]
        values = self._artist_array(collection)
        if values:
            for point, value in zip(points, values):
                point["value"] = value
        if not points:
            return None
        return {"type": "collection", "index": index, "label": self._artist_label(collection), "points": points}

    def _image_payload(self, image: Any, index: int) -> dict[str, Any] | None:
        if not self._exportable_artist(image):
            return None
        get_array = getattr(image, "get_array", None)
        if not callable(get_array):
            return None
        try:
            array = get_array()
        except (TypeError, ValueError):
            return None
        rows = self._as_rows(array)
        if not rows:
            return None
        extent = None
        get_extent = getattr(image, "get_extent", None)
        if callable(get_extent):
            try:
                extent = self._to_json_value(get_extent())
            except (TypeError, ValueError):
                extent = None
        points = []
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                points.append({"row": row_index, "column": column_index, "value": value})
        return {
            "type": "image",
            "index": index,
            "label": self._artist_label(image),
            "extent": extent,
            "points": points,
        }

    def _patch_payload(self, patch: Any, index: int) -> dict[str, Any] | None:
        if not self._exportable_artist(patch):
            return None
        get_xy = getattr(patch, "get_xy", None)
        get_width = getattr(patch, "get_width", None)
        get_height = getattr(patch, "get_height", None)
        if not callable(get_xy) or not callable(get_width) or not callable(get_height):
            return None
        try:
            xy = self._to_json_value(get_xy())
            width = self._to_json_value(get_width())
            height = self._to_json_value(get_height())
        except (TypeError, ValueError):
            return None
        return {
            "type": "patch",
            "index": index,
            "label": self._artist_label(patch),
            "points": [{"point_index": 0, "x": xy[0], "y": xy[1], "width": width, "height": height}],
        }

    def _write_csv(self, path: Path, data: dict[str, Any]) -> None:
        fields = [
            "artist_type",
            "artist_index",
            "label",
            "point_index",
            "x",
            "y",
            "z",
            "row",
            "column",
            "value",
            "width",
            "height",
        ]
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for artist in data["artists"]:
                for point in artist.get("points", []):
                    writer.writerow(
                        {
                            "artist_type": artist["type"],
                            "artist_index": artist["index"],
                            "label": artist.get("label", ""),
                            "point_index": point.get("point_index", ""),
                            "x": point.get("x", ""),
                            "y": point.get("y", ""),
                            "z": point.get("z", ""),
                            "row": point.get("row", ""),
                            "column": point.get("column", ""),
                            "value": point.get("value", ""),
                            "width": point.get("width", ""),
                            "height": point.get("height", ""),
                        }
                    )

    def _points_from_columns(self, **columns: Any) -> list[dict[str, Any]]:
        values = {name: self._as_flat_list(value) for name, value in columns.items() if value is not None}
        if "x" not in values or "y" not in values:
            return []
        lengths = [len(values["x"]), len(values["y"]), *(len(value) for name, value in values.items() if name not in {"x", "y"})]
        count = min(lengths)
        points = []
        for point_index in range(count):
            point = {"point_index": point_index}
            for name, value in values.items():
                point[name] = value[point_index]
            points.append(point)
        return points

    def _artist_array(self, artist: Any) -> list[Any]:
        get_array = getattr(artist, "get_array", None)
        if not callable(get_array):
            return []
        try:
            return self._as_flat_list(get_array())
        except (TypeError, ValueError):
            return []

    def _as_flat_list(self, value: Any) -> list[Any]:
        if hasattr(value, "compressed"):
            value = value.compressed()
        if hasattr(value, "ravel"):
            value = value.ravel()
        return [self._to_json_value(item) for item in list(value)]

    def _as_rows(self, value: Any) -> list[list[Any]]:
        if hasattr(value, "tolist"):
            value = value.tolist()
        if not isinstance(value, list):
            value = list(value)
        rows = []
        for row in value:
            if hasattr(row, "tolist"):
                row = row.tolist()
            if isinstance(row, (list, tuple)):
                rows.append([self._to_json_value(item) for item in row])
            else:
                rows.append([self._to_json_value(row)])
        return rows

    def _to_json_value(self, value: Any) -> Any:
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, tuple):
            return [self._to_json_value(item) for item in value]
        if isinstance(value, list):
            return [self._to_json_value(item) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    def _artist_label(self, artist: Any) -> str:
        get_label = getattr(artist, "get_label", None)
        if not callable(get_label):
            return ""
        label = str(get_label())
        return "" if label.startswith("_") else label

    def _exportable_artist(self, artist: Any) -> bool:
        if not self._artist_visible(artist):
            return False
        get_label = getattr(artist, "get_label", None)
        if not callable(get_label):
            return True
        label = str(get_label())
        return not label.startswith(("_matlab", "_py_matlab"))

    def _artist_visible(self, artist: Any) -> bool:
        get_visible = getattr(artist, "get_visible", None)
        if not callable(get_visible):
            return True
        return bool(get_visible())

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
            self._refresh_existing_legend(axes)
            self.plotter._draw_idle(axes)

    def _target_lines(self):
        return [state.line for state in self.plotter.selected_lines]

    def _refresh_existing_legend(self, axes) -> None:
        legend = getattr(axes, "get_legend", lambda: None)()
        if legend is None:
            return
        loc = getattr(legend, "_loc", None)
        remove = getattr(legend, "remove", None)
        if remove is not None:
            remove()
        legend_func = getattr(axes, "legend", None)
        if legend_func is None:
            return
        if loc is None:
            legend_func()
        else:
            legend_func(loc=loc)


class MatplotlibContextMenu:
    """Figure-level context menu that does not create Matplotlib Axes."""

    def __init__(
        self,
        fig,
        plotter: MatplotlibAxesPlotter,
        actions: MatplotlibContextMenuActions | None = None,
    ) -> None:
        self.fig = fig
        self.plotter = plotter
        self.actions = actions if actions is not None else MatplotlibContextMenuActions(None, plotter)
        self._artists = []
        self._items = []
        self._submenu_parent = None
        self._hover_patch = None

    def open(self, x: float, y: float, axes) -> None:
        """Open the figure-level menu at figure coordinates ``x``/``y``."""

        self.close()
        self.plotter.set_active_axes(axes)
        self._draw_menu(_MATLAB_MENU_ITEMS, x, y, level=0)
        self.fig.canvas.draw_idle()

    def _open(self, x: float, y: float, axes) -> None:
        self.open(x, y, axes)

    def build_menu_model(self) -> list[dict]:
        return self._build_model_items(_MATLAB_MENU_ITEMS)

    def _build_model_items(self, items) -> list[dict]:
        model = []
        for item in items:
            if item is None:
                model.append({"kind": "separator"})
                continue
            label, action_or_submenu = item
            enabled = not self._is_disabled_item(label, action_or_submenu)
            if isinstance(action_or_submenu, tuple):
                model.append(
                    {
                        "kind": "submenu",
                        "label": label,
                        "enabled": enabled,
                        "icon_kind": _MENU_ICON_BY_LABEL.get(label),
                        "items": self._build_model_items(action_or_submenu),
                    }
                )
            else:
                method_name = action_or_submenu
                model.append(
                    {
                        "kind": "action",
                        "label": label,
                        "method": method_name,
                        "enabled": enabled,
                        "checked": self._is_checked_method(method_name),
                        "icon_kind": _MENU_ICON_BY_METHOD.get(method_name),
                    }
                )
        return model

    def close(self, *, ignore_remove_errors: bool = False) -> None:
        if not self._artists:
            return
        for artist in list(self._artists):
            try:
                artist.remove()
            except (ValueError, RuntimeError, NotImplementedError):
                if not ignore_remove_errors:
                    raise
        self._artists.clear()
        self._items.clear()
        self._submenu_parent = None
        self._hover_patch = None
        self.fig.canvas.draw_idle()

    def _draw_menu(self, items, x: float, y: float, *, level: int, parent_patch=None) -> None:
        entries = list(items)
        row_height = 0.0243
        separator_height = 0.0054
        check_width = 0.010
        padding_x = 0.006
        icon_width = 0.0145
        icon_x = padding_x + check_width + 0.001
        text_x = icon_x + icon_width + 0.0035
        arrow_padding = 0.006
        padding_y = 0.0036
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
                    0.0009,
                    face="#d0d0d0",
                    edge="#d0d0d0",
                    line=0.0,
                    z=20_002 + level * 100,
                )
                current_y -= separator_height
                continue
            label, action_or_submenu = item
            item_y = current_y - row_height
            disabled = self._is_disabled_item(label, action_or_submenu)
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
                size=7.2,
                color="#9a9a9a" if disabled else "#1f1f1f",
                z=20_003 + level * 100,
            )
            submenu = action_or_submenu if isinstance(action_or_submenu, tuple) else None
            method_name = None if submenu is not None else action_or_submenu
            icon_kind = _MENU_ICON_BY_LABEL.get(label) if submenu is not None else _MENU_ICON_BY_METHOD.get(action_or_submenu)
            if icon_kind is not None:
                self._draw_menu_icon(icon_kind, x + icon_x, item_y + row_height / 2, icon_width, row_height, level, disabled=disabled)
            if method_name is not None and self._is_checked_method(method_name):
                self._draw_check_mark(x + padding_x, item_y + row_height / 2, check_width, row_height, 20_004 + level * 100)
            if submenu is not None:
                self._add_text(
                    x + menu_width - arrow_padding,
                    item_y + row_height / 2,
                    ">",
                    ha="right",
                    size=7.2,
                    color="#b0b0b0" if disabled else "#404040",
                    z=20_003 + level * 100,
                )
            else:
                self._draw_menu_sample(action_or_submenu, x, item_y, menu_width, row_height, level, disabled=disabled)
            self._items.append(
                {
                    "patch": patch,
                    "method": method_name,
                    "submenu": submenu,
                    "disabled": disabled,
                    "level": level,
                    "parent": parent_patch,
                    "menu_x": x,
                    "menu_y": y - menu_height,
                    "menu_width": menu_width,
                    "menu_height": menu_height,
                }
            )
            current_y -= row_height

    def _draw_menu_sample(self, method_name: str, x: float, y: float, width: float, height: float, level: int, *, disabled: bool = False):
        sample_x = x + width - 0.022
        sample_y = y + height / 2
        color_value = "#9a9a9a" if disabled else "#202020"
        if method_name.startswith("matlab_color_"):
            color_name = method_name.removeprefix("matlab_color_")
            color = "#c8c8c8" if disabled else self.actions._COLORS.get(color_name)
            if color is not None:
                self._add_patch(
                    sample_x,
                    sample_y - 0.0054,
                    0.020,
                    0.0108,
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
                self._add_text(sample_x, sample_y, line_text, ha="left", size=8, color=color_value, z=20_004 + level * 100)
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
                self._add_text(sample_x + 0.010, sample_y, marker_text, ha="center", size=9, color=color_value, z=20_004 + level * 100)

    def _draw_menu_icon(self, kind: str, x: float, y: float, width: float, height: float, level: int, *, disabled: bool = False) -> None:
        cx = x + width / 2
        z = 20_004 + level * 100
        left = x + width * 0.22
        right = x + width * 0.78
        top = y + height * 0.22
        bottom = y - height * 0.22
        accent = "#9a9a9a" if disabled else "#0072BD"
        base = "#9a9a9a" if disabled else "#202020"
        if kind.startswith("color_"):
            self._draw_color_icon(kind, x, y, width, height, z, disabled=disabled)
            return
        if kind.startswith("marker_"):
            self._draw_marker_icon(kind, cx, y, z, disabled=disabled)
            return
        if kind.startswith("line_"):
            self._draw_line_icon(kind, x, y, width, z, disabled=disabled)
            return
        if kind == "none":
            self._add_marker(cx, y, "o", color=base, size=6.2, z=z, fill="none")
            self._add_line([left, right], [bottom, top], color=base, width=1.0, z=z)
        elif kind in {"pointer", "select"}:
            self._add_line([left, right], [top, bottom], color=base, width=1.0, z=z)
            self._add_line([left, left + width * 0.26], [top, top - height * 0.02], color=base, width=1.0, z=z)
            self._add_line([left, left + width * 0.06], [top, top - height * 0.23], color=base, width=1.0, z=z)
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
            self._draw_line_icon("line_solid", x, y, width, z, disabled=disabled)
        elif kind == "color":
            self._draw_color_swatch(x, y, width, height, accent, z)
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
        elif kind == "auto_view":
            self._draw_outline_box(x, y, width, height, z)
            self._add_line([cx - width * 0.20, cx + width * 0.20], [y, y], color=accent, width=1.0, z=z)
            self._add_line([cx, cx], [y - height * 0.18, y + height * 0.18], color=accent, width=1.0, z=z)
        elif kind == "back":
            self._add_line([right, left, right], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "forward":
            self._add_line([left, right, left], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "hold":
            self._add_text(cx, y, "H", ha="center", size=8, color="#202020", z=z)
        elif kind == "export":
            self._add_line([cx - width * 0.20, cx + width * 0.20], [y - height * 0.18, y - height * 0.18], color=accent, width=1.0, z=z)
            self._add_line([cx, cx], [y + height * 0.20, y - height * 0.06], color=accent, width=1.0, z=z)
            self._add_line([cx - width * 0.10, cx, cx + width * 0.10], [y + height * 0.04, y - height * 0.08, y + height * 0.04], color=accent, width=1.0, z=z)
        elif kind in {"csv", "json"}:
            self._add_text(cx, y, "C" if kind == "csv" else "J", ha="center", size=8, color=accent, z=z)

    def _draw_marker_icon(self, kind: str, x: float, y: float, z: int, *, disabled: bool = False) -> None:
        color = "#9a9a9a" if disabled else "#0072BD"
        if kind == "marker_none":
            self._add_marker(x, y, "o", color=color, size=5.8, z=z, fill="none")
            self._add_line([x - 0.006, x + 0.006], [y - 0.006, y + 0.006], color=color, width=1.0, z=z)
            return
        marker = _MARKER_ICON_BY_KIND.get(kind, "o")
        self._add_marker(x, y, marker, color=color, size=5.8, z=z, fill=color)

    def _draw_line_icon(self, kind: str, x: float, y: float, width: float, z: int, *, disabled: bool = False) -> None:
        color = "#9a9a9a" if disabled else "#0072BD"
        if kind == "line_none":
            self._draw_x_icon(x, y, width, width, z, color=color)
            return
        style = _LINE_ICON_BY_KIND.get(kind, "-")
        self._add_line([x + width * 0.16, x + width * 0.84], [y, y], color=color, width=1.4, z=z, style=style)

    def _draw_color_icon(self, kind: str, x: float, y: float, width: float, height: float, z: int, *, disabled: bool = False) -> None:
        color = _COLOR_ICON_BY_KIND.get(kind, "#0072BD")
        if disabled:
            color = "#c8c8c8"
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

    def _draw_check_mark(self, x: float, y: float, width: float, height: float, z: int) -> None:
        left = x + width * 0.18
        mid = x + width * 0.42
        right = x + width * 0.82
        bottom = y - height * 0.05
        top = y + height * 0.14
        check = self._add_line([left, mid, right], [y, bottom, top], color="#0072BD", width=1.1, z=z)
        check.set_gid("_py_matlab_style_context_menu_check")

    def _is_checked_method(self, method_name: str) -> bool:
        mode = _MODE_BY_METHOD.get(method_name)
        if mode is not None:
            current = str(getattr(self.plotter.mode, "value", self.plotter.mode))
            return current == mode
        status = self._display_or_link_checked(method_name)
        if status is not None:
            return status
        if method_name in _MARKER_BY_METHOD:
            return self._selected_lines_have_value("get_marker", _MARKER_BY_METHOD[method_name], self._normalize_none_style)
        if method_name in _LINESTYLE_BY_METHOD:
            return self._selected_lines_have_value("get_linestyle", _LINESTYLE_BY_METHOD[method_name], self._normalize_line_style)
        color_name = _COLOR_BY_METHOD.get(method_name)
        if color_name is not None:
            return self._selected_lines_have_value("get_color", self.actions._COLORS[color_name], self._normalize_color)
        colormap_name = _COLORMAP_BY_METHOD.get(method_name)
        if colormap_name is not None:
            return self._current_colormap_name() == colormap_name
        return False

    def _display_or_link_checked(self, method_name: str) -> bool | None:
        axes = self.plotter.active_axes
        if method_name == "matlab_hold":
            return bool(self.plotter.hold_enabled)
        if axes is None:
            return False
        if method_name == "matlab_grid":
            return bool(self.plotter.grid_is_enabled(axes))
        if method_name == "matlab_legend":
            return bool(self.plotter.legend_is_enabled(axes))
        if method_name == "matlab_box":
            return bool(self.plotter.box_is_enabled(axes))
        if method_name == "matlab_colorbar":
            return bool(self.plotter.colorbar_is_enabled(axes))
        if method_name == "matlab_link_x":
            return bool(self.plotter.linked_axes_state.get("x"))
        if method_name == "matlab_link_y":
            return bool(self.plotter.linked_axes_state.get("y"))
        if method_name == "matlab_link_xy":
            return bool(self.plotter.linked_axes_state.get("xy"))
        return None

    def _selected_lines_have_value(self, getter_name: str, expected: Any, normalizer) -> bool:
        lines = self.actions._target_lines()
        if len(lines) != 1:
            return False
        getter = getattr(lines[0], getter_name, None)
        if getter is None:
            return False
        return normalizer(getter()) == normalizer(expected)

    def _normalize_none_style(self, value: Any) -> str:
        text = str(value)
        return "None" if text.lower() in {"none", "", " "} else text

    def _normalize_line_style(self, value: Any) -> str:
        text = self._normalize_none_style(value)
        aliases = {"solid": "-", "dashed": "--", "dashdot": "-.", "dotted": ":"}
        return aliases.get(text.lower(), text)

    def _normalize_color(self, value: Any) -> tuple[float, ...] | str:
        try:
            from matplotlib.colors import to_rgba

            return tuple(round(float(channel), 3) for channel in to_rgba(value))
        except (TypeError, ValueError):
            return str(value)

    def _is_disabled_item(self, label: str, action_or_submenu) -> bool:
        if label in _SELECTION_REQUIRED_LABELS and not self.plotter.selected_lines:
            return True
        if label in _MAPPABLE_REQUIRED_LABELS and not self._has_mappable(self.plotter.active_axes):
            return True
        return False

    def _has_mappable(self, axes: Any) -> bool:
        if axes is None:
            return False
        return bool(getattr(axes, "images", []) or getattr(axes, "collections", []))

    def _current_colormap_name(self) -> str | None:
        axes = self.plotter.active_axes
        if axes is None:
            return None
        for artist in [*getattr(axes, "images", []), *getattr(axes, "collections", [])]:
            get_cmap = getattr(artist, "get_cmap", None)
            if not callable(get_cmap):
                continue
            cmap = get_cmap()
            name = getattr(cmap, "name", None)
            if name:
                return str(name).lower()
        return None

    def _menu_width(self, entries) -> float:
        labels = [item[0] for item in entries if item is not None]
        longest = max((len(label) for label in labels), default=8)
        has_submenu = any(item is not None and isinstance(item[1], tuple) for item in entries)
        has_sample = any(item is not None and not isinstance(item[1], tuple) and str(item[1]).startswith(("matlab_marker_", "matlab_line_", "matlab_color_")) for item in entries)
        right_space = 0.018 if has_submenu else 0.0
        if has_sample:
            right_space = max(right_space, 0.029)
        return max(0.083, min(0.155, 0.043 + longest * 0.0052 + right_space))

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
        is_axes_right_click = event.inaxes is not None and self._is_right_click(getattr(event, "button", None))
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
                    if item.get("disabled", False):
                        self.fig.canvas.draw_idle()
                        return True
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
            if is_axes_right_click:
                self._prepare_context_selection(event)
                self._open(float(figure_xy[0]), float(figure_xy[1]), event.inaxes)
                return True
            self.close()
            return True
        if not is_axes_right_click:
            return False
        self._prepare_context_selection(event)
        self._open(float(figure_xy[0]), float(figure_xy[1]), event.inaxes)
        return True

    def _prepare_context_selection(self, event) -> None:
        if self.plotter.selected_lines:
            return
        axes = getattr(event, "inaxes", None)
        xdata = getattr(event, "xdata", None)
        ydata = getattr(event, "ydata", None)
        if axes is None:
            return
        for line in getattr(axes, "lines", []):
            if not self.plotter._line_is_pickable(line):
                continue
            contains = getattr(line, "contains", None)
            if contains is None:
                continue
            try:
                hit, _details = contains(event)
            except (AttributeError, TypeError, ValueError):
                continue
            if hit:
                self.plotter.select_line(line)
                self.plotter._draw_idle(axes)
                return
        if xdata is None or ydata is None:
            return
        try:
            if not self.plotter._is_finite_pair(float(xdata), float(ydata)):
                return
        except (TypeError, ValueError):
            return
        nearest = self.plotter.find_nearest_line_point(axes, float(xdata), float(ydata))
        if nearest is None:
            return
        line, _index, point_x, point_y, _point_z = nearest
        if self.plotter._normalized_point_distance(axes, point_x, point_y, float(xdata), float(ydata)) > self.plotter.selection_pick_tolerance:
            return
        self.plotter.select_line(line)
        self.plotter._draw_idle(axes)

    def _is_right_click(self, button) -> bool:
        if button == 3:
            return True
        name = getattr(button, "name", str(button)).lower()
        return name in {"right", "button3", "mousebutton.right"}


class MatplotlibContextMenuEventBridge(MatplotlibEventBridge):
    def __init__(
        self,
        plotter: MatplotlibAxesPlotter,
        canvas: Any | None = None,
        context_menu: MatplotlibContextMenu | None = None,
    ) -> None:
        if isinstance(canvas, MatplotlibContextMenu) and context_menu is None:
            context_menu = canvas
            canvas = None
        if context_menu is None:
            raise TypeError("context_menu is required")
        super().__init__(plotter, canvas)
        self.context_menu = context_menu
        self.context_menu.actions.set_bridge(self)

    def _on_button_press(self, event) -> None:
        if self.context_menu._on_press(event):
            return
        super()._on_button_press(event)
