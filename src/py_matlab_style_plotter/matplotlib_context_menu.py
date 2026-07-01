"""MATLAB-style Matplotlib figure context menu."""

from __future__ import annotations

from typing import Any

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
_SELECTION_REQUIRED_LABELS = {"Marker", "Line Style", "Color"}
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
_COLOR_ICON_BY_KIND = {
    "color_blue": "#0072BD",
    "color_orange": "#D95319",
    "color_yellow": "#EDB120",
    "color_purple": "#7E2F8E",
    "color_green": "#77AC30",
    "color_cyan": "#4DBEEE",
    "color_red": "#A2142F",
    "color_black": "#000000",
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
    elif kind == "back":
        add_line([right, left, right], [top, cy, bottom], width=1.2)
    elif kind == "forward":
        add_line([left, right, left], [top, cy, bottom], width=1.2)
    elif kind == "hold":
        add_text(cx, cy, "H", size=8)


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

    def __init__(self, bridge: MatplotlibEventBridge | None, plotter: MatplotlibAxesPlotter) -> None:
        self.bridge = bridge
        self.plotter = plotter

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
        elif kind == "back":
            self._add_line([right, left, right], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "forward":
            self._add_line([left, right, left], [top, y, bottom], color="#202020", width=1.2, z=z)
        elif kind == "hold":
            self._add_text(cx, y, "H", ha="center", size=8, color="#202020", z=z)

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
        return False

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
                self._open(float(figure_xy[0]), float(figure_xy[1]), event.inaxes)
                return True
            self.close()
            return True
        if not is_axes_right_click:
            return False
        self._open(float(figure_xy[0]), float(figure_xy[1]), event.inaxes)
        return True

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
