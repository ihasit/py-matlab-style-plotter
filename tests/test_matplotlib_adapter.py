import unittest

import matplotlib
import numpy as np

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from py_matlab_style_plotter import (
    ActiveAxesStyle,
    AxesLimits,
    BrushedPointsState,
    Camera3DState,
    CoordinateReadout,
    DataTip,
    MatplotlibAxesPlotter,
    PointerEvent,
    SelectedDataTipState,
    SelectedLineState,
)


class FakeAnnotation:
    def __init__(self, label, xy):
        self.label = label
        self.xy = xy
        self.removed = False
        self.visible = True
        self.kwargs = {}

    def remove(self):
        self.removed = True

    def get_visible(self):
        return self.visible

    def set_visible(self, value):
        self.visible = value


class FakePatch:
    def __init__(self, axes):
        self.axes = axes
        self.removed = False

    def remove(self):
        self.removed = True


class FakeLegend:
    def __init__(self, axes):
        self.axes = axes
        self.removed = False

    def remove(self):
        self.removed = True
        self.axes._legend = None


class FakeColorbar:
    def __init__(self, mappable, axes):
        self.mappable = mappable
        self.axes = axes
        self.removed = False

    def remove(self):
        self.removed = True


class FakeMappable:
    def __init__(self):
        self.autoscale_count = 0
        self.cmap_values = []

    def autoscale(self):
        self.autoscale_count += 1

    def set_cmap(self, value):
        self.cmap_values.append(value)


class FakeAutoscaleTypeErrorMappable(FakeMappable):
    def autoscale(self):
        self.autoscale_count += 1
        raise TypeError("You must first set_array for mappable")


class FakeScatter:
    def __init__(self, axes, args, kwargs):
        self.axes = axes
        self.args = args
        self.kwargs = kwargs
        self._label = str(kwargs.get("label", kwargs.get("DisplayName", "series")))
        self.removed = False
        self.visible = True

    def remove(self):
        self.removed = True
        if self.axes is not None and self in self.axes.collections:
            self.axes.collections.remove(self)

    def get_visible(self):
        return self.visible

    def set_visible(self, value):
        self.visible = value

    def get_label(self):
        return self._label


class FakeGridLine:
    def __init__(self, visible=False):
        self._visible = visible

    def get_visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value


class FakeSpine:
    def __init__(self, edgecolor="black", linewidth=1.0):
        self._edgecolor = edgecolor
        self._linewidth = linewidth
        self._visible = True
        self._position = ("outward", 0)

    def get_edgecolor(self):
        return self._edgecolor

    def set_edgecolor(self, value):
        self._edgecolor = value

    def get_linewidth(self):
        return self._linewidth

    def set_linewidth(self, value):
        self._linewidth = value

    def get_visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value

    def set_position(self, value):
        self._position = value


class FakeAxis:
    def __init__(self, minor_ticklines=None):
        self.ticks_position = None
        self.label_position = None
        self.minor_locator = None
        self.minor_ticklines = minor_ticklines if minor_ticklines is not None else []

    def set_ticks_position(self, value):
        self.ticks_position = value

    def set_label_position(self, value):
        self.label_position = value

    def set_minor_locator(self, locator):
        self.minor_locator = locator
        visible = locator.__class__.__name__ != "NullLocator"
        for line in self.minor_ticklines:
            line.set_visible(visible)


class FakeCanvas:
    def __init__(self):
        self.draw_count = 0
        self.toolbar = None

    def draw_idle(self):
        self.draw_count += 1


class FakeToolbar:
    def __init__(self, mode=""):
        self.mode = mode
        self.pan_count = 0
        self.zoom_count = 0

    def pan(self):
        self.pan_count += 1
        self.mode = ""

    def zoom(self):
        self.zoom_count += 1
        self.mode = ""


class FakeFigure:
    def __init__(self):
        self.canvas = FakeCanvas()
        self.axes = []
        self.colorbar_calls = []
        self.add_subplot_calls = []

    def colorbar(self, mappable, ax=None):
        colorbar = FakeColorbar(mappable, ax)
        self.colorbar_calls.append((mappable, ax, colorbar))
        return colorbar

    def add_subplot(self, *args):
        self.add_subplot_calls.append(args)
        axes = FakeAxes(figure=self)
        return axes


class FakeLine:
    def __init__(self, xdata, ydata, zdata=None, label="series", visible=True, linewidth=2.0, alpha=None, zorder=3.0):
        self._xdata = xdata
        self._ydata = ydata
        if zdata is not None:
            self.get_zdata = lambda: zdata
        self._label = label
        self._visible = visible
        self._linewidth = linewidth
        self._alpha = alpha
        self._zorder = zorder
        self.axes = None
        self.removed = False

    def get_xdata(self):
        return self._xdata

    def get_ydata(self):
        return self._ydata

    def get_label(self):
        return self._label

    def get_visible(self):
        return self._visible

    def set_visible(self, value):
        self._visible = value

    def get_linewidth(self):
        return self._linewidth

    def set_linewidth(self, value):
        self._linewidth = value

    def get_alpha(self):
        return self._alpha

    def set_alpha(self, value):
        self._alpha = value

    def get_zorder(self):
        return self._zorder

    def set_zorder(self, value):
        self._zorder = value

    def remove(self):
        self.removed = True
        if self.axes is not None and self in self.axes.lines:
            self.axes.lines.remove(self)


