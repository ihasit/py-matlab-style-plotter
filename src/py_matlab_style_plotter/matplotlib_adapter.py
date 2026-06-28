"""Matplotlib adapter for the MATLAB-like axes interaction base."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from math import isfinite
from typing import Any, Iterator

import copy
import numpy as np

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
    ImageSeries,
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
    marker: Any | None
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
    highlight: Any | None = None


@dataclass(frozen=True)
class SelectedDataTipState:
    """Selection state for a data cursor marker."""

    tip: DataTip
    highlight: Any | None = None


@dataclass(frozen=True)
class BrushedPointsState:
    """Highlight artist for data points selected by brushing."""

    axes: Any
    line: Any
    artist: Any
    indices: tuple[int, ...]


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
        self.selected_data_tips: list[SelectedDataTipState] = []
        self.brushed_points: list[BrushedPointsState] = []
        self.coordinate_readout: CoordinateReadout | None = None
        self.active_axes_style: ActiveAxesStyle | None = None
        self._draw_idle_batch_depth = 0
        self._draw_idle_pending_canvases: list[Any] = []
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

    def draw_scatter3_series(self, axes: Any, series: list[Any]) -> list[Any]:
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
            created = axes.scatter(item.x, item.y, item.z, **kwargs)
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

    def draw_stem3_series(self, axes: Any, series: list[Any]) -> list[Any]:
        import numpy as np
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            markerline, stemlines, baseline = axes.stem(item.x, item.y, item.z, **kwargs)
            artists.append(markerline)
            artists.extend(stemlines)
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

    def draw_barh_series(self, axes: Any, series: list[BarSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = {**dict(item.line_spec), **dict(item.properties)}
            kwargs.pop("marker", None)
            kwargs.pop("linestyle", None)
            created = axes.barh(item.x, item.y, **kwargs)
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

    def draw_image_series(self, axes: Any, series: list[ImageSeries]) -> list[Any]:
        artists: list[Any] = []
        for item in series:
            kwargs = dict(item.properties)
            kwargs.setdefault("origin", "upper")
            kwargs.setdefault("aspect", "auto")
            if item.x is not None and item.y is not None:
                kwargs.setdefault("extent", (item.x[0], item.x[1], item.y[1], item.y[0]))
            created = axes.imshow(item.cdata, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_contour_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.x is not None and item.y is not None:
                created = axes.contour(item.x, item.y, item.zdata, **kwargs)
            else:
                created = axes.contour(item.zdata, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_contourf_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.x is not None and item.y is not None:
                created = axes.contourf(item.x, item.y, item.zdata, **kwargs)
            else:
                created = axes.contourf(item.zdata, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_surf_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.cdata is not None:
                kwargs.setdefault("cmap", None)
            if item.x is not None and item.y is not None:
                x_arr = np.array(item.x)
                y_arr = np.array(item.y)
                z_arr = np.array(item.zdata)
                x_grid, y_grid = np.meshgrid(x_arr, y_arr)
                created = axes.plot_surface(x_grid, y_grid, z_arr, **kwargs)
            else:
                z_arr = np.array(item.zdata)
                y_grid, x_grid = np.mgrid[0:z_arr.shape[0], 0:z_arr.shape[1]]
                created = axes.plot_surface(x_grid, y_grid, z_arr, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists

    def draw_mesh_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            kwargs.setdefault("edgecolor", kwargs.pop("edge_color", "k"))
            if item.x is not None and item.y is not None:
                x_arr = np.array(item.x)
                y_arr = np.array(item.y)
                z_arr = np.array(item.zdata)
                x_grid, y_grid = np.meshgrid(x_arr, y_arr)
                created = axes.plot_wireframe(x_grid, y_grid, z_arr, **kwargs)
            else:
                z_arr = np.array(item.zdata)
                y_grid, x_grid = np.mgrid[0:z_arr.shape[0], 0:z_arr.shape[1]]
                created = axes.plot_wireframe(x_grid, y_grid, z_arr, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_quiver_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.x is not None and item.y is not None:
                created = axes.quiver(item.x, item.y, item.u, item.v, **kwargs)
            else:
                y_grid, x_grid = np.mgrid[0:len(item.u), 0:len(item.u[0]) if item.u else 0]
                created = axes.quiver(x_grid, y_grid, item.u, item.v, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_pcolor_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.x is not None and item.y is not None:
                created = axes.pcolormesh(item.x, item.y, item.cdata, **kwargs)
            else:
                created = axes.pcolormesh(item.cdata, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def create_subplot_axes(self, rows: int, columns: int, position: int) -> Any:
        fig = self.active_axes.figure if self.active_axes is not None else None
        if fig is None:
            raise RuntimeError("subplot requires an active axes with a figure")
        return fig.add_subplot(rows, columns, position)


    def delete_artist(self, artist: Any) -> None:
        try:
            artist.remove()
        except (NotImplementedError, ValueError):
            pass


    def set_artist_property(self, artist: Any, name: str, value: Any) -> None:
        setter = getattr(artist, f"set_{name}", None)
        if setter is not None:
            setter(value)
        elif hasattr(artist, name):
            setattr(artist, name, value)

    def get_artist_property(self, artist: Any, name: str) -> Any:
        getter = getattr(artist, f"get_{name}", None)
        if getter is not None:
            return getter()
        return getattr(artist, name, None)


    def get_children(self, obj: Any) -> list[Any]:
        children = []
        for attr in ("lines", "collections", "images", "patches"):
            children.extend(getattr(obj, attr, []))
        return children


    def copy_artist(self, artist: Any, target: Any) -> Any:
        new_artist = copy.copy(artist)
        if hasattr(new_artist, "axes"):
            new_artist.axes = target
        for attr in ("lines", "collections", "images", "patches"):
            if hasattr(target, attr) and isinstance(getattr(target, attr), list):
                getattr(target, attr).append(new_artist)
                break
        return new_artist


    def draw_spy_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            matrix = np.zeros((item.nrows, item.ncols))
            for r, c in zip(item.row_indices, item.col_indices):
                matrix[r, c] = 1
            created = axes.spy(matrix, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def _flush_graphics(self, axes: Any) -> None:
        self._draw_idle(axes)


    def draw_annotation_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.annotation_type == "line":
                from matplotlib.lines import Line2D
                line = Line2D([item.position[0], item.position[2]], [item.position[1], item.position[3]], transform=axes.figure.transFigure, **kwargs)
                axes.figure.patches.append(line)
                artists.append(line)
            elif item.annotation_type == "arrow":
                from matplotlib.patches import FancyArrowPatch
                arrow = FancyArrowPatch((item.position[0], item.position[1]), (item.position[2], item.position[3]), transform=axes.figure.transFigure, **kwargs)
                axes.figure.patches.append(arrow)
                artists.append(arrow)
            elif item.annotation_type == "textarrow":
                from matplotlib.patches import FancyArrowPatch
                from matplotlib.text import Annotation
                arrow = FancyArrowPatch((item.position[2], item.position[3]), (item.position[0], item.position[1]), transform=axes.figure.transFigure, **kwargs)
                axes.figure.patches.append(arrow)
                if item.text:
                    ann = Annotation(item.text, (item.position[0], item.position[1]), transform=axes.figure.transFigure, **kwargs)
                    axes.figure.patches.append(ann)
                    artists.append(ann)
                artists.append(arrow)
            elif item.annotation_type in ("textbox", "ellipse", "rectangle"):
                from matplotlib.patches import Rectangle, Ellipse
                x, y, w, h = item.position
                if item.annotation_type == "textbox":
                    patch = Rectangle((x, y), w, h, transform=axes.figure.transFigure, fill=False, **kwargs)
                elif item.annotation_type == "ellipse":
                    patch = Ellipse((x + w/2, y + h/2), w, h, transform=axes.figure.transFigure, **kwargs)
                else:
                    patch = Rectangle((x, y), w, h, transform=axes.figure.transFigure, **kwargs)
                axes.figure.patches.append(patch)
                artists.append(patch)
        self._draw_idle(axes)
        return artists


    def set_yyaxis_side(self, axes: Any, side: str) -> None:
        if side == "right":
            if not hasattr(axes, "_yyaxis_right") or axes._yyaxis_right is None:
                axes._yyaxis_right = axes.twinx()
            axes._yyaxis_active = "right"
        else:
            axes._yyaxis_active = "left"


    def draw_polar_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            theta_arr = np.array(item.theta)
            rho_arr = np.array(item.rho)
            kwargs = dict(item.properties)
            if item.line_spec:
                for key, val in item.line_spec:
                    kwargs.setdefault(key, val)
            created = axes.plot(theta_arr, rho_arr, **kwargs)
            artists.extend(created)
        self._draw_idle(axes)
        return artists

    def draw_polarhistogram_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            theta_arr = np.array(item.theta)
            kwargs = dict(item.properties)
            if item.bins is not None:
                kwargs.setdefault("bins", item.bins)
            created = axes.bar(theta_arr, np.ones_like(theta_arr), **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_pie_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            kwargs = dict(item.properties)
            if item.labels is not None:
                kwargs["labels"] = item.labels
            created = axes.pie(item.data, **kwargs)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_pareto_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            data = np.array(item.data)
            sorted_indices = np.argsort(-data)
            sorted_data = data[sorted_indices]
            cumulative = np.cumsum(sorted_data) / np.sum(sorted_data) * 100
            bar_labels = item.labels if item.labels is not None else [str(i) for i in range(len(data))]
            sorted_labels = [bar_labels[i] for i in sorted_indices]
            bar_artist = axes.bar(range(len(sorted_data)), sorted_data)
            axes.set_xticks(range(len(sorted_data)))
            axes.set_xticklabels(sorted_labels)
            ax2 = axes.twinx()
            ax2.plot(range(len(sorted_data)), cumulative, "r-o")
            ax2.set_ylabel("Cumulative %")
            ax2.set_ylim(0, 105)
            artists.append(bar_artist)
        self._draw_idle(axes)
        return artists


    def draw_heatmap_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            data = np.array(item.data)
            created = axes.imshow(data, cmap="viridis", aspect="auto")
            if item.x_labels is not None:
                axes.set_xticks(range(len(item.x_labels)))
                axes.set_xticklabels(item.x_labels)
            if item.y_labels is not None:
                axes.set_yticks(range(len(item.y_labels)))
                axes.set_yticklabels(item.y_labels)
            artists.append(created)
        self._draw_idle(axes)
        return artists


    def draw_rose_series(self, axes: Any, series: list[Any]) -> list[Any]:
        artists = []
        for item in series:
            theta_arr = np.array(item.theta)
            if isinstance(item.bins, int) or item.bins is None:
                n_bins = item.bins if item.bins is not None else 20
                bins = np.linspace(0, 2 * np.pi, n_bins + 1)
            else:
                bins = np.array(item.bins)
            counts, bin_edges = np.histogram(theta_arr, bins=bins)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            width = bin_edges[1] - bin_edges[0]
            created = axes.bar(bin_centers, counts, width=width, **dict(item.properties))
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
        self._draw_idle(axes)

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
        if self.is_3d_axes(axes):
            if hasattr(axes, "set_box_aspect"):
                axes.set_box_aspect(ratio)
        else:
            x_ratio = float(ratio[0]) if ratio else 1.0
            y_ratio = float(ratio[1]) if len(ratio) > 1 else 1.0
            axes.set_aspect(y_ratio / x_ratio if x_ratio != 0.0 else "auto")
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
        self._add_box_artist(axes, self._zoom_box_artist, x, y, x, y)
        self._draw_idle(axes)

    def update_zoom_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        if self._zoom_box_artist is None:
            return
        self._set_box_artist_bounds(self._zoom_box_artist, axes, x0, y0, x1, y1)
        self._draw_idle(axes)

    def end_zoom_box(self) -> None:
        if self._zoom_box_artist is None:
            return
        axes = self._box_artist_axes(self._zoom_box_artist)
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
        self._add_box_artist(axes, self._brush_box_artist, x, y, x, y)
        self._draw_idle(axes)

    def update_brush_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        if self._brush_box_artist is None:
            return
        self._set_box_artist_bounds(self._brush_box_artist, axes, x0, y0, x1, y1)
        self._draw_idle(axes)

    def end_brush_box(self) -> None:
        if self._brush_box_artist is None:
            return
        axes = self._box_artist_axes(self._brush_box_artist)
        self._brush_box_artist.remove()
        self._brush_box_artist = None
        if axes is not None:
            self._draw_idle(axes)

    def _add_box_artist(self, axes: Any, artist: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        figure = getattr(axes, "figure", None)
        if self.is_3d_axes(axes) and self._can_add_figure_overlay_box(axes):
            artist.set_transform(figure.transFigure)
            setattr(artist, "_py_matlab_style_overlay_axes", axes)
            setattr(artist, "_py_matlab_style_figure_overlay", True)
            self._set_box_artist_bounds(artist, axes, x0, y0, x1, y1)
            figure.patches.append(artist)
            artist._remove_method = figure.patches.remove
            return
        add_patch = getattr(axes, "add_patch", None)
        if add_patch is not None:
            add_patch(artist)

    def _set_box_artist_bounds(self, artist: Any, axes: Any, x0: float, y0: float, x1: float, y1: float) -> None:
        if getattr(artist, "_py_matlab_style_figure_overlay", False):
            x0, y0, x1, y1 = self._data_box_to_figure_box(axes, x0, y0, x1, y1)
        artist.set_xy((min(x0, x1), min(y0, y1)))
        artist.set_width(abs(x1 - x0))
        artist.set_height(abs(y1 - y0))

    def _box_artist_axes(self, artist: Any) -> Any | None:
        return getattr(artist, "_py_matlab_style_overlay_axes", None) or getattr(artist, "axes", None)

    def _can_add_figure_overlay_box(self, axes: Any) -> bool:
        figure = getattr(axes, "figure", None)
        return (
            figure is not None
            and hasattr(figure, "patches")
            and hasattr(figure, "transFigure")
            and hasattr(getattr(figure, "transFigure"), "inverted")
            and hasattr(axes, "transData")
        )

    def _data_box_to_figure_box(self, axes: Any, x0: float, y0: float, x1: float, y1: float) -> tuple[float, float, float, float]:
        figure = axes.figure
        p0, p1 = axes.transData.transform([(x0, y0), (x1, y1)])
        f0, f1 = figure.transFigure.inverted().transform([p0, p1])
        return float(f0[0]), float(f0[1]), float(f1[0]), float(f1[1])

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
        brushed_points = self.find_line_points_in_box(axes, start, end)
        brushed = [line for line, _points in brushed_points]
        had_selection = bool(self.selected_lines)
        had_brushed_points = bool(self.brushed_points)
        changed = False
        if not multi_select:
            self.clear_selection()
            changed = had_selection or had_brushed_points
        for line, points in brushed_points:
            if self._set_brushed_points(axes, line, points):
                changed = True
        if changed and (multi_select or brushed):
            self._draw_idle(axes)

    def _set_brushed_points(self, axes: Any, line: Any, points: tuple[tuple[int, float, float, float | None], ...]) -> bool:
        self._clear_brushed_points_for_line(line)
        if not points:
            return False
        artist = self._draw_brushed_points(axes, line, points)
        if artist is None:
            return False
        self.brushed_points.append(BrushedPointsState(axes, line, artist, tuple(index for index, *_rest in points)))
        return True

    def _draw_brushed_points(self, axes: Any, line: Any, points: tuple[tuple[int, float, float, float | None], ...]) -> Any | None:
        scatter = getattr(axes, "scatter", None)
        if scatter is None:
            return None
        xs = [point_x for _index, point_x, _point_y, _point_z in points]
        ys = [point_y for _index, _point_x, point_y, _point_z in points]
        kwargs = {
            "s": max(float(getattr(line, "get_markersize", lambda: 6.0)()) ** 2 * 1.7, 36.0),
            "marker": "o",
            "facecolors": "#FFD400",
            "edgecolors": "#7A4F00",
            "linewidths": 0.8,
            "zorder": float(getattr(line, "get_zorder", lambda: 3.0)()) + 1500.0,
        }
        z_values = [point_z for _index, _point_x, _point_y, point_z in points]
        if self.is_3d_axes(axes) and all(point_z is not None for point_z in z_values):
            return scatter(xs, ys, [float(point_z) for point_z in z_values], **kwargs)
        return scatter(xs, ys, **kwargs)

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
        marker = self._draw_data_tip_marker(axes, point_x, point_y, point_z)
        self.data_tips.append(DataTip(axes, line, annotation, marker, point_x, point_y, index, label, point_z))
        self._draw_idle(axes)

    def has_data_tip(self, axes: Any, line: Any, index: int) -> bool:
        return any(tip.axes is axes and tip.line is line and tip.index == index for tip in self.data_tips)

    def clear_data_tips(self, axes: Any | None = None) -> None:
        remaining = []
        for tip in self.data_tips:
            if axes is not None and tip.axes is not axes:
                remaining.append(tip)
                continue
            self._remove_data_tip(tip)
            self._draw_idle(tip.axes)
        self.data_tips = remaining

    def clear_data_tips_for_lines(self, lines: set[Any]) -> None:
        remaining = []
        redraw_axes = set()
        for tip in self.data_tips:
            if tip.line not in lines:
                remaining.append(tip)
                continue
            self._remove_data_tip(tip)
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
        multi_select = bool(modifiers & {"shift", "control", "ctrl", "cmd", "super"})
        nearest_tip = self.find_nearest_data_tip(axes, x, y)
        if nearest_tip is not None:
            tip, tip_x, tip_y = nearest_tip
            if self._normalized_point_distance(axes, tip_x, tip_y, x, y) <= self.selection_pick_tolerance:
                if self.is_data_tip_selected(tip):
                    if multi_select:
                        self.deselect_data_tip(tip)
                    return
                if not multi_select:
                    self.clear_selection()
                self.select_data_tip(tip)
                self._draw_idle(axes)
                return
        nearest = self.find_nearest_line_point(axes, x, y)
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

    def select_data_tip(self, tip: DataTip) -> None:
        if self.is_data_tip_selected(tip):
            return
        self.selected_data_tips.append(SelectedDataTipState(tip, self._draw_data_tip_selection_highlight(tip)))

    def deselect_data_tip(self, tip: DataTip) -> None:
        remaining = []
        redraw_axes = None
        for state in self.selected_data_tips:
            if state.tip is tip:
                self._remove_artist(state.highlight)
                redraw_axes = tip.axes
            else:
                remaining.append(state)
        self.selected_data_tips = remaining
        if redraw_axes is not None:
            self._draw_idle(redraw_axes)

    def is_data_tip_selected(self, tip: DataTip) -> bool:
        return any(state.tip is tip for state in self.selected_data_tips)

    def select_line(self, line: Any) -> None:
        if self.is_line_selected(line):
            return
        linewidth = float(getattr(line, "get_linewidth", lambda: 1.5)())
        zorder = float(getattr(line, "get_zorder", lambda: 2.0)())
        state = SelectedLineState(
            line=line,
            linewidth=linewidth,
            alpha=getattr(line, "get_alpha", lambda: None)(),
            zorder=zorder,
            visible=bool(getattr(line, "get_visible", lambda: True)()),
            highlight=self._draw_selected_line_highlight(line, linewidth, zorder),
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
        brushed_redraw_axes = self._remove_brushed_points(lines={line})
        if restored_axes is not None:
            self._draw_idle(restored_axes)
        for axes in brushed_redraw_axes:
            if axes is not restored_axes:
                self._draw_idle(axes)

    def clear_selection(self, axes: Any | None = None) -> None:
        remaining = []
        redraw_axes = set()
        restored_lines = set()
        for state in self.selected_lines:
            line_axes = getattr(state.line, "axes", None)
            if axes is not None and line_axes is not axes:
                remaining.append(state)
                continue
            self._restore_line_state(state)
            restored_lines.add(state.line)
            if line_axes is not None:
                redraw_axes.add(line_axes)
        self.selected_lines = remaining
        remaining_tips = []
        for state in self.selected_data_tips:
            if axes is not None and state.tip.axes is not axes:
                remaining_tips.append(state)
                continue
            self._remove_artist(state.highlight)
            redraw_axes.add(state.tip.axes)
        self.selected_data_tips = remaining_tips
        if axes is None:
            redraw_axes.update(self._remove_brushed_points(lines=restored_lines if restored_lines else None))
        else:
            redraw_axes.update(self._remove_brushed_points(axes=axes))
        for redraw_axis in redraw_axes:
            self._draw_idle(redraw_axis)

    def is_line_selected(self, line: Any) -> bool:
        return any(state.line is line for state in self.selected_lines)

    def toggle_selected_visibility(self) -> bool:
        if not self.selected_lines and not self.selected_data_tips:
            return False
        axes_to_redraw = set()
        selected_visibility = [bool(getattr(state.line, "get_visible", lambda: True)()) for state in self.selected_lines]
        selected_visibility.extend(bool(getattr(state.tip.annotation, "get_visible", lambda: True)()) for state in self.selected_data_tips)
        any_visible = any(selected_visibility)
        new_visible = not any_visible
        selected_lines = {state.line for state in self.selected_lines}
        for state in self.selected_lines:
            if not hasattr(state.line, "set_visible"):
                continue
            state.line.set_visible(new_visible)
            axes = getattr(state.line, "axes", None)
            if axes is not None:
                axes_to_redraw.add(axes)
        for brushed_state in self.brushed_points:
            if brushed_state.line not in selected_lines:
                continue
            set_visible = getattr(brushed_state.artist, "set_visible", None)
            if set_visible is not None:
                set_visible(new_visible)
                axes_to_redraw.add(brushed_state.axes)
        for state in self.selected_lines:
            set_visible = getattr(state.highlight, "set_visible", None)
            if set_visible is not None:
                set_visible(new_visible)
        for state in self.selected_data_tips:
            for artist in (state.tip.annotation, state.tip.marker, state.highlight):
                set_visible = getattr(artist, "set_visible", None)
                if set_visible is not None:
                    set_visible(new_visible)
            axes_to_redraw.add(state.tip.axes)
        for axes in axes_to_redraw:
            self._draw_idle(axes)
        return True

    def delete_selected(self) -> int:
        states = list(self.selected_lines)
        tip_states = list(self.selected_data_tips)
        if not states and not tip_states:
            return 0
        lines = {state.line for state in states}
        axes_to_redraw = {getattr(state.line, "axes", None) for state in states}
        if lines:
            self.clear_data_tips_for_lines(lines)
        axes_to_redraw.update(self._remove_brushed_points(lines=lines))
        for state in states:
            self._restore_line_state(state)
            state.line.remove()
        deleted_tips = []
        for state in tip_states:
            self._remove_artist(state.highlight)
            if state.tip in self.data_tips:
                self._remove_data_tip(state.tip)
                deleted_tips.append(state.tip)
                axes_to_redraw.add(state.tip.axes)
        self.selected_lines = []
        self.selected_data_tips = []
        if deleted_tips:
            deleted_tip_set = set(deleted_tips)
            self.data_tips = [tip for tip in self.data_tips if tip not in deleted_tip_set]
        for axes in axes_to_redraw:
            if axes is not None:
                self._draw_idle(axes)
        return len(states) + len(deleted_tips)

    def handle_delete_key(self) -> bool:
        if self.selected_lines or self.selected_data_tips:
            self.delete_selected()
            return True
        if self.data_tips:
            self.clear_data_tips()
            return True
        return False

    def _clear_brushed_points_for_line(self, line: Any) -> set[Any]:
        return self._remove_brushed_points(lines={line})

    def _remove_brushed_points(self, *, axes: Any | None = None, lines: set[Any] | None = None) -> set[Any]:
        remaining = []
        redraw_axes = set()
        for state in self.brushed_points:
            if axes is not None and state.axes is not axes:
                remaining.append(state)
                continue
            if lines is not None and state.line not in lines:
                remaining.append(state)
                continue
            remove = getattr(state.artist, "remove", None)
            if remove is not None:
                remove()
            redraw_axes.add(state.axes)
        self.brushed_points = remaining
        return redraw_axes

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

    def colorbar_is_enabled(self, axes: Any) -> bool:
        return self._get_colorbar(axes) is not None

    def set_colorbar_visible(self, axes: Any, visible: bool) -> bool:
        colorbar = self._get_colorbar(axes)
        if colorbar is not None:
            if visible:
                return True
            colorbar.remove()
            setattr(axes, "_matlab_like_colorbar", None)
            self._draw_idle(axes)
            return False
        if not visible:
            return False
        mappable = self._latest_mappable(axes)
        if mappable is None:
            return False
        figure = getattr(axes, "figure", None)
        create = getattr(figure, "colorbar", None)
        if create is None:
            return False
        colorbar = create(mappable, ax=axes)
        setattr(axes, "_matlab_like_colorbar", colorbar)
        self._draw_idle(axes)
        return True

    def set_colormap(self, axes: Any, value: str | tuple[tuple[float, float, float], ...]) -> None:
        for mappable in [*getattr(axes, "images", []), *getattr(axes, "collections", [])]:
            set_cmap = getattr(mappable, "set_cmap", None)
            if set_cmap is not None:
                set_cmap(value)
        self._draw_idle(axes)

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
        self._disable_default_3d_mouse_rotation(axes)
        self.apply_active_axes_highlight(axes)

    def _disable_default_3d_mouse_rotation(self, axes: Any) -> None:
        if not self.is_3d_axes(axes):
            return
        disable_mouse_rotation = getattr(axes, "disable_mouse_rotation", None)
        if disable_mouse_rotation is None:
            return
        try:
            disable_mouse_rotation()
        except (TypeError, ValueError, AttributeError):
            return

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
            xy = self._finite_line_xy_arrays(line)
            if xy is None:
                continue
            xdata, ydata, indices = xy
            zdata = self._line_zdata(line)
            distances = ((xdata - x) / x_span) ** 2 + ((ydata - y) / y_span) ** 2
            nearest_position = int(np.argmin(distances))
            distance = float(distances[nearest_position])
            if best is None or distance < best[0]:
                index = int(indices[nearest_position])
                px = float(xdata[nearest_position])
                py = float(ydata[nearest_position])
                best = (distance, line, index, px, py, self._coerce_z_value(zdata, index))
        if best is None:
            return None
        _, line, index, point_x, point_y, point_z = best
        return line, index, point_x, point_y, point_z

    def find_nearest_data_tip(self, axes: Any, x: float, y: float) -> tuple[DataTip, float, float] | None:
        best: tuple[float, DataTip, float, float] | None = None
        for tip in self.data_tips:
            if tip.axes is not axes:
                continue
            if not bool(getattr(tip.marker, "get_visible", lambda: True)()):
                continue
            distance = self._normalized_point_distance(axes, tip.x, tip.y, x, y) ** 2
            if best is None or distance < best[0]:
                best = (distance, tip, tip.x, tip.y)
        if best is None:
            return None
        _distance, tip, tip_x, tip_y = best
        return tip, tip_x, tip_y

    def find_lines_in_box(self, axes: Any, start: tuple[float, float], end: tuple[float, float]) -> list[Any]:
        return [line for line, _points in self.find_line_points_in_box(axes, start, end)]

    def find_line_points_in_box(
        self,
        axes: Any,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> list[tuple[Any, tuple[tuple[int, float, float, float | None], ...]]]:
        x0, x1 = sorted((start[0], end[0]))
        y0, y1 = sorted((start[1], end[1]))
        lines = []
        for line in getattr(axes, "lines", []):
            if not self._line_is_pickable(line):
                continue
            xy = self._finite_line_xy_arrays(line)
            if xy is None:
                continue
            xdata, ydata, indices = xy
            in_box = (xdata >= x0) & (xdata <= x1) & (ydata >= y0) & (ydata <= y1)
            if not np.any(in_box):
                continue
            zdata = self._line_zdata(line)
            points = tuple(
                (
                    int(index),
                    float(point_x),
                    float(point_y),
                    self._coerce_z_value(zdata, int(index)),
                )
                for index, point_x, point_y in zip(indices[in_box], xdata[in_box], ydata[in_box])
            )
            lines.append((line, points))
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
        self._remove_artist(state.highlight)
        state.line.set_linewidth(state.linewidth)
        state.line.set_alpha(state.alpha)
        state.line.set_zorder(state.zorder)
        if hasattr(state.line, "set_visible"):
            state.line.set_visible(state.visible)

    def _draw_data_tip_marker(self, axes: Any, x: float, y: float, z: float | None) -> Any | None:
        scatter = getattr(axes, "scatter", None)
        if scatter is None:
            return None
        kwargs = {
            "s": 52.0,
            "marker": "s",
            "facecolors": "#FFD400",
            "edgecolors": "#202020",
            "linewidths": 0.8,
            "zorder": 10_002,
            "label": "_matlab_data_tip_marker",
        }
        try:
            if z is not None and self.is_3d_axes(axes):
                return scatter([x], [y], [z], **kwargs)
            return scatter([x], [y], **kwargs)
        except (TypeError, ValueError, AttributeError):
            return None

    def _draw_data_tip_selection_highlight(self, tip: DataTip) -> Any | None:
        scatter = getattr(tip.axes, "scatter", None)
        if scatter is None:
            return None
        kwargs = {
            "s": 110.0,
            "marker": "s",
            "facecolors": "none",
            "edgecolors": "#0072BD",
            "linewidths": 1.8,
            "zorder": 10_003,
            "label": "_matlab_data_tip_selection",
        }
        try:
            if tip.z is not None and self.is_3d_axes(tip.axes):
                return scatter([tip.x], [tip.y], [tip.z], **kwargs)
            return scatter([tip.x], [tip.y], **kwargs)
        except (TypeError, ValueError, AttributeError):
            return None

    def _remove_data_tip(self, tip: DataTip) -> None:
        self._remove_artist(tip.annotation)
        self._remove_artist(tip.marker)
        remaining = []
        for state in self.selected_data_tips:
            if state.tip is tip:
                self._remove_artist(state.highlight)
            else:
                remaining.append(state)
        self.selected_data_tips = remaining

    def _draw_selected_line_highlight(self, line: Any, linewidth: float, zorder: float) -> Any | None:
        axes = getattr(line, "axes", None)
        plot = getattr(axes, "plot", None)
        get_xdata = getattr(line, "get_xdata", None)
        get_ydata = getattr(line, "get_ydata", None)
        if plot is None or get_xdata is None or get_ydata is None:
            return None
        args = [get_xdata(), get_ydata()]
        get_zdata = getattr(line, "get_zdata", None)
        if get_zdata is not None and self.is_3d_axes(axes):
            args.append(get_zdata())
        marker = getattr(line, "get_marker", lambda: None)()
        linestyle = getattr(line, "get_linestyle", lambda: "-")()
        highlight_kwargs = {
            "color": "#FFD400",
            "linewidth": max(linewidth + 4.0, linewidth * 2.4),
            "alpha": 0.55,
            "zorder": zorder + 999.0,
            "solid_capstyle": "round",
            "dash_capstyle": "round",
            "label": "_matlab_selection_highlight",
        }
        if marker not in {None, "", "None", "none", " "}:
            highlight_kwargs["marker"] = marker
            highlight_kwargs["markerfacecolor"] = "none"
            highlight_kwargs["markeredgecolor"] = "#FFD400"
            highlight_kwargs["markeredgewidth"] = 2.0
            markersize = getattr(line, "get_markersize", lambda: None)()
            if markersize is not None:
                highlight_kwargs["markersize"] = float(markersize) + 4.0
        if linestyle not in {None, "", "None", "none", " "}:
            highlight_kwargs["linestyle"] = linestyle
        else:
            highlight_kwargs["linestyle"] = "None"
        try:
            created = plot(*args, **highlight_kwargs)
        except (TypeError, ValueError, AttributeError):
            return None
        if isinstance(created, list):
            return created[0] if created else None
        try:
            return next(iter(created))
        except TypeError:
            return created

    def _remove_artist(self, artist: Any | None) -> None:
        if artist is None:
            return
        remove = getattr(artist, "remove", None)
        if remove is None:
            return
        try:
            remove()
        except ValueError:
            pass

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
        if canvas is None:
            return
        if self._draw_idle_batch_depth > 0:
            if not any(pending is canvas for pending in self._draw_idle_pending_canvases):
                self._draw_idle_pending_canvases.append(canvas)
            return
        canvas.draw_idle()

    @contextmanager
    def batch_draw_idle(self) -> Iterator[None]:
        self._draw_idle_batch_depth += 1
        try:
            yield
        finally:
            self._draw_idle_batch_depth -= 1
            if self._draw_idle_batch_depth == 0:
                pending = self._draw_idle_pending_canvases
                self._draw_idle_pending_canvases = []
                for canvas in pending:
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

    def _finite_line_xy_arrays(self, line: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        try:
            xdata = np.asarray(line.get_xdata(), dtype=float).ravel()
            ydata = np.asarray(line.get_ydata(), dtype=float).ravel()
        except (TypeError, ValueError):
            return self._finite_line_xy_arrays_fallback(line)
        count = min(xdata.size, ydata.size)
        if count == 0:
            return None
        xdata = xdata[:count]
        ydata = ydata[:count]
        finite = np.isfinite(xdata) & np.isfinite(ydata)
        if not np.any(finite):
            return None
        indices = np.flatnonzero(finite)
        return xdata[finite], ydata[finite], indices

    def _finite_line_xy_arrays_fallback(self, line: Any) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
        xs = []
        ys = []
        indices = []
        for index, (point_x, point_y) in enumerate(zip(line.get_xdata(), line.get_ydata())):
            try:
                px = float(point_x)
                py = float(point_y)
            except (TypeError, ValueError):
                continue
            if isfinite(px) and isfinite(py):
                xs.append(px)
                ys.append(py)
                indices.append(index)
        if not indices:
            return None
        return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float), np.asarray(indices, dtype=int)

    def _is_finite_box(self, start: tuple[float, float], end: tuple[float, float]) -> bool:
        return self._is_finite_pair(start[0], start[1]) and self._is_finite_pair(end[0], end[1])

    def _line_is_pickable(self, line: Any) -> bool:
        visible = getattr(line, "get_visible", lambda: True)()
        label = getattr(line, "get_label", lambda: "")()
        return bool(visible) and not str(label).startswith("_")

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
        ticks_location = self._matplotlib_axis_position(axes, location, lower="bottom", upper="top")
        if location == "origin":
            self._set_spine_position(spines, "bottom", ("data", 0))
            self._set_spine_visible(spines, "bottom", True)
            self._set_spine_visible(spines, "top", False)
            self._call_axis_method(xaxis, "set_ticks_position", ticks_location)
            self._call_axis_method(xaxis, "set_label_position", ticks_location)
            return True
        self._set_spine_position(spines, "bottom", ("outward", 0))
        self._set_spine_position(spines, "top", ("outward", 0))
        self._set_spine_visible(spines, "bottom", True)
        self._set_spine_visible(spines, "top", True)
        self._call_axis_method(xaxis, "set_ticks_position", ticks_location)
        self._call_axis_method(xaxis, "set_label_position", ticks_location)
        return True

    def _set_matplotlib_y_axis_location(self, axes: Any, location: YAxisLocation) -> bool:
        yaxis = getattr(axes, "yaxis", None)
        spines = getattr(axes, "spines", None)
        if yaxis is None and not spines:
            return False
        ticks_location = self._matplotlib_axis_position(axes, location, lower="left", upper="right")
        if location == "origin":
            self._set_spine_position(spines, "left", ("data", 0))
            self._set_spine_visible(spines, "left", True)
            self._set_spine_visible(spines, "right", False)
            self._call_axis_method(yaxis, "set_ticks_position", ticks_location)
            self._call_axis_method(yaxis, "set_label_position", ticks_location)
            return True
        self._set_spine_position(spines, "left", ("outward", 0))
        self._set_spine_position(spines, "right", ("outward", 0))
        self._set_spine_visible(spines, "left", True)
        self._set_spine_visible(spines, "right", True)
        self._call_axis_method(yaxis, "set_ticks_position", ticks_location)
        self._call_axis_method(yaxis, "set_label_position", ticks_location)
        return True

    def _matplotlib_axis_position(self, axes: Any, location: str, *, lower: str, upper: str) -> str:
        if not self.is_3d_axes(axes):
            return lower if location == "origin" else location
        if location in {"origin", lower}:
            return "lower"
        if location == upper:
            return "upper"
        return location

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
            try:
                method(value)
            except ValueError:
                pass

    def _get_legend(self, axes: Any) -> Any | None:
        return getattr(axes, "get_legend", lambda: None)()

    def _get_colorbar(self, axes: Any) -> Any | None:
        colorbar = getattr(axes, "_matlab_like_colorbar", None)
        removed = getattr(colorbar, "removed", False)
        return None if removed else colorbar

    def _latest_mappable(self, axes: Any) -> Any | None:
        candidates = [*getattr(axes, "images", []), *getattr(axes, "collections", [])]
        return candidates[-1] if candidates else None

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
