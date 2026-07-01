import unittest

from py_matlab_style_plotter import (
    AreaSeries,
    AxesLimits,
    AspectMode,
    AxisDirection,
    BarSeries,
    BoxAspectMode,
    Camera3DState,
    ConstantLineSeries,
    ContourSeries,
    ErrorBarSeries,
    FillSeries,
    HistogramSeries,
    ImageSeries,
    InteractionMode,
    MatlabLikeAxesBase,
    MouseButton,
    PColorSeries,
    QuiverSeries,
    Plot3Series,
    PlotSeries,
    PointerEvent,
    AnnotationSeries,
    RoseSeries,
    HeatmapSeries,
    ParetoSeries,
    PieSeries,
    PolarHistogramSeries,
    PolarSeries,
    SpySeries,
    Scatter3Series,
    Stem3Series,
    ScatterSeries,
    SurfaceSeries,
    StemSeries,
    TextSeries,
    ToolState,
)


class FakeAxes:
    def __init__(self, name="axes", is_3d=False):
        self.name = name
        self.is_3d = is_3d
        self.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0) if is_3d else None)
        self.xtick = (0.0, 5.0, 10.0)
        self.ytick = (-1.0, 0.0, 1.0)
        self.ztick = (0.0, 2.5, 5.0) if is_3d else ()
        self.xticklabel = ("0", "5", "10")
        self.yticklabel = ("-1", "0", "1")
        self.zticklabel = ("0", "2.5", "5") if is_3d else ()
        self.xticklabel_rotation = 0.0
        self.yticklabel_rotation = 0.0
        self.zticklabel_rotation = 0.0
        self.axes_title = ()
        self.subtitle_text = ()
        self.sgtitle_text = ()
        self.xlabel_text = ()
        self.ylabel_text = ()
        self.zlabel_text = ()
        self.camera = Camera3DState(azim=-37.5, elev=30.0)
        self.camera_projection = "orthographic"
        self.aspect = "auto"
        self.box_aspect = "auto"
        self.data_aspect_ratio = (1.0, 1.0, 1.0)
        self.plot_box_aspect_ratio = (1.0, 1.0, 1.0)
        self.axis_visible = True
        self.x_direction = "normal"
        self.y_direction = "normal"
        self.z_direction = "normal"
        self.x_scale = "linear"
        self.y_scale = "linear"
        self.z_scale = "linear"
        self.axis_layer = "bottom"
        self.tick_direction = "in"
        self.tick_length = (0.01, 0.025)
        self.x_axis_location = "bottom"
        self.y_axis_location = "left"
        self.grid_visible = False
        self.minor_grid_visible = False
        self.x_grid_visible = False
        self.y_grid_visible = False
        self.z_grid_visible = False
        self.x_minor_grid_visible = False
        self.y_minor_grid_visible = False
        self.z_minor_grid_visible = False
        self.x_minor_tick_visible = False
        self.y_minor_tick_visible = False
        self.z_minor_tick_visible = False
        self.box_visible = True
        self.legend_visible = False
        self.colorbar_visible = False
        self.colormap_value = "default"
        self.clear_calls = []
        self.autoscale_calls = []
        self.autoscale_clim_calls = 0


class FakeScreenToDataTransform:
    def __init__(self, x0=0.0, x_scale=0.1, y0=-1.0, y_scale=0.02):
        self.x0 = x0
        self.x_scale = x_scale
        self.y0 = y0
        self.y_scale = y_scale

    def transform(self, point):
        x, y = point
        return (self.x0 + x * self.x_scale, self.y0 + y * self.y_scale)

    def frozen(self):
        return self


class FakeDataTransform:
    def __init__(self, screen_to_data):
        self._screen_to_data = screen_to_data

    def inverted(self):
        return self._screen_to_data


class FakePlotter(MatlabLikeAxesBase):
    def __init__(self, axes=None):
        super().__init__(axes)
        self.active_changes = []
        self.mode_changes = []
        self.hold_changes = []
        self.readouts = []
        self.data_tips = []
        self.selections = []
        self.zoom_box_events = []
        self.brush_box_events = []
        self.brushes = []
        self.drawn_series = []
        self.drawn_plot3_series = []
        self.drawn_errorbar_series = []
        self.drawn_scatter_series = []
        self.drawn_scatter3_series = []
        self.drawn_stem_series = []
        self.drawn_stem3_series = []
        self.drawn_bar_series = []
        self.drawn_barh_series = []
        self.drawn_area_series = []
        self.drawn_fill_series = []
        self.drawn_histogram_series = []
        self.drawn_constant_line_series = []
        self.drawn_text_series = []
        self.drawn_contour_series = []
        self.drawn_contourf_series = []
        self.drawn_surf_series = []
        self.drawn_mesh_series = []
        self.drawn_quiver_series = []
        self.drawn_pcolor_series = []
        self.drawn_spy_series = []
        self.drawn_annotation_series = []
        self.drawn_polar_series = []
        self.drawn_polarhistogram_series = []
        self.drawn_pie_series = []
        self.drawn_pareto_series = []
        self.drawn_heatmap_series = []
        self.drawn_rose_series = []
        self.created_subplot_axes = []
        self.deleted_artists = []
        self.property_changes = []
        self.property_queries = []
        self.child_objects = []
        self.copied_artists = []
        self.flush_calls = 0
        self.yyaxis_changes = []
        self.colordef_changes = []
        self.drawn_image_series = []
        self.view_history_changes = []
        self.block_tool_presses = False
        self.filtered_events = []
        self.action_events = []

    def on_active_axes_changed(self, axes):
        self.active_changes.append(axes)

    def on_mode_changed(self, mode):
        self.mode_changes.append(mode)

    def on_hold_changed(self, enabled):
        self.hold_changes.append(enabled)

    def on_view_history_changed(self):
        self.view_history_changes.append((self.view_index, len(self.view_stack), self.can_back(), self.can_forward()))

    def button_down_filter(self, event):
        self.filtered_events.append(event)
        return self.block_tool_presses

    def action_pre_callback(self, mode, event):
        self.action_events.append(("pre", mode, event.axes))

    def action_post_callback(self, mode, event):
        self.action_events.append(("post", mode, event.axes))

    def update_coordinate_readout(self, axes, x, y):
        self.readouts.append((axes, x, y))

    def create_data_tip(self, axes, x, y, modifiers=frozenset()):
        self.data_tips.append((axes, x, y, modifiers))

    def select_nearest_artist(self, axes, x, y, modifiers):
        self.selections.append((axes, x, y, modifiers))

    def brush_box(self, axes, start, end, modifiers):
        self.brushes.append((axes, start, end, modifiers))

    def clear_children(self, axes, reset_properties):
        axes.clear_calls.append(reset_properties)

    def draw_plot_series(self, axes, series):
        self.drawn_series.append((axes, tuple(series)))
        return [f"line-{len(self.drawn_series)}-{index}" for index, _item in enumerate(series)]

    def draw_plot3_series(self, axes, series):
        self.drawn_plot3_series.append((axes, tuple(series)))
        return [f"line3-{len(self.drawn_plot3_series)}-{index}" for index, _item in enumerate(series)]

    def draw_errorbar_series(self, axes, series):
        self.drawn_errorbar_series.append((axes, tuple(series)))
        return [f"errorbar-{len(self.drawn_errorbar_series)}-{index}" for index, _item in enumerate(series)]

    def draw_scatter_series(self, axes, series):
        self.drawn_scatter_series.append((axes, tuple(series)))
        return [f"scatter-{len(self.drawn_scatter_series)}-{index}" for index, _item in enumerate(series)]

    def draw_scatter3_series(self, axes, series):
        self.drawn_scatter3_series.append((axes, tuple(series)))
        return [f"scatter3-{len(self.drawn_scatter3_series)}-{index}" for index, _item in enumerate(series)]

    def draw_stem_series(self, axes, series):
        self.drawn_stem_series.append((axes, tuple(series)))
        return [f"stem-{len(self.drawn_stem_series)}-{index}" for index, _item in enumerate(series)]

    def draw_stem3_series(self, axes, series):
        self.drawn_stem3_series.append((axes, tuple(series)))
        return [f"stem3-{len(self.drawn_stem3_series)}-{index}" for index, _item in enumerate(series)]

    def draw_bar_series(self, axes, series):
        self.drawn_bar_series.append((axes, tuple(series)))
        return [f"bar-{len(self.drawn_bar_series)}-{index}" for index, _item in enumerate(series)]

    def draw_barh_series(self, axes, series):
        self.drawn_barh_series.append((axes, tuple(series)))
        return [f"barh-{len(self.drawn_barh_series)}-{index}" for index, _item in enumerate(series)]

    def draw_area_series(self, axes, series):
        self.drawn_area_series.append((axes, tuple(series)))
        return [f"area-{len(self.drawn_area_series)}-{index}" for index, _item in enumerate(series)]

    def draw_fill_series(self, axes, series):
        self.drawn_fill_series.append((axes, tuple(series)))
        return [f"fill-{len(self.drawn_fill_series)}-{index}" for index, _item in enumerate(series)]

    def draw_histogram_series(self, axes, series):
        self.drawn_histogram_series.append((axes, tuple(series)))
        return [f"histogram-{len(self.drawn_histogram_series)}-{index}" for index, _item in enumerate(series)]

    def draw_constant_line_series(self, axes, series):
        self.drawn_constant_line_series.append((axes, tuple(series)))
        return [f"constant-line-{len(self.drawn_constant_line_series)}-{index}" for index, _item in enumerate(series)]

    def draw_text_series(self, axes, series):
        self.drawn_text_series.append((axes, tuple(series)))
        return [f"text-{len(self.drawn_text_series)}-{index}" for index, _item in enumerate(series)]

    def draw_contour_series(self, axes, series):
        self.drawn_contour_series.append((axes, tuple(series)))
        return [f"contour-{len(self.drawn_contour_series)}-{index}" for index, _item in enumerate(series)]

    def draw_contourf_series(self, axes, series):
        self.drawn_contourf_series.append((axes, tuple(series)))
        return [f"contourf-{len(self.drawn_contourf_series)}-{index}" for index, _item in enumerate(series)]

    def draw_surf_series(self, axes, series):
        self.drawn_surf_series.append((axes, tuple(series)))
        return [f"surf-{len(self.drawn_surf_series)}-{index}" for index, _item in enumerate(series)]

    def draw_mesh_series(self, axes, series):
        self.drawn_mesh_series.append((axes, tuple(series)))
        return [f"mesh-{len(self.drawn_mesh_series)}-{index}" for index, _item in enumerate(series)]

    def draw_quiver_series(self, axes, series):
        self.drawn_quiver_series.append((axes, tuple(series)))
        return [f"quiver-{len(self.drawn_quiver_series)}-{index}" for index, _item in enumerate(series)]

    def draw_pcolor_series(self, axes, series):
        self.drawn_pcolor_series.append((axes, tuple(series)))
        return [f"pcolor-{len(self.drawn_pcolor_series)}-{index}" for index, _item in enumerate(series)]

    def draw_spy_series(self, axes, series):
        self.drawn_spy_series.append((axes, tuple(series)))
        return [f"spy-{len(self.drawn_spy_series)}-{index}" for index, _item in enumerate(series)]

    def draw_annotation_series(self, axes, series):
        self.drawn_annotation_series.append((axes, tuple(series)))
        return [f"annotation-{len(self.drawn_annotation_series)}-{index}" for index, _item in enumerate(series)]

    def draw_polar_series(self, axes, series):
        self.drawn_polar_series.append((axes, tuple(series)))
        return [f"polar-{len(self.drawn_polar_series)}-{index}" for index, _item in enumerate(series)]

    def draw_polarhistogram_series(self, axes, series):
        self.drawn_polarhistogram_series.append((axes, tuple(series)))
        return [f"polarhist-{len(self.drawn_polarhistogram_series)}-{index}" for index, _item in enumerate(series)]

    def draw_pie_series(self, axes, series):
        self.drawn_pie_series.append((axes, tuple(series)))
        return [f"pie-{len(self.drawn_pie_series)}-{index}" for index, _item in enumerate(series)]

    def draw_pareto_series(self, axes, series):
        self.drawn_pareto_series.append((axes, tuple(series)))
        return [f"pareto-{len(self.drawn_pareto_series)}-{index}" for index, _item in enumerate(series)]

    def draw_heatmap_series(self, axes, series):
        self.drawn_heatmap_series.append((axes, tuple(series)))
        return [f"heatmap-{len(self.drawn_heatmap_series)}-{index}" for index, _item in enumerate(series)]

    def draw_rose_series(self, axes, series):
        self.drawn_rose_series.append((axes, tuple(series)))
        return [f"rose-{len(self.drawn_rose_series)}-{index}" for index, _item in enumerate(series)]

    def create_subplot_axes(self, rows, columns, position):
        axes = FakeAxes(f"subplot-{rows}x{columns}-{position}")
        self.created_subplot_axes.append((rows, columns, position, axes))
        return axes

    def delete_artist(self, artist):
        self.deleted_artists.append(artist)

    def set_artist_property(self, artist, name, value):
        self.property_changes.append((artist, name, value))

    def get_children(self, obj):
        return getattr(obj, 'child_list', [])

    def copy_artist(self, artist, target):
        self.copied_artists.append((artist, target))
        return f"copy-of-{getattr(artist, 'name', id(artist))}"

    def _flush_graphics(self, axes):
        self.flush_calls += 1

    def set_yyaxis_side(self, axes, side):
        self.yyaxis_changes.append((axes, side))

    def set_color_scheme(self, axes, scheme):
        self.colordef_changes.append((axes, scheme))

    def get_artist_property(self, artist, name):
        self.property_queries.append((artist, name))
        return getattr(artist, name, None)

    def draw_image_series(self, axes, series):
        self.drawn_image_series.append((axes, tuple(series)))
        return [f"image-{len(self.drawn_image_series)}-{index}" for index, _item in enumerate(series)]

    def is_axes_handle(self, value):
        return isinstance(value, FakeAxes)

    def reset_axes_properties(self, axes):
        axes.aspect = "auto"
        axes.box_aspect = "auto"
        axes.axis_visible = True
        axes.y_direction = "normal"

    def get_limits(self, axes):
        return axes.limits

    def set_limits(self, axes, limits):
        axes.limits = limits

    def autoscale_axes(self, axes, tight=False, recompute=True):
        axes.autoscale_calls.append(tight)

    def autoscale_clim(self, axes):
        axes.autoscale_clim_calls += 1

    def is_3d_axes(self, axes):
        return axes.is_3d

    def get_camera3d(self, axes):
        return axes.camera

    def set_camera3d(self, axes, camera):
        axes.camera = camera

    def set_aspect(self, axes, aspect: AspectMode):
        axes.aspect = aspect

    def set_box_aspect(self, axes, box_aspect: BoxAspectMode):
        axes.box_aspect = box_aspect

    def set_data_aspect_ratio(self, axes, ratio):
        axes.data_aspect_ratio = ratio

    def set_plot_box_aspect_ratio(self, axes, ratio):
        axes.plot_box_aspect_ratio = ratio

    def set_axis_visible(self, axes, visible):
        axes.axis_visible = visible

    def set_y_direction(self, axes, direction: AxisDirection):
        axes.y_direction = direction

    def set_x_direction(self, axes, direction: AxisDirection):
        axes.x_direction = direction

    def set_z_direction(self, axes, direction: AxisDirection):
        axes.z_direction = direction

    def set_axis_scale(self, axes, axis, scale):
        setattr(axes, f"{axis}_scale", scale)

    def grid_is_enabled(self, axes):
        return super().grid_is_enabled(axes)

    def set_grid_visible(self, axes, visible):
        super().set_grid_visible(axes, visible)
        axes.grid_visible = visible

    def minor_grid_is_enabled(self, axes):
        return super().minor_grid_is_enabled(axes)

    def set_minor_grid_visible(self, axes, visible):
        super().set_minor_grid_visible(axes, visible)
        axes.minor_grid_visible = visible

    def box_is_enabled(self, axes):
        return axes.box_visible

    def set_box_visible(self, axes, visible):
        axes.box_visible = visible

    def legend_is_enabled(self, axes):
        return axes.legend_visible

    def set_legend_visible(self, axes, visible):
        axes.legend_visible = visible
        return axes.legend_visible

    def colorbar_is_enabled(self, axes):
        return axes.colorbar_visible

    def set_colorbar_visible(self, axes, visible):
        axes.colorbar_visible = visible
        return axes.colorbar_visible

    def set_colormap(self, axes, value):
        axes.colormap_value = value

    def begin_zoom_box(self, axes, x, y):
        self.zoom_box_events.append(("begin", axes, x, y))

    def update_zoom_box(self, axes, x0, y0, x1, y1):
        self.zoom_box_events.append(("update", axes, x0, y0, x1, y1))

    def end_zoom_box(self):
        self.zoom_box_events.append(("end",))

    def begin_brush_box(self, axes, x, y):
        self.brush_box_events.append(("begin", axes, x, y))

    def update_brush_box(self, axes, x0, y0, x1, y1):
        self.brush_box_events.append(("update", axes, x0, y0, x1, y1))

    def end_brush_box(self):
        self.brush_box_events.append(("end",))