class FakeAxes:
    def __init__(self, with_spines=False, figure=None, is_3d=False):
        self.lines = []
        self.collections = []
        self.images = []
        self.patches = []
        self.figure = figure if figure is not None else FakeFigure()
        self.figure.axes.append(self)
        self.annotations = []
        self.is_3d = is_3d
        self._xlim = (0.0, 10.0)
        self._ylim = (0.0, 10.0)
        self._zlim = (0.0, 1.0)
        self._xticks = (0.0, 5.0, 10.0)
        self._yticks = (0.0, 5.0, 10.0)
        self._zticks = (0.0, 0.5, 1.0)
        self._xticklabels = ("0", "5", "10")
        self._yticklabels = ("0", "5", "10")
        self._zticklabels = ("0", "0.5", "1")
        self._clim = (0.0, 1.0)
        self._aspect = "auto"
        self._box_aspect = None
        self._axis_visible = True
        self._xaxis_inverted = False
        self._yaxis_inverted = False
        self._zaxis_inverted = False
        self._xscale = "linear"
        self._yscale = "linear"
        self._zscale = "linear"
        self._axisbelow = True
        self._tick_params = {}
        self._xgridlines = [FakeGridLine(False)]
        self._ygridlines = [FakeGridLine(False)]
        self._xminorgridlines = [FakeGridLine(False)]
        self._yminorgridlines = [FakeGridLine(False)]
        self.xaxis = FakeAxis(self._xminorgridlines)
        self.yaxis = FakeAxis(self._yminorgridlines)
        self._title = ""
        self._xlabel = ""
        self._ylabel = ""
        self._zlabel = ""
        self._legend = None
        self.dist = 10.0 if is_3d else None
        self.camera_position = (1.0, 2.0, 3.0) if is_3d else None
        self.camera_target = (4.0, 5.0, 6.0) if is_3d else None
        self.camera_up_vector = (0.0, 0.0, 1.0) if is_3d else None
        self.disable_mouse_rotation_count = 0
        self._proj_type = "ortho"
        self.plot_calls = []
        self.errorbar_calls = []
        self.scatter_calls = []
        self.stem_calls = []
        self.bar_calls = []
        self.fill_between_calls = []
        self.fill_calls = []
        self.hist_calls = []
        self.axvline_calls = []
        self.axhline_calls = []
        self.text_calls = []
        self.imshow_calls = []
        self.contour_calls = []
        self.contourf_calls = []
        self.plot_surface_calls = []
        self.plot_wireframe_calls = []
        self.quiver_calls = []
        self.pcolormesh_calls = []
        self.spy_calls = []
        self.relim_count = 0
        self.autoscale_view_calls = []
        self.spines = (
            {
                "left": FakeSpine("black", 1.0),
                "right": FakeSpine("gray", 0.8),
                "top": FakeSpine("gray", 0.8),
                "bottom": FakeSpine("black", 1.0),
            }
            if with_spines
            else {}
        )

    def cla(self):
        self.lines = []
        self.collections = []
        self.images = []
        self.patches = []
        for spine in self.spines.values():
            spine.set_edgecolor("black")
            spine.set_linewidth(1.0)

    def plot(self, x, y, *args, **kwargs):
        label = str(kwargs.get("label", "series"))
        z = None
        style_args = args
        if self.is_3d and args and not isinstance(args[0], str):
            z = tuple(args[0])
            style_args = args[1:]
        line = FakeLine(tuple(x), tuple(y), zdata=z, label=label)
        line.style_args = style_args
        line.kwargs = kwargs
        line.axes = self
        self.lines.append(line)
        if z is None:
            self.plot_calls.append((tuple(x), tuple(y), style_args, kwargs))
        else:
            self.plot_calls.append((tuple(x), tuple(y), z, style_args, kwargs))
        return [line]

    def relim(self):
        self.relim_count += 1

    def errorbar(self, x, y, yerr=None, **kwargs):
        line = FakeLine(tuple(x), tuple(y), label=str(kwargs.get("label", "series")))
        line.yerr = yerr
        line.kwargs = kwargs
        line.axes = self
        self.lines.append(line)
        self.errorbar_calls.append((tuple(x), tuple(y), yerr, kwargs))
        return line

    def scatter(self, x, y, z=None, **kwargs):
        args = (list(x), list(y)) if z is None else (list(x), list(y), list(z))
        collection = FakeScatter(self, args, kwargs)
        collection.x = tuple(x)
        collection.y = tuple(y)
        collection.z = None if z is None else tuple(z)
        collection.kwargs = kwargs
        self.collections.append(collection)
        if z is None:
            self.scatter_calls.append((tuple(x), tuple(y), kwargs))
        else:
            self.scatter_calls.append((tuple(x), tuple(y), tuple(z), kwargs))
        return collection

    def stem(self, x, y, *args, **kwargs):
        markerline = FakeLine(tuple(x), tuple(y), label=str(kwargs.get("label", "series")))
        stemlines = FakeLine(tuple(x), tuple(y))
        baseline = FakeLine(tuple(x), tuple(0.0 for _item in x))
        markerline.kwargs = kwargs
        stemlines.kwargs = kwargs
        baseline.kwargs = kwargs
        markerline.axes = self
        stemlines.axes = self
        baseline.axes = self
        self.lines.extend([markerline, stemlines, baseline])
        self.stem_calls.append((tuple(x), tuple(y), args, kwargs))
        return markerline, stemlines, baseline

    def bar(self, x, height, **kwargs):
        bars = []
        for x_value, height_value in zip(x, height):
            bar = FakePatch(self)
            bar.x = x_value
            bar.height = height_value
            bar.kwargs = kwargs
            bars.append(bar)
        self.patches.extend(bars)
        self.bar_calls.append((tuple(x), tuple(height), kwargs))
        return bars

    def fill_between(self, x, y1, y2=0, **kwargs):
        collection = FakeMappable()
        collection.x = tuple(x)
        collection.y1 = tuple(y1)
        collection.y2 = tuple(y2)
        collection.kwargs = kwargs
        self.collections.append(collection)
        self.fill_between_calls.append((tuple(x), tuple(y1), tuple(y2), kwargs))
        return collection

    def fill(self, x, y, **kwargs):
        patch = FakePatch(self)
        patch.x = tuple(x)
        patch.y = tuple(y)
        patch.kwargs = kwargs
        self.patches.append(patch)
        self.fill_calls.append((tuple(x), tuple(y), kwargs))
        return [patch]

    def hist(self, x, **kwargs):
        patches = [FakePatch(self)]
        counts = (1.0,)
        bins = tuple(kwargs.get("bins", (0.0, 1.0)))
        self.patches.extend(patches)
        self.hist_calls.append((tuple(x), kwargs))
        return counts, bins, patches

    def axvline(self, x=0, **kwargs):
        line = FakeLine((x, x), self._ylim, label=str(kwargs.get("label", "series")))
        line.kwargs = kwargs
        line.axes = self
        self.lines.append(line)
        self.axvline_calls.append((x, kwargs))
        return line

    def axhline(self, y=0, **kwargs):
        line = FakeLine(self._xlim, (y, y), label=str(kwargs.get("label", "series")))
        line.kwargs = kwargs
        line.axes = self
        self.lines.append(line)
        self.axhline_calls.append((y, kwargs))
        return line

    def text(self, *args, **kwargs):
        if len(args) == 3:
            x, y, value = args
            annotation = FakeAnnotation(value, (x, y))
        elif len(args) == 4:
            x, y, z, value = args
            annotation = FakeAnnotation(value, (x, y, z))
        else:
            raise TypeError("text expects 3 or 4 positional arguments")
        annotation.kwargs = kwargs
        self.text_calls.append((args, kwargs))
        return annotation

    def imshow(self, data, **kwargs):
        image = FakeMappable()
        image.data = tuple(tuple(row) for row in data)
        image.kwargs = kwargs
        self.images.append(image)
        self.imshow_calls.append((image.data, kwargs))
        return image

    def contour(self, *args, **kwargs):
        contour_artist = FakeMappable()
        contour_artist.args = args
        contour_artist.kwargs = kwargs
        self.contour_calls.append((args, kwargs))
        return contour_artist

    def contourf(self, *args, **kwargs):
        contourf_artist = FakeMappable()
        contourf_artist.args = args
        contourf_artist.kwargs = kwargs
        self.contourf_calls.append((args, kwargs))
        return contourf_artist

    def plot_surface(self, x, y, z, **kwargs):
        surface_artist = FakeMappable()
        surface_artist.x = x
        surface_artist.y = y
        surface_artist.z = z
        surface_artist.kwargs = kwargs
        self.plot_surface_calls.append((x, y, z, kwargs))
        return surface_artist

    def plot_wireframe(self, x, y, z, **kwargs):
        wireframe_artist = FakeMappable()
        wireframe_artist.x = x
        wireframe_artist.y = y
        wireframe_artist.z = z
        wireframe_artist.kwargs = kwargs
        self.plot_wireframe_calls.append((x, y, z, kwargs))
        return wireframe_artist

    def quiver(self, x, y, u, v, **kwargs):
        quiver_artist = FakeMappable()
        quiver_artist.x = x
        quiver_artist.y = y
        quiver_artist.u = u
        quiver_artist.v = v
        quiver_artist.kwargs = kwargs
        self.quiver_calls.append((x, y, u, v, kwargs))
        return quiver_artist

    def pcolormesh(self, *args, **kwargs):
        pcolor_artist = FakeMappable()
        pcolor_artist.args = args
        pcolor_artist.kwargs = kwargs
        self.pcolormesh_calls.append((args, kwargs))
        return pcolor_artist

    def spy(self, matrix, **kwargs):
        spy_artist = FakeMappable()
        spy_artist.matrix = matrix
        spy_artist.kwargs = kwargs
        self.spy_calls.append((matrix, kwargs))
        return spy_artist

    def autoscale_view(self, tight=False):
        self.autoscale_view_calls.append(tight)

    def get_xlim(self):
        return self._xlim

    def get_ylim(self):
        return self._ylim

    def get_zlim(self):
        if not self.is_3d:
            raise AttributeError("2D axes has no zlim")
        return self._zlim

    def set_xlim(self, left, right):
        self._xlim = (left, right)

    def set_ylim(self, bottom, top):
        self._ylim = (bottom, top)

    def set_zlim(self, bottom, top):
        self._zlim = (bottom, top)

    def get_xticks(self):
        return self._xticks

    def get_yticks(self):
        return self._yticks

    def get_zticks(self):
        return self._zticks

    def set_xticks(self, ticks):
        self._xticks = tuple(ticks)

    def set_yticks(self, ticks):
        self._yticks = tuple(ticks)

    def set_zticks(self, ticks):
        self._zticks = tuple(ticks)

    def get_xticklabels(self):
        return self._xticklabels

    def get_yticklabels(self):
        return self._yticklabels

    def get_zticklabels(self):
        return self._zticklabels

    def set_xticklabels(self, labels):
        self._xticklabels = tuple(labels)

    def set_yticklabels(self, labels):
        self._yticklabels = tuple(labels)

    def set_zticklabels(self, labels):
        self._zticklabels = tuple(labels)

    def get_clim(self):
        return self._clim

    def set_clim(self, bottom, top):
        self._clim = (bottom, top)

    def view_init(self, elev, azim, roll=0.0):
        self.elev = elev
        self.azim = azim
        self.roll = roll

    def get_proj_type(self):
        return self._proj_type

    def set_proj_type(self, projection):
        self._proj_type = projection

    def set_aspect(self, aspect):
        self._aspect = aspect

    def set_box_aspect(self, box_aspect):
        self._box_aspect = box_aspect

    def set_axis_on(self):
        self._axis_visible = True

    def set_axis_off(self):
        self._axis_visible = False

    def yaxis_inverted(self):
        return self._yaxis_inverted

    def xaxis_inverted(self):
        return self._xaxis_inverted

    def zaxis_inverted(self):
        return self._zaxis_inverted

    def invert_yaxis(self):
        self._yaxis_inverted = not self._yaxis_inverted

    def invert_xaxis(self):
        self._xaxis_inverted = not self._xaxis_inverted

    def invert_zaxis(self):
        self._zaxis_inverted = not self._zaxis_inverted

    def set_xscale(self, scale):
        self._xscale = scale

    def set_yscale(self, scale):
        self._yscale = scale

    def set_zscale(self, scale):
        self._zscale = scale

    def set_axisbelow(self, value):
        self._axisbelow = value

    def tick_params(self, **kwargs):
        which = kwargs.get("which", "major")
        self._tick_params.setdefault(which, {}).update(kwargs)
        axis = kwargs.get("axis")
        if axis is not None:
            self._tick_params.setdefault(axis, {}).update(kwargs)
        self._tick_params.update(kwargs)

    def get_title(self):
        return self._title

    def set_title(self, value):
        self._title = value

    def get_xlabel(self):
        return self._xlabel

    def set_xlabel(self, value):
        self._xlabel = value

    def get_ylabel(self):
        return self._ylabel

    def set_ylabel(self, value):
        self._ylabel = value

    def get_zlabel(self):
        return self._zlabel

    def set_zlabel(self, value):
        self._zlabel = value

    def annotate(self, label, xy, **kwargs):
        annotation = FakeAnnotation(label, xy)
        annotation.kwargs = kwargs
        self.annotations.append(annotation)
        return annotation

    def set_lines(self, lines):
        self.lines = lines
        for line in lines:
            line.axes = self

    def disable_mouse_rotation(self):
        self.disable_mouse_rotation_count += 1

    def grid(self, visible, which="major", axis="both"):
        if which == "minor":
            axis_lines = {"x": self._xminorgridlines, "y": self._yminorgridlines}
        else:
            axis_lines = {"x": self._xgridlines, "y": self._ygridlines}
        if axis == "both":
            lines = [*axis_lines["x"], *axis_lines["y"]]
        else:
            lines = axis_lines.get(axis, [])
        for line in lines:
            line.set_visible(visible)

    def get_xgridlines(self):
        return self._xgridlines

    def get_ygridlines(self):
        return self._ygridlines

    def get_xminorticklines(self):
        return self._xminorgridlines

    def get_yminorticklines(self):
        return self._yminorgridlines

    def legend(self):
        self._legend = FakeLegend(self)
        return self._legend

    def get_legend(self):
        return self._legend


class RecordingCoordinatePlotter(MatplotlibAxesPlotter):
    def __init__(self, axes=None):
        self.readout_changes = []
        super().__init__(axes)

    def on_coordinate_readout_changed(self, readout):
        self.readout_changes.append(readout)


