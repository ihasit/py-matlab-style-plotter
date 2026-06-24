"""Matplotlib adapter for the MATLAB-like axes interaction base."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any

from .interaction import (
    AreaSeries,
    AspectMode,
    AxesLimits,
    AxisDirection,
    AxisLayer,
    AxisScale,
    BoxAspectMode,
    Camera3DState,
    CameraProjection,
    BarSeries,
    ConstantLineSeries,
    ErrorBarSeries,
    FillSeries,
    HistogramSeries,
    MatlabLikeAxesBase,
    Plot3Series,
    PlotSeries,
    ScatterSeries,
    StemSeries,
    TextSeries,
    TickDirection,
    XAxisLocation,
    YAxisLocation,
)


@dataclass(frozen=True)
class DataTip:
    """A fixed data cursor annotation."""

    axes: Any
    line: Any
    annotation: Any
    x: float
    y: float
    index: int
    label: str
    z: float | None = None


@dataclass(frozen=True)
class SelectedLineState:
    """Original visual state for a selected line."""

    line: Any
    linewidth: float
    alpha: float | None
    zorder: float
    visible: bool


@dataclass(frozen=True)
class CoordinateReadout:
    """Current pointer coordinate readout."""

    axes: Any
    x: float
    y: float
    text: str
    z: float | None = None


@dataclass(frozen=True)
class SpineStyle:
    """Original visual state for one axes spine."""

    edgecolor: Any
    linewidth: float


@dataclass(frozen=True)
class ActiveAxesStyle:
    """Original spine styles for the highlighted active axes."""

    axes: Any
    spines: dict[str, SpineStyle]


class MatplotlibAxesPlotter(MatlabLikeAxesBase):
    """MATLAB-like interaction wrapper around a Matplotlib ``Axes`` object."""

    def __init__(self, axes: Any | None = None) -> None:
        super().__init__(axes)
        self._zoom_box_artist: Any | None = None
        self._brush_box_artist: Any | None = None
        self.data_tips: list[DataTip] = []
        self.selected_lines: list[SelectedLineState] = []
        self.coordinate_readout: CoordinateReadout | None = None
        self.active_axes_style: ActiveAxesStyle | None = None
        self.linked_axes_state = {"x": False, "y": False, "xy": False}
        self.x_axes_linked = False
        self.selection_pick_tolerance = 0.05
        self.data_tip_pick_tolerance = 0.05
        self.coordinate_readout_z_tolerance = 0.05
        self.tick_length_points_per_unit = 350.0
        if axes is not None:
            self.on_active_axes_changed(axes)

    def draw_plot_series(self, axes: Any, series: list[PlotSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            if item.style is None or item.line_spec:
                created = axes.plot(item.x, item.y, **kwargs)
            else:
                created = axes.plot(item.x, item.y, item.style, **kwargs)
            artists.extend(created if isinstance(created, list) else list(created))
        self._draw_idle(axes)
        return artists

    def draw_plot3_series(self, axes: Any, series: list[Plot3Series]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            if item.style is None or item.line_spec:
                created = axes.plot(item.x, item.y, item.z, **kwargs)
            else:
                created = axes.plot(item.x, item.y, item.z, item.style, **kwargs)
            artists.extend(created if isinstance(created, list) else list(created))
        self._draw_idle(axes)
        return artists

    def draw_errorbar_series(self, axes: Any, series: list[ErrorBarSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            yerr = (item.y_negative, item.y_positive)
            created = axes.errorbar(item.x, item.y, yerr=yerr, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_scatter_series(self, axes: Any, series: list[ScatterSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            color = item.color if item.color is not None else kwargs.get("color")
            kwargs.pop("color", None)
            kwargs.pop("linestyle", None)
            if item.size is not None:
                kwargs.setdefault("s", item.size)
            if color is not None:
                kwargs.setdefault("c", color)
            created = axes.scatter(item.x, item.y, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_stem_series(self, axes: Any, series: list[StemSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            style = item.style if item.style is not None and not item.line_spec else None
            if style is None:
                created = axes.stem(item.x, item.y, **kwargs)
            else:
                created = axes.stem(item.x, item.y, style, **kwargs)
            if isinstance(created, tuple):
                artists.extend(created)
            else:
                artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_bar_series(self, axes: Any, series: list[BarSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            kwargs.pop("marker", None)
            kwargs.pop("linestyle", None)
            created = axes.bar(item.x, item.y, **kwargs)
            try:
                artists.extend(created)
            except TypeError:
                artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_area_series(self, axes: Any, series: list[AreaSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            color = kwargs.get("color")
            kwargs.pop("marker", None)
            kwargs.pop("linestyle", None)
            if color is not None:
                kwargs.setdefault("facecolor", color)
            created = axes.fill_between(item.x, item.baseline, item.y, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_fill_series(self, axes: Any, series: list[FillSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            if "color" in kwargs and "facecolor" not in kwargs:
                kwargs["facecolor"] = kwargs.pop("color")
            created = axes.fill(item.x, item.y, **kwargs)
            artists.extend(created if isinstance(created, list) else list(created))
        self._draw_idle(axes)
        return artists

    def draw_histogram_series(self, axes: Any, series: list[HistogramSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            if "facecolor" in kwargs and "color" not in kwargs:
                kwargs["color"] = kwargs.pop("facecolor")
            if item.bins is not None:
                kwargs.setdefault("bins", item.bins)
            counts, bins, patches = axes.hist(item.values, **kwargs)
            artists.append((counts, bins, patches))
        self._draw_idle(axes)
        return artists

    def draw_constant_line_series(self, axes: Any, series: list[ConstantLineSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            if item.label is not None:
                kwargs.setdefault("label", item.label)
            if item.orientation == "x":
                created = axes.axvline(item.value, **kwargs)
            else:
                created = axes.axhline(item.value, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_text_series(self, axes: Any, series: list[TextSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = dict(item.properties)
            value = "\n".join(item.text)
            if item.z is None:
                created = axes.text(item.x, item.y, value, **kwargs)
            else:
                created = axes.text(item.x, item.y, item.z, value, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def is_axes_handle(self, value: Any) -> bool:
        return all(hasattr(value, name) for name in ("plot", "get_xlim", "get_ylim"))

    def clear_children(self, axes: Any, reset_properties: bool) -> None:
        self.clear_axes_interaction_state(axes)
        if reset_properties:
            highlighted = self.active_axes_style is not None and self.active_axes_style.axes is axes
            if highlighted:
                self.restore_active_axes_highlight()
            axes.cla()
            if highlighted and self.active_axes is axes:
                self.apply_active_axes_highlight(axes)
            return
        for artist in list(axes.lines) + list(axes.collections) + list(axes.images) + list(axes.patches):
            artist.remove()

    def clear_axes_interaction_state(self, axes: Any) -> None:
        self.clear_data_tips(axes)
        self.clear_selection(axes)
        if self.coordinate_readout is not None and self.coordinate_readout.axes is axes:
            self.clear_coordinate_readout()
        if getattr(self._zoom_box_artist, "axes", None) is axes:
            self.end_zoom_box()
        if getattr(self._brush_box_artist, "axes", None) is axes:
            self.end_brush_box()

    def reset_axes_properties(self, axes: Any) -> None:
        self.set_aspect(axes, "auto")
        self.set_box_aspect(axes, "auto")
        self.set_axis_visible(axes, True)
        self.set_y_direction(axes, "normal")

    def get_limits(self, axes: Any) -> AxesLimits:
        zlim = tuple(axes.get_zlim()) if self.is_3d_axes(axes) else None
        clim = tuple(axes.get_clim()) if hasattr(axes, "get_clim") else None
        return AxesLimits(tuple(axes.get_xlim()), tuple(axes.get_ylim()), zlim, clim)

    def set_limits(self, axes: Any, limits: AxesLimits) -> None:
        axes.set_xlim(*limits.xlim)
        axes.set_ylim(*limits.ylim)
        if limits.zlim is not None and self.is_3d_axes(axes):
            axes.set_zlim(*limits.zlim)
        if limits.clim is not None and hasattr(axes, "set_clim"):
            axes.set_clim(*limits.clim)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def autoscale_axes(self, axes: Any, tight: bool = False) -> None:
        axes.relim()
        axes.autoscale_view(tight=tight)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def autoscale_clim(self, axes: Any) -> None:
        for artist in [*getattr(axes, "images", []), *getattr(axes, "collections", [])]:
            autoscale = getattr(artist, "autoscale", None)
            if autoscale is not None:
                autoscale()
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_aspect(self, axes: Any, aspect: AspectMode) -> None:
        axes.set_aspect("equal" if aspect == "equal" else "auto")
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_box_aspect(self, axes: Any, box_aspect: BoxAspectMode) -> None:
        if not hasattr(axes, "set_box_aspect"):
            return
        fixed_aspect = (1, 1, 1) if self.is_3d_axes(axes) else 1
        axes.set_box_aspect(fixed_aspect if box_aspect in {"square", "vis3d"} else None)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_data_aspect_ratio(self, axes: Any, ratio: tuple[float, float, float]) -> None:
        axes.set_aspect(ratio)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_plot_box_aspect_ratio(self, axes: Any, ratio: tuple[float, float, float]) -> None:
        if not hasattr(axes, "set_box_aspect"):
            return
        axes.set_box_aspect(ratio)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_axis_visible(self, axes: Any, visible: bool) -> None:
        if visible:
            axes.set_axis_on()
        else:
            axes.set_axis_off()
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_x_direction(self, axes: Any, direction: AxisDirection) -> None:
        self._apply_axis_direction(axes, "x", direction)

    def set_y_direction(self, axes: Any, direction: AxisDirection) -> None:
        self._apply_axis_direction(axes, "y", direction)

    def set_z_direction(self, axes: Any, direction: AxisDirection) -> None:
        self._apply_axis_direction(axes, "z", direction)

    def _apply_axis_direction(self, axes: Any, axis: str, direction: AxisDirection) -> None:
        inverted = bool(getattr(axes, f"{axis}axis_inverted", lambda: False)())
        should_invert = direction == "reverse"
        if inverted != should_invert:
            invert = getattr(axes, f"invert_{axis}axis", None)
            if invert is not None:
                invert()
            else:
                setattr(axes, f"{axis}_direction", direction)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_axis_scale(self, axes: Any, axis: str, scale: AxisScale) -> None:
        setter = getattr(axes, f"set_{axis}scale", None)
        if setter is None:
            super().set_axis_scale(axes, axis, scale)  # type: ignore[arg-type]
        else:
            setter(scale)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_axis_layer(self, axes: Any, layer: AxisLayer) -> None:
        setter = getattr(axes, "set_axisbelow", None)
        if setter is None:
            super().set_axis_layer(axes, layer)
        else:
            setter(layer == "bottom")
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_tick_direction(self, axes: Any, direction: TickDirection) -> None:
        tick_params = getattr(axes, "tick_params", None)
        if tick_params is None:
            super().set_tick_direction(axes, direction)
        else:
            tick_params(direction=direction)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_tick_length(self, axes: Any, tick_length: tuple[float, float]) -> None:
        tick_params = getattr(axes, "tick_params", None)
        if tick_params is None:
            super().set_tick_length(axes, tick_length)
        else:
            tick_params(which="major", length=abs(tick_length[0]) * self.tick_length_points_per_unit)
            tick_params(which="minor", length=abs(tick_length[1]) * self.tick_length_points_per_unit)
        self._draw_idle(axes)

    def set_x_axis_location(self, axes: Any, location: XAxisLocation) -> None:
        if not self._set_matplotlib_x_axis_location(axes, location):
            super().set_x_axis_location(axes, location)
        self._draw_idle(axes)

    def set_y_axis_location(self, axes: Any, location: YAxisLocation) -> None:
        if not self._set_matplotlib_y_axis_location(axes, location):
            super().set_y_axis_location(axes, location)
        self._draw_idle(axes)

    def get_ticks(self, axes: Any, axis: str) -> tuple[float, ...]:
        getter = getattr(axes, f"get_{axis}ticks", None)
        if getter is None:
            return super().get_ticks(axes, axis)  # type: ignore[arg-type]
        return tuple(float(item) for item in getter())

    def set_ticks(self, axes: Any, axis: str, ticks: tuple[float, ...]) -> None:
        setter = getattr(axes, f"set_{axis}ticks", None)
        if setter is None:
            super().set_ticks(axes, axis, ticks)  # type: ignore[arg-type]
        else:
            setter(ticks)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def get_ticklabels(self, axes: Any, axis: str) -> tuple[str, ...]:
        getter = getattr(axes, f"get_{axis}ticklabels", None)
        if getter is None:
            return super().get_ticklabels(axes, axis)  # type: ignore[arg-type]
        labels = []
        for label in getter():
            get_text = getattr(label, "get_text", None)
            labels.append(str(get_text() if get_text is not None else label))
        return tuple(labels)

    def set_ticklabels(self, axes: Any, axis: str, labels: tuple[str, ...]) -> None:
        setter = getattr(axes, f"set_{axis}ticklabels", None)
        if setter is None:
            super().set_ticklabels(axes, axis, labels)  # type: ignore[arg-type]
        else:
            setter(labels)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def set_ticklabel_rotation(self, axes: Any, axis: str, rotation: float) -> None:
        tick_params = getattr(axes, "tick_params", None)
        if tick_params is None or axis == "z":
            super().set_ticklabel_rotation(axes, axis, rotation)  # type: ignore[arg-type]
        else:
            tick_params(axis=axis, labelrotation=rotation)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def get_axes_text(self, axes: Any, kind: str) -> tuple[str, ...]:
        getter = {
            "title": getattr(axes, "get_title", None),
            "xlabel": getattr(axes, "get_xlabel", None),
            "ylabel": getattr(axes, "get_ylabel", None),
            "zlabel": getattr(axes, "get_zlabel", None),
        }.get(kind)
        if getter is None:
            return super().get_axes_text(axes, kind)  # type: ignore[arg-type]
        value = str(getter())
        return tuple(value.splitlines()) if value else ()

    def set_axes_text(self, axes: Any, kind: str, text: tuple[str, ...]) -> None:
        value = "\n".join(text)
        setter = {
            "title": getattr(axes, "set_title", None),
            "xlabel": getattr(axes, "set_xlabel", None),
            "ylabel": getattr(axes, "set_ylabel", None),
            "zlabel": getattr(axes, "set_zlabel", None),
        }.get(kind)
        if setter is None:
            super().set_axes_text(axes, kind, text)  # type: ignore[arg-type]
        else:
            setter(value)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def is_3d_axes(self, axes: Any) -> bool:
        if hasattr(axes, "is_3d"):
            return bool(getattr(axes, "is_3d"))
        return hasattr(axes, "get_zlim") and hasattr(axes, "view_init")

    def get_camera3d(self, axes: Any) -> Camera3DState:
        return Camera3DState(
            azim=float(getattr(axes, "azim", 0.0)),
            elev=float(getattr(axes, "elev", 0.0)),
            roll=float(getattr(axes, "roll", 0.0)),
            view_angle=float(getattr(axes, "dist")) if getattr(axes, "dist", None) is not None else None,
            position=self._camera_vector_attr(axes, "camera_position"),
            target=self._camera_vector_attr(axes, "camera_target"),
            up_vector=self._camera_vector_attr(axes, "camera_up_vector"),
        )

    def set_camera3d(self, axes: Any, camera: Camera3DState) -> None:
        try:
            axes.view_init(elev=camera.elev, azim=camera.azim, roll=camera.roll)
        except TypeError:
            axes.view_init(elev=camera.elev, azim=camera.azim)
        if camera.view_angle is not None and hasattr(axes, "dist"):
            axes.dist = camera.view_angle
        if camera.position is not None:
            setattr(axes, "camera_position", camera.position)
        if camera.target is not None:
            setattr(axes, "camera_target", camera.target)
        if camera.up_vector is not None:
            setattr(axes, "camera_up_vector", camera.up_vector)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def get_camera_projection(self, axes: Any) -> CameraProjection:
        if hasattr(axes, "get_proj_type"):
            projection = axes.get_proj_type()
        else:
            projection = getattr(axes, "camera_projection", "orthographic")
        if projection == "persp":
            return "perspective"
        if projection in {"ortho", "orthographic"}:
            return "orthographic"
        if projection == "perspective":
            return "perspective"
        return "orthographic"

    def set_camera_projection(self, axes: Any, projection: CameraProjection) -> None:
        if hasattr(axes, "set_proj_type"):
            axes.set_proj_type("ortho" if projection == "orthographic" else "persp")
        else:
            setattr(axes, "camera_projection", projection)
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def _camera_vector_attr(self, axes: Any, name: str) -> tuple[float, float, float] | None:
        value = getattr(axes, name, None)
        if value is None:
            return None
        try:
            vector = tuple(float(item) for item in value)
        except (TypeError, ValueError):
            return None
        if len(vector) != 3:
            return None
        return vector

    def begin_zoom_box(self, axes: Any, x: float, y: float) -> None:
        self.end_zoom_box()
        try:
            from matplotlib.patches import Rectangle
        except ImportError:
            return
        self._zoom_box_artist = Rectangle(
            (x, y),
            0,
            0,
            fill=False,
            edgecolor="black",
            linewidth=1.0,
            linestyle="--",
            alpha=0.8,
            zorder=10_000,
        )
        axes.add_patch(self._zoom_box_artist)
        self._draw_idle(axes)

    def update_zoom_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        if self._zoom_box_artist is None:
            return
        self._zoom_box_artist.set_xy((min(x0, x1), min(y0, y1)))
        self._zoom_box_artist.set_width(abs(x1 - x0))
        self._zoom_box_artist.set_height(abs(y1 - y0))
        self._draw_idle(axes)

    def end_zoom_box(self) -> None:
        if self._zoom_box_artist is None:
            return
        axes = getattr(self._zoom_box_artist, "axes", None)
        self._zoom_box_artist.remove()
        self._zoom_box_artist = None
        if axes is not None:
            self._draw_idle(axes)

    def begin_brush_box(self, axes: Any, x: float, y: float) -> None:
        self.end_brush_box()
        try:
            from matplotlib.patches import Rectangle
        except ImportError:
            return
        self._brush_box_artist = Rectangle(
            (x, y),
            0,
            0,
            fill=True,
            facecolor="#0072BD",
            edgecolor="#0072BD",
            linewidth=1.0,
            linestyle="-",
            alpha=0.15,
            zorder=10_000,
        )
        axes.add_patch(self._brush_box_artist)
        self._draw_idle(axes)

    def update_brush_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        if self._brush_box_artist is None:
            return
        self._brush_box_artist.set_xy((min(x0, x1), min(y0, y1)))
        self._brush_box_artist.set_width(abs(x1 - x0))
        self._brush_box_artist.set_height(abs(y1 - y0))
        self._draw_idle(axes)

    def end_brush_box(self) -> None:
        if self._brush_box_artist is None:
            return
        axes = getattr(self._brush_box_artist, "axes", None)
        self._brush_box_artist.remove()
        self._brush_box_artist = None
        if axes is not None:
            self._draw_idle(axes)

    def brush_box(
        self,
        axes: Any,
        start: tuple[float, float],
        end: tuple[float, float],
        modifiers: frozenset[str],
    ) -> None:
        if not self._is_finite_box(start, end):
            return
        multi_select = bool(modifiers & {"shift", "control", "ctrl", "cmd", "super"})
        brushed = self.find_lines_in_box(axes, start, end)
        had_selection = bool(self.selected_lines)
        changed = False
        if not multi_select:
            self.clear_selection()
            changed = had_selection
        for line in brushed:
            if not self.is_line_selected(line):
                self.select_line(line)
                changed = True
        if changed and (multi_select or brushed):
            self._draw_idle(axes)

    def create_data_tip(self, axes: Any, x: float, y: float) -> None:
        if not self._is_finite_pair(x, y):
            return
        nearest = self.find_nearest_line_point(axes, x, y)
        if nearest is None:
            return
        line, index, point_x, point_y, point_z = nearest
        if self._normalized_point_distance(axes, point_x, point_y, x, y) > self.data_tip_pick_tolerance:
            return
        if self.has_data_tip(axes, line, index):
            return
        label = self.format_data_tip(line, index, point_x, point_y, point_z)
        annotation = axes.annotate(
            label,
            xy=(point_x, point_y),
            xytext=(8, 8),
            textcoords="offset points",
            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "0.35", "alpha": 0.95},
            arrowprops={"arrowstyle": "->", "color": "0.35", "linewidth": 0.8},
            fontsize=9,
            zorder=10_001,
        )
        self.data_tips.append(DataTip(axes, line, annotation, point_x, point_y, index, label, point_z))
        self._draw_idle(axes)

    def has_data_tip(self, axes: Any, line: Any, index: int) -> bool:
        return any(tip.axes is axes and tip.line is line and tip.index == index for tip in self.data_tips)

    def clear_data_tips(self, axes: Any | None = None) -> None:
        remaining = []
        for tip in self.data_tips:
            if axes is not None and tip.axes is not axes:
                remaining.append(tip)
                continue
            tip.annotation.remove()
            self._draw_idle(tip.axes)
        self.data_tips = remaining

    def clear_data_tips_for_lines(self, lines: set[Any]) -> None:
        remaining = []
        redraw_axes = set()
        for tip in self.data_tips:
            if tip.line not in lines:
                remaining.append(tip)
                continue
            tip.annotation.remove()
            redraw_axes.add(tip.axes)
        self.data_tips = remaining
        for axes in redraw_axes:
            self._draw_idle(axes)

    def select_nearest_artist(
        self,
        axes: Any,
        x: float,
        y: float,
        modifiers: frozenset[str],
    ) -> None:
        if not self._is_finite_pair(x, y):
            return
        nearest = self.find_nearest_line_point(axes, x, y)
        multi_select = bool(modifiers & {"shift", "control", "ctrl", "cmd", "super"})
        if nearest is None:
            if not multi_select:
                self.clear_selection()
            return
        line, _index, point_x, point_y, _point_z = nearest
        if self._normalized_point_distance(axes, point_x, point_y, x, y) > self.selection_pick_tolerance:
            if not multi_select:
                self.clear_selection()
            return
        if self.is_line_selected(line):
            if multi_select:
                self.deselect_line(line)
            return
        if not multi_select:
            self.clear_selection()
        self.select_line(line)
        self._draw_idle(axes)

    def select_line(self, line: Any) -> None:
        if self.is_line_selected(line):
            return
        state = SelectedLineState(
            line=line,
            linewidth=float(getattr(line, "get_linewidth", lambda: 1.5)()),
            alpha=getattr(line, "get_alpha", lambda: None)(),
            zorder=float(getattr(line, "get_zorder", lambda: 2.0)()),
            visible=bool(getattr(line, "get_visible", lambda: True)()),
        )
        self.selected_lines.append(state)
        line.set_linewidth(max(state.linewidth * 1.8, state.linewidth + 1.5))
        line.set_alpha(1.0)
        line.set_zorder(state.zorder + 1000)

    def deselect_line(self, line: Any) -> None:
        remaining = []
        restored_axes = None
        for state in self.selected_lines:
            if state.line is line:
                self._restore_line_state(state)
                restored_axes = getattr(line, "axes", None)
            else:
                remaining.append(state)
        self.selected_lines = remaining
        if restored_axes is not None:
            self._draw_idle(restored_axes)

    def clear_selection(self, axes: Any | None = None) -> None:
        remaining = []
        redraw_axes = set()
        for state in self.selected_lines:
            line_axes = getattr(state.line, "axes", None)
            if axes is not None and line_axes is not axes:
                remaining.append(state)
                continue
            self._restore_line_state(state)
            if line_axes is not None:
                redraw_axes.add(line_axes)
        self.selected_lines = remaining
        for redraw_axis in redraw_axes:
            self._draw_idle(redraw_axis)

    def is_line_selected(self, line: Any) -> bool:
        return any(state.line is line for state in self.selected_lines)

    def toggle_selected_visibility(self) -> bool:
        if not self.selected_lines:
            return False
        axes_to_redraw = set()
        any_visible = any(bool(getattr(state.line, "get_visible", lambda: True)()) for state in self.selected_lines)
        new_visible = not any_visible
        for state in self.selected_lines:
            if not hasattr(state.line, "set_visible"):
                continue
            state.line.set_visible(new_visible)
            axes = getattr(state.line, "axes", None)
            if axes is not None:
                axes_to_redraw.add(axes)
        for axes in axes_to_redraw:
            self._draw_idle(axes)
        return True

    def delete_selected(self) -> int:
        states = list(self.selected_lines)
        if not states:
            return 0
        lines = {state.line for state in states}
        axes_to_redraw = {getattr(state.line, "axes", None) for state in states}
        self.clear_data_tips_for_lines(lines)
        for state in states:
            self._restore_line_state(state)
            state.line.remove()
        self.selected_lines = []
        for axes in axes_to_redraw:
            if axes is not None:
                self._draw_idle(axes)
        return len(states)

    def handle_delete_key(self) -> bool:
        if self.selected_lines:
            self.delete_selected()
            return True
        if self.data_tips:
            self.clear_data_tips()
            return True
        return False

    def toggle_grid(self, axes: Any | None = None) -> None:
        self.grid("toggle", axes=axes)

    def grid_is_enabled(self, axes: Any) -> bool:
        return super().grid_is_enabled(axes)

    def set_grid_visible(self, axes: Any, visible: bool) -> None:
        super().set_grid_visible(axes, visible)

    def minor_grid_is_enabled(self, axes: Any) -> bool:
        return super().minor_grid_is_enabled(axes)

    def set_minor_grid_visible(self, axes: Any, visible: bool) -> None:
        super().set_minor_grid_visible(axes, visible)

    def axis_grid_is_enabled(self, axes: Any, axis: str, *, minor: bool = False) -> bool:
        if axis == "z":
            return super().axis_grid_is_enabled(axes, axis, minor=minor)  # type: ignore[arg-type]
        if minor:
            getter = getattr(axes, f"get_{axis}minorticklines", None)
        else:
            getter = getattr(axes, f"get_{axis}gridlines", None)
        if getter is None:
            return super().axis_grid_is_enabled(axes, axis, minor=minor)  # type: ignore[arg-type]
        lines = list(getter())
        if not lines:
            return super().axis_grid_is_enabled(axes, axis, minor=minor)  # type: ignore[arg-type]
        return any(getattr(line, "get_visible", lambda: False)() for line in lines)

    def set_axis_grid_visible(self, axes: Any, axis: str, visible: bool, *, minor: bool = False) -> None:
        if axis == "z":
            super().set_axis_grid_visible(axes, axis, visible, minor=minor)  # type: ignore[arg-type]
            self._draw_idle(axes)
            return
        try:
            axes.grid(visible, which="minor" if minor else "major", axis=axis)
        except TypeError:
            super().set_axis_grid_visible(axes, axis, visible, minor=minor)  # type: ignore[arg-type]
        self._draw_idle(axes)

    def axis_minor_tick_is_enabled(self, axes: Any, axis: str) -> bool:
        if axis == "z":
            return super().axis_minor_tick_is_enabled(axes, axis)  # type: ignore[arg-type]
        fallback_state = super().axis_minor_tick_is_enabled(axes, axis)  # type: ignore[arg-type]
        if fallback_state:
            return True
        getter = getattr(axes, f"get_{axis}minorticklines", None)
        if getter is None:
            return fallback_state
        lines = list(getter())
        if lines:
            return any(getattr(line, "get_visible", lambda: False)() for line in lines)
        return fallback_state

    def set_axis_minor_tick_visible(self, axes: Any, axis: str, visible: bool) -> None:
        if axis == "z":
            super().set_axis_minor_tick_visible(axes, axis, visible)  # type: ignore[arg-type]
            self._draw_idle(axes)
            return
        axis_obj = getattr(axes, f"{axis}axis", None)
        setter = getattr(axis_obj, "set_minor_locator", None)
        if setter is None:
            super().set_axis_minor_tick_visible(axes, axis, visible)  # type: ignore[arg-type]
            self._draw_idle(axes)
            return
        try:
            from matplotlib.ticker import AutoMinorLocator, NullLocator

            setter(AutoMinorLocator() if visible else NullLocator())
        except Exception:
            super().set_axis_minor_tick_visible(axes, axis, visible)  # type: ignore[arg-type]
        self._draw_idle(axes)

    def box_is_enabled(self, axes: Any) -> bool:
        spines = getattr(axes, "spines", None)
        if not spines:
            return False
        return all(getattr(spine, "get_visible", lambda: True)() for spine in spines.values())

    def set_box_visible(self, axes: Any, visible: bool) -> None:
        spines = getattr(axes, "spines", None)
        if not spines:
            return
        for spine in spines.values():
            set_visible = getattr(spine, "set_visible", None)
            if set_visible is not None:
                set_visible(visible)
        self._draw_idle(axes)

    def toggle_legend(self, axes: Any | None = None) -> bool:
        return self.legend("toggle", axes=axes)

    def legend_is_enabled(self, axes: Any) -> bool:
        legend = self._get_legend(axes)
        return legend is not None

    def set_legend_visible(self, axes: Any, visible: bool) -> bool:
        legend = self._get_legend(axes)
        if legend is not None:
            if visible:
                return True
            legend.remove()
            self._draw_idle(axes)
            return False
        if not visible:
            return False
        if not self._has_legendable_artists(axes):
            return False
        axes.legend()
        self._draw_idle(axes)
        return True

    def toggle_link_x_axes(self, axes: Any | None = None) -> bool:
        linked = self.toggle_link_axes("x", axes=axes)
        self.x_axes_linked = linked
        return linked

    def toggle_link_y_axes(self, axes: Any | None = None) -> bool:
        return self.toggle_link_axes("y", axes=axes)

    def toggle_link_xy_axes(self, axes: Any | None = None) -> bool:
        return self.toggle_link_axes("xy", axes=axes)

    def toggle_link_axes(self, axis: str, axes: Any | None = None) -> bool:
        axes = axes if axes is not None else self.require_active_axes()
        figure_axes = self._figure_axes(axes)
        if len(figure_axes) < 2:
            return False
        if self.linked_axes_state[axis]:
            self._unlink_axes(axis)
            self.linked_axes_state[axis] = False
            if axis == "x":
                self.x_axes_linked = False
            return False
        self.linkaxes(figure_axes, option=axis)
        self.linked_axes_state[axis] = True
        if axis == "x":
            self.x_axes_linked = True
        return True

    def update_coordinate_readout(self, axes: Any, x: float, y: float) -> None:
        if not (isfinite(float(x)) and isfinite(float(y))):
            return
        z = self.coordinate_readout_z(axes, x, y)
        readout = CoordinateReadout(axes=axes, x=x, y=y, text=self.format_coordinate_readout(axes, x, y, z), z=z)
        if self.coordinate_readout == readout:
            return
        self.coordinate_readout = readout
        self.on_coordinate_readout_changed(readout)

    def clear_coordinate_readout(self) -> None:
        if self.coordinate_readout is None:
            return
        self.coordinate_readout = None
        self.on_coordinate_readout_changed(None)

    def cancel_interaction(self) -> None:
        self.set_mode("none")
        self.clear_selection()
        self.clear_coordinate_readout()
        self.end_zoom_box()
        self.end_brush_box()

    def on_active_axes_changed(self, axes: Any | None) -> None:
        self.restore_active_axes_highlight()
        if axes is None:
            return
        self.apply_active_axes_highlight(axes)

    def apply_active_axes_highlight(self, axes: Any) -> None:
        spines = getattr(axes, "spines", None)
        if not spines:
            return
        original = {}
        for name, spine in spines.items():
            original[name] = SpineStyle(
                edgecolor=getattr(spine, "get_edgecolor", lambda: None)(),
                linewidth=float(getattr(spine, "get_linewidth", lambda: 1.0)()),
            )
            spine.set_edgecolor("#0072BD")
            spine.set_linewidth(max(original[name].linewidth, 1.8))
        self.active_axes_style = ActiveAxesStyle(axes=axes, spines=original)
        self._draw_idle(axes)

    def restore_active_axes_highlight(self) -> None:
        if self.active_axes_style is None:
            return
        axes = self.active_axes_style.axes
        spines = getattr(axes, "spines", {})
        for name, style in self.active_axes_style.spines.items():
            spine = spines.get(name)
            if spine is None:
                continue
            spine.set_edgecolor(style.edgecolor)
            spine.set_linewidth(style.linewidth)
        self.active_axes_style = None
        self._draw_idle(axes)

    def find_nearest_line_point(self, axes: Any, x: float, y: float) -> tuple[Any, int, float, float, float | None] | None:
        best: tuple[float, Any, int, float, float, float | None] | None = None
        x_span, y_span = self._axis_spans(axes)
        for line in getattr(axes, "lines", []):
            if not self._line_is_pickable(line):
                continue
            xdata = list(line.get_xdata())
            ydata = list(line.get_ydata())
            zdata = self._line_zdata(line)
            for index, (point_x, point_y) in enumerate(zip(xdata, ydata)):
                try:
                    px = float(point_x)
                    py = float(point_y)
                except (TypeError, ValueError):
                    continue
                if not (isfinite(px) and isfinite(py)):
                    continue
                pz = self._coerce_z_value(zdata, index)
                distance = self._normalized_point_distance(axes, px, py, x, y) ** 2
                if best is None or distance < best[0]:
                    best = (distance, line, index, px, py, pz)
        if best is None:
            return None
        _, line, index, point_x, point_y, point_z = best
        return line, index, point_x, point_y, point_z

    def find_lines_in_box(self, axes: Any, start: tuple[float, float], end: tuple[float, float]) -> list[Any]:
        x0, x1 = sorted((start[0], end[0]))
        y0, y1 = sorted((start[1], end[1]))
        lines = []
        for line in getattr(axes, "lines", []):
            if not self._line_is_pickable(line):
                continue
            xdata = list(line.get_xdata())
            ydata = list(line.get_ydata())
            for point_x, point_y in zip(xdata, ydata):
                try:
                    px = float(point_x)
                    py = float(point_y)
                except (TypeError, ValueError):
                    continue
                if isfinite(px) and isfinite(py) and x0 <= px <= x1 and y0 <= py <= y1:
                    lines.append(line)
                    break
        return lines

    def format_data_tip(self, line: Any, index: int, x: float, y: float, z: float | None = None) -> str:
        label = getattr(line, "get_label", lambda: "")()
        label_line = f"Series: {label}\n" if label and not str(label).startswith("_") else ""
        z_line = f"\nZ: {z:g}" if z is not None else ""
        return f"{label_line}X: {x:g}\nY: {y:g}{z_line}\nIndex: {index + 1}"

    def format_coordinate_readout(self, axes: Any, x: float, y: float, z: float | None = None) -> str:
        label = getattr(axes, "get_title", lambda: "")()
        prefix = f"{label}: " if label else ""
        z_text = f", z={z:g}" if z is not None else ""
        return f"{prefix}x={x:g}, y={y:g}{z_text}"

    def coordinate_readout_z(self, axes: Any, x: float, y: float) -> float | None:
        if not (isfinite(float(x)) and isfinite(float(y))):
            return None
        if not self.is_3d_axes(axes):
            return None
        nearest = self.find_nearest_line_point(axes, x, y)
        if nearest is None:
            return None
        _line, _index, point_x, point_y, point_z = nearest
        if self._normalized_point_distance(axes, point_x, point_y, x, y) > self.coordinate_readout_z_tolerance:
            return None
        return point_z

    def on_coordinate_readout_changed(self, readout: CoordinateReadout | None) -> None:
        """Hook for UI integrations that expose pointer coordinates."""

    def on_mode_changed(self, mode: Any) -> None:
        self._deactivate_matplotlib_toolbar_mode()

    def _restore_line_state(self, state: SelectedLineState) -> None:
        state.line.set_linewidth(state.linewidth)
        state.line.set_alpha(state.alpha)
        state.line.set_zorder(state.zorder)
        if hasattr(state.line, "set_visible"):
            state.line.set_visible(state.visible)

    def _deactivate_matplotlib_toolbar_mode(self) -> None:
        axes = self.active_axes or self.axes
        toolbar = getattr(getattr(getattr(axes, "figure", None), "canvas", None), "toolbar", None)
        mode = str(getattr(toolbar, "mode", "") or "").lower()
        if mode == "pan/zoom":
            pan = getattr(toolbar, "pan", None)
            if pan is not None:
                pan()
        elif mode == "zoom rect":
            zoom = getattr(toolbar, "zoom", None)
            if zoom is not None:
                zoom()

    def _draw_idle(self, axes: Any) -> None:
        canvas = getattr(getattr(axes, "figure", None), "canvas", None)
        if canvas is not None:
            canvas.draw_idle()

    def _axis_spans(self, axes: Any) -> tuple[float, float]:
        x0, x1 = axes.get_xlim()
        y0, y1 = axes.get_ylim()
        x_span = abs(float(x1) - float(x0)) or 1.0
        y_span = abs(float(y1) - float(y0)) or 1.0
        return x_span, y_span

    def _normalized_point_distance(self, axes: Any, point_x: float, point_y: float, x: float, y: float) -> float:
        x_span, y_span = self._axis_spans(axes)
        return (((point_x - x) / x_span) ** 2 + ((point_y - y) / y_span) ** 2) ** 0.5

    def _is_finite_box(self, start: tuple[float, float], end: tuple[float, float]) -> bool:
        return self._is_finite_pair(start[0], start[1]) and self._is_finite_pair(end[0], end[1])

    def _line_is_pickable(self, line: Any) -> bool:
        visible = getattr(line, "get_visible", lambda: True)()
        return bool(visible)

    def _line_zdata(self, line: Any) -> list[Any] | None:
        if hasattr(line, "get_zdata"):
            return list(line.get_zdata())
        vertices = getattr(line, "_verts3d", None)
        if vertices is not None and len(vertices) >= 3:
            return list(vertices[2])
        return None

    def _coerce_z_value(self, zdata: list[Any] | None, index: int) -> float | None:
        if zdata is None or index >= len(zdata):
            return None
        try:
            z = float(zdata[index])
        except (TypeError, ValueError):
            return None
        return z if isfinite(z) else None

    def _grid_is_enabled(self, axes: Any) -> bool:
        x_lines = getattr(axes, "get_xgridlines", lambda: [])()
        y_lines = getattr(axes, "get_ygridlines", lambda: [])()
        return any(getattr(line, "get_visible", lambda: False)() for line in [*x_lines, *y_lines])

    def _set_matplotlib_x_axis_location(self, axes: Any, location: XAxisLocation) -> bool:
        xaxis = getattr(axes, "xaxis", None)
        spines = getattr(axes, "spines", None)
        if xaxis is None and not spines:
            return False
        if location == "origin":
            self._set_spine_position(spines, "bottom", ("data", 0))
            self._set_spine_visible(spines, "bottom", True)
            self._set_spine_visible(spines, "top", False)
            self._call_axis_method(xaxis, "set_ticks_position", "bottom")
            self._call_axis_method(xaxis, "set_label_position", "bottom")
            return True
        self._set_spine_position(spines, "bottom", ("outward", 0))
        self._set_spine_position(spines, "top", ("outward", 0))
        self._set_spine_visible(spines, "bottom", True)
        self._set_spine_visible(spines, "top", True)
        self._call_axis_method(xaxis, "set_ticks_position", location)
        self._call_axis_method(xaxis, "set_label_position", location)
        return True

    def _set_matplotlib_y_axis_location(self, axes: Any, location: YAxisLocation) -> bool:
        yaxis = getattr(axes, "yaxis", None)
        spines = getattr(axes, "spines", None)
        if yaxis is None and not spines:
            return False
        if location == "origin":
            self._set_spine_position(spines, "left", ("data", 0))
            self._set_spine_visible(spines, "left", True)
            self._set_spine_visible(spines, "right", False)
            self._call_axis_method(yaxis, "set_ticks_position", "left")
            self._call_axis_method(yaxis, "set_label_position", "left")
            return True
        self._set_spine_position(spines, "left", ("outward", 0))
        self._set_spine_position(spines, "right", ("outward", 0))
        self._set_spine_visible(spines, "left", True)
        self._set_spine_visible(spines, "right", True)
        self._call_axis_method(yaxis, "set_ticks_position", location)
        self._call_axis_method(yaxis, "set_label_position", location)
        return True

    def _set_spine_position(self, spines: Any, name: str, position: Any) -> None:
        spine = spines.get(name) if spines else None
        setter = getattr(spine, "set_position", None)
        if setter is not None:
            setter(position)

    def _set_spine_visible(self, spines: Any, name: str, visible: bool) -> None:
        spine = spines.get(name) if spines else None
        setter = getattr(spine, "set_visible", None)
        if setter is not None:
            setter(visible)

    def _call_axis_method(self, axis: Any, method_name: str, value: str) -> None:
        method = getattr(axis, method_name, None)
        if method is not None:
            method(value)

    def _get_legend(self, axes: Any) -> Any | None:
        return getattr(axes, "get_legend", lambda: None)()

    def _has_legendable_artists(self, axes: Any) -> bool:
        for line in getattr(axes, "lines", []):
            label = getattr(line, "get_label", lambda: "")()
            if label and not str(label).startswith("_"):
                return True
        return False

    def _figure_axes(self, axes: Any) -> list[Any]:
        figure = getattr(axes, "figure", None)
        return list(getattr(figure, "axes", [axes]))

    def _unlink_axes(self, axis: str) -> None:
        self.unlink_axes(axis)  # type: ignore[arg-type]