class MatlabLikeAxesBaseTest(unittest.TestCase):
    def test_hold_controls_next_plot(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertFalse(plotter.hold())
        self.assertFalse(plotter.ishold())
        self.assertEqual(plotter.next_plot, "replace")

        self.assertTrue(plotter.hold(" On "))
        self.assertTrue(plotter.ishold())
        self.assertEqual(plotter.next_plot, "add")
        self.assertEqual(plotter.hold_changes, [True])

        self.assertTrue(plotter.hold("on"))
        self.assertEqual(plotter.hold_changes, [True])

        self.assertFalse(plotter.hold(" OFF "))
        self.assertEqual(plotter.next_plot, "replace")
        self.assertEqual(plotter.hold_changes, [True, False])

        self.assertTrue(plotter.hold(" toggle "))
        self.assertEqual(plotter.next_plot, "add")
        self.assertEqual(plotter.hold_changes, [True, False, True])

        plotter.set_next_plot("add")
        self.assertTrue(plotter.hold_enabled)
        self.assertEqual(plotter.hold_changes, [True, False, True])

        plotter.set_next_plot("replacechildren")
        self.assertFalse(plotter.hold_enabled)
        self.assertEqual(plotter.hold_changes, [True, False, True, False])

        with self.assertRaisesRegex(ValueError, " bad hold "):
            plotter.hold(" bad hold ")

    def test_copyobj_delegates_to_backend_copy_artist(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        class FakeArtist:
            name = "line1"

        artist = FakeArtist()
        result = plotter.copyobj(artist, axes)

        self.assertEqual(plotter.copied_artists[-1], (artist, axes))
        self.assertEqual(result, "copy-of-line1")

    def test_copyobj_defaults_to_active_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        class FakeArtist:
            name = "scatter1"

        artist = FakeArtist()
        result = plotter.copyobj(artist)

        self.assertEqual(plotter.copied_artists[-1], (artist, axes))

    def test_findobj_returns_matching_objects_recursively(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        class FakeObj:
            def __init__(self, name, children=None):
                self.name = name
                self.child_list = children or []

        child1 = FakeObj("line1")
        child2 = FakeObj("line2")
        root = FakeObj("axes", [child1, child2])

        # No filter - returns all
        result = plotter.findobj(root)
        self.assertEqual(result, [root, child1, child2])

        # Filter by property
        result = plotter.findobj(root, "name", "line1")
        self.assertEqual(result, [child1])

        # Filter by property existence
        result = plotter.findobj(root, "name")
        self.assertEqual(len(result), 3)

    def test_set_and_get_delegate_to_backend_hooks(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.set(axes, "grid_visible", True)
        self.assertEqual(plotter.property_changes[-1], (axes, "grid_visible", True))

        axes.grid_visible = True
        result = plotter.get(axes, "grid_visible")
        self.assertEqual(plotter.property_queries[-1], (axes, "grid_visible"))
        self.assertTrue(result)

    def test_delete_axes_removes_from_active_and_subplot_cache(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        ax1 = plotter.subplot(2, 2, 1)
        ax2 = plotter.subplot(2, 2, 2)
        plotter.set_active_axes(ax1)

        plotter.delete(ax1)

        self.assertIsNone(plotter.active_axes)
        self.assertIn(ax1, plotter.deleted_artists)
        self.assertEqual(plotter._subplot_axes.get((2, 2, 1)), None)
        self.assertEqual(plotter._subplot_axes.get((2, 2, 2)), ax2)

    def test_delete_non_axes_calls_delete_artist(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        class FakeArtist:
            pass

        artist = FakeArtist()
        plotter.delete(artist)
        self.assertIn(artist, plotter.deleted_artists)









    def test_rose_normalizes_theta_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.rose([0.1, 0.5, 1.0, 2.0, 3.0])

        self.assertEqual(artists, ["rose-1-0"])
        _axes, series = plotter.drawn_rose_series[0]
        self.assertEqual(len(series[0].theta), 5)

    def test_rose_accepts_bins(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.rose([0.1, 0.5, 1.0], 10)

        _axes, series = plotter.drawn_rose_series[0]
        self.assertEqual(series[0].bins, 10)

    def test_rose_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "theta"):
            plotter.rose()

    def test_polarhistogram_normalizes_theta_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.polarhistogram([0.1, 0.5, 1.0, 2.0, 3.0])

        self.assertEqual(artists, ["polarhist-1-0"])
        _axes, series = plotter.drawn_polarhistogram_series[0]
        self.assertEqual(len(series[0].theta), 5)

    def test_polarhistogram_accepts_bins(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.polarhistogram([0.1, 0.5, 1.0], 10)

        _axes, series = plotter.drawn_polarhistogram_series[0]
        self.assertEqual(series[0].bins, 10)

    def test_polarhistogram_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "theta"):
            plotter.polarhistogram()


    def test_feather_normalizes_uv_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.feather([1, 0, -1], [0, 1, 0])

        self.assertEqual(artists, ["quiver-1-0"])
        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(len(series[0].u), 3)

    def test_feather_accepts_rho_only(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.feather([1, 2, 3])

        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(len(series[0].u), 3)

    def test_feather_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "feather requires"):
            plotter.feather()

    def test_compass_normalizes_uv_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.compass([1, 0, -1], [0, 1, 0])

        self.assertEqual(artists, ["quiver-1-0"])
        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(len(series[0].u), 3)

    def test_compass_accepts_rho_only(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.compass([1, 2, 3])

        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(len(series[0].u), 3)

    def test_compass_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "compass requires"):
            plotter.compass()

    def test_heatmap_normalizes_data_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.heatmap([[1, 2], [3, 4]])

        self.assertEqual(artists, ["heatmap-1-0"])
        _axes, series = plotter.drawn_heatmap_series[0]
        self.assertEqual(series[0].data, ((1.0, 2.0), (3.0, 4.0)))

    def test_heatmap_accepts_labels(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.heatmap([[1, 2], [3, 4]], ["X1", "X2"], ["Y1", "Y2"])

        _axes, series = plotter.drawn_heatmap_series[0]
        self.assertEqual(series[0].x_labels, ("X1", "X2"))
        self.assertEqual(series[0].y_labels, ("Y1", "Y2"))

    def test_heatmap_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "data matrix"):
            plotter.heatmap()

    def test_pareto_normalizes_data_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pareto([50, 20, 10, 15, 5])

        self.assertEqual(artists, ["pareto-1-0"])
        _axes, series = plotter.drawn_pareto_series[0]
        self.assertEqual(series[0].data, (50.0, 20.0, 10.0, 15.0, 5.0))

    def test_pareto_accepts_labels(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pareto([50, 20, 10], ["A", "B", "C"])

        _axes, series = plotter.drawn_pareto_series[0]
        self.assertEqual(series[0].labels, ("A", "B", "C"))

    def test_pareto_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "data values"):
            plotter.pareto()

    def test_pie_normalizes_data_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pie([30, 20, 50])

        self.assertEqual(artists, ["pie-1-0"])
        _axes, series = plotter.drawn_pie_series[0]
        self.assertEqual(series[0].data, (30.0, 20.0, 50.0))
        self.assertIsNone(series[0].labels)

    def test_pie_accepts_labels(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pie([30, 20, 50], ["A", "B", "C"])

        _axes, series = plotter.drawn_pie_series[0]
        self.assertEqual(series[0].labels, ("A", "B", "C"))

    def test_pie_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "data values"):
            plotter.pie()

    def test_polarplot_normalizes_theta_rho_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.polarplot([0, 1.57, 3.14], [1, 2, 1])

        self.assertEqual(artists, ["polar-1-0"])
        _axes, series = plotter.drawn_polar_series[0]
        self.assertEqual(len(series[0].theta), 3)
        self.assertEqual(len(series[0].rho), 3)

    def test_polarplot_accepts_theta_only(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.polarplot([1, 2, 3])

        _axes, series = plotter.drawn_polar_series[0]
        self.assertEqual(series[0].rho, (1.0, 2.0, 3.0))
        self.assertEqual(series[0].theta, (0.0, 1.0, 2.0))

    def test_polarplot_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "theta"):
            plotter.polarplot()

    def test_annotation_line_creates_line_series(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.annotation("line", [0.1, 0.9], [0.2, 0.8])

        _axes, series = plotter.drawn_annotation_series[0]
        self.assertEqual(series[0].annotation_type, "line")
        self.assertEqual(series[0].position, (0.1, 0.2, 0.9, 0.8))

    def test_annotation_textarrow_creates_textarrow_series(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.annotation("textarrow", [0.1, 0.5], [0.2, 0.6], "hello")

        _axes, series = plotter.drawn_annotation_series[0]
        self.assertEqual(series[0].annotation_type, "textarrow")
        self.assertEqual(series[0].text, "hello")

    def test_annotation_textbox_creates_textbox_series(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.annotation("textbox", [0.1, 0.2, 0.3, 0.1], "note")

        _axes, series = plotter.drawn_annotation_series[0]
        self.assertEqual(series[0].annotation_type, "textbox")
        self.assertEqual(series[0].position, (0.1, 0.2, 0.3, 0.1))
        self.assertEqual(series[0].text, "note")

    def test_annotation_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "at least an annotation type"):
            plotter.annotation()
        with self.assertRaisesRegex(ValueError, "Unsupported annotation type"):
            plotter.annotation("bad")
        with self.assertRaisesRegex(ValueError, "2-element x and y"):
            plotter.annotation("line", [0.1], [0.2])
        with self.assertRaisesRegex(ValueError, "position vector"):
            plotter.annotation("textbox")

    def test_drawnow_flushes_graphics_for_active_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.drawnow()
        self.assertEqual(plotter.flush_calls, 1)

    def test_drawnow_noop_without_active_axes(self):
        plotter = FakePlotter(None)

        plotter.drawnow()

    def test_subplot_creates_and_reuses_axes_in_grid(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        ax1 = plotter.subplot(2, 3, 1)
        self.assertEqual(plotter.created_subplot_axes[-1], (2, 3, 1, ax1))
        self.assertIs(plotter.active_axes, ax1)

        ax1_again = plotter.subplot(2, 3, 1)
        self.assertIs(ax1_again, ax1)
        self.assertEqual(len(plotter.created_subplot_axes), 1)

        ax2 = plotter.subplot(2, 3, 4)
        self.assertEqual(plotter.created_subplot_axes[-1], (2, 3, 4, ax2))
        self.assertIs(plotter.active_axes, ax2)

    def test_subplot_accepts_shorthand_three_digit_integer(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        ax = plotter.subplot(231)
        self.assertEqual(plotter.created_subplot_axes[-1], (2, 3, 1, ax))

    def test_subplot_validates_grid_and_position(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "subplot requires"):
            plotter.subplot(1, 2)
        with self.assertRaisesRegex(ValueError, "out of.*grid range"):
            plotter.subplot(2, 3, 7)
        with self.assertRaisesRegex(ValueError, "out of.*grid range"):
            plotter.subplot(2, 3, 0)

    def test_gca_returns_current_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        self.assertIs(plotter.gca(), axes1)

        plotter.set_active_axes(axes2)
        self.assertIs(plotter.gca(), axes2)

        plotter.set_active_axes(None)
        self.assertIsNone(plotter.gca())

    def test_hold_and_next_plot_are_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.hold("on")
        self.assertTrue(plotter.hold_enabled)
        self.assertEqual(plotter.next_plot, "add")

        plotter.set_active_axes(axes2)
        self.assertFalse(plotter.hold_enabled)
        self.assertEqual(plotter.next_plot, "replace")

        plotter.prepare_for_plot(axes2)
        self.assertEqual(axes2.clear_calls, [True])

        plotter.set_active_axes(axes1)
        self.assertTrue(plotter.hold_enabled)
        self.assertEqual(plotter.next_plot, "add")
        self.assertEqual(plotter.hold_changes, [True, False, True])

    def test_ishold_can_query_non_active_axes_without_switching(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.set_active_axes(axes2)
        plotter.hold("on")
        plotter.set_active_axes(axes1)

        self.assertFalse(plotter.ishold())
        self.assertTrue(plotter.ishold(axes2))
        self.assertIs(plotter.active_axes, axes1)

    def test_prepare_for_plot_uses_target_axes_next_plot(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.set_next_plot("replacechildren")
        plotter.set_active_axes(axes2)

        plotter.prepare_for_plot(axes1)
        plotter.prepare_for_plot(axes2)

        self.assertEqual(axes1.clear_calls, [False])
        self.assertEqual(axes2.clear_calls, [True])

    def test_toggle_mode_matches_exclusive_toolbar_behavior(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.toggle_mode("pan"), InteractionMode.PAN)
        self.assertEqual(plotter.mode, InteractionMode.PAN)
        self.assertEqual(plotter.active_mode(), InteractionMode.PAN)
        self.assertTrue(plotter.is_mode_active("pan"))
        self.assertFalse(plotter.is_mode_active("zoom"))

        self.assertEqual(plotter.toggle_mode("pan"), InteractionMode.NONE)
        self.assertEqual(plotter.mode, InteractionMode.NONE)
        self.assertTrue(plotter.is_mode_active(InteractionMode.NONE))

        self.assertEqual(plotter.toggle_mode("zoom"), InteractionMode.ZOOM)
        self.assertEqual(plotter.toggle_mode("rotate3d"), InteractionMode.ROTATE3D)
        self.assertTrue(plotter.is_mode_active(InteractionMode.ROTATE3D))
        self.assertEqual(plotter.mode_changes, [
            InteractionMode.PAN,
            InteractionMode.NONE,
            InteractionMode.ZOOM,
            InteractionMode.ROTATE3D,
        ])

    def test_tool_state_snapshots_expose_matlab_like_enable_and_properties(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.pan_state(), ToolState(InteractionMode.PAN, "off", False, motion="both"))
        self.assertEqual(plotter.use_legacy_exploration_modes, "off")
        self.assertEqual(
            plotter.zoom_state(),
            ToolState(
                InteractionMode.ZOOM,
                "off",
                False,
                motion="both",
                direction="in",
                right_click_action="postcontextmenu",
                use_legacy_exploration_modes="off",
            ),
        )
        self.assertEqual(plotter.rotate3d_state(), ToolState(InteractionMode.ROTATE3D, "off", False, motion="both", rotate_style="orbit"))

        plotter.pan_motion = "horizontal"
        plotter.pan("on")
        self.assertEqual(plotter.pan_state(), ToolState(InteractionMode.PAN, "on", True, motion="horizontal"))
        self.assertEqual(plotter.zoom_state().enable, "off")

        plotter.zoom_motion = "vertical"
        plotter.zoom_direction = "out"
        plotter.zoom_right_click_action = "inversezoom"
        plotter.zoom("on")
        self.assertEqual(plotter.pan_state().enable, "off")
        self.assertEqual(
            plotter.tool_state("zoom"),
            ToolState(
                InteractionMode.ZOOM,
                "on",
                True,
                motion="vertical",
                direction="out",
                right_click_action="inversezoom",
            ),
        )

        plotter.rotate_motion = "horizontal"
        plotter.rotate_style = " Box "
        plotter.rotate3d("on")
        self.assertEqual(plotter.rotate3d_state(), ToolState(InteractionMode.ROTATE3D, "on", True, motion="horizontal", rotate_style="box"))

    def test_matlab_like_tool_mode_helpers_accept_on_off_toggle_and_bool(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.pan(), InteractionMode.PAN)
        self.assertEqual(plotter.zoom("on"), InteractionMode.ZOOM)
        self.assertEqual(plotter.zoom("off"), InteractionMode.NONE)
        self.assertEqual(plotter.rotate3d(True), InteractionMode.ROTATE3D)
        self.assertEqual(plotter.rotate3d(False), InteractionMode.NONE)
        self.assertEqual(plotter.datacursormode("toggle"), InteractionMode.DATA_CURSOR)
        self.assertEqual(plotter.selectmode("on"), InteractionMode.SELECT)
        self.assertEqual(plotter.brush("on"), InteractionMode.BRUSH)

        self.assertTrue(plotter.is_mode_active("brush"))

    def test_tool_mode_helpers_ignore_off_for_inactive_mode_and_reject_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.zoom("off"), InteractionMode.NONE)
        self.assertEqual(plotter.mode_changes, [])

        with self.assertRaisesRegex(ValueError, "Unsupported interaction mode value"):
            plotter.pan("bad")

    def test_grid_accepts_on_off_toggle_bool_and_returns_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.grid("on"))
        self.assertTrue(axes.grid_visible)
        self.assertTrue(plotter.grid(True))
        self.assertTrue(axes.grid_visible)

        self.assertFalse(plotter.grid("toggle"))
        self.assertFalse(axes.grid_visible)
        self.assertTrue(plotter.grid())
        self.assertTrue(axes.grid_visible)
        self.assertFalse(plotter.grid(False))
        self.assertFalse(axes.grid_visible)
        self.assertFalse(plotter.grid("off"))
        self.assertFalse(axes.grid_visible)

    def test_grid_updates_per_axis_grid_state_like_matlab(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.grid("on"))
        self.assertTrue(axes.x_grid_visible)
        self.assertTrue(axes.y_grid_visible)
        self.assertTrue(axes.z_grid_visible)
        self.assertTrue(plotter.xgrid())
        self.assertTrue(plotter.ygrid())
        self.assertTrue(plotter.zgrid())

        self.assertFalse(plotter.xgrid("off"))
        self.assertFalse(axes.x_grid_visible)
        self.assertTrue(axes.y_grid_visible)
        self.assertTrue(axes.z_grid_visible)
        self.assertFalse(plotter.grid("off"))
        self.assertFalse(axes.x_grid_visible)
        self.assertFalse(axes.y_grid_visible)
        self.assertFalse(axes.z_grid_visible)

    def test_grid_minor_updates_per_axis_minor_grid_state_like_matlab(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.grid("on")
        self.assertTrue(plotter.grid("minor"))
        self.assertTrue(axes.x_minor_grid_visible)
        self.assertTrue(axes.y_minor_grid_visible)
        self.assertTrue(axes.z_minor_grid_visible)
        self.assertTrue(axes.x_grid_visible)

        self.assertFalse(plotter.yminorgrid("off"))
        self.assertTrue(axes.x_minor_grid_visible)
        self.assertFalse(axes.y_minor_grid_visible)
        self.assertTrue(axes.z_minor_grid_visible)

        plotter.grid("off")
        self.assertFalse(axes.x_grid_visible)
        self.assertFalse(axes.y_grid_visible)
        self.assertFalse(axes.z_grid_visible)
        self.assertFalse(axes.x_minor_grid_visible)
        self.assertFalse(axes.y_minor_grid_visible)
        self.assertFalse(axes.z_minor_grid_visible)

    def test_minor_tick_helpers_are_independent_from_minor_grid(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertFalse(plotter.xminortick())
        self.assertFalse(plotter.yminortick())
        self.assertFalse(plotter.zminortick())

        plotter.grid("minor")
        self.assertTrue(axes.x_minor_grid_visible)
        self.assertFalse(axes.x_minor_tick_visible)
        self.assertFalse(axes.y_minor_tick_visible)
        self.assertFalse(axes.z_minor_tick_visible)

        self.assertTrue(plotter.xminortick("on"))
        self.assertTrue(plotter.yminortick(True))
        self.assertTrue(plotter.zminortick("on"))
        self.assertTrue(axes.x_minor_tick_visible)
        self.assertTrue(axes.y_minor_tick_visible)
        self.assertTrue(axes.z_minor_tick_visible)

        self.assertFalse(plotter.yminortick("off"))
        self.assertTrue(axes.x_minor_tick_visible)
        self.assertFalse(axes.y_minor_tick_visible)
        self.assertTrue(axes.z_minor_tick_visible)

    def test_z_minor_tick_is_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zminortick())
        self.assertIsNone(plotter.zminortick("on"))

    def test_minor_tick_helpers_reject_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported xminortick value"):
            plotter.xminortick("bad")

    def test_z_grid_helpers_are_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zgrid())
        self.assertIsNone(plotter.zgrid("on"))
        self.assertIsNone(plotter.zminorgrid())
        self.assertIsNone(plotter.zminorgrid("on"))

    def test_axis_grid_helpers_reject_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported xgrid value"):
            plotter.xgrid("toggle")
        with self.assertRaisesRegex(ValueError, "Unsupported yminorgrid value"):
            plotter.yminorgrid("bad")

    def test_grid_rejects_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported grid value"):
            plotter.grid("bad")

    def test_box_accepts_on_off_toggle_bool_and_returns_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertFalse(plotter.box("off"))
        self.assertFalse(axes.box_visible)
        self.assertFalse(plotter.box(False))
        self.assertFalse(axes.box_visible)

        self.assertTrue(plotter.box("toggle"))
        self.assertTrue(axes.box_visible)
        self.assertFalse(plotter.box())
        self.assertFalse(axes.box_visible)
        self.assertTrue(plotter.box(True))
        self.assertTrue(axes.box_visible)
        self.assertTrue(plotter.box("on"))
        self.assertTrue(axes.box_visible)

    def test_box_rejects_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported box value"):
            plotter.box("bad")

    def test_legend_accepts_on_off_toggle_bool_and_returns_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.legend("on"))
        self.assertTrue(axes.legend_visible)
        self.assertTrue(plotter.legend(True))
        self.assertTrue(axes.legend_visible)

        self.assertFalse(plotter.legend("toggle"))
        self.assertFalse(axes.legend_visible)
        self.assertTrue(plotter.legend())
        self.assertTrue(axes.legend_visible)
        self.assertFalse(plotter.legend(False))
        self.assertFalse(axes.legend_visible)
        self.assertFalse(plotter.legend("off"))
        self.assertFalse(axes.legend_visible)

    def test_legend_rejects_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported legend value"):
            plotter.legend("bad")

    def test_colorbar_accepts_on_off_toggle_bool_and_returns_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.colorbar("on"))
        self.assertTrue(axes.colorbar_visible)
        self.assertFalse(plotter.colorbar("toggle"))
        self.assertFalse(axes.colorbar_visible)
        self.assertTrue(plotter.colorbar())
        self.assertTrue(axes.colorbar_visible)
        self.assertFalse(plotter.colorbar(False))
        self.assertFalse(axes.colorbar_visible)

    def test_colorbar_rejects_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported colorbar value"):
            plotter.colorbar("bad")

    def test_colormap_queries_sets_names_and_rgb_matrix(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.colormap(), "default")

        self.assertIsNone(plotter.colormap(" Hot "))
        self.assertEqual(axes.colormap_value, "hot")
        self.assertEqual(plotter.colormap(), "hot")

        rgb = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        self.assertIsNone(plotter.colormap([(1, 0, 0), (0, 1, 0)]))
        self.assertEqual(axes.colormap_value, rgb)
        self.assertEqual(plotter.colormap(), rgb)

    def test_colormap_is_scoped_per_axes(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.colormap("hot", axes=axes2)

        self.assertEqual(plotter.colormap(axes=axes1), "default")
        self.assertEqual(plotter.colormap(axes=axes2), "hot")
        self.assertEqual(axes2.colormap_value, "hot")

    def test_colormap_rejects_bad_values(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "colormap name"):
            plotter.colormap(" ")
        with self.assertRaisesRegex(ValueError, "N-by-3"):
            plotter.colormap([(1, 0)])
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            plotter.colormap([(1.2, 0, 0)])

    def test_set_mode_is_noop_when_mode_is_unchanged(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.set_mode("pan")
        plotter.set_mode("pan")

        self.assertEqual(plotter.mode, InteractionMode.PAN)
        self.assertEqual(plotter.mode_changes, [InteractionMode.PAN])

    def test_set_same_mode_still_cancels_active_drag_without_duplicate_notification(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))

        plotter.set_mode("zoom")
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="left"))

        self.assertEqual(plotter.zoom_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(plotter.mode_changes, [InteractionMode.ZOOM])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_unknown_mouse_button_is_ignored_without_error(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for mode in ("pan", "zoom", "rotate3d", "data_cursor", "select", "brush"):
            with self.subTest(mode=mode):
                plotter.set_mode(mode)
                plotter.on_mouse_press(PointerEvent(axes=axes, x=0.0, y=0.0, xdata=1.0, ydata=0.1, button="back"))
                plotter.on_mouse_move(PointerEvent(axes=axes, x=120.0, y=60.0, xdata=4.0, ydata=0.8, button="back"))
                plotter.on_mouse_release(PointerEvent(axes=axes, x=120.0, y=60.0, xdata=4.0, ydata=0.8, button="back"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(plotter.selections, [])
        self.assertEqual(plotter.brushes, [])
        self.assertEqual(plotter.zoom_box_events, [])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_mouse_button_aliases_are_normalized_in_core_events(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.set_mode("pan")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button=1))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="button1"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="mousebutton.left"))
        self.assertEqual(axes.limits, AxesLimits((-1.0, 9.0), (-1.1, 0.9)))

        plotter.set_mode("zoom")
        plotter.zoom_right_click_action = "inversezoom"
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=4.0, ydata=0.0, button=3))
        self.assertEqual(axes.limits, AxesLimits((-6.0, 14.0), (-2.2, 1.8)))
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=4.0, ydata=0.0, button="button2"))
        self.assertEqual(plotter.zoom_box_events, [])

        plotter.set_mode("data_cursor")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="mousebutton.left"))
        self.assertEqual(plotter.data_tips, [(axes, 1.0, 0.1, frozenset())])

    def test_active_axes_queries_and_noop_reselection(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        self.assertIs(plotter.current_axes(), axes1)
        self.assertTrue(plotter.is_active_axes(axes1))
        self.assertFalse(plotter.is_active_axes(axes2))

        plotter.set_active_axes(axes1)
        self.assertEqual(plotter.active_changes, [])

        plotter.set_active_axes(axes2)
        self.assertIs(plotter.current_axes(), axes2)
        self.assertFalse(plotter.is_active_axes(axes1))
        self.assertTrue(plotter.is_active_axes(axes2))
        self.assertEqual(plotter.active_changes, [axes2])

    def test_axes_ui_state_is_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.set_xlim(1.0, 2.0)
        plotter.axis("equal")
        plotter.axis("off")
        plotter.axis("ij")

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertTrue(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "normal")

        plotter.set_ylim(10.0, 20.0)
        plotter.axis("square")
        plotter.grid("on")
        plotter.box("off")
        plotter.legend("on")

        plotter.set_active_axes(axes1)
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.axis_aspect, "equal")
        self.assertFalse(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "reverse")

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.box_aspect, "square")
        self.assertTrue(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "normal")
        self.assertTrue(axes2.grid_visible)
        self.assertFalse(axes2.box_visible)
        self.assertTrue(axes2.legend_visible)

    def test_first_active_axes_load_preserves_existing_backend_grid_state(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes2.grid_visible = True
        axes2.x_grid_visible = True
        axes2.y_grid_visible = True
        plotter = FakePlotter(axes1)

        plotter.set_active_axes(axes2)

        self.assertTrue(axes2.grid_visible)
        self.assertTrue(axes2.x_grid_visible)
        self.assertTrue(axes2.y_grid_visible)
        self.assertTrue(plotter.grid_is_enabled(axes2))

    def test_prepare_for_plot_uses_next_plot(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.prepare_for_plot()
        self.assertEqual(axes.clear_calls, [True])

        plotter.set_next_plot("replacechildren")
        plotter.prepare_for_plot()
        self.assertEqual(axes.clear_calls, [True, False])

        plotter.hold("on")
        plotter.prepare_for_plot()
        self.assertEqual(axes.clear_calls, [True, False])

    def test_newplot_prepares_active_axes_and_returns_it(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        result = plotter.newplot()

        self.assertIs(result, axes)
        self.assertIs(plotter.active_axes, axes)
        self.assertEqual(axes.clear_calls, [True])

    def test_newplot_accepts_target_axes_and_applies_its_next_plot(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.set_active_axes(axes2)
        plotter.hold("on")
        plotter.set_active_axes(axes1)

        result = plotter.newplot(axes2)

        self.assertIs(result, axes2)
        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [])
        self.assertTrue(plotter.hold_enabled)

    def test_cla_clears_children_without_resetting_axes_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.grid("on")
        plotter.box("off")
        plotter.hold("on")
        plotter.push_current_view()
        history_count = len(plotter.view_stack)

        self.assertIsNone(plotter.cla())

        self.assertEqual(axes.clear_calls, [False])
        self.assertTrue(axes.grid_visible)
        self.assertFalse(axes.box_visible)
        self.assertTrue(plotter.hold_enabled)
        self.assertEqual(len(plotter.view_stack), history_count)

    def test_cla_reset_clears_history_and_resets_axes_state(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.grid("on")
        plotter.box("off")
        plotter.legend("on")
        plotter.hold("on")
        plotter.ydir("reverse")
        plotter.push_current_view()

        self.assertIsNone(plotter.cla(" reset "))

        self.assertEqual(axes.clear_calls, [True])
        self.assertFalse(axes.grid_visible)
        self.assertTrue(axes.box_visible)
        self.assertFalse(axes.legend_visible)
        self.assertEqual(axes.y_direction, "normal")
        self.assertFalse(plotter.hold_enabled)
        self.assertEqual(plotter.next_plot, "replace")
        self.assertEqual(plotter.view_stack, [])
        self.assertEqual(plotter.view_index, -1)

    def test_cla_accepts_positional_axes_and_rejects_bad_options(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.cla(axes2)

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [False])

        with self.assertRaisesRegex(ValueError, "Unsupported cla option"):
            plotter.cla("bad")
        with self.assertRaisesRegex(ValueError, "at most one"):
            plotter.cla("reset", "extra")

    def test_plot_normalizes_matlab_like_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.plot([1, 2, 3], [2, 4, 6], [3, 4], [5, 6], "r--", linewidth=2)

        self.assertEqual(artists, ["line-1-0", "line-1-1"])
        self.assertEqual(axes.clear_calls, [True])
        self.assertEqual(len(plotter.drawn_series), 1)
        _axes, series = plotter.drawn_series[0]
        self.assertEqual(
            series,
            (
                PlotSeries(
                    (1.0, 2.0, 3.0),
                    (2.0, 4.0, 6.0),
                    None,
                    (("linewidth", 2),),
                    (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")),
                ),
                PlotSeries(
                    (3.0, 4.0),
                    (5.0, 6.0),
                    "r--",
                    (("linewidth", 2),),
                    (("color", "r"), ("linestyle", "--")),
                ),
            ),
        )
        self.assertEqual(axes.autoscale_calls, [False])
        self.assertGreaterEqual(len(plotter.view_stack), 1)

    def test_plot_respects_hold_add(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.hold("on")

        plotter.plot([1, 2, 3])

        self.assertEqual(axes.clear_calls, [])
        self.assertEqual(plotter.drawn_series[0][1][0].x, (1.0, 2.0, 3.0))
        self.assertEqual(plotter.drawn_series[0][1][0].y, (1.0, 2.0, 3.0))

    def test_plot_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.plot(axes2, [10, 20], [30, 40])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(
            series[0],
            PlotSeries(
                (10.0, 20.0),
                (30.0, 40.0),
                None,
                (),
                (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")),
            ),
        )

    def test_plot_assigns_default_color_order_per_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.plot([[1, 10], [2, 20]])

        _axes, series = plotter.drawn_series[0]
        self.assertEqual(series[0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")))
        self.assertEqual(series[1].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[1]), ("linestyle", "-")))
        self.assertEqual(plotter.next_series_index, 2)

    def test_plot_hold_continues_color_order_and_replace_resets_it(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.plot([1, 2])
        plotter.hold("on")
        plotter.plot([3, 4])
        plotter.hold("off")
        plotter.plot([5, 6])

        self.assertEqual(plotter.drawn_series[0][1][0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")))
        self.assertEqual(plotter.drawn_series[1][1][0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[1]), ("linestyle", "-")))
        self.assertEqual(plotter.drawn_series[2][1][0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")))
        self.assertEqual(plotter.next_series_index, 1)

    def test_plot_explicit_color_does_not_advance_default_color_order(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.plot([1, 2], [3, 4], "r--")
        plotter.hold("on")
        plotter.plot([5, 6])

        self.assertEqual(plotter.drawn_series[0][1][0].line_spec, (("color", "r"), ("linestyle", "--")))
        self.assertEqual(plotter.drawn_series[1][1][0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")))

    def test_plot_color_order_participates_in_view_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.plot([[1, 10], [2, 20]])
        state = plotter.current_view_state()

        self.assertEqual(state.next_series_index, 2)
        self.assertEqual(state.color_order, plotter.DEFAULT_COLOR_ORDER)
        self.assertEqual(state.line_style_order, plotter.DEFAULT_LINE_STYLE_ORDER)

    def test_plot_line_style_order_advances_after_color_order_cycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.color_order = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
        plotter.line_style_order = ("-", "--")
        plotter.hold("on")
        plotter._save_axes_ui_state(axes)

        plotter.plot([[1, 10, 100], [2, 20, 200], [3, 30, 300]])

        _axes, series = plotter.drawn_series[0]
        self.assertEqual(series[0].line_spec, (("color", (1.0, 0.0, 0.0)), ("linestyle", "-")))
        self.assertEqual(series[1].line_spec, (("color", (0.0, 1.0, 0.0)), ("linestyle", "-")))
        self.assertEqual(series[2].line_spec, (("color", (1.0, 0.0, 0.0)), ("linestyle", "--")))

    def test_colororder_linestyleorder_and_nextseriesindex_are_settable(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.colororder([(1, 0, 0), (0, 1, 0)])
        plotter.linestyleorder(["-", "--"])
        plotter.nextseriesindex(2)
        plotter.hold("on")
        plotter.plot([1, 2])

        self.assertEqual(plotter.colororder(), ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        self.assertEqual(plotter.linestyleorder(), ("-", "--"))
        self.assertEqual(plotter.drawn_series[0][1][0].line_spec, (("color", (1.0, 0.0, 0.0)), ("linestyle", "--")))
        self.assertEqual(plotter.nextseriesindex(), 3)

    def test_colororder_and_linestyleorder_default_reset_series_index(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.nextseriesindex(3)

        plotter.colororder("default")
        plotter.linestyleorder("default")

        self.assertEqual(plotter.colororder(), plotter.DEFAULT_COLOR_ORDER)
        self.assertEqual(plotter.linestyleorder(), plotter.DEFAULT_LINE_STYLE_ORDER)
        self.assertEqual(plotter.nextseriesindex(), 0)

    def test_plot_order_helpers_are_scoped_per_axes(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.colororder([(1, 0, 0)], axes=axes2)
        plotter.linestyleorder("--", axes=axes2)
        plotter.nextseriesindex(0, axes=axes2)
        plotter.set_active_axes(axes2)
        plotter.hold("on")
        plotter.set_active_axes(axes1)
        plotter.plot(axes2, [1, 2])

        self.assertEqual(plotter.drawn_series[0][1][0].line_spec, (("color", (1.0, 0.0, 0.0)), ("linestyle", "--")))
        self.assertEqual(plotter.colororder(axes=axes1), plotter.DEFAULT_COLOR_ORDER)

    def test_plot_order_helpers_validate_values(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "N-by-3"):
            plotter.colororder([(1, 0)])
        with self.assertRaisesRegex(ValueError, "between 0 and 1"):
            plotter.colororder([(1.2, 0, 0)])
        with self.assertRaisesRegex(ValueError, "linestyleorder"):
            plotter.linestyleorder(["bad"])
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            plotter.nextseriesindex(-1)

    def test_semilog_helpers_apply_axis_scales_after_plot(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.semilogx([1, 10], [2, 3])
        self.assertEqual(axes.x_scale, "log")
        self.assertEqual(axes.y_scale, "linear")
        self.assertEqual(len(plotter.drawn_series), 1)

        plotter.semilogy([1, 10], [2, 3])
        self.assertEqual(axes.x_scale, "linear")
        self.assertEqual(axes.y_scale, "log")

        plotter.loglog([1, 10], [2, 3])
        self.assertEqual(axes.x_scale, "log")
        self.assertEqual(axes.y_scale, "log")

    def test_semilog_helpers_accept_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.loglog(axes2, [1, 10], [2, 20])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        self.assertEqual(axes2.x_scale, "log")
        self.assertEqual(axes2.y_scale, "log")

    def test_scatter_normalizes_xy_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.scatter([1, 2], [3, 4], "DisplayName", "points")

        self.assertEqual(artists, ["scatter-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_scatter_series[0]
        self.assertEqual(
            series[0],
            ScatterSeries(
                (1.0, 2.0),
                (3.0, 4.0),
                None,
                None,
                (("label", "points"),),
                (("color", plotter.DEFAULT_COLOR_ORDER[0]),),
            ),
        )
        self.assertEqual(axes.autoscale_calls, [False])
        self.assertGreaterEqual(len(plotter.view_stack), 1)

    def test_scatter_assigns_default_color_order_per_series(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.scatter([1, 2], [[10, 100], [20, 200]])

        _axes, series = plotter.drawn_scatter_series[0]
        self.assertEqual(series[0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]),))
        self.assertEqual(series[1].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[1]),))
        self.assertEqual(plotter.next_series_index, 2)

    def test_scatter_preserves_explicit_size_and_color(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.scatter([1, 2], [3, 4], [20, 40], [1, 0, 0], "LineWidth", 2)

        _axes, series = plotter.drawn_scatter_series[0]
        self.assertEqual(
            series[0],
            ScatterSeries(
                (1.0, 2.0),
                (3.0, 4.0),
                (20.0, 40.0),
                (1.0, 0.0, 0.0),
                (("linewidth", 2),),
                (("color", (1.0, 0.0, 0.0)),),
            ),
        )
        self.assertEqual(plotter.next_series_index, 0)

    def test_scatter_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.scatter(axes2, [10, 20], [30, 40], 36, "blue")

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_scatter_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].size, 36.0)
        self.assertEqual(series[0].color, "blue")

    def test_scatter_validates_size_and_color(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "size vector length"):
            plotter.scatter([1, 2], [3, 4], [10])
        with self.assertRaisesRegex(ValueError, "finite nonnegative"):
            plotter.scatter([1, 2], [3, 4], -1)
        with self.assertRaisesRegex(ValueError, "RGB triplet"):
            plotter.scatter([1, 2], [3, 4], 10, [1, 0])
        with self.assertRaisesRegex(ValueError, "color rows"):
            plotter.scatter([1, 2], [3, 4], 10, [[1, 0, 0]])

    
    def test_scatter3_normalizes_xyz_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.scatter3([1, 2, 3], [4, 5, 6], [7, 8, 9])

        self.assertEqual(artists, ["scatter3-1-0"])
        _axes, series = plotter.drawn_scatter3_series[0]
        self.assertEqual(len(series[0].x), 3)
        self.assertEqual(len(series[0].y), 3)
        self.assertEqual(len(series[0].z), 3)

    def test_scatter3_requires_xyz(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "scatter3"):
            plotter.scatter3([1, 2], [3, 4])

    def test_stem3_normalizes_xyz_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.stem3([1, 2, 3], [4, 5, 6], [7, 8, 9])

        self.assertEqual(artists, ["stem3-1-0"])
        _axes, series = plotter.drawn_stem3_series[0]
        self.assertEqual(len(series[0].x), 3)
        self.assertEqual(len(series[0].y), 3)
        self.assertEqual(len(series[0].z), 3)

    def test_stem3_requires_xyz(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "stem3"):
            plotter.stem3([1, 2], [3, 4])


    def test_stem_normalizes_y_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.stem([10, 20, 30], "DisplayName", "stems")

        self.assertEqual(artists, ["stem-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_stem_series[0]
        self.assertEqual(
            series[0],
            StemSeries(
                (1.0, 2.0, 3.0),
                (10.0, 20.0, 30.0),
                None,
                (("label", "stems"),),
                (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")),
            ),
        )
        self.assertEqual(axes.autoscale_calls, [False])

    def test_stem_accepts_xy_linespec_and_matrix_columns(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.stem([1, 2], [[10, 100], [20, 200]], "r--o")

        _axes, series = plotter.drawn_stem_series[0]
        self.assertEqual(
            series,
            (
                StemSeries((1.0, 2.0), (10.0, 20.0), "r--o", (), (("color", "r"), ("linestyle", "--"), ("marker", "o"))),
                StemSeries((1.0, 2.0), (100.0, 200.0), "r--o", (), (("color", "r"), ("linestyle", "--"), ("marker", "o"))),
            ),
        )
        self.assertEqual(plotter.next_series_index, 0)

    def test_stem_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.stem(axes2, [10, 20], [30, 40])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_stem_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_bar_normalizes_y_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.bar([10, 20, 30], "DisplayName", "bars")

        self.assertEqual(artists, ["bar-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_bar_series[0]
        self.assertEqual(
            series[0],
            BarSeries(
                (1.0, 2.0, 3.0),
                (10.0, 20.0, 30.0),
                None,
                (("label", "bars"),),
                (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")),
            ),
        )
        self.assertEqual(axes.autoscale_calls, [False])

    def test_bar_accepts_xy_linespec_and_matrix_columns(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.bar([1, 2], [[10, 100], [20, 200]], "g:")

        _axes, series = plotter.drawn_bar_series[0]
        self.assertEqual(
            series,
            (
                BarSeries((1.0, 2.0), (10.0, 20.0), "g:", (), (("color", "g"), ("linestyle", ":"))),
                BarSeries((1.0, 2.0), (100.0, 200.0), "g:", (), (("color", "g"), ("linestyle", ":"))),
            ),
        )
        self.assertEqual(plotter.next_series_index, 0)

    def test_bar_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.bar(axes2, [10, 20], [30, 40])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_bar_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_barh_normalizes_y_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.barh([10, 20, 30], "DisplayName", "bars")

        self.assertEqual(artists, ["barh-1-0"])
        _axes, series = plotter.drawn_barh_series[0]
        self.assertEqual(len(series[0].y), 3)
        self.assertEqual(len(series[0].x), 3)

    def test_barh_accepts_positional_axes_handle(self):
        axes1 = FakeAxes()
        axes2 = FakeAxes()
        plotter = FakePlotter(axes1)

        artists = plotter.barh(axes2, [10, 20], [30, 40])

        self.assertTrue(plotter.is_active_axes(axes2))
        _axes, series = plotter.drawn_barh_series[0]
        self.assertEqual(len(series[0].y), 2)


    def test_area_normalizes_y_series_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.area([10, 20, 30], "DisplayName", "area")

        self.assertEqual(artists, ["area-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_area_series[0]
        self.assertEqual(
            series[0],
            AreaSeries(
                (1.0, 2.0, 3.0),
                (10.0, 20.0, 30.0),
                (0.0, 0.0, 0.0),
                None,
                (("label", "area"),),
                (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")),
            ),
        )
        self.assertEqual(axes.autoscale_calls, [False])

    def test_area_matrix_columns_stack_by_shared_x_data(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.area([1, 2], [[10, 100], [20, 200]])

        _axes, series = plotter.drawn_area_series[0]
        self.assertEqual(series[0].baseline, (0.0, 0.0))
        self.assertEqual(series[0].y, (10.0, 20.0))
        self.assertEqual(series[1].baseline, (10.0, 20.0))
        self.assertEqual(series[1].y, (110.0, 220.0))
        self.assertEqual(series[0].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[0]), ("linestyle", "-")))
        self.assertEqual(series[1].line_spec, (("color", plotter.DEFAULT_COLOR_ORDER[1]), ("linestyle", "-")))

    def test_area_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.area(axes2, [10, 20], [30, 40])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_area_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))
        self.assertEqual(series[0].baseline, (0.0, 0.0))

    def test_fill_normalizes_polygon_color_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.fill([0, 1, 0], [0, 0, 1], "red", "DisplayName", "triangle")

        self.assertEqual(artists, ["fill-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_fill_series[0]
        self.assertEqual(
            series[0],
            FillSeries(
                (0.0, 1.0, 0.0),
                (0.0, 0.0, 1.0),
                "red",
                (("label", "triangle"),),
                (("facecolor", "red"),),
            ),
        )
        self.assertEqual(plotter.next_series_index, 0)
        self.assertEqual(axes.autoscale_calls, [False])

    def test_fill_without_explicit_color_uses_color_order(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.fill([0, 1, 0], [0, 0, 1])

        _axes, series = plotter.drawn_fill_series[0]
        self.assertEqual(series[0].line_spec, (("facecolor", plotter.DEFAULT_COLOR_ORDER[0]),))
        self.assertEqual(plotter.next_series_index, 1)

    def test_fill_accepts_repeated_polygon_groups(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.fill([0, 1, 0], [0, 0, 1], "r", [2, 3, 2], [0, 0, 1], [0, 1, 0])

        _axes, series = plotter.drawn_fill_series[0]
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0].color, "r")
        self.assertEqual(series[1].color, (0.0, 1.0, 0.0))
        self.assertEqual(series[1].x, (2.0, 3.0, 2.0))

    def test_fill_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.fill(axes2, [0, 1, 0], [0, 0, 1], [0, 0, 1])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_fill_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].color, (0.0, 0.0, 1.0))

    def test_histogram_normalizes_values_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.histogram([1, 2, 2, 3], "DisplayName", "hist")

        self.assertEqual(artists, ["histogram-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_histogram_series[0]
        self.assertEqual(
            series[0],
            HistogramSeries(
                (1.0, 2.0, 2.0, 3.0),
                None,
                (("label", "hist"),),
                (("facecolor", plotter.DEFAULT_COLOR_ORDER[0]),),
            ),
        )
        self.assertEqual(plotter.next_series_index, 1)
        self.assertEqual(axes.autoscale_calls, [False])

    def test_histogram_accepts_bin_count_and_edges(self):
        plotter = FakePlotter(FakeAxes())

        count_series = plotter.normalize_histogram_args(([1, 2, 3], 5))
        edge_series = plotter.normalize_histogram_args(([1, 2, 3], [0, 1, 2, 3]))

        self.assertEqual(count_series[0].bins, 5)
        self.assertEqual(edge_series[0].bins, (0.0, 1.0, 2.0, 3.0))

    def test_histogram_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.histogram(axes2, [1, 2, 3], [0, 2, 4])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_histogram_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].bins, (0.0, 2.0, 4.0))

    def test_histogram_validates_bins(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "positive integer"):
            plotter.histogram([1, 2, 3], 0)
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            plotter.histogram([1, 2, 3], [0, 2, 2])

    def test_xline_adds_constant_lines_without_nextplot_or_series_order(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.xline([1, 2], "r--", "limit", "LineWidth", 2)

        self.assertEqual(artists, ["constant-line-1-0", "constant-line-1-1"])
        self.assertEqual(axes.clear_calls, [])
        _axes, series = plotter.drawn_constant_line_series[0]
        self.assertEqual(
            series,
            (
                ConstantLineSeries("x", 1.0, "limit", "r--", (("linewidth", 2),), (("color", "r"), ("linestyle", "--"))),
                ConstantLineSeries("x", 2.0, "limit", "r--", (("linewidth", 2),), (("color", "r"), ("linestyle", "--"))),
            ),
        )
        self.assertEqual(plotter.next_series_index, 0)

    def test_yline_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.yline(axes2, 3, "k:", "threshold")

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [])
        drawn_axes, series = plotter.drawn_constant_line_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0], ConstantLineSeries("y", 3.0, "threshold", "k:", (), (("color", "k"), ("linestyle", ":"))))

    def test_text_adds_annotation_without_nextplot_clear(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.text(1, 2, ["hello", "world"], "Color", "red")

        self.assertEqual(artists, ["text-1-0"])
        self.assertEqual(axes.clear_calls, [])
        _axes, series = plotter.drawn_text_series[0]
        self.assertEqual(series[0], TextSeries(1.0, 2.0, None, ("hello", "world"), (("color", "red"),)))

    def test_text_accepts_3d_and_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2", is_3d=True)
        plotter = FakePlotter(axes1)

        plotter.text(axes2, 1, 2, 3, "label")

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [])
        drawn_axes, series = plotter.drawn_text_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0], TextSeries(1.0, 2.0, 3.0, ("label",), ()))

    def test_imagesc_normalizes_cdata_and_runs_plot_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.imagesc([[1, 2], [3, 4]], "DisplayName", "img")

        self.assertEqual(artists, ["image-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_image_series[0]
        self.assertEqual(series[0], ImageSeries(((1.0, 2.0), (3.0, 4.0)), None, None, (("label", "img"),)))
        self.assertEqual(axes.autoscale_clim_calls, 1)
        self.assertEqual(axes.autoscale_calls, [False])

    def test_imagesc_accepts_x_y_and_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.imagesc(axes2, [10, 20], [30, 40], [[1, 2], [3, 4]])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        drawn_axes, series = plotter.drawn_image_series[0]
        self.assertIs(drawn_axes, axes2)
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_imagesc_does_not_autoscale_clim_in_manual_mode(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.clim("manual")
        plotter.hold("on")
        axes.autoscale_clim_calls = 0

        plotter.imagesc([[1, 2], [3, 4]])

        self.assertEqual(axes.autoscale_clim_calls, 0)

    def test_imagesc_validates_cdata_and_axis_vectors(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "nonempty"):
            plotter.imagesc([])
        with self.assertRaisesRegex(ValueError, "two axis endpoints"):
            plotter.imagesc([1, 2, 3], [1, 2], [[1, 2], [3, 4]])

    def test_contour_normalizes_z_and_runs_plot_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.contour([[1, 2], [3, 4]])

        self.assertEqual(artists, ["contour-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_contour_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))
        self.assertIsNone(series[0].x)
        self.assertIsNone(series[0].y)
        self.assertIsNone(series[0].levels)
        self.assertEqual(axes.autoscale_clim_calls, 1)

    def test_contour_accepts_x_y_z_and_levels(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.contour([10, 20], [30, 40], [[1, 2], [3, 4]], [1.5, 2.5])

        self.assertEqual(artists, ["contour-1-0"])
        _axes, series = plotter.drawn_contour_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))
        self.assertEqual(series[0].levels, (1.5, 2.5))

    def test_contour_does_not_autoscale_clim_in_manual_mode(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.clim("manual")
        plotter.hold("on")
        axes.autoscale_clim_calls = 0

        plotter.contour([[1, 2], [3, 4]])

        self.assertEqual(axes.autoscale_clim_calls, 0)


    def test_contour3_normalizes_z_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.contour3([[1, 2], [3, 4]])

        self.assertEqual(artists, ["contour-1-0"])
        _axes, series = plotter.drawn_contour_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))

    def test_contour3_accepts_x_y_z(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.contour3([10, 20], [30, 40], [[1, 2], [3, 4]])

        _axes, series = plotter.drawn_contour_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_contourf_normalizes_z_and_runs_plot_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.contourf([[1, 2], [3, 4]])

        self.assertEqual(artists, ["contourf-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_contourf_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))
        self.assertIsNone(series[0].levels)

    def test_contourf_accepts_x_y_z_and_levels(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.contourf([10, 20], [30, 40], [[1, 2], [3, 4]], [1.5, 2.5])

        _axes, series = plotter.drawn_contourf_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))
        self.assertEqual(series[0].levels, (1.5, 2.5))

    def test_contour_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "nonempty"):
            plotter.contour([])
        with self.assertRaisesRegex(ValueError, "contour requires"):
            plotter.contour([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])


    def test_surf_normalizes_z_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.surf([[1, 2], [3, 4]])

        self.assertEqual(artists, ["surf-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_surf_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))
        self.assertIsNone(series[0].x)
        self.assertIsNone(series[0].cdata)

    def test_surf_accepts_x_y_z_and_cdata(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.surf([10, 20], [30, 40], [[1, 2], [3, 4]], [[5, 6], [7, 8]])

        _axes, series = plotter.drawn_surf_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))
        self.assertEqual(series[0].cdata, ((5.0, 6.0), (7.0, 8.0)))



    def test_ribbon_normalizes_z_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.ribbon([[1, 2], [3, 4]])

        self.assertEqual(artists, ["mesh-1-0"])
        _axes, series = plotter.drawn_mesh_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))

    def test_ribbon_accepts_x_y_z(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.ribbon([10, 20], [30, 40], [[1, 2], [3, 4]])

        _axes, series = plotter.drawn_mesh_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_waterfall_normalizes_z_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.waterfall([[1, 2], [3, 4]])

        self.assertEqual(artists, ["mesh-1-0"])
        _axes, series = plotter.drawn_mesh_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))

    def test_waterfall_accepts_x_y_z(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.waterfall([10, 20], [30, 40], [[1, 2], [3, 4]])

        _axes, series = plotter.drawn_mesh_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_mesh_normalizes_z_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.mesh([[1, 2], [3, 4]])

        self.assertEqual(artists, ["mesh-1-0"])
        _axes, series = plotter.drawn_mesh_series[0]
        self.assertEqual(series[0].zdata, ((1.0, 2.0), (3.0, 4.0)))

    def test_surf_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "nonempty"):
            plotter.surf([])
        with self.assertRaisesRegex(ValueError, "surf requires"):
            plotter.surf([1, 2], [3, 4], [5, 6], [7, 8], [9, 10])


    def test_quiver_normalizes_uv_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.quiver([1, 2], [3, 4])

        self.assertEqual(artists, ["quiver-1-0"])
        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(series[0].u, (1.0, 2.0))
        self.assertEqual(series[0].v, (3.0, 4.0))
        self.assertIsNone(series[0].x)

    def test_quiver_accepts_xy_uv(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.quiver([10, 20], [30, 40], [1, 2], [3, 4])

        _axes, series = plotter.drawn_quiver_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))
        self.assertEqual(series[0].u, (1.0, 2.0))
        self.assertEqual(series[0].v, (3.0, 4.0))

    def test_quiver_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "quiver requires"):
            plotter.quiver([1])
        with self.assertRaisesRegex(ValueError, "quiver requires"):
            plotter.quiver([1], [2], [3])



    def test_spy_normalizes_sparse_matrix_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        matrix = [[0, 1, 0], [1, 0, 1]]
        artists = plotter.spy(matrix)

        self.assertEqual(artists, ["spy-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_spy_series[0]
        self.assertEqual(series[0].row_indices, (0, 1, 1))
        self.assertEqual(series[0].col_indices, (1, 0, 2))
        self.assertEqual(series[0].nrows, 2)
        self.assertEqual(series[0].ncols, 3)

    def test_spy_accepts_positional_axes(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        artists = plotter.spy(axes2, [[1, 0], [0, 1]])

        self.assertIs(plotter.active_axes, axes2)
        _axes, series = plotter.drawn_spy_series[0]
        self.assertEqual(series[0].row_indices, (0, 1))
        self.assertEqual(series[0].col_indices, (0, 1))

    def test_spy_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "matrix argument"):
            plotter.spy()

    def test_pcolor_normalizes_cdata_and_runs_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pcolor([[1, 2], [3, 4]])

        self.assertEqual(artists, ["pcolor-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_pcolor_series[0]
        self.assertEqual(series[0].cdata, ((1.0, 2.0), (3.0, 4.0)))
        self.assertIsNone(series[0].x)

    def test_pcolor_accepts_x_y_cdata(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.pcolor([10, 20], [30, 40], [[1, 2], [3, 4]])

        _axes, series = plotter.drawn_pcolor_series[0]
        self.assertEqual(series[0].x, (10.0, 20.0))
        self.assertEqual(series[0].y, (30.0, 40.0))

    def test_pcolor_validates_arguments(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "nonempty"):
            plotter.pcolor([])
        with self.assertRaisesRegex(ValueError, "pcolor requires"):
            plotter.pcolor([1, 2], [3, 4], [5, 6], [7, 8])

    def test_plot3_normalizes_xyz_series_and_runs_lifecycle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.plot3([1, 2], [3, 4], [5, 6], "r--", "DisplayName", "path")

        self.assertEqual(artists, ["line3-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        self.assertEqual(
            plotter.drawn_plot3_series[0][1],
            (
                Plot3Series(
                    (1.0, 2.0),
                    (3.0, 4.0),
                    (5.0, 6.0),
                    "r--",
                    (("label", "path"),),
                    (("color", "r"), ("linestyle", "--")),
                ),
            ),
        )

    def test_plot3_matrix_columns_expand_xyz_series(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))

        series = plotter.normalize_plot3_args((
            [[1, 10], [2, 20]],
            [[3, 30], [4, 40]],
            [[5, 50], [6, 60]],
            "o",
        ))

        self.assertEqual(
            series,
            [
                Plot3Series((1.0, 2.0), (3.0, 4.0), (5.0, 6.0), "o", (), (("marker", "o"),)),
                Plot3Series((10.0, 20.0), (30.0, 40.0), (50.0, 60.0), "o", (), (("marker", "o"),)),
            ],
        )

    def test_plot3_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1", is_3d=True)
        axes2 = FakeAxes("axes2", is_3d=True)
        plotter = FakePlotter(axes1)

        plotter.plot3(axes2, [1, 2], [3, 4], [5, 6])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        self.assertEqual(plotter.drawn_plot3_series[0][0], axes2)

    def test_stairs_expands_points_and_runs_plot_lifecycle(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.stairs([1, 2, 3], [10, 20, 30], "r--")

        self.assertEqual(artists, ["line-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_series[0]
        self.assertEqual(series[0].x, (1.0, 2.0, 2.0, 3.0, 3.0))
        self.assertEqual(series[0].y, (10.0, 10.0, 20.0, 20.0, 30.0))
        self.assertEqual(series[0].line_spec, (("color", "r"), ("linestyle", "--")))

    def test_stairs_matrix_columns_expand_independently(self):
        plotter = FakePlotter(FakeAxes())

        plotter.stairs([1, 2], [[10, 100], [20, 200]])

        _axes, series = plotter.drawn_series[0]
        self.assertEqual(series[0].x, (1.0, 2.0, 2.0))
        self.assertEqual(series[0].y, (10.0, 10.0, 20.0))
        self.assertEqual(series[1].x, (1.0, 2.0, 2.0))
        self.assertEqual(series[1].y, (100.0, 100.0, 200.0))

    def test_stairs_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.stairs(axes2, [1, 2], [3, 4])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [True])
        self.assertIs(plotter.drawn_series[0][0], axes2)

    def test_line_adds_2d_primitive_without_nextplot_clear_or_series_order(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.line([1, 2], [3, 4], "Color", "red")

        self.assertEqual(artists, ["line-1-0"])
        self.assertEqual(axes.clear_calls, [])
        _axes, series = plotter.drawn_series[0]
        self.assertEqual(series[0], PlotSeries((1.0, 2.0), (3.0, 4.0), None, (("color", "red"),)))

    def test_line_adds_3d_primitive_without_nextplot_clear(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        artists = plotter.line([1, 2], [3, 4], [5, 6], "LineStyle", "--")

        self.assertEqual(artists, ["line3-1-0"])
        self.assertEqual(axes.clear_calls, [])
        _axes, series = plotter.drawn_plot3_series[0]
        self.assertEqual(series[0], Plot3Series((1.0, 2.0), (3.0, 4.0), (5.0, 6.0), None, (("linestyle", "--"),)))

    def test_line_accepts_positional_axes_handle(self):
        axes1 = FakeAxes("axes1")
        axes2 = FakeAxes("axes2")
        plotter = FakePlotter(axes1)

        plotter.line(axes2, [1, 2], [3, 4])

        self.assertIs(plotter.active_axes, axes2)
        self.assertEqual(axes1.clear_calls, [])
        self.assertEqual(axes2.clear_calls, [])
        self.assertIs(plotter.drawn_series[0][0], axes2)

    def test_errorbar_normalizes_y_and_symmetric_error(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        artists = plotter.errorbar([10, 20], [1, 2], "r--", "DisplayName", "err")

        self.assertEqual(artists, ["errorbar-1-0"])
        self.assertEqual(axes.clear_calls, [True])
        _axes, series = plotter.drawn_errorbar_series[0]
        self.assertEqual(
            series[0],
            ErrorBarSeries(
                (1.0, 2.0),
                (10.0, 20.0),
                (1.0, 2.0),
                (1.0, 2.0),
                "r--",
                (("label", "err"),),
                (("color", "r"), ("linestyle", "--")),
            ),
        )

    def test_errorbar_normalizes_x_y_negative_positive_errors(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_errorbar_args(([1, 2], [10, 20], [0.5, 1.0], [1.5, 2.0]))

        self.assertEqual(
            series,
            [
                ErrorBarSeries(
                    (1.0, 2.0),
                    (10.0, 20.0),
                    (0.5, 1.0),
                    (1.5, 2.0),
                )
            ],
        )

    def test_errorbar_matrix_columns_expand_errors(self):
        plotter = FakePlotter(FakeAxes())

        plotter.errorbar([1, 2], [[10, 100], [20, 200]], [[1, 10], [2, 20]])

        _axes, series = plotter.drawn_errorbar_series[0]
        self.assertEqual(series[0].y, (10.0, 20.0))
        self.assertEqual(series[0].y_negative, (1.0, 2.0))
        self.assertEqual(series[1].y, (100.0, 200.0))
        self.assertEqual(series[1].y_negative, (10.0, 20.0))

    def test_plot_y_matrix_expands_columns(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([[1, 10], [2, 20], [3, 30]],))

        self.assertEqual(
            series,
            [
                PlotSeries((1.0, 2.0, 3.0), (1.0, 2.0, 3.0)),
                PlotSeries((1.0, 2.0, 3.0), (10.0, 20.0, 30.0)),
            ],
        )

    def test_plot_x_vector_y_matrix_expands_columns(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([10, 20, 30], [[1, 10], [2, 20], [3, 30]]), {"color": "blue"})

        self.assertEqual(
            series,
            [
                PlotSeries((10.0, 20.0, 30.0), (1.0, 2.0, 3.0), None, (("color", "blue"),)),
                PlotSeries((10.0, 20.0, 30.0), (10.0, 20.0, 30.0), None, (("color", "blue"),)),
            ],
        )

    def test_plot_x_y_matrices_pair_columns(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([[1, 10], [2, 20]], [[3, 30], [4, 40]], "o"))

        self.assertEqual(
            series,
            [
                PlotSeries((1.0, 2.0), (3.0, 4.0), "o", (), (("marker", "o"),)),
                PlotSeries((10.0, 20.0), (30.0, 40.0), "o", (), (("marker", "o"),)),
            ],
        )

    def test_plot_accepts_matlab_name_value_properties(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([1, 2], [3, 4], "r--", "LineWidth", 2, "DisplayName", "signal"))

        self.assertEqual(
            series,
            [
                PlotSeries(
                    (1.0, 2.0),
                    (3.0, 4.0),
                    "r--",
                    (("linewidth", 2), ("label", "signal")),
                    (("color", "r"), ("linestyle", "--")),
                )
            ],
        )

    def test_plot_parses_matlab_line_spec(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([1, 2], [3, 4], "--or"))

        self.assertEqual(series[0].style, "--or")
        self.assertEqual(series[0].line_spec, (("color", "r"), ("linestyle", "--"), ("marker", "o")))

    def test_plot_keeps_unparsed_line_spec_as_raw_style(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([1, 2], [3, 4], "custom-style"))

        self.assertEqual(series[0].style, "custom-style")
        self.assertEqual(series[0].line_spec, ())

    def test_plot_merges_kwargs_with_matlab_property_aliases(self):
        plotter = FakePlotter(FakeAxes())

        series = plotter.normalize_plot_args(([1, 2], "Color", "red"), {"DisplayName": "series"})

        self.assertEqual(
            series,
            [
                PlotSeries(
                    (1.0, 2.0),
                    (1.0, 2.0),
                    None,
                    (("color", "red"), ("label", "series")),
                )
            ],
        )

    def test_plot_rejects_mismatched_x_y_lengths(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "same length"):
            plotter.plot([1, 2], [1])

    def test_prepare_replace_restores_default_grid_box_and_legend_state(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.grid("on")
        plotter.box("off")
        plotter.legend("on")

        plotter.prepare_for_plot()

        self.assertFalse(axes.grid_visible)
        self.assertTrue(axes.box_visible)
        self.assertFalse(axes.legend_visible)
        state = plotter.current_view_state()
        self.assertFalse(state.grid_visible)
        self.assertTrue(state.box_visible)
        self.assertFalse(state.legend_visible)

    def test_replace_plot_clears_view_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_xlim(1.0, 2.0)

        plotter.prepare_for_plot()

        self.assertEqual(axes.clear_calls, [True])
        self.assertEqual(plotter.view_stack, [])
        self.assertEqual(plotter.view_index, -1)
        self.assertFalse(plotter.can_home())
        self.assertFalse(plotter.can_back())
        self.assertFalse(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (-1, 0, False, False))

    def test_replace_plot_resets_axes_ui_and_backend_properties(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_xlim(1.0, 2.0)
        plotter.axis("equal")
        plotter.axis("square")
        plotter.axis("off")
        plotter.axis("ij")
        plotter.view(45.0, 20.0)

        plotter.prepare_for_plot()

        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(plotter.clim_mode, "auto")
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")
        self.assertTrue(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "normal")
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(axes.aspect, "auto")
        self.assertEqual(axes.box_aspect, "auto")
        self.assertTrue(axes.axis_visible)
        self.assertEqual(axes.y_direction, "normal")

    def test_replacechildren_keeps_axes_ui_properties(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.axis("equal")
        plotter.axis("off")
        plotter.axis("ij")
        plotter.view(45.0, 20.0)
        plotter.set_next_plot("replacechildren")

        plotter.prepare_for_plot()

        self.assertEqual(plotter.axis_aspect, "equal")
        self.assertFalse(plotter.axis_visible)
        self.assertEqual(plotter.y_direction, "reverse")
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(axes.aspect, "equal")
        self.assertFalse(axes.axis_visible)
        self.assertEqual(axes.y_direction, "reverse")

    def test_add_and_replacechildren_keep_view_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_xlim(1.0, 2.0)

        plotter.hold("on")
        plotter.prepare_for_plot()
        self.assertEqual(axes.clear_calls, [])
        self.assertEqual(len(plotter.view_stack), 2)
        self.assertEqual(plotter.view_index, 1)

        plotter.set_next_plot("replacechildren")
        plotter.prepare_for_plot()
        self.assertEqual(axes.clear_calls, [False])
        self.assertEqual(len(plotter.view_stack), 2)
        self.assertEqual(plotter.view_index, 1)

    def test_scroll_zoom_sets_manual_limits_and_pushes_view(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=1.0))

        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertLess(axes.limits.xlim[1] - axes.limits.xlim[0], 10.0)
        self.assertEqual(len(plotter.view_stack), 1)

    def test_scroll_with_zero_step_is_ignored(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=0.0), base_scale=1.0)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_scroll_rejects_invalid_base_scale(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        event = PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=1.0)

        for base_scale in (1.0, 0.0, -2.0, float("nan"), float("inf")):
            with self.subTest(base_scale=base_scale):
                with self.assertRaisesRegex(ValueError, "base_scale"):
                    plotter.on_scroll(event, base_scale=base_scale)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_scroll_ignores_nonfinite_pointer_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=float("nan"), ydata=0.0, step=1.0))
        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=float("inf"), step=1.0))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_scroll_ignores_nonfinite_step(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=float("nan")))
        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=float("inf")))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_scroll_zoom_uses_step_magnitude(self):
        axes_multi_step = FakeAxes()
        plotter_multi_step = FakePlotter(axes_multi_step)
        axes_repeated = FakeAxes()
        plotter_repeated = FakePlotter(axes_repeated)

        plotter_multi_step.on_scroll(PointerEvent(axes=axes_multi_step, xdata=5.0, ydata=0.0, step=2.0))
        plotter_repeated.on_scroll(PointerEvent(axes=axes_repeated, xdata=5.0, ydata=0.0, step=1.0))
        plotter_repeated.on_scroll(PointerEvent(axes=axes_repeated, xdata=5.0, ydata=0.0, step=1.0))

        self.assertAlmostEqual(axes_multi_step.limits.xlim[0], axes_repeated.limits.xlim[0])
        self.assertAlmostEqual(axes_multi_step.limits.xlim[1], axes_repeated.limits.xlim[1])
        self.assertAlmostEqual(axes_multi_step.limits.ylim[0], axes_repeated.limits.ylim[0])
        self.assertAlmostEqual(axes_multi_step.limits.ylim[1], axes_repeated.limits.ylim[1])

    def test_scroll_zoom_respects_zoom_motion_and_direction(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.zoom_motion = "horizontal"
        plotter.zoom_direction = "out"

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=1.0))

        self.assertEqual(axes.limits, AxesLimits((-1.0, 11.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "auto")

    def test_scroll_zoom_on_3d_axes_does_not_mark_z_limits_manual(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=1.0))

        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "auto")

    def test_scroll_zoom_on_3d_axes_uses_camera_view_angle_when_available(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)

        plotter.on_scroll(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, step=1.0))

        self.assertAlmostEqual(axes.camera.view_angle, 8.339796221)
        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")

    def test_axis_auto_and_tight_reset_axes_limit_modes_and_autoscale(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.xlim_mode = "manual"
        plotter.ylim_mode = "manual"
        plotter.zlim_mode = "manual"
        plotter.clim_mode = "manual"

        plotter.axis("auto")
        plotter.axis("tight")

        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(plotter.clim_mode, "manual")
        self.assertEqual(axes.autoscale_calls, [False, True])
        self.assertEqual(len(plotter.view_stack), 1)

    def test_axis_manual_freezes_axes_limit_modes_without_autoscale(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.clim_mode = "auto"

        plotter.axis("manual")

        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "auto")
        self.assertEqual(axes.autoscale_calls, [])
        self.assertEqual(len(plotter.view_stack), 1)

    def test_repeating_axis_manual_is_noop(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.axis("manual")
        history_after_first_manual = list(plotter.view_history_changes)
        plotter.axis("manual")

        self.assertEqual(plotter.view_history_changes, history_after_first_manual)
        self.assertEqual(len(plotter.view_stack), 1)

    def test_axis_normalizes_string_case_and_whitespace(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("  TiGhT  ")

        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(axes.autoscale_calls, [True])

    def test_axis_error_preserves_original_value(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, " bad axis "):
            plotter.axis(" bad axis ")

    def test_axis_without_arguments_returns_current_limits_without_pushing_history(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((1.0, 4.0), (-2.0, 3.0))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.axis(), (1.0, 4.0, -2.0, 3.0))
        self.assertEqual(plotter.view_stack, [])

    def test_axis_without_arguments_returns_3d_limits(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((1.0, 4.0), (-2.0, 3.0), (10.0, 20.0), (0.2, 0.8))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.axis(), (1.0, 4.0, -2.0, 3.0, 10.0, 20.0))

    def test_axis_state_reports_auto_or_manual_limit_modes_without_pushing_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.axis("state"), "auto")
        plotter.clim([0.2, 0.8])
        self.assertEqual(plotter.axis("state"), "auto")
        plotter.set_xlim(1.0, 2.0)
        self.assertEqual(plotter.axis(" state "), "manual")
        plotter.axis("auto")
        self.assertEqual(plotter.axis("state"), "auto")
        self.assertEqual(plotter.clim_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 3)

    def test_axis_limit_vector_sets_2d_limits_and_manual_modes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis([1.0, 4.0, -2.0, 3.0])

        self.assertEqual(axes.limits, AxesLimits((1.0, 4.0), (-2.0, 3.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(plotter.clim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_axis_limit_vector_sets_3d_limits(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.axis((1.0, 4.0, -2.0, 3.0, 10.0, 20.0))

        self.assertEqual(axes.limits, AxesLimits((1.0, 4.0), (-2.0, 3.0), (10.0, 20.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")

    def test_axis_limit_vector_sets_3d_limits_and_color_limits(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0), (0.0, 1.0))
        plotter = FakePlotter(axes)

        plotter.axis((1.0, 4.0, -2.0, 3.0, 10.0, 20.0, 0.2, 0.8))

        self.assertEqual(axes.limits, AxesLimits((1.0, 4.0), (-2.0, 3.0), (10.0, 20.0), (0.2, 0.8)))
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "manual")

    def test_set_clim_updates_color_limits_and_records_history(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), None, (0.0, 1.0))
        plotter = FakePlotter(axes)

        plotter.set_clim(0.2, 0.8)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), None, (0.2, 0.8)))
        self.assertEqual(plotter.clim_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_repeating_same_manual_limits_is_noop(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((1.0, 2.0), (-3.0, 4.0), (5.0, 6.0), (0.2, 0.8))
        plotter = FakePlotter(axes)

        plotter.set_xlim(1.0, 2.0)
        plotter.set_ylim(-3.0, 4.0)
        plotter.set_zlim(5.0, 6.0)
        plotter.set_clim(0.2, 0.8)
        history_after_first_set = list(plotter.view_history_changes)

        plotter.set_xlim(1.0, 2.0)
        plotter.set_ylim(-3.0, 4.0)
        plotter.set_zlim(5.0, 6.0)
        plotter.set_clim(0.2, 0.8)

        self.assertEqual(axes.limits, AxesLimits((1.0, 2.0), (-3.0, 4.0), (5.0, 6.0), (0.2, 0.8)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "manual")
        self.assertEqual(plotter.view_history_changes, history_after_first_set)

    def test_manual_limit_setters_reject_nan_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        cases = (
            (plotter.set_xlim, (float("nan"), 2.0)),
            (plotter.set_ylim, (-3.0, float("nan"))),
            (plotter.set_zlim, (5.0, float("nan"))),
            (plotter.set_clim, (0.0, float("nan"))),
        )
        for setter, args in cases:
            with self.subTest(setter=setter.__name__):
                with self.assertRaisesRegex(ValueError, "NaN"):
                    setter(*args)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_manual_limit_setters_accept_infinite_endpoints(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0), (0.0, 1.0))
        plotter = FakePlotter(axes)

        plotter.set_xlim(float("-inf"), float("inf"))
        plotter.set_ylim(-3.0, float("inf"))
        plotter.set_zlim(float("-inf"), 5.0)
        plotter.set_clim(0.0, float("inf"))

        self.assertEqual(axes.limits, AxesLimits((float("-inf"), float("inf")), (-3.0, float("inf")), (float("-inf"), 5.0), (0.0, float("inf"))))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "manual")

    def test_manual_limit_setters_require_strictly_increasing_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        cases = (
            (plotter.set_xlim, (2.0, 1.0)),
            (plotter.set_ylim, (3.0, 3.0)),
            (plotter.set_zlim, (6.0, 5.0)),
            (plotter.set_clim, (0.8, 0.8)),
        )
        for setter, args in cases:
            with self.subTest(setter=setter.__name__):
                with self.assertRaisesRegex(ValueError, "increasing"):
                    setter(*args)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_xlim_ylim_zlim_accept_limits_auto_and_manual(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xlim([1.0, 2.0])
        plotter.ylim((-3.0, 4.0))
        plotter.zlim([5.0, 6.0])

        self.assertEqual(axes.limits, AxesLimits((1.0, 2.0), (-3.0, 4.0), (5.0, 6.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")

        plotter.xlim(" auto ")
        plotter.ylim("auto")
        plotter.zlim("auto")
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(axes.autoscale_calls, [False, False, False])

        plotter.xlim("manual")
        plotter.ylim("manual")
        plotter.zlim("manual")
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")

    def test_repeating_limit_manual_commands_are_noop(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0), (0.0, 1.0))
        plotter = FakePlotter(axes)

        plotter.xlim("manual")
        plotter.ylim("manual")
        plotter.zlim("manual")
        plotter.clim("manual")
        history_after_first_manual = list(plotter.view_history_changes)

        plotter.xlim("manual")
        plotter.ylim("manual")
        plotter.zlim("manual")
        plotter.clim("manual")

        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "manual")
        self.assertEqual(plotter.view_history_changes, history_after_first_manual)

    def test_xlim_ylim_zlim_without_arguments_return_current_limits(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((1.0, 2.0), (-3.0, 4.0), (5.0, 6.0))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xlim(), (1.0, 2.0))
        self.assertEqual(plotter.ylim(), (-3.0, 4.0))
        self.assertEqual(plotter.zlim(), (5.0, 6.0))

    def test_limit_mode_queries_return_modes_without_pushing_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xlim("mode"), "auto")
        self.assertEqual(plotter.ylim(" mode "), "auto")
        self.assertEqual(plotter.zlim("MODE"), "auto")
        self.assertEqual(plotter.clim("mode"), "auto")
        self.assertEqual(plotter.view_stack, [])

        plotter.xlim([1.0, 2.0])
        plotter.ylim([-3.0, 4.0])
        plotter.zlim([5.0, 6.0])
        plotter.clim([0.2, 0.8])
        history_after_manual_limits = list(plotter.view_history_changes)

        self.assertEqual(plotter.xlim("mode"), "manual")
        self.assertEqual(plotter.ylim("mode"), "manual")
        self.assertEqual(plotter.zlim("mode"), "manual")
        self.assertEqual(plotter.clim("mode"), "manual")
        self.assertEqual(plotter.view_history_changes, history_after_manual_limits)

    def test_zlim_is_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zlim())
        self.assertIsNone(plotter.zlim("mode"))
        plotter.zlim([1.0, 2.0])
        plotter.zlim("auto")

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.zlim_mode, "auto")

    def test_xticks_yticks_zticks_query_set_modes_and_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xticks(), (0.0, 5.0, 10.0))
        self.assertEqual(plotter.yticks(), (-1.0, 0.0, 1.0))
        self.assertEqual(plotter.zticks(), (0.0, 2.5, 5.0))
        self.assertEqual(plotter.xticks("mode"), "auto")

        plotter.xticks([1.0, 2.0, 3.0])
        plotter.yticks([])
        plotter.zticks((2.0, 4.0))

        self.assertEqual(axes.xtick, (1.0, 2.0, 3.0))
        self.assertEqual(axes.ytick, ())
        self.assertEqual(axes.ztick, (2.0, 4.0))
        self.assertEqual(plotter.xtick_mode, "manual")
        self.assertEqual(plotter.ytick_mode, "manual")
        self.assertEqual(plotter.ztick_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 3)

        plotter.xticks("auto")
        plotter.yticks("manual")

        self.assertEqual(plotter.xtick_mode, "auto")
        self.assertEqual(plotter.xtick, (1.0, 2.0, 3.0))
        self.assertEqual(plotter.ytick_mode, "manual")

    def test_repeating_ticks_commands_are_noop_and_bad_values_error(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xticks([1.0, 2.0, 3.0])
        history_after_xticks = list(plotter.view_history_changes)
        plotter.xticks([1.0, 2.0, 3.0])
        self.assertEqual(plotter.view_history_changes, history_after_xticks)

        for command_name, command in (("xticks", plotter.xticks), ("yticks", plotter.yticks), ("zticks", plotter.zticks)):
            with self.subTest(command=command_name, value="bad"):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")
            for value in ([1.0, float("nan")], [1.0, float("inf")], [2.0, 1.0], [1.0, 1.0]):
                with self.subTest(command=command_name, value=value):
                    with self.assertRaisesRegex(ValueError, command_name):
                        command(value)

    def test_zticks_is_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zticks())
        self.assertIsNone(plotter.zticks("mode"))
        self.assertIsNone(plotter.zticks([1.0, 2.0]))
        self.assertEqual(plotter.ztick_mode, "auto")

    def test_xticklabels_yticklabels_zticklabels_query_set_modes_and_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xticklabels(), ("0", "5", "10"))
        self.assertEqual(plotter.yticklabels(), ("-1", "0", "1"))
        self.assertEqual(plotter.zticklabels(), ("0", "2.5", "5"))
        self.assertEqual(plotter.xticklabels("mode"), "auto")

        plotter.xticklabels(["a", "b"])
        plotter.yticklabels([])
        plotter.zticklabels(("low", "high"))

        self.assertEqual(axes.xticklabel, ("a", "b", ""))
        self.assertEqual(axes.yticklabel, ("", "", ""))
        self.assertEqual(axes.zticklabel, ("low", "high", ""))
        self.assertEqual(plotter.xticklabel_mode, "manual")
        self.assertEqual(plotter.yticklabel_mode, "manual")
        self.assertEqual(plotter.zticklabel_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 3)

        plotter.xticklabels("auto")
        plotter.yticklabels("manual")

        self.assertEqual(plotter.xticklabel_mode, "auto")
        self.assertEqual(plotter.xticklabel, ("a", "b", ""))
        self.assertEqual(plotter.yticklabel_mode, "manual")

    def test_repeating_ticklabels_commands_are_noop_and_bad_values_error(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xticklabels(["a", "b"])
        history_after_labels = list(plotter.view_history_changes)
        plotter.xticklabels(["a", "b"])
        self.assertEqual(plotter.view_history_changes, history_after_labels)

        for command_name, command in (("xticklabels", plotter.xticklabels), ("yticklabels", plotter.yticklabels), ("zticklabels", plotter.zticklabels)):
            with self.subTest(command=command_name):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")

    def test_layer_and_tickdir_match_matlab_axes_properties(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.layer(), "bottom")
        self.assertEqual(plotter.tickdir(), "in")
        self.assertEqual(plotter.tickdir("mode"), "auto")
        self.assertEqual(plotter.tickdirmode(), "auto")

        self.assertIsNone(plotter.layer(" top "))
        self.assertEqual(plotter.layer(), "top")
        self.assertEqual(axes.axis_layer, "top")

        self.assertIsNone(plotter.tickdir(" out "))
        self.assertEqual(plotter.tickdir(), "out")
        self.assertEqual(plotter.tickdirmode(), "manual")
        self.assertEqual(axes.tick_direction, "out")

        self.assertIsNone(plotter.tickdir("both"))
        self.assertEqual(axes.tick_direction, "both")
        self.assertIsNone(plotter.tickdir("none"))
        self.assertEqual(axes.tick_direction, "none")

    def test_layer_and_tickdir_reject_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported layer value"):
            plotter.layer("middle")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "Unsupported tickdir value"):
            plotter.tickdir("sideways")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "Unsupported tickdirmode value"):
            plotter.tickdirmode("bad")  # type: ignore[arg-type]

    def test_tickdirmode_controls_mode_without_changing_direction(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.tickdir("out")
        self.assertEqual(plotter.tickdirmode(), "manual")
        self.assertEqual(axes.tick_direction, "out")

        plotter.tickdirmode("auto")
        self.assertEqual(plotter.tickdirmode(), "auto")
        self.assertEqual(plotter.tickdir(), "out")
        self.assertEqual(axes.tick_direction, "out")

        plotter.tickdirmode("manual")
        self.assertEqual(plotter.tickdirmode(), "manual")

    def test_ticklength_matches_matlab_axes_property(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.ticklength(), (0.01, 0.025))
        self.assertIsNone(plotter.ticklength([0.02, 0.05]))
        self.assertEqual(plotter.ticklength(), (0.02, 0.05))
        self.assertEqual(axes.tick_length, (0.02, 0.05))

        self.assertIsNone(plotter.ticklength([-0.01, 0.02]))
        self.assertEqual(axes.tick_length, (-0.01, 0.02))

    def test_ticklength_rejects_bad_shape_and_nonfinite_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "ticklength vector must contain 2 values"):
            plotter.ticklength([0.01])
        with self.assertRaisesRegex(ValueError, "ticklength vector must contain 2 values"):
            plotter.ticklength([0.01, 0.02, 0.03])
        with self.assertRaisesRegex(ValueError, "ticklength values must be finite"):
            plotter.ticklength([float("nan"), 0.02])
        with self.assertRaisesRegex(ValueError, "ticklength values must be finite"):
            plotter.ticklength([float("inf"), 0.02])

    def test_ticklength_is_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.ticklength([0.02, 0.05])

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.ticklength(), (0.01, 0.025))
        self.assertEqual(axes2.tick_length, (0.01, 0.025))

        plotter.set_active_axes(axes1)
        self.assertEqual(plotter.ticklength(), (0.02, 0.05))
        self.assertEqual(axes1.tick_length, (0.02, 0.05))

    def test_layer_and_tickdir_are_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.layer("top")
        plotter.tickdir("out")

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.layer(), "bottom")
        self.assertEqual(plotter.tickdir(), "in")
        self.assertEqual(axes2.axis_layer, "bottom")
        self.assertEqual(axes2.tick_direction, "in")

        plotter.set_active_axes(axes1)
        self.assertEqual(plotter.layer(), "top")
        self.assertEqual(plotter.tickdir(), "out")
        self.assertEqual(axes1.axis_layer, "top")
        self.assertEqual(axes1.tick_direction, "out")

    def test_axis_location_helpers_match_matlab_axes_properties(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xaxislocation(), "bottom")
        self.assertEqual(plotter.yaxislocation(), "left")

        self.assertIsNone(plotter.xaxislocation(" top "))
        self.assertIsNone(plotter.yaxislocation(" right "))
        self.assertEqual(plotter.xaxislocation(), "top")
        self.assertEqual(plotter.yaxislocation(), "right")
        self.assertEqual(axes.x_axis_location, "top")
        self.assertEqual(axes.y_axis_location, "right")

        self.assertIsNone(plotter.xaxislocation("origin"))
        self.assertIsNone(plotter.yaxislocation("origin"))
        self.assertEqual(axes.x_axis_location, "origin")
        self.assertEqual(axes.y_axis_location, "origin")

    def test_axis_location_helpers_reject_bad_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "Unsupported xaxislocation value"):
            plotter.xaxislocation("left")  # type: ignore[arg-type]
        with self.assertRaisesRegex(ValueError, "Unsupported yaxislocation value"):
            plotter.yaxislocation("top")  # type: ignore[arg-type]

    def test_axis_location_is_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.xaxislocation("top")
        plotter.yaxislocation("right")

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.xaxislocation(), "bottom")
        self.assertEqual(plotter.yaxislocation(), "left")
        self.assertEqual(axes2.x_axis_location, "bottom")
        self.assertEqual(axes2.y_axis_location, "left")

        plotter.set_active_axes(axes1)
        self.assertEqual(plotter.xaxislocation(), "top")
        self.assertEqual(plotter.yaxislocation(), "right")
        self.assertEqual(axes1.x_axis_location, "top")
        self.assertEqual(axes1.y_axis_location, "right")

    def test_zticklabels_is_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zticklabels())
        self.assertIsNone(plotter.zticklabels("mode"))
        self.assertIsNone(plotter.zticklabels(["a"]))
        self.assertEqual(plotter.zticklabel_mode, "auto")

    def test_ticklabel_rotation_helpers_query_set_modes_and_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xticklabelrotation(), 0.0)
        self.assertEqual(plotter.yticklabelrotation(), 0.0)
        self.assertEqual(plotter.zticklabelrotation(), 0.0)
        self.assertEqual(plotter.xticklabelrotation("mode"), "auto")

        plotter.xticklabelrotation(45)
        plotter.yticklabelrotation(-30)
        plotter.zticklabelrotation(370)

        self.assertEqual(plotter.xticklabelrotation(), 45.0)
        self.assertEqual(plotter.yticklabelrotation(), -30.0)
        self.assertEqual(plotter.zticklabelrotation(), 370.0)
        self.assertEqual(plotter.xticklabel_rotation_mode, "manual")
        self.assertEqual(axes.xticklabel_rotation, 45.0)
        self.assertEqual(axes.yticklabel_rotation, -30.0)
        self.assertEqual(axes.zticklabel_rotation, 370.0)

        plotter.xticklabelrotation("auto")
        self.assertEqual(plotter.xticklabelrotation(), 0.0)
        self.assertEqual(plotter.xticklabelrotation("mode"), "auto")
        self.assertEqual(axes.xticklabel_rotation, 0.0)

        plotter.yticklabelrotation("manual")
        self.assertEqual(plotter.yticklabelrotation("mode"), "manual")

    def test_ticklabel_rotation_rejects_nonfinite_and_bad_modes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for command_name, command in (
            ("xticklabelrotation", plotter.xticklabelrotation),
            ("yticklabelrotation", plotter.yticklabelrotation),
            ("zticklabelrotation", plotter.zticklabelrotation),
        ):
            with self.subTest(command=command_name, value="bad"):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")
            for value in (float("nan"), float("inf")):
                with self.subTest(command=command_name, value=value):
                    with self.assertRaisesRegex(ValueError, command_name):
                        command(value)

    def test_zticklabelrotation_is_noop_for_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.zticklabelrotation())
        self.assertIsNone(plotter.zticklabelrotation("mode"))
        self.assertIsNone(plotter.zticklabelrotation(45))





    def test_colordef_sets_white_dark_scheme(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        result = plotter.colordef("white")
        self.assertEqual(result, "white")
        self.assertEqual(plotter._color_scheme, "white")
        self.assertEqual(plotter.colordef_changes[-1], (axes, "white"))

        result = plotter.colordef("dark")
        self.assertEqual(result, "dark")
        self.assertEqual(plotter._color_scheme, "dark")

    def test_colordef_rejects_invalid_scheme(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "white.*dark"):
            plotter.colordef("rainbow")

    def test_yyaxis_sets_left_right_side(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        result = plotter.yyaxis("left")
        self.assertEqual(result, "left")
        self.assertEqual(plotter.yyaxis_side, "left")
        self.assertEqual(plotter.yyaxis_changes[-1], (axes, "left"))

        result = plotter.yyaxis("right")
        self.assertEqual(result, "right")
        self.assertEqual(plotter.yyaxis_side, "right")
        self.assertEqual(plotter.yyaxis_changes[-1], (axes, "right"))

    def test_yyaxis_rejects_invalid_side(self):
        plotter = FakePlotter(FakeAxes())

        with self.assertRaisesRegex(ValueError, "left.*right"):
            plotter.yyaxis("middle")

    def test_yyaxis_is_scoped_per_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.yyaxis("right", axes=axes2)
        self.assertEqual(plotter.yyaxis_side, "left")  # active axes unchanged

    def test_sgtitle_query_set_and_record_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.sgtitle(), ())
        plotter.sgtitle("Group Title")
        self.assertEqual(plotter.sgtitle_text, ("Group Title",))
        self.assertEqual(axes.sgtitle_text, ("Group Title",))

    def test_sgtitle_supports_multiline(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.sgtitle(["Main", "Details"])
        self.assertEqual(plotter.sgtitle_text, ("Main", "Details"))

    def test_subtitle_query_set_and_record_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.subtitle(), ())
        plotter.subtitle("Secondary")
        self.assertEqual(plotter.subtitle_text, ("Secondary",))
        self.assertEqual(axes.subtitle_text, ("Secondary",))

    def test_subtitle_supports_multiline(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.subtitle(["Line 1", "Line 2"])
        self.assertEqual(plotter.subtitle_text, ("Line 1", "Line 2"))

    def test_title_and_axis_labels_query_set_and_record_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.title(), ())
        self.assertEqual(plotter.xlabel(), ())
        self.assertEqual(plotter.ylabel(), ())
        self.assertEqual(plotter.zlabel(), ())

        plotter.title("Main")
        plotter.xlabel(["X", "Axis"])
        plotter.ylabel(123)
        plotter.zlabel("")

        self.assertEqual(plotter.axes_title, ("Main",))
        self.assertEqual(plotter.xlabel_text, ("X", "Axis"))
        self.assertEqual(plotter.ylabel_text, ("123",))
        self.assertEqual(plotter.zlabel_text, ("",))
        self.assertEqual(axes.axes_title, ("Main",))
        self.assertEqual(axes.xlabel_text, ("X", "Axis"))
        self.assertEqual(axes.ylabel_text, ("123",))
        self.assertEqual(axes.zlabel_text, ("",))
        self.assertEqual(len(plotter.view_stack), 4)

    def test_repeating_text_commands_are_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.title("Main")
        history_after_title = list(plotter.view_history_changes)
        plotter.title("Main")

        self.assertEqual(plotter.view_history_changes, history_after_title)

    def test_limit_commands_reject_invalid_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "2 values"):
            plotter.xlim([1.0, 2.0, 3.0])
        with self.assertRaisesRegex(ValueError, "bad"):
            plotter.ylim("bad")
        with self.assertRaisesRegex(ValueError, "bad"):
            plotter.zlim("bad")

        for command, value in ((plotter.xlim, [float("nan"), 2.0]), (plotter.ylim, [-1.0, float("nan")]), (plotter.zlim, [0.0, float("nan")])):
            with self.subTest(command=command.__name__):
                with self.assertRaisesRegex(ValueError, "NaN"):
                    command(value)

        for command, value in ((plotter.xlim, [2.0, 1.0]), (plotter.ylim, [3.0, 3.0]), (plotter.zlim, [6.0, 5.0])):
            with self.subTest(command=command.__name__, value=value):
                with self.assertRaisesRegex(ValueError, "increasing"):
                    command(value)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_clim_accepts_limits_auto_and_manual(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), None, (0.0, 1.0))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.clim(), (0.0, 1.0))

        plotter.clim([0.2, 0.8])
        self.assertEqual(axes.limits.clim, (0.2, 0.8))
        self.assertEqual(plotter.clim_mode, "manual")

        plotter.clim(" auto ")
        self.assertEqual(plotter.clim_mode, "auto")
        self.assertEqual(axes.autoscale_clim_calls, 1)

        plotter.clim("manual")
        self.assertEqual(plotter.clim_mode, "manual")

    def test_caxis_matches_clim_color_limit_behavior(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), None, (0.0, 1.0))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.caxis(), (0.0, 1.0))

        plotter.caxis([0.25, 0.75])
        self.assertEqual(axes.limits.clim, (0.25, 0.75))
        self.assertEqual(plotter.caxis("mode"), "manual")

        plotter.caxis("auto")
        self.assertEqual(plotter.clim_mode, "auto")
        self.assertEqual(axes.autoscale_clim_calls, 1)

        plotter.caxis("manual")
        self.assertEqual(plotter.clim_mode, "manual")

    def test_clim_rejects_invalid_values(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "2 values"):
            plotter.clim([0.0, 1.0, 2.0])

        with self.assertRaisesRegex(ValueError, "bad"):
            plotter.clim("bad")

        with self.assertRaisesRegex(ValueError, "NaN"):
            plotter.clim([0.0, float("nan")])

        with self.assertRaisesRegex(ValueError, "increasing"):
            plotter.clim([1.0, 1.0])

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_axis_limit_vector_rejects_invalid_lengths_and_3d_limits_on_2d_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "4, 6, or 8"):
            plotter.axis([1.0, 2.0, 3.0])

        with self.assertRaisesRegex(ValueError, "3D axes"):
            plotter.axis([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])

        with self.assertRaisesRegex(ValueError, "3D axes"):
            plotter.axis([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])

    def test_axis_limit_vector_rejects_nan_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for values in (
            [1.0, float("nan"), -2.0, 3.0],
            [1.0, 4.0, -2.0, 3.0, float("nan"), 20.0],
            [1.0, 4.0, -2.0, 3.0, 10.0, 20.0, 0.2, float("nan")],
        ):
            with self.subTest(values=values):
                with self.assertRaisesRegex(ValueError, "NaN"):
                    plotter.axis(values)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_axis_limit_vector_accepts_infinite_endpoints(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.axis([float("-inf"), float("inf"), -2.0, float("inf"), float("-inf"), 20.0, 0.2, float("inf")])

        self.assertEqual(
            axes.limits,
            AxesLimits((float("-inf"), float("inf")), (-2.0, float("inf")), (float("-inf"), 20.0), (0.2, float("inf"))),
        )
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(plotter.clim_mode, "manual")

    def test_axis_limit_vector_requires_strictly_increasing_ranges(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for values in (
            [4.0, 1.0, -2.0, 3.0],
            [1.0, 4.0, 3.0, 3.0],
            [1.0, 4.0, -2.0, 3.0, 20.0, 10.0],
            [1.0, 4.0, -2.0, 3.0, 10.0, 20.0, 0.8, 0.2],
        ):
            with self.subTest(values=values):
                with self.assertRaisesRegex(ValueError, "increasing"):
                    plotter.axis(values)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_after_plot_respects_manual_modes_and_autoscales_any_auto_axis(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.axis("manual")

        plotter.after_plot()
        self.assertEqual(axes.autoscale_calls, [])

        plotter.zlim_mode = "auto"
        plotter.after_plot()
        self.assertEqual(axes.autoscale_calls, [False])

    def test_axis_equal_normal_fill_and_square_update_aspects_and_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("equal")
        self.assertEqual(plotter.axis_aspect, "equal")
        self.assertEqual(axes.aspect, "equal")

        plotter.axis("normal")
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")
        self.assertEqual(axes.aspect, "auto")
        self.assertEqual(axes.box_aspect, "auto")

        plotter.axis("equal")
        plotter.axis("square")
        self.assertEqual(plotter.box_aspect, "square")
        self.assertEqual(axes.box_aspect, "square")

        plotter.axis("vis3d")
        self.assertEqual(plotter.box_aspect, "vis3d")
        self.assertEqual(axes.box_aspect, "vis3d")

        plotter.axis("fill")
        self.assertEqual(plotter.axis_aspect, "auto")
        self.assertEqual(plotter.box_aspect, "auto")
        self.assertEqual(axes.aspect, "auto")
        self.assertEqual(axes.box_aspect, "auto")
        self.assertEqual(len(plotter.view_stack), 6)

    def test_repeating_axis_aspect_commands_are_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("equal")
        history_after_equal = list(plotter.view_history_changes)
        plotter.axis("equal")
        self.assertEqual(plotter.view_history_changes, history_after_equal)

        plotter.axis("square")
        history_after_square = list(plotter.view_history_changes)
        plotter.axis("square")
        self.assertEqual(plotter.view_history_changes, history_after_square)

        plotter.axis("vis3d")
        history_after_vis3d = list(plotter.view_history_changes)
        plotter.axis("vis3d")
        self.assertEqual(plotter.view_history_changes, history_after_vis3d)

        plotter.axis("normal")
        history_after_normal = list(plotter.view_history_changes)
        plotter.axis("fill")
        self.assertEqual(plotter.view_history_changes, history_after_normal)

    def test_axis_image_applies_tight_limits_and_equal_aspect(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.xlim_mode = "manual"
        plotter.ylim_mode = "manual"
        plotter.axis_aspect = "auto"

        plotter.axis("image")

        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(axes.autoscale_calls, [True])
        self.assertEqual(plotter.axis_aspect, "equal")
        self.assertEqual(axes.aspect, "equal")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_daspect_and_pbaspect_query_set_modes_and_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.daspect(), (1.0, 1.0, 1.0))
        self.assertEqual(plotter.daspect("mode"), "auto")
        self.assertEqual(plotter.pbaspect(), (1.0, 1.0, 1.0))
        self.assertEqual(plotter.pbaspect("mode"), "auto")

        plotter.daspect([1.0, 2.0, 3.0])
        plotter.pbaspect((3.0, 2.0, 1.0))

        self.assertEqual(plotter.daspect(), (1.0, 2.0, 3.0))
        self.assertEqual(plotter.daspect("mode"), "manual")
        self.assertEqual(axes.data_aspect_ratio, (1.0, 2.0, 3.0))
        self.assertEqual(plotter.pbaspect(), (3.0, 2.0, 1.0))
        self.assertEqual(plotter.pbaspect("mode"), "manual")
        self.assertEqual(axes.plot_box_aspect_ratio, (3.0, 2.0, 1.0))
        self.assertEqual(len(plotter.view_stack), 2)

        plotter.daspect("auto")
        plotter.pbaspect("auto")

        self.assertEqual(plotter.daspect("mode"), "auto")
        self.assertEqual(plotter.daspect(), (1.0, 2.0, 3.0))
        self.assertEqual(plotter.pbaspect("mode"), "auto")
        self.assertEqual(plotter.pbaspect(), (3.0, 2.0, 1.0))

    def test_repeating_daspect_and_pbaspect_commands_are_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.daspect([1.0, 2.0, 3.0])
        history_after_daspect = list(plotter.view_history_changes)
        plotter.daspect([1.0, 2.0, 3.0])
        self.assertEqual(plotter.view_history_changes, history_after_daspect)

        plotter.pbaspect([3.0, 2.0, 1.0])
        history_after_pbaspect = list(plotter.view_history_changes)
        plotter.pbaspect([3.0, 2.0, 1.0])
        self.assertEqual(plotter.view_history_changes, history_after_pbaspect)

        plotter.daspect("auto")
        history_after_auto = list(plotter.view_history_changes)
        plotter.daspect("auto")
        self.assertEqual(plotter.view_history_changes, history_after_auto)

    def test_daspect_and_pbaspect_reject_bad_values(self):
        plotter = FakePlotter(FakeAxes())

        for command_name, command in (("daspect", plotter.daspect), ("pbaspect", plotter.pbaspect)):
            with self.subTest(command=command_name, value="bad"):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")
            for value in (
                [1.0, 2.0],
                [1.0, 0.0, 3.0],
                [1.0, -2.0, 3.0],
                [1.0, float("nan"), 3.0],
                [1.0, float("inf"), 3.0],
            ):
                with self.subTest(command=command_name, value=value):
                    with self.assertRaisesRegex(ValueError, command_name):
                        command(value)

    def test_axis_on_and_off_update_visibility_and_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("off")
        self.assertFalse(plotter.axis_visible)
        self.assertFalse(axes.axis_visible)

        plotter.axis("on")
        self.assertTrue(plotter.axis_visible)
        self.assertTrue(axes.axis_visible)
        self.assertEqual(len(plotter.view_stack), 2)

    def test_grid_minor_toggles_minor_grid_and_off_clears_both(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.grid("minor"))
        self.assertFalse(axes.grid_visible)
        self.assertTrue(axes.minor_grid_visible)

        self.assertFalse(plotter.grid("minor"))
        self.assertFalse(axes.minor_grid_visible)

        plotter.grid("on")
        plotter.grid("minor")
        self.assertTrue(axes.grid_visible)
        self.assertTrue(axes.minor_grid_visible)

        self.assertFalse(plotter.grid("off"))
        self.assertFalse(axes.grid_visible)
        self.assertFalse(axes.minor_grid_visible)

    def test_repeating_axis_visibility_commands_are_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("off")
        history_after_off = list(plotter.view_history_changes)
        plotter.axis("off")
        self.assertEqual(plotter.view_history_changes, history_after_off)

        plotter.axis("on")
        history_after_on = list(plotter.view_history_changes)
        plotter.axis("on")
        self.assertEqual(plotter.view_history_changes, history_after_on)

    def test_axis_ij_and_xy_update_y_direction_and_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("ij")
        self.assertEqual(plotter.y_direction, "reverse")
        self.assertEqual(axes.y_direction, "reverse")

        plotter.axis("xy")
        self.assertEqual(plotter.y_direction, "normal")
        self.assertEqual(axes.y_direction, "normal")
        self.assertEqual(len(plotter.view_stack), 2)

    def test_xdir_ydir_zdir_query_set_and_record_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xdir(), "normal")
        self.assertEqual(plotter.ydir(), "normal")
        self.assertEqual(plotter.zdir(), "normal")

        plotter.xdir(" reverse ")
        plotter.ydir("reverse")
        plotter.zdir("reverse")

        self.assertEqual(plotter.xdir(), "reverse")
        self.assertEqual(plotter.ydir(), "reverse")
        self.assertEqual(plotter.zdir(), "reverse")
        self.assertEqual(axes.x_direction, "reverse")
        self.assertEqual(axes.y_direction, "reverse")
        self.assertEqual(axes.z_direction, "reverse")
        self.assertEqual(len(plotter.view_stack), 3)

        plotter.axis("xy")

        self.assertEqual(plotter.xdir(), "reverse")
        self.assertEqual(plotter.ydir(), "normal")
        self.assertEqual(plotter.zdir(), "reverse")

    def test_repeating_axis_direction_commands_are_noop_and_bad_values_error(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.xdir("reverse")
        history_after_xdir = list(plotter.view_history_changes)
        plotter.xdir("reverse")
        self.assertEqual(plotter.view_history_changes, history_after_xdir)

        for command_name, command in (("xdir", plotter.xdir), ("ydir", plotter.ydir), ("zdir", plotter.zdir)):
            with self.subTest(command=command_name):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")

    def test_xscale_yscale_zscale_query_set_and_record_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.xscale(), "linear")
        self.assertEqual(plotter.yscale(), "linear")
        self.assertEqual(plotter.zscale(), "linear")

        plotter.xscale(" log ")
        plotter.yscale("log")
        plotter.zscale("log")

        self.assertEqual(plotter.xscale(), "log")
        self.assertEqual(plotter.yscale(), "log")
        self.assertEqual(plotter.zscale(), "log")
        self.assertEqual(axes.x_scale, "log")
        self.assertEqual(axes.y_scale, "log")
        self.assertEqual(axes.z_scale, "log")
        self.assertEqual(len(plotter.view_stack), 3)

    def test_repeating_axis_scale_commands_are_noop_and_bad_values_error(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.xscale("log")
        history_after_xscale = list(plotter.view_history_changes)
        plotter.xscale("log")
        self.assertEqual(plotter.view_history_changes, history_after_xscale)

        for command_name, command in (("xscale", plotter.xscale), ("yscale", plotter.yscale), ("zscale", plotter.zscale)):
            with self.subTest(command=command_name):
                with self.assertRaisesRegex(ValueError, command_name):
                    command("bad")

    def test_repeating_axis_direction_commands_are_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("ij")
        history_after_ij = list(plotter.view_history_changes)
        plotter.axis("ij")
        self.assertEqual(plotter.view_history_changes, history_after_ij)

        plotter.axis("xy")
        history_after_xy = list(plotter.view_history_changes)
        plotter.axis("xy")
        self.assertEqual(plotter.view_history_changes, history_after_xy)

    def test_pan_drag_moves_limits_and_records_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((-1.0, 9.0), (-1.5, 0.5)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_pan_drag_uses_press_transform_for_stable_screen_delta(self):
        axes = FakeAxes()
        axes.transData = FakeDataTransform(FakeScreenToDataTransform())
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, x=20.0, y=50.0, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=30.0, y=75.0, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        first_limits = axes.limits
        plotter.on_mouse_move(PointerEvent(axes=axes, x=30.0, y=75.0, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))

        self.assertEqual(first_limits, AxesLimits((-1.0, 9.0), (-1.5, 0.5)))
        self.assertEqual(axes.limits, first_limits)

    def test_left_double_click_homes_and_does_not_start_tool_drag(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_xlim(1.0, 2.0)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, button=MouseButton.LEFT, dblclick=True))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertIsNone(plotter._drag)
        self.assertEqual(plotter.action_events, [])

    def test_non_left_double_click_does_not_home(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_xlim(1.0, 2.0)

        plotter.on_mouse_press(PointerEvent(axes=axes, button=MouseButton.RIGHT, dblclick=True))

        self.assertEqual(axes.limits, AxesLimits((1.0, 2.0), (-1.0, 1.0)))

    def test_pan_drag_on_log_axes_moves_limits_by_ratio(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((1.0, 100.0), (1.0, 1000.0))
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=10.0, ydata=10.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=100.0, ydata=100.0, button=MouseButton.LEFT))

        self.assertEqual(axes.limits.xlim, (0.1, 10.0))
        self.assertEqual(axes.limits.ylim, (0.1, 100.0))

    def test_pan_drag_on_log_axes_falls_back_to_linear_for_nonpositive_points(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((-1.0, 100.0), (1.0, 1000.0))
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=10.0, ydata=10.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=100.0, ydata=100.0, button=MouseButton.LEFT))

        self.assertEqual(axes.limits.xlim, (-91.0, 10.0))
        self.assertEqual(axes.limits.ylim, (0.1, 100.0))

    def test_pan_motion_can_constrain_drag_to_one_axis(self):
        horizontal_axes = FakeAxes()
        horizontal = FakePlotter(horizontal_axes)
        horizontal.pan_motion = "horizontal"
        horizontal.set_mode(InteractionMode.PAN)

        horizontal.on_mouse_press(PointerEvent(axes=horizontal_axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        horizontal.on_mouse_move(PointerEvent(axes=horizontal_axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        horizontal.on_mouse_release(PointerEvent(axes=horizontal_axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(horizontal_axes.limits, AxesLimits((-1.0, 9.0), (-1.0, 1.0)))
        self.assertEqual(horizontal.xlim_mode, "manual")
        self.assertEqual(horizontal.ylim_mode, "auto")

        vertical_axes = FakeAxes()
        vertical = FakePlotter(vertical_axes)
        vertical.pan_motion = " vertical "
        vertical.set_mode(InteractionMode.PAN)

        vertical.on_mouse_press(PointerEvent(axes=vertical_axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        vertical.on_mouse_move(PointerEvent(axes=vertical_axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        vertical.on_mouse_release(PointerEvent(axes=vertical_axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(vertical_axes.limits, AxesLimits((0.0, 10.0), (-1.5, 0.5)))
        self.assertEqual(vertical.xlim_mode, "auto")
        self.assertEqual(vertical.ylim_mode, "manual")

    def test_pan_drag_on_3d_axes_defaults_to_camera_dolly(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(axes.camera.position, (0.0, 1.5, 3.0))
        self.assertEqual(axes.camera.target, (3.0, 4.5, 6.0))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_pan_drag_on_3d_axes_can_use_legacy_limit_mode(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.pan_3d_mode = "limits"
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((-1.0, 9.0), (-1.5, 0.5), (0.0, 5.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.camera_position_mode, "auto")

    def test_button_down_filter_blocks_exploration_tools(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.block_tool_presses = True

        for mode in (InteractionMode.PAN, InteractionMode.ZOOM, InteractionMode.ROTATE3D):
            with self.subTest(mode=mode):
                plotter.set_mode(mode)
                plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=10.0, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
                plotter.on_mouse_move(PointerEvent(axes=axes, x=100.0, y=40.0, xdata=4.0, ydata=0.5, button=MouseButton.LEFT))
                plotter.on_mouse_release(PointerEvent(axes=axes, x=100.0, y=40.0, xdata=4.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.zoom_box_events, [])
        self.assertEqual(plotter.action_events, [])
        self.assertEqual(len(plotter.filtered_events), 3)

    def test_action_callbacks_wrap_pan_zoom_and_rotate_actions(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.set_mode("pan")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=3.0, ydata=0.5, button="left"))

        plotter.set_mode("zoom")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, button="left"))

        plotter.set_mode("rotate3d")
        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=100.0, y=40.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=100.0, y=40.0, xdata=1.0, ydata=2.0, button="left"))

        self.assertEqual(
            plotter.action_events,
            [
                ("pre", InteractionMode.PAN, axes),
                ("post", InteractionMode.PAN, axes),
                ("pre", InteractionMode.ZOOM, axes),
                ("post", InteractionMode.ZOOM, axes),
                ("pre", InteractionMode.ROTATE3D, axes),
                ("post", InteractionMode.ROTATE3D, axes),
            ],
        )

    def test_action_post_callback_runs_when_mode_switch_cancels_drag(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("pan")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button="left"))
        plotter.set_mode("zoom")

        self.assertEqual(
            plotter.action_events,
            [
                ("pre", InteractionMode.PAN, axes),
                ("post", InteractionMode.PAN, axes),
            ],
        )

    def test_pan_and_zoom_tool_properties_default_like_matlab_and_reject_bad_values(self):
        plotter = FakePlotter(FakeAxes())

        self.assertEqual(plotter.pan_motion, "both")
        self.assertEqual(plotter.zoom_motion, "both")
        self.assertEqual(plotter.zoom_3d_mode, "camera")
        self.assertEqual(plotter.zoom_direction, "in")
        self.assertEqual(plotter.zoom_right_click_action, "postcontextmenu")
        self.assertEqual(plotter.pan_3d_mode, "camera")
        self.assertEqual(plotter.rotate_motion, "both")

        with self.assertRaisesRegex(ValueError, "pan motion"):
            plotter.pan_motion = "diagonal"
        with self.assertRaisesRegex(ValueError, "3D pan mode"):
            plotter.pan_3d_mode = "bad"
        with self.assertRaisesRegex(ValueError, "zoom motion"):
            plotter.zoom_motion = "diagonal"
        with self.assertRaisesRegex(ValueError, "3D zoom mode"):
            plotter.zoom_3d_mode = "bad"
        with self.assertRaisesRegex(ValueError, "zoom direction"):
            plotter.zoom_direction = "toggle"
        with self.assertRaisesRegex(ValueError, "right-click action"):
            plotter.zoom_right_click_action = "zoomout"
        with self.assertRaisesRegex(ValueError, "rotate style"):
            plotter.rotate_style = "turntable"
        with self.assertRaisesRegex(ValueError, "rotate motion"):
            plotter.rotate_motion = "diagonal"

    def test_pan_click_without_motion_does_not_record_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)
        self.assertEqual(plotter.view_history_changes, [])

    def test_pan_ignores_nonfinite_press_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=float("nan"), ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=5.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=5.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_pan_ignores_nonfinite_move_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=float("inf"), ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=float("inf"), ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_shift_pan_drag_constrains_to_dominant_horizontal_axis(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(
            PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT, modifiers=frozenset({"shift"}))
        )
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=5.0, ydata=0.5, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=5.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((-3.0, 7.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 1)

    def test_shift_pan_drag_constrains_to_dominant_vertical_axis(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(
            PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button=MouseButton.LEFT, modifiers=frozenset({"shift"}))
        )
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=2.5, ydata=0.8, button=MouseButton.LEFT))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.5, ydata=0.8, button=MouseButton.LEFT))

        self.assertEqual(axes.limits.xlim, (0.0, 10.0))
        self.assertAlmostEqual(axes.limits.ylim[0], -1.8)
        self.assertAlmostEqual(axes.limits.ylim[1], 0.2)
        self.assertEqual(len(plotter.view_stack), 1)

    def test_shift_pan_prefers_screen_direction_over_data_direction(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(
            PointerEvent(axes=axes, x=10.0, y=10.0, xdata=2.0, ydata=0.0, button=MouseButton.LEFT, modifiers=frozenset({"shift"}))
        )
        plotter.on_mouse_move(PointerEvent(axes=axes, x=110.0, y=20.0, xdata=2.5, ydata=0.8, button=MouseButton.LEFT))

        self.assertEqual(axes.limits, AxesLimits((-0.5, 9.5), (-1.0, 1.0)))

    def test_shift_pan_uses_screen_vertical_direction_when_dominant(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.PAN)

        plotter.on_mouse_press(
            PointerEvent(axes=axes, x=10.0, y=10.0, xdata=2.0, ydata=0.0, button=MouseButton.LEFT, modifiers=frozenset({"shift"}))
        )
        plotter.on_mouse_move(PointerEvent(axes=axes, x=20.0, y=110.0, xdata=5.0, ydata=0.5, button=MouseButton.LEFT))

        self.assertEqual(axes.limits.xlim, (0.0, 10.0))
        self.assertEqual(axes.limits.ylim, (-1.5, 0.5))

    def test_switching_mode_after_pan_motion_records_history(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("pan")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=2.0, ydata=0.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=5.0, ydata=0.5, button="left"))
        plotter.set_mode("zoom")

        self.assertEqual(axes.limits, AxesLimits((-3.0, 7.0), (-1.5, 0.5)))
        self.assertEqual(plotter.mode, InteractionMode.ZOOM)
        self.assertEqual(len(plotter.view_stack), 1)
        self.assertEqual(plotter.view_stack[-1].limits, AxesLimits((-3.0, 7.0), (-1.5, 0.5)))

    def test_box_zoom_normalizes_limits(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_box_zoom(axes, (8.0, 0.8), (2.0, -0.4))

        self.assertEqual(axes.limits, AxesLimits((2.0, 8.0), (-0.4, 0.8)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")

    def test_box_zoom_does_not_mark_unchanged_z_or_color_limits_manual(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0), (0.0, 1.0))
        plotter = FakePlotter(axes)

        plotter.on_box_zoom(axes, (8.0, 0.8), (2.0, -0.4))

        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(plotter.clim_mode, "auto")

    def test_box_zoom_on_log_axes_accepts_positive_box(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((1.0, 100.0), (1.0, 1000.0))
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")

        plotter.on_box_zoom(axes, (2.0, 5.0), (20.0, 50.0))

        self.assertEqual(axes.limits, AxesLimits((2.0, 20.0), (5.0, 50.0)))

    def test_box_zoom_on_log_axes_rejects_nonpositive_box_values(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((1.0, 100.0), (1.0, 1000.0))
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")

        plotter.on_box_zoom(axes, (-2.0, 5.0), (20.0, 50.0))
        plotter.on_box_zoom(axes, (2.0, 0.0), (20.0, 50.0))

        self.assertEqual(axes.limits, AxesLimits((1.0, 100.0), (1.0, 1000.0)))
        self.assertEqual(len(plotter.view_stack), 2)  # xscale and yscale only

    def test_box_zoom_log_validation_respects_zoom_motion(self):
        horizontal_axes = FakeAxes()
        horizontal_axes.limits = AxesLimits((1.0, 100.0), (1.0, 1000.0))
        horizontal = FakePlotter(horizontal_axes)
        horizontal.xscale("log")
        horizontal.yscale("log")
        horizontal.zoom_motion = "horizontal"

        horizontal.on_box_zoom(horizontal_axes, (2.0, -5.0), (20.0, -50.0))
        self.assertEqual(horizontal_axes.limits, AxesLimits((2.0, 20.0), (1.0, 1000.0)))

        vertical_axes = FakeAxes()
        vertical_axes.limits = AxesLimits((1.0, 100.0), (1.0, 1000.0))
        vertical = FakePlotter(vertical_axes)
        vertical.xscale("log")
        vertical.yscale("log")
        vertical.zoom_motion = "vertical"

        vertical.on_box_zoom(vertical_axes, (-2.0, 5.0), (-20.0, 50.0))
        self.assertEqual(vertical_axes.limits, AxesLimits((1.0, 100.0), (5.0, 50.0)))

    def test_box_zoom_on_log_axes_uses_log_span_for_degenerate_check(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((1.0, 1.0e300), (1.0, 1000.0))
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.zoom_motion = "horizontal"

        plotter.on_box_zoom(axes, (10.0, -0.5), (10.000001, 0.5))
        self.assertEqual(axes.limits, AxesLimits((1.0, 1.0e300), (1.0, 1000.0)))

        plotter.on_box_zoom(axes, (10.0, -0.5), (100.0, 0.5))
        self.assertEqual(axes.limits, AxesLimits((10.0, 100.0), (1.0, 1000.0)))

    def test_box_zoom_ignores_degenerate_box(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_box_zoom(axes, (2.0, 0.5), (2.0, -0.5))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_box_zoom_ignores_nonfinite_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_box_zoom(axes, (float("nan"), 0.5), (2.0, -0.5))
        plotter.on_box_zoom(axes, (1.0, 0.5), (2.0, float("inf")))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_set_zlim_updates_3d_axes_and_records_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.set_zlim(-1.0, 7.0)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (-1.0, 7.0)))
        self.assertEqual(plotter.zlim_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_set_zlim_is_noop_for_2d_axes(self):
        axes = FakeAxes(is_3d=False)
        plotter = FakePlotter(axes)

        plotter.set_zlim(-1.0, 7.0)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.zlim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_drag_updates_box_and_applies_limits_on_release(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=8.0, ydata=0.8, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=2.0, ydata=-0.4, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=-0.4, button="left"))

        self.assertEqual(axes.limits, AxesLimits((2.0, 8.0), (-0.4, 0.8)))
        self.assertEqual(
            plotter.zoom_box_events,
            [
                ("begin", axes, 8.0, 0.8),
                ("update", axes, 8.0, 0.8, 2.0, -0.4),
                ("end",),
            ],
        )
        self.assertEqual(len(plotter.view_stack), 1)

    def test_zoom_left_click_without_drag_does_not_zoom(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(plotter.zoom_box_events, [("begin", axes, 5.0, 0.0), ("end",)])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_direction_out_does_not_make_left_click_zoom_out(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.zoom_direction = "out"
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_left_click_on_3d_axes_without_drag_does_not_zoom_camera(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))

        self.assertAlmostEqual(axes.camera.view_angle, 10.0)
        self.assertEqual(plotter.camera_view_angle_mode, "auto")
        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0)))

    def test_zoom_on_3d_axes_can_use_legacy_limit_mode(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)
        plotter.zoom_3d_mode = "limits"

        plotter.on_point_zoom(axes, 5.0, 0.0, 0.5)

        self.assertEqual(axes.camera.view_angle, 10.0)
        self.assertEqual(axes.limits, AxesLimits((2.5, 7.5), (-0.5, 0.5), (0.0, 5.0)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")

    def test_zoom_motion_constrains_point_zoom_and_box_zoom_to_one_axis(self):
        horizontal_axes = FakeAxes()
        horizontal = FakePlotter(horizontal_axes)
        horizontal.zoom_motion = "horizontal"
        horizontal.on_point_zoom(horizontal_axes, 5.0, 0.0, 0.5)

        self.assertEqual(horizontal_axes.limits, AxesLimits((2.5, 7.5), (-1.0, 1.0)))
        self.assertEqual(horizontal.xlim_mode, "manual")
        self.assertEqual(horizontal.ylim_mode, "auto")

        vertical_axes = FakeAxes()
        vertical = FakePlotter(vertical_axes)
        vertical.zoom_motion = "vertical"
        vertical.on_box_zoom(vertical_axes, (8.0, 0.8), (2.0, -0.4))

        self.assertEqual(vertical_axes.limits, AxesLimits((0.0, 10.0), (-0.4, 0.8)))
        self.assertEqual(vertical.xlim_mode, "auto")
        self.assertEqual(vertical.ylim_mode, "manual")

    def test_zoom_small_pointer_motion_does_not_zoom(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=100.0, y=200.0, xdata=5.0, ydata=0.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=102.0, y=201.0, xdata=5.2, ydata=0.1, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_right_click_defaults_to_context_menu_noop_like_matlab(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, button="right"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.zoom_box_events, [])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_right_click_inversezoom_action_zooms_out(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.zoom_right_click_action = " InverseZoom "
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=5.0, ydata=0.0, button="right"))

        self.assertEqual(axes.limits, AxesLimits((-5.0, 15.0), (-2.0, 2.0)))
        self.assertEqual(plotter.zoom_box_events, [])
        self.assertEqual(len(plotter.view_stack), 1)

    def test_point_zoom_scale_one_is_noop(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_point_zoom(axes, 5.0, 0.0, 1.0)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.xlim_mode, "auto")
        self.assertEqual(plotter.ylim_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_point_zoom_rejects_nonpositive_scale(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        for scale in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(scale=scale):
                with self.assertRaisesRegex(ValueError, "scale"):
                    plotter.on_point_zoom(axes, 5.0, 0.0, scale)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_point_zoom_ignores_nonfinite_center(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_point_zoom(axes, float("nan"), 0.0, 0.5)
        plotter.on_point_zoom(axes, 5.0, float("inf"), 0.5)

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_limits_scale_one_preserves_limits(self):
        axes = FakeAxes(is_3d=True)
        limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), (0.0, 5.0), (0.0, 1.0))
        plotter = FakePlotter(axes)

        self.assertEqual(plotter._zoom_limits(limits, 5.0, 0.0, 1.0), limits)

    def test_zoom_limits_on_log_axes_scale_in_log_space(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")

        limits = plotter._zoom_limits(AxesLimits((1.0, 100.0), (1.0, 1000.0)), 10.0, 10.0, 0.5)

        self.assertAlmostEqual(limits.xlim[0], 10 ** 0.5)
        self.assertAlmostEqual(limits.xlim[1], 10 ** 1.5)
        self.assertAlmostEqual(limits.ylim[0], 10 ** 0.5)
        self.assertAlmostEqual(limits.ylim[1], 10 ** 2.0)

    def test_zoom_limits_on_log_axes_falls_back_to_linear_for_nonpositive_center_or_limits(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.xscale("log")
        plotter.yscale("log")

        limits = plotter._zoom_limits(AxesLimits((-1.0, 100.0), (1.0, 1000.0)), 10.0, -10.0, 0.5)

        self.assertEqual(limits.xlim, (4.5, 55.0))
        self.assertEqual(limits.ylim, (-4.5, 495.0))

    def test_zoom_limits_rejects_nonpositive_scale(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        for scale in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(scale=scale):
                with self.assertRaisesRegex(ValueError, "zoom scale"):
                    plotter._zoom_limits(axes.limits, 5.0, 0.0, scale)

    def test_zoom_limits_rejects_nonfinite_center(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "zoom center"):
            plotter._zoom_limits(axes.limits, float("nan"), 0.0, 0.5)
        with self.assertRaisesRegex(ValueError, "zoom center"):
            plotter._zoom_limits(axes.limits, 5.0, float("inf"), 0.5)

    def test_zoom_drag_cancelled_when_release_is_outside_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=None, xdata=None, ydata=None, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.zoom_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_drag_with_nonfinite_release_only_clears_rubber_band(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=float("nan"), ydata=0.2, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(plotter.zoom_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_drag_degenerate_box_only_clears_rubber_band(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=10.0, xdata=2.0, ydata=0.8, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=10.0, y=30.0, xdata=2.0, ydata=-0.8, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=10.0, y=30.0, xdata=2.0, ydata=-0.8, button="left"))

        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(
            plotter.zoom_box_events,
            [
                ("begin", axes, 2.0, 0.8),
                ("update", axes, 2.0, 0.8, 2.0, -0.8),
                ("end",),
            ],
        )
        self.assertEqual(len(plotter.view_stack), 0)

    def test_switching_mode_clears_active_zoom_box(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.set_mode("pan")
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="left"))

        self.assertEqual(plotter.zoom_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_zoom_mode_does_not_start_on_middle_button(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("zoom")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="middle"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="middle"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=2.0, ydata=0.2, button="middle"))

        self.assertEqual(plotter.zoom_box_events, [])
        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))

    def test_data_cursor_and_selection_hooks(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.set_mode("data_cursor")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=2.0, button="left"))
        self.assertEqual(plotter.data_tips, [(axes, 1.0, 2.0, frozenset())])

        plotter.on_mouse_press(
            PointerEvent(axes=axes, xdata=1.5, ydata=2.5, button="left", modifiers=frozenset({"control"}))
        )
        self.assertEqual(
            plotter.data_tips,
            [(axes, 1.0, 2.0, frozenset()), (axes, 1.5, 2.5, frozenset({"control"}))],
        )

        plotter.set_mode("select")
        plotter.on_mouse_press(
            PointerEvent(axes=axes, xdata=3.0, ydata=4.0, button="left", modifiers=frozenset({"shift"}))
        )
        self.assertEqual(plotter.selections, [(axes, 3.0, 4.0, frozenset({"shift"}))])

    def test_data_cursor_and_selection_ignore_nonfinite_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.set_mode("data_cursor")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=float("nan"), ydata=2.0, button="left"))
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=float("inf"), button="left"))

        plotter.set_mode("select")
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=float("nan"), ydata=4.0, button="left"))
        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=3.0, ydata=float("inf"), button="left"))

        self.assertEqual(plotter.data_tips, [])
        self.assertEqual(plotter.selections, [])

    def test_coordinate_readout_ignores_nonfinite_motion_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=float("nan"), ydata=2.0))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=1.0, ydata=float("inf")))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=1.0, ydata=2.0))

        self.assertEqual(plotter.readouts, [(axes, 1.0, 2.0)])

    def test_brush_drag_updates_box_and_calls_hook(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left"))
        plotter.on_mouse_release(
            PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left", modifiers=frozenset({"shift"}))
        )

        self.assertEqual(
            plotter.brush_box_events,
            [
                ("begin", axes, 1.0, 0.1),
                ("update", axes, 1.0, 0.1, 4.0, 0.8),
                ("end",),
            ],
        )
        self.assertEqual(plotter.brushes, [(axes, (1.0, 0.1), (4.0, 0.8), frozenset({"shift"}))])

    def test_brush_ignores_nonfinite_press_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=float("nan"), ydata=0.1, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left"))

        self.assertEqual(plotter.brush_box_events, [])
        self.assertEqual(plotter.brushes, [])

    def test_brush_ignores_nonfinite_move_coordinates(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=4.0, ydata=float("inf"), button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left"))

        self.assertEqual(plotter.brush_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(plotter.brushes, [(axes, (1.0, 0.1), (4.0, 0.8), frozenset())])

    def test_brush_nonfinite_release_only_clears_rubber_band(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=4.0, ydata=float("nan"), button="left"))

        self.assertEqual(plotter.brush_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(plotter.brushes, [])

    def test_brush_drag_cancelled_when_release_is_outside_axes(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=None, xdata=None, ydata=None, button="left"))

        self.assertEqual(plotter.brush_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(plotter.brushes, [])

    def test_switching_mode_clears_active_brush_box(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)
        plotter.set_mode("brush")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=1.0, ydata=0.1, button="left"))
        plotter.set_mode("zoom")
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=4.0, ydata=0.8, button="left"))

        self.assertEqual(plotter.brush_box_events, [("begin", axes, 1.0, 0.1), ("end",)])
        self.assertEqual(plotter.brushes, [])

    def test_linked_axes_sync_requested_axis_only(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes2.limits = AxesLimits((100.0, 200.0), (10.0, 20.0))
        plotter = FakePlotter(axes1)
        plotter.link_axes([axes1, axes2], axis="x")

        plotter.set_xlim(2.0, 4.0)

        self.assertEqual(axes1.limits.xlim, (2.0, 4.0))
        self.assertEqual(axes2.limits.xlim, (2.0, 4.0))
        self.assertEqual(axes2.limits.ylim, (10.0, 20.0))

        plotter.set_active_axes(axes2)
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "auto")

    def test_linked_axes_marks_both_limit_modes_manual_for_xy_link(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes2.limits = AxesLimits((100.0, 200.0), (10.0, 20.0))
        plotter = FakePlotter(axes1)
        plotter.link_axes([axes1, axes2], axis="xy")

        plotter.on_box_zoom(axes1, (2.0, -0.5), (4.0, 0.5))

        plotter.set_active_axes(axes2)
        self.assertEqual(axes2.limits, AxesLimits((2.0, 4.0), (-0.5, 0.5)))
        self.assertEqual(plotter.xlim_mode, "manual")
        self.assertEqual(plotter.ylim_mode, "manual")

    def test_linkaxes_defaults_to_xy_union_then_syncs_limits(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes1.limits = AxesLimits((1.0, 2.0), (3.0, 4.0))
        axes2.limits = AxesLimits((10.0, 20.0), (30.0, 40.0))
        plotter = FakePlotter(axes1)

        plotter.linkaxes([axes1, axes2])

        self.assertEqual(axes1.limits, AxesLimits((1.0, 20.0), (3.0, 40.0)))
        self.assertEqual(axes2.limits, AxesLimits((1.0, 20.0), (3.0, 40.0)))

        plotter.set_xlim(5.0, 6.0)
        plotter.set_ylim(7.0, 8.0)

        self.assertEqual(axes2.limits, AxesLimits((5.0, 6.0), (7.0, 8.0)))

    def test_linkaxes_y_option_unions_and_syncs_only_y_limits(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes1.limits = AxesLimits((1.0, 2.0), (3.0, 4.0))
        axes2.limits = AxesLimits((10.0, 20.0), (30.0, 40.0))
        plotter = FakePlotter(axes1)

        plotter.linkaxes([axes1, axes2], "y")

        self.assertEqual(axes1.limits, AxesLimits((1.0, 2.0), (3.0, 40.0)))
        self.assertEqual(axes2.limits, AxesLimits((10.0, 20.0), (3.0, 40.0)))

        plotter.set_xlim(5.0, 6.0)
        plotter.set_ylim(7.0, 8.0)

        self.assertEqual(axes2.limits.xlim, (10.0, 20.0))
        self.assertEqual(axes2.limits.ylim, (7.0, 8.0))

    def test_linkaxes_off_unlinks_matching_axes_set(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.linkaxes([axes1, axes2], "x")
        plotter.linkaxes([axes1, axes2], "off")
        plotter.set_xlim(5.0, 6.0)

        self.assertEqual(axes1.limits.xlim, (5.0, 6.0))
        self.assertEqual(axes2.limits.xlim, (0.0, 10.0))
        self.assertEqual(plotter._linked, [])

    def test_linkaxes_allows_single_axes_and_rejects_bad_option(self):
        axes = FakeAxes("a1")
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.linkaxes(axes, "x"))
        self.assertEqual(plotter._linked, [])

        with self.assertRaisesRegex(ValueError, "linkaxes"):
            plotter.linkaxes([axes], "bad")

    def test_link_axes_is_idempotent_for_same_axes_and_axis(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.link_axes([axes1, axes2], axis="x")
        plotter.link_axes([axes2, axes1], axis="x")

        self.assertEqual(len(plotter._linked), 1)

    def test_unlink_axes_removes_requested_axis_links(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)
        plotter.link_axes([axes1, axes2], axis="x")
        plotter.link_axes([axes1, axes2], axis="y")

        plotter.unlink_axes("x")

        self.assertEqual(plotter._linked, [({axes1, axes2}, "y")])

    def test_view_history_home_back_forward(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertFalse(plotter.can_home())
        self.assertFalse(plotter.can_back())
        self.assertFalse(plotter.can_forward())

        plotter.push_current_view()
        self.assertTrue(plotter.can_home())
        self.assertFalse(plotter.can_back())
        self.assertFalse(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes, [(0, 1, False, False)])

        plotter.push_current_view()
        self.assertEqual(plotter.view_history_changes, [(0, 1, False, False)])

        plotter.set_xlim(1.0, 2.0)
        plotter.set_ylim(-0.5, 0.5)
        self.assertTrue(plotter.can_back())
        self.assertFalse(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (2, 3, True, False))

        self.assertTrue(plotter.back())
        self.assertEqual(axes.limits, AxesLimits((1.0, 2.0), (-1.0, 1.0)))
        self.assertTrue(plotter.can_back())
        self.assertTrue(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (1, 3, True, True))

        self.assertTrue(plotter.back())
        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertFalse(plotter.can_back())
        self.assertTrue(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (0, 3, False, True))

        self.assertTrue(plotter.forward())
        self.assertEqual(axes.limits, AxesLimits((1.0, 2.0), (-1.0, 1.0)))
        self.assertTrue(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (1, 3, True, True))

        self.assertTrue(plotter.home())
        self.assertEqual(axes.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertFalse(plotter.can_back())
        self.assertTrue(plotter.can_forward())
        self.assertEqual(plotter.view_history_changes[-1], (0, 3, False, True))

    def test_view_history_is_scoped_to_active_axes(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes2.limits = AxesLimits((100.0, 200.0), (10.0, 20.0))
        plotter = FakePlotter(axes1)

        plotter.push_current_view(axes1)
        plotter.set_xlim(1.0, 2.0)
        plotter.set_active_axes(axes2)
        plotter.push_current_view(axes2)
        plotter.set_xlim(110.0, 120.0)

        self.assertEqual(axes1.limits, AxesLimits((1.0, 2.0), (-1.0, 1.0)))
        self.assertEqual(axes2.limits, AxesLimits((110.0, 120.0), (10.0, 20.0)))

        self.assertTrue(plotter.back())
        self.assertEqual(axes1.limits, AxesLimits((1.0, 2.0), (-1.0, 1.0)))
        self.assertEqual(axes2.limits, AxesLimits((100.0, 200.0), (10.0, 20.0)))

        plotter.set_active_axes(axes1)
        self.assertTrue(plotter.back())
        self.assertEqual(axes1.limits, AxesLimits((0.0, 10.0), (-1.0, 1.0)))
        self.assertEqual(axes2.limits, AxesLimits((100.0, 200.0), (10.0, 20.0)))

    def test_replace_plot_clears_only_target_axes_history(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        axes2.limits = AxesLimits((100.0, 200.0), (10.0, 20.0))
        plotter = FakePlotter(axes1)
        plotter.push_current_view(axes1)
        plotter.set_xlim(1.0, 2.0)
        plotter.set_active_axes(axes2)
        plotter.push_current_view(axes2)
        plotter.set_xlim(110.0, 120.0)

        plotter.prepare_for_plot(axes2)

        self.assertEqual(axes2.clear_calls, [True])
        self.assertEqual(len(plotter.view_stack), 2)
        self.assertTrue(all(state.axes is axes1 for state in plotter.view_stack))
        self.assertFalse(plotter.can_home())
        self.assertFalse(plotter.can_back())

        plotter.set_active_axes(axes1)
        self.assertTrue(plotter.can_home())
        self.assertTrue(plotter.can_back())

    def test_current_view_state_returns_snapshot_without_pushing_history(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((1.0, 2.0), (-3.0, 4.0), (5.0, 6.0), (0.2, 0.8))
        axes.camera = Camera3DState(azim=45.0, elev=10.0)
        plotter = FakePlotter(axes)
        plotter.xlim_mode = "manual"
        plotter.axis_aspect = "equal"
        plotter.grid("on")
        plotter.view_stack = []
        plotter.view_history_changes = []
        axes.box_visible = False
        axes.legend_visible = True

        state = plotter.current_view_state()

        self.assertIsNotNone(state)
        self.assertEqual(state.limits, axes.limits)
        self.assertEqual(state.xlim_mode, "manual")
        self.assertEqual(state.aspect, "equal")
        self.assertTrue(state.grid_visible)
        self.assertFalse(state.box_visible)
        self.assertTrue(state.legend_visible)
        self.assertEqual(state.camera_mode, "auto")
        self.assertEqual(state.camera, Camera3DState(azim=45.0, elev=10.0, roll=0.0))
        self.assertEqual(plotter.view_stack, [])

    def test_current_view_state_normalizes_equivalent_camera_azimuth(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=304.5, elev=10.0)
        plotter = FakePlotter(axes)

        state = plotter.current_view_state()

        self.assertEqual(state.camera, Camera3DState(azim=-55.5, elev=10.0, roll=0.0))

    def test_current_view_state_ignores_nonfinite_backend_camera(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=float("nan"), elev=10.0)
        plotter = FakePlotter(axes)

        self.assertIsNone(plotter.current_view_state())

        plotter.push_current_view()

        self.assertEqual(plotter.view_stack, [])
        self.assertEqual(plotter.view_history_changes, [])

    def test_current_view_state_uses_target_axes_ui_state(self):
        axes1 = FakeAxes("a1")
        axes2 = FakeAxes("a2")
        plotter = FakePlotter(axes1)

        plotter.set_xlim(1.0, 2.0)
        plotter.axis("off")
        plotter.set_active_axes(axes2)
        plotter.set_ylim(10.0, 20.0)

        state1 = plotter.current_view_state(axes1)
        state2 = plotter.current_view_state(axes2)

        self.assertIsNotNone(state1)
        self.assertIsNotNone(state2)
        self.assertEqual(state1.xlim_mode, "manual")
        self.assertEqual(state1.ylim_mode, "auto")
        self.assertFalse(state1.axis_visible)
        self.assertEqual(state2.xlim_mode, "auto")
        self.assertEqual(state2.ylim_mode, "manual")
        self.assertTrue(state2.axis_visible)

    def test_current_view_state_returns_none_without_axes(self):
        plotter = FakePlotter(None)

        self.assertIsNone(plotter.current_view_state())

    def test_view_history_restores_axis_aspect(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("equal")
        plotter.axis("square")
        plotter.axis("normal")

        self.assertTrue(plotter.back())
        self.assertEqual(plotter.box_aspect, "square")
        self.assertEqual(axes.box_aspect, "square")

        self.assertTrue(plotter.back())
        self.assertEqual(plotter.axis_aspect, "equal")
        self.assertEqual(axes.aspect, "equal")

    def test_view_history_restores_explicit_aspect_ratios(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.daspect([1.0, 2.0, 3.0])
        plotter.pbaspect([4.0, 5.0, 6.0])
        plotter.daspect([2.0, 3.0, 4.0])

        self.assertEqual(axes.data_aspect_ratio, (2.0, 3.0, 4.0))
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.data_aspect_ratio, (1.0, 2.0, 3.0))
        self.assertEqual(axes.data_aspect_ratio, (1.0, 2.0, 3.0))
        self.assertEqual(plotter.plot_box_aspect_ratio, (4.0, 5.0, 6.0))
        self.assertEqual(axes.plot_box_aspect_ratio, (4.0, 5.0, 6.0))
        self.assertEqual(plotter.data_aspect_ratio_mode, "manual")
        self.assertEqual(plotter.plot_box_aspect_ratio_mode, "manual")

    def test_view_history_does_not_apply_auto_aspect_ratios_as_manual(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.push_current_view()
        axes.data_aspect_ratio = (9.0, 9.0, 9.0)
        axes.plot_box_aspect_ratio = (8.0, 8.0, 8.0)

        self.assertTrue(plotter.home())

        self.assertEqual(plotter.data_aspect_ratio_mode, "auto")
        self.assertEqual(plotter.plot_box_aspect_ratio_mode, "auto")
        self.assertEqual(axes.data_aspect_ratio, (9.0, 9.0, 9.0))
        self.assertEqual(axes.plot_box_aspect_ratio, (8.0, 8.0, 8.0))

    def test_view_history_restores_axis_visibility(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("off")
        plotter.axis("on")

        self.assertTrue(plotter.back())
        self.assertFalse(plotter.axis_visible)
        self.assertFalse(axes.axis_visible)

    def test_view_history_restores_y_direction(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.axis("ij")
        plotter.axis("xy")

        self.assertTrue(plotter.back())
        self.assertEqual(plotter.y_direction, "reverse")
        self.assertEqual(axes.y_direction, "reverse")

    def test_view_history_restores_x_y_z_directions(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xdir("reverse")
        plotter.ydir("reverse")
        plotter.zdir("reverse")
        plotter.xdir("normal")

        self.assertEqual(axes.x_direction, "normal")
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.x_direction, "reverse")
        self.assertEqual(plotter.y_direction, "reverse")
        self.assertEqual(plotter.z_direction, "reverse")
        self.assertEqual(axes.x_direction, "reverse")
        self.assertEqual(axes.y_direction, "reverse")
        self.assertEqual(axes.z_direction, "reverse")

    def test_view_history_restores_x_y_z_scales(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xscale("log")
        plotter.yscale("log")
        plotter.zscale("log")
        plotter.xscale("linear")

        self.assertEqual(axes.x_scale, "linear")
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.x_scale, "log")
        self.assertEqual(plotter.y_scale, "log")
        self.assertEqual(plotter.z_scale, "log")
        self.assertEqual(axes.x_scale, "log")
        self.assertEqual(axes.y_scale, "log")
        self.assertEqual(axes.z_scale, "log")

    def test_view_history_restores_layer_and_tick_direction(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.layer("top")
        plotter.tickdir("out")
        plotter.layer("bottom")

        self.assertEqual(axes.axis_layer, "bottom")
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.axis_layer, "top")
        self.assertEqual(plotter.tick_direction, "out")
        self.assertEqual(plotter.tick_direction_mode, "manual")
        self.assertEqual(axes.axis_layer, "top")
        self.assertEqual(axes.tick_direction, "out")

    def test_view_history_restores_tick_length(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.ticklength([0.02, 0.05])
        plotter.tickdir("out")
        plotter.ticklength([0.03, 0.06])

        self.assertEqual(axes.tick_length, (0.03, 0.06))
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.tick_length, (0.02, 0.05))
        self.assertEqual(plotter.tick_direction, "out")
        self.assertEqual(axes.tick_length, (0.02, 0.05))
        self.assertEqual(axes.tick_direction, "out")

    def test_view_history_restores_axis_locations(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.xaxislocation("top")
        plotter.yaxislocation("right")
        plotter.xaxislocation("origin")

        self.assertEqual(axes.x_axis_location, "origin")
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.x_axis_location, "top")
        self.assertEqual(plotter.y_axis_location, "right")
        self.assertEqual(axes.x_axis_location, "top")
        self.assertEqual(axes.y_axis_location, "right")

    def test_view_history_restores_per_axis_grid_state(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.grid("on")
        plotter.xgrid("off")
        plotter.zminorgrid("on")
        plotter.ygrid("off")

        self.assertFalse(axes.y_grid_visible)
        self.assertTrue(plotter.back())
        self.assertFalse(axes.x_grid_visible)
        self.assertTrue(axes.y_grid_visible)
        self.assertTrue(axes.z_grid_visible)
        self.assertFalse(axes.x_minor_grid_visible)
        self.assertFalse(axes.y_minor_grid_visible)
        self.assertTrue(axes.z_minor_grid_visible)

    def test_view_history_restores_per_axis_minor_tick_state(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xminortick("on")
        plotter.zminortick("on")
        plotter.yminortick("on")
        plotter.xminortick("off")

        self.assertFalse(axes.x_minor_tick_visible)
        self.assertTrue(plotter.back())
        self.assertTrue(axes.x_minor_tick_visible)
        self.assertTrue(axes.y_minor_tick_visible)
        self.assertTrue(axes.z_minor_tick_visible)

    def test_view_history_restores_manual_ticks(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xticks([1.0, 2.0, 3.0])
        plotter.yticks([4.0, 5.0, 6.0])
        plotter.xticks([7.0, 8.0, 9.0])

        self.assertEqual(axes.xtick, (7.0, 8.0, 9.0))
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.xtick, (1.0, 2.0, 3.0))
        self.assertEqual(plotter.ytick, (4.0, 5.0, 6.0))
        self.assertEqual(plotter.xtick_mode, "manual")
        self.assertEqual(plotter.ytick_mode, "manual")
        self.assertEqual(axes.xtick, (1.0, 2.0, 3.0))
        self.assertEqual(axes.ytick, (4.0, 5.0, 6.0))

    def test_view_history_restores_manual_ticklabels(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xticklabels(["a", "b"])
        plotter.yticklabels(["c", "d"])
        plotter.xticklabels(["e", "f"])

        self.assertEqual(axes.xticklabel, ("e", "f", ""))
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.xticklabel, ("a", "b", ""))
        self.assertEqual(plotter.yticklabel, ("c", "d", ""))
        self.assertEqual(plotter.xticklabel_mode, "manual")
        self.assertEqual(plotter.yticklabel_mode, "manual")
        self.assertEqual(axes.xticklabel, ("a", "b", ""))
        self.assertEqual(axes.yticklabel, ("c", "d", ""))

    def test_view_history_restores_ticklabel_rotations(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.xticklabelrotation(45)
        plotter.yticklabelrotation(-30)
        plotter.zticklabelrotation(370)
        plotter.xticklabelrotation(90)

        self.assertEqual(axes.xticklabel_rotation, 90.0)
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.xticklabel_rotation, 45.0)
        self.assertEqual(plotter.yticklabel_rotation, -30.0)
        self.assertEqual(plotter.zticklabel_rotation, 370.0)
        self.assertEqual(plotter.xticklabel_rotation_mode, "manual")
        self.assertEqual(axes.xticklabel_rotation, 45.0)
        self.assertEqual(axes.yticklabel_rotation, -30.0)
        self.assertEqual(axes.zticklabel_rotation, 370.0)

    def test_view_history_restores_title_and_axis_labels(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.title("Main")
        plotter.xlabel("X")
        plotter.title("Next")

        self.assertEqual(axes.axes_title, ("Next",))
        self.assertTrue(plotter.back())
        self.assertEqual(plotter.axes_title, ("Main",))
        self.assertEqual(plotter.xlabel_text, ("X",))
        self.assertEqual(axes.axes_title, ("Main",))
        self.assertEqual(axes.xlabel_text, ("X",))

    def test_view_history_restores_grid_box_and_legend_visibility(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        plotter.grid("on")
        plotter.grid("minor")
        plotter.box("off")
        plotter.legend("on")

        self.assertTrue(plotter.back())
        self.assertTrue(axes.grid_visible)
        self.assertTrue(axes.minor_grid_visible)
        self.assertFalse(axes.box_visible)
        self.assertFalse(axes.legend_visible)

        self.assertTrue(plotter.forward())
        self.assertTrue(axes.grid_visible)
        self.assertTrue(axes.minor_grid_visible)
        self.assertFalse(axes.box_visible)
        self.assertTrue(axes.legend_visible)

    def test_rotate3d_uses_low_sensitivity_and_records_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=0.0, ydata=0.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=100.0, ydata=20.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, xdata=100.0, ydata=20.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-55.5, elev=27.6, roll=0.0))
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "manual")
        self.assertEqual(plotter.view_stack[-1].camera_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_rotate3d_click_without_motion_does_not_record_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)
        self.assertEqual(plotter.view_history_changes, [])

    def test_rotate3d_ignores_motion_below_drag_threshold(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=12.0, y=21.0, xdata=20.0, ydata=30.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=12.0, y=21.0, xdata=20.0, ydata=30.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_rotate3d_only_left_button_starts_camera_drag(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        for button in ("right", "middle"):
            with self.subTest(button=button):
                plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button=button))
                plotter.on_mouse_move(PointerEvent(axes=axes, x=120.0, y=80.0, xdata=20.0, ydata=30.0, button=button))
                plotter.on_mouse_release(PointerEvent(axes=axes, x=120.0, y=80.0, xdata=20.0, ydata=30.0, button=button))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_rotate3d_ignores_nonfinite_press_coordinates(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=float("nan"), y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=120.0, y=80.0, xdata=20.0, ydata=30.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=120.0, y=80.0, xdata=20.0, ydata=30.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_rotate3d_ignores_nonfinite_move_coordinates(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=float("inf"), y=80.0, xdata=20.0, ydata=30.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=axes, x=float("inf"), y=80.0, xdata=20.0, ydata=30.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_rotate3d_zero_drag_threshold_allows_small_motion(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.rotate_drag_pixel_threshold = 0.0
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=11.0, y=20.0, xdata=20.0, ydata=30.0, button="left"))

        self.assertAlmostEqual(axes.camera.azim, -37.68)
        self.assertEqual(axes.camera.elev, 30.0)
        self.assertEqual(axes.camera.roll, 0.0)
        self.assertEqual(plotter.camera_mode, "manual")

    def test_rotate3d_drag_threshold_rejects_negative_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "drag pixel threshold"):
            plotter.rotate_drag_pixel_threshold = -1.0

        self.assertEqual(plotter.rotate_drag_pixel_threshold, 3.0)

    def test_rotate3d_drag_threshold_rejects_nonfinite_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for value in (float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite"):
                    plotter.rotate_drag_pixel_threshold = value

        self.assertEqual(plotter.rotate_drag_pixel_threshold, 3.0)

    def test_rotate3d_continues_pixel_drag_outside_start_axes(self):
        axes = FakeAxes("start", is_3d=True)
        other_axes = FakeAxes("other", is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=other_axes, x=120.0, y=80.0, xdata=20.0, ydata=30.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=None, x=220.0, y=160.0, xdata=None, ydata=None, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=None, x=220.0, y=160.0, xdata=None, ydata=None, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-75.3, elev=13.2, roll=0.0))
        self.assertEqual(other_axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_rotate3d_ignores_outside_motion_without_pixel_coordinates(self):
        axes = FakeAxes("start", is_3d=True)
        other_axes = FakeAxes("other", is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=10.0, y=20.0, xdata=1.0, ydata=2.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=other_axes, xdata=20.0, ydata=30.0, button="left"))
        plotter.on_mouse_release(PointerEvent(axes=other_axes, xdata=20.0, ydata=30.0, button="left"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(other_axes.camera, Camera3DState(azim=-37.5, elev=30.0))
        self.assertEqual(plotter.camera_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

    def test_switching_mode_after_rotate3d_motion_records_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=0.0, y=0.0, xdata=0.0, ydata=0.0, button="left"))
        plotter.on_mouse_move(PointerEvent(axes=axes, x=100.0, y=20.0, xdata=0.0, ydata=0.0, button="left"))
        plotter.set_mode("pan")

        self.assertEqual(axes.camera, Camera3DState(azim=-55.5, elev=27.6, roll=0.0))
        self.assertEqual(plotter.mode, InteractionMode.PAN)
        self.assertEqual(len(plotter.view_stack), 1)
        self.assertEqual(plotter.view_stack[-1].camera, Camera3DState(azim=-55.5, elev=27.6, roll=0.0))

    def test_switching_mode_after_rotate3d_click_does_not_record_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.set_mode("rotate3d")

        plotter.on_mouse_press(PointerEvent(axes=axes, x=0.0, y=0.0, xdata=0.0, ydata=0.0, button="left"))
        plotter.set_mode("pan")

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(plotter.mode, InteractionMode.PAN)
        self.assertEqual(len(plotter.view_stack), 0)

    def test_rotate3d_sensitivity_can_be_tuned_with_compatibility_scalar(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.rotate_sensitivity = 0.5

        self.assertEqual(plotter.rotate_azimuth_sensitivity, 0.5)
        self.assertEqual(plotter.rotate_elevation_sensitivity, 0.5)

        camera = plotter._rotate_camera(Camera3DState(azim=10.0, elev=20.0), dx=10.0, dy=4.0)

        self.assertEqual(camera, Camera3DState(azim=5.0, elev=18.0, roll=0.0))

    def test_rotate3d_axis_sensitivities_can_be_tuned_independently(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.rotate_azimuth_sensitivity = 0.4
        plotter.rotate_elevation_sensitivity = 0.1

        camera = plotter._rotate_camera(Camera3DState(azim=10.0, elev=20.0), dx=10.0, dy=4.0)

        self.assertEqual(camera, Camera3DState(azim=6.0, elev=19.6, roll=0.0))

    def test_rotate3d_motion_can_constrain_rotation_axis(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        camera = Camera3DState(azim=10.0, elev=20.0)

        plotter.rotate_motion = "horizontal"
        horizontal = plotter._rotate_camera(camera, dx=10.0, dy=4.0)
        self.assertAlmostEqual(horizontal.azim, 8.2)
        self.assertEqual(horizontal.elev, 20.0)

        plotter.rotate_motion = "vertical"
        vertical = plotter._rotate_camera(camera, dx=10.0, dy=4.0)
        self.assertEqual(vertical.azim, 10.0)
        self.assertAlmostEqual(vertical.elev, 19.52)

    def test_rotate3d_sensitivity_rejects_negative_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "non-negative"):
            plotter.rotate_sensitivity = -0.1

        self.assertEqual(plotter.rotate_azimuth_sensitivity, 0.18)
        self.assertEqual(plotter.rotate_elevation_sensitivity, 0.12)

    def test_rotate3d_axis_sensitivities_reject_negative_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "azimuth sensitivity"):
            plotter.rotate_azimuth_sensitivity = -0.1
        with self.assertRaisesRegex(ValueError, "elevation sensitivity"):
            plotter.rotate_elevation_sensitivity = -0.1

        self.assertEqual(plotter.rotate_azimuth_sensitivity, 0.18)
        self.assertEqual(plotter.rotate_elevation_sensitivity, 0.12)

    def test_rotate3d_sensitivity_parameters_reject_nonfinite_values(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for attr in ("rotate_sensitivity", "rotate_azimuth_sensitivity", "rotate_elevation_sensitivity"):
            for value in (float("nan"), float("inf")):
                with self.subTest(attr=attr, value=value):
                    with self.assertRaisesRegex(ValueError, "finite"):
                        setattr(plotter, attr, value)

        self.assertEqual(plotter.rotate_azimuth_sensitivity, 0.18)
        self.assertEqual(plotter.rotate_elevation_sensitivity, 0.12)

    def test_rotate3d_zero_sensitivity_disables_camera_motion(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.rotate_sensitivity = 0.0

        camera = plotter._rotate_camera(Camera3DState(azim=10.0, elev=20.0), dx=100.0, dy=40.0)

        self.assertEqual(camera, Camera3DState(azim=10.0, elev=20.0, roll=0.0))

    def test_rotate3d_rejects_nonfinite_camera_or_delta_inputs(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))

        with self.assertRaisesRegex(ValueError, "camera angles"):
            plotter._rotate_camera(Camera3DState(azim=float("nan"), elev=20.0), dx=1.0, dy=1.0)
        with self.assertRaisesRegex(ValueError, "deltas"):
            plotter._rotate_camera(Camera3DState(azim=10.0, elev=20.0), dx=float("inf"), dy=1.0)
        with self.assertRaisesRegex(ValueError, "deltas"):
            plotter._rotate_camera(Camera3DState(azim=10.0, elev=20.0), dx=1.0, dy=float("nan"))

    def test_rotate3d_normalizes_azimuth_to_signed_range(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))

        self.assertEqual(plotter._rotate_camera(Camera3DState(azim=-170.0, elev=10.0), dx=100.0, dy=0.0).azim, 172.0)
        self.assertEqual(plotter._rotate_camera(Camera3DState(azim=170.0, elev=10.0), dx=-100.0, dy=0.0).azim, -172.0)

    def test_rotate3d_clamps_elevation(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=0.0, elev=85.0)
        plotter = FakePlotter(axes)
        plotter.set_mode(InteractionMode.ROTATE3D)

        plotter.on_mouse_press(PointerEvent(axes=axes, xdata=0.0, ydata=0.0, button=MouseButton.LEFT))
        plotter.on_mouse_move(PointerEvent(axes=axes, xdata=0.0, ydata=-100.0, button=MouseButton.LEFT))

        self.assertEqual(axes.camera.elev, 90.0)

    def test_rotate3d_uses_custom_elevation_limits(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))
        plotter.elevation_limits = (-30.0, 45.0)

        upper = plotter._rotate_camera(Camera3DState(azim=0.0, elev=40.0), dx=0.0, dy=-100.0)
        lower = plotter._rotate_camera(Camera3DState(azim=0.0, elev=-25.0), dx=0.0, dy=100.0)

        self.assertEqual(upper.elev, 45.0)
        self.assertEqual(lower.elev, -30.0)

    def test_rotate3d_elevation_limits_reject_invalid_ranges(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))

        with self.assertRaisesRegex(ValueError, "2 values"):
            plotter.elevation_limits = (-90.0,)
        with self.assertRaisesRegex(ValueError, "ascending"):
            plotter.elevation_limits = (45.0, -45.0)

        self.assertEqual(plotter.elevation_limits, (-90.0, 90.0))

    def test_rotate3d_elevation_limits_reject_nonfinite_values(self):
        plotter = FakePlotter(FakeAxes(is_3d=True))

        for limits in ((float("nan"), 90.0), (-90.0, float("inf"))):
            with self.subTest(limits=limits):
                with self.assertRaisesRegex(ValueError, "finite"):
                    plotter.elevation_limits = limits

        self.assertEqual(plotter.elevation_limits, (-90.0, 90.0))

    def test_camva_controls_3d_camera_view_angle_mode_and_history(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.camva(), 10.0)
        self.assertEqual(plotter.camva("mode"), "auto")

        plotter.camva(12.5)
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0, view_angle=12.5))
        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(plotter.camva(" mode "), "manual")
        self.assertEqual(len(plotter.view_stack), 1)

        plotter.view(45.0, 20.0)
        self.assertEqual(axes.camera, Camera3DState(azim=45.0, elev=20.0, roll=0.0, view_angle=12.5))
        self.assertEqual(plotter.camera_view_angle_mode, "manual")

        plotter.camva("auto")
        self.assertEqual(plotter.camera_view_angle_mode, "auto")
        self.assertEqual(axes.camera.view_angle, 12.5)

    def test_camva_manual_mode_query_and_repeated_commands_are_noop(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)

        plotter.camva("manual")
        history_after_manual = list(plotter.view_history_changes)
        plotter.camva("manual")
        plotter.camva(10.0)

        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(plotter.view_history_changes, history_after_manual)

    def test_camva_rejects_bad_values_and_is_noop_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "bad"):
            plotter.camva("bad")
        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.camva(float("nan"))
        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.camva(float("inf"))

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camva())
        self.assertIsNone(plotter2d.camva("mode"))
        self.assertIsNone(plotter2d.camva(10.0))

    def test_camzoom_scales_camera_view_angle_like_matlab(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0, view_angle=10.0)
        plotter = FakePlotter(axes)

        plotter.camzoom(2.0)

        self.assertAlmostEqual(axes.camera.view_angle, 5.009537444)
        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

        plotter.camzoom(0.5)

        self.assertAlmostEqual(axes.camera.view_angle, 10.0)
        self.assertEqual(len(plotter.view_stack), 2)

    def test_camorbit_updates_view_and_marks_camera_position_and_up_manual(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            view_angle=10.0,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)

        plotter.camorbit(10.0, 5.0)

        self.assertEqual(
            axes.camera,
            Camera3DState(
                azim=-27.5,
                elev=35.0,
                roll=0.0,
                view_angle=10.0,
                position=(1.0, 2.0, 3.0),
                target=(4.0, 5.0, 6.0),
                up_vector=(0.0, 0.0, 1.0),
            ),
        )
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "auto")
        self.assertEqual(plotter.camera_up_vector_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_camorbit_clamps_elevation_rejects_bad_deltas_and_noops_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=170.0, elev=85.0)
        plotter = FakePlotter(axes)

        plotter.camorbit(20.0, 20.0)

        self.assertEqual(axes.camera.azim, -170.0)
        self.assertEqual(axes.camera.elev, 90.0)

        for args in ((float("nan"), 0.0), (0.0, float("inf"))):
            with self.subTest(args=args):
                with self.assertRaisesRegex(ValueError, "camorbit deltas"):
                    plotter.camorbit(*args)

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camorbit(10.0, 5.0))

    def test_camroll_updates_roll_and_marks_camera_up_manual(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            view_angle=10.0,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)

        plotter.camroll(10.0)

        self.assertEqual(
            axes.camera,
            Camera3DState(
                azim=-37.5,
                elev=30.0,
                roll=10.0,
                view_angle=10.0,
                position=(1.0, 2.0, 3.0),
                target=(4.0, 5.0, 6.0),
                up_vector=(0.0, 0.0, 1.0),
            ),
        )
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(plotter.camera_position_mode, "auto")
        self.assertEqual(plotter.camera_target_mode, "auto")
        self.assertEqual(plotter.camera_up_vector_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_camroll_zero_marks_camera_up_manual_once(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(azim=-37.5, elev=30.0)
        plotter = FakePlotter(axes)

        plotter.camroll(0.0)

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 1)

        plotter.camroll(0.0)

        self.assertEqual(len(plotter.view_stack), 1)

    def test_camroll_rejects_bad_angle_and_noops_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for angle in (float("nan"), float("inf")):
            with self.subTest(angle=angle):
                with self.assertRaisesRegex(ValueError, "camroll angle"):
                    plotter.camroll(angle)

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camroll(10.0))

    def test_camproj_queries_and_sets_3d_projection(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.camproj(), "orthographic")

        plotter.camproj(" perspective ")

        self.assertEqual(axes.camera_projection, "perspective")
        self.assertEqual(plotter.camera_projection, "perspective")
        self.assertEqual(len(plotter.view_stack), 1)

        history_after_set = list(plotter.view_history_changes)
        plotter.camproj("perspective")

        self.assertEqual(plotter.view_history_changes, history_after_set)

    def test_camproj_rejects_bad_value_and_noops_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "camproj"):
            plotter.camproj("bad")

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camproj())
        self.assertIsNone(plotter2d.camproj("perspective"))

    def test_view_history_restores_camera_projection(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        plotter.push_current_view()
        plotter.camproj("perspective")

        self.assertEqual(axes.camera_projection, "perspective")
        self.assertTrue(plotter.home())
        self.assertEqual(axes.camera_projection, "orthographic")
        self.assertEqual(plotter.camera_projection, "orthographic")
        self.assertTrue(plotter.forward())
        self.assertEqual(axes.camera_projection, "perspective")
        self.assertEqual(plotter.camera_projection, "perspective")

    def test_camlookat_fits_missing_camera_vectors_from_limits(self):
        axes = FakeAxes(is_3d=True)
        axes.limits = AxesLimits((0.0, 10.0), (-2.0, 2.0), (0.0, 6.0))
        axes.camera = Camera3DState(azim=0.0, elev=0.0)
        plotter = FakePlotter(axes)

        plotter.camlookat()

        self.assertEqual(axes.camera.target, (5.0, 0.0, 3.0))
        self.assertEqual(axes.camera.position, (25.0, 0.0, 3.0))
        self.assertEqual(axes.camera.view_angle, 10.0)
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")
        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_camlookat_preserves_existing_camera_vectors_and_marks_modes(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            view_angle=12.5,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)

        plotter.camlookat()

        self.assertEqual(
            axes.camera,
            Camera3DState(
                azim=-37.5,
                elev=30.0,
                roll=0.0,
                view_angle=12.5,
                position=(1.0, 2.0, 3.0),
                target=(4.0, 5.0, 6.0),
                up_vector=(0.0, 0.0, 1.0),
            ),
        )
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")
        self.assertEqual(plotter.camera_view_angle_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 1)

        history_after_first = list(plotter.view_history_changes)
        plotter.camlookat()

        self.assertEqual(plotter.view_history_changes, history_after_first)

    def test_camlookat_noops_for_2d_axes(self):
        plotter = FakePlotter(FakeAxes())

        self.assertIsNone(plotter.camlookat())
        self.assertEqual(len(plotter.view_stack), 0)

    def test_camdolly_translates_camera_position_and_target(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            view_angle=10.0,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)

        plotter.camdolly(1.0, -2.0, 3.0)

        self.assertEqual(
            axes.camera,
            Camera3DState(
                azim=-37.5,
                elev=30.0,
                roll=0.0,
                view_angle=10.0,
                position=(2.0, 0.0, 6.0),
                target=(5.0, 3.0, 9.0),
                up_vector=(0.0, 0.0, 1.0),
            ),
        )
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 1)

    def test_camdolly_rejects_bad_deltas_and_noops_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.camdolly(1.0, float("nan"), 3.0)
        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.camdolly(1.0, 2.0, float("inf"))

        plotter.camdolly(1.0, 2.0, 3.0)
        self.assertIsNone(axes.camera.position)
        self.assertIsNone(axes.camera.target)
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camdolly(1.0, 2.0, 3.0))

    def test_camzoom_rejects_invalid_factor_and_noops_without_view_angle(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for factor in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(factor=factor):
                with self.assertRaisesRegex(ValueError, "camzoom factor"):
                    plotter.camzoom(factor)

        plotter.camzoom(2.0)
        self.assertEqual(axes.camera.view_angle, None)
        self.assertEqual(plotter.camera_view_angle_mode, "auto")
        self.assertEqual(len(plotter.view_stack), 0)

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.camzoom(2.0))

    def test_camera_vector_helpers_control_modes_and_history(self):
        axes = FakeAxes(is_3d=True)
        axes.camera = Camera3DState(
            azim=-37.5,
            elev=30.0,
            position=(1.0, 2.0, 3.0),
            target=(4.0, 5.0, 6.0),
            up_vector=(0.0, 0.0, 1.0),
        )
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.campos(), (1.0, 2.0, 3.0))
        self.assertEqual(plotter.camtarget(), (4.0, 5.0, 6.0))
        self.assertEqual(plotter.camup(), (0.0, 0.0, 1.0))
        self.assertEqual(plotter.campos("mode"), "auto")
        self.assertEqual(plotter.camtarget("mode"), "auto")
        self.assertEqual(plotter.camup("mode"), "auto")

        plotter.campos((7.0, 8.0, 9.0))
        plotter.camtarget([10.0, 11.0, 12.0])
        plotter.camup((0.0, 1.0, 0.0))

        self.assertEqual(axes.camera.position, (7.0, 8.0, 9.0))
        self.assertEqual(axes.camera.target, (10.0, 11.0, 12.0))
        self.assertEqual(axes.camera.up_vector, (0.0, 1.0, 0.0))
        self.assertEqual(plotter.camera_position_mode, "manual")
        self.assertEqual(plotter.camera_target_mode, "manual")
        self.assertEqual(plotter.camera_up_vector_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 3)

        plotter.campos("auto")
        plotter.camtarget("auto")
        plotter.camup("auto")

        self.assertEqual(plotter.campos("mode"), "auto")
        self.assertEqual(plotter.camtarget("mode"), "auto")
        self.assertEqual(plotter.camup("mode"), "auto")

    def test_camera_vector_helpers_reject_bad_values_and_are_noop_for_2d_axes(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        for command in (plotter.campos, plotter.camtarget, plotter.camup):
            with self.subTest(command=command.__name__):
                with self.assertRaisesRegex(ValueError, "3 values"):
                    command([1.0, 2.0])
                with self.assertRaisesRegex(ValueError, "finite"):
                    command([1.0, float("nan"), 3.0])
                with self.assertRaisesRegex(ValueError, "bad"):
                    command("bad")

        plotter2d = FakePlotter(FakeAxes())
        self.assertIsNone(plotter2d.campos())
        self.assertIsNone(plotter2d.camtarget("mode"))
        self.assertIsNone(plotter2d.camup([0.0, 1.0, 0.0]))

    def test_view_history_restores_3d_camera(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.view(45.0, 10.0)
        self.assertEqual(plotter.camera_mode, "manual")

        self.assertTrue(plotter.back())
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(plotter.camera_mode, "auto")

    def test_view_history_restores_3d_z_limits(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_zlim(2.0, 8.0)

        self.assertTrue(plotter.back())

        self.assertEqual(axes.limits.zlim, (0.0, 5.0))
        self.assertEqual(plotter.zlim_mode, "auto")

    def test_view_history_restores_color_limits(self):
        axes = FakeAxes()
        axes.limits = AxesLimits((0.0, 10.0), (-1.0, 1.0), None, (0.0, 1.0))
        plotter = FakePlotter(axes)
        plotter.push_current_view()
        plotter.set_clim(0.2, 0.8)

        self.assertTrue(plotter.back())

        self.assertEqual(axes.limits.clim, (0.0, 1.0))
        self.assertEqual(plotter.clim_mode, "auto")

    def test_view_3d_presets_update_camera_and_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.view(), (-37.5, 30.0))

        self.assertTrue(plotter.view_3d("2d"))
        self.assertEqual(axes.camera, Camera3DState(azim=0.0, elev=90.0, roll=0.0))
        self.assertEqual(plotter.camera_mode, "manual")

        self.assertTrue(plotter.view("3d"))
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(plotter.view_stack[-1].camera_mode, "manual")
        self.assertEqual(len(plotter.view_stack), 2)

    def test_view_accepts_matlab_numeric_2d_and_3d_presets(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.view(2))
        self.assertEqual(axes.camera, Camera3DState(azim=0.0, elev=90.0, roll=0.0))

        self.assertTrue(plotter.view(3.0))
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(len(plotter.view_stack), 2)

    def test_view_3d_wrapper_accepts_matlab_numeric_presets(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.view_3d(2))
        self.assertEqual(axes.camera, Camera3DState(azim=0.0, elev=90.0, roll=0.0))

        self.assertTrue(plotter.view_3d(3.0))
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(len(plotter.view_stack), 2)

    def test_repeating_same_manual_view_is_noop(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.view("3d"))
        history_after_first_view = list(plotter.view_history_changes)
        self.assertTrue(plotter.view("3d"))

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(plotter.camera_mode, "manual")
        self.assertEqual(plotter.view_history_changes, history_after_first_view)
        self.assertEqual(len(plotter.view_stack), 1)

    def test_equivalent_view_azimuths_do_not_duplicate_history(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.view(304.5, 30.0))
        history_after_first_view = list(plotter.view_history_changes)
        self.assertEqual(plotter.view_stack[-1].camera, Camera3DState(azim=-55.5, elev=30.0, roll=0.0))

        self.assertTrue(plotter.view(-55.5, 30.0))

        self.assertEqual(plotter.view_history_changes, history_after_first_view)
        self.assertEqual(len(plotter.view_stack), 1)

    def test_view_accepts_matlab_style_numeric_angles(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        self.assertTrue(plotter.view(45.0, 20.0))
        self.assertEqual(axes.camera, Camera3DState(azim=45.0, elev=20.0, roll=0.0))

        self.assertTrue(plotter.view([120.0, 15.0]))
        self.assertEqual(axes.camera, Camera3DState(azim=120.0, elev=15.0, roll=0.0))

        self.assertTrue(plotter.set_view_3d(-20.0, 35.0))
        self.assertEqual(plotter.get_view_3d(), (-20.0, 35.0))
        self.assertEqual(len(plotter.view_stack), 3)

    def test_view_rejects_invalid_angle_vector(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaises(ValueError):
            plotter.view([45.0])

        with self.assertRaises(ValueError):
            plotter.view("bad")

        with self.assertRaises(ValueError):
            plotter.view(4)

    def test_view_rejects_nonfinite_camera_angles(self):
        axes = FakeAxes(is_3d=True)
        plotter = FakePlotter(axes)

        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.view([float("nan"), 20.0])
        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.view(45.0, float("inf"))
        with self.assertRaisesRegex(ValueError, "finite"):
            plotter.set_view_3d(float("-inf"), 20.0)

        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(len(plotter.view_stack), 0)

    def test_view_3d_is_noop_for_2d_axes(self):
        axes = FakeAxes(is_3d=False)
        plotter = FakePlotter(axes)

        self.assertFalse(plotter.view_3d("3d"))
        self.assertFalse(plotter.view(2))
        self.assertFalse(plotter.view([45.0, 20.0]))
        self.assertIsNone(plotter.view())
        self.assertEqual(axes.camera, Camera3DState(azim=-37.5, elev=30.0, roll=0.0))
        self.assertEqual(len(plotter.view_stack), 0)


if __name__ == "__main__":
    unittest.main()

    def test_fontname_query_and_set(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.fontname(), "")
        plotter.fontname("Arial")
        self.assertEqual(plotter.fontname(), "Arial")

    def test_fontsize_query_and_set(self):
        axes = FakeAxes()
        plotter = FakePlotter(axes)

        self.assertEqual(plotter.fontsize(), 10.0)
        plotter.fontsize(14)
        self.assertEqual(plotter.fontsize(), 14.0)

    def test_fontweight_validates(self):
        plotter = FakePlotter(FakeAxes())

        plotter.fontweight("bold")
        self.assertEqual(plotter.fontweight(), "bold")

        with self.assertRaisesRegex(ValueError, "fontweight"):
            plotter.fontweight("invalid")

    def test_fontangle_validates(self):
        plotter = FakePlotter(FakeAxes())

        plotter.fontangle("italic")
        self.assertEqual(plotter.fontangle(), "italic")

        with self.assertRaisesRegex(ValueError, "fontangle"):
            plotter.fontangle("invalid")