class MatplotlibAxesPlotterDataCursorTest(unittest.TestCase):
    def test_plot_draws_matlab_like_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        stale_line = FakeLine([0.0], [0.0], label="old")
        axes.set_lines([stale_line])
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.plot([0, 1], [2, 3], "k:", [4, 5], label="signal", linewidth=2)

        self.assertNotIn(stale_line, axes.lines)
        self.assertEqual(len(artists), 2)
        self.assertEqual(
            axes.plot_calls,
            [
                ((0.0, 1.0), (2.0, 3.0), (), {"color": "k", "linestyle": ":", "label": "signal", "linewidth": 2}),
                ((1.0, 2.0), (4.0, 5.0), (), {"color": plotter.DEFAULT_COLOR_ORDER[0], "linestyle": "-", "label": "signal", "linewidth": 2}),
            ],
        )
        # The plot lifecycle autoscales via autoscale_view only; data limits are
        # tracked incrementally (and cla resets them), so no O(N) relim is needed.
        self.assertEqual(axes.relim_count, 0)
        self.assertEqual(axes.autoscale_view_calls, [False])
        self.assertGreater(axes.figure.canvas.draw_count, 0)

    def test_plot_respects_matplotlib_hold_add(self):
        axes = FakeAxes()
        existing = FakeLine([0.0], [0.0], label="old")
        axes.set_lines([existing])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.hold("on")

        plotter.plot([7, 8])

        self.assertFalse(existing.removed)
        self.assertEqual(len(axes.lines), 2)
        self.assertEqual(axes.plot_calls[0][0], (1.0, 2.0))
        self.assertEqual(axes.plot_calls[0][1], (7.0, 8.0))

    def test_plot_accepts_positional_matplotlib_axes(self):
        axes1 = FakeAxes()
        axes2 = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes1)

        artists = plotter.plot(axes2, [1, 2], [3, 4])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(len(artists), 1)
        self.assertEqual(axes1.plot_calls, [])
        self.assertEqual(axes2.plot_calls, [((1.0, 2.0), (3.0, 4.0), (), {"color": plotter.DEFAULT_COLOR_ORDER[0], "linestyle": "-"})])

    def test_plot_default_color_order_is_passed_to_matplotlib(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.plot([[1, 10], [2, 20]])

        self.assertEqual(
            axes.plot_calls,
            [
                ((1.0, 2.0), (1.0, 2.0), (), {"color": plotter.DEFAULT_COLOR_ORDER[0], "linestyle": "-"}),
                ((1.0, 2.0), (10.0, 20.0), (), {"color": plotter.DEFAULT_COLOR_ORDER[1], "linestyle": "-"}),
            ],
        )

    def test_plot_matrix_columns_create_multiple_matplotlib_lines(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.plot([10, 20, 30], [[1, 10], [2, 20], [3, 30]], "x")

        self.assertEqual(len(artists), 2)
        self.assertEqual(
            axes.plot_calls,
            [
                ((10.0, 20.0, 30.0), (1.0, 2.0, 3.0), (), {"marker": "x", "color": plotter.DEFAULT_COLOR_ORDER[0], "linestyle": "-"}),
                ((10.0, 20.0, 30.0), (10.0, 20.0, 30.0), (), {"marker": "x", "color": plotter.DEFAULT_COLOR_ORDER[1], "linestyle": "-"}),
            ],
        )

    def test_normalize_plot_args_preserves_numpy_vector_without_tuple_copy(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)
        x = np.linspace(0.0, 1.0, 8)
        y = np.linspace(1.0, 2.0, 8)

        series = plotter.normalize_plot_args((x, y))

        self.assertIs(series[0].x, x)
        self.assertIs(series[0].y, y)

    def test_normalize_plot_args_uses_numpy_matrix_column_views(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)
        x = np.linspace(0.0, 1.0, 8)
        y = np.column_stack((np.sin(x), np.cos(x)))

        series = plotter.normalize_plot_args((x, y))

        self.assertEqual(len(series), 2)
        self.assertTrue(np.shares_memory(series[0].y, y))
        self.assertTrue(np.shares_memory(series[1].y, y))

    def test_plot_matlab_name_value_properties_map_to_matplotlib_kwargs(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.plot([1, 2], [3, 4], "r--", "LineWidth", 2, "DisplayName", "signal")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.plot_calls,
            [((1.0, 2.0), (3.0, 4.0), (), {"color": "r", "linestyle": "--", "linewidth": 2, "label": "signal"})],
        )

    def test_semilog_helpers_plot_and_set_matplotlib_axis_scales(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.semilogx([1, 10], [2, 3])
        self.assertEqual(axes._xscale, "log")
        self.assertEqual(axes._yscale, "linear")

        plotter.semilogy([1, 10], [2, 3])
        self.assertEqual(axes._xscale, "linear")
        self.assertEqual(axes._yscale, "log")

        plotter.loglog([1, 10], [2, 3])
        self.assertEqual(axes._xscale, "log")
        self.assertEqual(axes._yscale, "log")
        self.assertEqual(len(axes.plot_calls), 3)

    def test_plot3_draws_matlab_like_series_through_matplotlib_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.plot3([1, 2], [3, 4], [5, 6], "r--", "DisplayName", "path")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.plot_calls,
            [
                (
                    (1.0, 2.0),
                    (3.0, 4.0),
                    (5.0, 6.0),
                    (),
                    {"color": "r", "linestyle": "--", "label": "path"},
                )
            ],
        )

    def test_stairs_draws_expanded_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.stairs([1, 2, 3], [10, 20, 30], "r--")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.plot_calls,
            [
                (
                    (1.0, 2.0, 2.0, 3.0, 3.0),
                    (10.0, 10.0, 20.0, 20.0, 30.0),
                    (),
                    {"color": "r", "linestyle": "--"},
                )
            ],
        )

    def test_line_draws_without_nextplot_clear_or_default_series_order(self):
        axes = FakeAxes()
        existing = FakeLine([0], [0], label="old")
        axes.set_lines([existing])
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.line([1, 2], [3, 4], "Color", "red")

        self.assertEqual(len(artists), 1)
        self.assertIn(existing, axes.lines)
        self.assertEqual(axes.plot_calls, [((1.0, 2.0), (3.0, 4.0), (), {"color": "red"})])

    def test_line_draws_3d_primitive_through_matplotlib_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.line([1, 2], [3, 4], [5, 6], "LineStyle", "--")

        self.assertEqual(axes.plot_calls, [((1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (), {"linestyle": "--"})])

    def test_errorbar_draws_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.errorbar([1, 2], [10, 20], [0.5, 1.0], [1.5, 2.0], "r--", "DisplayName", "err")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.errorbar_calls,
            [
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    ((0.5, 1.0), (1.5, 2.0)),
                    {"color": "r", "linestyle": "--", "label": "err"},
                )
            ],
        )

    def test_scatter_draws_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.scatter([1, 2], [10, 20], [25, 36], [1, 0, 0], "LineStyle", "--", "DisplayName", "pts")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.scatter_calls,
            [
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    {"label": "pts", "s": (25.0, 36.0), "c": (1.0, 0.0, 0.0)},
                )
            ],
        )

    def test_scatter3_draws_series_with_size_and_color(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.scatter3([1, 2], [10, 20], [3, 4], 32, "#D95319", "DisplayName", "pts3")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.scatter_calls,
            [
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    (3.0, 4.0),
                    {"label": "pts3", "s": 32.0, "c": "#D95319"},
                )
            ],
        )

    def test_stem_draws_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.stem([1, 2], [10, 20], "r--o", "DisplayName", "stem")

        self.assertEqual(len(artists), 3)
        self.assertEqual(
            axes.stem_calls,
            [
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    ("r--o",),
                    {"label": "stem"},
                )
            ],
        )

    def test_stem_draws_through_real_matplotlib_axes(self):
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.stem([1, 2], [10, 20], "r--o", "DisplayName", "stem")

        self.assertGreaterEqual(len(artists), 3)
        self.assertEqual(axes.get_legend_handles_labels()[1], ["stem"])
        plt.close(fig)

    def test_bar_draws_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.bar([1, 2], [10, 20], "r--o", "DisplayName", "bars")

        self.assertEqual(len(artists), 2)
        self.assertEqual(
            axes.bar_calls,
            [
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    {"color": "r", "label": "bars"},
                )
            ],
        )

    def test_area_draws_stacked_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.area([1, 2], [[10, 100], [20, 200]], "r--o", "DisplayName", "area")

        self.assertEqual(len(artists), 2)
        self.assertEqual(
            axes.fill_between_calls,
            [
                (
                    (1.0, 2.0),
                    (0.0, 0.0),
                    (10.0, 20.0),
                    {"color": "r", "label": "area", "facecolor": "r"},
                ),
                (
                    (1.0, 2.0),
                    (10.0, 20.0),
                    (110.0, 220.0),
                    {"color": "r", "label": "area", "facecolor": "r"},
                ),
            ],
        )

    def test_fill_draws_polygon_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.fill([0, 1, 0], [0, 0, 1], "r", "DisplayName", "triangle")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.fill_calls,
            [
                (
                    (0.0, 1.0, 0.0),
                    (0.0, 0.0, 1.0),
                    {"facecolor": "r", "label": "triangle"},
                )
            ],
        )

    def test_histogram_draws_series_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.histogram([1, 2, 2, 3], [0, 2, 4], "DisplayName", "hist")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.hist_calls,
            [
                (
                    (1.0, 2.0, 2.0, 3.0),
                    {"label": "hist", "color": plotter.DEFAULT_COLOR_ORDER[0], "bins": (0.0, 2.0, 4.0)},
                )
            ],
        )

    def test_constant_lines_draw_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        x_artists = plotter.xline([1, 2], "r--", "limit", "LineWidth", 2)
        y_artists = plotter.yline(3, "k:", "threshold")

        self.assertEqual(len(x_artists), 2)
        self.assertEqual(len(y_artists), 1)
        self.assertEqual(
            axes.axvline_calls,
            [
                (1.0, {"color": "r", "linestyle": "--", "linewidth": 2, "label": "limit"}),
                (2.0, {"color": "r", "linestyle": "--", "linewidth": 2, "label": "limit"}),
            ],
        )
        self.assertEqual(axes.axhline_calls, [(3.0, {"color": "k", "linestyle": ":", "label": "threshold"})])

    def test_text_draws_annotation_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.text(1, 2, ["hello", "world"], "Color", "red")

        self.assertEqual(len(artists), 1)
        self.assertEqual(axes.text_calls, [((1.0, 2.0, "hello\nworld"), {"color": "red"})])

    def test_text_draws_3d_annotation_through_matplotlib_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.text(1, 2, 3, "label")

        self.assertEqual(len(artists), 1)
        self.assertEqual(axes.text_calls, [((1.0, 2.0, 3.0, "label"), {})])

    def test_imagesc_draws_scaled_image_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.imagesc([10, 20], [30, 40], [[1, 2], [3, 4]], "DisplayName", "img")

        self.assertEqual(len(artists), 1)
        self.assertEqual(
            axes.imshow_calls,
            [
                (
                    ((1.0, 2.0), (3.0, 4.0)),
                    {"label": "img", "origin": "upper", "aspect": "auto", "extent": (10.0, 20.0, 40.0, 30.0)},
                )
            ],
        )
        self.assertEqual(axes.images, artists)

    def test_contour_draws_contour_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.contour([10, 20], [30, 40], [[1, 2], [3, 4]], "DisplayName", "contour1")

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.contour_calls), 1)
        args, kwargs = axes.contour_calls[0]
        self.assertEqual(args, ((10.0, 20.0), (30.0, 40.0), ((1.0, 2.0), (3.0, 4.0)),))
        self.assertEqual(kwargs.get("label"), "contour1")


    def test_contourf_draws_filled_contour_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.contourf([10, 20], [30, 40], [[1, 2], [3, 4]], "DisplayName", "contourf1")

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.contourf_calls), 1)
        args, kwargs = axes.contourf_calls[0]
        self.assertEqual(args, ((10.0, 20.0), (30.0, 40.0), ((1.0, 2.0), (3.0, 4.0)),))
        self.assertEqual(kwargs.get("label"), "contourf1")

    def test_surf_draws_surface_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.surf([[1, 2], [3, 4]], "DisplayName", "surf1")

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.plot_surface_calls), 1)

    def test_mesh_draws_wireframe_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.mesh([[1, 2], [3, 4]])

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.plot_wireframe_calls), 1)

    def test_quiver_draws_vector_field_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.quiver([10, 20], [30, 40], [1, 2], [3, 4], "DisplayName", "field1")

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.quiver_calls), 1)


    def test_spy_draws_sparsity_pattern_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.spy([[0, 1], [1, 0]])

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.spy_calls), 1)

    def test_pcolor_draws_pseudocolor_through_matplotlib_axes(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        artists = plotter.pcolor([[1, 2], [3, 4]], "DisplayName", "pc1")

        self.assertEqual(len(artists), 1)
        self.assertEqual(len(axes.pcolormesh_calls), 1)
    def test_subplot_creates_axes_through_matplotlib_figure(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        ax = plotter.subplot(2, 3, 1)
        self.assertEqual(axes.figure.add_subplot_calls, [(2, 3, 1)])
        self.assertIs(plotter.active_axes, ax)

        ax_again = plotter.subplot(2, 3, 1)
        self.assertIs(ax_again, ax)
        self.assertEqual(len(axes.figure.add_subplot_calls), 1)

    def test_plot_line_spec_properties_are_overridden_by_name_value(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.plot([1, 2], [3, 4], "r--o", "Color", "blue")

        self.assertEqual(
            axes.plot_calls,
            [((1.0, 2.0), (3.0, 4.0), (), {"color": "blue", "linestyle": "--", "marker": "o"})],
        )

    def test_plot_unparsed_line_spec_is_passed_as_raw_style(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.plot([1, 2], [3, 4], "custom-style")

        self.assertEqual(axes.plot_calls, [((1.0, 2.0), (3.0, 4.0), ("custom-style",), {})])

    def test_prepare_replace_clears_target_axes_interaction_state(self):
        axes1 = FakeAxes()
        axes2 = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([2.0], [2.0], label="b")
        axes1.set_lines([line1])
        axes2.set_lines([line2])
        plotter = MatplotlibAxesPlotter(axes1)
        plotter.create_data_tip(axes1, 1.0, 1.0)
        plotter.create_data_tip(axes2, 2.0, 2.0)
        plotter.select_line(line1)
        plotter.select_line(line2)
        plotter.update_coordinate_readout(axes1, 1.0, 1.0)
        zoom_patch = FakePatch(axes1)
        brush_patch = FakePatch(axes1)
        plotter._zoom_box_artist = zoom_patch
        plotter._brush_box_artist = brush_patch

        plotter.prepare_for_plot(axes1)

        self.assertEqual(axes1.lines, [])
        self.assertEqual(len(plotter.data_tips), 1)
        self.assertIs(plotter.data_tips[0].axes, axes2)
        self.assertTrue(axes1.annotations[0].removed)
        self.assertFalse(axes2.annotations[0].removed)
        self.assertFalse(plotter.is_line_selected(line1))
        self.assertTrue(plotter.is_line_selected(line2))
        self.assertIsNone(plotter.coordinate_readout)
        self.assertTrue(zoom_patch.removed)
        self.assertTrue(brush_patch.removed)

    def test_prepare_replace_resets_matplotlib_axes_properties(self):
        axes = FakeAxes(with_spines=True)
        axes.set_lines([FakeLine([1.0], [1.0], label="signal")])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.axis("equal")
        plotter.axis("square")
        plotter.axis("off")
        plotter.axis("ij")
        plotter.grid("on")
        plotter.box("off")
        plotter.legend("on")

        plotter.prepare_for_plot(axes)

        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")
        self.assertTrue(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "normal")
        self.assertEqual(axes._aspect, "auto")
        self.assertIsNone(axes._box_aspect)
        self.assertTrue(axes._axis_visible)
        self.assertFalse(axes.yaxis_inverted())
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))
        self.assertTrue(all(spine.get_visible() for spine in axes.spines.values()))
        self.assertIsNone(axes.get_legend())

    def test_prepare_replacechildren_clears_interaction_state_and_removes_children(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        patch = FakePatch(axes)
        axes.patches = [patch]
        plotter = MatplotlibAxesPlotter(axes)
        plotter.create_data_tip(axes, 1.0, 1.0)
        plotter.select_line(line)
        plotter.set_next_plot("replacechildren")

        plotter.prepare_for_plot(axes)

        self.assertEqual(axes.lines, [])
        self.assertTrue(patch.removed)
        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(plotter.selected_lines, [])

    def test_find_nearest_line_point_uses_normalized_axis_distance(self):
        axes = FakeAxes()
        close_by_normalized_distance = FakeLine([1.0], [9.0], label="far y")
        nearest = FakeLine([2.0, 8.0], [2.0, 8.0], label="main")
        axes.set_lines([close_by_normalized_distance, nearest])
        plotter = MatplotlibAxesPlotter(axes)

        line, index, x, y, z = plotter.find_nearest_line_point(axes, 2.2, 2.4)

        self.assertIs(line, nearest)
        self.assertEqual(index, 0)
        self.assertEqual((x, y), (2.0, 2.0))
        self.assertIsNone(z)

    def test_find_nearest_line_point_skips_nonfinite_points_and_keeps_original_index(self):
        axes = FakeAxes()
        line = FakeLine([0.0, float("nan"), 4.0], [0.0, 2.0, 4.0], label="series")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        nearest = plotter.find_nearest_line_point(axes, 3.9, 4.1)

        self.assertIsNotNone(nearest)
        found_line, index, x, y, z = nearest
        self.assertIs(found_line, line)
        self.assertEqual(index, 2)
        self.assertEqual((x, y), (4.0, 4.0))
        self.assertIsNone(z)

    def test_find_nearest_line_point_uses_fallback_for_mixed_data(self):
        axes = FakeAxes()
        line = FakeLine([0.0, "bad", 4.0], [0.0, 2.0, 4.0], label="series")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        nearest = plotter.find_nearest_line_point(axes, 4.0, 4.0)

        self.assertIsNotNone(nearest)
        _line, index, x, y, _z = nearest
        self.assertEqual(index, 2)
        self.assertEqual((x, y), (4.0, 4.0))

    def test_create_data_tip_marks_scatter_point(self):
        axes = FakeAxes()
        collection = axes.scatter([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], label="dots")
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 2.1, 4.2)

        self.assertEqual(len(plotter.data_tips), 1)
        tip = plotter.data_tips[0]
        self.assertIs(tip.line, collection)
        self.assertEqual(tip.index, 1)
        self.assertEqual((tip.x, tip.y, tip.z), (2.0, 4.0, None))
        self.assertEqual(tip.label, "Series: dots\nX: 2\nY: 4\nIndex: 2")

    def test_create_data_tip_marks_3d_scatter_point(self):
        axes = FakeAxes(is_3d=True)
        collection = axes.scatter([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], [0.5, 1.5, 2.5], label="space dots")
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 2.1, 4.2)

        tip = plotter.data_tips[0]
        self.assertIs(tip.line, collection)
        self.assertEqual((tip.x, tip.y, tip.z), (2.0, 4.0, 1.5))
        self.assertEqual(tip.label, "Series: space dots\nX: 2\nY: 4\nZ: 1.5\nIndex: 2")

    def test_create_data_tip_adds_annotation_and_stores_tip(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 2.1, 4.2)

        self.assertEqual(len(plotter.data_tips), 1)
        tip = plotter.data_tips[0]
        self.assertIsInstance(tip, DataTip)
        self.assertIs(tip.axes, axes)
        self.assertIs(tip.line, line)
        self.assertEqual(tip.index, 1)
        self.assertEqual(tip.x, 2.0)
        self.assertEqual(tip.y, 4.0)
        self.assertIsNone(tip.z)
        self.assertEqual(tip.label, "Series: quad\nX: 2\nY: 4\nIndex: 2")
        self.assertEqual(axes.annotations[0].label, tip.label)
        self.assertIs(tip.marker, axes.collections[0])
        self.assertEqual(tip.marker.args[:2], ([2.0], [4.0]))
        self.assertEqual(tip.marker.kwargs["label"], "_matlab_data_tip_marker")
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_create_data_tip_includes_3d_z_value(self):
        axes = FakeAxes(is_3d=True)
        line = FakeLine([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], [0.5, 1.5, 2.5], label="space")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 2.1, 4.2)

        tip = plotter.data_tips[0]
        self.assertEqual(tip.x, 2.0)
        self.assertEqual(tip.y, 4.0)
        self.assertEqual(tip.z, 1.5)
        self.assertEqual(tip.label, "Series: space\nX: 2\nY: 4\nZ: 1.5\nIndex: 2")
        self.assertEqual(axes.annotations[0].label, tip.label)
        self.assertEqual(tip.marker.args[:3], ([2.0], [4.0], [1.5]))

    def test_create_data_tip_ignores_duplicate_line_point(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 2.1, 4.2)
        plotter.create_data_tip(axes, 1.9, 3.8)

        self.assertEqual(len(plotter.data_tips), 1)
        self.assertEqual(len(axes.annotations), 1)
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_create_data_tip_replaces_existing_tip_by_default(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 1.0, 1.0)
        first_tip = plotter.data_tips[0]
        plotter.create_data_tip(axes, 3.0, 9.0)

        self.assertEqual(len(plotter.data_tips), 1)
        self.assertEqual(plotter.data_tips[0].index, 2)
        self.assertTrue(first_tip.annotation.removed)
        self.assertTrue(first_tip.marker.removed)

    def test_create_data_tip_with_control_adds_new_tip(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0, 3.0], [1.0, 4.0, 9.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 1.0, 1.0)
        plotter.create_data_tip(axes, 3.0, 9.0, frozenset({"control"}))

        self.assertEqual(len(plotter.data_tips), 2)
        self.assertEqual([tip.index for tip in plotter.data_tips], [0, 2])
        self.assertFalse(plotter.data_tips[0].annotation.removed)
        self.assertFalse(plotter.data_tips[0].marker.removed)

    def test_create_data_tip_ignores_clicks_outside_pick_tolerance(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 5.0, 5.0)

        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(axes.annotations, [])

    def test_create_data_tip_ignores_nonfinite_coordinates(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, float("nan"), 1.0)
        plotter.create_data_tip(axes, 1.0, float("inf"))

        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(axes.annotations, [])
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_data_tip_pick_tolerance_can_be_tuned(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.data_tip_pick_tolerance = 0.6

        plotter.create_data_tip(axes, 5.0, 5.0)

        self.assertEqual(len(plotter.data_tips), 1)

    def test_format_data_tip_omits_private_matplotlib_labels(self):
        plotter = MatplotlibAxesPlotter(FakeAxes())
        line = FakeLine([1], [2], label="_child0")

        self.assertEqual(plotter.format_data_tip(line, 0, 1.0, 2.0), "X: 1\nY: 2\nIndex: 1")

    def test_format_data_tip_can_include_z_value(self):
        plotter = MatplotlibAxesPlotter(FakeAxes())
        line = FakeLine([1], [2], [3], label="_child0")

        self.assertEqual(plotter.format_data_tip(line, 0, 1.0, 2.0, 3.0), "X: 1\nY: 2\nZ: 3\nIndex: 1")

    def test_create_data_tip_ignores_axes_without_lines(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.create_data_tip(axes, 1.0, 1.0)

        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(axes.annotations, [])
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_clear_data_tips_removes_only_requested_axes(self):
        axes1 = FakeAxes()
        axes2 = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([2.0], [2.0], label="b")
        axes1.set_lines([line1])
        axes2.set_lines([line2])
        plotter = MatplotlibAxesPlotter(axes1)
        plotter.create_data_tip(axes1, 1.0, 1.0)
        plotter.create_data_tip(axes2, 2.0, 2.0)

        plotter.clear_data_tips(axes1)

        self.assertTrue(axes1.annotations[0].removed)
        self.assertTrue(plotter.data_tips[0].marker in axes2.collections)
        self.assertFalse(axes2.annotations[0].removed)
        self.assertEqual(len(plotter.data_tips), 1)
        self.assertIs(plotter.data_tips[0].axes, axes2)

    def test_select_nearest_artist_highlights_single_line(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a", linewidth=2.0, alpha=0.6, zorder=4.0)
        line2 = FakeLine([8.0], [8.0], label="b", linewidth=3.0, alpha=0.5, zorder=5.0)
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_nearest_artist(axes, 1.1, 1.1, frozenset())

        self.assertEqual(len(plotter.selected_lines), 1)
        state = plotter.selected_lines[0]
        self.assertIsInstance(state, SelectedLineState)
        self.assertIs(state.line, line1)
        self.assertEqual(state.linewidth, 2.0)
        self.assertEqual(state.alpha, 0.6)
        self.assertEqual(state.zorder, 4.0)
        self.assertTrue(state.visible)
        self.assertIsNotNone(state.highlight)
        self.assertIn(state.highlight, axes.lines)
        self.assertEqual(state.highlight.kwargs["color"], "#FFD400")
        self.assertEqual(state.highlight.kwargs["label"], "_matlab_selection_highlight")
        self.assertGreater(line1.get_linewidth(), 2.0)
        self.assertEqual(line1.get_alpha(), 1.0)
        self.assertEqual(line1.get_zorder(), 1004.0)
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_select_nearest_artist_can_select_data_tip_marker(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0], [1.0, 4.0], label="quad", linewidth=2.0)
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.create_data_tip(axes, 2.0, 4.0)
        draw_count = axes.figure.canvas.draw_count

        plotter.select_nearest_artist(axes, 2.0, 4.0, frozenset())

        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(len(plotter.selected_data_tips), 1)
        state = plotter.selected_data_tips[0]
        self.assertIsInstance(state, SelectedDataTipState)
        self.assertIs(state.tip, plotter.data_tips[0])
        self.assertIs(state.highlight, axes.collections[-1])
        self.assertEqual(state.highlight.kwargs["label"], "_matlab_data_tip_selection")
        self.assertEqual(line.get_linewidth(), 2.0)
        self.assertEqual(axes.figure.canvas.draw_count, draw_count + 1)

    def test_delete_selected_can_remove_selected_data_tip_without_deleting_line(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0], [1.0, 4.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.create_data_tip(axes, 2.0, 4.0)
        tip = plotter.data_tips[0]
        plotter.select_nearest_artist(axes, 2.0, 4.0, frozenset())
        highlight = plotter.selected_data_tips[0].highlight

        deleted_count = plotter.delete_selected()

        self.assertEqual(deleted_count, 1)
        self.assertFalse(line.removed)
        self.assertEqual(axes.lines, [line])
        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(plotter.selected_data_tips, [])
        self.assertTrue(tip.annotation.removed)
        self.assertTrue(tip.marker.removed)
        self.assertTrue(highlight.removed)

    def test_toggle_selected_visibility_hides_selected_data_tip(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0], [1.0, 4.0], label="quad")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.create_data_tip(axes, 2.0, 4.0)
        tip = plotter.data_tips[0]
        plotter.select_nearest_artist(axes, 2.0, 4.0, frozenset())
        highlight = plotter.selected_data_tips[0].highlight

        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertFalse(tip.annotation.visible)
        self.assertFalse(tip.marker.visible)
        self.assertFalse(highlight.visible)
        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertTrue(tip.annotation.visible)
        self.assertTrue(tip.marker.visible)
        self.assertTrue(highlight.visible)

    def test_select_line_is_idempotent_for_selected_line(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a", linewidth=2.0, alpha=0.6, zorder=4.0)
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_line(line)
        highlight = plotter.selected_lines[0].highlight
        plotter.select_line(line)
        plotter.clear_selection()

        self.assertEqual(len(plotter.selected_lines), 0)
        self.assertTrue(highlight.removed)
        self.assertNotIn(highlight, axes.lines)
        self.assertEqual(line.get_linewidth(), 2.0)
        self.assertEqual(line.get_alpha(), 0.6)
        self.assertEqual(line.get_zorder(), 4.0)

    def test_selection_highlight_is_not_pickable(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a", linewidth=2.0, alpha=0.6, zorder=4.0)
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_line(line)
        highlight = plotter.selected_lines[0].highlight

        self.assertIs(plotter.find_nearest_line_point(axes, 1.0, 1.0)[0], line)
        self.assertNotEqual(plotter.find_nearest_line_point(axes, 1.0, 1.0)[0], highlight)

    def test_click_selected_line_without_modifier_is_noop(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a", linewidth=2.0, alpha=0.6, zorder=4.0)
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_nearest_artist(axes, 1.0, 1.0, frozenset())
        plotter.select_nearest_artist(axes, 1.0, 1.0, frozenset())

        self.assertTrue(plotter.is_line_selected(line))
        self.assertEqual(len(plotter.selected_lines), 1)
        self.assertEqual(line.get_linewidth(), 3.6)
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_select_without_modifier_replaces_previous_selection(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a", linewidth=2.0, alpha=0.6, zorder=4.0)
        line2 = FakeLine([8.0], [8.0], label="b", linewidth=3.0, alpha=0.5, zorder=5.0)
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_nearest_artist(axes, 1.0, 1.0, frozenset())
        plotter.select_nearest_artist(axes, 8.0, 8.0, frozenset())

        self.assertFalse(plotter.is_line_selected(line1))
        self.assertTrue(plotter.is_line_selected(line2))
        self.assertEqual(line1.get_linewidth(), 2.0)
        self.assertEqual(line1.get_alpha(), 0.6)
        self.assertEqual(line1.get_zorder(), 4.0)

    def test_shift_select_adds_and_toggles_selection(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([8.0], [8.0], label="b")
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.select_nearest_artist(axes, 1.0, 1.0, frozenset())
        plotter.select_nearest_artist(axes, 8.0, 8.0, frozenset({"shift"}))
        self.assertTrue(plotter.is_line_selected(line1))
        self.assertTrue(plotter.is_line_selected(line2))

        plotter.select_nearest_artist(axes, 1.0, 1.0, frozenset({"shift"}))
        self.assertFalse(plotter.is_line_selected(line1))
        self.assertTrue(plotter.is_line_selected(line2))

    def test_select_nearest_artist_ignores_nonfinite_coordinates(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line)

        plotter.select_nearest_artist(axes, float("nan"), 1.0, frozenset())
        plotter.select_nearest_artist(axes, 1.0, float("inf"), frozenset())

        self.assertTrue(plotter.is_line_selected(line))
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_brush_box_marks_points_without_selecting_entire_lines(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0, 2.0], [1.0, 2.0], label="inside")
        line2 = FakeLine([8.0, 9.0], [8.0, 9.0], label="outside")
        line3 = FakeLine([3.0, 7.0], [3.0, 7.0], label="crossing")
        axes.set_lines([line1, line2, line3])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.brush_box(axes, (0.5, 0.5), (3.5, 3.5), frozenset())

        self.assertFalse(plotter.is_line_selected(line1))
        self.assertFalse(plotter.is_line_selected(line2))
        self.assertFalse(plotter.is_line_selected(line3))
        self.assertEqual({state.line for state in plotter.brushed_points}, {line1, line3})
        self.assertEqual(line1.get_linewidth(), 2.0)
        self.assertEqual(line3.get_linewidth(), 2.0)

    def test_brush_box_highlights_only_points_inside_box(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0, 8.0], [1.0, 2.0, 8.0], label="series")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.brush_box(axes, (0.5, 0.5), (2.5, 2.5), frozenset())

        self.assertEqual(len(plotter.brushed_points), 1)
        state = plotter.brushed_points[0]
        self.assertIsInstance(state, BrushedPointsState)
        self.assertIs(state.line, line)
        self.assertEqual(state.indices, (0, 1))
        self.assertEqual(state.artist.args[:2], ([1.0, 2.0], [1.0, 2.0]))
        self.assertIn(state.artist, axes.collections)

    def test_brush_box_skips_nonfinite_points_and_keeps_original_indices(self):
        axes = FakeAxes()
        line = FakeLine([1.0, float("nan"), 2.0, 8.0], [1.0, 2.0, 2.0, 8.0], label="series")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.brush_box(axes, (0.5, 0.5), (2.5, 2.5), frozenset())

        self.assertEqual(len(plotter.brushed_points), 1)
        state = plotter.brushed_points[0]
        self.assertEqual(state.indices, (0, 2))
        self.assertEqual(state.artist.args[:2], ([1.0, 2.0], [1.0, 2.0]))

    def test_brush_box_replaces_or_adds_brushed_points_based_on_modifier(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([8.0], [8.0], label="b")
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line2)

        plotter.brush_box(axes, (0.0, 0.0), (2.0, 2.0), frozenset())
        self.assertFalse(plotter.is_line_selected(line1))
        self.assertFalse(plotter.is_line_selected(line2))
        self.assertEqual([state.line for state in plotter.brushed_points], [line1])

        plotter.brush_box(axes, (7.0, 7.0), (9.0, 9.0), frozenset({"shift"}))
        self.assertFalse(plotter.is_line_selected(line1))
        self.assertFalse(plotter.is_line_selected(line2))
        self.assertEqual({state.line for state in plotter.brushed_points}, {line1, line2})

    def test_brush_box_ignores_nonfinite_coordinates(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line)

        plotter.brush_box(axes, (float("nan"), 0.0), (2.0, 2.0), frozenset())
        plotter.brush_box(axes, (0.0, 0.0), (2.0, float("inf")), frozenset())

        self.assertTrue(plotter.is_line_selected(line))
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_empty_brush_box_without_selection_does_not_redraw(self):
        axes = FakeAxes()
        axes.set_lines([FakeLine([8.0], [8.0], label="outside")])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.brush_box(axes, (0.0, 0.0), (2.0, 2.0), frozenset())

        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_batch_draw_idle_coalesces_multiple_limit_redraws(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        with plotter.batch_draw_idle():
            plotter.set_limits(axes, AxesLimits((1.0, 2.0), (3.0, 4.0)))
            plotter.set_limits(axes, AxesLimits((2.0, 3.0), (4.0, 5.0)))

        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_empty_brush_box_clears_existing_selection_and_redraws(self):
        axes = FakeAxes()
        line = FakeLine([8.0], [8.0], label="outside")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line)

        plotter.brush_box(axes, (0.0, 0.0), (2.0, 2.0), frozenset())

        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(line.get_linewidth(), 2.0)
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_clear_selection_removes_brushed_point_highlights(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0], [1.0, 2.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.brush_box(axes, (0.0, 0.0), (2.0, 2.0), frozenset())
        scatter = plotter.brushed_points[0].artist

        plotter.clear_selection()

        self.assertEqual(plotter.brushed_points, [])
        self.assertTrue(scatter.removed)

    def test_toggle_selected_visibility_hides_brushed_point_highlights_for_selected_lines(self):
        axes = FakeAxes()
        line = FakeLine([1.0, 2.0], [1.0, 2.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.brush_box(axes, (0.0, 0.0), (2.0, 2.0), frozenset())
        scatter = plotter.brushed_points[0].artist
        plotter.select_line(line)

        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertFalse(scatter.visible)
        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertTrue(scatter.visible)

    def test_clear_selection_can_target_one_axes(self):
        axes1 = FakeAxes()
        axes2 = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([2.0], [2.0], label="b")
        axes1.set_lines([line1])
        axes2.set_lines([line2])
        plotter = MatplotlibAxesPlotter(axes1)
        plotter.select_line(line1)
        plotter.select_line(line2)

        plotter.clear_selection(axes1)

        self.assertFalse(plotter.is_line_selected(line1))
        self.assertTrue(plotter.is_line_selected(line2))
        self.assertEqual(line1.get_linewidth(), 2.0)
        self.assertGreater(line2.get_linewidth(), 2.0)

    def test_click_empty_space_clears_selection_without_modifier(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line)
        axes.set_lines([])

        plotter.select_nearest_artist(axes, 5.0, 5.0, frozenset())

        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(line.get_linewidth(), 2.0)

    def test_click_far_from_line_clears_selection_without_selecting_nearest_line(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([8.0], [8.0], label="b")
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line1)

        plotter.select_nearest_artist(axes, 5.0, 5.0, frozenset())

        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(line1.get_linewidth(), 2.0)
        self.assertEqual(line2.get_linewidth(), 2.0)

    def test_selection_pick_tolerance_can_be_tuned(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.selection_pick_tolerance = 0.3

        plotter.select_nearest_artist(axes, 3.0, 3.0, frozenset())

        self.assertTrue(plotter.is_line_selected(line))

    def test_toggle_selected_visibility_hides_and_restores_selected_lines(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a", visible=True)
        line2 = FakeLine([2.0], [2.0], label="b", visible=True)
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line1)
        plotter.select_line(line2)

        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertFalse(line1.get_visible())
        self.assertFalse(line2.get_visible())

        self.assertTrue(plotter.toggle_selected_visibility())
        self.assertTrue(line1.get_visible())
        self.assertTrue(line2.get_visible())

    def test_toggle_selected_visibility_returns_false_without_selection(self):
        plotter = MatplotlibAxesPlotter(FakeAxes())

        self.assertFalse(plotter.toggle_selected_visibility())

    def test_clear_selection_restores_original_visibility(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a", visible=False)
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line)
        line.set_visible(True)

        plotter.clear_selection()

        self.assertFalse(line.get_visible())

    def test_cancel_interaction_clears_mode_selection_and_readout(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_mode("select")
        plotter.select_line(line)
        plotter.update_coordinate_readout(axes, 1.0, 1.0)
        zoom_patch = FakePatch(axes)
        brush_patch = FakePatch(axes)
        plotter._zoom_box_artist = zoom_patch
        plotter._brush_box_artist = brush_patch

        plotter.cancel_interaction()

        self.assertEqual(plotter.mode.value, "none")
        self.assertEqual(plotter.selected_lines, [])
        self.assertIsNone(plotter.coordinate_readout)
        self.assertEqual(line.get_linewidth(), 2.0)
        self.assertTrue(zoom_patch.removed)
        self.assertTrue(brush_patch.removed)
        self.assertIsNone(plotter._zoom_box_artist)
        self.assertIsNone(plotter._brush_box_artist)

    def test_mode_change_deactivates_matplotlib_toolbar_pan_or_zoom(self):
        axes = FakeAxes()
        toolbar = FakeToolbar("pan/zoom")
        axes.figure.canvas.toolbar = toolbar
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_mode("rotate3d")

        self.assertEqual(toolbar.pan_count, 1)
        self.assertEqual(toolbar.zoom_count, 0)
        self.assertEqual(toolbar.mode, "")

        toolbar.mode = "zoom rect"
        plotter.set_mode("pan")

        self.assertEqual(toolbar.pan_count, 1)
        self.assertEqual(toolbar.zoom_count, 1)
        self.assertEqual(toolbar.mode, "")

    def test_mode_change_leaves_inactive_matplotlib_toolbar_alone(self):
        axes = FakeAxes()
        toolbar = FakeToolbar("")
        axes.figure.canvas.toolbar = toolbar
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_mode("zoom")

        self.assertEqual(toolbar.pan_count, 0)
        self.assertEqual(toolbar.zoom_count, 0)

    def test_delete_selected_removes_lines_and_related_data_tips(self):
        axes = FakeAxes()
        line1 = FakeLine([1.0], [1.0], label="a")
        line2 = FakeLine([2.0], [2.0], label="b")
        axes.set_lines([line1, line2])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.select_line(line1)
        plotter.create_data_tip(axes, 1.0, 1.0)
        plotter.create_data_tip(axes, 2.0, 2.0)

        deleted_count = plotter.delete_selected()

        self.assertEqual(deleted_count, 1)
        self.assertTrue(line1.removed)
        self.assertFalse(line2.removed)
        self.assertEqual(axes.lines, [line2])
        self.assertEqual(plotter.selected_lines, [])
        self.assertEqual(len(plotter.data_tips), 1)
        self.assertIs(plotter.data_tips[0].line, line2)
        self.assertTrue(axes.annotations[0].removed)
        self.assertFalse(axes.annotations[1].removed)

    def test_handle_delete_key_clears_data_tips_when_no_selection(self):
        axes = FakeAxes()
        line = FakeLine([1.0], [1.0], label="a")
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.create_data_tip(axes, 1.0, 1.0)
        marker = plotter.data_tips[0].marker

        handled = plotter.handle_delete_key()

        self.assertTrue(handled)
        self.assertEqual(plotter.data_tips, [])
        self.assertTrue(axes.annotations[0].removed)
        self.assertTrue(marker.removed)

    def test_handle_delete_key_returns_false_when_nothing_to_delete(self):
        plotter = MatplotlibAxesPlotter(FakeAxes())

        self.assertFalse(plotter.handle_delete_key())

    def test_toggle_grid_flips_active_axes_grid_state(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.toggle_grid()
        self.assertTrue(all(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))

        plotter.toggle_grid()
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))

    def test_grid_helper_sets_matplotlib_axes_grid_state(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.grid("on"))
        self.assertTrue(all(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))

        self.assertFalse(plotter.grid("off"))
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))

    def test_grid_minor_maps_to_matplotlib_minor_grid_state(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.grid("minor"))
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))
        self.assertTrue(all(line.get_visible() for line in [*axes.get_xminorticklines(), *axes.get_yminorticklines()]))

        self.assertFalse(plotter.grid("off"))
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xgridlines(), *axes.get_ygridlines()]))
        self.assertFalse(any(line.get_visible() for line in [*axes.get_xminorticklines(), *axes.get_yminorticklines()]))

    def test_axis_grid_helpers_map_to_matplotlib_axis_specific_grid_state(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.xgrid("on"))
        self.assertTrue(all(line.get_visible() for line in axes.get_xgridlines()))
        self.assertFalse(any(line.get_visible() for line in axes.get_ygridlines()))
        self.assertTrue(plotter.xgrid())
        self.assertFalse(plotter.ygrid())

        self.assertTrue(plotter.yminorgrid("on"))
        self.assertFalse(any(line.get_visible() for line in axes.get_xminorticklines()))
        self.assertTrue(all(line.get_visible() for line in axes.get_yminorticklines()))
        self.assertFalse(plotter.xminorgrid())
        self.assertTrue(plotter.yminorgrid())

    def test_minor_tick_helpers_map_to_axis_minor_locator_when_available(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.xminortick("on"))
        self.assertTrue(plotter.xminortick())
        self.assertFalse(plotter.yminortick())

        self.assertTrue(plotter.yminortick("on"))
        self.assertTrue(plotter.yminortick())
        self.assertFalse(plotter.xminortick("off"))
        self.assertFalse(plotter.xminortick())
        self.assertTrue(plotter.yminortick())

    def test_box_helper_sets_matplotlib_spine_visibility(self):
        axes = FakeAxes(with_spines=True)
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.box_is_enabled(axes))
        self.assertFalse(plotter.box("off"))
        self.assertFalse(any(spine.get_visible() for spine in axes.spines.values()))

        self.assertTrue(plotter.box("on"))
        self.assertTrue(all(spine.get_visible() for spine in axes.spines.values()))

    def test_box_helper_is_noop_without_spines(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.box("on"))
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_toggle_legend_creates_and_removes_legend(self):
        axes = FakeAxes()
        axes.set_lines([FakeLine([1.0], [1.0], label="signal")])
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.toggle_legend())
        legend = axes.get_legend()
        self.assertIsNotNone(legend)

        self.assertFalse(plotter.toggle_legend())
        self.assertTrue(legend.removed)
        self.assertIsNone(axes.get_legend())

    def test_legend_helper_sets_matplotlib_legend_state(self):
        axes = FakeAxes()
        axes.set_lines([FakeLine([1.0], [1.0], label="signal")])
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.legend("on"))
        legend = axes.get_legend()
        self.assertIsNotNone(legend)
        self.assertTrue(plotter.legend("on"))
        self.assertIs(axes.get_legend(), legend)

        self.assertFalse(plotter.legend("off"))
        self.assertTrue(legend.removed)
        self.assertIsNone(axes.get_legend())

    def test_colorbar_helper_creates_and_removes_matplotlib_colorbar(self):
        axes = FakeAxes()
        image = FakeMappable()
        axes.images = [image]
        plotter = MatplotlibAxesPlotter(axes)

        self.assertTrue(plotter.colorbar("on"))
        colorbar = getattr(axes, "_matlab_like_colorbar")
        self.assertIsNotNone(colorbar)
        self.assertEqual(axes.figure.colorbar_calls, [(image, axes, colorbar)])
        self.assertTrue(plotter.colorbar("on"))
        self.assertFalse(colorbar.removed)

        self.assertFalse(plotter.colorbar("off"))
        self.assertTrue(colorbar.removed)
        self.assertIsNone(getattr(axes, "_matlab_like_colorbar"))

    def test_colorbar_helper_ignores_axes_without_mappables(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertFalse(plotter.colorbar("on"))
        self.assertEqual(axes.figure.colorbar_calls, [])

    def test_colormap_applies_to_images_and_collections(self):
        axes = FakeAxes()
        image = FakeMappable()
        collection = FakeMappable()
        axes.images = [image]
        axes.collections = [collection]
        plotter = MatplotlibAxesPlotter(axes)

        plotter.colormap("hot")

        self.assertEqual(image.cmap_values, ["hot"])
        self.assertEqual(collection.cmap_values, ["hot"])
        self.assertEqual(plotter.colormap(), "hot")
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_toggle_legend_ignores_axes_without_public_labels(self):
        axes = FakeAxes()
        axes.set_lines([FakeLine([1.0], [1.0], label="_child0")])
        plotter = MatplotlibAxesPlotter(axes)

        self.assertFalse(plotter.toggle_legend())
        self.assertIsNone(axes.get_legend())

        self.assertFalse(plotter.legend("on"))
        self.assertIsNone(axes.get_legend())
        self.assertEqual(axes.figure.canvas.draw_count, 0)

    def test_toggle_link_x_axes_syncs_and_unlinks_figure_axes(self):
        figure = FakeFigure()
        axes1 = FakeAxes(figure=figure)
        axes2 = FakeAxes(figure=figure)
        plotter = MatplotlibAxesPlotter(axes1)

        self.assertTrue(plotter.toggle_link_x_axes())
        self.assertEqual(len(plotter._linked), 1)
        plotter.set_xlim(2.0, 4.0)
        self.assertEqual(axes1.get_xlim(), (2.0, 4.0))
        self.assertEqual(axes2.get_xlim(), (2.0, 4.0))

        self.assertFalse(plotter.toggle_link_x_axes())
        self.assertEqual(plotter._linked, [])
        plotter.set_xlim(5.0, 6.0)
        self.assertEqual(axes1.get_xlim(), (5.0, 6.0))
        self.assertEqual(axes2.get_xlim(), (2.0, 4.0))

    def test_toggle_link_axes_uses_matlab_style_initial_union(self):
        figure = FakeFigure()
        axes1 = FakeAxes(figure=figure)
        axes2 = FakeAxes(figure=figure)
        axes1.set_xlim(1.0, 2.0)
        axes2.set_xlim(10.0, 20.0)
        axes1.set_ylim(3.0, 4.0)
        axes2.set_ylim(30.0, 40.0)
        plotter = MatplotlibAxesPlotter(axes1)

        self.assertTrue(plotter.toggle_link_xy_axes())

        self.assertEqual(axes1.get_xlim(), (1.0, 20.0))
        self.assertEqual(axes2.get_xlim(), (1.0, 20.0))
        self.assertEqual(axes1.get_ylim(), (3.0, 40.0))
        self.assertEqual(axes2.get_ylim(), (3.0, 40.0))

    def test_toggle_link_x_axes_returns_false_for_single_axes_figure(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertFalse(plotter.toggle_link_x_axes())
        self.assertFalse(plotter.x_axes_linked)

    def test_axis_equal_normal_fill_and_square_map_to_matplotlib_aspects(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.axis("equal")
        self.assertEqual(axes._aspect, "equal")
        self.assertEqual(plotter.axis_aspect, "equal")

        plotter.axis("normal")
        self.assertEqual(axes._aspect, "auto")
        self.assertIsNone(axes._box_aspect)
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")

        plotter.axis("equal")
        plotter.axis("square")
        self.assertEqual(axes._box_aspect, 1)
        self.assertEqual(plotter.box_aspect, "square")

        plotter.axis("fill")
        self.assertEqual(axes._aspect, "auto")
        self.assertIsNone(axes._box_aspect)
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")

    def test_axis_square_uses_3d_box_aspect_tuple(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.axis("square")

        self.assertEqual(axes._box_aspect, (1, 1, 1))

    def test_axis_vis3d_uses_fixed_3d_box_aspect(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.axis("vis3d")

        self.assertEqual(axes._box_aspect, (1, 1, 1))
        self.assertEqual(plotter.box_aspect, "vis3d")

    def test_axis_on_and_off_map_to_matplotlib_axis_visibility(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.axis("off")
        self.assertFalse(axes._axis_visible)
        self.assertFalse(plotter.axis_visible)

        plotter.axis("on")
        self.assertTrue(axes._axis_visible)
        self.assertTrue(plotter.axis_visible)

    def test_axis_ij_and_xy_map_to_matplotlib_y_direction(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.axis("ij")
        self.assertTrue(axes.yaxis_inverted())
        self.assertEqual(plotter.y_direction, "reverse")

        plotter.axis("ij")
        self.assertTrue(axes.yaxis_inverted())

        plotter.axis("xy")
        self.assertFalse(axes.yaxis_inverted())
        self.assertEqual(plotter.y_direction, "normal")

    def test_xdir_ydir_zdir_map_to_matplotlib_axis_inversion(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.xdir("reverse")
        plotter.ydir("reverse")
        plotter.zdir("reverse")

        self.assertTrue(axes.xaxis_inverted())
        self.assertTrue(axes.yaxis_inverted())
        self.assertTrue(axes.zaxis_inverted())

        plotter.xdir("normal")
        plotter.ydir("normal")
        plotter.zdir("normal")

        self.assertFalse(axes.xaxis_inverted())
        self.assertFalse(axes.yaxis_inverted())
        self.assertFalse(axes.zaxis_inverted())

    def test_3d_axis_locations_map_to_matplotlib_lower_upper_positions(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_x_axis_location(axes, "bottom")
        plotter.set_y_axis_location(axes, "left")

        self.assertEqual(axes.xaxis.ticks_position, "lower")
        self.assertEqual(axes.yaxis.ticks_position, "lower")

        plotter.set_x_axis_location(axes, "top")
        plotter.set_y_axis_location(axes, "right")

        self.assertEqual(axes.xaxis.ticks_position, "upper")
        self.assertEqual(axes.yaxis.ticks_position, "upper")

    def test_xscale_yscale_zscale_map_to_matplotlib_axis_scale(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.xscale("log")
        plotter.yscale("log")
        plotter.zscale("log")

        self.assertEqual(axes._xscale, "log")
        self.assertEqual(axes._yscale, "log")
        self.assertEqual(axes._zscale, "log")

        plotter.xscale("linear")
        plotter.yscale("linear")
        plotter.zscale("linear")

        self.assertEqual(axes._xscale, "linear")
        self.assertEqual(axes._yscale, "linear")
        self.assertEqual(axes._zscale, "linear")

    def test_layer_and_tickdir_map_to_matplotlib_axisbelow_and_tick_params(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.layer("top")
        self.assertFalse(axes._axisbelow)
        plotter.layer("bottom")
        self.assertTrue(axes._axisbelow)

        plotter.tickdir("out")
        self.assertEqual(axes._tick_params["direction"], "out")
        plotter.tickdir("both")
        self.assertEqual(axes._tick_params["direction"], "both")

    def test_ticklength_maps_to_matplotlib_major_and_minor_tick_params(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.ticklength([0.02, 0.05])

        self.assertEqual(axes._tick_params["major"]["length"], 7.0)
        self.assertEqual(axes._tick_params["minor"]["length"], 17.5)

        plotter.ticklength([-0.01, 0.02])
        self.assertEqual(plotter.ticklength(), (-0.01, 0.02))
        self.assertEqual(axes._tick_params["major"]["length"], 3.5)
        self.assertEqual(axes._tick_params["minor"]["length"], 7.0)

    def test_axis_locations_map_to_matplotlib_spines_and_tick_positions(self):
        axes = FakeAxes(with_spines=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.xaxislocation("top")
        self.assertEqual(axes.xaxis.ticks_position, "top")
        self.assertEqual(axes.xaxis.label_position, "top")
        self.assertTrue(axes.spines["bottom"].get_visible())
        self.assertTrue(axes.spines["top"].get_visible())

        plotter.yaxislocation("right")
        self.assertEqual(axes.yaxis.ticks_position, "right")
        self.assertEqual(axes.yaxis.label_position, "right")
        self.assertTrue(axes.spines["left"].get_visible())
        self.assertTrue(axes.spines["right"].get_visible())

        plotter.xaxislocation("origin")
        self.assertEqual(axes.spines["bottom"]._position, ("data", 0))
        self.assertTrue(axes.spines["bottom"].get_visible())
        self.assertFalse(axes.spines["top"].get_visible())
        self.assertEqual(axes.xaxis.ticks_position, "bottom")

        plotter.yaxislocation("origin")
        self.assertEqual(axes.spines["left"]._position, ("data", 0))
        self.assertTrue(axes.spines["left"].get_visible())
        self.assertFalse(axes.spines["right"].get_visible())
        self.assertEqual(axes.yaxis.ticks_position, "left")

    def test_get_and_set_limits_include_3d_z_limits(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        self.assertEqual(plotter.get_limits(axes), AxesLimits((0.0, 10.0), (0.0, 10.0), (0.0, 1.0), (0.0, 1.0)))

        plotter.set_limits(axes, AxesLimits((1.0, 2.0), (3.0, 4.0), (5.0, 6.0), (7.0, 8.0)))

        self.assertEqual(axes.get_xlim(), (1.0, 2.0))
        self.assertEqual(axes.get_ylim(), (3.0, 4.0))
        self.assertEqual(axes.get_zlim(), (5.0, 6.0))
        self.assertEqual(axes.get_clim(), (7.0, 8.0))

    def test_ticks_helpers_map_to_matplotlib_ticks(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        self.assertEqual(plotter.xticks(), (0.0, 5.0, 10.0))
        self.assertEqual(plotter.yticks(), (0.0, 5.0, 10.0))
        self.assertEqual(plotter.zticks(), (0.0, 0.5, 1.0))

        plotter.xticks([1.0, 2.0, 3.0])
        plotter.yticks([])
        plotter.zticks([0.25, 0.75])

        self.assertEqual(axes.get_xticks(), (1.0, 2.0, 3.0))
        self.assertEqual(axes.get_yticks(), ())
        self.assertEqual(axes.get_zticks(), (0.25, 0.75))

    def test_ticklabels_helpers_map_to_matplotlib_ticklabels(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        self.assertEqual(plotter.xticklabels(), ("0", "5", "10"))
        self.assertEqual(plotter.yticklabels(), ("0", "5", "10"))
        self.assertEqual(plotter.zticklabels(), ("0", "0.5", "1"))

        plotter.xticklabels(["a", "b"])
        plotter.yticklabels([])
        plotter.zticklabels(["low", "high"])

        self.assertEqual(axes.get_xticklabels(), ("a", "b", ""))
        self.assertEqual(axes.get_yticklabels(), ("", "", ""))
        self.assertEqual(axes.get_zticklabels(), ("low", "high", ""))

    def test_ticklabel_rotation_helpers_map_to_matplotlib_tick_params(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.xticklabelrotation(45)
        plotter.yticklabelrotation(-30)
        plotter.zticklabelrotation(370)

        self.assertEqual(axes._tick_params["x"]["labelrotation"], 45.0)
        self.assertEqual(axes._tick_params["y"]["labelrotation"], -30.0)
        self.assertEqual(axes.zticklabel_rotation, 370.0)

        plotter.xticklabelrotation("auto")
        self.assertEqual(axes._tick_params["x"]["labelrotation"], 0.0)

    def test_title_and_axis_labels_map_to_matplotlib_text(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.title(["Main", "Subtitle"])
        plotter.xlabel("X Axis")
        plotter.ylabel("Y Axis")
        plotter.zlabel("Z Axis")

        self.assertEqual(axes.get_title(), "Main\nSubtitle")
        self.assertEqual(axes.get_xlabel(), "X Axis")
        self.assertEqual(axes.get_ylabel(), "Y Axis")
        self.assertEqual(axes.get_zlabel(), "Z Axis")
        self.assertEqual(plotter.title(), ("Main", "Subtitle"))

    def test_get_and_set_camera3d_include_matplotlib_view_distance(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        axes.azim = -37.5
        axes.elev = 30.0
        axes.roll = 0.0
        axes.dist = 10.0
        axes.camera_position = (1.0, 2.0, 3.0)
        axes.camera_target = (4.0, 5.0, 6.0)
        axes.camera_up_vector = (0.0, 0.0, 1.0)

        self.assertEqual(
            plotter.get_camera3d(axes),
            Camera3DState(
                azim=-37.5,
                elev=30.0,
                roll=0.0,
                view_angle=10.0,
                position=(1.0, 2.0, 3.0),
                target=(4.0, 5.0, 6.0),
                up_vector=(0.0, 0.0, 1.0),
            ),
        )

        plotter.set_camera3d(
            axes,
            Camera3DState(
                azim=45.0,
                elev=20.0,
                roll=5.0,
                view_angle=12.5,
                position=(7.0, 8.0, 9.0),
                target=(10.0, 11.0, 12.0),
                up_vector=(0.0, 1.0, 0.0),
            ),
        )

        self.assertEqual((axes.azim, axes.elev, axes.roll), (45.0, 20.0, 5.0))
        self.assertEqual(axes.dist, 12.5)
        self.assertEqual(axes.camera_position, (7.0, 8.0, 9.0))
        self.assertEqual(axes.camera_target, (10.0, 11.0, 12.0))
        self.assertEqual(axes.camera_up_vector, (0.0, 1.0, 0.0))

    def test_camera_projection_maps_matplotlib_projection_names(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        self.assertEqual(plotter.get_camera_projection(axes), "orthographic")

        plotter.set_camera_projection(axes, "perspective")

        self.assertEqual(axes.get_proj_type(), "persp")
        self.assertEqual(plotter.get_camera_projection(axes), "perspective")
        self.assertEqual(axes.figure.canvas.draw_count, 1)

        plotter.set_camera_projection(axes, "orthographic")

        self.assertEqual(axes.get_proj_type(), "ortho")
        self.assertEqual(plotter.get_camera_projection(axes), "orthographic")
        self.assertEqual(axes.figure.canvas.draw_count, 2)

    def test_restore_view_batches_matplotlib_redraws(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)
        plotter.push_current_view()
        plotter.set_xlim(1.0, 2.0)
        plotter.set_ylim(3.0, 4.0)
        draw_count_after_changes = axes.figure.canvas.draw_count

        self.assertTrue(plotter.home())

        self.assertEqual(axes.figure.canvas.draw_count, draw_count_after_changes + 1)
        self.assertEqual(axes.get_xlim(), (0.0, 10.0))
        self.assertEqual(axes.get_ylim(), (0.0, 10.0))

    def test_explicit_aspect_ratios_map_to_matplotlib_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_data_aspect_ratio(axes, (1.0, 2.0, 3.0))
        plotter.set_plot_box_aspect_ratio(axes, (3.0, 2.0, 1.0))

        self.assertEqual(axes._aspect, "auto")
        self.assertEqual(axes._box_aspect, (3.0, 2.0, 1.0))
        self.assertEqual(axes.figure.canvas.draw_count, 2)

    def test_explicit_2d_data_aspect_ratio_maps_to_float_aspect(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_data_aspect_ratio(axes, (2.0, 3.0, 1.0))

        self.assertEqual(axes._aspect, 1.5)
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_explicit_3d_data_aspect_ratio_maps_to_box_aspect(self):
        axes = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_data_aspect_ratio(axes, (1.0, 2.0, 3.0))

        self.assertEqual(axes._aspect, "auto")
        self.assertEqual(axes._box_aspect, (1.0, 2.0, 3.0))
        self.assertEqual(axes.figure.canvas.draw_count, 1)

    def test_set_clim_maps_to_matplotlib_color_limits(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        plotter.set_clim(0.25, 0.75)

        self.assertEqual(axes.get_clim(), (0.25, 0.75))
        self.assertEqual(plotter.clim_mode, "manual")

    def test_clim_auto_autoscales_images_and_collections(self):
        axes = FakeAxes()
        image = FakeMappable()
        collection = FakeMappable()
        axes.images = [image]
        axes.collections = [collection]
        plotter = MatplotlibAxesPlotter(axes)

        plotter.clim("auto")

        self.assertEqual(image.autoscale_count, 1)
        self.assertEqual(collection.autoscale_count, 1)
        self.assertEqual(plotter.clim_mode, "auto")

    def test_clim_auto_skips_mappables_without_array_data(self):
        axes = FakeAxes()
        image = FakeMappable()
        collection = FakeAutoscaleTypeErrorMappable()
        axes.images = [image]
        axes.collections = [collection]
        plotter = MatplotlibAxesPlotter(axes)

        plotter.clim("auto")

        self.assertEqual(image.autoscale_count, 1)
        self.assertEqual(collection.autoscale_count, 1)
        self.assertEqual(plotter.clim_mode, "auto")

    def test_caxis_maps_to_matplotlib_color_limit_behavior(self):
        axes = FakeAxes()
        image = FakeMappable()
        axes.images = [image]
        plotter = MatplotlibAxesPlotter(axes)

        plotter.caxis([0.25, 0.75])
        self.assertEqual(axes.get_clim(), (0.25, 0.75))
        self.assertEqual(plotter.caxis("mode"), "manual")

        plotter.caxis("auto")
        self.assertEqual(image.autoscale_count, 1)
        self.assertEqual(plotter.clim_mode, "auto")

    def test_toggle_link_y_axes_syncs_and_unlinks_figure_axes(self):
        figure = FakeFigure()
        axes1 = FakeAxes(figure=figure)
        axes2 = FakeAxes(figure=figure)
        plotter = MatplotlibAxesPlotter(axes1)

        self.assertTrue(plotter.toggle_link_y_axes())
        plotter.set_ylim(-2.0, 8.0)
        self.assertEqual(axes1.get_ylim(), (-2.0, 8.0))
        self.assertEqual(axes2.get_ylim(), (-2.0, 8.0))
        self.assertEqual(axes2.get_xlim(), (0.0, 10.0))

        self.assertFalse(plotter.toggle_link_y_axes())
        plotter.set_ylim(1.0, 3.0)
        self.assertEqual(axes1.get_ylim(), (1.0, 3.0))
        self.assertEqual(axes2.get_ylim(), (-2.0, 8.0))

    def test_toggle_link_xy_axes_syncs_both_limits(self):
        figure = FakeFigure()
        axes1 = FakeAxes(figure=figure)
        axes2 = FakeAxes(figure=figure)
        plotter = MatplotlibAxesPlotter(axes1)

        self.assertTrue(plotter.toggle_link_xy_axes())
        plotter.on_box_zoom(axes1, (2.0, 3.0), (6.0, 9.0))

        self.assertEqual(axes1.get_xlim(), (2.0, 6.0))
        self.assertEqual(axes1.get_ylim(), (3.0, 9.0))
        self.assertEqual(axes2.get_xlim(), (2.0, 6.0))
        self.assertEqual(axes2.get_ylim(), (3.0, 9.0))

    def test_box_zoom_preserves_fixed_aspect_axes_display_size(self):
        fig, axes = plt.subplots(figsize=(3, 3))
        try:
            axes.imshow(np.arange(100).reshape(10, 10))
            fig.canvas.draw()
            before = tuple(float(value) for value in axes.get_position().bounds)
            plotter = MatplotlibAxesPlotter(axes)

            plotter.on_box_zoom(axes, (2.0, 2.0), (4.0, 8.0))
            fig.canvas.draw()

            after = tuple(float(value) for value in axes.get_position().bounds)
            self.assertEqual(after, before)
            self.assertEqual(tuple(float(value) for value in axes.get_xlim()), (0.0, 6.0))
            self.assertEqual(tuple(float(value) for value in axes.get_ylim()), (2.0, 8.0))
        finally:
            plt.close(fig)

    def test_coordinate_readout_formats_and_stores_pointer_position(self):
        axes = FakeAxes()
        axes._title = "Main"
        plotter = MatplotlibAxesPlotter(axes)

        plotter.update_coordinate_readout(axes, 1.25, -3.5)

        self.assertIsInstance(plotter.coordinate_readout, CoordinateReadout)
        self.assertIs(plotter.coordinate_readout.axes, axes)
        self.assertEqual(plotter.coordinate_readout.x, 1.25)
        self.assertEqual(plotter.coordinate_readout.y, -3.5)
        self.assertIsNone(plotter.coordinate_readout.z)
        self.assertEqual(plotter.coordinate_readout.text, "Main: x=1.25, y=-3.5")

    def test_coordinate_readout_repeated_same_value_is_noop(self):
        axes = FakeAxes()
        plotter = RecordingCoordinatePlotter(axes)

        plotter.update_coordinate_readout(axes, 1.0, 2.0)
        plotter.update_coordinate_readout(axes, 1.0, 2.0)
        plotter.update_coordinate_readout(axes, 1.0, 2.5)

        self.assertEqual(len(plotter.readout_changes), 2)
        self.assertEqual(plotter.readout_changes[0].text, "x=1, y=2")
        self.assertEqual(plotter.readout_changes[1].text, "x=1, y=2.5")

    def test_mouse_move_coordinate_readout_is_throttled_by_screen_distance(self):
        axes = FakeAxes()
        plotter = RecordingCoordinatePlotter(axes)

        plotter.on_mouse_move(PointerEvent(axes=axes, x=10.0, y=10.0, xdata=1.0, ydata=2.0))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=11.0, y=11.0, xdata=1.1, ydata=2.1))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=14.0, y=10.0, xdata=1.4, ydata=2.0))

        self.assertEqual(len(plotter.readout_changes), 2)
        self.assertEqual(plotter.readout_changes[0].text, "x=1, y=2")
        self.assertEqual(plotter.readout_changes[1].text, "x=1.4, y=2")

    def test_mouse_move_coordinate_readout_throttle_can_be_disabled(self):
        axes = FakeAxes()
        plotter = RecordingCoordinatePlotter(axes)
        plotter.coordinate_readout_pixel_threshold = 0.0

        plotter.on_mouse_move(PointerEvent(axes=axes, x=10.0, y=10.0, xdata=1.0, ydata=2.0))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=11.0, y=11.0, xdata=1.1, ydata=2.1))

        self.assertEqual(len(plotter.readout_changes), 2)

    def test_coordinate_readout_ignores_nonfinite_coordinates(self):
        axes = FakeAxes()
        plotter = RecordingCoordinatePlotter(axes)

        plotter.update_coordinate_readout(axes, 1.0, 2.0)
        plotter.update_coordinate_readout(axes, float("nan"), 2.0)
        plotter.update_coordinate_readout(axes, 1.0, float("inf"))

        self.assertEqual(len(plotter.readout_changes), 1)
        self.assertEqual(plotter.coordinate_readout.text, "x=1, y=2")

    def test_coordinate_readout_includes_nearest_3d_z_value(self):
        axes = FakeAxes(is_3d=True)
        axes._title = "Cloud"
        line = FakeLine([1.0, 5.0], [2.0, 6.0], zdata=[3.0, 7.0])
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.update_coordinate_readout(axes, 1.1, 2.1)

        self.assertIsInstance(plotter.coordinate_readout, CoordinateReadout)
        self.assertEqual(plotter.coordinate_readout.z, 3.0)
        self.assertEqual(plotter.coordinate_readout.text, "Cloud: x=1.1, y=2.1, z=3")

    def test_coordinate_readout_omits_3d_z_when_no_line_z_is_available(self):
        axes = FakeAxes(is_3d=True)
        line = FakeLine([1.0], [2.0])
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.update_coordinate_readout(axes, 1.0, 2.0)

        self.assertIsNone(plotter.coordinate_readout.z)
        self.assertEqual(plotter.coordinate_readout.text, "x=1, y=2")

    def test_coordinate_readout_omits_3d_z_outside_pick_tolerance(self):
        axes = FakeAxes(is_3d=True)
        line = FakeLine([1.0], [2.0], zdata=[3.0])
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)

        plotter.update_coordinate_readout(axes, 8.0, 8.0)

        self.assertIsNone(plotter.coordinate_readout.z)
        self.assertEqual(plotter.coordinate_readout.text, "x=8, y=8")

    def test_coordinate_readout_z_tolerance_can_be_tuned(self):
        axes = FakeAxes(is_3d=True)
        line = FakeLine([1.0], [2.0], zdata=[3.0])
        axes.set_lines([line])
        plotter = MatplotlibAxesPlotter(axes)
        plotter.coordinate_readout_z_tolerance = 1.0

        plotter.update_coordinate_readout(axes, 8.0, 8.0)

        self.assertEqual(plotter.coordinate_readout.z, 3.0)
        self.assertEqual(plotter.coordinate_readout.text, "x=8, y=8, z=3")

    def test_clear_coordinate_readout_resets_state(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.update_coordinate_readout(axes, 1.0, 2.0)

        plotter.clear_coordinate_readout()

        self.assertIsNone(plotter.coordinate_readout)

    def test_clear_coordinate_readout_is_noop_when_already_empty(self):
        axes = FakeAxes()
        plotter = RecordingCoordinatePlotter(axes)

        plotter.clear_coordinate_readout()
        plotter.update_coordinate_readout(axes, 1.0, 2.0)
        plotter.clear_coordinate_readout()
        plotter.clear_coordinate_readout()

        self.assertEqual(len(plotter.readout_changes), 2)
        self.assertIsInstance(plotter.readout_changes[0], CoordinateReadout)
        self.assertIsNone(plotter.readout_changes[1])

    def test_active_axes_highlight_applies_and_restores_spines(self):
        axes1 = FakeAxes(with_spines=True)
        axes2 = FakeAxes(with_spines=True)
        plotter = MatplotlibAxesPlotter(axes1)
        plotter.set_active_axes_highlight_enabled(True)

        self.assertIsInstance(plotter.active_axes_style, ActiveAxesStyle)
        self.assertEqual(axes1.spines["left"].get_edgecolor(), "#0072BD")
        self.assertEqual(axes1.spines["left"].get_linewidth(), 1.8)

        plotter.set_active_axes(axes2)

        self.assertEqual(axes1.spines["left"].get_edgecolor(), "black")
        self.assertEqual(axes1.spines["left"].get_linewidth(), 1.0)
        self.assertEqual(axes2.spines["left"].get_edgecolor(), "#0072BD")
        self.assertEqual(axes2.spines["left"].get_linewidth(), 1.8)

    def test_active_axes_highlight_is_disabled_by_default(self):
        axes1 = FakeAxes(with_spines=True)
        axes2 = FakeAxes(with_spines=True)
        plotter = MatplotlibAxesPlotter(axes1)

        self.assertIsNone(plotter.active_axes_style)
        self.assertEqual(axes1.spines["left"].get_edgecolor(), "black")
        self.assertNotEqual(axes1.spines["left"].get_edgecolor(), "#0072BD")

        plotter.set_active_axes(axes2)

        self.assertIsNone(plotter.active_axes_style)
        self.assertEqual(axes1.spines["left"].get_edgecolor(), "black")
        self.assertEqual(axes2.spines["left"].get_edgecolor(), "black")

    def test_3d_axes_default_mouse_rotation_is_disabled_when_active(self):
        axes2d = FakeAxes()
        axes3d = FakeAxes(is_3d=True)
        plotter = MatplotlibAxesPlotter(axes2d)

        self.assertEqual(axes2d.disable_mouse_rotation_count, 0)
        self.assertEqual(axes3d.disable_mouse_rotation_count, 0)

        plotter.set_active_axes(axes3d)

        self.assertEqual(axes3d.disable_mouse_rotation_count, 1)

    def test_prepare_replace_reapplies_active_axes_highlight_after_cla(self):
        axes = FakeAxes(with_spines=True)
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_active_axes_highlight_enabled(True)

        plotter.prepare_for_plot(axes)

        self.assertIsInstance(plotter.active_axes_style, ActiveAxesStyle)
        self.assertIs(plotter.active_axes_style.axes, axes)
        self.assertEqual(axes.spines["left"].get_edgecolor(), "#0072BD")
        self.assertEqual(axes.spines["left"].get_linewidth(), 1.8)
        self.assertEqual(plotter.active_axes_style.spines["left"].edgecolor, "black")
        self.assertEqual(plotter.active_axes_style.spines["left"].linewidth, 1.0)

    def test_active_axes_highlight_is_noop_without_spines(self):
        axes = FakeAxes()
        plotter = MatplotlibAxesPlotter(axes)

        self.assertIsNone(plotter.active_axes_style)

    def test_set_mode_label_enabled_hides_and_restores_label(self):
        fig, axes = plt.subplots()
        plotter = MatplotlibAxesPlotter(axes)
        plotter.set_mode("pan")

        self.assertIsNotNone(plotter._mode_label_artist)

        plotter.set_mode_label_enabled(False)

        self.assertIsNone(plotter._mode_label_artist)

        plotter.set_mode_label_enabled(True)

        self.assertIsNotNone(plotter._mode_label_artist)
        self.assertEqual(plotter._mode_label_artist.get_text(), "Pan")
        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
